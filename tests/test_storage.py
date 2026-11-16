import pytest
from chinese_transcriber.storage import Store

def source(tmp_path):
    path=tmp_path/'lecture.wav'; path.write_bytes(b'RIFF-audio-sample')
    store=Store(tmp_path/'data'); audio,_=store.import_audio(path)
    transcript=store.new_transcript(audio['id'],'test')
    segment=store.append_segment(transcript,0,2,'正态分布。')
    store.set_transcript_status(transcript,'complete')
    return store,path,audio,transcript,segment

def test_dedup_versions_and_independent_trash(tmp_path):
    store,path,audio,t,s=source(tmp_path)
    again,created=store.import_audio(path)
    assert not created and again['id']==audio['id']
    v1=store.new_version(audio['id'],t,'one','low','',[])
    v2=store.new_version(audio['id'],t,'two','high','context',[{'zh':'正态分布','vi':'phân phối chuẩn'}])
    store.trash_version(v1); store.purge_version(v1)
    assert store.audio_path(audio['id']).exists() and len(store.versions(audio['id']))==1
    store.trash_version(v2)
    assert store.list_audio()[0]['version_count']==0
    store.restore_version(v2)
    with pytest.raises(ValueError): store.purge_audio(audio['id'])
    store.trash_audio(audio['id']); store.restore_audio(audio['id'])
    assert len(store.versions(audio['id']))==1
    store.trash_audio(audio['id']); store.purge_audio(audio['id'])
    assert not store.list_audio() and not list((store.root/'audio').glob('*.wav'))

def test_recovery_and_snapshot(tmp_path):
    store,path,a,t,s=source(tmp_path)
    glossary=[{'zh':'总体','vi':'tổng thể'}]
    v=store.new_version(a['id'],t,'one','medium','lecture',glossary)
    glossary[0]['vi']='changed'
    assert 'changed' not in store.versions(a['id'])[0]['glossary']
    store.translation_result(v,s,'tổng thể')
    store.job('translate',v,{})
    assert store.recover_jobs()[0]['state']=='interrupted'
    assert store.segments(t,v)[0]['vi']=='tổng thể'
    assert store.backup().exists()
    with pytest.raises(ValueError): store.translation_result(v,'wrong-id','x')

def test_segments_must_not_overlap(tmp_path):
    store,path,a,t,s=source(tmp_path)
    with pytest.raises(ValueError): store.append_segment(t,1,3,'bad')
    assert len(store.segments(t))==1


def test_batch_translation_commit_rolls_back_if_a_result_cannot_be_saved(tmp_path):
    store,path,audio,transcript,segment=source(tmp_path)
    version=store.new_version(audio['id'],transcript,'one','low','',[])
    with pytest.raises(ValueError,match='không thuộc'):
        store.translation_results(version,[dict(id=segment,vi='hợp lệ',note=''),dict(id='wrong-id',vi='sai',note='')])
    row=store.segments(transcript,version)[0]
    assert row['translation_status']=='queued' and not row['vi']
