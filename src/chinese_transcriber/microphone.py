"""Microphone identity and measurements of the unmodified capture signal."""
from __future__ import annotations
import math
import numpy as np
import sounddevice as sd


def input_devices():
    devices = []
    apis = None
    for index, item in enumerate(sd.query_devices()):
        if item['max_input_channels'] <= 0:
            continue
        api = ''
        if 'hostapi' in item:
            if apis is None:
                apis = sd.query_hostapis()
            api = apis[item['hostapi']]['name']
        devices.append(dict(index=index, name=item['name'], hostapi=api))
    return devices


def device_identity(device):
    return {key: device[key] for key in ('name', 'hostapi')}


def find_input_device(identity, devices):
    if not isinstance(identity, dict):
        return None
    identity = {key: identity.get(key) for key in ('name', 'hostapi')}
    matches = [item for item in devices if device_identity(item) == identity]
    # Numeric PortAudio indices can change after reconnecting a headset.
    return matches[0] if len(matches) == 1 else None


def default_input_index():
    return int(sd.default.device[0])


def selected_input(identity, devices):
    if identity is not None:
        return find_input_device(identity, devices)
    default = default_input_index()
    return next((item for item in devices if item['index'] == default), None)


def resolve_input_device(identity):
    device = find_input_device(device_identity(identity), input_devices())
    if device is None:
        raise ValueError('Microphone đã chọn không còn kết nối hoặc không xác định được duy nhất. Hãy chọn lại microphone.')
    return device


class InputSignalMonitor:
    """Measure PCM before ASR; never gate, amplify, or discard original samples."""
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.total = self.zeros = self.clipped = 0
        self.energy = self.peak = 0.0
        self.last_warning = None
        self.reset_window()

    def reset_window(self):
        self.meter_samples = self.quality_samples = 0
        self.meter_energy = self.quality_energy = 0.0
        self.quality_zeros = self.quality_clipped = 0
        self.last_warning = None

    @staticmethod
    def dbfs(energy, count):
        return round(10 * math.log10(max(energy / max(1, count), 1e-12)), 1)

    def stats(self):
        return dict(samples=self.total, rms_dbfs=self.dbfs(self.energy, self.total),
                    peak_dbfs=round(20 * math.log10(max(self.peak, 1e-6)), 1),
                    zero_percent=round(100 * self.zeros / max(1, self.total), 1),
                    clipped_percent=round(100 * self.clipped / max(1, self.total), 2))

    def feed(self, samples):
        samples = np.asarray(samples, dtype=np.float32)
        count = len(samples)
        if not count:
            return None
        energy = float(np.dot(samples, samples))
        zeros = int(np.count_nonzero(samples == 0))
        clipped = int(np.count_nonzero(np.abs(samples) >= .999))
        self.total += count; self.energy += energy
        self.zeros += zeros; self.clipped += clipped
        self.peak = max(self.peak, float(np.max(np.abs(samples))))
        self.meter_samples += count; self.meter_energy += energy
        self.quality_samples += count; self.quality_energy += energy
        self.quality_zeros += zeros; self.quality_clipped += clipped
        warning = None
        if self.quality_samples >= self.sample_rate * 8:
            rms = self.dbfs(self.quality_energy, self.quality_samples)
            issue = ('silent' if self.quality_zeros / self.quality_samples >= .9 else
                     'weak' if rms < -50 else
                     'clipping' if self.quality_clipped / self.quality_samples >= .01 else None)
            if issue and issue != self.last_warning:
                warning = {
                    'silent': 'Microphone đang gửi tín hiệu gần như im lặng. Nếu đang có người nói, hãy kiểm tra đúng mic, âm lượng và bộ lọc tiếng gọi của tai nghe.',
                    'weak': 'Tín hiệu microphone rất nhỏ. Nếu đang có người nói, hãy đưa nguồn nói gần mic hơn và kiểm tra âm lượng đầu vào.',
                    'clipping': 'Tín hiệu microphone đang bị vỡ tiếng. Hãy giảm âm lượng nguồn phát hoặc mức thu microphone.',
                }[issue]
            self.last_warning = issue
            self.quality_samples = self.quality_zeros = self.quality_clipped = 0
            self.quality_energy = 0.0
        if self.meter_samples < self.sample_rate // 4 and not warning:
            return None
        rms = self.dbfs(self.meter_energy, self.meter_samples)
        # Logarithmic display makes quiet speech visible without changing audio.
        level = round(max(0, min(100, (rms + 60) / 54 * 100)))
        self.meter_samples = 0; self.meter_energy = 0.0
        return dict(level=level, rms_dbfs=rms, warning=warning)
