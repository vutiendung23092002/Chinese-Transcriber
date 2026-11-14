# Định hướng thương hiệu — Chinese Transcriber

Trạng thái: đề xuất giai đoạn 1, chưa phê duyệt. Ngày: 14/11/2026.

## Tính cách sản phẩm

Một công cụ học tập nghiêm túc, tĩnh và dễ đọc. Nội dung bài giảng là trọng tâm. Giao diện cần cho người học biết đang nghe gì, câu nào đã chốt, bản nào đã dịch và có thể tìm lại kết quả ở đâu.

Tên sản phẩm giữ nguyên **Chinese Transcriber**. Nhãn giao diện bằng tiếng Việt. Dòng mô tả đề xuất: **Nghe hiểu. Học sâu.** Không dùng chữ Hán làm biểu tượng trang trí: chúng xuất hiện trong nội dung thật hoặc nhãn ngôn ngữ.

## A — Ngọc nghiên cứu / Ưu tiên sáng / Đề xuất

Xanh ngọc trầm `#0F766E`, giấy ấm `#F4F5F2`, nền thẻ trắng `#FFFFFF`, chữ xanh than `#182C29`. Điểm nhấn phụ đồng ấm `#B57A34` chỉ dùng hạn chế, không tô màu mỗi thẻ thống kê.

Cảm giác một góc bàn học sáng, có trật tự. Phù hợp đọc dài, tra thuật ngữ, đối chiếu hai ngôn ngữ. Chế độ tối chuyển xanh ngọc sang `#72D5BF`, đặt trên nền `#141C1B`; không đảo màu cơ học.

Thanh bên nhẹ, vùng chọn phủ xanh nhạt, đường phân chia mảnh. Bo góc 7–12 px, ít bóng đổ. Hạn chế gradient, không dùng hiệu ứng phát sáng quanh nội dung.

## B — Đêm tập trung / Ưu tiên tối

Xanh mực `#141827`, nền thẻ `#1C2235`, tím dịu `#B6A2FF`, chữ trắng mềm `#F1F0FA`, chữ phụ `#B7BED3`. Điểm nhấn phụ cát ấm `#E5BD82` dùng ít.

Cảm giác không gian nghe và ghi chú yên tĩnh. Phù hợp học buổi tối, với các mức bề mặt rõ thay vì nền đen tuyệt đối. Chế độ sáng dùng nền `#F5F3FA`, tím đậm `#6B4BC3`, chữ `#29243C`.

Hai hướng giữ cùng bố cục và ngữ nghĩa trạng thái. Người duyệt có thể chọn màu và logo độc lập.

## Logo 01 — Hai trang song ngữ / Đề xuất

Tệp vector: [01-parallel-pages.svg](../assets/logo-concepts/01-parallel-pages.svg).

Cuốn sách mở gồm hai trang. Trang trái có hai nhịp âm, trang phải có ba dòng văn bản. Đường sống sách nối hai ngôn ngữ. Tạo liên tưởng học tập và chuyển âm thanh thành kiến thức, đồng thời gợi cách trình bày hai cột trong ứng dụng.

Khung vuông bo góc; một màu nền và một màu nét. Không phụ thuộc chi tiết chữ cái nhỏ, quốc kỳ hoặc chữ Hán khó đọc ở cỡ biểu tượng. Đây là logo đề xuất, chưa phải thương hiệu đã được kiểm tra trùng lặp.

## Logo 02 — Nhịp cầu ngôn ngữ

Tệp vector: [02-voice-bridge.svg](../assets/logo-concepts/02-voice-bridge.svg).

Bong bóng hội thoại chứa ba nhịp âm và hai dòng chữ. Mạnh về hội thoại và chế độ trực tiếp, ít nhấn mạnh việc học từ bài giảng hơn logo 01. Dùng tím dịu, có thể đổi sang hệ ngọc nếu chọn hướng A.

## Quy tắc sử dụng dự kiến

- Lưới gốc 128 × 128; khoảng trống an toàn ít nhất 12% chiều rộng biểu tượng.
- Bản xem có mẫu 16 px và 32 px để kiểm tra khả năng nhận diện. Khi làm icon Windows sau duyệt, cần tinh chỉnh quang học bản 16 px, ưu tiên giữ hình sách/bong bóng và giảm số nét nhỏ nếu cần.
- Icon cửa sổ: 16–24 px; sidebar: 38 px; icon ứng dụng: xuất nhiều cỡ trong giai đoạn đóng gói.
- Không đổi màu logo theo trạng thái ghi âm hoặc lỗi. Trạng thái dùng biểu tượng và nhãn riêng.
- Wordmark dùng Segoe UI Semibold. Hai từ có thể xuống dòng trong sidebar hẹp; không bóp ngang chữ.
- Phông tiếng Trung dự kiến Microsoft YaHei; fallback Noto Sans SC nếu cần. Kiểm tra lại trên Windows sạch trước đóng gói.

## Tài sản duyệt

Xem [bảng định hướng](../assets/mockups/00-brand-board.png) để đối chiếu hai bảng màu, bốn biến thể sáng/tối và hai logo. Bản xem tại `assets/mockups/review.html` cho đổi màu trực tiếp.

Đề xuất chốt: hướng A làm mặc định sáng, hỗ trợ tối cùng hệ ngọc, logo 01. Hướng B là phương án thay thế để người dùng chọn trong vòng duyệt này.
