# Chinese Transcriber 1.0

Ứng dụng Windows native Python + PySide6: chép lời tiếng Trung bằng CPU, dịch tiếng Việt qua Codex CLI, quản lý nguồn âm thanh và nhiều phiên bản dịch. Phase 2 triển khai theo thiết kế Pastel Light đã duyệt. Có Light/Dark; giữ sidebar capsule và hai cột trái cố định theo kích thước cửa sổ, không cuộn giữa hoặc đổi độ rộng khi chuyển tab.

> **Bản thử nghiệm — Live/thu âm trực tiếp chưa hoàn thiện.** Ưu tiên sử dụng dịch file âm thanh; phần Live chưa được nghiệm thu đầy đủ với microphone thực.

[Tải bản Windows x64 tại GitHub Releases](https://github.com/vutiendung23092002/Chinese-Transcriber/releases). Chọn file ZIP trong **Assets**, giải nén toàn bộ rồi chạy ứng dụng. Ghi chú bản hiện tại: [1.0.0 Preview 1](docs/RELEASE_NOTES_v1.0.0-preview.1.md).

## Chạy ứng dụng

Mở **ChineseTranscriber.exe** trong gói phát hành, hoặc **Run.bat** tại thư mục dự án/gói dist/ChineseTranscriber. Gói đầy đủ kèm Python chính thức, Qt, FFmpeg và ba model INT8/VAD; giữ nguyên cả thư mục. Không cần cài Python, Docker, WSL hay GPU NVIDIA.

EXE build ngày 16/11/2026 đã chạy trực tiếp trên máy kiểm tra. EXE chưa có chữ ký Authenticode; Smart App Control trên máy khác vẫn có thể chặn. Gói có thêm **Run.bat**: launcher dùng Python PSF có chữ ký chạy source native đi kèm. Không thay đổi chính sách Windows. Xem chi tiết tại [PACKAGING](docs/PACKAGING.md).

Dữ liệu mặc định: `%LOCALAPPDATA%/ChineseTranscriber`. Tùy chọn `--portable` lưu trong `data` cạnh EXE; `--data-dir "D:\ThuVien"` chọn nơi khác. Codex CLI và đăng nhập ChatGPT dùng cài đặt hiện có trên máy; tài khoản/token không nằm trong gói portable.

1. Vào **Cài đặt & Codex → Kiểm tra kết nối**; chọn model/effort được tài khoản xác nhận.
2. **Dịch file** → chọn âm thanh → điền bối cảnh/thuật ngữ → **Chép lời và dịch**. Đoạn chốt xong được đưa sang dịch song song, phần chép lời vẫn chạy. **Tạo bản dịch** dùng khi muốn dịch lại bản Trung đã có.
3. Xem timeline cùng hàng, nghe/tua, hiệu đính hoặc xuất **Trung TXT / Việt TXT**.

## Chức năng

- Import WAV/MP3/M4A và các định dạng FFmpeg hỗ trợ; SHA-256 giữ một bản nguồn cho nội dung trùng.
- SenseVoiceSmall INT8 cho bản cuối; Streaming Paraformer INT8 cho chữ tạm thời; Silero VAD xác định ranh giới lời nói. Chỉ gửi câu đã chốt sang dịch.
- Ghi microphone vào journal PCM liên tục, tách khỏi ASR/dịch; tạm dừng, tiếp tục, dừng/lưu và phục hồi sau gián đoạn.
- Codex app-server thật: đọc model/effort, xác minh trước khi chạy, JSON có kiểm tra ID, hàng đợi/thử lại, hạn mức khi server cung cấp.
- Bối cảnh và bộ thuật ngữ được lưu theo từng phiên bản. Sửa nội dung tạo bản mới; kết quả cũ được giữ.
- Thư viện, tìm kiếm, phiên bản, so sánh, Thùng rác/khôi phục/xóa vĩnh viễn có xác nhận; SQLite transaction và sao lưu.

## Kết quả xác minh và giới hạn

Bản EXE build ngày 16/11/2026 đã khởi động và chạy ASR → Codex thật → hai TXT; Qt giải mã WAV/MP3/M4A, SQLite integrity và nguồn dùng chung đều đạt. Bộ kiểm tra source hiện có 77 test đạt; kiểm tra bố cục 7 trang × 4 kích thước × 2 theme × 4 mức scale đạt. Các màn File, Ghi âm, Thư viện, Thuật ngữ và Cài đặt triển khai theo ảnh đã duyệt; danh sách model và số nấc suy luận lấy từ Codex thật. Gói vẫn có Python launcher để dùng khi cần.

Microphone Bluetooth soundcore R60i NC trên máy phát triển được nhận diện nhưng cả PortAudio và Qt trả **0 mẫu âm thanh**. Pipeline live đã qua kiểm tra bằng WAV tiếng Trung chính thức đưa vào đầu vào capture, dùng ASR/Codex thật; chưa xác nhận thu giọng nói trực tiếp trên thiết bị này. Ứng dụng báo chờ dữ liệu và không báo thành công với bản ghi rỗng.

Benchmark chạy trên **Intel i7-12700F / 31,8 GiB**, CPU 4 luồng; chưa đo trên Ryzen 5 7535HS / 16 GB. Các fixture ngắn dùng đo tốc độ, chưa có đánh giá CER/WER trên bài giảng. Mốc giờ theo VAD/sample, chưa phải căn chỉnh từng từ. Kiểm tra bổ sung phần microphone và loại kết quả chỉ có dấu câu đưa tổng số test lên **64**; chưa xác nhận cải thiện độ chính xác khi thu loa điện thoại qua mic tai nghe thực. Xem [báo cáo kiểm thử](docs/VALIDATION.md).

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

Sau khi cài môi trường và tải model, mở `Run.bat` để chạy từ source. Launcher tự dùng `.venv\Scripts\pythonw.exe` nếu có.

Ở workspace bàn giao, `.tools/python311/python.exe` là runtime PSF 3.11.9 đã xác minh, đọc dependency trong `.venv` và source trong `src`; có thể dùng thay `.venv/Scripts/python.exe`. Script build cũng tự chọn runtime này nếu có. Quy trình chi tiết: [PACKAGING](docs/PACKAGING.md).

## Tài liệu

- [Hướng dẫn sử dụng](docs/USER_GUIDE.md), [xử lý lỗi](docs/TROUBLESHOOTING.md)
- [Kiểm thử](docs/VALIDATION.md), [tiến độ sáu milestone](docs/IMPLEMENTATION_STATUS.md), [benchmark thô](docs/ASR_BENCHMARK.json)
- [Kiến trúc](docs/ARCHITECTURE.md), [lưu trữ](docs/STORAGE.md), [Codex](docs/CODEX_SETUP.md), [thành phần bên thứ ba](docs/THIRD_PARTY.md)
- Tài liệu Phase 1 và `assets/mockups` giữ làm tham chiếu thiết kế đã duyệt; chương trình thực nằm tại `src/chinese_transcriber`, không nhúng HTML.
