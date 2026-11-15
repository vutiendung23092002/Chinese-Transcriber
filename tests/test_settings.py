import sqlite3
import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton
from chinese_transcriber.storage import Store
from chinese_transcriber.workspace import WorkspaceWindow


MODELS=[dict(model='gpt-6.1-sol',displayName='GPT-6.1 Sol',defaultReasoningEffort='medium',
    supportedReasoningEfforts=[dict(reasoningEffort=x) for x in ('low','medium','high')])]


@pytest.mark.parametrize('model,effort',[('removed-model','high'),('gpt-6.1-sol','ultra')])
def test_settings_requires_explicit_supported_default_selection(qtbot,tmp_path,model,effort):
    store=Store(tmp_path); store.set_setting('model',model); store.set_setting('effort',effort)
    window=WorkspaceWindow(store); qtbot.addWidget(window); window.models=MODELS
    errors=[]; window.error=lambda message:errors.append(str(message)); window.navigate('settings')
    page=window.settings_page
    assert page.model_selector.model_id==model
    assert page.model_selector.effort==effort
    page.save_button.click()
    assert errors and store.setting('model')==model and store.setting('effort')==effort
    page.model_selector.select_model('gpt-6.1-sol')
    page.model_selector.select_effort('medium')
    assert store.setting('effort')==effort
    page.save_button.click()
    assert store.setting('model')=='gpt-6.1-sol' and store.setting('effort')=='medium'


def test_settings_uses_reported_quota_and_does_not_invent_missing_values(qtbot,tmp_path):
    window=WorkspaceWindow(Store(tmp_path)); qtbot.addWidget(window)
    window.codex_status={'limits':{'rateLimits':{'primary':{'usedPercent':8,'windowDurationMins':300},'secondary':{'usedPercent':47,'windowDurationMins':10080}}}}
    window.navigate('settings')
    assert [bar.value() for bar in window.settings_page.quota_bars]==[80,470]
    window.codex_status={'limits':{'rateLimits':{'primary':{'usedPercent':None},'secondary':{'usedPercent':float('nan')}}}}
    window.navigate('settings')
    assert window.settings_page.quota_bars==[]
    assert window.settings_page.findChild(QLabel,'settings_quota_missing') is not None


def test_settings_cpu_backup_and_theme_controls_keep_real_state(qtbot,tmp_path):
    store=Store(tmp_path); store.set_setting('model','gpt-6.1-sol'); store.set_setting('effort','medium')
    window=WorkspaceWindow(store); qtbot.addWidget(window); window.models=MODELS
    window.resize(1440,900); window.show(); window.navigate('settings'); qtbot.wait(30)
    expected_width=window.context.width()
    window.settings_page.threads.setValue(2)
    assert store.setting('asr_threads')==2
    window.settings_page.findChild(QPushButton,'settings_backup').click()
    backups=list((store.root/'backups').glob('*.sqlite3'))
    assert len(backups)==1
    with sqlite3.connect(backups[0]) as db: assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    tile=window.settings_page.theme_group.button(1)
    qtbot.mouseClick(tile,Qt.MouseButton.LeftButton); qtbot.wait(30)
    assert store.setting('theme')=='dark' and window.colors['bg']=='#24212E'
    assert store.setting('model')=='gpt-6.1-sol' and store.setting('effort')=='medium'
    assert window.context.width()==expected_width
