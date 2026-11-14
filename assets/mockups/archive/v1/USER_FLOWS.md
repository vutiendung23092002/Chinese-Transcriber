# Luồng trải nghiệm đề xuất

Giai đoạn 1 · Chờ phê duyệt · Không có nghiệp vụ đang chạy trong bản xem.

## 1. Từ file mới đến hai TXT

1. Trang chủ → **Tải file ghi âm** hoặc sidebar → **Dịch file ghi âm**.
2. Chọn file/kéo thả. Kiểm tra đọc được nguồn và dung lượng trước khi bắt đầu.
3. Nếu mới: báo đang nhập rồi lưu một bản trong thư viện do app quản lý. Giữ file ngoài của người dùng nguyên vị trí. Nếu cùng nội dung đã có: “Âm thanh này đã có trong thư viện. Dùng file đã lưu để tạo bản dịch mới?”
4. Nhập bối cảnh, chọn bộ thuật ngữ, model và effort. Model/effort không khả dụng phải được giải thích trước khi chạy.
5. Chọn **Chép lời tiếng Trung**. Hiện tiến trình có chữ, cho hủy. Khi không có phần trăm đáng tin cậy, dùng trạng thái đang xử lý và thời gian đã chạy, không bịa tỷ lệ.
6. Xem timeline tiếng Trung, kiểm tra các câu cần xem lại. Chỉ bật **Tạo bản dịch mới** khi có transcript sử dụng được và công cụ dịch sẵn sàng.
7. Dịch theo segment, mỗi bản Việt về đúng hàng thời gian. Nếu lỗi một đoạn, giữ các đoạn thành công và nút thử lại.
8. Lưu phiên bản với bối cảnh, thuật ngữ, model/effort và tham chiếu bản chép lời đã dùng.
9. **Trung TXT** xuất chép lời tiếng Trung; **Việt TXT** xuất bản dịch. Tên đề xuất: `lecture03_v2_zh.txt` và `lecture03_v2_vi.txt`, UTF-8. Có tùy chọn kèm mốc thời gian; mặc định cần duyệt khi triển khai.

Điểm kết thúc: một nguồn âm thanh trong thư viện, một bản transcript có các segment và một phiên bản dịch. Chỉ báo thành công sau khi kết quả được lưu. TXT xuất là bản sao phục vụ sử dụng bên ngoài, không phải thêm âm thanh vào thư viện.

## 2. Dịch lại cùng âm thanh

1. Thư viện → chọn `lecture03.m4a` → xem v1, v2.
2. **Tạo bản dịch từ file gốc** mở File mode với đúng nguồn đã lưu.
3. Mặc định đề xuất dùng lại transcript hiện tại; cho chọn chép lời lại nếu cần, có giải thích bản dịch cũ không bị đổi.
4. Đổi bối cảnh / glossary / model / effort → tạo phiên bản mới.
5. Thư viện vẫn có một hàng nguồn; số phiên bản tăng. Hiển thị rõ cấu hình từng bản và bản mới nhất.

Nếu glossary được sửa sau khi v2 tạo xong, v2 vẫn hiển thị đúng nội dung glossary đã dùng lúc tạo. Không sửa lịch sử âm thầm.

## 3. Từ microphone đến phiên đã lưu

1. Ghi âm trực tiếp → chọn microphone → xem mức tín hiệu, bối cảnh, glossary và cấu hình dịch trước khi bắt đầu. Trong màn hình đang thu, cấu hình được tóm tắt; thay đổi lớn áp dụng cho phiên mới.
2. **Bắt đầu**: kiểm tra quyền và thiết bị. Chỉ hiện “Đang ghi âm” và chạy timer khi thu thành công. Nút Bắt đầu vô hiệu hóa trong khi thu; thay bằng “Tiếp tục” khi đã tạm dừng.
3. Câu chưa chốt cập nhật trong ô tạm, có thể thay chữ. Chưa gửi câu này đi dịch.
4. Khi chốt câu: tạo hàng ZH với ID và khoảng thời gian, đưa vào hàng đợi dịch. Phần tạm bắt đầu câu mới.
5. Khi dịch xong: đặt bản VI vào cùng hàng. Không đảo hàng vì phản hồi mô hình đến khác thứ tự.
6. **Tạm dừng** dừng thu thêm; các câu đã chốt vẫn được dịch. Giữ mốc thời gian theo nguồn audio; cần kiểm tra chính sách khoảng dừng với dữ liệu thu thực tế.
7. **Dừng**: chốt phần cuối nếu có nội dung. Hiển thị số câu đang dịch/chờ, tên phiên và lựa chọn lưu. Không bắt chờ hàng đợi mới được giữ âm thanh.
8. Lưu phiên → thư viện. Chỉ lưu một âm thanh của phiên; các lần dịch sau dùng lại nguồn đó. Cho xuất TXT khi phần tương ứng đã có, nêu rõ nếu bản dịch chưa đầy đủ.

