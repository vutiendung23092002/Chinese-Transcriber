# Windows portable build

Đã build và chạy trên Windows 11 x64 bằng Python PSF 3.11.9, PyInstaller 6.22.3, PySide6 6.12.0, sherpa-onnx 1.13.8. Phiên bản dependency đầy đủ nằm tại requirements-lock.txt.

## Từ source

Cài Python 3.11 x64, tạo .venv, cài requirements-lock.txt và `pip install --no-deps -e .`. Tải model bằng `python -m chinese_transcriber.models --root models`. Chạy `scripts/build_windows.ps1 -Python .venv/Scripts/python.exe` trong PowerShell.

Nếu môi trường không cho chạy file ps1, các bước tương đương trong terminal Python được phép của máy:

```powershell
.venv\Scripts\python.exe scripts\create_icon.py
.venv\Scripts\python.exe -m PyInstaller --noconfirm packaging\ChineseTranscriber.spec
.venv\Scripts\python.exe scripts\prepare_distribution.py
```

Ở máy bàn giao, runtime chính thức `.tools/python311/python.exe` đã được dùng thay Python uv vì DLL chuẩn của bản uv bị Windows Application Control chặn. Không thay đổi chính sách Windows. Runtime embeddable này đọc dependency và source qua python311._pth; không cần cài vào hệ thống.

## Gói đầu ra

`dist/ChineseTranscriber/ChineseTranscriber.exe` là EXE cửa sổ, không mở console. Thư mục `_internal` chứa Python/Qt/codec và dependency native. Thư mục `models` chứa SenseVoiceSmall INT8, Streaming Paraformer INT8 và Silero VAD. Không nhúng QtWebEngine/Electron, không kèm Codex executable, token, thư viện cá nhân hoặc dữ liệu test.

Giữ nguyên cả thư mục khi chuyển máy. Có thể zip nguyên thư mục; giải nén trước khi chạy. Bản one-directory được chọn để không giải nén vài trăm MB model mỗi lần khởi động và để có thể thay model riêng. Bản build hiện chưa có chữ ký Authenticode của nhà phát hành.

## Tình trạng Smart App Control và launcher Python

Một bản EXE trước chạy đầy đủ smoke/ASR/Codex/codec, report .test-data/prior-frozen/validation.json. Artifact EXE cuối sau sửa bảo vệ thuật ngữ chưa lưu bị Smart App Control chặn với WinError 4551, Code Integrity event 3077/3033; report .test-data/release/validation.json không đạt bước khởi động. Chưa xác định được nguyên nhân policy đánh giá khác nhau giữa các build. Không vô hiệu hóa kiểm soát hoặc thêm chứng thư vào Windows. EXE hiện chưa có chữ ký nhà phát hành và cần xử lý yêu cầu chữ ký/phê duyệt theo chính sách máy trước khi nghiệm thu đường chạy EXE.

Gói bàn giao có **Run.bat**, `python/` (runtime PSF chính thức có chữ ký), `src/` và `assets/`. Đây là cách khởi động đã kiểm tra cho gói cuối. Launcher chạy source bằng Python chính thức và dùng dependency native từ _internal, không chạy EXE đang bị chặn. Không cần cài Python lên máy; vẫn là cùng ứng dụng PySide6 native. Giữ nguyên toàn bộ thư mục để launcher tìm đúng dependency và model.

Sau build, `python scripts/prepare_python_fallback.py` thêm launcher khi workspace có runtime PSF embeddable tại .tools/python311; build_windows.ps1 tự thực hiện bước này nếu có. Không dùng Python uv đang bị policy chặn. Chạy lại prepare_distribution.py sau cùng để checksum bao gồm launcher.

`SHA256SUMS.txt` liệt kê hash từng file trong gói, được sinh sau khi chép model và tài liệu. Icon EXE lấy từ logo Nhịp lời đã duyệt. Font Noto và bản OFL được kèm để có fallback tiếng Trung/Việt.

## Xác minh bản EXE

Chạy `python scripts/verify_release.py` sau build. Script dùng thư viện riêng trong .test-data/release, kiểm tra:

- EXE khởi động/thoát bình thường.
- WAV, MP3 và M4A được FFmpeg/Qt giải mã; SenseVoice tạo đoạn thật.
- Với WAV: gọi Codex thật bằng GPT-6 Luna/low, xác minh ID, xuất hai TXT, trash/restore và kiểm tra nguồn còn nguyên.
- SQLite integrity và không có WebEngine trong gói.

Có thể chạy self-test thủ công: `ChineseTranscriber.exe --self-test-audio "duong-dan.wav" --self-test-codex --data-dir "thu-vien-kiem-tra-rieng"`. Tùy chọn Codex sử dụng hạn mức tài khoản thật, không tự chạy khi mở ứng dụng bình thường. Kết quả ghi trong selftest-report.json của thư viện kiểm tra.

`python scripts/verify_release.py --portable-python` kiểm tra Python launcher **trong gói** từ working directory khác; `--source` kiểm tra source workspace. Hai chế độ này không được dùng để báo rằng EXE PyInstaller đã vượt Smart App Control.
