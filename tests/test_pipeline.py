from concurrent.futures import ThreadPoolExecutor
import threading
import numpy as np
import pytest
from chinese_transcriber import asr, pipeline
from chinese_transcriber.storage import Store

MODELS=[dict(model='test',supportedReasoningEfforts=[dict(reasoningEffort='low')])]
OPTIONS=dict(model='test',effort='low',context='lecture',glossary=[])


@pytest.fixture
def library(tmp_path,monkeypatch):
    store=Store(tmp_path/'library'); wav=tmp_path/'source.wav'; wav.write_bytes(b'original audio')
    audio,_=store.import_audio(wav,10)
    monkeypatch.setattr(pipeline,'find_codex',lambda *_:'test.exe')
    return store,audio['id']


def segment(number):
    return dict(start=number-1,end=number,zh=f'句子{number}',timing='vad-boundary')


def response(rows):
    return [dict(id=row['id'],vi='Dịch '+row['zh'],note='') for row in rows]


def run(store,audio,progress,cancel,**kwargs):
    return pipeline.transcribe_translate_job(store,None,audio,OPTIONS,progress,cancel,known_models=MODELS,**kwargs)


def test_asr_keeps_producing_while_first_translation_waits(library,monkeypatch):
    store,audio=library; translating=threading.Event(); produced=threading.Event(); release=threading.Event()
    class Recognizer:
        def __init__(self,*args): pass
        def transcribe(self,path,final,cancel,progress,**kwargs):
            final(segment(1))
            assert translating.wait(3), 'Translation must start before ASR finishes'
            for i in range(2,6): final(segment(i))
            produced.set()
    def translate(*args):
        assert not produced.is_set() or translating.is_set()
        translating.set(); assert release.wait(3)
        return response(args[7])
    monkeypatch.setattr(asr,'Recognizer',Recognizer); monkeypatch.setattr(pipeline,'translate_segments',translate)
    with ThreadPoolExecutor(1) as pool:
        future=pool.submit(run,store,audio,lambda _:None,threading.Event())
        try:
            assert produced.wait(3), 'ASR was blocked by translation'
            version=store.versions(audio)[0]; rows=store.segments(version['transcript_id'],version['id'])
            assert len(rows)==5 and rows[0]['translation_status']=='translating'
            assert all(row['translation_status']=='queued' for row in rows[1:])
        finally: release.set()
        result=future.result(5)
    assert result['status']=='complete'
    assert all(row['translation_status']=='complete' for row in store.segments(result['transcript_id'],result['version_id']))


def test_translation_error_does_not_stop_asr_and_can_resume_same_version(library,monkeypatch):
    store,audio=library; failed=threading.Event(); calls=[]
    class Recognizer:
        def __init__(self,*args): pass
        def transcribe(self,path,final,cancel,progress,**kwargs):
            final(segment(1)); assert failed.wait(3)
            final(segment(2)); final(segment(3))
    class NoDelay:
        def is_set(self): return False
        def wait(self,*args): return False
    def failure(*args): calls.append(args[7]); raise ValueError('translation unavailable')
    monkeypatch.setattr(asr,'Recognizer',Recognizer); monkeypatch.setattr(pipeline,'translate_segments',failure)
    result=run(store,audio,lambda item:failed.set() if item['type']=='translation_error' else None,NoDelay())
    assert result['status']=='partial' and len(calls)==3
    assert store.latest_transcript(audio)['status']=='complete'
    rows=store.segments(result['transcript_id'],result['version_id']); ids=[row['id'] for row in rows]
    assert [row['translation_status'] for row in rows]==['failed','queued','queued']
    monkeypatch.setattr(pipeline,'translate_segments',lambda *args:response(args[7]))
    resumed=run(store,audio,lambda _:None,threading.Event(),version_id=result['version_id'])
    assert resumed['status']=='complete' and resumed['version_id']==result['version_id']
    assert [row['id'] for row in store.segments(result['transcript_id'])]==ids
    assert len(store.versions(audio))==1


