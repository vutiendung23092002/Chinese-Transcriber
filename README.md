# Chinese Transcriber 1.0

Ứng dụng Windows native Python + PySide6: chép lời tiếng Trung bằng CPU, dịch tiếng Việt qua Codex CLI, quản lý nguồn âm thanh và nhiều phiên bản dịch. Phase 2 triển khai theo thiết kế Pastel Light đã duyệt. Có Light/Dark; giữ sidebar capsule và hai cột trái cố định theo kích thước cửa sổ, không cuộn giữa hoặc đổi độ rộng khi chuyển tab.

## Chạy ứng dụng

Mở **Run.bat** tại thư mục dự án, hoặc **Run.bat trong gói dist/ChineseTranscriber**. Gói đầy đủ kèm Python chính thức, Qt, FFmpeg và ba model INT8/VAD; giữ nguyên cả thư mục. Không cần cài Python, Docker, WSL hay GPU NVIDIA.

Gói có **ChineseTranscriber.exe** do PyInstaller tạo, nhưng artifact cuối bị Smart App Control trên máy này chặn vì yêu cầu chữ ký. **Dùng Run.bat**: launcher dùng Python PSF có chữ ký chạy source native đi kèm và đã kiểm tra độc lập. Không thay đổi chính sách Windows. Xem chi tiết tại [PACKAGING](docs/PACKAGING.md).

Dữ liệu mặc định: `%LOCALAPPDATA%/ChineseTranscriber`. Tùy chọn `--portable` lưu trong `data` cạnh EXE; `--data-dir "D:\ThuVien"` chọn nơi khác. Codex CLI và đăng nhập ChatGPT dùng cài đặt hiện có trên máy; tài khoản/token không nằm trong gói portable.

1. Vào **Cài đặt & Codex → Kiểm tra kết nối**; chọn model/effort được tài khoản xác nhận.
2. **Dịch file** → chọn âm thanh → điền bối cảnh/thuật ngữ → **Chép lời tiếng Trung** → **Tạo bản dịch mới**.
3. Xem timeline cùng hàng, nghe/tua, hiệu đính hoặc xuất **Trung TXT / Việt TXT**.

## Chức năng

- Import WAV/MP3/M4A và các định dạng FFmpeg hỗ trợ; SHA-256 giữ một bản nguồn cho nội dung trùng.
- SenseVoiceSmall INT8 cho bản cuối; Streaming Paraformer INT8 cho chữ tạm thời; Silero VAD xác định ranh giới lời nói. Chỉ gửi câu đã chốt sang dịch.
- Ghi microphone vào journal PCM liên tục, tách khỏi ASR/dịch; tạm dừng, tiếp tục, dừng/lưu và phục hồi sau gián đoạn.
- Codex app-server thật: đọc model/effort, xác minh trước khi chạy, JSON có kiểm tra ID, hàng đợi/thử lại, hạn mức khi server cung cấp.
- Bối cảnh và bộ thuật ngữ được lưu theo từng phiên bản. Sửa nội dung tạo bản mới; kết quả cũ được giữ.
- Thư viện, tìm kiếm, phiên bản, so sánh, Thùng rác/khôi phục/xóa vĩnh viễn có xác nhận; SQLite transaction và sao lưu.

## Kết quả xác minh và giới hạn

Python launcher trong gói đã chạy ASR → Codex thật → hai TXT; Qt giải mã WAV/MP3/M4A, SQLite integrity và nguồn dùng chung đều đạt. Bộ kiểm tra source hiện có 24 test đạt; kiểm tra bố cục 7 trang × 4 kích thước × 2 theme × 4 mức scale đạt. Trang Cài đặt mới triển khai theo ảnh đã duyệt, kiểm tra thêm bằng Qt Windows và Codex thật ở năm kích thước. Một bản EXE trước đã qua luồng ASR/dịch; EXE hiện chưa thể nghiệm thu chạy vì Smart App Control chặn, không đánh đồng với kết quả Python launcher.

Microphone Bluetooth soundcore R60i NC trên máy phát triển được nhận diện nhưng cả PortAudio và Qt trả **0 mẫu âm thanh**. Pipeline live đã qua kiểm tra bằng WAV tiếng Trung chính thức đưa vào đầu vào capture, dùng ASR/Codex thật; chưa xác nhận thu giọng nói trực tiếp trên thiết bị này. Ứng dụng báo chờ dữ liệu và không báo thành công với bản ghi rỗng.

Benchmark chạy trên **Intel i7-12700F / 31,8 GiB**, CPU 4 luồng; chưa đo trên Ryzen 5 7535HS / 16 GB. Các fixture ngắn dùng đo tốc độ, chưa có đánh giá CER/WER trên bài giảng. Mốc giờ theo VAD/sample, chưa phải căn chỉnh từng từ. Xem [báo cáo kiểm thử](docs/VALIDATION.md).

## Phát triển và đóng gói

Python 3.11 x64 trên Windows:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.venv\Scripts\python.exe -m pip install --no-deps -e .
.venv\Scripts\python.exe -m chinese_transcriber.models --root models
.venv\Scripts\python.exe -m chinese_transcriber.app
$env:QT_QPA_PLATFORM='offscreen'
.venv\Scripts\python.exe -m pytest -q
.\scripts\build_windows.ps1 -Python .venv\Scripts\python.exe
```

Ở workspace bàn giao, `.tools/python311/python.exe` là runtime PSF 3.11.9 đã xác minh, đọc dependency trong `.venv` và source trong `src`; có thể dùng thay `.venv/Scripts/python.exe`. Script build cũng tự chọn runtime này nếu có. Quy trình chi tiết: [PACKAGING](docs/PACKAGING.md).

## Tài liệu

- [Hướng dẫn sử dụng](docs/USER_GUIDE.md), [xử lý lỗi](docs/TROUBLESHOOTING.md)
- [Kiểm thử](docs/VALIDATION.md), [tiến độ sáu milestone](docs/IMPLEMENTATION_STATUS.md), [benchmark thô](docs/ASR_BENCHMARK.json)
- [Kiến trúc](docs/ARCHITECTURE.md), [lưu trữ](docs/STORAGE.md), [Codex](docs/CODEX_SETUP.md), [thành phần bên thứ ba](docs/THIRD_PARTY.md)
- Tài liệu Phase 1 và `assets/mockups` giữ làm tham chiếu thiết kế đã duyệt; chương trình thực nằm tại `src/chinese_transcriber`, không nhúng HTML.
