# UX/UI concept — Chinese Transcriber

**DESIGN READY FOR REVIEW.** Chỉ giai đoạn 1. Tất cả hành vi dưới đây là thiết kế đề xuất; bản xem không triển khai tính năng sản phẩm.

## 1. Bài toán và ưu tiên

Người học cần nghe bài giảng tiếng Trung, hiểu bản dịch tiếng Việt, kiểm tra thuật ngữ và xem lại sau buổi học. Hai lối vào là file có sẵn và microphone. Cả hai cùng kết thúc ở một không gian đọc song ngữ và một thư viện có lịch sử phiên bản.

Ưu tiên theo thứ tự:

1. Ghép đúng câu Trung–Việt với cùng mốc thời gian.
2. Giữ câu hoàn chỉnh, phân biệt nội dung tạm với nội dung đã chốt.
3. Dịch có bối cảnh và thuật ngữ học thuật.
4. Tìm lại âm thanh và các phiên bản, không nhân bản âm thanh gốc.
5. Hiểu trạng thái công cụ, hàng đợi, lỗi và các thao tác xóa.

Định hướng đề xuất: **A — Ngọc nghiên cứu + Logo 01**. Phương án B — Đêm tập trung có cùng cấu trúc để đánh giá màu mà không thay đổi luồng.

Hai ảnh tham khảo trong brief không có đường dẫn hoặc tệp đính kèm. Thiết kế dựa trên mô tả sidebar và dashboard; không khẳng định đã xem ảnh tham khảo.

## 2. Kiến trúc thông tin

| Vị trí thanh bên | Mục đích | Điểm đến chính |
|---|---|---|
| Trang chủ | Tiếp tục học, tóm tắt thư viện | Nhập file / ghi âm / phiên gần đây |
| Dịch file ghi âm | Chuẩn bị nguồn, bối cảnh và lượt dịch | Timeline và hai TXT |
| Ghi âm trực tiếp | Thu tiếng, theo dõi câu đã chốt và bản dịch | Lưu phiên và xem lại |
| Thư viện | Tìm nguồn âm thanh, xem các phiên bản | Mở, xuất, so sánh, dịch lại |
| Prompt & Thuật ngữ | Soạn bối cảnh, quản lý bộ thuật ngữ | Áp dụng cho lượt dịch mới |
| Cài đặt & Codex | Mô hình, mức suy luận, đăng nhập và giao diện | Hướng dẫn, trạng thái kết nối |
| Thùng rác | Xem mục đã xóa mềm và phạm vi liên quan | Khôi phục hoặc xóa vĩnh viễn |
| Chân sidebar: Kết nối Codex CLI | Lối vào trợ giúp luôn sẵn có | Cài đặt & hướng dẫn đăng nhập |

Gộp mô hình vào Cài đặt & Codex để không tạo thêm một trang cấu hình gần trùng nhau. Model và effort vẫn xuất hiện ngay tại File/Live, thuộc lượt dịch hiện tại. Trợ giúp Codex được nhúng vào Cài đặt và có lối vào cố định ở chân sidebar.

## 3. Bố cục và thành phần dùng chung

Khung desktop có titlebar Windows, sidebar 226 px, header nội dung và workspace. Ảnh chính xuất ở 1600 × 1000 px; đây là kích thước khung duyệt, không phải ràng buộc độ phân giải sản phẩm. Khoảng cách theo bội 4/8 px, panel 12 px, control 6–8 px. Icon nét đơn 16–20 px, cùng trọng lượng thị giác.

Hai kiểu workspace:

- **Làm việc:** thiết lập bên trái, timeline chiếm phần lớn diện tích bên phải. Với Live, thanh ghi âm nằm trên và bảng giải thích trạng thái ở phải.
- **Quản lý:** danh sách nguồn bên trái, chi tiết phiên bản bên phải. Có thể thu panel phụ khi cửa sổ nhỏ.

Nội dung chính cuộn dọc khi thiếu chiều cao. Sidebar và tác vụ trong header vẫn dễ tìm. Không ép hai ngôn ngữ cuộn độc lập. Các giao diện hẹp trong bản xem dùng để phát hiện tràn nội dung; không đề xuất một ứng dụng mobile.