Khi Codex lỗi hoặc hết hạn mức: tiếp tục giữ âm thanh và transcript nếu ghi âm vẫn hoạt động; hiện trạng thái lỗi/chờ tại các hàng. Cho dừng thu, lưu và tiếp tục dịch sau. Không tự xóa hoặc bỏ qua đoạn.

## 4. Chốt câu tiếng Trung — quy tắc trải nghiệm

Mục tiêu: đủ nhanh để theo bài giảng, nhưng bản dịch xuất hiện ở đơn vị dễ hiểu. Đây là giả thuyết thiết kế cần benchmark, không phải thông số engine đã kiểm chứng.

1. Dùng phát hiện giọng nói/khoảng lặng để đề xuất endpoint; xử lý câu Trung với dấu `。？！` và tín hiệu ngữ điệu nếu engine có.
2. Một khoảng lặng ngắn giữa mệnh đề không tự tạo câu mới. Kết hợp độ ổn định của transcript, dấu câu và độ dài đoạn.
3. Có thể thử ngưỡng lặng khoảng 0,7–1,2 giây cho lời giảng trong giai đoạn benchmark; không cố định trước khi đo. Khi không có dấu câu, ưu tiên ngắt ở ranh giới mệnh đề và giới hạn độ dài hợp lý. Phần chưa ổn định vẫn ở ô tạm.
4. Đề xuất điểm bảo vệ khoảng 15–25 giây cho lời nói không nghỉ, chọn ranh giới ngôn ngữ tốt nhất; không cắt giữa từ/thuật ngữ chỉ để đạt timer. Giá trị thực tế sẽ theo phần cứng và bộ ASR.
5. Mốc segment lấy từ thời gian audio, không lấy thời điểm bản dịch trả về. Xử lý chồng lấn cửa sổ ASR để tránh lặp từ/câu trong giao diện.
6. Sau khi chốt, câu không bị ASR thay đổi âm thầm. Nếu người học sửa/ngắt/gộp khi xem lại, đánh dấu các bản dịch liên quan cần cập nhật và tạo lịch sử phù hợp.
7. Dịch có thể dùng ngữ cảnh các câu trước, nhưng kết quả gắn về segment hiện tại; không tự gộp hai hàng thành một đoạn mất đối chiếu.

Nội dung có thể cần nhiều giây sau khi người nói dừng mới hiện bản dịch. UI gọi đó là “theo câu đã chốt”, không hứa dịch tức thời từng từ. Không hứa độ chính xác, độ trễ hoặc model STT cụ thể trong giai đoạn 1.

## 5. Đọc lại và thuật ngữ

Thư viện → chọn nguồn → chọn phiên bản → mở tại vị trí đọc gần nhất. Bấm mốc giờ/nghe đoạn để phát lại phần audio tương ứng, tô cả hai ô của cùng hàng. Tìm trong bản dịch cho kết quả theo segment, không cuộn hai cột lệch nhau.

Mở ghi chú thuật ngữ khi cần. Trạng thái “Cần xem lại” cho các đoạn không chắc chắn là bổ sung dự kiến. Chế độ đọc dài cần điều chỉnh cỡ chữ và điều hướng bàn phím, không đưa ghi chú mở sẵn vào mọi hàng.

