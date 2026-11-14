# Xử lý sự cố

## Microphone nhận diện nhưng đồng hồ vẫn 00:00

Thiết bị chưa trả mẫu âm thanh. Kiểm tra microphone đã kết nối, chế độ đàm thoại của tai nghe Bluetooth, quyền microphone cho ứng dụng desktop trong Windows và chọn đúng thiết bị trong ứng dụng. Thử microphone có dây hoặc microphone tích hợp. Chương trình không lưu một bản ghi rỗng như thành công.

Trong môi trường phát triển, soundcore R60i NC được cả PortAudio và Qt nhận diện nhưng trả 0 mẫu dù quyền Windows là Allow. Vì vậy chưa thể xác nhận thu giọng nói thực qua thiết bị này; ASR live được kiểm tra bằng luồng âm thanh tiếng Trung thật phát lại vào đường xử lý.

## Chưa có model

Mở Cài đặt → nhận dạng giọng nói → tải SenseVoiceSmall, Streaming Paraformer và Silero VAD; hoặc chọn thư mục có ba thư mục con sensevoice, paraformer và vad. Đừng chỉ chọn một file ONNX. Cần kết nối mạng để tải lần đầu; ASR sau đó chạy cục bộ.

## Codex không tìm thấy / chưa đăng nhập

Chọn codex.exe trong Cài đặt. Có thể dùng executable đi kèm phần mở rộng Codex của VS Code hoặc bản CLI độc lập. Đăng nhập bằng nút trong ứng dụng hoặc codex login; kiểm tra lại. Không nhập API key/token vào prompt dịch.

## Model hoặc mức suy luận không khả dụng

Chọn Kiểm tra kết nối để đọc danh sách hiện tại. Lựa chọn cũ không khả dụng được giữ với cảnh báo để bạn tự chọn; ứng dụng không tự thay thế. Nếu CLI đổi giao thức, xem application.log và đối chiếu phiên bản trong Cài đặt.

## Một số đoạn dịch lỗi / hết hạn mức

Nguồn, transcript và các đoạn hoàn tất vẫn còn. Dừng tác vụ, đợi hạn mức nếu cần, rồi mở Thư viện → Tiếp tục/thử lại. Chỉ đoạn chưa hoàn tất được xử lý lại. Không xóa thư viện để sửa lỗi đăng nhập hoặc quota.

## ASR chậm hoặc thiếu đoạn trong Live

Để luồng CPU ở 2–4, đóng ứng dụng nặng và giữ nguồn ghi âm. Nếu hàng đợi ASR chậm quá mức, app giữ âm thanh và đánh dấu cần chép lời lại từ nguồn đã lưu. Không dùng model GPU vì bản hiện tại tối ưu CPU.

## Lưu thất bại / thiếu dung lượng

Không xóa recordings/ khi chưa phục hồi. Dọn dung lượng hoặc chọn thư viện khác; thư viện lỗi không được âm thầm tạo lại. Tạo bản sao toàn bộ dữ liệu trước thao tác sửa thủ công.

## Portable

Giải nén toàn bộ folder và mở **Run.bat**. Không kéo riêng launcher hoặc EXE ra khỏi các thư mục đi kèm. Artifact EXE cuối bị Smart App Control chặn do yêu cầu chữ ký; gói có launcher đã kiểm tra chạy source bằng runtime Python PSF chính thức có chữ ký, không cần cài Python. Không thay đổi chính sách bảo vệ Windows. Xem PACKAGING.md để phân biệt các kết quả kiểm thử của EXE và Python launcher.
