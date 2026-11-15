import numpy as np
import pytest
import soundfile as sf
from PySide6.QtCore import Qt
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QComboBox
from PySide6.QtGui import QFontInfo, QColor
from chinese_transcriber.file_page import WaveformSlider
from chinese_transcriber.storage import Store
from chinese_transcriber.theme import LIGHT
from chinese_transcriber.widgets import PAGES
from chinese_transcriber.workspace import WorkspaceWindow


@pytest.fixture
def file_window(qtbot, tmp_path):
    source = tmp_path / ('Southwest Jiaotong University Xipu Campus ' * 2 + 'Dianqiuan 3.wav')
    sf.write(source, np.zeros(16000, dtype='float32'), 16000)
    store = Store(tmp_path / 'library')
    audio, _ = store.import_audio(source, 1)
    window = WorkspaceWindow(store)
    qtbot.addWidget(window)
    window.show()
    window.open_audio(audio['id'])
    yield window
    window.waveform_cancel.set()
    window.pool.waitForDone()


def test_file_workflow_empty_transcript_and_translation_actions(file_window, qtbot, monkeypatch):
    window = file_window
    assert window.timeline.empty.isVisible()
    assert not window.translate_button.isEnabled()
    assert not window.file_page.export_zh.isEnabled()
    assert not window.file_page.export_vi.isEnabled()
    assert window.file_page.steps.completed == 1
    transcript = window.store.new_transcript(window.audio_id, 'test')
    segment = window.store.append_segment(transcript, 0, 1, '你好。')
    window.store.set_transcript_status(transcript, 'complete')
    window.transcript_id = transcript
    window.fill_timeline()
    assert not window.timeline.empty.isVisible()
    assert window.translate_button.isEnabled()
    assert window.file_page.export_zh.isEnabled()
    assert not window.file_page.export_vi.isEnabled()
    version = window.store.new_version(window.audio_id, transcript, 'test', 'low', '', [])
    window.store.translation_result(version, segment, 'Xin chào.', 'Lời chào')
    window.store.set_version_status(version, 'complete')
    window.open_audio(window.audio_id, version)
    assert window.file_page.steps.completed == 3
    assert window.file_page.export_vi.isEnabled()
    window.notes_toggle.click()
    assert 'Lời chào' in window.timeline.item(0, 2).text()
    calls = []
    monkeypatch.setattr(window, 'export', calls.append)
    window.file_page.export_zh.trigger()
    window.file_page.export_vi.trigger()
    assert calls == ['zh', 'vi']
    window.file_page.versions.setCurrentIndex(0)
    window.file_page.versions.activated.emit(0)
    assert window.version_id is None
    assert window.timeline.item(0, 2).text() == 'Chưa dịch'
    selector = window.file_page.versions
    selector.setCurrentIndex(selector.findData(version))
    selector.activated.emit(selector.currentIndex())
    assert window.version_id == version
    assert 'Xin chào.' in window.timeline.item(0, 2).text()
    window.is_busy = True
    window.refresh_file_state()
    assert not window.transcribe_button.isEnabled()
    assert not window.translate_button.isEnabled()
    window.is_busy = False
    window.refresh_file_state()


def test_long_filename_and_fixed_sidebar_without_page_headers(file_window, qtbot):
    window = file_window
    for size in ((1440, 900), (1024, 700)):
        window.resize(*size)
        qtbot.wait(20)
        widths = (window.rail.width(), window.context.width())
        filename = window.file_page.filename
        shown = filename.display_text()
        assert shown.startswith('Southwest') and shown.endswith('Dianqiuan 3.wav')
        assert shown != filename.text()
        assert not filename.wordWrap()
        assert filename.toolTip() == filename.text()
        assert window.scroll.horizontalScrollBar().maximum() == 0
        assert window.scroll.verticalScrollBar().maximum() == 0
        for page, _, _ in PAGES:
            window.navigate(page)
            qtbot.wait(5)
            assert window.workspace_layout.count() == 1
            assert (window.rail.width(), window.context.width()) == widths
        window.navigate('file')


def test_seek_mouse_keyboard_and_playback_settings(file_window, qtbot):
    slider = WaveformSlider(LIGHT)
    qtbot.addWidget(slider)
    slider.setRange(0, 1000)
    slider.resize(400, 36)
    slider.show()
    moved = QSignalSpy(slider.sliderMoved)
    qtbot.mouseClick(slider, Qt.MouseButton.LeftButton, pos=slider.rect().center())
    assert 450 < slider.value() < 550
    assert moved.count() == 1
    qtbot.keyClick(slider, Qt.Key.Key_End)
    assert slider.value() == 1000
    window = file_window
    speed = window.file_page.findChild(QComboBox, 'playback_speed')
    speed.setCurrentIndex(speed.findData(1.25))
    window.file_page.volume_button.click()
    assert window.player.playbackRate() == 1.25
    assert window.audio_output.isMuted()
    window.navigate('library')
    window.navigate('file')
    assert window.player.playbackRate() == 1.25
    assert window.file_page.volume_button.accessibleName() == 'Bật âm thanh'


def test_approved_typography_and_solid_play_glyph(file_window, qtbot):
    window = file_window
    window.resize(1440, 900)
    qtbot.wait(20)
    page = window.file_page
    # These sizes come from the approved mockup; verify the resolved font,
    # including machines without the Windows Segoe UI family installed.
    for widget, pixels, weight in (
        (window.file_import_button, 17, 600),
        (window.model_selector.model_label, 15, 400),
        (window.model_selector.effort_label, 16, 700),
        (page.steps, 18, 500),
        (page.filename, 22, 700),
        (page.timeline.empty_title, 30, 700),
    ):
        assert QFontInfo(widget.font()).family() == 'Inter'
        assert widget.font().pixelSize() == pixels
        assert int(widget.font().weight()) == weight
    assert window.file_import_button.height() == 48
    assert window.model_selector.height() == 116
    assert window.transcribe_button.text() == 'Chép lời tiếng Trung'
    assert window.translate_button.text() == 'Tạo bản dịch'
    assert page.play_button.size().width() == page.play_button.size().height() == 52
    rendered = page.play_button.grab().toImage()
    assert rendered.pixelColor(25, 26) == QColor(window.colors['on_primary'])


def test_media_loading_does_not_overwrite_library_pages(file_window, qtbot):
    from PySide6.QtCore import QUrl
    window = file_window
    source = QUrl.fromLocalFile(str(window.store.audio_path(window.audio_id)))
    # Reuse native media handles while SQLite opens and checkpoints connections.
    # A prior Windows/CRT logging path wrote "Input #0, wav" into a DB page.
    for i in range(20):
        window.player.setSource(QUrl())
        window.player.setSource(source)
        window.store.set_setting('media_probe', i)
        qtbot.wait(5)
        with window.store.connect() as db:
            assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'


def test_partial_asr_does_not_enable_complete_vietnamese_export(file_window):
    window=file_window; store=window.store
    transcript=store.new_transcript(window.audio_id,'test')
    segment=store.append_segment(transcript,0,1,'你好。')
    store.set_transcript_status(transcript,'interrupted')
    version=store.new_version(window.audio_id,transcript,'test','low','',[])
    store.translation_result(version,segment,'Xin chào.')
    store.set_version_status(version,'partial')
    window.open_audio(window.audio_id,version)
    assert window.file_page.export_zh.isEnabled()
    assert not window.file_page.export_vi.isEnabled()
    store.set_transcript_status(transcript,'complete'); store.set_version_status(version,'complete')
    window.refresh_file_state()
    assert window.file_page.export_vi.isEnabled()
