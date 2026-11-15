# Hướng dẫn sử dụng Chinese Transcriber

## Khởi động

Mở Run.bat trong thư mục portable. Giữ nguyên các thư mục python, src, assets, _internal và models đi kèm. Không cần cài Python, WSL2, Docker hoặc GPU NVIDIA. Chương trình dùng CPU, mặc định tối đa 4 luồng ASR.

ChineseTranscriber.exe cũng nằm trong gói, nhưng artifact cuối bị Smart App Control trên máy phát triển chặn do chữ ký. **Dùng Run.bat** để chạy cùng ứng dụng native bằng runtime Python chính thức có chữ ký đi kèm; đường khởi động này đã được kiểm tra riêng, không sửa chính sách bảo vệ Windows.

Dữ liệu mặc định nằm trong %LOCALAPPDATA%/ChineseTranscriber. Có thể chạy với --portable để đặt thư viện tại thư mục data bên cạnh EXE, hoặc --data-dir để dùng một thư viện riêng. Không mở hai cửa sổ cùng dùng một thư viện.

Hai cột bên trái giữ cùng chiều rộng khi chuyển tab. Cả bảy trang đều có panel tác vụ bo góc, bắt đầu ngang logo/vùng làm việc và kết thúc ngang đáy menu. Chỉ vùng làm việc bên phải cuộn. Nút menu đã được bỏ theo thiết kế đã duyệt.

## Lần đầu

1. Mở Cài đặt & Codex, chọn Kiểm tra kết nối. Ứng dụng tự tìm codex.exe trong PATH hoặc phần mở rộng Codex của VS Code; có thể chọn đường dẫn thủ công.
2. Nếu chưa đăng nhập, chọn Đăng nhập hoặc làm theo hướng dẫn codex login trong Terminal. Nút sao chép chỉ chép hướng dẫn.
3. Chọn model và mức suy luận được tài khoản hỗ trợ. Danh sách lấy trực tiếp từ Codex; lựa chọn không khả dụng không được tự thay thế.
4. Kiểm tra ba mô hình ASR đã có: SenseVoiceSmall INT8, Streaming Paraformer INT8 và Silero VAD. Bản portable đầy đủ đã kèm chúng. Bản không kèm model có nút tải và chọn thư mục.

## Cài đặt & Codex

Trang cài đặt chia sáu thẻ theo thiết kế đã duyệt. Cột trái đưa đến từng nhóm; cửa sổ thấp hoặc hẹp chỉ cuộn phần bên phải.

- Kết nối Codex: xem trạng thái, đăng nhập lại; Đường dẫn & chi tiết mở lựa chọn codex.exe. Hướng dẫn đăng nhập / Tài liệu chứa lệnh và liên kết trợ giúp.
- Hạn mức: thanh thể hiện phần trăm đã dùng do Codex trả về; thiếu số liệu thì hiện thông báo, không coi là 0%.
- Mô hình dịch mặc định: bấm tên trong thẻ để chọn model, bấm/kéo thanh chọn mức suy luận rồi nhấn Lưu mặc định. Nút mũi tên vòng đưa mức suy luận về mặc định của model đang chọn. Xem danh sách hiển thị khả dụng và mức suy luận. Lựa chọn cũ không được hỗ trợ được giữ có cảnh báo.
- Giao diện: nhấn ô Sáng hoặc Tối để áp dụng; vị trí đang xem trong trang cài đặt được giữ.
- Nhận dạng: xem ba model đã tải hay chưa, chỉnh số luồng CPU (1–4), mở Quản lý mô hình để tải hoặc đổi thư mục.
- Dữ liệu: Sao lưu ngay sao lưu SQLite; Mở thư mục truy cập thư viện. Nếu có tác vụ gián đoạn, lối phục hồi xuất hiện tại đây.

## Trang chủ

