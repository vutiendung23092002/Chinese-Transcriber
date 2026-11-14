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
