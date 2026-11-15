import pytest
from PySide6.QtCore import QPoint
from chinese_transcriber.workspace import WorkspaceWindow
from chinese_transcriber.storage import Store
from chinese_transcriber.widgets import PAGES

@pytest.mark.parametrize('size',[(1440,900),(1366,768),(1100,720)])
def test_native_navigation_keeps_columns_fixed(qtbot,tmp_path,size):
    window=WorkspaceWindow(Store(tmp_path/'library')); qtbot.addWidget(window); window.resize(*size); window.show()
    qtbot.wait(50)
    expected=(window.rail.width(),window.context.width(),window.workspace.x())
    for mode in (0,1):
        window.change_theme(mode)
        for page,_,_ in PAGES:
            window.navigate(page); qtbot.wait(5)
            assert (window.rail.width(),window.context.width(),window.workspace.x())==expected
            panel=window.context_panel
            assert panel.geometry()==window.context.rect().adjusted(6,24,-6,-18)
            assert panel.graphicsEffect() is not None
            assert panel.mapTo(window,panel.rect().bottomRight()).y()==window.rail.pill.mapTo(window,window.rail.pill.rect().bottomRight()).y()
            footer=window.context_layout.itemAt(window.context_layout.count()-1).widget()
            assert panel.contentsRect().contains(footer.mapTo(panel,QPoint()))
            assert panel.contentsRect().contains(footer.mapTo(panel,footer.rect().bottomRight()))
    assert window.colors['bg']=='#24212E'
