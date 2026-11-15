# Thẻ model và mức suy luận — bản đã duyệt

Ảnh tham chiếu được duyệt trước khi triển khai: [model-selector-approved-v1.png](model-selector-approved-v1.png).

- Thay hai dropdown model/effort bằng một thẻ kiểu Codex: icon tia sét, mức suy luận hiện tại, nút đặt lại, tên model có chevron và thanh chọn theo nấc.
- Thẻ nền tím nhạt ở theme sáng, nền tím tối ở theme tối; bo góc 16px, cao 116px. Font Inter: mức suy luận 16px/700, tên model 15px/400. Giữ bố cục menu, panel bo góc và vùng làm việc đã duyệt.
- Bấm tên mở danh sách model có đánh dấu mục đang chọn. Bấm/kéo thanh hoặc dùng phím mũi tên/Home/End để đổi mức. Nút đặt lại chỉ đưa effort về `defaultReasoningEffort` của model đang chọn.
- Số nấc và giá trị gửi dịch lấy từ `supportedReasoningEfforts` thực tế, không cố định số chấm theo ảnh. Ví dụ Codex trên máy trả sáu mức cho GPT-6.1 Sol và năm mức cho Luna; Extra High tương ứng `xhigh`, còn Max/Ultra tiếp tục nằm sau đó nếu được hỗ trợ.
- Giữ model/effort cũ không còn được hỗ trợ, hiển thị Không khả dụng/Không hỗ trợ/Chưa xác minh; không tự chọn thay. Người dùng chọn lại một mục được xác nhận trước khi dịch.
- Dùng cùng widget trong Dịch file, Ghi âm trực tiếp và model mặc định ở Cài đặt. Cài đặt chỉ ghi mặc định khi bấm Lưu mặc định; File/Live giữ lựa chọn khi chuyển tab, chạy dịch hoặc đóng app.
- Hai nút phía dưới đổi thành **Chép lời tiếng Trung** và **Tạo bản dịch**, bỏ tiền tố `1.` và `2.`; giữ icon, font và trạng thái bật/tắt.

Widget Qt nằm tại `src/chinese_transcriber/model_selector.py`; ảnh chỉ dùng để đối chiếu thiết kế, không nhúng vào giao diện.
