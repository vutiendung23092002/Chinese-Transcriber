"""Continuous PCM journal independent from ASR/translation lifetimes."""
from __future__ import annotations
import json
import os
import queue
import threading
import time
import wave
from pathlib import Path
import numpy as np
import sounddevice as sd
from .storage import uid
from .asr import Recognizer

class LiveSession:
    def __init__(self,store,models,notify,device=None,threads=4,translation=None):
        self.store=store; self.notify=notify; self.device=device
        self.engine=Recognizer(models,threads,streaming=True)
        self.identifier=uid(); self.path=store.root/'recordings'/(self.identifier+'.pcm')
        self.samples=0; self.segments=[]; self.paused=False; self.error=''; self.lagged=False
        self.translation=translation; self.translation_queue=queue.Queue()
        self.translation_cancel=threading.Event(); self.state_lock=threading.RLock(); self.saved=False
        self.capture_queue=queue.Queue(maxsize=256); self.asr_queue=queue.Queue(maxsize=256)
        self.closed=threading.Event(); self.capture_stopped=threading.Event()
        self.job=store.job('recording',self.identifier,self.payload())
        self.stream=None

    def payload(self):
        with self.state_lock:
            translation={key:self.translation[key] for key in ('model','effort','context','glossary')} if self.translation else None
            return {'path':str(self.path.relative_to(self.store.root)),'sample_rate':16000,'segments':[dict(x) for x in self.segments],
                'samples':self.samples,'lagged':self.lagged,'translation':translation}

    def start(self):
        try:
            self.stream=sd.RawInputStream(samplerate=16000,channels=1,dtype='int16',blocksize=1600,device=self.device,callback=self.capture)
            self.writer=threading.Thread(target=self.write,name='recording-writer',daemon=True)
            self.decoder=threading.Thread(target=self.decode,name='live-asr',daemon=True)
            self.writer.start(); self.decoder.start(); self.stream.start()
            if self.translation:
                self.translator=threading.Thread(target=self.translate,name='live-translation',daemon=True); self.translator.start()
            return self
        except Exception as error:
            self.error=str(error)
            self.capture_stopped.set()
            self.store.job('recording',self.identifier,self.payload(),self.job,'failed',self.error)
            if self.stream: self.stream.close()
            raise ValueError('Không mở được microphone: '+str(error)) from error

    def capture(self,data,frames,time_info,status):
        if self.paused or self.capture_stopped.is_set(): return
        if status:
            self.notify(dict(type='warning',message='Thiết bị âm thanh báo: '+str(status)))
        try: self.capture_queue.put_nowait(bytes(data))
        except queue.Full:
            self.error='Ổ đĩa không theo kịp ghi âm. Các phần đã ghi vẫn được giữ.'
            self.capture_stopped.set(); self.notify(dict(type='warning',message=self.error))

    def write(self):
        last=time.monotonic(); warned=False
        try:
            with self.path.open('xb') as output:
                while not self.capture_stopped.is_set() or not self.capture_queue.empty():
                    try: data=self.capture_queue.get(timeout=.2)
                    except queue.Empty:
                        if not self.samples and not warned and time.monotonic()-last>5:
                            self.notify(dict(type='warning',message='Microphone chưa trả dữ liệu. Kiểm tra tai nghe Bluetooth hoặc chọn thiết bị khác.')); warned=True
                        continue
                    if data is None:
                        if not self.lagged:
                            try: self.asr_queue.put(None,timeout=.5)
                            except queue.Full: self.lagged=True
                        continue
                    output.write(data); self.samples+=len(data)//2
                    if not self.lagged:
                        try: self.asr_queue.put_nowait(np.frombuffer(data,dtype='<i2').astype('float32')/32768)
                        except queue.Full:
                            self.lagged=True
                            self.notify(dict(type='warning',message='ASR đang chậm. Âm thanh vẫn đang lưu; có thể chép lời lại toàn bộ sau khi dừng.'))
                    if time.monotonic()-last>=1:
                        output.flush(); os.fsync(output.fileno()); last=time.monotonic()
                        self.store.job('recording',self.identifier,self.payload(),self.job)
                        values=np.frombuffer(data,dtype='<i2').astype('float32')/32768
                        level=int(min(100,np.sqrt(np.mean(values*values))*250)) if len(values) else 0
                        self.notify(dict(type='level',seconds=self.samples/16000,level=level))
                output.flush(); os.fsync(output.fileno())
        except Exception as error:
            self.error=str(error); self.notify(dict(type='warning',message='Lỗi ghi file: '+self.error))
        finally:
            self.closed.set()

    def chunks(self):
        while not self.closed.is_set() or not self.asr_queue.empty():
            try: yield self.asr_queue.get(timeout=.2)
            except queue.Empty: continue

    def decode(self):
        try:
            def result(item):
                if item['type']=='final':
                    item=dict(item,id=uid(),vi='',note='',translation_status='queued' if self.translation else 'untranslated')
                    with self.state_lock: self.segments.append(item)
                    self.store.job('recording',self.identifier,self.payload(),self.job)
                    self.notify(dict(item))
                    if self.translation: self.translation_queue.put(item)
                    return
                self.notify(item)
            self.engine.stream(self.chunks(),result)
        except Exception as error:
            self.lagged=True; self.notify(dict(type='warning',message='ASR dừng: '+str(error)+'. Âm thanh vẫn được lưu.'))

    def translate(self):
        from .codex import translate_segments
        config=self.translation
        while not self.translation_cancel.is_set():
            try: segment=self.translation_queue.get(timeout=.2)
            except queue.Empty: continue
            with self.state_lock: segment['translation_status']='translating'
            self.notify(dict(segment,type='translation'))
            try:
                for attempt in range(3):
                    try:
                        result=translate_segments(config['executable'],self.store.root/'work',config['models'],config['model'],config['effort'],
                            config['context'],config['glossary'],[segment],self.translation_cancel)[0]
                        with self.state_lock: segment.update(vi=result['vi'],note=result['note'],translation_status='complete')
                        break
                    except InterruptedError: raise
                    except Exception:
                        if attempt==2: raise
                        if self.translation_cancel.wait(2**attempt): raise InterruptedError('Dịch tiếp sau khi lưu phiên.')
            except InterruptedError:
                with self.state_lock: segment['translation_status']='queued'
            except Exception as error:
                with self.state_lock: segment.update(translation_status='failed',error=str(error))
            with self.state_lock:
                if not self.saved: self.store.job('recording',self.identifier,self.payload(),self.job)
            self.notify(dict(segment,type='translation'))

    def pause(self):
        self.paused=not self.paused
        if self.paused:
            self.capture_queue.put(None,timeout=3)
        return self.paused

    def stop(self):
        if self.stream:
            self.stream.stop(); self.stream.close()
        self.capture_stopped.set()
        self.writer.join(timeout=15)
        if self.writer.is_alive(): raise ValueError('Chưa ghi xong âm thanh; file tạm được giữ để phục hồi.')
        self.decoder.join(timeout=90)
        if self.decoder.is_alive():
            self.store.job('recording',self.identifier,self.payload(),self.job,'interrupted','ASR chưa dừng; có thể phục hồi âm thanh.')
            raise ValueError('ASR chưa dừng. Âm thanh đã lưu tạm; mở phục hồi sau khi ASR kết thúc.')
        self.translation_cancel.set()
        if self.translation: self.translator.join(timeout=8)
        with self.state_lock: self.saved=True
        if not self.path.exists() or self.path.stat().st_size<2:
            message='Microphone chưa trả dữ liệu âm thanh. Kiểm tra kết nối Bluetooth, thiết bị và quyền microphone của Windows.'
            self.store.job('recording',self.identifier,self.payload(),self.job,'failed',message)
            self.path.unlink(missing_ok=True)
            return dict(audio_id=None,transcript_id=None,warning=message)
        return materialize_recording(self.store,self.payload(),self.job,self.error)

