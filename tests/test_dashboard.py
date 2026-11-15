import numpy as np
from pathlib import Path
import soundfile as sf
from PySide6.QtCore import Qt, QMimeData, QUrl, QPoint, QPointF
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFontInfo
from PySide6.QtWidgets import QLabel, QToolButton
from chinese_transcriber.dashboard_page import ActionCard
from chinese_transcriber.storage import Store
from chinese_transcriber.workspace import WorkspaceWindow


def source_file(tmp_path):
    path = tmp_path / 'Southwest Jiaotong University Xipu Campus Dianqiguan 3.wav'
    sf.write(path, np.zeros(16000, dtype='float32'), 16000)
    return path


def test_dashboard_uses_real_counts_and_lesson_states(qtbot, tmp_path):
    store = Store(tmp_path / 'library')
    window = WorkspaceWindow(store)
    qtbot.addWidget(window)
    assert window.dashboard_page.metrics['audio'].value.text() == '0'
    assert window.dashboard_page.metrics['versions'].value.text() == '0'
    assert window.dashboard_page.metrics['latest'].value.text() == '—'
    assert window.dashboard_page.findChild(QLabel, 'dashboard_empty_library') is not None
    audio, _ = store.import_audio(source_file(tmp_path), 1)
    window.navigate('dashboard')
    assert window.dashboard_page.metrics['audio'].value.text() == '1'
    assert window.dashboard_page.lessons[0].status.text() == 'Chưa chép lời'
    transcript = store.new_transcript(audio['id'], 'test')
    segment = store.append_segment(transcript, 0, 1, '你好。')
    store.set_transcript_status(transcript, 'complete')
    window.navigate('dashboard')
    assert window.dashboard_page.lessons[0].status.text() == 'Đã chép lời'
    version = store.new_version(audio['id'], transcript, 'test', 'low', '', [])
    store.translation_result(version, segment, 'Xin chào.')
    store.set_version_status(version, 'complete')
    window.navigate('dashboard')
    assert window.dashboard_page.metrics['versions'].value.text() == '1'
    assert window.dashboard_page.metrics['latest'].value.text() != '—'
    assert window.dashboard_page.lessons[0].status.text() == 'Đã dịch'
    store.trash_audio(audio['id'])
    window.navigate('dashboard')
    assert window.dashboard_page.metrics['audio'].value.text() == '0'
    assert window.dashboard_page.metrics['versions'].value.text() == '0'
    assert window.dashboard_page.lessons == []


def test_dashboard_actions_typography_and_responsive_layout(qtbot, tmp_path, monkeypatch):
    store = Store(tmp_path / 'library')
    audio, _ = store.import_audio(source_file(tmp_path), 1)
    store.set_setting('model', 'gpt-6.1-sol')
    window = WorkspaceWindow(store)
    qtbot.addWidget(window)
    chosen, opened = [], []
    monkeypatch.setattr(window, 'choose_audio', lambda: chosen.append(True))
    monkeypatch.setattr(window, 'open_audio', opened.append)
    window.navigate('dashboard')
    window.resize(1440, 900)
    window.show()
    qtbot.wait(30)
    page = window.dashboard_page
    actions = window.dashboard_actions.cards
    assert page.metrics['model'].value.text() == 'GPT-6.1 Sol'
    assert QFontInfo(actions[0].heading.font()).family() == 'Inter'
    assert actions[0].heading.font().pixelSize() == 20
    assert int(actions[0].heading.font().weight()) == 700
    assert actions[0].height() == 190
    assert len(actions) == 3 and all(action.parentWidget()==window.dashboard_actions for action in actions)
    assert page.findChildren(ActionCard) == []
    assert window.context.findChildren(QToolButton) == []
    assert page.metrics['audio'].geometry().top() == 0
    assert page.lessons[0].open_button.height() == 44
    assert page.library_button.height() == 36
    assert page.drop_zone.heading.font().pixelSize() == 24
    actions[0].click()
    page.drop_zone.click()
    assert len(chosen) == 2
    page.lessons[0].open_button.click()
    assert opened == [audio['id']]
    page.library_button.click()
    assert window.page == 'library'
    qtbot.wait(30)
    assert window.context_panel.geometry() == window.context.rect().adjusted(6,24,-6,-18)
    assert window.context_panel.graphicsEffect() is not None
    window.navigate('dashboard')
    window.dashboard_actions.cards[1].click()
    assert window.page == 'live' and window.recording is None
    window.navigate('dashboard')
    window.dashboard_actions.cards[2].click()
    assert window.page == 'prompts'
    window.navigate('dashboard')
    for width, height in ((1440, 900), (1024, 700)):
        window.resize(width, height)
        qtbot.wait(40)
        assert window.scroll.horizontalScrollBar().maximum() == 0
        assert window.workspace_layout.count() == 1
        assert window.dashboard_page._narrow == (width == 1024)
        assert window.dashboard_actions.cards[0].height() == (190 if height==900 else 160)
        assert (window.rail.width(), window.context.width()) == ((82, 260) if width==1440 else (74, 238))
        panel = window.context_panel
        assert panel.parentWidget() == window.context
        assert panel.width() == window.context.width() - 12
        assert panel.mapTo(window,QPoint()).y() == window.dashboard_page.metrics['audio'].mapTo(window,QPoint()).y()
        assert panel.mapTo(window,panel.rect().bottomRight()).y() == window.rail.pill.mapTo(window,window.rail.pill.rect().bottomRight()).y()
        footer = window.context_layout.itemAt(window.context_layout.count()-1).widget()
        controls = [*window.dashboard_actions.cards,footer]
        for control in controls:
            assert panel.contentsRect().contains(control.mapTo(panel,QPoint()))
            assert panel.contentsRect().contains(control.mapTo(panel,control.rect().bottomRight()))
        assert window.dashboard_actions.cards[-1].mapTo(panel,window.dashboard_actions.cards[-1].rect().bottomRight()).y() < footer.mapTo(panel,QPoint()).y()


def test_dashboard_drop_zone_imports_one_local_file_and_respects_busy_state(qtbot, tmp_path, monkeypatch):
    window = WorkspaceWindow(Store(tmp_path / 'library'))
    qtbot.addWidget(window)
    imported = []
    monkeypatch.setattr(window, 'import_audio', imported.append)
    mime = QMimeData()
    path = source_file(tmp_path)
    mime.setUrls([QUrl.fromLocalFile(str(path))])
    zone = window.dashboard_page.drop_zone
    enter = QDragEnterEvent(QPointF(10, 10), Qt.DropAction.CopyAction, mime,
                           Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
    zone.dragEnterEvent(enter)
    assert enter.isAccepted() and zone.dragging
    drop = QDropEvent(QPointF(10, 10), Qt.DropAction.CopyAction, mime,
                      Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
    zone.dropEvent(drop)
    assert drop.isAccepted() and [Path(item) for item in imported] == [path] and not zone.dragging
    window.is_busy = True
    busy_drop = QDropEvent(QPointF(10, 10), Qt.DropAction.CopyAction, mime,
                          Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
    zone.dropEvent(busy_drop)
    assert not busy_drop.isAccepted() and len(imported) == 1
    window.is_busy = False
    mime.setUrls([QUrl('https://example.com/audio.wav')])
    assert not zone.can_import(mime)
