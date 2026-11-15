import numpy as np
import soundfile as sf
import pytest
from PySide6.QtCore import Qt,QPoint,QTimer
from PySide6.QtGui import QFontInfo
from PySide6.QtWidgets import QPushButton,QMessageBox,QApplication
from chinese_transcriber.storage import Store
from chinese_transcriber.workspace import WorkspaceWindow


@pytest.fixture
def library_window(qtbot,tmp_path):
    store=Store(tmp_path/'library')
    ids=[]
    for i,(name,title,kind) in enumerate((
        ('Southwest Jiaotong University Xipu Campus Dianqiguan 3.wav','Bài giảng Đại số','upload'),
        ('统计学课程.wav','Thống kê học','live'),
    )):
        source=tmp_path/name; sf.write(source,np.full(16000,(i+1)*.1,dtype='float32'),16000)
        row,_=store.import_audio(source,1,kind,title); ids.append(row['id'])
    transcript=store.new_transcript(ids[0],'test'); segment=store.append_segment(transcript,0,1,'你好。')
    store.set_transcript_status(transcript,'complete')
    versions=[]
    for status in ('complete','partial','complete'):
        version=store.new_version(ids[0],transcript,'gpt-6.1-sol','low','',[])
        if status=='complete': store.translation_result(version,segment,'Xin chào.')
        store.set_version_status(version,status); versions.append(version)
    store.trash_version(versions[-1])
    window=WorkspaceWindow(store); qtbot.addWidget(window); window.show(); window.navigate('library'); qtbot.wait(20)
    yield window,dict(audio=ids[0],other=ids[1],transcript=transcript,versions=versions)
    window.waveform_cancel.set(); window.pool.waitForDone()


def test_empty_library_import_actions_and_responsive_layout(qtbot,tmp_path,monkeypatch):
    window=WorkspaceWindow(Store(tmp_path/'library')); qtbot.addWidget(window)
    chosen=[]; monkeypatch.setattr(window,'choose_audio',lambda:chosen.append(True))
    window.show(); window.navigate('library'); qtbot.wait(20)
    page=window.library_page
    assert page.count.text()=='0 nguồn' and page.table.rowCount()==0
    assert page.table.empty.isVisible() and page.details_stack.currentIndex()==0
    assert QFontInfo(page.table.empty.heading.font()).family()=='Inter'
    assert page.table.empty.heading.font().pixelSize()==28
    assert int(page.table.empty.heading.font().weight())==700
    assert [b.text() for b in window.context.findChildren(QPushButton) if b.property('library_nav')]==['Tất cả âm thanh','Nhập âm thanh mới','Thùng rác']
    page.import_button.click(); page.table.empty.import_button.click(); window.library_import_action.click()
    assert len(chosen)==3
    for width,height in ((1440,900),(1024,700),(1366,768),(1440,900)):
        window.resize(width,height); qtbot.wait(30)
        assert window.scroll.horizontalScrollBar().maximum()==window.scroll.verticalScrollBar().maximum()==0
        assert page._narrow==(width==1024)
        assert page.mapTo(window,QPoint()).y()==window.context_panel.mapTo(window,QPoint()).y()
        assert page.mapTo(window,page.rect().bottomRight()).y()==window.context_panel.mapTo(window,window.context_panel.rect().bottomRight()).y()
        for child in (page.search,page.import_button,page.table,page.details):
            assert page.contentsRect().contains(child.mapTo(page,QPoint()))
            assert page.contentsRect().contains(child.mapTo(page,child.rect().bottomRight()))
        for state in (page.table.empty,page.details_empty):
            assert state.description.height()>=state.description.heightForWidth(state.description.width())
    window.is_busy=True; window.refresh_library_state()
    assert not page.import_button.isEnabled() and not window.library_import_action.isEnabled()
    assert not page.table.empty.import_button.isEnabled()
    window.is_busy=False


