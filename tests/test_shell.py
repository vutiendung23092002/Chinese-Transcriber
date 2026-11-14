import pytest
from chinese_transcriber.window import MainWindow
from chinese_transcriber.widgets import PAGES

@pytest.mark.parametrize('size',[(1440,900),(1366,768),(1100,720)])
def test_native_navigation_keeps_columns_fixed(qtbot,size):
    window=MainWindow(); qtbot.addWidget(window); window.resize(*size); window.show()
    qtbot.wait(50)
    expected=(window.rail.width(),window.context.width(),window.workspace.x())
    for page,_,_ in PAGES:
        window.navigate(page); qtbot.wait(5)
        assert (window.rail.width(),window.context.width(),window.workspace.x())==expected
    window.change_theme(1)
    assert window.colors['bg']=='#24212E'
