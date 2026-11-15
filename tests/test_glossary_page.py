import json
import pytest
from PySide6.QtCore import Qt,QPoint
from PySide6.QtGui import QFontInfo
from PySide6.QtWidgets import QTableWidgetItem,QMessageBox,QInputDialog,QPushButton
from chinese_transcriber.storage import Store
from chinese_transcriber.workspace import WorkspaceWindow


@pytest.fixture
def glossary_window(qtbot,tmp_path):
    window=WorkspaceWindow(Store(tmp_path/'library')); qtbot.addWidget(window)
    window.show(); window.navigate('prompts'); qtbot.wait(20)
    yield window
    if window.page=='prompts': window.glossary_clean=window.glossary_state()
    window.pool.waitForDone()


def test_glossary_layout_placeholders_and_resizing(glossary_window,qtbot):
    window=glossary_window; page=window.glossary_page
    assert page.name.placeholderText()=='Ví dụ: Đại số tuyến tính'
    assert page.table.rowCount()==1 and page.table.item(0,0) is None
    assert page.save_status.text()=='Chưa lưu' and page.count.text()=='0 thuật ngữ'
    assert not page.delete_button.isEnabled()
    assert QFontInfo(page.name.font()).family()=='Inter' and page.name.font().pixelSize()==15
    for width,height in ((1440,900),(1024,700),(1366,768),(1440,900)):
        window.resize(width,height); qtbot.wait(30)
        assert window.scroll.horizontalScrollBar().maximum()==window.scroll.verticalScrollBar().maximum()==0
        assert page.mapTo(window,QPoint()).y()==window.context_panel.mapTo(window,QPoint()).y()
        assert page.mapTo(window,page.rect().bottomRight()).y()==window.context_panel.mapTo(window,window.context_panel.rect().bottomRight()).y()
        assert page.name.height()==44 and page.save_button.height()==44
        for widget in (page.name,page.context,page.table,page.add_button,page.delete_button,page.save_button):
            assert page.contentsRect().contains(widget.mapTo(page,QPoint()))
            assert page.contentsRect().contains(widget.mapTo(page,widget.rect().bottomRight()))
        assert page.hint.isVisible()==(width!=1024)
    window.change_theme(1)
    assert window.glossary_page.count.text()=='0 thuật ngữ'


def test_cell_editor_save_status_and_real_glossary_storage(glossary_window,qtbot,monkeypatch):
    window=glossary_window; page=window.glossary_page
    page.name.setText('Đại số tuyến tính'); page.context.setPlainText('Chương 1: Không gian vector')
    page.table.setItem(0,0,QTableWidgetItem('向量'))
    assert page.count.text()=='0 thuật ngữ'
    page.table.setItem(0,1,QTableWidgetItem('vectơ'))
    assert page.count.text()=='1 thuật ngữ'
    page.table.setCurrentCell(0,2); page.table.edit(page.table.model().index(0,2))
    qtbot.waitUntil(lambda:page.delegate.editor is not None)
    qtbot.keyClicks(page.delegate.editor,'lecture note')
    assert page.current_state()[2][0][2]=='lecture note'
    # Programmatic click retains editor focus; save must explicitly commit it.
    page.save_button.click()
    identifier=window.glossary_id
    row=window.store.one('SELECT * FROM glossaries WHERE id=?',(identifier,))
    assert json.loads(row['entries'])==[dict(zh='向量',vi='vectơ',note='lecture note')]
    assert row['context']=='Chương 1: Không gian vector'
    page=window.glossary_page
    assert page.save_status.text()=='Đã lưu' and page.count.text()=='1 thuật ngữ'
    page.table.setCurrentCell(0,1); page.table.edit(page.table.model().index(0,1))
    qtbot.waitUntil(lambda:page.delegate.editor is not None)
    qtbot.keyClick(page.delegate.editor,Qt.Key.Key_A,Qt.KeyboardModifier.ControlModifier)
    qtbot.keyClicks(page.delegate.editor,'vector')
    assert page.save_status.text()=='Chưa lưu'
    monkeypatch.setattr(QMessageBox,'question',lambda *args:QMessageBox.StandardButton.Save)
    window.navigate('file')
    assert json.loads(window.store.one('SELECT entries FROM glossaries WHERE id=?',(identifier,))['entries'])[0]['vi']=='vector'
    assert window.option_widgets[1].currentData()==identifier


