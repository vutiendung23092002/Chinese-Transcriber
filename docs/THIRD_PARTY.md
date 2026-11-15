# Thành phần bên thứ ba

Ứng dụng không bao gồm tài khoản, token hoặc executable Codex của người dùng. Codex CLI được phát hiện từ cài đặt có sẵn.

- Python: Python Software Foundation license, https://www.python.org/psf/license/
- PySide6 / Qt: LGPLv3/GPLv3 hoặc giấy phép thương mại tương ứng, https://www.qt.io/licensing/
- sherpa-onnx: Apache-2.0, https://github.com/k2-fsa/sherpa-onnx
- SenseVoiceSmall: mô hình chính thức được chuyển ONNX bởi sherpa-onnx; xem https://github.com/FunAudioLLM/SenseVoice và manifest kèm model.
- Streaming Paraformer: xem nguồn model https://huggingface.co/csukuangfj/sherpa-onnx-streaming-paraformer-bilingual-zh-en và ModelScope liên kết từ tài liệu sherpa-onnx.
- Silero VAD: MIT, https://github.com/snakers4/silero-vad
- Noto Sans / Noto Sans SC: SIL Open Font License 1.1. Các bản OFL nằm trong assets/fonts và bản đóng gói.
- Inter (Regular/Italic variable): SIL Open Font License 1.1, nguồn https://github.com/google/fonts/tree/main/ofl/inter. Font và OFL-Inter.txt đi kèm trong assets/fonts để giữ cùng kiểu chữ trên mọi máy.
- NumPy, SoundFile, sounddevice, imageio-ffmpeg, jsonschema, platformdirs và psutil: xem metadata/license trong các gói tương ứng.
- FFmpeg executable được cung cấp qua imageio-ffmpeg. Xem build/license chính xác tại https://github.com/imageio/imageio-ffmpeg và thông tin -version của executable kèm gói; không phải mã riêng của ứng dụng.

Gói có licenses/Python-LICENSE.txt, LGPL-3.0.txt, GPL-3.0.txt và FFmpeg-build.txt; metadata/license của thư viện nằm trong _internal. FFmpeg đi kèm là build 9.0.2 essentials từ gyan.dev, cấu hình --enable-gpl --enable-version3; thông tin nguồn build: https://www.gyan.dev/ffmpeg/builds/ và https://github.com/FFmpeg/FFmpeg. Font có OFL riêng.

Models và font giữ riêng ngoài mã ứng dụng. Đối chiếu các giấy phép nguồn trước khi phân phối thương mại hoặc sửa đổi; bản đang bàn giao phục vụ mục đích học tập cá nhân được yêu cầu.
