# Ghi âm trực tiếp — bản đã duyệt

Ảnh duyệt cuối: [live-workspace-approved-v1.png](live-workspace-approved-v1.png). Người dùng yêu cầu bỏ trọn cụm icon, tiêu đề **Sẵn sàng ghi âm** và dòng mô tả trên cùng; không chừa chỗ của cụm này.

- Một thẻ trắng bo góc 20px, trên/dưới ngang panel tác vụ. Bắt đầu bằng thanh điều khiển: trạng thái, đồng hồ, tín hiệu microphone và ba nút Bắt đầu ghi âm / Tạm dừng / Dừng & lưu.
- Nút chính có chấm hồng, cao 44px; ba nút giữ chiều rộng khi đổi Tạm dừng thành Tiếp tục. Thanh mức mic dùng các vạch rời, 0% không có vạch sáng, không tạo dạng sóng giả.
- Toolbar Bản chép lời có công tắc Theo đoạn mới nhất. Bảng ba cột Mốc giờ / TIẾNG TRUNG / TIẾNG VIỆT giãn theo cửa sổ; trạng thái chờ nằm giữa bảng. Các hàng thật có thể giãn để đọc đủ câu dài.
- Câu đang nghe nằm trong khung tím nhạt nét đứt phía dưới, có nhãn Chưa chốt. Văn bản chưa chốt chỉ ở vùng này; bảng chỉ nhận câu đã chốt và bản dịch đúng ID.
- Inter: tiêu đề panel tác vụ 22px/700; nhãn 14px; dropdown/nội dung/nút 15px; đồng hồ và tiêu đề giữa bảng 30px/700; Bản chép lời 22px/700; Câu đang nghe 20px/700. Thẻ model/suy luận giữ thiết kế đã duyệt riêng.
- Cửa sổ hẹp xếp thanh ghi âm thành hai hàng; cửa sổ thấp giảm khoảng cách và chiều cao vùng phụ, giữ cỡ chữ và kích thước nút. Chỉ vùng bên phải có thể cuộn, menu gốc và chiều rộng cột trái giữ nguyên.
- Trạng thái dừng/đang ghi/tạm dừng/chờ microphone/đang lưu lấy từ phiên thật. Đồng hồ chỉ tính mẫu âm thanh đã nhận. Không có mẫu thì giữ 00:00 và không báo lưu thành công.

Triển khai Qt tại `src/chinese_transcriber/live_page.py`, dùng cùng bảng transcript và công tắc với màn File. Không nhúng mockup vào giao diện.
