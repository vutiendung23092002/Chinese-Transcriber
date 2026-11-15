"""Native playback regressions run out of process so a GIL deadlock times out."""
import json
import os
from pathlib import Path
import subprocess
import sys
from chinese_transcriber.audio import ffmpeg, hidden_process


PLAY_WHILE_TRANSLATING = r'''
import json,sys,time,threading
from pathlib import Path
from unittest.mock import patch
from PySide6.QtCore import QTimer,qInstallMessageHandler
from PySide6.QtWidgets import QApplication
from chinese_transcriber.storage import Store
from chinese_transcriber.theme import load_fonts
from chinese_transcriber.workspace import WorkspaceWindow
app=QApplication([]); load_fonts(app)
store=Store(Path(sys.argv[1])/'library')
audio,_=store.import_audio(Path(sys.argv[1])/'source.m4a',3)
transcript=store.new_transcript(audio['id'],'fixture')
for i in range(11): store.append_segment(transcript,i/4,(i+1)/4,'\u4f60\u597d\u3002')
store.set_transcript_status(transcript,'complete')
model=dict(model='test',displayName='Test',supportedReasoningEfforts=[dict(reasoningEffort='low')],defaultReasoningEffort='low')
store.set_setting('model','test'); store.set_setting('effort','low')
window=WorkspaceWindow(store); window.models=[model]; window.audio_output.setMuted(True)
window.open_audio(audio['id']); window.show()
if '--legacy-handler' in sys.argv:
    # Reproduce the old callback's dependency on the GIL, not its log contents.
    qInstallMessageHandler(lambda *args:None)
errors=[]; window.error=errors.append; beats=[]; progress=[]; main=threading.get_ident()
original=window.translation_progress
def on_progress(item):
    assert threading.get_ident()==main
    progress.append(item['done']); original(item)
window.translation_progress=on_progress
def translate(*args,**kwargs):
    time.sleep(.3)
    return [dict(id=row['id'],vi='Translation '+row['zh'],note='') for row in args[7]]
timer=QTimer(); timer.timeout.connect(lambda:beats.append(time.monotonic())); timer.start(10)
with patch('chinese_transcriber.workspace.find_codex',lambda *_:'test.exe'), \
     patch('chinese_transcriber.workspace.capabilities',lambda *_:dict(models=[model])), \
     patch('chinese_transcriber.codex.translate_segments',translate):
    QTimer.singleShot(0,window.translate)
    QTimer.singleShot(20,window.toggle_play)
    QTimer.singleShot(300,lambda:window.player.setPosition(500))
    QTimer.singleShot(600,window.toggle_play)
    QTimer.singleShot(900,window.toggle_play)
    QTimer.singleShot(1800,app.quit)
    app.exec()
window.waveform_cancel.set(); window.pool.waitForDone(3000)
rows=store.segments(transcript,window.version_id)
with store.connect() as db: integrity=db.execute('PRAGMA integrity_check').fetchone()[0]
report=dict(heartbeats=len(beats),progress=progress,complete=all(row['translation_status']=='complete' for row in rows),
            rows=len(rows),errors=errors,integrity=integrity,busy=window.is_busy)
window.player.stop(); window.close()
print(json.dumps(report),flush=True)
assert report['heartbeats']>30 and report['complete'] and report['rows']==11
assert progress==[0,6,6,11] and not errors and integrity=='ok' and not window.is_busy
'''


def test_media_playback_during_translation_keeps_ui_responsive_and_results(tmp_path):
    subprocess.run([ffmpeg(), '-nostdin', '-v', 'error', '-f', 'lavfi', '-i',
                    'sine=frequency=440:sample_rate=16000:duration=3', '-c:a', 'aac',
                    str(tmp_path/'source.m4a')], check=True, capture_output=True, **hidden_process())
    env=dict(os.environ,QT_QPA_PLATFORM='offscreen',CHINESE_TRANSCRIBER_NO_PROBE='1')
    result=subprocess.run([sys.executable,'-c',PLAY_WHILE_TRANSLATING,str(tmp_path)],
                          env=env,capture_output=True,text=True,timeout=20,**hidden_process())
    assert result.returncode==0, result.stdout+'\n'+result.stderr
    report=json.loads(result.stdout.strip().splitlines()[-1])
    assert report['complete'] and report['integrity']=='ok'


def test_media_configuration_does_not_install_python_message_handler():
    # Installing a Python handler requires the GIL on native decoder threads.
    # Checking the public Qt API also catches reintroducing that deadlock even
    # if a particular audio driver does not happen to trigger it in playback.
    from PySide6.QtCore import qInstallMessageHandler
    from chinese_transcriber.multimedia import configure_multimedia_logging
    configure_multimedia_logging()
    assert qInstallMessageHandler(None) is None
    assert 'QT_FFMPEG_DEBUG' in os.environ
