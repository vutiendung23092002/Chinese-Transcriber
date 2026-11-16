"""File transcription with parallel or whole-transcript translation."""
from __future__ import annotations
import json
import threading
from .asr import transcribe_job
from .codex import capabilities, find_codex, translate_segments, validate_selection


def transcribe_translate_job(store, models, audio_id, options, progress, cancel, threads=4,
                             *, version_id=None, transcript_id=None, known_models=None, translation_mode='parallel'):
    previous=None
    if version_id:
        version=store.one('SELECT * FROM versions WHERE id=? AND deleted IS NULL',(version_id,))
        if not version or version['audio_id']!=audio_id:
            raise ValueError('Bản dịch không thuộc âm thanh đang xử lý.')
        transcript=version['transcript_id']
        options={key:version[key] for key in ('model','effort','context')}
        options['glossary']=json.loads(version['glossary'])
        previous=store.one("SELECT id,payload FROM jobs WHERE kind='transcribe_translate' AND target=? ORDER BY updated DESC LIMIT 1",(version_id,))
        # A resumed task uses its own snapshot, never the current UI preference.
        translation_mode=json.loads(previous['payload']).get('translation_mode','parallel') if previous else translation_mode
    if translation_mode not in ('parallel','whole'):
        raise ValueError('Chế độ dịch không hợp lệ.')
    if version_id:
        store.queue_missing_translations(version_id)
    else:
        if transcript_id:
            source=store.one('SELECT * FROM transcripts WHERE id=? AND audio_id=? AND deleted IS NULL',(transcript_id,audio_id))
            if not source or source['status']!='complete' or not store.segments(transcript_id):
                raise ValueError('Cần bản chép lời hoàn chỉnh thuộc âm thanh này trước khi dịch.')
            transcript=transcript_id
        else:
            transcript=store.new_transcript(audio_id,'SenseVoiceSmall int8 + Silero VAD')
        version_id=store.new_version(audio_id,transcript,**options)
    payload=dict(audio_id=audio_id,transcript_id=transcript,version_id=version_id,translation_mode=translation_mode)
    job=store.job('transcribe_translate',version_id,payload,previous['id'] if previous else None)
    store.set_version_status(version_id,'running')
    producer_done=threading.Event(); available=threading.Event(); emit_lock=threading.RLock()
    saved_rows=store.segments(transcript,version_id)
    failures={}; seconds=[saved_rows[-1]['end'] if saved_rows else 0]

    def emit(kind='progress'):
        with emit_lock:
            rows=store.segments(transcript,version_id)
            done=sum(row['translation_status']=='complete' for row in rows)
            progress(dict(type=kind,**payload,seconds=seconds[0],recognized=len(rows),translated=done,
                          pending=len(rows)-done,asr_done=producer_done.is_set(),
                          translation_error=failures.get('translation','')))

    def translate():
        active=[]
        try:
            if translation_mode=='whole':
                # Do not call Codex, including capability discovery, before ASR
                # has saved a complete transcript. Failed/cancelled ASR stays local.
                while not producer_done.wait(.1):
                    if cancel.is_set(): raise InterruptedError('Đã dừng dịch.')
                if cancel.is_set(): raise InterruptedError('Đã dừng dịch.')
                source=store.one('SELECT status FROM transcripts WHERE id=?',(transcript,))
                if source['status']!='complete': return
            if cancel.is_set(): raise InterruptedError('Đã dừng dịch.')
            executable=find_codex(store.setting('codex_path'))
            actual_models=known_models or capabilities(executable,store.root/'work',cancel)['models']
            validate_selection(actual_models,options['model'],options['effort'])
            while True:
                if cancel.is_set(): raise InterruptedError('Đã dừng dịch.')
                available.clear()
                finished=producer_done.is_set()
                rows=store.segments(transcript,version_id)
                active=[row for row in rows if row['translation_status']!='complete']
                if translation_mode=='parallel': active=active[:6]
                if not active:
                    # Read the completion flag BEFORE the outbox snapshot.
                    # A producer finishing just after this SELECT may have
                    # committed another row, so one more read is necessary.
                    if finished: break
                    available.wait(.2); continue
                with store.transaction() as db:
                    db.executemany("UPDATE translations SET status='translating',error='',attempts=attempts+1 WHERE version_id=? AND segment_id=?",
                                   [(version_id,row['id']) for row in active])
                emit()
                previous_text=[dict(zh=row['zh'],vi=row['vi']) for row in rows if row['translation_status']=='complete']
                if translation_mode=='parallel': previous_text=previous_text[-2:]
                for attempt in range(3):
                    try:
                        kwargs={'timeout':900} if translation_mode=='whole' else {}
                        result=translate_segments(executable,store.root/'work',actual_models,
                            options['model'],options['effort'],options['context'],options['glossary'],
                            active,cancel,previous_text,**kwargs)
                        if cancel.is_set(): raise InterruptedError('Đã dừng dịch.')
                        store.translation_results(version_id,result)
                        break
                    except InterruptedError: raise
                    except Exception:
                        if attempt==2: raise
                        if cancel.wait(2**attempt): raise InterruptedError('Đã dừng dịch.')
                active=[]; emit()
        except Exception as error:
            failures['translation']=str(error)
            with store.transaction() as db:
                db.execute("UPDATE translations SET status='queued' WHERE version_id=? AND status='translating'",(version_id,))
            if not isinstance(error,InterruptedError):
                with store.transaction() as db:
                    db.executemany("UPDATE translations SET status='failed',error=? WHERE version_id=? AND segment_id=?",
                                   [(str(error),version_id,row['id']) for row in active])
            emit('translation_error')

    emit('started')
    translator=threading.Thread(target=translate,name='file-translation',daemon=True)
    translator.start()
    try:
        source=store.one('SELECT status FROM transcripts WHERE id=?',(transcript,))
        if source['status']!='complete':
            def asr_progress(item):
                if 'seconds' in item: seconds[0]=max(seconds[0],item['seconds'])
                if item.get('type')=='final':
                    seconds[0]=item['end']; available.set()
                emit()
            transcribe_job(store,models,audio_id,asr_progress,cancel,threads,
                transcript_id=transcript,version_id=version_id,manage_job=False)
    except Exception as error:
        failures['asr']=str(error)
    finally:
        producer_done.set(); available.set(); emit()
        # Only this background coordinator waits. The ASR producer never waits
        # for a network response, and no worker outlives its task or recovery.
        translator.join()
    source=store.one('SELECT status FROM transcripts WHERE id=?',(transcript,))
    rows=store.segments(transcript,version_id)
    complete=source['status']=='complete' and bool(rows) and all(row['translation_status']=='complete' for row in rows)
    state='complete' if complete else 'interrupted' if cancel.is_set() else 'partial'
    store.set_version_status(version_id,state)
    message=' · '.join(failures.values())
    store.job('transcribe_translate',version_id,payload,job,'complete' if complete else 'interrupted' if cancel.is_set() else 'failed',message)
    emit('finished')
    return dict(**payload,status=state,warnings=failures,cancelled=cancel.is_set())
