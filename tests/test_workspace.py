import soundfile as sf
import numpy as np
from chinese_transcriber.storage import Store
from chinese_transcriber.workspace import WorkspaceWindow
from chinese_transcriber.widgets import PAGES
from chinese_transcriber.audio import export_txt

def test_real_library_and_export(qtbot,tmp_path):
    store=Store(tmp_path/'data'); wav=tmp_path/'sample.wav'; sf.write(wav,np.zeros(16000,dtype='float32'),16000)
    audio,_=store.import_audio(wav,1)
    t=store.new_transcript(audio['id'],'test'); s=store.append_segment(t,0,1,'你好。'); store.set_transcript_status(t,'complete')
    v=store.new_version(audio['id'],t,'test','low','',[]); store.translation_result(v,s,'Xin chào.')
    window=WorkspaceWindow(store); qtbot.addWidget(window); window.show(); window.open_audio(audio['id'],v)
    assert window.timeline.item(0,1).text()=='你好。'
    assert window.timeline.item(0,2).text()=='Xin chào.'
    for page,_,_ in PAGES:
        window.navigate(page); qtbot.wait(5)
        assert window.context.width()==260
    out=tmp_path/'vi.txt'; export_txt(store,t,v,out,'vi')
    assert 'Xin chào.' in out.read_text(encoding='utf-8')

def test_unsupported_previous_model_is_preserved_without_substitution(qtbot,tmp_path):
    store=Store(tmp_path); store.set_setting('model','removed-model'); store.set_setting('effort','high')
    window=WorkspaceWindow(store); qtbot.addWidget(window)
    window.models=[dict(model='available-model',displayName='Available',supportedReasoningEfforts=[dict(reasoningEffort='low')],defaultReasoningEffort='low')]
    window.navigate('file')
    assert window.model_selector.model_id=='removed-model'
    window.capture_options()
    assert store.setting('model')=='removed-model'

def test_manual_translation_fills_missing_segment_in_new_version(qtbot,tmp_path,monkeypatch):
    store=Store(tmp_path/'data'); wav=tmp_path/'sample.wav'; sf.write(wav,np.zeros(16000,dtype='float32'),16000)
    audio,_=store.import_audio(wav,1); transcript=store.new_transcript(audio['id'],'test')
    segment=store.append_segment(transcript,0,1,'你好。'); store.set_transcript_status(transcript,'complete')
    old=store.new_version(audio['id'],transcript,'test','low','',[])
    window=WorkspaceWindow(store); qtbot.addWidget(window); window.open_audio(audio['id'],old)
    monkeypatch.setattr('chinese_transcriber.workspace.QInputDialog.getMultiLineText',lambda *args:('Xin chào.',True))
    window.edit_segment(0,2)
    assert window.version_id!=old
    assert store.segments(transcript,window.version_id)[0]['vi']=='Xin chào.'
    assert store.segments(transcript,old)[0]['vi']==''
    assert store.versions(audio['id'])[0]['status']=='complete'

def test_unsaved_glossary_can_cancel_navigation_or_save(qtbot,tmp_path,monkeypatch):
    from PySide6.QtWidgets import QMessageBox
    store=Store(tmp_path); window=WorkspaceWindow(store); qtbot.addWidget(window)
    window.navigate('prompts'); window.glossary_name.setText('Thống kê')
    monkeypatch.setattr(QMessageBox,'question',lambda *args:QMessageBox.StandardButton.Cancel)
    window.navigate('file'); assert window.page=='prompts'
    monkeypatch.setattr(QMessageBox,'question',lambda *args:QMessageBox.StandardButton.Save)
    window.navigate('file'); assert window.page=='file'
    assert store.one('SELECT name FROM glossaries WHERE id=?',(window.glossary_id,))['name']=='Thống kê'
