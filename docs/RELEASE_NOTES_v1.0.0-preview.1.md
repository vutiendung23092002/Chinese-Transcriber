# Chinese Transcriber 1.0.0 Preview 1

> **PRE-RELEASE — PHẦN LIVE / THU ÂM TRỰC TIẾP CHƯA HOÀN THIỆN.**
> Ưu tiên dùng chức năng dịch file âm thanh. Live đang được hoàn thiện và chưa được nghiệm thu đầy đủ với microphone thực.

Bản Windows x64 cập nhật ngày 16/11/2026. ZIP và MSI được build lại cùng đợt từ mã ứng dụng [e12403f](https://github.com/vutiendung23092002/Chinese-Transcriber/commit/e12403fddc7ff48f58bf697868d48f12734d49d9); commit và SHA-256 EXE cũng được ghi trong `BUILD-INFO.json` bên trong gói. EXE nằm trong ZIP và cần các thư mục đi kèm. Tag Preview 1 được giữ nguyên.

## Dịch file với hai chế độ

- Thêm toggle **Dịch cả bài một lượt** dưới phần chọn model. **Tắt:** dịch song song như trước, tối đa 6 đoạn đang chờ mỗi lượt. **Bật:** chép lời hoàn tất rồi gửi toàn bộ bản Trung trong một lượt dịch; giữ nguyên ID, dòng và mốc giờ.
- Ghi nhớ lựa chọn và lưu chế độ riêng cho từng tác vụ. Tiếp tục bài dở giữ nguyên chế độ và các phần đã lưu.
- Bỏ nút phụ **Tạo bản dịch**. Khi chọn **Bản chép lời** đã hoàn chỉnh, nút chính đổi thành **Dịch bản chép lời**, không cần nhận dạng âm thanh lại.
- Bỏ viền khi bấm chọn model và nét đứt khi bấm toggle. Điều khiển bằng bàn phím vẫn hoạt động.
- Lượt dịch cả bài chờ tối đa 15 phút mỗi lần thử. Nếu bài vượt giới hạn của model, ứng dụng giữ bản Trung và báo lỗi; không tự chia thành các lượt nhỏ.
- `Run.bat` trong source ưu tiên runtime Python PSF chính thức đã cấu hình trước `.venv`. Thay đổi này xử lý trường hợp Windows chặn launcher Python chưa ký số trong `.venv`, không sửa chính sách bảo mật.

## Cập nhật sửa thanh nháy ở Live

- Sửa đường phân cách 1 px bị hiện thành cửa sổ riêng trong tích tắc khi mở tab Live.
- EXE trong ZIP đã được build lại và xác minh chứa bản sửa; `Run.bat` cũng dùng mã nguồn đã sửa.
- EXE, MSI và BAT chưa có bảo đảm chạy trên mọi chính sách Windows. Trước đợt build này, EXE đã từng bị chặn `4551` trong kiểm tra tại chỗ, nhưng người dùng mở được EXE tải về; BAT mang dấu nguồn Internet lại bị chặn ngay khi mở. Kết quả từng gói được ghi riêng trong `BUILD-INFO.json` và `docs/VALIDATION.md`.
- **Với ZIP, ưu tiên mở `ChineseTranscriber.exe`.** `Run.bat` tải từ Internet có thể bị chặn ngay khi mở, dù runtime Python đi kèm có chữ ký. Không cần chuyển sang BAT khi EXE đang chạy bình thường.

## Tải và chạy

### Bộ cài MSI thử nghiệm

1. Tải **`ChineseTranscriber-1.0.0-preview.1-win-x64.msi`** trong Assets rồi mở file.
2. Đợi Windows Installer hoàn tất. Bộ cài dùng giao diện tiến trình cơ bản và tự cài cho người dùng hiện tại tại `%LOCALAPPDATA%\Programs\ChineseTranscriber`.
3. Mở **Chinese Transcriber** từ Start Menu. Lối tắt dùng runtime Python chính thức đi kèm để chạy ứng dụng; không cần cài Python riêng.
4. Có thể gỡ từ **Settings → Apps → Installed apps**. Bộ cài không quản lý thư viện dữ liệu mặc định tại `%LOCALAPPDATA%\ChineseTranscriber`; dữ liệu đó được giữ lại khi gỡ.

MSI đợt này đã được Windows Installer trích xuất thành công: đủ 1.220 file, hash manifest khớp, định nghĩa lối tắt đúng, launcher từ bản trích xuất chạy exit 0 và SQLite integrity ok. Máy kiểm tra đã có bản MSI đang cài nên đợt này không chạy lại chu kỳ cài/gỡ; đã xác minh bản đang cài, đăng ký sản phẩm và file EXE cũ được giữ nguyên. Đợt MSI trước đã qua kiểm tra cài/gỡ riêng. Chi tiết trong `docs/VALIDATION.md`.

**MSI chưa có chữ ký số và không bảo đảm chạy trên mọi máy.** EXE mới bị Application Control chặn 4551 khi kiểm tra khởi động tại máy build; launcher Python trong gói chạy được. Lối tắt Start Menu dùng launcher này.

### Gói ZIP portable

1. Trong **Assets**, tải `ChineseTranscriber-1.0.0-win-x64.zip`.
2. Giải nén toàn bộ ZIP; giữ nguyên các thư mục đi kèm.
3. Mở `ChineseTranscriber.exe`. Giữ `Run.bat` như launcher phụ; đây không phải cách khắc phục Smart App Control được bảo đảm. File BAT tải từ Internet có thể bị chặn dù EXE chạy được.
4. Để dịch sang tiếng Việt, máy cần có Codex CLI và tài khoản ChatGPT đã đăng nhập. Vào **Cài đặt & Codex → Kiểm tra kết nối**. Codex CLI và thông tin đăng nhập không được đóng gói.

Gói đã kèm Qt, FFmpeg, font và ba model SenseVoiceSmall INT8, Streaming Paraformer INT8, Silero VAD. Chép lời chạy cục bộ bằng CPU; không cần cài thêm Python, Docker, WSL hoặc CUDA.

Các file `.sha256` trong Assets dùng để kiểm tra ZIP hoặc MSI sau khi tải, không bắt buộc để chạy ứng dụng.

## Đã kiểm tra

- Toàn bộ 90 test source đạt, gồm hai chế độ dịch, dừng/tiếp tục, lưu kết quả nguyên tử và ca bắt cửa sổ thừa ngay lúc chuyển sang Live.
- 224 lượt kiểm tra bố cục ở các kích thước, theme và mức scale đều đạt.
- Ca kiểm tra cửa sổ thừa đạt trên backend Qt Windows; launcher Python trong gói được kiểm tra thêm qua sáu lượt chuyển trang/kích thước/theme và không tạo cửa sổ thừa.
- Luồng chép lời toàn bộ rồi dịch đã được thử bằng ASR và Codex thật; đúng một lượt dịch sau khi transcript hoàn tất, giữ timeline và xuất Trung/Việt TXT.
- Bản portable mới qua smoke và ASR/codec WAV, MP3, M4A; WAV gọi Codex thật, xuất Trung/Việt TXT và SQLite integrity ok. Chính source/model trong gói cũng được thử chế độ cả bài: 3 đoạn được dịch trong một lượt sau ASR.
- Bytecode trong EXE của 7 module chính khớp source `e12403f`; kiểm tra này không thay thế khởi động EXE đang bị Windows chặn.
- Bản `Run.bat` trong Downloads khớp SHA-256 với bản build, nhưng có `Zone.Identifier` với `ZoneId=3` (nguồn Internet); bản build tại chỗ không có dấu này. Thông báo người dùng chụp phù hợp với việc Windows chặn BAT theo nguồn tải. [Tài liệu Microsoft về dấu nguồn Internet](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/unblock-file#description).
- Chi tiết kết quả hiện tại và các kiểm tra ASR/Codex/codec của bản build trước nằm trong `docs/VALIDATION.md` và `BUILD-INFO.json` của gói.

## Giới hạn của bản thử nghiệm

- **Live/thu âm trực tiếp chưa hoàn thiện**; các kiểm tra bằng WAV phát lại chưa thay thế nghiệm thu microphone thực. Kết quả thu qua microphone Bluetooth/loa điện thoại chưa được bảo đảm.
- EXE và MSI chưa có chữ ký Authenticode của nhà phát hành. EXE, MSI và BAT có thể bị Windows đánh giá khác nhau; kiểm tra chạy được tại chỗ không bảo đảm bản tải từ Internet được phép mở. Xem [Smart App Control FAQ của Microsoft](https://support.microsoft.com/en-us/windows/security/threat-malware-protection/smart-app-control-frequently-asked-questions).
- Chưa có đánh giá CER/WER trên tập bài giảng gán nhãn. Hiệu năng phụ thuộc phần cứng và dữ liệu âm thanh. Mốc giờ ở cấp đoạn, chưa căn chỉnh từng từ.
