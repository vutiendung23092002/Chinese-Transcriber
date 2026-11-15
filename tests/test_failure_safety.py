from concurrent.futures import ThreadPoolExecutor
import json
import threading
import numpy as np
import pytest
from chinese_transcriber.storage import Store
from chinese_transcriber.recording import LiveSession,materialize_recording
from chinese_transcriber.codex import translate_version

def test_parallel_imports_never_duplicate_source(tmp_path):
    store=Store(tmp_path/'data'); path=tmp_path/'audio.wav'; path.write_bytes(b'audio'*10000)
    with ThreadPoolExecutor(max_workers=4) as pool:
        result=list(pool.map(lambda _:store.import_audio(path),range(4)))
    assert sum(created for _,created in result)==1
    assert len(store.list_audio())==1
    assert len(list((store.root/'audio').iterdir()))==1

def test_restore_group_does_not_restore_previously_trashed_version(tmp_path,monkeypatch):
    store=Store(tmp_path/'data'); path=tmp_path/'a.wav'; path.write_bytes(b'a')
    audio,_=store.import_audio(path); t=store.new_transcript(audio['id'],'test'); store.append_segment(t,0,1,'中')
    a=store.new_version(audio['id'],t,'m','low','',[]); b=store.new_version(audio['id'],t,'m','low','',[])
    monkeypatch.setattr('chinese_transcriber.storage.now',lambda:'2026-11-14T12:00:00.000000+00:00')
    store.trash_version(a); store.trash_audio(audio['id']); store.restore_audio(audio['id'])
    assert [x['id'] for x in store.versions(audio['id'])]==[b]

def test_failed_translation_retains_previous_completed_results(tmp_path,monkeypatch):
    store=Store(tmp_path/'data'); path=tmp_path/'a.wav'; path.write_bytes(b'a'); audio,_=store.import_audio(path)
    t=store.new_transcript(audio['id'],'test'); one=store.append_segment(t,0,1,'一'); two=store.append_segment(t,1,2,'二')
    v=store.new_version(audio['id'],t,'m','low','',[]); store.translation_result(v,one,'Một')
    def failure(*args,**kwargs): raise ValueError('invalid JSON IDs')
    monkeypatch.setattr('chinese_transcriber.codex.translate_segments',failure)
    class NoDelay:
        def is_set(self): return False
        def wait(self,seconds): return False
    with pytest.raises(ValueError): translate_version(store,'unused',v,[dict(model='m',supportedReasoningEfforts=[dict(reasoningEffort='low')])],lambda _:None,NoDelay())
    rows=store.segments(t,v)
    assert rows[0]['vi']=='Một' and rows[0]['translation_status']=='complete'
    assert rows[1]['translation_status']=='failed'
    assert store.audio_path(audio['id']).exists()

def test_asr_failure_does_not_stop_continuous_audio_storage(tmp_path,monkeypatch):
    class BrokenRecognizer:
        def __init__(self,*args,**kwargs): pass
        def stream(self,chunks,callback): raise RuntimeError('ASR failure')
    class Source:
        def __init__(self,**kwargs): self.callback=kwargs['callback']
        def start(self):
            for _ in range(10): self.callback(np.zeros(1600,dtype='<i2').tobytes(),1600,None,None)
        def stop(self): pass
        def close(self): pass
    monkeypatch.setattr('chinese_transcriber.recording.Recognizer',BrokenRecognizer)
    monkeypatch.setattr('chinese_transcriber.recording.sd.RawInputStream',Source)
    store=Store(tmp_path); session=LiveSession(store,None,lambda _:None).start(); result=session.stop()
    assert store.audio_path(result['audio_id']).exists()
    assert store.list_audio()[0]['duration']==1
    assert store.latest_transcript(result['audio_id'],False)['status']=='interrupted'
    assert result['warning']

def test_completed_live_translations_survive_materialization(tmp_path):
    store=Store(tmp_path); path=store.root/'recordings'/'session.pcm'; path.write_bytes(np.zeros(32000,dtype='<i2').tobytes())
    payload=dict(path='recordings/session.pcm',translation=dict(model='m',effort='low',context='lecture',glossary=[]),segments=[dict(id='temporary-id',start=0,end=1.9,zh='你好',timing='vad-boundary',vi='Xin chào',note='',translation_status='complete')])
    job=store.job('recording','session',payload); result=materialize_recording(store,payload,job)
    assert store.segments(result['transcript_id'],result['version_id'])[0]['vi']=='Xin chào'
    assert store.versions(result['audio_id'])[0]['status']=='complete'
