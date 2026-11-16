# Chinese Transcriber 1.0.0 Preview 1

> **PRE-RELEASE — PHẦN LIVE / THU ÂM TRỰC TIẾP CHƯA HOÀN THIỆN.**
> Ưu tiên dùng chức năng dịch file âm thanh. Live đang được hoàn thiện và chưa được nghiệm thu đầy đủ với microphone thực.

Bản Windows x64 cập nhật ngày 16/11/2026. Mã nguồn đúng bản ZIP này: [80567cb](https://github.com/vutiendung23092002/Chinese-Transcriber/commit/80567cb1e8fbc37ccd33383014983495fc853648). Nếu tự build bản cập nhật, dùng commit được liên kết này.

## Cập nhật sửa thanh nháy ở Live

- Sửa đường phân cách 1 px bị hiện thành cửa sổ riêng trong tích tắc khi mở tab Live.
- EXE trong ZIP đã được build lại và xác minh chứa bản sửa; `Run.bat` cũng dùng mã nguồn đã sửa.
- **EXE mới hiện bị Windows Application Control chặn (`4551`) trên máy kiểm tra.** Chưa xác nhận khởi động thành công bằng EXE mới; có thể dùng `Run.bat` đi kèm. Không thay đổi chính sách bảo vệ Windows.

## Tải và chạy

1. Trong **Assets**, tải `ChineseTranscriber-1.0.0-win-x64.zip`.
2. Giải nén toàn bộ ZIP; giữ nguyên các thư mục đi kèm.
3. Mở `ChineseTranscriber.exe`. Gói có thêm `Run.bat` dùng runtime Python chính thức đi kèm.
4. Để dịch sang tiếng Việt, máy cần có Codex CLI và tài khoản ChatGPT đã đăng nhập. Vào **Cài đặt & Codex → Kiểm tra kết nối**. Codex CLI và thông tin đăng nhập không được đóng gói.

Gói đã kèm Qt, FFmpeg, font và ba model SenseVoiceSmall INT8, Streaming Paraformer INT8, Silero VAD. Chép lời chạy cục bộ bằng CPU; không cần cài thêm Python, Docker, WSL hoặc CUDA.

File `.zip.sha256` trong Assets dùng để kiểm tra ZIP sau khi tải, không bắt buộc để chạy ứng dụng.

## Đã kiểm tra

- Toàn bộ 78 test source đạt, gồm ca bắt cửa sổ thừa ngay lúc chuyển sang Live.
- 224 lượt kiểm tra bố cục ở các kích thước, theme và mức scale đều đạt.
- Ca kiểm tra cửa sổ thừa đạt trên backend Qt Windows; launcher Python trong gói được kiểm tra thêm qua sáu lượt chuyển trang/kích thước/theme và không tạo cửa sổ thừa.
- Mã khởi tạo Live trong EXE khớp mã nguồn đã sửa. Kết quả này không thay thế kiểm tra khởi động EXE, đang bị Windows chặn như ghi ở trên.
- Chi tiết kết quả hiện tại và các kiểm tra ASR/Codex/codec của bản build trước nằm trong `docs/VALIDATION.md` và `BUILD-INFO.json` của gói.

## Giới hạn của bản thử nghiệm

- **Live/thu âm trực tiếp chưa hoàn thiện**; các kiểm tra bằng WAV phát lại chưa thay thế nghiệm thu microphone thực. Kết quả thu qua microphone Bluetooth/loa điện thoại chưa được bảo đảm.
- EXE chưa có chữ ký Authenticode; bản cập nhật hiện bị Application Control chặn trên máy kiểm tra. Khả năng chạy phụ thuộc chính sách và đánh giá an toàn của Windows trên từng máy.
- Chưa có đánh giá CER/WER trên tập bài giảng gán nhãn. Hiệu năng phụ thuộc phần cứng và dữ liệu âm thanh. Mốc giờ ở cấp đoạn, chưa căn chỉnh từng từ.