So sánh phiên bản: mặc định cùng transcript, đặt v1/v2 theo cùng segment và làm nổi thay đổi thuật ngữ. Nếu transcript khác, phải thông báo không thể ghép chính xác từng hàng trước khi cung cấp so sánh theo khoảng thời gian.

## 6. Đăng nhập và chọn mô hình

1. Chân sidebar → Cài đặt & Codex.
2. **Kiểm tra Codex CLI**: xác định công cụ/path và trạng thái đăng nhập. “Không tìm thấy công cụ” khác với “Chưa đăng nhập”; không báo một lỗi chung.
3. Chưa có công cụ → hướng dẫn cài chính thức và chọn đường dẫn. Có công cụ → hướng dẫn `codex login`; người dùng hoàn tất đăng nhập trong giao diện chính thức.
4. Kiểm tra lại rồi khám phá model/effort được hỗ trợ. Danh sách đề xuất theo brief không chứng minh quyền truy cập.
5. Chọn model + effort, lưu mặc định cho lượt dịch mới. Bản dịch cũ giữ cấu hình cũ.
6. Đọc hạn mức nếu kết nối hỗ trợ; nếu không, dấu “—”, lý do ngắn và hướng dẫn tự kiểm tra. Không coi thiếu dữ liệu là 0% hoặc hết hạn mức.

Các lệnh chỉ là văn bản trong bản xem; không kích hoạt đăng nhập trong giai đoạn này. Căn cứ tài liệu và giới hạn xác minh ở UI_CONCEPT.md.

## 7. Xóa, khôi phục và nguồn dùng chung

| Thao tác | Xác nhận | Kết quả thiết kế |
|---|---|---|
| Xóa v1, vẫn có v2 | Nêu tên v1 và các mục được giữ | Chỉ v1 vào thùng rác; audio và v2 còn |
| Xóa bản dịch cuối | Checkbox “Chuyển cả âm thanh gốc…” mặc định bỏ chọn | Chỉ bản cuối vào thùng rác nếu không chọn thêm |
| Xóa nguồn âm thanh | Liệt kê nguồn và toàn bộ bản liên quan, số lượng | Đưa cả nhóm vào thùng rác, giữ quan hệ để khôi phục |
| Khôi phục bản lẻ, nguồn còn | Báo bản đã về thư viện | Nối lại đúng nguồn, không sao chép audio |
| Khôi phục bản lẻ, nguồn ở thùng rác | Cho khôi phục cả nguồn liên quan | Không tạo một bản dịch không còn nguồn hợp lệ |
| Khôi phục nhóm nguồn | Tóm tắt nguồn và các bản được khôi phục | Giữ thông tin phiên bản và mốc thời gian |
| Xóa vĩnh viễn một phiên bản | Cảnh báo không thể hoàn tác, nêu rõ audio còn | Không xóa nguồn đang được bản khác dùng |
| Xóa vĩnh viễn nguồn/nhóm | Liệt kê mọi mục liên quan, số lượng, hậu quả | Chỉ xóa sau xác nhận đầy đủ; không để phiên bản còn trỏ tới nguồn đã mất |

Nếu nguồn có bản dịch đang hoạt động, không cho một thao tác xóa vĩnh viễn âm thầm bỏ nguồn. Người dùng phải quyết định phạm vi cả nhóm hoặc hủy. Phần mềm cần kiểm tra lại các quan hệ tại thời điểm xác nhận trong giai đoạn triển khai.

Ba ảnh hộp thoại: [xóa một phiên bản](../assets/mockups/dialog-purge-version.png), [xóa nguồn và bản liên quan](../assets/mockups/dialog-purge-audio.png), [bản dịch cuối cùng](../assets/mockups/dialog-last-version.png).

## 8. Điều kiện chuyển giai đoạn

Chỉ khi người dùng phê duyệt thiết kế mới triển khai. Phê duyệt màu/logo không tự thay thế việc xác minh kỹ thuật ASR, các lệnh Codex và quota. Các kiểm tra kỹ thuật đó diễn ra trong giai đoạn sau, và các khác biệt làm thay đổi trải nghiệm phải được trình bày rõ.
