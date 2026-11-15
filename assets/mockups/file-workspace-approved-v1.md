# Màn Dịch file — bản đã duyệt

Ảnh tham chiếu: [file-workspace-approved-v1.png](file-workspace-approved-v1.png).

- Giữ nguyên logo, rail capsule, notch của mục đang chọn, icon và chiều rộng hai cột bên trái trong ứng dụng gốc.
- Bỏ tiêu đề và mô tả đầu vùng làm việc ở tất cả tab, không chừa khoảng trống cho header cũ. Các thao tác xuất, nhập và kiểm tra kết nối nằm trong nội dung tương ứng.
- Tên file một dòng, rút gọn ở giữa, giữ phần cuối và định dạng file; tooltip chứa tên đầy đủ.
- Màn File có thẻ âm thanh giãn theo cửa sổ, tiến trình ba bước, chọn phiên bản, ghi chú thuật ngữ, bảng Trung–Việt và trạng thái chờ.
- Xuất TXT qua menu trong thẻ. Thanh phát nằm cuối thẻ, dạng sóng lấy từ file thật; tốc độ, tắt tiếng và vị trí phát giữ khi chuyển tab.
- Trạng thái nút và các bước lấy từ dữ liệu thật. Chưa có transcript hoàn tất thì chưa bật nút dịch; chưa dịch đủ thì chưa bật xuất Việt.

Triển khai bằng Qt/PySide6 tại `src/chinese_transcriber/file_page.py`, không nhúng ảnh mockup vào giao diện.

## Chữ và kích thước điều khiển

Đóng gói Inter cùng app, không dựa vào Segoe UI cài trên máy. Các giá trị dưới đây tính bằng pixel logic Qt (Windows DPI scale áp dụng riêng):

| Thành phần | Cỡ chữ | Độ đậm |
|---|---:|---:|
| Tiêu đề cột tác vụ | 24 | 700 |
| Chọn file âm thanh | 17 | 600 |
| Nhãn trường | 14 | 400 |
| Dropdown / nội dung trường | 15 | 400 |
| Tên file | 22 | 700 |
| Ba bước xử lý | 18 | 500 |
| Tiêu đề trạng thái chờ | 30 | 700 |
| Mô tả trạng thái chờ | 17 | 400 |

Nút chọn file cao 48px, dropdown 40px, nút Play tròn 52px với tam giác đặc. Ở cửa sổ thấp, giảm khoảng cách và chiều cao điều khiển để giữ đủ thao tác; giữ nguyên cỡ và độ đậm chữ. Cửa sổ hẹp dùng nút xuất dạng icon để dành chỗ cho tên file.
