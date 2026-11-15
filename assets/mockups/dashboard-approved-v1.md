# Trang chủ — bản đã duyệt

Lịch sử thiết kế. Bố cục hiện tại dùng [bản v2](dashboard-approved-v2.md), đưa ba thẻ sang cột tác vụ.

Ảnh tham chiếu: [dashboard-approved-v1.png](dashboard-approved-v1.png).

- Giữ nguyên rail, notch, logo và sáu lối tắt ở cột tác vụ; không có tiêu đề đầu vùng làm việc.
- Ba thẻ lớn màu hồng / tím / kem dẫn đến chọn file, chuẩn bị ghi âm và soạn thuật ngữ. Nút ghi âm đưa đến màn chọn microphone, không tự bật microphone.
- Bốn ô thống kê đọc thư viện thật, loại mục trong Thùng rác; model hiển thị tên dễ đọc, giữ nguyên ID cấu hình. Thời điểm dịch hiển thị theo giờ địa phương.
- Khu Tiếp tục bài học có tối đa bốn nguồn gần nhất; tên file một dòng rút gọn giữa, tooltip có tên đầy đủ. Trạng thái lấy từ transcript / phiên bản đang có.
- Mở bài học vào đúng nguồn; Mở thư viện vào danh sách. Vùng nét đứt nhận một file cục bộ hoặc bấm để chọn file; không nhận file mới khi tác vụ hoặc ghi âm đang chạy.
- Cửa sổ hẹp xếp thẻ tác vụ theo chiều dọc và thống kê thành hai cột, chỉ cuộn vùng bên phải. Giữ cỡ chữ thay vì thu nhỏ chữ để ép đủ cột.

Inter được đóng gói cùng app. Ở cửa sổ 1440×900: thẻ tác vụ cao 240px, tiêu đề 26px/700, mô tả 18px/400, CTA 17px/700; thống kê 16px và giá trị 34px/700 (model 30px); Tiếp tục bài học 30px/700; tên file 18px/700; nhãn kéo thả 24px/700 và mô tả 18px/400.

Triển khai native Qt tại `src/chinese_transcriber/dashboard_page.py`. Không dùng ảnh mockup làm giao diện, không tạo số liệu hay file minh họa trong thư viện người dùng.
