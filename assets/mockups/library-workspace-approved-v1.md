# Thư viện — bản đã duyệt

Ảnh duyệt trước khi triển khai: [library-workspace-approved-v1.png](library-workspace-approved-v1.png).

- Một thẻ trắng bo góc 20px, trên/dưới ngang panel tác vụ; thanh tìm kiếm và nút Nhập file mới nằm đầu thẻ. Không thêm tiêu đề trang lặp phía trên.
- Bên trái là Âm thanh với số nguồn đang hiển thị và bảng Âm thanh / Thời lượng / Ngày nhập / Nguồn / Bản dịch. Bên phải là Phiên bản đã lưu. Hai phần chia khoảng 64/36 ở cửa sổ rộng và xếp dọc ở cửa sổ hẹp.
- Thư viện trống có icon tài liệu âm thanh, Chưa có âm thanh, hướng dẫn, nút Nhập file âm thanh và định dạng hỗ trợ. Chưa chọn nguồn thì phần phiên bản hiện Chọn một âm thanh. Không có kết quả tìm kiếm dùng thông báo và nút Xóa tìm kiếm riêng.
- Giữ menu rail gốc và panel tác vụ. Ba nút trái có icon, mục Tất cả âm thanh nền tím nhạt; Nhập âm thanh mới mở chọn file, Thùng rác mở trang tương ứng.
- Inter: tiêu đề cột tác vụ/Âm thanh 22px/700, Phiên bản đã lưu 20px/700, tiêu đề trống 28px/700, tiêu đề chọn nguồn 24px/700, input/nút/nội dung 15px, header bảng 14px/500. Nút chính và ô tìm kiếm cao 44px. Giữ cỡ chữ khi thu nhỏ, giảm khoảng cách và ẩn icon/phần phụ ở vùng trống thấp.
- Nguồn thật hiện tên file rút gọn giữa, giữ đuôi file và tooltip đầy đủ; có thể tìm cả tên bài lẫn tên file, không phân biệt hoa/thường. Mục trong Thùng rác không được tính.
- Chọn nguồn hiện bản chép lời và các bản dịch thật, trạng thái/model/effort/ngày lưu; mở, tiếp tục, so sánh và xóa gọi lại các luồng hiện có. Phần phiên bản cuộn riêng khi dài. Các thao tác ghi bị khóa khi ứng dụng đang bận/ghi âm, vẫn có thể đọc nguồn và phiên bản.

Widget Qt nằm tại `src/chinese_transcriber/library_page.py`. Ảnh là tham chiếu thiết kế, không được nhúng vào ứng dụng.
