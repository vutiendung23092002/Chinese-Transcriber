import threading
import numpy as np
import soundfile as sf
from PySide6.QtCore import Qt,QTimer
from PySide6.QtWidgets import QPushButton
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


def test_whole_mode_toggle_waits_for_asr_and_updates_every_timeline_row(qtbot,tmp_path,monkeypatch):
    models=[dict(model='test',displayName='Test',supportedReasoningEfforts=[dict(reasoningEffort='low')],defaultReasoningEffort='low')]
    source=tmp_path/'source.wav'; sf.write(source,np.zeros(16000,dtype='float32'),16000)
    store=Store(tmp_path/'library'); audio,_=store.import_audio(source,8)
    store.set_setting('model','test'); store.set_setting('effort','low')
    produced=threading.Event(); finish_asr=threading.Event(); translating=threading.Event(); finish_translation=threading.Event(); calls=[]
    class Recognizer:
        def __init__(self,*args): pass
        def transcribe(self,path,final,*args,**kwargs):
            for i in range(8): final(dict(start=i,end=i+1,zh=f'句子{i+1}',timing='vad-boundary'))
            produced.set(); assert finish_asr.wait(5)
    def translate(*args,**kwargs):
        assert store.latest_transcript(audio['id'])['status']=='complete'
        calls.append(args[7]); translating.set(); assert finish_translation.wait(5)
        return [dict(id=row['id'],vi='Bản dịch '+row['zh'],note='') for row in args[7]]
    monkeypatch.setattr(asr,'Recognizer',Recognizer)
    monkeypatch.setattr(pipeline,'find_codex',lambda *_:'test.exe')
    monkeypatch.setattr(pipeline,'translate_segments',translate)
    window=WorkspaceWindow(store); qtbot.addWidget(window); window.models=models
    window.show(); window.open_audio(audio['id']); errors=[]; window.error=errors.append
    assert not window.file_translation_toggle.isChecked()
    assert not any(button.text()=='Tạo bản dịch' for button in window.context.findChildren(QPushButton))
    qtbot.mouseClick(window.file_translation_toggle,Qt.MouseButton.LeftButton)
    assert store.setting('file_translation_mode')=='whole'
    window.navigate('dashboard'); window.navigate('file')
    assert window.file_translation_toggle.isChecked()
    qtbot.mouseClick(window.transcribe_button,Qt.MouseButton.LeftButton)
    try:
        qtbot.waitUntil(lambda:produced.is_set() and window.timeline.rowCount()==8,timeout=4000)
        assert not calls and all(window.timeline.item(i,2).text()=='Chờ dịch' for i in range(8))
        assert not window.file_translation_toggle.isEnabled()
        assert 'Chờ chép lời hoàn tất' in window.statusBar().currentMessage()
        qtbot.mouseClick(window.file_translation_toggle,Qt.MouseButton.LeftButton)
        assert store.setting('file_translation_mode')=='whole'
        finish_asr.set()
        qtbot.waitUntil(lambda:translating.is_set() and window.timeline.item(0,2).text()=='Đang dịch…',timeout=4000)
        assert len(calls)==1 and len(calls[0])==8
        assert window.file_page.steps.completed==2
    finally:
        finish_asr.set(); finish_translation.set()
        qtbot.waitUntil(lambda:not window.is_busy,timeout=5000)
        window.waveform_cancel.set(); window.pool.waitForDone()
    assert not errors and window.file_translation_toggle.isEnabled()
    assert window.file_page.export_vi.isEnabled() and window.file_page.steps.completed==3
    assert all(window.timeline.item(i,2).text()==f'Bản dịch 句子{i+1}' for i in range(8))


def test_single_primary_action_reuses_local_transcript_for_whole_translation(qtbot,tmp_path,monkeypatch):
    models=[dict(model='test',displayName='Test',supportedReasoningEfforts=[dict(reasoningEffort='low')],defaultReasoningEffort='low')]
    source=tmp_path/'source.wav'; sf.write(source,np.zeros(16000,dtype='float32'),16000)
    store=Store(tmp_path/'library'); audio,_=store.import_audio(source,8)
    store.set_setting('model','test'); store.set_setting('effort','low'); store.set_setting('file_translation_mode','whole')
    transcript=store.new_transcript(audio['id'],'saved')
    for i in range(8): store.append_segment(transcript,i,i+1,f'句子{i+1}')
    store.set_transcript_status(transcript,'complete'); calls=[]
    monkeypatch.setattr(pipeline,'find_codex',lambda *_:'test.exe')
    monkeypatch.setattr(pipeline,'transcribe_job',lambda *a,**k:(_ for _ in ()).throw(AssertionError('No ASR needed')))
    def translate(*args,**kwargs):
        calls.append(args[7]); return [dict(id=row['id'],vi='Bản dịch',note='') for row in args[7]]
    monkeypatch.setattr(pipeline,'translate_segments',translate)
    window=WorkspaceWindow(store); qtbot.addWidget(window); window.models=models
    window.show(); window.open_audio(audio['id'],transcript_only=True); errors=[]; window.error=errors.append
    assert window.transcribe_button.text()=='Dịch bản chép lời'
    qtbot.mouseClick(window.transcribe_button,Qt.MouseButton.LeftButton)
    qtbot.waitUntil(lambda:not window.is_busy,timeout=5000)
    assert not errors and len(calls)==1 and len(calls[0])==8
    assert window.transcript_id==transcript and len(store.rows('SELECT * FROM transcripts'))==1
    window.waveform_cancel.set(); window.pool.waitForDone()
