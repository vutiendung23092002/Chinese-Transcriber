import threading
from types import SimpleNamespace
import numpy as np
import pytest
from PySide6.QtCore import Qt, QPoint, QObject, QEvent
from PySide6.QtGui import QFontInfo
from PySide6.QtWidgets import QLabel, QAbstractSlider, QWidget
from chinese_transcriber.storage import Store
from chinese_transcriber.workspace import WorkspaceWindow
from chinese_transcriber.recording import materialize_recording


@pytest.fixture
def live_window(qtbot,tmp_path,monkeypatch):
    monkeypatch.setattr('sounddevice.query_devices',lambda:[dict(name='Test microphone',max_input_channels=1)])
    monkeypatch.setattr('chinese_transcriber.microphone.default_input_index',lambda:0)
    window=WorkspaceWindow(Store(tmp_path/'library')); qtbot.addWidget(window)
    window.resize(1440,900); window.show(); window.navigate('live'); qtbot.wait(20)
    yield window
    if window.record_timer: window.record_timer.stop()
    window.recording=None
    window.pool.waitForDone()


def test_entering_live_does_not_flash_an_extra_window(live_window,qtbot,qapp):
    window=live_window
    shown=[]

    class WindowShows(QObject):
        def eventFilter(self,widget,event):
            if event.type()==QEvent.Type.Show and isinstance(widget,QWidget):
                if widget.isWindow() and widget is not window:
                    shown.append((widget.metaObject().className(),widget.size().width(),widget.size().height()))
            return False

    observer=WindowShows()
    qapp.installEventFilter(observer)
    try:
        for mode in (0,1):
            window.change_theme(mode)
            for width,height in ((1440,900),(1024,700),(1440,900)):
                window.resize(width,height)
                window.navigate('dashboard')
                window.navigate('live')
                qtbot.wait(10)
        assert shown==[]
    finally:
        qapp.removeEventFilter(observer)


def test_live_layout_typography_and_responsive_transport(live_window,qtbot):
    window=live_window
    for width,height in ((1440,900),(1366,768),(1024,700),(1440,900)):
        window.resize(width,height); qtbot.wait(30)
        page=window.live_page
        assert page.body.itemAt(0).widget() is page.transport
        assert 'Sẵn sàng ghi âm' not in [x.text() for x in page.findChildren(QLabel)]
        assert window.scroll.horizontalScrollBar().maximum()==window.scroll.verticalScrollBar().maximum()==0
        assert window.content_layout.count()==1
        assert page._narrow==(width==1024)
        assert page.mapTo(window,QPoint()).y()==window.context_panel.mapTo(window,QPoint()).y()
        assert page.mapTo(window,page.rect().bottomRight()).y()==window.context_panel.mapTo(window,window.context_panel.rect().bottomRight()).y()
        assert page.record_button.height()==44
        for control in (page.record_button,page.pause_button,page.stop_button,page.draft,page.timeline):
            assert page.contentsRect().contains(control.mapTo(page,QPoint()))
            assert page.contentsRect().contains(control.mapTo(page,control.rect().bottomRight()))
        assert page.clock.text()=='00:00' and page.meter.value()==0
        assert page.record_button.isEnabled() and not page.pause_button.isEnabled() and not page.stop_button.isEnabled()
        assert page.timeline.empty.isVisible()
        assert page.interim.placeholderText()=='Câu đang nghe sẽ xuất hiện tại đây.'
        assert QFontInfo(window.mic_select.font()).family()=='Inter'
        assert window.mic_select.font().pixelSize()==15
        assert page.clock.font().pixelSize()==30 and int(page.clock.font().weight())==700
    window.change_theme(1)
    assert window.live_page.timeline.horizontalHeaderItem(1).text()=='TIẾNG TRUNG'


def test_interim_final_translation_and_follow_state(live_window,qtbot):
    window=live_window
    window.live_signals.event.emit(dict(type='interim',zh='这是正在识别的句子'))
    assert window.timeline.rowCount()==0
    assert window.live_page.interim.toPlainText()=='这是正在识别的句子'
    window.live_signals.event.emit(dict(type='final',id='one',start=0,end=2,zh='你好。',translation_status='queued'))
    assert window.timeline.rowCount()==1 and not window.timeline.empty.isVisible()
    assert window.timeline.item(0,2).text()=='Trong hàng đợi dịch'
    window.live_signals.event.emit(dict(type='translation',id='one',vi='Xin chào.',translation_status='complete'))
    assert window.timeline.item(0,2).text()=='Xin chào.'
    first=window.timeline.item(0,1)
    window.live_signals.event.emit(dict(type='level',level=57))
    window.live_signals.event.emit(dict(type='interim',zh='下一句'))
    assert window.timeline.item(0,1) is first
    for i in range(15):
        window.live_event(dict(type='final',id=str(i),start=i+2,end=i+3,zh='句子',translation_status='untranslated'))
    qtbot.wait(20)
    scrollbar=window.timeline.verticalScrollBar()
    assert scrollbar.value()==scrollbar.maximum()
    scrollbar.triggerAction(QAbstractSlider.SliderAction.SliderSingleStepSub)
    assert not window.follow_live.isChecked()
    position=scrollbar.value()
    window.live_event(dict(type='final',id='last',start=20,end=21,zh='最后一句'))
    assert scrollbar.value()==position
    window.navigate('library'); window.navigate('live')
    assert not window.follow_live.isChecked()
    assert window.live_page.interim.toPlainText()=='下一句'
    qtbot.mouseClick(window.follow_live,Qt.MouseButton.LeftButton)
    assert window.timeline.verticalScrollBar().value()==window.timeline.verticalScrollBar().maximum()


