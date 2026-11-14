# Hệ màu V2 — Pastel & Graphite

Giai đoạn 1 · Chờ duyệt · Thay thế đề xuất màu V1 theo ảnh tham khảo mới.

## Token chính

| Vai trò | Sáng | Tối |
|---|---|---|
| Nền workspace | #F6F5F7 | #24212E |
| Panel / cột thao tác | #FFFFFF | #302B3B |
| Bề mặt phụ | #F7F6F8 | #393343 |
| Thanh icon | #292636 | #211E2B |
| Icon chưa chọn | #C1BBCD | #C8BFD4 |
| Mục chọn sidebar | #F2BFCD | #EFC0CF |
| Icon trên mục chọn | #373044 | #373044 |
| Chữ chính | #292633 | #F5F0F6 |
| Chữ phụ | #696471 | #C3BACD |
| Nút chính | #302B40 | #EDD6E5 |
| Chữ nút chính | #FFFFFF | #302738 |
| Vùng chọn phụ | #F1EBF7 | #44364E |
| Viền phân nhóm | #E9E6ED | #4B4458 |
| Vòng focus | #8A638D | #E5B8D1 |

## Pastel hỗ trợ

| Nhóm màu | Nền sáng / chữ | Nền tối / chữ | Cách dùng |
|---|---|---|---|
| Hồng | #FBE2E9 / #694553 | #503443 / #F4CBD9 | Tác vụ file, nhãn VI, điểm nhấn |
| Lavender | #EEE5FB / #5C467B | #443650 / #DFCCF4 | Live, nhãn ZH, phiên bản được chọn |
| Vàng kem | #FFF0CB / #735A27 | #4C402C / #F1DDAE | Chuẩn bị thuật ngữ |
| Xanh sương | #DEF1F3 / #385E63 | #2E4549 / #C3E3E6 | Nhóm nội dung hỗ trợ |

Màu thẻ dùng để phân nhóm nhẹ. Khi màu có ý nghĩa phải kèm nhãn và icon. Không tô toàn bộ timeline bằng nhiều màu; cột Việt chỉ phủ hồng ở mức rất nhẹ để hỗ trợ đối chiếu.

## Trạng thái

| Trạng thái | Chữ / nền sáng | Chữ / nền tối |
|---|---|---|
| Đã dịch | #3E6455 / #EAF3EE | #C0DEC9 / #31453A |
| Đã chốt câu | #655281 / #EFE8FA | #DECEF3 / #44374F |
| Chờ / đang dịch | #7C6028 / #FFF2D5 | #EFDAAF / #4C402B |
| Ghi âm / lỗi / xóa | #A13E59 / #FBE7ED | #F5BECC / #513442 |
| Nội dung tạm | #696471 trên panel | #C3BACD trên panel |

Nội dung tạm có nhãn, chữ nghiêng và khung nét đứt. Câu đã chốt có mốc giờ và nhãn riêng. Đang dịch có vòng tiến trình. Không dùng màu như dấu hiệu duy nhất.

## Kiểm tra đọc và tương phản

Kiểm tra các cặp token chữ/nền cho hai chế độ, gồm chữ chính/phụ, nút, nhãn trạng thái, pastel và sidebar. Mục tiêu chữ thường ít nhất 4,5:1. Đây là kiểm tra token của mockup, chưa là chứng nhận accessibility cho ứng dụng.

Sidebar dùng nút có tên truy cập và nhãn khi focus/hover. Vòng focus không bị xóa. Cỡ chữ timeline mẫu desktop rộng: Trung 18 px, Việt 14 px, giãn dòng rộng. Các nhãn metadata nhỏ chỉ phục vụ thông tin phụ; khi triển khai cần tùy chọn tăng cỡ chữ và kiểm tra Windows scaling 125–200%.

Viền trang trí không được dùng làm dấu hiệu duy nhất cho control hoặc trạng thái. Cần kiểm tra thêm High Contrast, trình đọc màn hình, focus và trạng thái disabled trong PySide6 sau duyệt.

Ảnh: [Sáng](../assets/mockups/v2-light-01-dashboard.png), [Tối](../assets/mockups/v2-dark-01-dashboard.png), [Bảng màu](../assets/mockups/v2-00-brand-board.png).
