import threading
import numpy as np
import soundfile as sf
from PySide6.QtCore import Qt,QTimer
from chinese_transcriber import asr,pipeline
from chinese_transcriber.storage import Store
from chinese_transcriber.workspace import WorkspaceWindow


def test_combined_action_shows_new_chinese_while_translation_is_waiting(qtbot,tmp_path,monkeypatch):
    models=[dict(model='test',displayName='Test',supportedReasoningEfforts=[dict(reasoningEffort='low')],defaultReasoningEffort='low')]
    source=tmp_path/'source.wav'; sf.write(source,np.zeros(48000,dtype='float32'),16000)
    store=Store(tmp_path/'library'); audio,_=store.import_audio(source,3)
    store.set_setting('model','test'); store.set_setting('effort','low')
    translating=threading.Event(); produced=threading.Event(); release=threading.Event()
    class Recognizer:
        def __init__(self,*args): pass
        def transcribe(self,path,final,cancel,progress,**kwargs):
            final(dict(start=0,end=1,zh='第一句',timing='vad-boundary'))
            assert translating.wait(3)
            for i in (1,2): final(dict(start=i,end=i+1,zh=f'句子{i+1}',timing='vad-boundary'))
            produced.set()
    def translate(*args):
        translating.set(); assert release.wait(3)
        return [dict(id=row['id'],vi='Bản dịch',note='') for row in args[7]]
    monkeypatch.setattr(asr,'Recognizer',Recognizer)
    monkeypatch.setattr(pipeline,'find_codex',lambda *_:'test.exe')
    monkeypatch.setattr(pipeline,'translate_segments',translate)
    window=WorkspaceWindow(store); qtbot.addWidget(window); window.models=models
    window.show(); window.open_audio(audio['id'])
    errors=[]; window.error=errors.append
    beats=[]; timer=QTimer(window); timer.timeout.connect(lambda:beats.append(1)); timer.start(10)
    assert window.transcribe_button.text()=='Chép lời và dịch'
    qtbot.mouseClick(window.transcribe_button,Qt.MouseButton.LeftButton)
    try:
        qtbot.waitUntil(lambda:produced.is_set() and window.timeline.rowCount()==3,timeout=4000)
        assert window.is_busy and len(beats)>3
        assert window.timeline.item(0,2).text()=='Đang dịch…'
        assert window.timeline.item(1,2).text()=='Chờ dịch'
        assert window.file_page.versions.currentData()==window.version_id
        assert not window.transcribe_button.isEnabled()
    finally: release.set()
    qtbot.waitUntil(lambda:not window.is_busy,timeout=5000)
    assert not errors and window.timeline.rowCount()==3
    assert all(window.timeline.item(i,2).text()=='Bản dịch' for i in range(3))
    assert store.versions(audio['id'])[0]['status']=='complete'
    assert window.file_page.export_vi.isEnabled()
    timer.stop(); window.waveform_cancel.set(); window.pool.waitForDone()
