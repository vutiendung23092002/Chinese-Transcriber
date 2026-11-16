# Chinese Transcriber 1.0.0 Preview 1

> **PRE-RELEASE — PHẦN LIVE / THU ÂM TRỰC TIẾP CHƯA HOÀN THIỆN.**
> Ưu tiên dùng chức năng dịch file âm thanh. Live đang được hoàn thiện và chưa được nghiệm thu đầy đủ với microphone thực.

Bản Windows x64 cập nhật ngày 16/11/2026. Mã nguồn đúng bản ZIP này: [80567cb](https://github.com/vutiendung23092002/Chinese-Transcriber/commit/80567cb1e8fbc37ccd33383014983495fc853648). Nếu tự build bản cập nhật, dùng commit được liên kết này.

## Cập nhật sửa thanh nháy ở Live

- Sửa đường phân cách 1 px bị hiện thành cửa sổ riêng trong tích tắc khi mở tab Live.
- EXE trong ZIP đã được build lại và xác minh chứa bản sửa; `Run.bat` cũng dùng mã nguồn đã sửa.
- EXE bị Windows Application Control chặn (`4551`) trong lần kiểm tra build. Sau đó người dùng xác nhận **EXE từ ZIP tải trên Release chạy được**, trong khi mở `Run.bat` bị Smart App Control chặn. Đây là hai kết quả được ghi nhận riêng; không bảo đảm file nào cũng chạy trên mọi máy.
- **Với ZIP, ưu tiên mở `ChineseTranscriber.exe`.** `Run.bat` tải từ Internet có thể bị chặn ngay khi mở, dù runtime Python đi kèm có chữ ký. Không cần chuyển sang BAT khi EXE đang chạy bình thường.

## Tải và chạy

### Bộ cài MSI thử nghiệm

1. Tải **`ChineseTranscriber-1.0.0-preview.1-win-x64.msi`** trong Assets rồi mở file.
2. Đợi Windows Installer hoàn tất. Bộ cài dùng giao diện tiến trình cơ bản và tự cài cho người dùng hiện tại tại `%LOCALAPPDATA%\Programs\ChineseTranscriber`.
3. Mở **Chinese Transcriber** từ Start Menu. Lối tắt dùng runtime Python chính thức đi kèm để chạy ứng dụng; không cần cài Python riêng.
4. Có thể gỡ từ **Settings → Apps → Installed apps**. Bộ cài không quản lý thư viện dữ liệu mặc định tại `%LOCALAPPDATA%\ChineseTranscriber`; dữ liệu đó được giữ lại khi gỡ.

Đã kiểm tra cài đặt và gỡ cài đặt thành công trên Windows 11 x64 khi Smart App Control ở trạng thái On; đối chiếu đủ 1.222 file, lối tắt Start Menu, khởi động launcher và SQLite integrity. Sau khi gỡ, sản phẩm/lối tắt/file ứng dụng đã được xóa, file ngoài bộ cài và thư viện thử nghiệm được giữ lại.

**MSI chưa có chữ ký số và không bảo đảm chạy trên mọi máy.** EXE PyInstaller riêng vẫn bị Application Control chặn 4551 sau khi cài trên máy kiểm tra; lối tắt Start Menu dùng launcher đi kèm đã được kiểm tra chạy thành công.

### Gói ZIP portable

1. Trong **Assets**, tải `ChineseTranscriber-1.0.0-win-x64.zip`.
2. Giải nén toàn bộ ZIP; giữ nguyên các thư mục đi kèm.
3. Mở `ChineseTranscriber.exe`. Giữ `Run.bat` như launcher phụ; đây không phải cách khắc phục Smart App Control được bảo đảm. File BAT tải từ Internet có thể bị chặn dù EXE chạy được.
4. Để dịch sang tiếng Việt, máy cần có Codex CLI và tài khoản ChatGPT đã đăng nhập. Vào **Cài đặt & Codex → Kiểm tra kết nối**. Codex CLI và thông tin đăng nhập không được đóng gói.

Gói đã kèm Qt, FFmpeg, font và ba model SenseVoiceSmall INT8, Streaming Paraformer INT8, Silero VAD. Chép lời chạy cục bộ bằng CPU; không cần cài thêm Python, Docker, WSL hoặc CUDA.

Các file `.sha256` trong Assets dùng để kiểm tra ZIP hoặc MSI sau khi tải, không bắt buộc để chạy ứng dụng.

## Đã kiểm tra

- Toàn bộ 78 test source đạt, gồm ca bắt cửa sổ thừa ngay lúc chuyển sang Live.
- 224 lượt kiểm tra bố cục ở các kích thước, theme và mức scale đều đạt.
- Ca kiểm tra cửa sổ thừa đạt trên backend Qt Windows; launcher Python trong gói được kiểm tra thêm qua sáu lượt chuyển trang/kích thước/theme và không tạo cửa sổ thừa.
- Mã khởi tạo Live trong EXE khớp mã nguồn đã sửa. Bước chạy EXE kiểm thử tự động bị Windows chặn; người dùng sau đó báo EXE tải về chạy được. Phản hồi đó chưa thay thế kiểm thử tích hợp EXE trên nhiều máy.
- Bản `Run.bat` trong Downloads khớp SHA-256 với bản build, nhưng có `Zone.Identifier` với `ZoneId=3` (nguồn Internet); bản build tại chỗ không có dấu này. Thông báo người dùng chụp phù hợp với việc Windows chặn BAT theo nguồn tải. [Tài liệu Microsoft về dấu nguồn Internet](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/unblock-file#description).
- Chi tiết kết quả hiện tại và các kiểm tra ASR/Codex/codec của bản build trước nằm trong `docs/VALIDATION.md` và `BUILD-INFO.json` của gói.

## Giới hạn của bản thử nghiệm

- **Live/thu âm trực tiếp chưa hoàn thiện**; các kiểm tra bằng WAV phát lại chưa thay thế nghiệm thu microphone thực. Kết quả thu qua microphone Bluetooth/loa điện thoại chưa được bảo đảm.
- EXE và MSI chưa có chữ ký Authenticode của nhà phát hành. EXE, MSI và BAT có thể bị Windows đánh giá khác nhau; kiểm tra chạy được tại chỗ không bảo đảm bản tải từ Internet được phép mở. Xem [Smart App Control FAQ của Microsoft](https://support.microsoft.com/en-us/windows/security/threat-malware-protection/smart-app-control-frequently-asked-questions).
- Chưa có đánh giá CER/WER trên tập bài giảng gán nhãn. Hiệu năng phụ thuộc phần cứng và dữ liệu âm thanh. Mốc giờ ở cấp đoạn, chưa căn chỉnh từng từ.
