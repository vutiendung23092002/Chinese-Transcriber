# Báo cáo kiểm thử Phase 2

Ngày 14/11/2026. Windows 11 x64, Intel Core i7-12700F (20 logical CPU), RAM 31,8 GiB. Python 3.11.9, Qt/PySide6 6.12.0, sherpa-onnx 1.13.8. ASR giới hạn 4 luồng CPU, VAD 1 luồng; không CUDA, Docker hoặc WSL.

## Tự động

24 test đạt với pytest: import trùng và import đồng thời; phiên bản/quan hệ nguồn; trash/restore/xóa vĩnh viễn; không khôi phục nhầm bản đã xóa trước; glossary snapshot; ID JSON sai/thiếu/trùng; model/effort không được thay ngầm; ASR và online streaming thật; phục hồi PCM; lỗi ASR vẫn giữ ghi âm; lỗi dịch vẫn giữ kết quả trước; timeline/TXT và hiệu đính đoạn Việt còn thiếu tạo bản mới, giữ bản cũ; thay đổi thuật ngữ chưa lưu có thể hủy chuyển trang hoặc lưu rồi chuyển. Bốn ca mới kiểm tra trang Cài đặt: giữ model/effort không được hỗ trợ cho tới khi người dùng chọn hợp lệ và lưu, không bịa hạn mức còn thiếu, CPU/theme được lưu và nút backup tạo SQLite thật.

Trang Cài đặt mới bám ảnh assets/mockups/settings-redesign-v1.png đã được người dùng duyệt. scripts/verify_settings.py kiểm tra sáu thẻ không chồng lấn, không cuộn ngang, điều hướng nhóm ở cửa sổ hẹp; có mười ảnh cho năm kích thước × hai theme và tám ảnh hộp thoại chi tiết. Chế độ --live --windows dùng backend Qt Windows và trạng thái/model/quota đọc trực tiếp từ CLI đã cài. Report tại .test-data/settings-approved/validation-live.json. Chế độ fixture ghi rõ dữ liệu minh họa, chỉ dùng để đối chiếu bố cục với ảnh mẫu; không phải dữ liệu hiển thị trong ứng dụng bình thường.

Kiểm tra bố cục native qua 7 trang, 4 kích thước cửa sổ 1440×900 / 1366×768 / 1100×720 / 1024×700, cả Light/Dark, scale 100/125/150/200% trong Qt offscreen: 224 lượt đạt. Kiểm tra chiều rộng rail/context không đổi khi chuyển trang, không có QScrollArea trong context và các field/nút hiển thị nằm trong cột. Đây là kiểm tra hình học Qt; chưa thay cho kiểm tra Windows multi-monitor và DPI động trên phần cứng khác. Ảnh chụp widget thật của bảy trang đã được xem để kiểm tra màu, chữ và sidebar.

## Luồng dữ liệu thật

- File Mandarin WAV chính thức của sherpa-onnx → Silero/SenseVoice → SQLite → Codex CLI đã cài → bản Việt đúng tập ID → hai TXT UTF-8. Không dùng phản hồi dịch giả.
- Codex CLI 0.169.0-alpha.11.1: đã đăng nhập ChatGPT, model/list trả đủ 8 model đã yêu cầu và supportedReasoningEfforts. account/rateLimits/read cung cấp cửa sổ 300 và 10080 phút. UI đọc dữ liệu thật, không tạo giá trị khi thiếu.
- Live: WAV Mandarin đưa vào ranh giới adapter microphone, phía sau dùng capture queue/journal/Streaming Paraformer/Silero/SenseVoice/Codex thật. Có interim, final, bản Việt và WAV đã lưu; mọi event dịch đến sau final tương ứng. Chỉ phần thiết bị đầu vào được thay trong script kiểm tra, không thay recognizer/translator.
- EXE đóng gói đầu: smoke exit 0; ASR/Codex/TXT/restore/SQLite integrity đạt; Qt QAudioDecoder tạo 89.472 mẫu từ fixture WAV, không lỗi codec. Report tại .test-data/frozen-selftest/selftest-report.json.
- Một bản EXE trước (SHA-256 e9d2253b839588f548acf818da016e59ddb6dcca13dd54eb28d7615975f074b9) đã chạy smoke/ASR/Codex/WAV-MP3-M4A/TXT/SQLite thành công. Report giữ tại .test-data/prior-frozen/validation.json. Sau sửa bảo vệ thay đổi thuật ngữ chưa lưu, artifact EXE cuối bị Smart App Control chặn (WinError 4551); report .test-data/release/validation.json ghi rõ chưa chạy được. Code Integrity 3077/3033 cho thấy yêu cầu chữ ký. Không sửa chính sách Windows, không thêm chứng thư tự ký; chưa xác định được vì sao policy đánh giá khác nhau giữa các build. Kết quả artifact trước không được coi là nghiệm thu EXE cuối.
- Runtime Python PSF có chữ ký chạy source cuối: WAV/MP3/M4A đều có ASR và Qt decode hơn 89 nghìn mẫu; WAV gọi Codex và xuất hai TXT thành công. Gói có Run.bat cùng runtime Python riêng; kết quả kiểm tra gói này tại .test-data/portable-python/validation.json, khác với kiểm tra EXE PyInstaller.

