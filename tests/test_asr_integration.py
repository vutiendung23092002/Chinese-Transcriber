from pathlib import Path
import threading
import pytest
import soundfile as sf
from chinese_transcriber.models import ModelManager
from chinese_transcriber.asr import Recognizer,transcribe_job
from chinese_transcriber.storage import Store

@pytest.fixture(scope='module')
def engine():
    models=ModelManager('models')
    if not all(models.ready(x) for x in ('sensevoice','paraformer','vad')): pytest.skip('Mô hình chưa tải')
    return Recognizer(models,4,True)

def test_real_file_inference_is_durable(tmp_path,engine):
    store=Store(tmp_path)
    sample=engine.models.path('sensevoice')/'test-zh.wav'
    audio,_=store.import_audio(sample,sf.info(sample).duration)
    events=[]
    transcript=transcribe_job(store,engine.models,audio['id'],events.append,threading.Event())
    rows=store.segments(transcript)
    assert rows and all(x['zh'] and 0<=x['start']<x['end']<=audio['duration']+.05 for x in rows)
    assert store.latest_transcript(audio['id'])['status']=='complete'
    assert any(event.get('type')=='final' for event in events)

def test_live_replay_only_finalizes_stable_speech(engine):
    audio,sr=sf.read(engine.models.path('sensevoice')/'test-zh.wav',dtype='float32')
    events=[]
    engine.stream((audio[i:i+1600] for i in range(0,len(audio),1600)),events.append)
    final=[x for x in events if x['type']=='final']
    assert final and all(x['zh'] and x['timing']=='vad-boundary' for x in final)
    assert events[-1]['type']=='interim' and events[-1]['zh']==''


def test_real_asr_combined_pipeline_preserves_final_segments(tmp_path,engine,monkeypatch):
    import hashlib
    import numpy as np
    from chinese_transcriber import pipeline
    sample,sr=sf.read(engine.models.path('sensevoice')/'test-zh.wav',dtype='float32')
    source=tmp_path/'three-sentences.wav'
    sf.write(source,np.concatenate([np.concatenate([sample,np.zeros(sr,dtype='float32')]) for _ in range(3)]),sr)
    before=hashlib.sha256(source.read_bytes()).hexdigest()
    store=Store(tmp_path/'library'); audio,_=store.import_audio(source,sf.info(source).duration)
    models=[dict(model='test',supportedReasoningEfforts=[dict(reasoningEffort='low')])]
    monkeypatch.setattr(pipeline,'find_codex',lambda *_:'test.exe')
    monkeypatch.setattr(pipeline,'translate_segments',lambda *args:[dict(id=row['id'],vi='Bản dịch thử',note='') for row in args[7]])
    events=[]
    result=pipeline.transcribe_translate_job(store,engine.models,audio['id'],dict(model='test',effort='low',context='',glossary=[]),events.append,threading.Event(),known_models=models)
    rows=store.segments(result['transcript_id'],result['version_id'])
    assert result['status']=='complete' and len(rows)==3
    assert all(row['zh'] and row['translation_status']=='complete' and row['vi']=='Bản dịch thử' for row in rows)
    assert all(0<=row['start']<row['end']<=audio['duration']+.05 for row in rows)
    assert events[0]['type']=='started' and events[-1]['type']=='finished'
    assert hashlib.sha256(source.read_bytes()).hexdigest()==before
