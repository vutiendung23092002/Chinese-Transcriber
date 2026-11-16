# Chinese Transcriber 1.0

Ứng dụng Windows giúp chép lời tiếng Trung bằng CPU, dịch sang tiếng Việt qua Codex CLI và quản lý nguồn âm thanh cùng nhiều phiên bản dịch. Giao diện native Python + PySide6, hỗ trợ chế độ Sáng/Tối.

> **Bản thử nghiệm — Live/thu âm trực tiếp chưa hoàn thiện.** Ưu tiên sử dụng dịch file âm thanh; phần Live chưa được nghiệm thu đầy đủ với microphone thực.

[Tải bản Windows x64 tại GitHub Releases](https://github.com/vutiendung23092002/Chinese-Transcriber/releases). Trong **Assets** có bộ cài MSI và gói ZIP portable. Ghi chú bản hiện tại: [1.0.0 Preview 1](docs/RELEASE_NOTES_v1.0.0-preview.1.md).

Có thêm bộ cài thử nghiệm **`ChineseTranscriber-1.0.0-preview.1-win-x64.msi`** trong Assets. Mở MSI, đợi cài đặt xong rồi mở **Chinese Transcriber** từ Start Menu. Bộ cài dành cho người dùng hiện tại, kèm đầy đủ runtime và model; không cần cài Python riêng. Lối tắt dùng launcher Python chính thức đi kèm, đã kiểm tra chạy được trên máy thử nghiệm khi Smart App Control đang bật. MSI chưa ký số nên vẫn có thể bị chính sách Windows trên máy khác chặn.

## Chạy ứng dụng

Với gói ZIP đã giải nén, mở **ChineseTranscriber.exe**. Với MSI, mở **Chinese Transcriber** từ Start Menu. Gói đầy đủ kèm Python chính thức, Qt, FFmpeg và ba model INT8/VAD; giữ nguyên cả thư mục. Không cần cài Python, Docker, WSL hay GPU NVIDIA.

Bản cập nhật ngày 16/11/2026 đã sửa thanh nháy khi mở Live trong cả EXE và mã nguồn đi kèm. EXE chưa có chữ ký Authenticode: đã bị Windows Application Control chặn (`4551`) trong lần kiểm tra build, nhưng người dùng xác nhận EXE tải từ Release chạy được. **Run.bat tải từ Internet vẫn có thể bị Smart App Control chặn ngay khi mở**, dù EXE chạy được; runtime Python có chữ ký không bảo đảm file BAT được phép chạy. Nếu EXE đang chạy bình thường, tiếp tục dùng EXE. Xem [xử lý lỗi Smart App Control](docs/TROUBLESHOOTING.md#smart-app-control-chặn-runbat-nhưng-exe-vẫn-chạy) và [PACKAGING](docs/PACKAGING.md).

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

Bộ kiểm tra source hiện có 78 test đạt; kiểm tra bố cục 7 trang × 4 kích thước × 2 theme × 4 mức scale đạt. Bản sửa Live không còn tạo cửa sổ phân cách thừa trong kiểm tra Qt Windows và launcher Python trong gói. EXE mới chứa bản sửa nhưng bước chạy kiểm thử tự động bị Windows chặn; phản hồi chạy EXE tải về của người dùng được ghi riêng, không thay thế kiểm thử tích hợp. Bản EXE trước đã qua ASR → Codex thật → hai TXT, giải mã WAV/MP3/M4A, SQLite integrity và giữ nguồn dùng chung; kết quả đó được lưu riêng trong [báo cáo kiểm thử](docs/VALIDATION.md).

**Live/thu âm trực tiếp đang được hoàn thiện.** Tuyến xử lý đã được kiểm tra bằng WAV phát lại với ASR/Codex thật, nhưng chưa được nghiệm thu đầy đủ trên nhiều microphone và driver. Chi tiết môi trường và các giới hạn kiểm tra nằm trong [báo cáo kiểm thử](docs/VALIDATION.md).

Hiệu năng phụ thuộc phần cứng, độ dài và nội dung âm thanh. [Benchmark](docs/ASR_BENCHMARK.json) ghi rõ cấu hình máy thử nghiệm và kết quả đo trên các fixture ngắn; đây không phải cấu hình máy bắt buộc. Chưa có đánh giá CER/WER trên tập bài giảng gán nhãn. Mốc giờ hiện ở cấp đoạn theo VAD/sample, chưa căn chỉnh từng từ.

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

Script build cũng hỗ trợ Python PSF embeddable tại `.tools/python311` nếu runtime này đã được cấu hình để đọc dependency và mã nguồn. Quy trình đóng gói chi tiết: [PACKAGING](docs/PACKAGING.md).

## Tài liệu

- [Hướng dẫn sử dụng](docs/USER_GUIDE.md), [xử lý lỗi](docs/TROUBLESHOOTING.md)
- [Kiểm thử](docs/VALIDATION.md), [tiến độ sáu milestone](docs/IMPLEMENTATION_STATUS.md), [benchmark thô](docs/ASR_BENCHMARK.json)
- [Kiến trúc](docs/ARCHITECTURE.md), [lưu trữ](docs/STORAGE.md), [Codex](docs/CODEX_SETUP.md), [thành phần bên thứ ba](docs/THIRD_PARTY.md)
- Tài liệu Phase 1 và `assets/mockups` giữ làm tham chiếu thiết kế đã duyệt; chương trình thực nằm tại `src/chinese_transcriber`, không nhúng HTML.