Ba thẻ màu xếp dọc trong panel bo góc bên trái giúp chọn âm thanh, mở màn ghi âm hoặc soạn bộ thuật ngữ, thay cho sáu ô lối tắt cũ. Panel bắt đầu ngang logo và hàng thống kê, kết thúc ngang đáy menu; trạng thái kết nối nằm bên trong panel. Bốn ô thống kê nằm đầu vùng bên phải, hiển thị số nguồn, số phiên bản đã lưu, lần dịch gần nhất và model mặc định từ thư viện hiện tại; không tính mục trong Thùng rác.

Trong **Tiếp tục bài học**, chọn **Mở bài học** cạnh nguồn gần đây hoặc **Mở thư viện** để xem tất cả. Nhãn cho biết nguồn chưa chép lời, đã chép lời hay trạng thái dịch thực tế. Kéo thả một file vào vùng nét đứt, hoặc bấm vùng này để chọn file; kết thúc tác vụ/ghi âm đang chạy trước khi nhập nguồn mới. Ở cửa sổ hẹp, chỉ vùng nội dung bên phải cuộn, sidebar giữ nguyên.

## Dịch file

Chọn Dịch file ghi âm, kéo thả hoặc chọn WAV, MP3, M4A, FLAC, OGG, AAC hay định dạng FFmpeg đọc được. File ngoài của bạn được giữ nguyên; ứng dụng sao chép một bản vào thư viện và dùng SHA-256 để tránh nhập trùng nội dung.

Nhập bối cảnh, chọn bộ thuật ngữ. Trong thẻ **Mô hình & suy luận**, bấm tên để đổi model; bấm hoặc kéo từng nấc để đổi mức suy luận (cũng dùng được phím mũi tên, Home/End). Số nấc tùy model được Codex xác nhận; nút đặt lại đưa về mức mặc định của model đó. Nếu hiện Không khả dụng/Không hỗ trợ/Chưa xác minh, kiểm tra kết nối và chọn lại trước khi dịch.

Khi Codex đã kết nối và có model khả dụng, bấm **Chép lời và dịch**. Đoạn tiếng Trung nào chốt xong sẽ được lưu và đưa ngay vào hàng đợi dịch; chép lời vẫn tiếp tục trong khi dịch đang chạy. Tiếng Việt xuất hiện ở đúng hàng khi có kết quả. Thanh trạng thái cho biết số đoạn đã chốt, đã dịch và còn chờ. Hàng đợi dùng các đoạn đang có, tối đa 6 đoạn mỗi lượt, không đợi chép lời xong toàn bộ file mới dịch.

Nếu dịch chậm hoặc lỗi, chép lời vẫn tiếp tục và các đoạn chờ được giữ. **Dừng tác vụ** dừng cả hai luồng; vào **Thư viện → Tiếp tục / thử lại** để tiếp tục bản chép lời/bản dịch đó. Những đoạn đã dịch không bị dịch lại, ID/mốc giờ và phiên bản đã lưu được giữ. Nếu chép lời còn thiếu, ứng dụng đọc lại nguồn để tiếp tục, bỏ qua nhận dạng những đoạn đã lưu. Chỉ xuất Việt TXT khi toàn bộ chép lời và dịch đã hoàn tất.

Khi chưa có danh sách model Codex, nút vẫn là **Chép lời tiếng Trung** và chạy cục bộ. Nút **Tạo bản dịch** dùng để dịch bản Trung hoàn chỉnh đã có hoặc tạo bản dịch khác theo model/bối cảnh mới. Mỗi lần bắt đầu chép lời mới hay tạo bản dịch riêng đều giữ lịch sử cũ và âm thanh nguồn. Hai nút không có số thứ tự. Màn Ghi âm trực tiếp dùng cùng thẻ chọn model và suy luận; thiết lập bị khóa trong phiên ghi âm.

