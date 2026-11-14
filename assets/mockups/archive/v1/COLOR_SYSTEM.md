# Hệ màu đề xuất

Trạng thái: giai đoạn 1, chờ duyệt. Token được dùng trong bản xem thiết kế; chưa được đưa vào ứng dụng PySide6.

## Hướng A — Ngọc nghiên cứu

| Vai trò | Sáng (mặc định đề xuất) | Tối |
|---|---|---|
| Nền workspace | `#F4F5F2` | `#141C1B` |
| Bề mặt panel | `#FFFFFF` | `#1B2825` |
| Thanh bên | `#EDF0EB` | `#17211F` |
| Bề mặt phụ | `#F8FAF7` | `#1F2F2B` |
| Chữ chính | `#182C29` | `#ECF4F0` |
| Chữ phụ | `#52645F` | `#AFBFB8` |
| Màu hành động chính | `#0F766E` | `#72D5BF` |
| Chữ trên nút chính | `#FFFFFF` | `#102A23` |
| Nền vùng chọn | `#E1F2ED` | `#263E36` |
| Viền phân nhóm | `#D7DFD9` | `#3B5149` |
| Điểm nhấn hỗ trợ | `#B57A34` | `#DFB379` |
| Vòng focus | `#356BDB` | `#A6C6FF` |

Xanh ngọc dùng cho hành động chính, chọn trang, nhãn ngôn ngữ và liên kết. Chừa phần lớn diện tích cho màu nền và văn bản. Không dùng màu đồng cho chữ nhỏ trên nền sáng nếu chưa kiểm tra tương phản.

## Hướng B — Đêm tập trung

| Vai trò | Tối (mặc định hướng B) | Sáng |
|---|---|---|
| Nền workspace | `#141827` | `#F5F3FA` |
| Bề mặt panel | `#1C2235` | `#FFFFFF` |
| Thanh bên | `#181D2E` | `#EFEBF6` |
| Bề mặt phụ | `#222A40` | `#FAF8FD` |
| Chữ chính | `#F1F0FA` | `#29243C` |
| Chữ phụ | `#B7BED3` | `#625A76` |
| Màu hành động chính | `#B6A2FF` | `#6B4BC3` |
| Chữ trên nút chính | `#211A3A` | `#FFFFFF` |
| Nền vùng chọn | `#302B49` | `#EEE7FC` |
| Viền phân nhóm | `#3C4662` | `#DDD6EB` |
| Điểm nhấn hỗ trợ | `#E5BD82` | `#956526` |
| Vòng focus | `#C5B9FF` | `#6B4BC3` |

## Trạng thái ngữ nghĩa — giữ nguyên giữa các hướng

| Trạng thái | Chữ sáng / nền sáng | Chữ tối / nền tối | Dấu hiệu bổ sung |
|---|---|---|---|
| Hoàn tất, đã dịch | `#16634B` / `#E5F3E9` | `#88D6AB` / `#243E31` | Nhãn “Đã dịch”, chấm trạng thái |
| Đã chốt câu | `#355EA8` / `#EAF0FC` | `#A9C6FF` / `#263652` | Nhãn “Đã chốt câu” |
| Đang dịch / chờ | `#855510` / `#FFF2D8` | `#EAC885` / `#3D3220` | Vòng tiến trình hoặc nhãn “Trong hàng đợi” |
| Ghi âm / lỗi / xóa | `#AD3744` / `#FBECEE` | `#FFADB8` / `#432A30` | Biểu tượng và động từ rõ ràng |
| Tạm thời | `#65736E` trên panel | Chữ phụ của hướng trên panel | Khung nét đứt, chữ nghiêng, nhãn “Câu chưa chốt” |

Không phân biệt tiếng Trung và tiếng Việt chỉ bằng màu. Dùng cột cố định, nhãn ZH/VI, ngôn ngữ viết đầy đủ và mốc thời gian chung. Không dùng đỏ để biểu thị bản dịch chỉ đang chờ.

## Tương phản và độ dễ đọc

Mục tiêu thiết kế: chữ thường đạt tỷ lệ tương phản ít nhất 4,5:1 với nền sử dụng; trạng thái phải có nhãn, không chỉ có màu. Công cụ xuất thiết kế kiểm tra các cặp chữ chính/panel, chữ phụ/panel, chữ phụ/workspace, chữ phụ/vùng chọn, primary/vùng chọn, primary/panel, chữ nút/nút chính, bốn trạng thái/nền tương ứng và chữ tạm thời/panel cho bốn biến thể.

Đây là kiểm tra token, không phải chứng nhận accessibility toàn ứng dụng. Viền phân nhóm là trang trí, không dùng riêng nó để biểu thị trạng thái. Khi triển khai cần kiểm tra thêm ranh giới control, focus, disabled, High Contrast, trình đọc màn hình và tỷ lệ Windows 125–200%.

Chữ tiếng Việt chính trong timeline 13 px, giãn dòng 1,85; tiếng Trung 17 px, giãn dòng 1,8 trong mẫu desktop rộng. Đây là mật độ mẫu, cần cho người học tăng cỡ chữ 100/125/150% khi triển khai; không giảm cỡ chỉ để nhét nội dung. Metadata mẫu 10–12 px chỉ dành cho mốc giờ, trạng thái và thông tin phụ. Kích thước cuối cần duyệt trên máy Windows thực.

## Quy tắc thành phần

- Một hành động chính cho mỗi cụm thao tác. Tránh nhiều nút màu đặc cạnh nhau.
- Chọn dòng: nền tint, nhãn chọn và viền/điểm đánh dấu đi cùng; không dựa vào độ sáng nhỏ.
- Đường chia hai ngôn ngữ phải liên tục; chiều cao hàng theo ô dài nhất.
- Focus: vòng 3 px lệch ra ngoài 4 px trong bản xem, không xóa focus mặc định của bàn phím.
- Shadow chỉ dùng nhẹ ở logo minh họa, thông báo và hộp thoại. Không làm nổi mọi hàng timeline.
- Chuyển theme đổi token ngữ nghĩa, không giữ chữ trắng cố định trên nút sáng.

Ảnh màu thực tế: [bảng màu](../assets/mockups/00-brand-board.png), [A sáng](../assets/mockups/a-light-01-dashboard.png), [A tối](../assets/mockups/a-dark-dashboard.png), [B tối](../assets/mockups/b-dark-01-dashboard.png), [B sáng](../assets/mockups/b-light-dashboard.png).
