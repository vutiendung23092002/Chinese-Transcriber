"""Real ASR/Codex with an official WAV replayed at the microphone adapter boundary."""
import json
from pathlib import Path
import threading
import time
from unittest.mock import patch
import numpy as np
import soundfile as sf
from chinese_transcriber.models import ModelManager
from chinese_transcriber.storage import Store
from chinese_transcriber.codex import capabilities,find_codex
from chinese_transcriber.recording import LiveSession

models=ModelManager('models'); store=Store('.test-data/live-pipeline')
actual=capabilities(find_codex(),store.root/'work')
audio,sr=sf.read(models.path('sensevoice')/'test-zh.wav',dtype='float32')
audio=np.concatenate([audio,np.zeros(32000,dtype='float32')])
class WavInput:
    def __init__(self,**kwargs): self.callback=kwargs['callback']
    def start(self):
        for start in range(0,len(audio),1600):
            chunk=(np.clip(audio[start:start+1600],-1,1)*32767).astype('<i2').tobytes()
            self.callback(chunk,len(chunk)//2,None,None)
    def stop(self): pass
    def close(self): pass
events=[]
config=dict(model='gpt-6-luna',effort='low',context='Thông báo giờ phục vụ',glossary=[],executable=actual['path'],models=actual['models'])
with patch('chinese_transcriber.recording.sd.RawInputStream',WavInput):
    session=LiveSession(store,models,events.append,translation=config).start()
    deadline=time.monotonic()+60
    while time.monotonic()<deadline:
        if session.segments and all(x.get('translation_status')=='complete' for x in session.segments): break
        time.sleep(.2)
    result=session.stop()
rows=store.segments(result['transcript_id'],result['version_id'])
final_order={item['id']:i for i,item in enumerate(events) if item['type']=='final'}
stable_order=all(item['id'] in final_order and final_order[item['id']]<i for i,item in enumerate(events) if item['type']=='translation')
report=dict(source='official Mandarin WAV replay, not physical microphone',saved_audio=store.audio_path(result['audio_id']).is_file(),segments=len(rows),translated=all(x['translation_status']=='complete' for x in rows),
    interim_events=sum(x['type']=='interim' for x in events),finalized_before_translation=stable_order)
assert report['saved_audio'] and report['segments'] and report['translated'] and report['finalized_before_translation']
(store.root/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
