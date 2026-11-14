"""Actual widget and persistent pipeline checks; fixtures stay outside user data."""
import json
import os
from pathlib import Path
import threading
os.environ['QT_QPA_PLATFORM']='offscreen'
os.environ['CHINESE_TRANSCRIBER_NO_PROBE']='1'
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer,QCoreApplication,QEvent
import soundfile as sf
from chinese_transcriber.storage import Store
from chinese_transcriber.models import ModelManager
from chinese_transcriber.asr import transcribe_job
from chinese_transcriber.codex import capabilities,find_codex,translate_version
from chinese_transcriber.workspace import WorkspaceWindow
from chinese_transcriber.audio import export_txt
from chinese_transcriber.widgets import PAGES
from chinese_transcriber.theme import load_fonts

def main():
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('--ui-only',action='store_true'); args=parser.parse_args()
    root=Path('.test-data/integration').resolve(); root.mkdir(parents=True,exist_ok=True)
    store=Store(root); models=ModelManager('models')
    wav=models.path('sensevoice')/'test-zh.wav'
    audio,_=store.import_audio(wav,sf.info(wav).duration)
    if args.ui_only:
        version=store.versions(audio['id'])[0]['id']; transcript=store.versions(audio['id'])[0]['transcript_id']
        actual=json.loads(Path('.test-data/codex-capabilities.json').read_text(encoding='utf-8'))
    else:
        transcript=transcribe_job(store,models,audio['id'],lambda _:None,threading.Event())
        actual=capabilities(find_codex(),root/'work')
        version=store.new_version(audio['id'],transcript,'gpt-6-luna','low','Thông báo giờ mở cửa',[])
        translate_version(store,actual['path'],version,actual['models'],lambda _:None,threading.Event())
    export_txt(store,transcript,version,root/'zh.txt','zh')
    export_txt(store,transcript,version,root/'vi.txt','vi')
    app=QApplication([]); load_fonts(app); window=WorkspaceWindow(store)
    window.models=actual['models']; window.codex_status=actual
    window.audio_id=audio['id']; window.transcript_id=transcript; window.version_id=version
    report=[]
    for width,height in [(1440,900),(1366,768),(1100,720)]:
        window.resize(width,height); window.show(); app.processEvents()
        for page,_,_ in PAGES:
            window.navigate(page); QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete); app.processEvents()
            fields=window.context.findChildren(__import__('PySide6.QtWidgets',fromlist=['QComboBox']).QComboBox)
            report.append(dict(page=page,requested=[width,height],actual=[window.width(),window.height()],rail=window.rail.width(),context=window.context.width(),context_scrollbars=len(window.context.findChildren(__import__('PySide6.QtWidgets',fromlist=['QScrollArea']).QScrollArea)),fields_inside=all(x.mapTo(window.context,x.rect().bottomRight()).y()<=window.context.height() for x in fields)))
            if width==1440: window.grab().save(str(root/('native-'+page+'.png')))
    output={'ui':report,'audio_files':len(store.list_audio()),'versions':len(store.versions(audio['id'])),'translated_segments':len(store.segments(transcript,version)),
        'exports':['zh.txt','vi.txt'],'codex_models':len(actual['models']),'quota_available':bool(actual['limits'].get('rateLimits'))}
    (root/'validation.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'native_views':len(report),'geometry_ok':all(x['fields_inside'] and not x['context_scrollbars'] for x in report),'versions':output['versions'],'translated_segments':output['translated_segments']},ensure_ascii=False))
    window.close(); app.processEvents()

if __name__=='__main__': main()
