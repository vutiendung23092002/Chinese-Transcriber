# Bản bàn giao duyệt thiết kế

**DESIGN READY FOR REVIEW** · 14/11/2026 · Chưa phê duyệt · Chưa bắt đầu triển khai.

## Đề xuất

Chọn **A — Ngọc nghiên cứu, ưu tiên sáng** với **Logo 01 — Hai trang song ngữ**. Bố cục thanh bên và timeline theo hàng dùng chung cho cả hai theme. Giữ B — Đêm tập trung làm phương án so sánh trong vòng duyệt.

## Xem theo thứ tự

1. [Bảng định hướng màu và logo](../assets/mockups/00-brand-board.png).
2. [Tổng quan 7 màn hình × 2 hướng](../assets/mockups/00-screen-overview.png).
3. Mở [bản xem thiết kế](../assets/mockups/review.html), chọn màu và chế độ ở thanh phía trên; chuyển màn hình bằng sidebar.
4. Xem riêng thư viện và hộp thoại bản dịch cuối cùng để duyệt quan hệ âm thanh/phiên bản.

## Danh mục ảnh

| Màn hình | Hướng A sáng | Hướng B tối |
|---|---|---|
| Trang chủ | [PNG](../assets/mockups/a-light-01-dashboard.png) | [PNG](../assets/mockups/b-dark-01-dashboard.png) |
| Dịch file | [PNG](../assets/mockups/a-light-02-file.png) | [PNG](../assets/mockups/b-dark-02-file.png) |
| Ghi âm trực tiếp | [PNG](../assets/mockups/a-light-03-live.png) | [PNG](../assets/mockups/b-dark-03-live.png) |
| Thư viện | [PNG](../assets/mockups/a-light-04-library.png) | [PNG](../assets/mockups/b-dark-04-library.png) |
| Prompt & Thuật ngữ | [PNG](../assets/mockups/a-light-05-prompts.png) | [PNG](../assets/mockups/b-dark-05-prompts.png) |
| Cài đặt & Codex | [PNG](../assets/mockups/a-light-06-settings.png) | [PNG](../assets/mockups/b-dark-06-settings.png) |
| Thùng rác | [PNG](../assets/mockups/a-light-07-trash.png) | [PNG](../assets/mockups/b-dark-07-trash.png) |

Bổ sung: [A tối](../assets/mockups/a-dark-dashboard.png), [B sáng](../assets/mockups/b-light-dashboard.png), [xóa phiên bản](../assets/mockups/dialog-purge-version.png), [xóa nguồn](../assets/mockups/dialog-purge-audio.png), [bản cuối](../assets/mockups/dialog-last-version.png). Hai logo SVG gốc nằm trong `assets/logo-concepts/`.

Tổng: **21 PNG, 2 SVG, bản xem có điều hướng và 4 tài liệu thiết kế chính**, kèm README và bản bàn giao này.

## Điểm cần quyết định

| Quyết định | Đề xuất | Trạng thái |
|---|---|---|
| Màu thương hiệu | A · Xanh ngọc `#0F766E` | Chờ duyệt |
| Chế độ mặc định | Sáng, có chế độ tối tương ứng | Chờ duyệt |
| Logo | 01 · Hai trang song ngữ | Chờ duyệt |
| Cấu trúc ứng dụng | Sidebar 7 mục, trợ giúp Codex ở chân sidebar | Chờ duyệt |
| Timeline | ZH bên trái, VI bên phải, cùng hàng và mốc thời gian | Chờ duyệt |
| Lịch sử | Một nguồn audio, nhiều phiên bản; chi tiết ở phải | Chờ duyệt |
| Live | Ô tạm riêng, chỉ dịch câu đã chốt | Chờ duyệt |
| Xóa | Xóa mềm, giữ audio mặc định khi xóa bản cuối | Chờ duyệt |

Có thể trả lời ngắn: **“Duyệt A + Logo 01 + bố cục hiện tại”** hoặc nêu phần muốn sửa. Tài liệu này không ghi nhận sự chấp thuận thay người dùng.

## Kiểm tra bản thiết kế

Các ảnh được dựng từ cùng một bộ mockup, không phải ảnh chụp ứng dụng đã triển khai. Đã kiểm tra hiển thị tiếng Việt/Trung, đối chiếu hàng timeline và phạm vi ba hộp thoại xóa bằng mắt. Công cụ duyệt kiểm tra lỗi JavaScript, điều hướng, chọn model mẫu, lọc thư viện, đóng dialog bằng Escape và checkbox giữ audio mặc định.

Bố cục được kiểm tra tràn ngang ở 1600, 1366, 1024, 768 và 390 px. Kiểm tra các cặp token chữ trên nền cho bốn biến thể màu. Đây là kiểm tra bản xem, chưa kiểm chứng Windows native, ASR, dịch, lưu trữ, quota, xuất TXT hoặc xóa/khôi phục thật.

Các ảnh gốc không chứa đường dẫn tài khoản, token hay số liệu quota thật. Các tham khảo ảnh trong brief không được cung cấp. Bước tiếp theo hiện tại là **duyệt hoặc sửa thiết kế**.
