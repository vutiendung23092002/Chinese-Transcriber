# Xử lý sự cố

## Chữ Trung tiếp tục xuất hiện nhưng tiếng Việt còn chờ

Khi toggle **Dịch cả bài một lượt** tắt, ASR và dịch là hai luồng độc lập. Dịch có thể chậm hơn ASR; thanh trạng thái cho biết số đoạn đã chốt/đã dịch/còn chờ. Khi toggle bật, chờ toàn bộ chép lời hoàn tất mới bắt đầu dịch là hành vi dự kiến; tiếng Việt xuất hiện sau khi Codex trả đủ kết quả của lượt dịch. Đoạn chờ nằm trong SQLite, không mất khi giao diện chuyển trang.

Nếu dịch báo lỗi, chép lời vẫn tiếp tục. Chờ tác vụ kết thúc hoặc bấm **Dừng tác vụ**, sau đó chọn **Thư viện → Tiếp tục / thử lại** trên đúng bản dịch. Ứng dụng giữ chế độ dịch/model/bối cảnh đã dùng, giữ phần đã dịch và tiếp tục phần còn thiếu; nếu ASR cũng chưa xong thì tiếp tục cùng transcript, không tạo thêm bản trùng. Dừng là thao tác có phối hợp, giữ các đoạn đã lưu và chờ lượt gọi đang chạy đóng lại.

Nếu dịch cả bài báo vượt giới hạn hoặc hết thời gian chờ, bản Trung và âm thanh vẫn được giữ. Chế độ này không tự chia bài thành nhiều lượt; chọn **Bản chép lời**, tắt toggle và dùng **Dịch bản chép lời** để tạo một bản dịch song song mới nếu cần. **Tiếp tục / thử lại** luôn dùng chế độ đã lưu của tác vụ cũ.

## App báo Not Responding khi phát âm thanh trong lúc dịch

Bản sửa ngày 15/11/2026 loại bỏ Python Qt message handler khỏi đường log của FFmpeg. Callback này có thể đợi GIL trong luồng giải mã trong khi luồng giao diện giữ GIL và chờ giải mã trong `QMediaPlayer.play()`, làm khóa cả giao diện lẫn tiến độ tác vụ Python. Không phải cứ chờ model lâu là giao diện phải đứng.

Chạy bản source cập nhật bằng `Run.bat`. Khi cần mở lại sau một phiên treo, các câu đã hoàn tất vẫn nằm trong thư viện; vào **Thư viện → Tiếp tục / thử lại** trên bản dịch gián đoạn để chạy phần còn thiếu. Không cần tạo bản dịch mới hoặc xóa dữ liệu. Đường FFmpeg → Qt vẫn được giữ để tránh lỗi CRT stderr từng ảnh hưởng file SQLite; log native không gọi Python. Lỗi phát âm thanh và lỗi dịch vẫn có thông báo riêng trong app.

## Live bỏ sót lời khi điện thoại phát loa ngoài gần mic tai nghe

Đây là đường thu microphone, không phải thu âm thanh hệ thống. Chọn đúng **Headset/Microphone** của tai nghe trong trang Live; tên trình điều khiển nằm sau dấu chấm giữa. Sau bản cập nhật cách nhớ mic, có thể cần chọn lại một lần. Ứng dụng nhớ tên và trình điều khiển, tìm lại số thứ tự ngay trước khi thu; nếu thiết bị cũ không còn kết nối hoặc có nhiều thiết bị trùng tên, phải chọn lại thay vì tự chuyển sang mic khác.

Thử cùng một đoạn 10–15 giây bằng giọng nói trực tiếp gần mic và bằng loa ngoài điện thoại gần mic. Nghe lại âm thanh gốc đã lưu: nếu lời đã bị cắt hoặc im lặng trong WAV thì thay model dịch hay tăng mức suy luận không khôi phục được. Nếu chỉ tiếng từ điện thoại bị mất, kiểm tra bộ lọc tiếng gọi/voice isolation của tai nghe và hiệu ứng microphone của Windows. Có thể thử tắt **Audio enhancements** cho đúng microphone nếu Windows có mục này, rồi so sánh lại; ANC dùng khi nghe không đồng nghĩa với bộ lọc microphone. Hướng dẫn Microsoft: https://support.microsoft.com/en-au/office/disable-audio-enhancements.