Khi triển khai desktop: cửa sổ tham chiếu từ 1280 × 800 logical px; màn hình nhỏ/Windows scaling cần thu panel tùy chọn hoặc dùng drawer, giữ transcript dễ đọc. Kiểm tra thực tế 1366 × 768, 1920 × 1080 với scaling 100/125/150/200% trước chốt kích thước tối thiểu.

## 4. Trang chủ

Bốn chỉ số đúng nhu cầu: số âm thanh, số bản dịch, lần dịch gần nhất và model mặc định. Không coi một phiên bản là một file âm thanh mới. Bốn lối vào: tải file, ghi âm, mở thư viện và đăng nhập Codex. Khu “Tiếp tục học” mở đúng nguồn, phiên bản và vị trí xem gần nhất theo thiết kế tương lai.

Trạng thái đầu tiên: chỉ số bằng 0, ẩn danh sách gần đây và đặt lời mời “Thêm bài giảng đầu tiên”. Model chưa cấu hình hiển thị “Chưa chọn”, không tự nhận tài khoản có quyền dùng model.

## 5. Dịch file ghi âm

Panel trái chứa: kéo thả/chọn file mới, chọn nguồn đã lưu, bối cảnh bài giảng, bộ thuật ngữ và lối chỉnh sửa, model, effort, nút “Chép lời tiếng Trung” và “Tạo bản dịch mới”. Dùng từ “Chép lời” thay cho “Dịch” ở bước ASR để phân biệt hai tác vụ.

Panel phải hiển thị tên nguồn, thời lượng, phiên bản, tiến trình ba bước, transcript và bản dịch đối chiếu. Hai nút xuất độc lập “Trung TXT”, “Việt TXT” ở header. Tên đầy đủ và cách ghép cặp được giải thích trong hộp thoại xuất. Nút tạo bản dịch luôn tạo phiên bản mới, không ghi đè kết quả trước.

Trước khi có transcript: vùng phải hiển thị placeholder “Chọn âm thanh để bắt đầu”, tắt dịch/xuất. Có transcript nhưng chưa dịch: cột Việt là placeholder. Có kết quả: mỗi hàng liên kết ZH/VI theo segment; thuật ngữ thu gọn dưới bản dịch. Nút chép lời lại phải giải thích đây là bản transcript mới; các bản dịch cũ giữ nguyên nguồn transcript cũ.

Import sẽ sao chép vào thư viện do ứng dụng quản lý trong giai đoạn triển khai. Nếu trùng nội dung âm thanh: hiển thị “File đã có trong thư viện” và đề xuất dùng nguồn cũ. Không chỉ kiểm tra tên file. Không có thao tác “di chuyển file gốc” của người dùng.

## 6. Ghi âm trực tiếp

Thanh điều khiển lớn gồm bắt đầu, tạm dừng/tiếp tục, dừng; timer, microphone đang chọn, mức tín hiệu và trạng thái có chữ. Ở trạng thái đang thu, nút Bắt đầu phải vô hiệu hóa; chỉ có một phiên thu hoạt động.

Timeline phân biệt rõ bốn giai đoạn:

| Giai đoạn | Vị trí / dấu hiệu | Hành vi đề xuất |
|---|---|---|
| Tạm thời | Ô “Đang nghe · Câu chưa chốt”, viền nét đứt, chữ nghiêng | Được cập nhật, chưa gửi dịch |
| Đã chốt câu | Hàng có segment và khoảng thời gian, nhãn xanh lam | Không tự thay chữ đã chốt |
| Đang dịch / chờ | Cột Việt có nhãn/vòng tiến trình, giữ hàng | Không đưa kết quả sang sai câu |
| Đã dịch | Văn bản Việt và nhãn hoàn tất | Có thể phát lại và mở ghi chú |

Chỉ chuyển câu đã chốt vào timeline; bản dịch có thể đến sau. Kết quả luôn về đúng hàng, kể cả khi hoàn thành khác thứ tự. Không nhảy vị trí đọc nếu người dùng cuộn lên; khi đó hiện “Có đoạn mới” để quay về. Bật “Theo đoạn mới nhất” chỉ khi người dùng muốn.

