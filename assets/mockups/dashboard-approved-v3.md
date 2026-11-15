# Trang chủ — panel tác vụ bo góc

Ảnh được người dùng duyệt trước khi triển khai: [dashboard-approved-v3.png](dashboard-approved-v3.png). Tiếp nối bố cục ba thẻ bên trái của [v2](dashboard-approved-v2.md).

- Cột tác vụ trở thành panel trắng bo góc 26px, viền mảnh và bóng nhẹ. Nền ngoài panel đồng màu vùng làm việc.
- Mép trên panel ngang hàng logo và hàng thống kê, cách đầu vùng nội dung 24px. Mép dưới ngang đáy menu tối, cách cuối vùng nội dung 18px. Panel không bắt đầu thấp ngang capsule menu.
- Giữ nguyên chiều rộng cột 260px (238px ở cửa sổ hẹp), inset panel 6px mỗi bên. Menu gốc và vị trí vùng bên phải giữ nguyên.
- Tiêu đề panel Inter 20px/700, mô tả 13px. Ba thẻ giữ chữ Inter của v2: tiêu đề 20px/700, mô tả 15px/400, CTA 14px/700; cao 190px, icon 48px, cách nhau 12px.
- Dưới 820px chiều cao cửa sổ, thẻ cao 160px, icon 32px đứng cạnh tiêu đề, khoảng cách 8px. Giữ cỡ và độ đậm chữ, ba thẻ và chân kết nối đều nằm trong panel, không cuộn cột trái.
- Theo bổ sung của người dùng, toàn bộ bảy tab dùng chung panel nổi này, cùng mép trên/dưới, bo góc và bóng. Nội dung riêng từng tab nằm bên trong panel.

Khung panel nằm tại `MainWindow.context_panel`; cột ngoài `context` vẫn giữ kích thước cố định khi đổi tab. Nội dung và hành vi của ba thẻ, thống kê, bài học và kéo thả tiếp tục dùng dữ liệu thật như v2.
