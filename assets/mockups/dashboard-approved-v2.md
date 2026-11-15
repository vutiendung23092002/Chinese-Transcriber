# Trang chủ — bố cục ba thẻ ở cột tác vụ

Ảnh duyệt lịch sử: [dashboard-approved-v2.png](dashboard-approved-v2.png). Bản [v3](dashboard-approved-v3.md) thay phần khung cột tác vụ theo lượt duyệt mới; giữ bản này để đối chiếu bố cục.

- Bỏ sáu ô lối tắt trong cột trắng. Ba thẻ hồng / tím / kem chuyển sang cột này, xếp dọc, không lặp lại ở vùng bên phải.
- Giữ nguyên logo, rail capsule, notch, các icon và chiều rộng hai cột bên trái. Tiêu đề cột tác vụ và chân kết nối Codex giữ vị trí cũ.
- Vùng bên phải bắt đầu ngay bằng bốn ô thống kê; ở cửa sổ hẹp thống kê thành hai cột. Thẻ Tiếp tục bài học nằm ngay dưới, có nút Mở thư viện, nguồn gần đây và vùng kéo thả.
- Các nút, số liệu và nhãn trạng thái giữ hành vi của v1, đọc từ thư viện thật.
- Font Inter: tiêu đề thẻ bên trái 20px/700, mô tả 15px/400, CTA 14px/700. Thẻ cao 190px, icon 48px, cách nhau 12px ở cửa sổ 1440×900.
- Cửa sổ thấp hơn 820px: icon đứng cạnh tiêu đề, thẻ cao 160px, cách nhau 8px, giữ nguyên cỡ và độ đậm chữ. Ba thẻ và chân Codex luôn nằm trong cột, không tạo vùng cuộn ở bên trái.
- Thống kê và Tiếp tục bài học giữ font của v1. Vùng kéo thả cao 226px; phần trống phía dưới giữ màu nền ứng dụng như ảnh đã duyệt.

`DashboardActions` sở hữu ba thẻ ở cột tác vụ, `DashboardPage` chỉ chứa thống kê và bài học. Cả hai nằm tại `src/chinese_transcriber/dashboard_page.py`.
