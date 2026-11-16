# Tiến độ Phase 2

Người dùng đã phê duyệt Pastel Light và cho phép triển khai ứng dụng native Python/PySide6 ngày 14/11/2026.

## Sáu milestone

| Mốc | Kết quả triển khai | Xác minh |
|---|---|---|
| 1. Desktop shell | PySide6 native, bảy trang, Pastel Light/Dark, sidebar capsule không menu, cột trái cố định khi đổi tab | 3 test shell; 224 lượt trang/kích thước/theme/scale đạt; ảnh widget thật đã rà soát |
| 2. Storage/library | SQLite, import/SHA-256, dùng chung audio, transcript và nhiều version, trash/restore/purge, backup | Test quan hệ, import đồng thời, xóa bản riêng, khôi phục nhóm và dữ liệu đã xóa trước đạt |
| 3. Speech-to-text | File SenseVoice/VAD; live Paraformer interim + SenseVoice final; journal thu liên tục | ASR thật và WAV replay qua capture đạt; benchmark cả hai model trên cùng fixture. Micro Bluetooth hiện có trả 0 frame; nghiệm thu thu giọng nói vật lý còn chờ thiết bị có tín hiệu |
| 4. Translation | Codex app-server thật, kiểm tra model/effort, context/glossary, JSON/ID, retry/cancel, quota khi khả dụng | CLI đã cài trả đủ 8 model; dịch thật thành công; JSON sai/thiếu/trùng bị từ chối; không thay model ngầm |
| 5. Integration | Timeline cùng hàng, playback/tua/tốc độ, hiệu đính tạo bản mới, TXT, so sánh, phục hồi | Luồng thật từ WAV đến hai TXT đạt; lỗi ASR không mất PCM, lỗi dịch không mất đoạn xong; tổng 24 test đạt |
| 6. Distribution | EXE PyInstaller build lại ngày 16/11/2026; gói portable có model/font/FFmpeg, hướng dẫn/checksum và launcher Python PSF | EXE mới đạt smoke/ASR/Codex/WAV-MP3-M4A/TXT/SQLite trên máy kiểm tra; bộ source hiện có 77 test đạt |

Mã thực thi nằm tại src/chinese_transcriber. Không nhúng QtWebEngine, trình duyệt hoặc Electron. Các màn hình Phase 1 chỉ còn là tài liệu tham chiếu đã duyệt, không dùng làm runtime.

Trang Cài đặt & Codex đã được thiết kế lại theo ảnh settings-redesign-v1.png do người dùng chốt: sáu thẻ, điều hướng nhóm, quota dạng thanh, chọn theme bằng ô xem trước và các chi tiết nằm trong hộp thoại. Đã đối chiếu screenshot widget native ở năm kích thước, Light/Dark; kiểm tra thêm bằng backend Qt Windows và CLI thật. Bản chạy Python hiện tại được cập nhật; thay đổi UI này chưa tạo một EXE đã ký mới.

## Môi trường xác minh

- Windows 11 Pro; Intel i7-12700F; RAM 31,8 GiB.
- Máy đích theo yêu cầu: Ryzen 5 7535HS / RAM 16 GB. Kết quả đo ở môi trường phát triển phải ghi riêng, không coi là benchmark trên máy đích.
- Codex CLI tìm thấy: 0.169.0-alpha.11.1, trạng thái đã đăng nhập ChatGPT.
- CLI schema được sinh trực tiếp để xác minh giao thức, không đọc token đăng nhập.

Python portable do uv cung cấp bị Windows Application Control chặn DLL chuẩn. Môi trường kiểm tra chuyển sang gói Python 3.11.9 embeddable chính thức, chữ ký Python Software Foundation hợp lệ, không tắt hoặc thay đổi chính sách Windows. EXE portable đã chạy bằng runtime đóng gói này.

## Giới hạn nghiệm thu

Triển khai sáu mốc đã có mã và gói chạy qua EXE mới lẫn Python launcher. Bản EXE ngày 16/11 đã chạy trên máy kiểm tra, chưa có chữ ký Authenticode của nhà phát hành. Chưa xác minh microphone vật lý có tín hiệu trên soundcore R60i NC, chưa benchmark trên Ryzen đích, chưa có CER/WER bài giảng gán nhãn. Timestamp là VAD/sample ở cấp đoạn; chưa forced alignment từng từ hoặc diarization. Chi tiết và bằng chứng tại VALIDATION.md, ASR_BENCHMARK.json và các report riêng trong .test-data. Không đánh đồng các giới hạn này với kiểm thử đã đạt.
