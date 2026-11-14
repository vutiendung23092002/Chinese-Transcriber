"""Capture the real settings widgets for comparison with the approved image.

Default data is an explicit visual fixture reproducing the mockup, not account data.
--live reads login/model/quota from the installed CLI. All storage remains isolated.
"""
import argparse
import json
import os
from pathlib import Path
from datetime import datetime

parser=argparse.ArgumentParser()
parser.add_argument('--live',action='store_true')
parser.add_argument('--windows',action='store_true',help='Render with the native Windows Qt backend')
args=parser.parse_args()
os.environ['QT_QPA_PLATFORM']='windows' if args.windows else 'offscreen'
os.environ['CHINESE_TRANSCRIBER_NO_PROBE']='1'

from PySide6.QtCore import Qt,QTimer,QCoreApplication,QEvent,QEventLoop
from PySide6.QtWidgets import QApplication,QDialog,QScrollArea
from chinese_transcriber.workspace import WorkspaceWindow
from chinese_transcriber.storage import Store
from chinese_transcriber.theme import load_fonts
from chinese_transcriber.codex import APPROVED_MODELS,capabilities,find_codex

root=Path(__file__).resolve().parents[1]; os.chdir(root)
output=root/'.test-data/settings-approved'; output.mkdir(parents=True,exist_ok=True)
kind='live' if args.live else 'fixture'
store=Store(output/(kind+'-library')); store.set_setting('theme','light')
app=QApplication([]); load_fonts(app); window=WorkspaceWindow(store)

def settle(milliseconds):
    app.processEvents(); loop=QEventLoop()
    QTimer.singleShot(milliseconds,loop.quit); loop.exec(); app.processEvents()

if args.windows: window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen,True)
if args.live:
    actual=capabilities(find_codex(),store.root/'work')
else:
    models=[dict(model=name.lower().replace(' ','-'),displayName=name,defaultReasoningEffort='medium',supportedReasoningEfforts=[dict(reasoningEffort=x) for x in ('low','medium','high')]) for name in APPROVED_MODELS]
    actual=dict(version='codex-cli 0.169.0-alpha.11.1',authenticated=True,models=models,limits={'rateLimits':{'primary':dict(usedPercent=8,windowDurationMins=300,resetsAt=int(datetime.fromisoformat('2026-11-14T20:40:00+07:00').timestamp())),'secondary':dict(usedPercent=47,windowDurationMins=10080,resetsAt=int(datetime.fromisoformat('2026-11-19T15:53:00+07:00').timestamp()))}})
window.models=actual['models']; window.codex_status=actual
if window.models:
    store.set_setting('model',window.models[0]['model']); store.set_setting('effort','medium')
window.show(); report=[]
for mode in (0,1):
    window.change_theme(mode)
    for width,height in ((1568,968),(1440,900),(1366,768),(1100,720),(1024,700)):
        window._settings_section='connection'
        window.resize(width,height); window.navigate('settings')
        QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete); settle(80)
        page=window.settings_page; rects=[card.geometry() for card in page.cards.values()]
        assert all(not a.intersects(b) for i,a in enumerate(rects) for b in rects[i+1:])
        assert not window.context.findChildren(QScrollArea)
        assert window.scroll.horizontalScrollBar().maximum()==0
        assert all(item.mapTo(window.context,item.rect().bottomRight()).y()<window.context.height() for item in page.nav.values())
        mode_name='dark' if mode else 'light'
        file=output/f'native-{kind}-{width}-{mode_name}.png'
        window.grab().save(str(file))
        report.append(dict(mode=mode,size=[width,height],two_columns=page._wide,cards={name:item.geometry().getRect() for name,item in page.cards.items()},screenshot=file.name))
        if width==1024:
            page.activate_section('asr'); settle(15)
            assert window.scroll.verticalScrollBar().value()>0
            assert page.nav['asr'].isChecked()

# Advanced controls remain reachable without expanding the overview.
window.resize(1440,900);dialogs=[]
for mode in (0,1):
    window.change_theme(mode);window.navigate('settings');settle(60);page=window.settings_page
    for name,show in [('connection',page.show_connection_details),('help',page.show_help),('models',page.show_models),('asr',page.show_asr_models)]:
        def capture(name=name,mode=mode):
            dialog=app.activeModalWidget()
            if isinstance(dialog,QDialog):
                dialog.grab().save(str(output/f'dialog-{kind}-{mode}-{name}.png'));dialogs.append(name);dialog.reject()
        QTimer.singleShot(40,capture);show()
assert len(dialogs)==8
window.close()
result=dict(data_source='installed CLI' if args.live else 'explicit mockup fixture',platform=app.platformName(),views=report,dialogs=dialogs)
(output/f'validation-{kind}.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(dict(source=result['data_source'],platform=result['platform'],views=len(report),dialogs=len(dialogs),geometry_ok=True)))