def test_real_library_search_versions_and_action_routes(library_window,qtbot,monkeypatch):
    window,data=library_window; page=window.library_page
    assert len(page.rows)==2
    page.search.setText('  ĐẠI SỐ  ')
    assert [r['id'] for r in page.rows]==[data['audio']] and page.count.text()=='1 nguồn'
    assert page.table.item(0,4).text()=='2'
    assert [v['version']['id'] for v in page.version_cards]==data['versions'][1::-1]
    assert page.version_cards[0]['resume_button'] is not None
    assert page.version_cards[1]['resume_button'] is None
    opened=[]; resumed=[]; compared=[]; deleted=[]
    monkeypatch.setattr(window,'open_audio',lambda *args,**kwargs:opened.append((args,kwargs)))
    monkeypatch.setattr(window,'resume_translation',resumed.append)
    monkeypatch.setattr(window,'compare_versions',lambda a,b:compared.append((a['id'],b['id'])))
    monkeypatch.setattr(window,'delete_version',lambda v:deleted.append(v['id']))
    page.transcript_button.click(); page.version_cards[0]['open_button'].click()
    page.version_cards[0]['resume_button'].click(); page.version_cards[0]['delete_button'].click(); page.compare_button.click()
    assert opened==[((data['audio'],),dict(transcript_only=True)),((data['audio'],data['versions'][1]),{})]
    assert resumed==deleted==[data['versions'][1]]
    assert compared==[(data['versions'][0],data['versions'][1])]
    page.table.activated.emit(page.table.model().index(0,0))
    assert opened[-1]==((data['audio'],),{})
    page.search.setText('does-not-exist')
    assert not page.rows and page.table.empty.filtered and page.details_stack.currentIndex()==0
    assert page.table.empty.heading.text()=='Không tìm thấy âm thanh'
    page.table.empty.import_button.click()
    assert len(page.rows)==2 and page.selected_id==data['audio']
    page.search.setText('统计学')
    assert page.rows[0]['id']==data['other'] and page.table.item(0,3).text()=='Ghi trực tiếp'
    window.navigate('dashboard'); window.navigate('library')
    assert window.library_page.search.text()=='统计学' and window.library_page.selected_id==data['other']


def test_library_delete_confirmation_and_restore_real_data(library_window,qtbot,monkeypatch):
    window,data=library_window; page=window.library_page; page.search.setText('Dianqiguan')
    monkeypatch.setattr(QMessageBox,'question',lambda *args:QMessageBox.StandardButton.No)
    page.delete_audio_button.click()
    assert len(window.store.versions(data['audio']))==2
    # Accept the version dialog against this isolated test library only.
    QTimer.singleShot(0,lambda:QApplication.activeModalWidget().accept())
    page.version_cards[0]['delete_button'].click()
    assert [v['id'] for v in window.store.versions(data['audio'])]==[data['versions'][0]]
    assert window.store.audio_path(data['audio']).exists()
    window.store.restore_version(data['versions'][1]); window.navigate('library')
    assert len(window.library_page.version_cards)==2
    monkeypatch.setattr(QMessageBox,'question',lambda *args:QMessageBox.StandardButton.Yes)
    window.library_page.delete_audio_button.click()
    assert window.library_page.rows==[] and window.store.audio_path(data['audio']).exists()
    window.restore('audio',data['audio']); window.navigate('library')
    assert window.library_page.selected_id==data['audio']
    assert [v['id'] for v in window.store.versions(data['audio'])]==data['versions'][1::-1]


def test_populated_library_reflows_and_locks_mutations(library_window,qtbot):
    window,data=library_window; page=window.library_page; page.search.setText('Dianqiguan')
    for width,height in ((1440,900),(1024,700),(1440,900)):
        window.resize(width,height); qtbot.wait(30)
        assert window.scroll.horizontalScrollBar().maximum()==0
        assert page.table.horizontalScrollBar().maximum()==0
        assert page.details_scroll.horizontalScrollBar().maximum()==0
        assert page.selected_id==data['audio']
        page.details_scroll.ensureWidgetVisible(page.compare_button); qtbot.wait(10)
        viewport=page.details_scroll.viewport()
        assert viewport.rect().contains(page.compare_button.mapTo(viewport,page.compare_button.rect().center()))
    window.is_busy=True; window.refresh_library_state()
    assert all(not b.isEnabled() for b in page.write_buttons)
    assert page.open_button.isEnabled() and page.transcript_button.isEnabled()
    window.is_busy=False