Các kết quả kiểm tra dùng thư viện riêng trong .test-data, không lấy âm thanh cá nhân. Không đưa thông tin tài khoản Codex, fixture WAV hoặc kết quả thử vào gói portable.

## Benchmark model

Cả SenseVoiceSmall INT8 và Streaming Paraformer INT8 được chạy trên **cùng hai fixture**, mỗi cặp hai lượt. Kết quả thô, chữ nhận dạng và thông số nằm tại ASR_BENCHMARK.json.

| Fixture | Thời lượng | SenseVoice RTF | Paraformer RTF |
|---|---:|---:|---:|
| Mandarin của SenseVoice | 5,592 giây | 0,027–0,029 | 0,064–0,070 |
| Mandarin/English của Paraformer | 10,053 giây | 0,026 | 0,055–0,057 |

RTF = thời gian inference / thời lượng nguồn; số trên không gồm tốc độ phát microphone, mạng hoặc Codex. Nạp hai model khoảng 2,39 giây, process khoảng 601–626 MiB RSS. Pipeline file đã nạp model mất 0,209–0,237 giây cho fixture 5,592 giây. Đây là phép đo ngắn trên máy phát triển, không phải cam kết tốc độ bài giảng dài.

SenseVoice được chọn tạo chữ cuối; Paraformer cung cấp interim. Kết quả ngắn cho thấy đầu ra còn lỗi, đặc biệt code-switching. Chưa có tập bài giảng gán nhãn để kết luận CER/WER, độ chính xác chuyên ngành hoặc ưu thế tổng quát. Chưa benchmark trên Ryzen 5 7535HS / 16 GB theo máy đích.

## Các giới hạn cần kiểm tra thực tế

Microphone Bluetooth **soundcore R60i NC** được Windows/PortAudio/Qt liệt kê nhưng hai backend đều không nhận được frame trong lần kiểm tra, dù stream mở và không báo lỗi, quyền microphone là Allow. Chưa xác minh thu giọng nói trực tiếp trên thiết bị này. Ứng dụng giữ trạng thái chờ dữ liệu, cảnh báo sau 5 giây và không coi bản ghi rỗng là thành công. Cần kiểm tra với microphone có tín hiệu thực; chưa thể khẳng định nguyên nhân nằm ở driver, cấu hình Bluetooth hay môi trường thu.

Mốc giờ là ranh giới speech từ sample/Silero VAD, chưa phải forced alignment từng từ. Đoạn dài bị giới hạn 20 giây để tránh tăng bộ nhớ/độ trễ; VAD có thể cắt ngang câu dài hoặc gộp nhiều câu không có khoảng nghỉ. Cần nghe và hiệu đính ở vùng lời nối liền, tiếng ồn hoặc nhiều người nói. Chưa có diarization.

Qt decoder/playback điều khiển được kiểm tra ở mức backend; chưa có đánh giá nghe chủ quan hoặc bài kiểm tra khóa máy/sleep/unplug thiết bị dài hạn. Journal fsync theo chu kỳ khoảng 1 giây; mất điện đột ngột có thể mất phần cuối chưa đồng bộ. Model/CLI và quyền truy cập tài khoản có thể thay đổi, ứng dụng xác minh lại trước khi dịch.
