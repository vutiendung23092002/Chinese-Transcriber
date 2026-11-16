# Chinese Transcriber 1.0.0 Preview 1

> **PRE-RELEASE — PHẦN LIVE / THU ÂM TRỰC TIẾP CHƯA HOÀN THIỆN.**
> Ưu tiên dùng chức năng dịch file âm thanh. Live đang được hoàn thiện và chưa được nghiệm thu đầy đủ với microphone thực.

Bản Windows x64 build ngày 16/11/2026. Mã ứng dụng trong gói được build từ commit `9fa392c`; tag phát hành có thêm tài liệu và ghi chú này.

## Tải và chạy

1. Trong **Assets**, tải `ChineseTranscriber-1.0.0-win-x64.zip`.
2. Giải nén toàn bộ ZIP; giữ nguyên các thư mục đi kèm.
3. Mở `ChineseTranscriber.exe`. Gói có thêm `Run.bat` dùng runtime Python chính thức đi kèm.
4. Để dịch sang tiếng Việt, máy cần có Codex CLI và tài khoản ChatGPT đã đăng nhập. Vào **Cài đặt & Codex → Kiểm tra kết nối**. Codex CLI và thông tin đăng nhập không được đóng gói.

Gói đã kèm Qt, FFmpeg, font và ba model SenseVoiceSmall INT8, Streaming Paraformer INT8, Silero VAD. Chép lời chạy cục bộ bằng CPU; không cần cài thêm Python, Docker, WSL hoặc CUDA.

File `.zip.sha256` trong Assets dùng để kiểm tra ZIP sau khi tải, không bắt buộc để chạy ứng dụng.

## Đã kiểm tra

- Khởi động trực tiếp bản EXE đóng gói trên Windows 11 x64.
- Nhận dạng tiếng Trung từ WAV, MP3 và M4A bằng model thật.
- Dịch qua Codex thật, kiểm tra ID JSON và xuất TXT Trung/Việt.
- Giải mã âm thanh Qt, kiểm tra SQLite và giữ nguồn sau trash/restore.
- Toàn bộ 77 test source đạt. Chi tiết trong `docs/VALIDATION.md` và `BUILD-INFO.json` của gói.

## Giới hạn của bản thử nghiệm

- **Live/thu âm trực tiếp chưa hoàn thiện**; các kiểm tra bằng WAV phát lại chưa thay thế nghiệm thu microphone thực. Kết quả thu qua microphone Bluetooth/loa điện thoại chưa được bảo đảm.
- EXE chưa có chữ ký Authenticode. Smart App Control trên máy khác có thể chặn dù bản này đã chạy được trên máy kiểm tra.
- Chưa có đánh giá CER/WER trên tập bài giảng gán nhãn. Hiệu năng phụ thuộc phần cứng và dữ liệu âm thanh. Mốc giờ ở cấp đoạn, chưa căn chỉnh từng từ.
