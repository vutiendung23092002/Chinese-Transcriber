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

Script build hỗ trợ runtime Python PSF embeddable tại `.tools/python311/python.exe` nếu được cấu hình qua python311._pth để đọc dependency và mã nguồn. Khi Windows Application Control chặn DLL của một bản phân phối Python, có thể dùng runtime PSF chính thức phù hợp; quy trình build không thay đổi chính sách Windows.

## Gói đầu ra

`dist/ChineseTranscriber/ChineseTranscriber.exe` là EXE cửa sổ, không mở console. Thư mục `_internal` chứa Python/Qt/codec và dependency native. Thư mục `models` chứa SenseVoiceSmall INT8, Streaming Paraformer INT8 và Silero VAD. Không nhúng QtWebEngine/Electron, không kèm Codex executable, token, thư viện cá nhân hoặc dữ liệu test.

Giữ nguyên cả thư mục khi chuyển máy. Có thể zip nguyên thư mục; giải nén trước khi chạy. Bản one-directory được chọn để không giải nén vài trăm MB model mỗi lần khởi động và để có thể thay model riêng. Bản build hiện chưa có chữ ký Authenticode của nhà phát hành.

## Tình trạng Smart App Control và launcher Python

Đợt cập nhật hai chế độ dịch từ commit `e12403f` có SHA-256 EXE `977971dcf28825128dd0b032d83b331e15e88b4711a15b0f05c69d6d06429f8f`. EXE đã build lại, bytecode các module ứng dụng khớp source; bước khởi động bị Application Control chặn 4551 tại máy kiểm tra. Launcher portable đã qua smoke, ASR/Codex thật, WAV/MP3/M4A, xuất TXT và SQLite integrity; chế độ cả bài gửi đủ các đoạn sau ASR trong đúng một lượt. Commit và kết quả của gói hiện tại được ghi trong `BUILD-INFO.json`.

MSI mới dùng đúng payload ZIP đã xác minh, gồm 1.220 file. Vì máy kiểm tra đã có bản MSI đang cài, không chạy `verify_installer.py` để tránh tác động bản đó. Đợt này kiểm tra riêng bảng MSI/lối tắt và trích xuất bằng `/a` vào thư mục test, đối chiếu manifest và khởi động launcher trích xuất; đăng ký/EXE cũ không đổi. Đây là kiểm tra trích xuất/payload, không thay thế chu kỳ cài/nâng cấp/gỡ trên máy mới. Các kiểm tra cài/gỡ đầy đủ của MSI đợt trước được giữ riêng bên dưới.

Bản EXE cập nhật từ commit 80567cb ngày 16/11/2026 chứa sửa lỗi thanh nháy khi mở Live. SHA-256: a853af5bb06f232229fcf34204579da0b379e753bfd28346e4983c6c8852aebc. Windows Application Control trên máy kiểm tra chặn khởi động với WinError 4551; chưa nghiệm thu chạy EXE mới. Report tại .test-data/live-flash-release-refresh/frozen-validation.json. Không thay đổi chính sách Windows hoặc thêm chứng thư; EXE chưa có chữ ký Authenticode của nhà phát hành.

Bản EXE trước từ commit 9fa392c, SHA-256 bbc7e759b372eee933f8d23801c4a7814c7c495382f51c8d821ca01cd5a38540, đã chạy smoke/ASR/Codex/WAV-MP3-M4A/TXT/SQLite; report .test-data/release/validation.json thuộc bản đó. Các kết quả cũ không được coi là nghiệm thu khởi động EXE cập nhật.

Gói phát hành có thêm **Run.bat**, `python/` (runtime PSF chính thức có chữ ký), `src/` và `assets/`. Launcher chạy source bằng Python chính thức và dùng dependency native từ _internal. Không cần cài Python lên máy; vẫn là cùng ứng dụng PySide6 native. Có thể mở trực tiếp ChineseTranscriber.exe; giữ nguyên toàn bộ thư mục để chương trình tìm đúng dependency và model.

**Launcher BAT không bảo đảm tránh được Smart App Control.** Người dùng đã xác nhận EXE từ ZIP tải trên Release chạy được, còn mở BAT hiện thông báo chặn loại file từ Internet. Đối chiếu bản trong Downloads: SHA-256 EXE khớp `a853af5b…`, BAT khớp bản build nhưng có `Zone.Identifier` / `ZoneId=3`; BAT tại chỗ không có dấu nguồn này. Không coi test gọi trực tiếp Python bằng subprocess là test mở BAT từ Explorer sau khi tải về. Chữ ký của Python không ký cho BAT. Hướng dẫn người dùng ZIP ưu tiên EXE, MSI dùng Start Menu; xem [xử lý Smart App Control](TROUBLESHOOTING.md#smart-app-control-chặn-runbat-nhưng-exe-vẫn-chạy).

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

## Bộ cài MSI thử nghiệm

MSI được tạo từ ZIP portable và checksum đã chuẩn bị bằng Windows Python 3.11 hoặc 3.12. Script dùng `msilib` trong thư viện chuẩn; Python 3.13 trở lên đã bỏ module này. Đây là yêu cầu của bước build, không phải yêu cầu với người cài ứng dụng.

```powershell
python scripts/build_installer.py
python scripts/verify_installer.py
```

Đầu ra: `dist/ChineseTranscriber-1.0.0-preview.1-win-x64.msi`, file `.msi.sha256` và `.build-info.json`. MSI kèm đúng 1.222 file của ZIP portable, kể cả runtime, model, font và giấy phép; không cần tải thêm khi cài. Bộ cài không kèm Codex CLI hoặc thông tin tài khoản.

MSI dùng giao diện tiến trình cơ bản của Windows Installer và cài theo profile người dùng hiện tại, mặc định tại `%LOCALAPPDATA%\Programs\ChineseTranscriber`. Lối tắt Start Menu trỏ tới `python/pythonw.exe` với `launch.py`; không chạy EXE PyInstaller đang bị chặn. Sản phẩm có mục gỡ trong Installed apps. Component có key path ở HKCU; đường dẫn cài và Start Menu được ghi nhớ cho repair/uninstall. File ngoài bộ cài được giữ lại; thư viện `%LOCALAPPDATA%\ChineseTranscriber` nằm ngoài thư mục cài.

Đã kiểm tra cài/gỡ (exit 0), đối chiếu đủ 1.222 file, lối tắt, khởi động launcher đã cài và SQLite integrity; kiểm tra đường dẫn mặc định mà không cài vào profile thật. Sau khi gỡ, sản phẩm/lối tắt/file ứng dụng được xóa, file người dùng và thư viện thử nghiệm vẫn còn. Script kiểm tra từ chối thao tác nếu sản phẩm hoặc đường dẫn installer đã tồn tại; mọi cài/gỡ thử đều dùng thư mục riêng trong `.test-data/installer`.

Smart App Control vẫn On trong lần kiểm tra. EXE PyInstaller đã cài vẫn bị chặn 4551; launcher trong gói chạy thành công. MSI chưa ký số, nên đây không phải bảo đảm rằng các chính sách Windows khác sẽ cho phép cài/chạy. Báo cáo tại `.test-data/installer/validation.json`.