Live đo mức thu từ PCM gốc khoảng 3 lần/giây, dùng thang âm lượng để dễ thấy tiếng nhỏ. Khi tín hiệu gần như im lặng, rất nhỏ hoặc bị vỡ kéo dài 8 giây, thanh trạng thái hiện cảnh báo có điều kiện; im lặng khi không ai nói vẫn bình thường. Rê chuột lên mức mic để xem dBFS. Cảnh báo không dừng ghi, không tăng âm, không xóa mẫu và không làm thay đổi âm thanh đã lưu. Thông số mức thu và tên mic nằm trong journal tác vụ để chẩn đoán.

`RawInputStream` chỉ có nghĩa dữ liệu PCM thô ở giao diện thư viện, không bảo đảm bỏ qua xử lý của Windows hoặc firmware tai nghe. Bản sửa không tuyên bố đã tắt các bộ lọc này. Các kết quả ASR chỉ có dấu câu sẽ không tạo hàng chép lời hoặc gửi dịch; các từ ngắn như “一”, “没有。” vẫn được giữ. Ngưỡng VAD và model nhận dạng chưa đổi vì hạ ngưỡng chưa chứng minh cải thiện trên bản ghi lỗi.

## Microphone nhận diện nhưng đồng hồ vẫn 00:00

Thiết bị chưa trả mẫu âm thanh. Kiểm tra microphone đã kết nối, chế độ đàm thoại của tai nghe Bluetooth, quyền microphone cho ứng dụng desktop trong Windows và chọn đúng thiết bị trong ứng dụng. Thử microphone có dây hoặc microphone tích hợp. Chương trình không lưu một bản ghi rỗng như thành công.

Trong môi trường phát triển, soundcore R60i NC được cả PortAudio và Qt nhận diện nhưng trả 0 mẫu dù quyền Windows là Allow. Vì vậy chưa thể xác nhận thu giọng nói thực qua thiết bị này; ASR live được kiểm tra bằng luồng âm thanh tiếng Trung thật phát lại vào đường xử lý.

## Chưa có model

Mở Cài đặt → nhận dạng giọng nói → tải SenseVoiceSmall, Streaming Paraformer và Silero VAD; hoặc chọn thư mục có ba thư mục con sensevoice, paraformer và vad. Đừng chỉ chọn một file ONNX. Cần kết nối mạng để tải lần đầu; ASR sau đó chạy cục bộ.

## Codex không tìm thấy / chưa đăng nhập

Chọn codex.exe trong Cài đặt. Có thể dùng executable đi kèm phần mở rộng Codex của VS Code hoặc bản CLI độc lập. Đăng nhập bằng nút trong ứng dụng hoặc codex login; kiểm tra lại. Không nhập API key/token vào prompt dịch.

## Model hoặc mức suy luận không khả dụng

Chọn Kiểm tra kết nối để đọc danh sách hiện tại. Lựa chọn cũ không khả dụng được giữ với cảnh báo để bạn tự chọn; ứng dụng không tự thay thế. Nếu CLI đổi giao thức, xem application.log và đối chiếu phiên bản trong Cài đặt.

## Một số đoạn dịch lỗi / hết hạn mức

Nguồn, transcript và các đoạn hoàn tất vẫn còn. Dừng tác vụ, đợi hạn mức nếu cần, rồi mở Thư viện → Tiếp tục/thử lại. Chỉ đoạn chưa hoàn tất được xử lý lại. Không xóa thư viện để sửa lỗi đăng nhập hoặc quota.

## ASR chậm hoặc thiếu đoạn trong Live

