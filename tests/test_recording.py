import numpy as np
from chinese_transcriber.storage import Store
from chinese_transcriber.recording import materialize_recording

def test_crashed_recording_recovery_preserves_audio_and_segments(tmp_path):
    store=Store(tmp_path)
    path=store.root/'recordings'/'interrupted.pcm'; path.write_bytes(np.zeros(32000,dtype='<i2').tobytes())
    payload=dict(path='recordings/interrupted.pcm',segments=[dict(start=.1,end=1.8,zh='你好。',timing='vad-boundary')])
    job=store.job('recording','interrupted',payload)
    result=materialize_recording(store,payload,job)
    assert store.audio_path(result['audio_id']).exists()
    assert store.segments(result['transcript_id'])[0]['zh']=='你好。'
    assert not path.exists()
