"""Native Qt layout verification in fresh processes at common scale factors."""
import json
import os
from pathlib import Path
import subprocess
import sys

if '--child' in sys.argv:
    from PySide6.QtCore import QCoreApplication,QEvent
    from PySide6.QtWidgets import QApplication,QScrollArea,QComboBox,QPushButton,QPlainTextEdit,QSlider,QToolButton
    from chinese_transcriber.storage import Store
    from chinese_transcriber.workspace import WorkspaceWindow
    from chinese_transcriber.widgets import PAGES
    from chinese_transcriber.theme import load_fonts
    app=QApplication([]); load_fonts(app)
    window=WorkspaceWindow(Store('.test-data/scaling/'+os.environ['QT_SCALE_FACTOR']))
    checks=[]
    for size in ((1440,900),(1366,768),(1100,720),(1024,700)):
        window.resize(*size); window.show(); app.processEvents()
        expected=(window.rail.width(),window.context.width())
        for mode in (0,1):
            window.change_theme(mode)
            for key,_,_ in PAGES:
                window.navigate(key)
                QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete); app.processEvents()
                widgets=window.context.findChildren(QComboBox)+window.context.findChildren(QPushButton)+window.context.findChildren(QPlainTextEdit)+window.context.findChildren(QSlider)+window.context.findChildren(QToolButton)
                panel=window.context_panel
                inside=all(panel.contentsRect().contains(x.mapTo(panel,x.rect().topLeft())) and panel.contentsRect().contains(x.mapTo(panel,x.rect().bottomRight())) for x in widgets if x.isVisible())
                aligned=panel.geometry()==window.context.rect().adjusted(6,24,-6,-18) and panel.mapTo(window,panel.rect().bottomRight()).y()==window.rail.pill.mapTo(window,window.rail.pill.rect().bottomRight()).y()
                live_inside=True
                if key=='live':
                    page=window.live_page
                    controls=(page.transport,page.record_button,page.pause_button,page.stop_button,page.timeline,page.draft)
                    live_inside=all(page.contentsRect().contains(x.mapTo(page,x.rect().topLeft())) and page.contentsRect().contains(x.mapTo(page,x.rect().bottomRight())) for x in controls) and window.scroll.horizontalScrollBar().maximum()==0
                if key=='library':
                    page=window.library_page
                    controls=(page.search,page.import_button,page.table,page.details)
                    live_inside=all(page.contentsRect().contains(x.mapTo(page,x.rect().topLeft())) and page.contentsRect().contains(x.mapTo(page,x.rect().bottomRight())) for x in controls) and window.scroll.horizontalScrollBar().maximum()==0
                if key=='prompts':
                    page=window.glossary_page
                    controls=(page.name,page.context,page.table,page.add_button,page.delete_button,page.save_button)
                    live_inside=all(page.contentsRect().contains(x.mapTo(page,x.rect().topLeft())) and page.contentsRect().contains(x.mapTo(page,x.rect().bottomRight())) for x in controls) and window.scroll.horizontalScrollBar().maximum()==0
                checks.append(inside and aligned and live_inside and (window.rail.width(),window.context.width())==expected and not window.context.findChildren(QScrollArea))
    report=dict(scale=os.environ['QT_SCALE_FACTOR'],views=len(checks),ok=all(checks))
    print(json.dumps(report)); window.close()
    sys.exit(0 if report['ok'] else 1)

reports=[]
for factor in ('1','1.25','1.5','2'):
    env=dict(os.environ,QT_SCALE_FACTOR=factor,QT_QPA_PLATFORM='offscreen',CHINESE_TRANSCRIBER_NO_PROBE='1')
    result=subprocess.run([sys.executable,__file__,'--child'],env=env,capture_output=True,text=True,timeout=45)
    if result.returncode: raise RuntimeError(result.stdout+result.stderr)
    reports.append(json.loads(result.stdout.strip().splitlines()[-1]))
Path('.test-data/scaling/validation.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
print(json.dumps(reports))
