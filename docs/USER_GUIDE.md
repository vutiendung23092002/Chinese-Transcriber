# Hướng dẫn sử dụng Chinese Transcriber

## Khởi động

Mở Run.bat trong thư mục portable. Giữ nguyên các thư mục python, src, assets, _internal và models đi kèm. Không cần cài Python, WSL2, Docker hoặc GPU NVIDIA. Chương trình dùng CPU, mặc định tối đa 4 luồng ASR.

ChineseTranscriber.exe cũng nằm trong gói, nhưng artifact cuối bị Smart App Control trên máy phát triển chặn do chữ ký. **Dùng Run.bat** để chạy cùng ứng dụng native bằng runtime Python chính thức có chữ ký đi kèm; đường khởi động này đã được kiểm tra riêng, không sửa chính sách bảo vệ Windows.

Dữ liệu mặc định nằm trong %LOCALAPPDATA%/ChineseTranscriber. Có thể chạy với --portable để đặt thư viện tại thư mục data bên cạnh EXE, hoặc --data-dir để dùng một thư viện riêng. Không mở hai cửa sổ cùng dùng một thư viện.

Hai cột bên trái giữ cùng chiều rộng khi chuyển tab. Chỉ vùng làm việc bên phải cuộn. Nút menu đã được bỏ theo thiết kế đã duyệt.

## Lần đầu

1. Mở Cài đặt & Codex, chọn Kiểm tra kết nối. Ứng dụng tự tìm codex.exe trong PATH hoặc phần mở rộng Codex của VS Code; có thể chọn đường dẫn thủ công.
2. Nếu chưa đăng nhập, chọn Đăng nhập hoặc làm theo hướng dẫn codex login trong Terminal. Nút sao chép chỉ chép hướng dẫn.
3. Chọn model và mức suy luận được tài khoản hỗ trợ. Danh sách lấy trực tiếp từ Codex; lựa chọn không khả dụng không được tự thay thế.
4. Kiểm tra ba mô hình ASR đã có: SenseVoiceSmall INT8, Streaming Paraformer INT8 và Silero VAD. Bản portable đầy đủ đã kèm chúng. Bản không kèm model có nút tải và chọn thư mục.

## Dịch file

Chọn Dịch file ghi âm, kéo thả hoặc chọn WAV, MP3, M4A, FLAC, OGG, AAC hay định dạng FFmpeg đọc được. File ngoài của bạn được giữ nguyên; ứng dụng sao chép một bản vào thư viện và dùng SHA-256 để tránh nhập trùng nội dung.

Nhập bối cảnh, chọn bộ thuật ngữ, model và effort. Chọn Chép lời tiếng Trung, xem lại các đoạn rồi chọn Tạo bản dịch mới. Mỗi lần dịch tạo phiên bản riêng; các bản cũ và nguồn âm thanh được giữ. Có thể dùng lại bản chép lời hoàn chỉnh thay vì chạy ASR lại.

Nhấn Trung TXT hoặc Việt TXT để xuất UTF-8, có mốc thời gian. Bản dịch Việt chưa đầy đủ sẽ không được xuất như một kết quả hoàn tất. Tiếp tục/thử lại từ Thư viện để xử lý đoạn còn thiếu.

## Ghi âm trực tiếp

Chọn microphone thật từ danh sách, kiểm tra bối cảnh/thuật ngữ và cấu hình dịch trước khi bấm Bắt đầu. Thiết lập bị khóa trong phiên; nút Tạm dừng/tiếp tục và Dừng & lưu điều khiển ghi âm.

Âm thanh được ghi liên tục vào journal PCM, độc lập với ASR và dịch. Chữ tạm thời có thể thay đổi và không được gửi dịch. Sau khi VAD chốt một đoạn lời nói, SenseVoice xử lý bản cuối; Codex dịch đoạn đã chốt vào đúng hàng. Bản dịch có thể đến chậm hơn lời nói.

Nếu Codex chưa được xác nhận, phiên vẫn ghi âm và chép lời; cột Việt nói rõ chưa kết nối dịch. Nếu thiết bị không trả mẫu âm thanh, đồng hồ vẫn ở 00:00, báo chờ dữ liệu và không báo lưu thành công một bản ghi rỗng.

Khi dừng, ứng dụng lưu nguồn và các câu đã có. Phần dịch còn chờ được giữ trong phiên bản để tiếp tục từ Thư viện. Cuộn lên đọc sẽ tắt theo đoạn mới; bật lại Theo đoạn mới nhất khi muốn.

## Xem và hiệu đính

Trong Thư viện, một hàng là một âm thanh; bảng phiên bản nằm bên cạnh trên cửa sổ rộng và chuyển xuống dưới ở cửa sổ hẹp. Mở bản dịch để xem timeline Trung–Việt cùng hàng.

Nhấn mốc giờ để tua, dùng nút phát/tạm dừng và tốc độ 0,75–1,5×. Nhấp đúp ô Trung hoặc Việt để hiệu đính. Sửa Trung tạo transcript mới; sửa Việt tạo phiên bản dịch mới, không ghi đè lịch sử. Bật Hiện ghi chú thuật ngữ khi cần. So sánh hai phiên bản chỉ ghép từng đoạn khi chúng dùng cùng transcript.

## Prompt & Thuật ngữ

Tạo bộ theo môn học; điền tên, bối cảnh và bảng Trung / Việt ưu tiên / ghi chú. Dòng không dùng có thể để trống, thuật ngữ cần đủ hai ngôn ngữ và không trùng mục Trung. Lưu rồi áp dụng ở File hoặc Live. Mỗi bản dịch giữ bản chụp ngữ cảnh và thuật ngữ đã dùng lúc tạo.

Nếu có thay đổi chưa lưu, ứng dụng hỏi Lưu / Bỏ thay đổi / Hủy khi chuyển trang, đổi bộ hoặc đóng cửa sổ. Chọn Hủy để tiếp tục chỉnh sửa; lỗi thuật ngữ sẽ giữ bạn ở bộ hiện tại.

## Xóa và khôi phục

Xóa một bản dịch chuyển nó vào Thùng rác, giữ âm thanh và các bản khác. Khi xóa bản cuối, lựa chọn chuyển cả âm thanh mặc định bỏ chọn. Xóa nguồn nêu rõ số phiên bản liên quan và chuyển cả nhóm vào Thùng rác.

Khôi phục đưa mục về thư viện. Xóa vĩnh viễn chỉ có trong Thùng rác, luôn có xác nhận và không thể hoàn tác. Không có tự động dọn thùng rác.

## Sau sự cố

Tác vụ đang chạy khi chương trình bị đóng bất thường được đánh dấu gián đoạn. Mở Cài đặt để phục hồi bản ghi hoặc tiếp tục dịch. Các đoạn hoàn tất không bị xóa. Bản ghi PCM được giữ cho tới khi nguồn WAV và metadata đã được lưu thành công.

Mỗi lần mở chương trình có bản sao lưu SQLite nhất quán trong backups. Muốn chuyển máy, sao chép toàn bộ thư mục dữ liệu khi ứng dụng đã đóng, không chỉ file SQLite đang dùng.