Dừng ghi âm chốt đoạn cuối và mở lưu phiên. Có thể lưu âm thanh trong khi bản dịch còn chờ; thư viện phải thể hiện “Chưa dịch xong” và cho tiếp tục sau. Nếu rời trang đang thu, hiển thị trạng thái thu cố định và xác nhận trước khi kết thúc/đóng ứng dụng.

Chiến lược chốt câu chi tiết trong USER_FLOWS.md. Chưa đưa ra cam kết độ trễ hoặc chọn model ASR trước benchmark sau duyệt.

## 7. Thư viện và phiên bản

Mỗi hàng là **một nguồn âm thanh**: tên bài, tên file, thời lượng, ngày nhập, nguồn tải lên/ghi trực tiếp và số bản dịch. Nguồn chưa có bản dịch vẫn có thể ở thư viện.

Chọn nguồn mở các phiên bản gắn với nguồn đó. Chi tiết mỗi phiên bản có model, effort, thời gian tạo, bối cảnh, bộ thuật ngữ và trạng thái. Tóm tắt nguồn nói rõ “1 file gốc”; không hiển thị hai bản dịch như hai bản sao âm thanh.

Ví dụ trong mockup: `lecture03.m4a` có v1 không thuật ngữ và v2 có bộ Thống kê cơ bản. Cả hai dùng một âm thanh. Bản xem so sánh minh họa khác biệt thuật ngữ ở cùng đoạn; so sánh thực tế cần xử lý khác biệt segmentation nếu hai lần ASR khác nhau.

Hành động: mở lại, xuất Trung, xuất Việt, tạo bản dịch mới, so sánh, chuyển một phiên bản vào thùng rác; hành động xóa nguồn nằm trong menu nguồn và phải nêu toàn bộ phiên bản liên quan. Không dùng biểu tượng thùng rác không nhãn khi phạm vi có thể bị hiểu nhầm.

## 8. Prompt & Thuật ngữ

Cột trái là bộ đã lưu và nút tạo bộ. Khu chính có ô bối cảnh lớn và bảng gồm tiếng Trung, bản dịch Việt ưu tiên, ghi chú. Áp dụng bộ không thay đổi các phiên bản cũ. Lượt dịch lưu bản chụp nội dung bối cảnh/thuật ngữ đã dùng, không chỉ tên bộ có thể sửa sau này.

Ghi chú dưới timeline mặc định thu gọn. Nếu thuật ngữ mơ hồ, thiết kế đề xuất đánh dấu “Cần xem lại”, tránh khẳng định nghĩa khi chưa đủ ngữ cảnh. Cần thử nghiệm chất lượng sau duyệt; UI không bảo đảm dịch luôn đúng.

## 9. Cài đặt, Codex và giới hạn xác minh

Mẫu dùng trạng thái **Chưa kiểm tra / Chưa xác định** cho cài đặt và đăng nhập. Hiển thị đường dẫn công cụ, chọn file, kiểm tra công cụ, đăng nhập, hướng dẫn và sao chép lệnh. Không chèn đường dẫn cài đặt giả vào trạng thái thành công.

