# Bối cảnh & Thuật ngữ — bản đã duyệt

Ảnh duyệt trước khi triển khai: [glossary-workspace-approved-v1.png](glossary-workspace-approved-v1.png).

- Thẻ trắng bo góc 20px, trên/dưới ngang panel tác vụ. Bắt đầu ngay bằng Tên bộ thuật ngữ và trạng thái Chưa lưu/Đã lưu; bỏ tiêu đề trang lặp trong thẻ.
- Ô tên cao 44px; bối cảnh cao 140px, có gợi ý và dòng hướng dẫn. Phần Thuật ngữ ưu tiên có bộ đếm và nút Thêm dòng bên phải; bảng ba cột Trung / Việt ưu tiên / Ghi chú giãn theo cửa sổ.
- Bảng có gợi ý trong ô trống, số dòng và hàng cao 52px. Gợi ý chỉ được vẽ, không trở thành dữ liệu lưu. Bộ đếm tính các dòng đủ cặp Trung/Việt; dòng còn thiếu được nêu trong tooltip bộ đếm.
- Nút Xóa dòng chọn ở cuối, chỉ bật khi có ô/dòng được chọn; xóa theo các dòng đang chọn và giữ lại một dòng trống nếu xóa hết. Lưu bộ thuật ngữ nằm góc phải, icon đĩa mềm. Hướng dẫn chỉnh sửa nằm bên trái chân thẻ.
- Inter: tiêu đề panel và Thuật ngữ ưu tiên 22px/700; caption trường 15px/600; input, bảng và nút 15px; header bảng 14px/600; trạng thái và hướng dẫn 13px. Nút chính cao 44px, giữ cỡ chữ khi thu nhỏ.
- Cửa sổ thấp giảm bối cảnh còn 76px và khoảng cách; cửa sổ hẹp ẩn hướng dẫn phụ ở chân thẻ, giữ đủ nút. Danh sách bộ đã lưu nằm trong vùng giới hạn chiều cao của panel, không đẩy chân kết nối ra ngoài.
- Trạng thái thay đổi và bộ đếm có tính cả ô đang gõ. Lưu hoặc chuyển bộ/trang sẽ chốt ô đang chỉnh sửa trước khi kiểm tra thay đổi. Kiểm tra thiếu/trùng thuật ngữ và hộp thoại Lưu/Bỏ thay đổi/Hủy tiếp tục dùng luồng hiện có. Chọn Hủy khôi phục cả bộ đang chọn trong danh sách bên trái.

Widget Qt nằm tại `src/chinese_transcriber/glossary_page.py`; dữ liệu vẫn lưu qua `Store.save_glossary`, không đổi schema và không nhúng ảnh mockup vào ứng dụng.