@pytest.mark.parametrize('invalid',['missing','duplicate'])
def test_invalid_terms_keep_draft_and_block_save_navigation(glossary_window,monkeypatch,invalid):
    window=glossary_window
    identifier=window.store.save_glossary('Bộ gốc','',[dict(zh='向量',vi='vectơ',note='')])
    window.glossary_id=identifier; window.navigate('prompts'); page=window.glossary_page
    if invalid=='missing': page.table.setItem(0,1,QTableWidgetItem(''))
    else:
        page.table.setItem(1,0,QTableWidgetItem('向量')); page.table.setItem(1,1,QTableWidgetItem('trùng'))
    errors=[]; window.error=lambda text:errors.append(str(text))
    page.save_button.click()
    assert errors and page.save_status.text()=='Chưa lưu'
    stored=json.loads(window.store.one('SELECT entries FROM glossaries WHERE id=?',(identifier,))['entries'])
    assert stored==[dict(zh='向量',vi='vectơ',note='')]
    monkeypatch.setattr(QMessageBox,'question',lambda *args:QMessageBox.StandardButton.Save)
    window.navigate('library')
    assert window.page=='prompts' and window.glossary_page is page
    assert page.current_state()!=window.glossary_clean


def test_set_switch_cancel_discard_save_creation_and_row_deletion(glossary_window,qtbot,monkeypatch):
    window=glossary_window
    first=window.store.save_glossary('A Bộ thứ nhất','cũ',[])
    second=window.store.save_glossary('B Bộ thứ hai','cũ',[])
    for i in range(15): window.store.save_glossary(f'Z Bộ thuật ngữ rất dài thứ {i}','',[])
    window.glossary_id=first; window.navigate('prompts')
    def choose(identifier):
        box=window.glossary_sets
        item=next(box.item(i) for i in range(box.count()) if box.item(i).data(Qt.ItemDataRole.UserRole)==identifier)
        box.setCurrentItem(item)
    window.glossary_name.setText('Thay đổi chưa lưu')
    monkeypatch.setattr(QMessageBox,'question',lambda *args:QMessageBox.StandardButton.Cancel)
    choose(second)
    assert window.glossary_id==first and window.glossary_name.text()=='Thay đổi chưa lưu'
    assert window.glossary_sets.currentItem().data(Qt.ItemDataRole.UserRole)==first
    monkeypatch.setattr(QMessageBox,'question',lambda *args:QMessageBox.StandardButton.Discard)
    choose(second)
    assert window.glossary_id==second
    assert window.store.one('SELECT name FROM glossaries WHERE id=?',(first,))['name']=='A Bộ thứ nhất'
    window.glossary_context.setPlainText('Bối cảnh đã sửa')
    monkeypatch.setattr(QMessageBox,'question',lambda *args:QMessageBox.StandardButton.Save)
    choose(first)
    assert window.store.one('SELECT context FROM glossaries WHERE id=?',(second,))['context']=='Bối cảnh đã sửa'
    monkeypatch.setattr(QInputDialog,'getText',lambda *args:('C Bộ mới',True))
    window.context.findChild(QPushButton,'glossary_new').click()
    assert window.glossary_name.text()=='C Bộ mới' and window.glossary_page.save_status.text()=='Đã lưu'
    page=window.glossary_page
    page.add_button.click(); assert page.table.rowCount()==2 and page.delete_button.isEnabled()
    page.delete_button.click(); assert page.table.rowCount()==1 and page.count.text()=='0 thuật ngữ'
    for width,height in ((1440,900),(1024,700)):
        window.resize(width,height); qtbot.wait(30)
        footer=window.context_layout.itemAt(window.context_layout.count()-1).widget()
        assert window.context_panel.contentsRect().contains(footer.mapTo(window.context_panel,footer.rect().bottomRight()))
        assert window.glossary_sets.horizontalScrollBar().maximum()==0