def test_cancel_and_resume_preserve_source_segment_ids_and_completed_text(library,monkeypatch):
    store,audio=library; cancel=threading.Event(); translated=threading.Event(); checkpoints=[]; requested=[]
    class Recognizer:
        def __init__(self,*args): pass
        def transcribe(self,path,final,stop,progress,skip_before=0):
            checkpoints.append(skip_before)
            if not skip_before:
                final(segment(1)); assert translated.wait(3)
                final(segment(2)); stop.set(); raise InterruptedError('stopped')
            assert skip_before==2
            final(segment(3))
    def translate(*args):
        rows=args[7]; requested.extend(row['id'] for row in rows)
        if cancel.is_set(): raise InterruptedError('stopped')
        return response(rows)
    monkeypatch.setattr(asr,'Recognizer',Recognizer); monkeypatch.setattr(pipeline,'translate_segments',translate)
    result=run(store,audio,lambda item:translated.set() if item['translated']==1 else None,cancel)
    rows=store.segments(result['transcript_id'],result['version_id']); before=rows[0].copy()
    assert result['status']=='interrupted' and len(rows)==2
    assert before['translation_status']=='complete'
    requested.clear(); cancel.clear(); store.recover_jobs()
    resumed=run(store,audio,lambda _:None,cancel,version_id=result['version_id'])
    after=store.segments(result['transcript_id'],result['version_id'])
    assert checkpoints==[0,2] and resumed['status']=='complete'
    assert after[0]['id']==before['id'] and after[0]['vi']==before['vi']
    assert before['id'] not in requested and len(after)==3
    assert len(store.rows('SELECT * FROM jobs'))==1
    assert len(store.rows('SELECT * FROM transcripts'))==len(store.versions(audio))==1


def test_translation_setup_failure_still_saves_all_chinese(library,monkeypatch):
    store,audio=library
    class Recognizer:
        def __init__(self,*args): pass
        def transcribe(self,path,final,*args,**kwargs):
            final(segment(1)); final(segment(2))
    monkeypatch.setattr(asr,'Recognizer',Recognizer)
    monkeypatch.setattr(pipeline,'find_codex',lambda *_:(_ for _ in ()).throw(FileNotFoundError('offline')))
    result=run(store,audio,lambda _:None,threading.Event())
    assert result['warnings']['translation']=='offline' and result['status']=='partial'
    assert store.latest_transcript(audio)['status']=='complete'
    assert [row['translation_status'] for row in store.segments(result['transcript_id'],result['version_id'])]==['queued','queued']


def test_asr_failure_keeps_and_translates_already_finalized_rows(library,monkeypatch):
    store,audio=library
    class Recognizer:
        def __init__(self,*args): pass
        def transcribe(self,path,final,*args,**kwargs):
            final(segment(1)); raise RuntimeError('decoder failed')
    monkeypatch.setattr(asr,'Recognizer',Recognizer)
    monkeypatch.setattr(pipeline,'translate_segments',lambda *args:response(args[7]))
    result=run(store,audio,lambda _:None,threading.Event())
    assert result['warnings']['asr']=='decoder failed' and result['status']=='partial'
    assert store.latest_transcript(audio,False)['status']=='failed'
    assert store.segments(result['transcript_id'],result['version_id'])[0]['translation_status']=='complete'


def test_segment_and_queue_insert_are_atomic(library):
    store,audio=library; one=store.new_transcript(audio,'test'); two=store.new_transcript(audio,'test')
    version=store.new_version(audio,two,**OPTIONS)
    with pytest.raises(ValueError,match='không thuộc'):
        store.append_segment(one,0,1,'你好',version_id=version)
    assert store.segments(one)==[]


def test_resume_skips_recognition_for_previously_saved_vad_segments():
    from types import SimpleNamespace
    rows=[SimpleNamespace(start=i*16000,samples=np.ones(16000,dtype='float32')) for i in range(3)]
    class Vad:
        def empty(self): return not rows
        @property
        def front(self): return rows[0]
        def pop(self): rows.pop(0)
    engine=asr.Recognizer.__new__(asr.Recognizer); calls=[]
    engine.recognize=lambda samples:(calls.append(len(samples)) or '你好')
    result=[]; engine.consume_vad(Vad(),result.append,skip_before=2)
    assert len(calls)==1 and result[0]['start']==2 and result[0]['end']==3


def test_last_segment_is_not_lost_when_producer_finishes_after_queue_snapshot(library,monkeypatch):
    store,audio=library; gap=threading.Event(); finished=threading.Event(); reads=[0]
    original=store.segments
    def snapshot(*args,**kwargs):
        rows=original(*args,**kwargs)
        if threading.current_thread().name=='file-translation' and len(rows)==1 and rows[0]['translation_status']=='complete':
            reads[0]+=1
            if reads[0]==2:
                # Return a stale, empty-outbox view after the final segment
                # has been committed and the producer has closed its side.
                gap.set(); assert finished.wait(3)
        return rows
    class Recognizer:
        def __init__(self,*args): pass
        def transcribe(self,path,final,*args,**kwargs):
            final(segment(1)); assert gap.wait(3); final(segment(2))
    monkeypatch.setattr(store,'segments',snapshot)
    monkeypatch.setattr(asr,'Recognizer',Recognizer)
    monkeypatch.setattr(pipeline,'translate_segments',lambda *args:response(args[7]))
    result=run(store,audio,lambda item:finished.set() if item['asr_done'] else None,threading.Event())
    assert result['status']=='complete' and reads[0]>=2
    rows=original(result['transcript_id'],result['version_id'])
    assert len(rows)==2 and all(row['translation_status']=='complete' for row in rows)