Hướng dẫn `codex login` rồi `codex login status` dựa trên [tài liệu lệnh Codex](https://learn.chatgpt.com/docs/developer-commands?surface=cli). Đây là hướng dẫn, không phải kết quả kiểm tra máy. Môi trường công cụ của lượt thiết kế không tìm thấy `codex` trên PATH; điều này không chứng minh máy không cài Codex ở vị trí khác.

Mockup hiển thị đủ tám tên theo brief: GPT-6.1 Sol, GPT-6 Astra, GPT-6.1 Terra, GPT-6 Sol, GPT-6 Luna, GPT-5.6 Sol, GPT-5.6 Terra, GPT-5.6 Luna. Tất cả ghi “Chưa xác minh”. Không suy ra model ID hoặc quyền tài khoản từ tên hiển thị.

[Codex App Server](https://learn.chatgpt.com/docs/app-server) có `model/list` kèm các mức effort, và `account/rateLimits/read` cho hạn mức. Đây là cơ sở cho thiết kế khám phá khả năng, chưa phải tích hợp đã thử. Khi triển khai sẽ ưu tiên dữ liệu trả về; các tên trong brief không khả dụng vẫn có thể nằm trong nhóm “Đề xuất / Chưa khả dụng”, không cho gửi lượt dịch lỗi.

[Configuration Reference](https://learn.chatgpt.com/docs/config-file/config-reference) mô tả `model_reasoning_effort`, tùy model/client. Mẫu low/medium/high chỉ để duyệt cấu trúc control. Giai đoạn sau cần kiểm tra phiên bản CLI, cách truyền model/effort chính thức và các giá trị thực tế trước khi nối lệnh.

Hạn mức đang là dấu “—”, không vẽ thanh phần trăm giả. Cửa sổ 5 giờ/1 tuần trong mẫu là trạng thái dự kiến theo brief, không là tuyên bố về mọi gói tài khoản. Sau kết nối: chỉ hiển thị đúng thời lượng cửa sổ, mức dùng, thời điểm reset và thời điểm cập nhật trả về. Không có dữ liệu: “Chưa thể tự động đọc hạn mức trong kết nối hiện tại”; có thể mở hướng dẫn tự kiểm tra. Không khẳng định không có API chính thức.

Tất cả nguồn web được đối chiếu ngày 14/11/2026; cần xác minh lại khi triển khai. Không gọi model, chạy ASR hoặc đăng nhập trong giai đoạn thiết kế.

## 10. Thùng rác và cảnh báo

Thùng rác có loại mục, tên, ngày xóa, quan hệ âm thanh/bản dịch và hai hành động có nhãn. Không tự dọn theo thời gian trong đề xuất đầu tiên.

- Xóa một bản dịch: âm thanh gốc và các bản khác vẫn còn.
- Xóa bản cuối: mặc định giữ âm thanh, checkbox chuyển cả âm thanh bỏ chọn.
- Xóa âm thanh: xác nhận liệt kê số phiên bản và tên các mục bị ảnh hưởng.
- Xóa vĩnh viễn: nói rõ không thể hoàn tác; không dùng từ “Dọn dẹp” cho thao tác này.
- Khôi phục nguồn có các bản đi kèm: khôi phục nhóm liên quan. Khôi phục bản lẻ nhưng nguồn đang ở thùng rác: giải thích và cho khôi phục cả nguồn.

## 11. Trạng thái cần giữ khi triển khai

| Tình huống | Phản hồi UI / hướng giải quyết |
|---|---|
| File chưa có, thư viện rỗng | Lời mời nhập file hoặc ghi âm đầu tiên |
| File không đọc được / định dạng chưa hỗ trợ | Giải thích lỗi tại nguồn; cho chọn lại, không tạo phiên hoàn tất giả |
| Thiếu bộ chép lời / FFmpeg | Hướng dẫn cài đặt tại chỗ trước tác vụ liên quan |
| Microphone bị từ chối / không có thiết bị | Dừng timer, báo “Chưa ghi âm”, cho chọn thiết bị/kiểm tra quyền |
| Hàng đợi dịch tăng | Vẫn thu âm, hiện số đoạn chờ, cho dịch tiếp sau |
| Codex chưa đăng nhập / mất kết nối | Giữ transcript và âm thanh; cho kết nối lại và thử lại đoạn lỗi |
| Chạm hạn mức | Giữ hàng chờ, hiển thị dữ liệu reset nếu có; không tự đổi model |
| Một đoạn dịch lỗi | Nhãn “Dịch chưa thành công”, nút thử lại tại hàng; không xóa các đoạn khác |
| Ít dung lượng / lưu thất bại | Hiện lỗi rõ ràng; không báo “Đã lưu”; cho chọn nơi lưu hoặc thử lại |
| Sửa prompt chưa lưu | Cảnh báo khi rời trang; lưu hoặc bỏ thay đổi |
| Nguồn trong thùng rác | Chỉ cho khôi phục hoặc xử lý phạm vi liên quan trước khi tạo bản dịch mới |
| Đóng ứng dụng khi đang xử lý | Tóm tắt phần đã lưu/chưa lưu; xác nhận kết thúc tác vụ |

## 12. Phạm vi phê duyệt

Duyệt cấu trúc, màu, logo, độ rõ timeline, thư viện và hộp thoại. Sau đó mới bắt đầu skeleton PySide6, benchmark ASR, dữ liệu, tích hợp Codex và đóng gói Windows. HTML/CSS của mockup không phải quyết định chuyển sang Electron hoặc sản phẩm web.