Để luồng CPU ở 2–4, đóng ứng dụng nặng và giữ nguồn ghi âm. Nếu hàng đợi ASR chậm quá mức, app giữ âm thanh và đánh dấu cần chép lời lại từ nguồn đã lưu. Không dùng model GPU vì bản hiện tại tối ưu CPU.

## Lưu thất bại / thiếu dung lượng

Không xóa recordings/ khi chưa phục hồi. Dọn dung lượng hoặc chọn thư viện khác; thư viện lỗi không được âm thầm tạo lại. Tạo bản sao toàn bộ dữ liệu trước thao tác sửa thủ công.

## Portable

Giải nén toàn bộ folder và mở **ChineseTranscriber.exe**. Không kéo riêng launcher hoặc EXE ra khỏi các thư mục đi kèm. Với MSI, dùng lối tắt **Chinese Transcriber** trong Start Menu. Không cần cài Python riêng. Xem PACKAGING.md để phân biệt các kết quả kiểm thử của EXE và Python launcher.

## Smart App Control chặn Run.bat nhưng EXE vẫn chạy

Nếu **ChineseTranscriber.exe** chạy bình thường, tiếp tục mở EXE; không cần chạy thêm `Run.bat`. BAT là launcher phụ, không phải bước bắt buộc.

Thông báo **“files of this type from the internet can be dangerous”** khi mở BAT cho thấy Windows đang chặn loại file tải từ Internet. Trong trường hợp đã kiểm tra ngày 16/11/2026, `Run.bat` trong Downloads có cùng SHA-256 với bản build, nhưng mang `Zone.Identifier` với `ZoneId=3`; file build tại chỗ không có dấu đó. Microsoft xác nhận giá trị này biểu thị nguồn Internet trong [tài liệu về Zone.Identifier](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/unblock-file#description). Chữ ký của `pythonw.exe` không áp dụng cho `Run.bat`, nên Python có chữ ký không bảo đảm BAT được phép mở.

Người dùng xác nhận EXE cùng gói ZIP tải từ Release chạy được dù BAT bị chặn. Kết quả EXE bị chặn `4551` trong lần kiểm tra build trước vẫn được giữ như dữ liệu kiểm thử riêng; không suy rộng kết quả đó cho mọi lần chạy. [Smart App Control](https://support.microsoft.com/en-us/windows/security/threat-malware-protection/smart-app-control-frequently-asked-questions) đánh giá độ tin cậy của ứng dụng qua dịch vụ bảo mật và chữ ký.

Bộ cài MSI tạo lối tắt trỏ trực tiếp tới runtime đi kèm và `launch.py`, không cần mở BAT. MSI chưa ký số và vẫn có thể bị chính sách Windows chặn. Không cần tắt Smart App Control khi EXE đã chạy được.

## Run.bat trong thư mục source bị chặn khi mở Python

Kiểm tra đường dẫn file trong log **Event Viewer → Applications and Services Logs → Microsoft → Windows → CodeIntegrity → Operational**. Trong lần chặn đã xác minh ngày 16/11/2026, event 3077/3033 ghi `cmd.exe` mở `.venv\Scripts\pythonw.exe` không đạt yêu cầu chữ ký. BAT trong workspace không có dấu nguồn Internet; đây là trường hợp khác với BAT tải về bị chặn ngay khi mở.

Launcher source đã đổi thứ tự: ưu tiên Python PSF chính thức có chữ ký tại `.tools/python311` nếu có cấu hình `python311._pth`, sau đó mới dùng `.venv`. Bản runtime trong workspace đã được cấu hình đọc dependency ở `.venv/Lib/site-packages` và source ở `src`; không xóa môi trường hoặc dữ liệu. Nếu dùng máy mới, cần chuẩn bị runtime/dependency theo PACKAGING.md hoặc dùng gói phát hành. Thay đổi này không bảo đảm mọi chính sách Windows cho phép mọi runtime và không sửa chính sách bảo mật.
