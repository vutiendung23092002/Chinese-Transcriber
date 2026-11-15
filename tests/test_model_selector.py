import pytest
from PySide6.QtCore import Qt, QPoint
from chinese_transcriber.storage import Store
from chinese_transcriber.workspace import WorkspaceWindow


MODELS = [
    dict(model='gpt-6.1-sol', displayName='GPT-6.1-Sol', defaultReasoningEffort='medium',
         supportedReasoningEfforts=[dict(reasoningEffort=x) for x in ('low','medium','high','xhigh')]),
    dict(model='gpt-6-luna', displayName='GPT-6 Luna', defaultReasoningEffort='low',
         supportedReasoningEfforts=[dict(reasoningEffort=x) for x in ('low','high')]),
]


def open_file(qtbot, tmp_path, model='gpt-6.1-sol', effort='low', models=MODELS):
    store = Store(tmp_path/'library')
    store.set_setting('model',model); store.set_setting('effort',effort)
    window = WorkspaceWindow(store); qtbot.addWidget(window)
    window.models = models; window.show(); window.navigate('file'); qtbot.wait(20)
    return window


def test_slider_click_drag_keyboard_reset_and_persistence(qtbot, tmp_path):
    window = open_file(qtbot,tmp_path)
    selector = window.model_selector; slider = selector.effort_slider
    assert selector.model_label.text() == 'GPT-6.1 Sol'
    qtbot.mouseClick(slider,Qt.MouseButton.LeftButton,pos=QPoint(round(slider.stop_x(3)),18))
    assert selector.effort == 'xhigh' and selector.effort_label.text() == 'Extra High'
    qtbot.keyClick(slider,Qt.Key.Key_Left)
    assert selector.effort == 'high'
    qtbot.mousePress(slider,Qt.MouseButton.LeftButton,pos=QPoint(15,18))
    qtbot.mouseMove(slider,QPoint(round(slider.stop_x(1)),18))
    qtbot.mouseRelease(slider,Qt.MouseButton.LeftButton,pos=QPoint(round(slider.stop_x(1)),18))
    assert selector.effort == 'medium'
    qtbot.keyClick(slider,Qt.Key.Key_End)
    qtbot.mouseClick(selector.reset_button,Qt.MouseButton.LeftButton)
    assert selector.effort == 'medium' and not selector.reset_button.isEnabled()
    qtbot.keyClick(slider,Qt.Key.Key_End)
    window.navigate('live')
    assert window.model_selector.effort == window.store.setting('effort') == 'xhigh'
    window.change_theme(1)
    assert window.model_selector.effort == 'xhigh'
    window.navigate('file')
    assert window.model_selector.effort == 'xhigh'


def test_model_menu_uses_real_capabilities_and_rejects_unavailable_choices(qtbot, tmp_path):
    window = open_file(qtbot,tmp_path)
    selector = window.model_selector
    qtbot.mouseClick(selector.model_button,Qt.MouseButton.LeftButton); qtbot.wait(20)
    menu = selector.model_menu
    assert menu.isVisible()
    assert [a.data() for a in menu.actions() if a.isEnabled() and not a.isSeparator()] == ['gpt-6.1-sol','gpt-6-luna']
    action = next(a for a in menu.actions() if a.data() == 'gpt-6-luna')
    qtbot.mouseClick(menu,Qt.MouseButton.LeftButton,pos=menu.actionGeometry(action).center())
    assert selector.model_id == 'gpt-6-luna' and selector.effort == 'low'
    assert selector.effort_slider.steps == ['low','high']
    qtbot.keyClick(selector.effort_slider,Qt.Key.Key_Right)
    assert selector.effort == 'high'
    selector.select_effort('medium')
    assert selector.effort == 'high'
    selector.select_model('not-returned-by-codex')
    assert selector.model_id == 'gpt-6-luna'
    assert window.translation_options()['effort'] == 'high'


@pytest.mark.parametrize('models,model,effort,title',[
    (MODELS,'removed-model','high','Không khả dụng'),
    (MODELS,'gpt-6.1-sol','ultra','Không hỗ trợ'),
    ([], 'gpt-6.1-sol','xhigh','Chưa xác minh'),
])
def test_unverified_or_unsupported_selection_is_preserved_and_blocks_translation(qtbot,tmp_path,models,model,effort,title):
    window = open_file(qtbot,tmp_path,model,effort,models)
    selector = window.model_selector
    assert selector.effort_label.text() == title
    assert not selector.effort_slider.valid
    with pytest.raises(ValueError): window.translation_options()
    assert window.store.setting('model') == model and window.store.setting('effort') == effort
    window.navigate('live')
    assert window.model_selector.model_id == model and window.model_selector.effort == effort
    if models:
        window.model_selector.select_model('gpt-6-luna')
        assert window.translation_options()['model'] == 'gpt-6-luna'
    else:
        assert not window.model_selector.effort_slider.isEnabled()
