"""Measure CPU inference on official Mandarin fixtures and record the test hardware."""
import json
import platform
import subprocess
from pathlib import Path
import sys
import time
import psutil
import soundfile as sf
import numpy as np
import sherpa_onnx
from chinese_transcriber.models import ModelManager
from chinese_transcriber.asr import Recognizer

def main():
    models=ModelManager(Path('models'))
    cpu=platform.processor()
    try:
        cpu=subprocess.check_output(['powershell','-NoProfile','-Command','(Get-CimInstance Win32_Processor).Name'],text=True,creationflags=0x08000000).strip()
    except Exception: pass
    report={'platform':platform.platform(),'cpu':cpu,'logical_cores':psutil.cpu_count(),
        'ram_gib':round(psutil.virtual_memory().total/2**30,1),'threads':4,'hardware_note':'Measured on the reference test machine listed here. Performance varies by hardware and workload.',
        'accuracy_note':'No labelled lecture corpus or CER/WER evaluation. These short fixtures measure speed only. VAD boundaries are not word-level alignment.',
        'runs':[]}
    started=time.perf_counter(); engine=Recognizer(models,4,True); report['load_seconds']=round(time.perf_counter()-started,3)
    for fixture,path in [('sensevoice-official',models.path('sensevoice')/'test-zh.wav'),('paraformer-official',models.path('paraformer')/'test-zh.wav')]:
        audio,sr=sf.read(path,dtype='float32'); duration=len(audio)/sr
        assert sr==16000
        for kind in ('sensevoice','paraformer'):
            for repeat in range(2):
                start=time.perf_counter()
                if kind=='sensevoice':
                    text=engine.recognize(audio)
                else:
                    stream=engine.online.create_stream()
                    for offset in range(0,len(audio),1600):
                        stream.accept_waveform(sr,audio[offset:offset+1600])
                        while engine.online.is_ready(stream): engine.online.decode_stream(stream)
                    stream.accept_waveform(sr,np.zeros(int(.8*sr),dtype='float32')); stream.input_finished()
                    while engine.online.is_ready(stream): engine.online.decode_stream(stream)
                    text=engine.online.get_result(stream)
                seconds=time.perf_counter()-start
                report['runs'].append(dict(fixture=fixture,model=kind,repeat=repeat+1,audio_seconds=round(duration,3),inference_seconds=round(seconds,3),rtf=round(seconds/duration,3),rss_mb=round(psutil.Process().memory_info().rss/2**20,1),text=text))
    report['file_pipeline']=[]
    for repeat in range(2):
        segments=[]; started=time.perf_counter(); engine.transcribe(models.path('sensevoice')/'test-zh.wav',segments.append)
        report['file_pipeline'].append(dict(repeat=repeat+1,seconds=round(time.perf_counter()-started,3),segments=segments))
    output=Path('docs/ASR_BENCHMARK.json'); output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(report=str(output),runs=len(report['runs']),load_seconds=report['load_seconds'])))

if __name__=='__main__': main()