Trong thẻ âm thanh, mở **Xuất văn bản** → **Tiếng Trung (.txt)** hoặc **Tiếng Việt (.txt)** để xuất UTF-8, có mốc thời gian. Chỉ bật xuất Việt khi bản dịch đầy đủ. Tiếp tục/thử lại từ Thư viện để xử lý đoạn còn thiếu.

Tên file luôn hiện một dòng, rút gọn ở giữa khi dài và giữ phần cuối cùng định dạng file; rê chuột để xem tên đầy đủ. Vùng Trung–Việt mở rộng theo cửa sổ, có trạng thái chờ trước khi chép lời. Thanh phát phía dưới hiển thị dạng sóng từ âm thanh gốc, hỗ trợ bấm/kéo để tua, đổi tốc độ và bật/tắt âm thanh. Nút tạo bản dịch chỉ bật khi có bản chép lời hoàn tất. Các tab không còn tiêu đề và mô tả lặp lại ở đầu vùng làm việc; thanh menu sidebar giữ nguyên.

## Ghi âm trực tiếp

Chọn microphone thật từ danh sách, kiểm tra bối cảnh/thuật ngữ và cấu hình dịch trước khi bấm Bắt đầu. Thiết lập bị khóa trong phiên; nút Tạm dừng/tiếp tục và Dừng & lưu điều khiển ghi âm.

Thanh điều khiển ở đầu thẻ hiển thị trạng thái, đồng hồ, mức microphone và các nút ghi âm. Cửa sổ hẹp xếp thanh thành hai hàng. Bảng Trung–Việt mở rộng ở giữa, vùng **Câu đang nghe · Chưa chốt** nằm riêng phía dưới; có thể chọn/sao chép văn bản đang nhận dạng. Đồng hồ chỉ tăng theo số mẫu đã thu, mức mic về 0 khi tạm dừng.

Âm thanh được ghi liên tục vào journal PCM, độc lập với ASR và dịch. Chữ tạm thời có thể thay đổi và không được gửi dịch. Sau khi VAD chốt một đoạn lời nói, SenseVoice xử lý bản cuối; Codex dịch đoạn đã chốt vào đúng hàng. Bản dịch có thể đến chậm hơn lời nói.

Chọn đúng microphone theo tên và trình điều khiển; ứng dụng tìm lại thiết bị trước khi thu, không dựa vào số thứ tự cũ sau khi kết nối lại tai nghe. Mức mic cập nhật khoảng 3 lần/giây; rê chuột để xem dBFS của tín hiệu gốc. Cảnh báo tín hiệu nhỏ/im lặng/vỡ tiếng kéo dài không làm dừng ghi hoặc sửa âm thanh. Nếu dùng loa ngoài điện thoại cho mic tai nghe thu, xem hướng dẫn kiểm tra bộ lọc tiếng gọi trong **Xử lý sự cố**. Kết quả nhận dạng chỉ có dấu câu được bỏ qua.

Nếu Codex chưa được xác nhận, phiên vẫn ghi âm và chép lời; cột Việt nói rõ chưa kết nối dịch. Nếu thiết bị không trả mẫu âm thanh, đồng hồ vẫn ở 00:00, báo chờ dữ liệu và không báo lưu thành công một bản ghi rỗng. Công tắc **Theo đoạn mới nhất** tự cuộn đến câu mới; cuộn lên đọc sẽ tắt tự theo, bật lại để trở về cuối bảng.

Khi dừng, ứng dụng lưu nguồn và các câu đã có. Phần dịch còn chờ được giữ trong phiên bản để tiếp tục từ Thư viện. Cuộn lên đọc sẽ tắt theo đoạn mới; bật lại Theo đoạn mới nhất khi muốn.

## Xem và hiệu đính

Trong Thư viện, một hàng là một âm thanh; phần **Phiên bản đã lưu** nằm bên cạnh trên cửa sổ rộng và chuyển xuống dưới ở cửa sổ hẹp. Thanh tìm kiếm lọc cả tên bài và tên file; **Tất cả âm thanh** xóa tìm kiếm và đọc lại danh sách. Nhập âm thanh từ nút trên cùng, nút ở trạng thái trống hoặc cột trái. Tên dài rút gọn ở giữa, rê chuột xem đầy đủ.