def materialize_recording(store,payload,job_id,error=''):
    pcm=(store.root/payload['path']).resolve()
    if not pcm.is_relative_to(store.root/'recordings'): raise ValueError('Đường dẫn bản ghi không hợp lệ.')
    if not pcm.exists() or pcm.stat().st_size<2: raise ValueError('Bản ghi chưa có âm thanh.')
    wav=pcm.with_suffix('.wav')
    with wave.open(str(wav),'wb') as output,pcm.open('rb') as incoming:
        output.setnchannels(1); output.setsampwidth(2); output.setframerate(16000)
        while chunk:=incoming.read(1024*1024): output.writeframesraw(chunk[:len(chunk)//2*2])
    duration=pcm.stat().st_size//2/16000
    audio,created=store.import_audio(wav,duration,'live','Ghi âm '+time.strftime('%d/%m/%Y %H:%M'))
    transcript=store.new_transcript(audio['id'],'Live Paraformer → SenseVoice + Silero')
    mapping=[]
    for segment in payload.get('segments',[]):
        end=min(duration,segment['end'])
        if end>segment['start']:
            identifier=store.append_segment(transcript,segment['start'],end,segment['zh'],segment['timing'])
            mapping.append((identifier,segment))
    status='interrupted' if error or payload.get('lagged') else 'complete'
    store.set_transcript_status(transcript,status)
    version=None
    if payload.get('translation') and mapping:
        version=store.new_version(audio['id'],transcript,**payload['translation'])
        for identifier,segment in mapping:
            if segment.get('translation_status')=='complete': store.translation_result(version,identifier,segment['vi'],segment.get('note',''))
        store.set_version_status(version,'complete' if all(x.get('translation_status')=='complete' for _,x in mapping) else 'partial')
    store.job('recording',audio['id'],dict(audio_id=audio['id'],transcript_id=transcript),job_id,'complete',error)
    pcm.unlink(missing_ok=True); wav.unlink(missing_ok=True)
    return dict(audio_id=audio['id'],transcript_id=transcript,version_id=version,warning=error or ('Cần chép lời lại từ file đã lưu để lấy đầy đủ nội dung.' if payload.get('lagged') else ''))
