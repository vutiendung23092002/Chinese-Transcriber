const fs=require('fs');
const documents={
'README.md':`# Chinese Transcriber — Thiết kế V2

**DESIGN READY FOR REVIEW · Giai đoạn 1 · Chưa phê duyệt.**

V2 thiết kế lại giao diện và màu theo ảnh tham khảo bạn vừa gửi: sidebar than tím dạng capsule, mục chọn hồng nhạt, cột thao tác riêng và khung làm việc trắng ngà bo góc lớn. Hai hướng màu của V1 được thay thế trong bản duyệt hiện tại.

## Xem bản mới

Mở [review.html](assets/mockups/review.html) bằng Chrome hoặc Edge, không cần máy chủ. Dùng các icon ở thanh bên để chuyển trang; tên trang hiện khi rê chuột hoặc focus bằng bàn phím. Cột kế bên hiển thị tác vụ theo từng trang. Thanh phía trên cho đổi sáng/tối.

- [Trang chủ V2](assets/mockups/v2-light-01-dashboard.png)
- [Chi tiết sidebar](assets/mockups/v2-sidebar-detail.png)
- [Màn hình dịch file](assets/mockups/v2-light-02-file.png)
- [Ghi âm trực tiếp](assets/mockups/v2-light-03-live.png)
- [Toàn bộ 7 màn hình sáng/tối](assets/mockups/v2-00-screen-overview.png)
- [Màu sắc và logo](assets/mockups/v2-00-brand-board.png)

## Hướng thị giác

Than tím #292636 · Trắng ngà #F6F5F7 · Hồng chọn #F2BFCD · Hồng phấn #FBE2E9 · Lavender #EEE5FB · Vàng kem #FFF0CB · Xanh sương #DEF1F3.

Logo đề xuất V2: Nhịp lời, biểu tượng tròn than tím có bốn nhịp âm trắng/hồng. Có thêm phương án sách song ngữ cùng bảng màu.

## Tài liệu

- [UI_CONCEPT.md](docs/UI_CONCEPT.md): cấu trúc và từng màn hình.
- [USER_FLOWS.md](docs/USER_FLOWS.md): các luồng file, live, phiên bản và thùng rác.
- [BRAND_DIRECTION.md](docs/BRAND_DIRECTION.md): định hướng V2 theo mẫu tham khảo.
- [COLOR_SYSTEM.md](docs/COLOR_SYSTEM.md): màu sáng/tối và ngữ nghĩa.
- [DESIGN_REVIEW.md](docs/DESIGN_REVIEW.md): ảnh bàn giao và các điểm chờ duyệt.

Bộ V2 có 20 PNG và 2 logo SVG mới. Bản V1 được lưu trong assets/mockups/archive/v1 để tham khảo lịch sử, không còn là đề xuất hiện tại.

## Phạm vi

Đây là bản xem thiết kế với dữ liệu mẫu. Điều hướng, đổi theme, chọn model mẫu, lọc thư viện và hộp thoại giúp duyệt UX; nút sản phẩm chưa kết nối dịch, ghi âm, xuất file hoặc xóa dữ liệu. Nút sao chép hướng dẫn chỉ chép văn bản vào clipboard.

Chưa triển khai Python/PySide6, cơ sở dữ liệu, xử lý âm thanh hoặc tích hợp Codex. Chỉ bắt đầu sau khi bạn duyệt thiết kế. Công nghệ ứng dụng vẫn theo brief ban đầu, không đổi sang ứng dụng web.

## Xuất lại ảnh thiết kế

Chạy từ thư mục dự án trên máy có Node và Chrome:

    npm.cmd install --prefix .design-tools playwright --no-audit --no-fund
    node .design-tools/render.cjs

Playwright chỉ phục vụ xuất PNG và kiểm tra bản thiết kế.
`,
'docs/BRAND_DIRECTION.md':`# Định hướng thương hiệu — V2

**Chờ duyệt · Giai đoạn 1 · 14/11/2026.**

## Căn cứ mới

Người dùng không chọn giao diện và bảng màu V1, đồng thời cung cấp ảnh dashboard có sidebar tối dạng thanh icon bo tròn, khung nội dung sáng và các điểm nhấn pastel. V2 lấy cấu trúc, nhịp khoảng trắng, độ mềm của thẻ và tương quan màu từ ảnh này. Các nội dung bác sĩ, bệnh viện và ảnh chân dung được thay bằng tác vụ học tập Trung–Việt.

## Pastel & Graphite

Thanh điều hướng than tím #292636, mục đang chọn hồng #F2BFCD, workspace trắng ngà #F6F5F7 và panel trắng. Hồng phấn, lavender, vàng kem và xanh sương giúp phân nhóm tác vụ. Chữ chính luôn dùng than tím đủ đậm, không dùng màu pastel nhạt cho chữ nhỏ.

Thanh icon là capsule đứng rộng 54 px, đặt trong dải trắng 82 px. Logo tròn tách ở trên. Mục chọn nổi bằng nền hồng và khoảng trắng xung quanh; tên mục hiện khi hover hoặc focus. Tên trang và tác vụ được viết đầy đủ ở cột kế bên, tránh phụ thuộc hoàn toàn vào việc nhớ icon.

Cột thao tác thay đổi theo trang: lưới tác vụ ở Home; nguồn và tùy chọn ở File; bối cảnh phiên ở Live; nhóm âm thanh ở Library; bộ glossary ở Prompt. Vùng nội dung chính không có sidebar chữ dài của V1.

Bo góc lớn 17–29 px, viền mỏng, bóng nhẹ. Nút chính than tím thay cho xanh ngọc. Ảnh mẫu có cảm giác mềm nhưng sản phẩm vẫn cần giữ transcript dễ đọc: mốc giờ ổn định, hai cột cùng hàng, trạng thái có chữ.

## Logo V2 — Nhịp lời

[03-v2-voice-rhythm.svg](../assets/logo-concepts/03-v2-voice-rhythm.svg)

Đĩa tròn than tím với bốn nhịp âm trắng/hồng. Phù hợp vị trí đầu sidebar và dễ thu nhỏ. Đây là biểu tượng đề xuất của vòng duyệt, chưa phải thương hiệu được kiểm tra trùng lặp.

Phương án khác: [04-v2-parallel-pages.svg](../assets/logo-concepts/04-v2-parallel-pages.svg), cuốn sách mở có nhịp âm và dòng chữ, đổi sang hồng phấn/than tím. Giữ lựa chọn này nếu muốn nhấn mạnh việc học song ngữ hơn hội thoại.

Bảng duyệt có mẫu 32 px và 16 px. Khi đóng gói Windows sau duyệt cần tinh chỉnh quang học và xuất icon nhiều kích thước. Không dùng màu logo thay cho trạng thái ghi âm hoặc lỗi.

## Giao diện tối

Giữ cùng hướng thị giác: nền tím than ấm #24212E, panel #302B3B, nhấn hồng #EFC0CF và chữ trắng mềm. Đây là biến thể tối của V2, không giữ hai phương án A/B đã bị từ chối.

## Phạm vi duyệt

Logo, màu, độ bo góc, kiểu sidebar và nhịp bố cục đang chờ duyệt. Bản đầu được lưu tại assets/mockups/archive/v1. Xem [bảng V2](../assets/mockups/v2-00-brand-board.png).
`,
'docs/COLOR_SYSTEM.md':`# Hệ màu V2 — Pastel & Graphite

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
`,
'docs/DESIGN_REVIEW.md':`# Bàn giao duyệt thiết kế V2

**DESIGN READY FOR REVIEW · Chưa phê duyệt · Chưa triển khai ứng dụng.**

## Thay đổi theo phản hồi

V1 không được chọn. V2 thiết kế lại theo ảnh sidebar bạn gửi: thanh icon tối dạng capsule, mục chọn hồng nổi trên khoảng trắng, logo tròn ở đầu thanh, cột thao tác kế bên và workspace sáng bo góc lớn. Màu chủ đạo chuyển sang than tím/trắng ngà; thẻ hồng phấn, lavender, vàng kem và xanh sương.

Luồng học tập vẫn theo brief. File mode đưa nguồn, bối cảnh, model và effort vào cột thao tác để timeline rộng hơn. Home dùng các thẻ tác vụ và bài học gần đây. Library vẫn giữ một nguồn âm thanh với nhiều phiên bản.

## Xem bản mới

1. [Bản xem có điều hướng](../assets/mockups/review.html).
2. [Chi tiết sidebar](../assets/mockups/v2-sidebar-detail.png).
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

Tổng V2: 20 PNG, 2 SVG logo mới, bản xem điều hướng và tài liệu cập nhật. Bản V1 được lưu tại assets/mockups/archive/v1.

## Chờ duyệt

- Kiểu sidebar capsule và trạng thái chọn hồng.
- Cấu trúc ba phần: icon / thao tác / nội dung.
- Bảng màu pastel và mức bo góc.
- Độ rõ của timeline và danh sách phiên bản.
- Logo Nhịp lời hoặc phương án Hai trang song ngữ.

Bạn có thể duyệt V2 hoặc yêu cầu chỉnh tiếp. Mẫu tham khảo là căn cứ định hướng, không được coi là phê duyệt bản thiết kế mới thay bạn.

## Kiểm tra bản xem

Kiểm tra hiển thị các màn hình, lỗi JavaScript, điều hướng sidebar, chọn model mẫu, tìm trong thư viện, theme, đóng dialog bằng Escape và checkbox giữ audio mặc định. Kiểm tra tràn ngang ở 1600, 1366, 1024, 768 và 390 px; kiểm tra cặp màu chữ/nền ở cả sáng và tối.

Đây là kiểm tra mockup. Chưa chạy ASR, thu microphone, gọi Codex, lưu cơ sở dữ liệu, xuất TXT hoặc xóa/khôi phục thật. Bước tiếp theo vẫn là duyệt hoặc sửa thiết kế giai đoạn 1.
`
};
for(const [file,text] of Object.entries(documents))fs.writeFileSync(file,text,'utf8');
let ui=fs.readFileSync('docs/UI_CONCEPT.md','utf8');
ui=ui.replace('Định hướng đề xuất: **A — Ngọc nghiên cứu + Logo 01**. Phương án B — Đêm tập trung có cùng cấu trúc để đánh giá màu mà không thay đổi luồng.','Định hướng hiện tại: **V2 — Pastel & Graphite**, thiết kế lại theo mẫu sidebar người dùng cung cấp sau khi không chọn V1. Có hai chế độ sáng/tối trong cùng hướng, logo đề xuất Nhịp lời.');
ui=ui.replace('Hai ảnh tham khảo trong brief không có đường dẫn hoặc tệp đính kèm. Thiết kế dựa trên mô tả sidebar và dashboard; không khẳng định đã xem ảnh tham khảo.','Brief đầu không có ảnh đính kèm; ở vòng V2 người dùng đã cung cấp trực tiếp ảnh dashboard với sidebar capsule tối, mục chọn hồng và cột tác vụ. Thiết kế hiện tại dựa trên ảnh này. Nội dung y tế trong ảnh được thay bằng tác vụ học tập.');
ui=ui.replace('Khung desktop có titlebar Windows, sidebar 226 px, header nội dung và workspace. Ảnh chính xuất ở 1600 × 1000 px; đây là kích thước khung duyệt, không phải ràng buộc độ phân giải sản phẩm. Khoảng cách theo bội 4/8 px, panel 12 px, control 6–8 px. Icon nét đơn 16–20 px, cùng trọng lượng thị giác.','Khung desktop V2 có titlebar Windows, dải điều hướng 82 px chứa capsule tối 54 px, cột thao tác 198–267 px tùy trang và workspace bên phải. Ảnh chính xuất ở 1600 × 1000 px, không phải ràng buộc độ phân giải sản phẩm. Panel bo góc 17–22 px, khung app 29 px. Icon nét đơn 16–20 px. Nhãn điều hướng hiện khi hover/focus; tên trang và tác vụ luôn có trong nội dung.');
ui=ui.replace('Hai kiểu workspace:','Hai kiểu workspace bên phải thanh icon và cột thao tác:');
ui=ui.replace('**Làm việc:** thiết lập bên trái, timeline chiếm phần lớn diện tích bên phải. Với Live, thanh ghi âm nằm trên và bảng giải thích trạng thái ở phải.','**Làm việc:** thiết lập nằm trong cột thao tác, timeline chiếm vùng chính. Với Live, thanh ghi âm nằm trên; cấu hình và giải thích trạng thái nằm ở cột thao tác, không thêm panel phải.');
ui=ui.replace('Sidebar và tác vụ trong header vẫn dễ tìm.','Thanh icon giữ vị trí và tác vụ trong header vẫn dễ tìm. Cột thao tác được thu lại ở bản xem dưới 1151 px; cấu hình File chuyển vào vùng nội dung.');
ui=ui.replace('Cột trái là bộ đã lưu và nút tạo bộ.','Cột thao tác kế thanh icon là bộ đã lưu và nút tạo bộ.');
fs.writeFileSync('docs/UI_CONCEPT.md',ui,'utf8');
let flows=fs.readFileSync('docs/USER_FLOWS.md','utf8');
flows=flows.replace('Giai đoạn 1 · Chờ phê duyệt · Không có nghiệp vụ đang chạy trong bản xem.','Giai đoạn 1 · V2 theo ảnh sidebar mới · Chờ phê duyệt · Không có nghiệp vụ đang chạy trong bản xem. Các bước điều hướng dùng icon có nhãn hover/focus và cột thao tác theo trang.');
flows=flows.replaceAll('../assets/mockups/dialog-','../assets/mockups/v2-dialog-');
fs.writeFileSync('docs/USER_FLOWS.md',flows,'utf8');
let render=fs.readFileSync('.design-tools/render.cjs','utf8');
render=render.replace("  await capture('v2-00-brand-board'", "  report.screenshots.push('v2-sidebar-detail.png');\n  await capture('v2-00-brand-board'");
render=render.replace('background:#edf0eb;color:#182c29','background:#f6f5f7;color:#292633').replace('color:#52645f','color:#696471').replace('border:1px solid #ccd7cf','border:1px solid #e9e6ed').replace('color:#0f766e','color:#85536c');
render=render.replace('Bảy màn hình. Hai hướng thị giác.','Thiết kế V2 · Theo mẫu sidebar mới.').replace('A · Ngọc nghiên cứu / Sáng','Pastel & Graphite / Sáng').replace('B · Đêm tập trung / Tối','Pastel & Graphite / Tối');
render=render.replace("path.join(output,'00-screen-overview.png')","path.join(output,'v2-00-screen-overview.png')");
render=render.replace("'info-bg','interim'","'info-bg','interim','pink','pink-ink','lavender','lavender-ink','yellow','yellow-ink','cyan','cyan-ink','rail','rail-muted'");
render=render.replace("['interim','panel']","['interim','panel'],['pink-ink','pink'],['lavender-ink','lavender'],['yellow-ink','yellow'],['cyan-ink','cyan'],['rail-muted','rail']");
fs.writeFileSync('.design-tools/render.cjs',render,'utf8');
console.log('Updated V2 documentation, review links and design exports.');
