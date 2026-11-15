from types import SimpleNamespace
import json
import numpy as np
import pytest
from chinese_transcriber import microphone
from chinese_transcriber.asr import Recognizer, clean_asr_text
from chinese_transcriber.recording import LiveSession
from chinese_transcriber.storage import Store


def test_saved_microphone_survives_index_changes_without_switching_device(monkeypatch):
    saved = dict(name='Headset', hostapi='Windows WASAPI')
    devices = [dict(index=19, name='Line In', hostapi='Windows WDM-KS'),
               dict(index=3, **saved)]
    monkeypatch.setattr(microphone, 'input_devices', lambda: devices)
    assert microphone.resolve_input_device(saved)['index'] == 3
    devices.pop()
    with pytest.raises(ValueError, match='chọn lại'):
        microphone.resolve_input_device(saved)
    assert microphone.selected_input(saved, devices) is None


def test_ambiguous_or_missing_device_does_not_pick_first_input(monkeypatch):
    saved = dict(name='Headset', hostapi='Windows WASAPI')
    devices = [dict(index=2, **saved), dict(index=7, **saved)]
    assert microphone.find_input_device(saved, devices) is None
    monkeypatch.setattr(microphone, 'default_input_index', lambda: -1)
    assert microphone.selected_input(None, devices) is None
    monkeypatch.setattr(microphone, 'default_input_index', lambda: 7)
    assert microphone.selected_input(None, devices)['index'] == 7
    assert microphone.selected_input(dict(name='Missing', hostapi='MME'), devices) is None


def test_silence_warning_is_conditional_and_does_not_repeat_or_modify_audio():
    monitor = microphone.InputSignalMonitor()
    samples = np.zeros(1600, dtype='float32'); before = samples.copy()
    events = [monitor.feed(samples) for _ in range(160)]
    warnings = [event['warning'] for event in events if event and event['warning']]
    assert len(warnings) == 1 and 'Nếu đang có người nói' in warnings[0]
    assert monitor.stats()['zero_percent'] == 100
    assert np.array_equal(samples, before)
    monitor.reset_window()
    assert all(not (event and event['warning']) for event in
               (monitor.feed(samples) for _ in range(79)))


def test_meter_distinguishes_quiet_speech_and_detects_clipping():
    quiet = microphone.InputSignalMonitor(); loud = microphone.InputSignalMonitor()
    small = np.full(4000, .01, dtype='float32')
    assert 20 < quiet.feed(small)['level'] < loud.feed(small * 10)['level']
    assert quiet.stats()['rms_dbfs'] == -40
    weak = microphone.InputSignalMonitor()
    result = weak.feed(np.full(128000, .001, dtype='float32'))
    assert 'rất nhỏ' in result['warning']
    clipped = microphone.InputSignalMonitor()
    result = clipped.feed(np.full(128000, 32767 / 32768, dtype='float32'))
    assert 'vỡ tiếng' in result['warning']


@pytest.mark.parametrize('text,expected', [
    ('。', ''), (' …！？\n', ''), ('<|zh|><|NEUTRAL|>。', ''),
    ('<|zh|>你好。', '你好。'), ('没有。', '没有。'), ('一', '一'), ('9点。', '9点。'),
])
def test_asr_keeps_short_words_but_not_punctuation(text, expected):
    assert clean_asr_text(text) == expected


def test_punctuation_only_result_is_not_finalized_for_translation():
    rows = [SimpleNamespace(start=0, samples=np.zeros(1600)),
            SimpleNamespace(start=1600, samples=np.ones(1600))]
    class Vad:
        def empty(self): return not rows
        @property
        def front(self): return rows[0]
        def pop(self): rows.pop(0)
    engine = Recognizer.__new__(Recognizer)
    engine.recognize = lambda samples: '你好。' if samples[0] else '。'
    finals = []; engine.consume_vad(Vad(), finals.append)
    assert len(finals) == 1 and finals[0]['zh'] == '你好。'
    assert finals[0]['start'] == .1 and finals[0]['end'] == .2


def test_live_silence_warning_preserves_exact_pcm_and_diagnostic_metadata(tmp_path, monkeypatch):
    pcm = np.zeros(1600, dtype='<i2').tobytes()
    class RecognizerStub:
        def __init__(self, *args, **kwargs): pass
        def stream(self, chunks, callback):
            for _ in chunks: pass
    class Source:
        def __init__(self, **kwargs): self.callback = kwargs['callback']
        def start(self):
            for _ in range(100): self.callback(pcm, 1600, None, None)
        def stop(self): pass
        def close(self): pass
    monkeypatch.setattr('chinese_transcriber.recording.Recognizer', RecognizerStub)
    monkeypatch.setattr('chinese_transcriber.recording.sd.RawInputStream', Source)
    store = Store(tmp_path); events = []
    session = LiveSession(store, None, events.append).start()
    result = session.stop()
    import soundfile as sf
    saved, rate = sf.read(store.audio_path(result['audio_id']), dtype='int16')
    assert rate == 16000 and saved.tobytes() == pcm * 100
    assert any(item['type'] == 'warning' and 'im lặng' in item['message'] for item in events)
    payload = json.loads(store.one('SELECT payload FROM jobs WHERE id=?', (session.job,))['payload'])
    assert payload['input_signal']['zero_percent'] == 100
    assert store.latest_transcript(result['audio_id'], False)['status'] == 'complete'
