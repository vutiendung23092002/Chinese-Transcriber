"""Local CPU recognition; speech boundary times come from sample offsets."""
from __future__ import annotations
import re
import threading
import time
import numpy as np
import sherpa_onnx
from .audio import decoded_chunks

def clean_asr_text(text):
    text=re.sub(r'<\|[^>]+\|>','',text).strip()
    return text if any(character.isalnum() for character in text) else ''

class Recognizer:
    def __init__(self,models,threads=4,streaming=False):
        self.models=models; self.threads=max(1,min(4,int(threads)))
        required=['sensevoice','vad']+(['paraformer'] if streaming else [])
        missing=[key for key in required if not models.ready(key)]
        if missing: raise ValueError('Chưa có mô hình: '+', '.join(missing)+'. Mở Cài đặt → Tải mô hình ASR.')
        root=models.path('sensevoice')
        self.offline=sherpa_onnx.OfflineRecognizer.from_sense_voice(model=str(root/'model.int8.onnx'),tokens=str(root/'tokens.txt'),
            language='zh',use_itn=True,num_threads=self.threads,provider='cpu')
        self.online=None
        if streaming:
            root=models.path('paraformer')
            self.online=sherpa_onnx.OnlineRecognizer.from_paraformer(tokens=str(root/'tokens.txt'),encoder=str(root/'encoder.int8.onnx'),
                decoder=str(root/'decoder.int8.onnx'),num_threads=self.threads,provider='cpu',enable_endpoint_detection=True,
                rule1_min_trailing_silence=1.8,rule2_min_trailing_silence=0.9,rule3_min_utterance_length=20)

    def vad(self):
        config=sherpa_onnx.VadModelConfig()
        config.silero_vad.model=str(self.models.path('vad')/'silero_vad.onnx')
        config.silero_vad.min_silence_duration=0.8
        config.silero_vad.min_speech_duration=0.25
        config.silero_vad.max_speech_duration=20
        config.silero_vad.window_size=512
        config.sample_rate=16000; config.num_threads=1
        return sherpa_onnx.VoiceActivityDetector(config,buffer_size_in_seconds=60)

    def recognize(self,samples):
        stream=self.offline.create_stream(); stream.accept_waveform(16000,np.asarray(samples,dtype='float32'))
        self.offline.decode_stream(stream)
        # Strip non-speech metadata without manufacturing word timestamps.
        return clean_asr_text(stream.result.text)

    def consume_vad(self,vad,callback,offset=0,skip_before=0):
        while not vad.empty():
            segment=vad.front
            start=offset+segment.start/16000; samples=np.array(segment.samples,dtype='float32')
            end=start+len(samples)/16000
            vad.pop()
            if end<=skip_before+.001: continue
            text=clean_asr_text(self.recognize(samples))
            if text:
                callback(dict(start=round(start,3),end=round(end,3),zh=text,timing='vad-boundary'))

    def transcribe(self,path,callback,cancel=None,progress=lambda x:None,skip_before=0):
        vad=self.vad(); processed=0
        for samples in decoded_chunks(path,512,cancel):
            vad.accept_waveform(samples); processed+=len(samples)
            self.consume_vad(vad,callback,skip_before=skip_before)
            if processed%(16000*2)<512: progress(dict(seconds=processed/16000))
        vad.flush(); self.consume_vad(vad,callback,skip_before=skip_before)

    def stream(self,chunks,callback):
        vad=self.vad(); online=self.online.create_stream(); total=0; base=0; last=time.monotonic()
        for samples in chunks:
            if samples is None:
                vad.flush(); self.consume_vad(vad,lambda row:callback(dict(type='final',**row)),base)
                vad=self.vad(); base=total/16000; online=self.online.create_stream(); continue
            samples=np.asarray(samples,dtype='float32')
            online.accept_waveform(16000,samples)
            while self.online.is_ready(online): self.online.decode_stream(online)
            total+=len(samples); vad.accept_waveform(samples)
            self.consume_vad(vad,lambda row:callback(dict(type='final',**row)),base)
            if time.monotonic()-last>.35:
                callback(dict(type='interim',zh=clean_asr_text(self.online.get_result(online)),seconds=total/16000)); last=time.monotonic()
            if self.online.is_endpoint(online): self.online.reset(online)
        vad.flush(); self.consume_vad(vad,lambda row:callback(dict(type='final',**row)),base)
        callback(dict(type='interim',zh='',seconds=total/16000))

def transcribe_job(store,models,audio_id,progress,cancel,threads=4,*,transcript_id=None,version_id=None,manage_job=True):
    transcript=transcript_id or store.new_transcript(audio_id,'SenseVoiceSmall int8 + Silero VAD')
    saved=store.segments(transcript); skip_before=saved[-1]['end'] if saved else 0
    store.set_transcript_status(transcript,'running')
    job=store.job('transcribe',transcript,{'audio_id':audio_id}) if manage_job else None
    try:
        progress(dict(type='started',transcript_id=transcript,version_id=version_id))
        engine=Recognizer(models,threads)
        def final(segment):
            identifier=store.append_segment(transcript,**dict(start=segment['start'],end=segment['end'],text=segment['zh'],timing=segment['timing']),version_id=version_id)
            progress(dict(type='final',transcript_id=transcript,version_id=version_id,id=identifier,**segment))
        kwargs=dict(skip_before=skip_before) if skip_before else {}
        engine.transcribe(store.audio_path(audio_id),final,cancel,progress,**kwargs)
        if not store.segments(transcript): raise ValueError('Không phát hiện lời nói. Âm thanh vẫn được giữ trong thư viện.')
        store.set_transcript_status(transcript,'complete')
        if manage_job: store.job('transcribe',transcript,{'audio_id':audio_id},job,'complete')
        return transcript
    except Exception as error:
        store.set_transcript_status(transcript,'interrupted' if isinstance(error,InterruptedError) else 'failed')
        if manage_job: store.job('transcribe',transcript,{'audio_id':audio_id},job,'interrupted' if isinstance(error,InterruptedError) else 'failed',str(error))
        raise
