"""Opt-in validation of the packaged runtime against an isolated library."""
import json
from pathlib import Path
import threading
import sys
from PySide6.QtCore import QEventLoop,QTimer,QUrl
from PySide6.QtMultimedia import QAudioDecoder
from .storage import Store
from .models import ModelManager
from .asr import transcribe_job
from .audio import audio_info,export_txt
from .codex import capabilities,find_codex,translate_version

def validate_runtime(root,wav,with_codex=False):
    store=Store(root)
    folder=Path(sys.executable).parent/'models' if getattr(sys,'frozen',False) else Path(__file__).resolve().parents[2]/'models'
    models=ModelManager(folder)
    report={'frozen':bool(getattr(sys,'frozen',False)),'python':sys.version.split()[0],'models_ready':all(models.ready(k) for k in ('sensevoice','paraformer','vad'))}
    try:
        audio,_=store.import_audio(wav,audio_info(wav)); duplicate,created=store.import_audio(wav,audio['duration'])
        if created or duplicate['id']!=audio['id']: raise AssertionError('Deduplication failed')
        transcript=transcribe_job(store,models,audio['id'],lambda _:None,threading.Event())
        segments=store.segments(transcript)
        report['asr_segments']=len(segments)
        export_txt(store,transcript,None,store.root/'selftest_zh.txt','zh')
        if with_codex:
            actual=capabilities(find_codex(),store.root/'work')
            version=store.new_version(audio['id'],transcript,'gpt-6-luna','low','Thông báo giờ phục vụ',[])
            translate_version(store,actual['path'],version,actual['models'],lambda _:None,threading.Event())
            export_txt(store,transcript,version,store.root/'selftest_vi.txt','vi')
            store.trash_version(version); store.restore_version(version)
            report.update(codex_models=len(actual['models']),json_ids_validated=True,vi_exported=True,shared_audio_retained=store.audio_path(audio['id']).is_file())
        decoder=QAudioDecoder(); loop=QEventLoop(); sample_count=[0]; errors=[]
        def data(): sample_count[0]+=decoder.read().sampleCount()
        decoder.bufferReady.connect(data); decoder.finished.connect(loop.quit)
        decoder.error.connect(lambda *args:(errors.append(decoder.errorString()),loop.quit()))
        decoder.setSource(QUrl.fromLocalFile(str(Path(wav).resolve()))); decoder.start()
        QTimer.singleShot(10000,loop.quit); loop.exec(); decoder.stop()
        report['qt_decoded_samples']=sample_count[0]; report['qt_decoder_errors']=errors
        if not sample_count[0]: raise ValueError('Qt audio decoder did not produce samples: '+str(errors))
        with store.connect() as db: report['sqlite_integrity']=db.execute('PRAGMA integrity_check').fetchone()[0]
        report['ok']=report['sqlite_integrity']=='ok' and bool(segments)
    except Exception as error:
        report['ok']=False; report['error']=str(error)
    (store.root/'selftest-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return 0 if report['ok'] else 2