def test_microphone_selection_is_remembered_by_name_and_driver(live_window,monkeypatch):
    window=live_window
    window.capture_options()
    assert window.store.setting('mic_device_identity')==dict(name='Test microphone',hostapi='')
    monkeypatch.setattr('sounddevice.query_devices',lambda:[dict(name='New unrelated microphone',max_input_channels=1)])
    window.navigate('dashboard'); window.navigate('live')
    assert window.mic_select.currentData() is None
    assert 'Hãy chọn lại mic' in window.mic_select.toolTip()
    errors=[]; window.error=errors.append; window.start_recording()
    assert errors and 'chọn microphone' in errors[0]


def test_live_start_pause_resume_stop_and_save(live_window,qtbot,monkeypatch):
    window=live_window; release=threading.Event(); errors=[]
    window.error=lambda text:errors.append(text)
    class Session:
        def __init__(self,*args,**kwargs):
            self.samples=0; self.paused=False; self.closed=threading.Event()
        def start(self): return self
        def pause(self): self.paused=not self.paused; return self.paused
        def stop(self):
            release.wait(3); self.closed.set()
            pcm=window.store.root/'recordings'/'test-session.pcm'
            pcm.write_bytes(np.zeros(self.samples,dtype='<i2').tobytes())
            payload=dict(path='recordings/test-session.pcm',segments=[dict(start=0,end=1.8,zh='你好。',timing='vad-boundary')])
            job=window.store.job('recording','test-session',payload)
            return materialize_recording(window.store,payload,job)
    monkeypatch.setattr('chinese_transcriber.workspace.LiveSession',Session)
    qtbot.mouseClick(window.record_button,Qt.MouseButton.LeftButton)
    qtbot.waitUntil(lambda:window.recording is not None and not window.is_busy)
    assert window.live_page.status_text.text()=='Chờ microphone'
    assert window.live_page.clock.text()=='00:00'
    assert not window.mic_select.isEnabled() and not window.model_selector.isEnabled()
    window.recording.samples=32000
    window.live_event(dict(type='level',level=64)); window.update_record_timer()
    assert window.live_page.clock.text()=='00:02' and window.microphone_level.value()==64
    qtbot.mouseClick(window.pause_button,Qt.MouseButton.LeftButton)
    assert window.pause_button.text()=='Tiếp tục' and window.live_page.status_text.text()=='Tạm dừng'
    assert window.microphone_level.value()==0 and window.live_page.clock.text()=='00:02'
    qtbot.mouseClick(window.pause_button,Qt.MouseButton.LeftButton)
    assert window.pause_button.text()=='Tạm dừng' and window.live_page.status_text.text()=='Đang ghi âm'
    try:
        qtbot.mouseClick(window.stop_button,Qt.MouseButton.LeftButton)
        assert window.live_page.status_text.text()=='Đang lưu…'
        assert not window.pause_button.isEnabled() and not window.stop_button.isEnabled()
    finally:
        release.set()
    qtbot.waitUntil(lambda:window.recording is None and not window.is_busy)
    assert errors==[] and window.page=='file'
    assert window.store.list_audio()[0]['duration']==2
    assert window.timeline.item(0,1).text()=='你好。'
    assert window.store.audio_path(window.audio_id).exists()


def test_zero_sample_stop_does_not_claim_saved_recording(live_window,qtbot):
    window=live_window; errors=[]; window.error=errors.append
    session=SimpleNamespace(samples=0,paused=False,closed=threading.Event())
    session.stop=lambda:dict(audio_id=None,warning='Microphone chưa trả dữ liệu âm thanh.')
    window.recording=session; window.refresh_live_state()
    assert window.live_page.status_text.text()=='Chờ microphone'
    assert window.live_page.clock.text()=='00:00'
    qtbot.mouseClick(window.stop_button,Qt.MouseButton.LeftButton)
    qtbot.waitUntil(lambda:window.recording is None and not window.is_busy)
    assert errors==['Microphone chưa trả dữ liệu âm thanh.']
    assert window.store.list_audio()==[] and window.page=='live'
    assert window.live_page.clock.text()=='00:00' and window.microphone_level.value()==0
    assert window.record_button.isEnabled() and window.model_selector.isEnabled()