Chọn nguồn để xem bản chép lời và các bản dịch, trạng thái, model, mức suy luận, ngày lưu. **Mở bản chép lời** mở riêng chữ Trung; **Mở bản dịch** mở đúng phiên bản trong timeline Trung–Việt. Bản dịch chưa hoàn tất có **Tiếp tục / thử lại**; **So sánh hai phiên bản** dùng hai bản gần nhất và chỉ ghép được khi cùng transcript. Phần phiên bản có thanh cuộn khi cần. Xóa vẫn chuyển vào Thùng rác và giữ bước xác nhận.

Nhấn mốc giờ để tua, dùng nút phát/tạm dừng và tốc độ 0,75–1,5×. Nhấp đúp ô Trung hoặc Việt để hiệu đính. Sửa Trung tạo transcript mới; sửa Việt tạo phiên bản dịch mới, không ghi đè lịch sử. Bật Ghi chú thuật ngữ khi cần. So sánh hai phiên bản chỉ ghép từng đoạn khi chúng dùng cùng transcript.

## Prompt & Thuật ngữ

Tạo bộ theo môn học; điền tên, bối cảnh và bảng Trung / Việt ưu tiên / ghi chú. Dòng không dùng có thể để trống, thuật ngữ cần đủ hai ngôn ngữ và không trùng mục Trung. Lưu rồi áp dụng ở File hoặc Live. Mỗi bản dịch giữ bản chụp ngữ cảnh và thuật ngữ đã dùng lúc tạo.

Trạng thái **Chưa lưu/Đã lưu** nằm cạnh tên bộ. Bộ đếm chỉ tính các dòng đủ Trung/Việt; rê chuột lên bộ đếm để xem số dòng chưa hoàn tất. Nhấp đúp ô để sửa, dùng **Thêm dòng** hoặc chọn ô/dòng rồi **Xóa dòng chọn**. Dòng gợi ý trống không được lưu thành thuật ngữ. Nút **Lưu bộ thuật ngữ** ở cuối bên phải cũng lưu nội dung ô đang nhập. Khi cửa sổ thấp, phần bối cảnh co lại để giữ đủ bảng và các nút.

Nếu có thay đổi chưa lưu, ứng dụng hỏi Lưu / Bỏ thay đổi / Hủy khi chuyển trang, đổi bộ hoặc đóng cửa sổ. Chọn Hủy để tiếp tục chỉnh sửa; lỗi thuật ngữ sẽ giữ bạn ở bộ hiện tại.

## Xóa và khôi phục

Xóa một bản dịch chuyển nó vào Thùng rác, giữ âm thanh và các bản khác. Khi xóa bản cuối, lựa chọn chuyển cả âm thanh mặc định bỏ chọn. Xóa nguồn nêu rõ số phiên bản liên quan và chuyển cả nhóm vào Thùng rác.

Khôi phục đưa mục về thư viện. Xóa vĩnh viễn chỉ có trong Thùng rác, luôn có xác nhận và không thể hoàn tác. Không có tự động dọn thùng rác.

## Sau sự cố

Tác vụ đang chạy khi chương trình bị đóng bất thường được đánh dấu gián đoạn. Mở Cài đặt để phục hồi bản ghi hoặc tiếp tục dịch. Các đoạn hoàn tất không bị xóa. Bản ghi PCM được giữ cho tới khi nguồn WAV và metadata đã được lưu thành công.

Mỗi lần mở chương trình có bản sao lưu SQLite nhất quán trong backups. Muốn chuyển máy, sao chép toàn bộ thư mục dữ liệu khi ứng dụng đã đóng, không chỉ file SQLite đang dùng.
