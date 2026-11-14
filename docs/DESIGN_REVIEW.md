# Bàn giao duyệt thiết kế V2

**Pastel Light đã được phê duyệt cho Phase 2 ngày 14/11/2026.** Tài liệu này giữ lại bộ bàn giao Phase 1; tiến độ ứng dụng thật tại [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md).

## Thay đổi theo phản hồi

V1 không được chọn. V2 thiết kế lại theo ảnh sidebar bạn gửi: thanh icon tối dạng capsule, mục chọn hồng nổi trên khoảng trắng, logo tròn ở đầu thanh, cột thao tác kế bên và workspace sáng bo góc lớn. Màu chủ đạo chuyển sang than tím/trắng ngà; thẻ hồng phấn, lavender, vàng kem và xanh sương.

Luồng học tập vẫn theo brief. File mode đưa nguồn, bối cảnh, model và effort vào cột thao tác để timeline rộng hơn. Home dùng các thẻ tác vụ và bài học gần đây. Library vẫn giữ một nguồn âm thanh với nhiều phiên bản.

## Xem bản mới

1. [Bản xem có điều hướng](../assets/mockups/review.html).
2. [Sidebar đã bỏ menu và sửa phần khoét](../assets/mockups/v2-sidebar-refined.png) và [cận cảnh trạng thái chọn](../assets/mockups/v2-sidebar-notch.png).
3. [Bảng màu và logo V2](../assets/mockups/v2-00-brand-board.png).
4. [Tổng quan 7 màn hình sáng/tối](../assets/mockups/v2-00-screen-overview.png).

## Ảnh từng màn hình

| Màn hình | Sáng | Tối |
|---|---|---|
| Trang chủ | [PNG](../assets/mockups/v2-light-01-dashboard.png) | [PNG](../assets/mockups/v2-dark-01-dashboard.png) |
| Dịch file | [PNG](../assets/mockups/v2-light-02-file.png) | [PNG](../assets/mockups/v2-dark-02-file.png) |
| Ghi âm trực tiếp | [PNG](../assets/mockups/v2-light-03-live.png) | [PNG](../assets/mockups/v2-dark-03-live.png) |
| Thư viện | [PNG](../assets/mockups/v2-light-04-library.png) | [PNG](../assets/mockups/v2-dark-04-library.png) |
| Prompt & Thuật ngữ | [PNG](../assets/mockups/v2-light-05-prompts.png) | [PNG](../assets/mockups/v2-dark-05-prompts.png) |
| Cài đặt & Codex | [PNG](../assets/mockups/v2-light-06-settings.png) | [PNG](../assets/mockups/v2-dark-06-settings.png) |
| Thùng rác | [PNG](../assets/mockups/v2-light-07-trash.png) | [PNG](../assets/mockups/v2-dark-07-trash.png) |

Hộp thoại: [Xóa bản dịch](../assets/mockups/v2-dialog-purge-version.png), [Xóa nguồn và bản liên quan](../assets/mockups/v2-dialog-purge-audio.png), [Bản dịch cuối](../assets/mockups/v2-dialog-last-version.png).

Tổng V2: 20 PNG chính, 2 ảnh cận cảnh sidebar và 2 ảnh kiểm tra bố cục ở cửa sổ 1920 × 912, 2 SVG logo mới, bản xem điều hướng và tài liệu cập nhật. Bản V1 được lưu tại assets/mockups/archive/v1.

Theo phản hồi mới nhất, cột trái giữ cùng chiều rộng khi đổi tab và không có thanh cuộn riêng ở giữa. Đã kiểm tra cả vị trí bắt đầu vùng làm việc và việc các nút trong cột trái vẫn nằm trọn trong khung.

## Nội dung đã duyệt cho Phase 2

- Kiểu sidebar capsule và trạng thái chọn hồng.
- Cấu trúc ba phần: icon / thao tác / nội dung.
- Bảng màu pastel và mức bo góc.
- Độ rõ của timeline và danh sách phiên bản.
- Logo Nhịp lời được dùng trong ứng dụng; Hai trang song ngữ giữ làm phương án tham khảo.

Người dùng đã xác nhận Phase 1 hoàn tất và cho phép triển khai native trong yêu cầu Phase 2.

## Kiểm tra bản xem

Kiểm tra hiển thị các màn hình, lỗi JavaScript, điều hướng sidebar, chọn model mẫu, tìm trong thư viện, theme, đóng dialog bằng Escape và checkbox giữ audio mặc định. Kiểm tra tràn ngang ở 1600, 1366, 1024, 768 và 390 px; kiểm tra cặp màu chữ/nền ở cả sáng và tối.

Các phép kiểm tra trong tài liệu này thuộc mockup Phase 1. Kết quả ứng dụng native, ASR, Codex, storage và đóng gói Phase 2 được ghi riêng tại [VALIDATION.md](VALIDATION.md).
