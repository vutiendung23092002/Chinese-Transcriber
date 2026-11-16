# Báo cáo kiểm thử Phase 2

Ngày 14/11/2026. Windows 11 x64, Intel Core i7-12700F (20 logical CPU), RAM 31,8 GiB. Python 3.11.9, Qt/PySide6 6.12.0, sherpa-onnx 1.13.8. ASR giới hạn 4 luồng CPU, VAD 1 luồng; không CUDA, Docker hoặc WSL.

## Build lại EXE — 16/11/2026

Build từ commit 9fa392c bằng PyInstaller 6.22.3 và Python PSF 3.11.9. EXE mới có các màn giao diện hiện tại và SVG dropdown; smoke exit 0. Kiểm tra trực tiếp EXE đóng gói qua WAV, MP3, M4A đều có ASR thật, Qt decode 89.472 mẫu, không lỗi codec và SQLite integrity ok. WAV gọi Codex thật, kiểm tra ID JSON, xuất hai TXT và giữ nguồn sau trash/restore. Report .test-data/release/validation.json ghi frozen=true, source_mode=false và portable_python=false. SHA-256 EXE: bbc7e759b372eee933f8d23801c4a7814c7c495382f51c8d821ca01cd5a38540.

Chạy lại toàn bộ bộ kiểm thử: 77 test đạt trong 35,53 giây. Không thay đổi chính sách Windows hoặc chữ ký để chạy bản EXE này. Thông tin bản build kèm trong BUILD-INFO.json của gói portable.

## Chép lời file và dịch song song — 15/11/2026

Toàn bộ **77 test đạt** (`pytest -q`, 28,96 giây), bố cục 224 lượt vẫn đạt. Nút chính File đổi thành **Chép lời và dịch** khi có danh sách model Codex; khi chưa kết nối vẫn có đường chép lời cục bộ. Nút dịch riêng giữ chức năng tạo bản dịch khác từ transcript có sẵn.

Ca dùng ASR và Codex thật chạy trên ba câu Mandarin chính thức trong thư viện thử riêng, giữ model/mức suy luận đang chọn: GPT-6.1 Sol / high. Lượt dịch đầu bắt đầu ở giây 1,891; ASR tiếp tục và hoàn tất ở giây 2,594, trong khi lượt dịch đầu đến giây 10,547 mới trả về. Lượt sau xử lý hai đoạn còn chờ; cả 3 đoạn hoàn tất ở khoảng giây 20,375. Báo cáo trong `.test-data/combined-real/latest.json`; không tạo phiên bản thử trong thư viện người dùng. Đây là kiểm tra tính đồng thời, không phải đánh giá CER/WER hay benchmark bài giảng.

Các ca bổ sung giữ lượt dịch đầu trong trạng thái chờ để kiểm tra ASR vẫn lưu thêm đoạn và bảng UI vẫn cập nhật/nhận timer. Lỗi chuẩn bị dịch hoặc lỗi sau ba lần thử không hủy ASR. Dừng/khôi phục dùng cùng transcript/version/job, giữ ID và nội dung đã dịch, không gửi lại đoạn complete; có kiểm tra nhận dạng thật ba câu và bỏ qua VAD segment đã lưu khi tiếp tục. Segment và mục chờ dịch được ghi cùng transaction; sai version rollback cả hai. Một ca điều khiển race lúc producer kết thúc sau snapshot hàng đợi kiểm tra không bỏ sót đoạn cuối. Bản chép lời chưa đủ không bật xuất Việt như một bản dịch hoàn chỉnh.

## Sửa treo khi phát âm thanh trong lúc dịch — 15/11/2026

Toàn bộ **66 test đạt** (`pytest -q`, 21,63 giây). Stack Python và native của tiến trình treo xác định main thread đang trong `QMediaPlayer.play()`, chờ FFmpeg decoder; decoder đang ghi log qua Qt và chờ GIL để gọi Python message handler. Callback ghi log được bỏ, giữ `QT_FFMPEG_DEBUG` để FFmpeg đi qua Qt thay cho callback CRT cũ. Qt dùng message handler native, không gọi Python từ decoder. Lỗi của player vẫn được chuyển qua tín hiệu `errorOccurred`; lỗi tác vụ Python vẫn ghi vào application.log.

Ca hồi quy chạy ở tiến trình con, dùng M4A/AAC được tạo từ tín hiệu thử và tác vụ dịch giả lập 11 đoạn, đồng thời phát/tua/tạm dừng/tiếp tục. Parent đặt timeout để chính bộ test không bị kẹt nếu lỗi trở lại. Cách cũ bị timeout sau 8 giây; bản sửa hoàn tất với 168 nhịp UI, đủ 11 đoạn và SQLite integrity `ok`. Ca kiểm tra cũ nạp lại media/ghi/checkpoint SQLite 20 lần vẫn đạt; một ca riêng kiểm tra không cài Python Qt message handler.

Đã sao lưu và kiểm tra integrity trước khi khởi động lại app treo. Bản dịch hiện có được tiếp tục, hoàn tất 11/11 đoạn; bấm phát ngay trong lúc dịch không làm treo giao diện. Không tạo phiên bản dịch thay thế hoặc thay model/effort. Stack và kết quả A/B của lần chẩn đoán nằm trong `.test-data/media-deadlock/`, không đóng gói vào sản phẩm.

## Bổ sung đường thu microphone — 15/11/2026

Toàn bộ **64 test đạt** (`pytest -q`, 19,47 giây), gồm các ca nhận dạng file và phát lại live bằng model thật. Các ca mới kiểm tra tên/driver tìm lại đúng mic khi index thay đổi, không chọn nhầm thiết bị khi mất kết nối/trùng tên, lựa chọn UI và chặn bắt đầu khi mic cũ không còn. WASAPI dùng chuyển định dạng dùng chung do PortAudio hỗ trợ; không thêm đường thu âm thanh hệ thống.

Mức thu đo từ PCM chưa sửa, hiển thị theo thang âm lượng khoảng 3 lần/giây; cảnh báo có điều kiện sau 8 giây im lặng/tín hiệu nhỏ/vỡ tiếng. Ca ghi 10 giây PCM im lặng kiểm tra WAV lưu ra giống từng mẫu, cảnh báo không dừng thu và thông số chẩn đoán còn trong journal đã hoàn tất. Các ca ngắn/metadata/dấu câu kiểm tra không gửi riêng “。” sang dịch và vẫn giữ một từ tiếng Trung hoặc chữ số có nghĩa. Ngưỡng VAD và model không đổi.

Các kiểm tra này không chứng minh cải thiện CER/WER với loa điện thoại qua mic tai nghe. Chưa thử lại nguồn điện thoại ngoài đời; phần mềm không thể khôi phục âm thanh đã bị thiết bị/driver triệt thành số 0 hoặc bảo đảm tắt bộ lọc trong firmware. Hướng dẫn so sánh giọng nói thật/loa điện thoại và hiệu ứng microphone ở `TROUBLESHOOTING.md`.

## Giao diện Bối cảnh & Thuật ngữ

Triển khai `assets/mockups/glossary-workspace-approved-v1.png`, không thêm tiêu đề lớn phía trên form. Lượt kiểm tra giao diện này có **50 test đạt**. Năm ca mới kiểm tra placeholder không thành dữ liệu, font/kích thước và co/giãn cửa sổ, bộ đếm và trạng thái lưu, chốt ô còn đang gõ khi lưu/chuyển trang, ghi JSON/context thật vào SQLite và lựa chọn áp dụng ở màn File.

Các ca thiếu/trùng thuật ngữ giữ nguyên bản lưu và chặn chuyển trang khi lưu lỗi. Ca đổi bộ kiểm tra Hủy khôi phục cả lựa chọn sidebar, Bỏ thay đổi giữ bản cũ, Lưu ghi đúng bộ trước khi chuyển, tạo bộ mới và xóa dòng; danh sách 17 bộ không đẩy chân kết nối ra khỏi panel. `.test-data/glossary-approved/validation.json` ghi 12 ảnh trống/có dữ liệu × ba kích thước × hai theme, dùng thư viện minh họa riêng; không cuộn ngang/dọc ngoài thẻ. Bộ 224 lượt kiểm tra bố cục/scale bao gồm các điều khiển chính của màn này. Mười ảnh Cài đặt và tám hộp thoại vẫn đạt kiểm tra hình học.

## Giao diện Thư viện

Triển khai `assets/mockups/library-workspace-approved-v1.png`, dùng bảng nguồn và phiên bản từ SQLite thật. Các ca Thư viện kiểm tra ba nút nhập, tìm kiếm chữ Việt/Trung và hoa/thường, trạng thái rỗng/không có kết quả, bộ đếm loại phiên bản đã xóa, mở đúng nguồn/transcript/phiên bản, tiếp tục/so sánh/xóa đúng ID. Ca xóa dùng thư viện thử riêng, kiểm tra hủy xác nhận, chuyển phiên bản/nguồn vào Thùng rác, khôi phục đúng nhóm và file gốc vẫn tồn tại.

Kiểm tra co/giãn cửa sổ trên chính trang đang mở, cả thư viện trống và có phiên bản, không cuộn ngang; các nút cuối danh sách phiên bản vẫn tới được bằng cuộn. `.test-data/library-approved/validation.json` ghi 12 ảnh (trống/có dữ liệu × ba kích thước × hai theme), dùng WAV và nội dung minh họa trong thư viện riêng. Cả 12 ảnh không cuộn ngang ở trang/bảng/phiên bản. Bộ 224 lượt kiểm tra scale có thêm hình học các vùng Thư viện. Mười ảnh Cài đặt và tám hộp thoại vẫn đạt.

## Giao diện Ghi âm trực tiếp

Triển khai `assets/mockups/live-workspace-approved-v1.png` sau lượt duyệt bỏ cụm tiêu đề trên cùng. Thanh ghi âm ở đầu thẻ, bảng Trung–Việt giãn và vùng câu chưa chốt riêng phía dưới. Không thêm lại header đã bỏ. Các ca Live kiểm tra hình học ở 1440×900, 1366×768, 1024×700, font thực tế, thao tác bắt đầu/tạm dừng/tiếp tục/dừng, đồng hồ từ số mẫu và mức mic.

Ca UI dùng adapter phiên thử nghiệm, không mở microphone: khởi tạo, đổi trạng thái, rồi đưa PCM thử vào hàm lưu thật để kiểm tra WAV/SQLite/bảng File sau khi dừng. Ca không có mẫu giữ 00:00, không tạo nguồn và hiển thị cảnh báo. Sự kiện interim không vào bảng; final/translation đi vào đúng hàng, mức mic/interim không dựng lại bảng, cuộn tay tắt tự theo và cờ này giữ khi đổi tab. Kết quả này không thay cho kiểm tra microphone phần cứng, vốn vẫn có giới hạn ghi ở cuối báo cáo.

Kiểm tra bố cục 224 lượt qua bảy trang, bốn kích thước, hai theme và bốn mức scale, gồm cả các điều khiển bên phải của Live và trường nhập trong panel tác vụ. Ảnh đối chiếu được tạo trong thư viện thử riêng; không dùng nội dung âm thanh cá nhân.

## Thẻ chọn model và suy luận

Triển khai `assets/mockups/model-selector-approved-v1.png` bằng widget Qt dùng chung cho File, Live và Cài đặt. Hai nút File bỏ tiền tố 1./2. Kiểm tra bấm/kéo theo nấc, bàn phím, đặt lại về mặc định của model, menu chỉ cho chọn model đã xác nhận, số nấc đổi theo model và giữ lựa chọn khi đổi tab/theme. Model/effort cũ không còn khả dụng được giữ và chặn dịch cho tới khi chọn lại; Cài đặt vẫn cần bấm Lưu mặc định.

Bộ thẻ model gồm kiểm tra bố cục 224 lượt qua bảy trang, bốn kích thước, hai theme và bốn mức scale; phạm vi containment gồm cả slider và nút đặt lại. Mười ảnh Cài đặt và tám hộp thoại vẫn đạt kiểm tra hình học. `.test-data/selector-design/validation.json` ghi 18 ảnh File/Live/Cài đặt ở ba kích thước × hai theme, dùng danh sách model đọc từ CLI đã cài và thư viện minh họa riêng đặt xhigh để đối chiếu ảnh. Cả 18 ảnh không cuộn ngang. Không đổi model/effort trong thư viện người dùng để tạo ảnh kiểm tra.

## Trang chủ sau khi duyệt giao diện

Trang chủ triển khai theo `assets/mockups/dashboard-approved-v3.png`, giữ nguyên menu gốc và vị trí vùng bên phải. Panel tác vụ bo góc 26px, mép trên ngang hàng thống kê/logo, mép dưới ngang đáy menu; ba thẻ và chân Codex nằm trong panel. Theo bổ sung của người dùng, cả bảy tab dùng chung panel này; kiểm tra hình học gồm mép trên/dưới và các nút/field nằm trong panel khi đổi trang, theme và scale. Thống kê và bài học tiếp tục theo bố cục v2. Kiểm tra ảnh render Qt ở 1440×900, 1366×768, 1024×700 và cả sáng/tối; không cuộn ngang. Cửa sổ thấp thu gọn cách xếp icon trong thẻ nhưng giữ nguyên cỡ chữ; chỉ vùng nội dung bên phải có thể cuộn. Kiểm tra thêm font Inter thực tế, cỡ/độ đậm tiêu đề, chiều cao thẻ, không có thẻ tác vụ lặp bên phải và nút mở bài học.

Bộ kiểm thử Trang chủ kiểm tra số nguồn/phiên bản và nhãn trạng thái từ SQLite thật, loại mục trong Thùng rác, mở đúng bài học, điều hướng ba thẻ, kéo thả file cục bộ và chặn nhập khi đang bận. Bộ bố cục bảy trang × bốn kích thước × hai theme × bốn mức scale vẫn qua 224 lượt.

Vòng kiểm thử Windows phát hiện thỉnh thoảng một trang SQLite trong thư viện thử nghiệm bị ghi đè bằng dòng `Input #0, wav` của FFmpeg. Đây là đường log native, không phải dữ liệu SQL của Trang chủ. Bản đầu của `multimedia.py` bật đường FFmpeg → Qt → Python logging trước khi tạo player/decoder. Bản sửa treo ở đầu báo cáo giữ FFmpeg → Qt nhưng dùng handler native, bỏ callback Python vì có thể khóa chéo GIL. Vẫn tránh `av_log_default_callback` và CRT stderr của FFmpeg. Đối chiếu [mã logger Qt Multimedia](https://github.com/qt/qtmultimedia/blob/dev/src/plugins/multimedia/ffmpeg/qffmpegmediaintegration.cpp) và [cấu hình FFmpeg của Qt](https://doc.qt.io/qt-6.12/advanced-ffmpeg-configuration.html). Ca hồi quy nạp lại player và mở/ghi/checkpoint SQLite 20 lần, mỗi lần kiểm tra integrity, vẫn đạt với bản sửa mới. Kiểm tra chỉ đọc thư viện người dùng trả `ok`; không sửa hoặc tạo lại thư viện đó để xử lý lỗi này.

## Tự động ở mốc Phase 2 ban đầu

24 test đạt với pytest: import trùng và import đồng thời; phiên bản/quan hệ nguồn; trash/restore/xóa vĩnh viễn; không khôi phục nhầm bản đã xóa trước; glossary snapshot; ID JSON sai/thiếu/trùng; model/effort không được thay ngầm; ASR và online streaming thật; phục hồi PCM; lỗi ASR vẫn giữ ghi âm; lỗi dịch vẫn giữ kết quả trước; timeline/TXT và hiệu đính đoạn Việt còn thiếu tạo bản mới, giữ bản cũ; thay đổi thuật ngữ chưa lưu có thể hủy chuyển trang hoặc lưu rồi chuyển. Bốn ca mới kiểm tra trang Cài đặt: giữ model/effort không được hỗ trợ cho tới khi người dùng chọn hợp lệ và lưu, không bịa hạn mức còn thiếu, CPU/theme được lưu và nút backup tạo SQLite thật.

Trang Cài đặt mới bám ảnh assets/mockups/settings-redesign-v1.png đã được người dùng duyệt. scripts/verify_settings.py kiểm tra sáu thẻ không chồng lấn, không cuộn ngang, điều hướng nhóm ở cửa sổ hẹp; có mười ảnh cho năm kích thước × hai theme và tám ảnh hộp thoại chi tiết. Chế độ --live --windows dùng backend Qt Windows và trạng thái/model/quota đọc trực tiếp từ CLI đã cài. Report tại .test-data/settings-approved/validation-live.json. Chế độ fixture ghi rõ dữ liệu minh họa, chỉ dùng để đối chiếu bố cục với ảnh mẫu; không phải dữ liệu hiển thị trong ứng dụng bình thường.

Kiểm tra bố cục native qua 7 trang, 4 kích thước cửa sổ 1440×900 / 1366×768 / 1100×720 / 1024×700, cả Light/Dark, scale 100/125/150/200% trong Qt offscreen: 224 lượt đạt. Kiểm tra chiều rộng rail/context không đổi khi chuyển trang, không có QScrollArea trong context và các field/nút hiển thị nằm trong cột. Đây là kiểm tra hình học Qt; chưa thay cho kiểm tra Windows multi-monitor và DPI động trên phần cứng khác. Ảnh chụp widget thật của bảy trang đã được xem để kiểm tra màu, chữ và sidebar.

## Luồng dữ liệu thật

- File Mandarin WAV chính thức của sherpa-onnx → Silero/SenseVoice → SQLite → Codex CLI đã cài → bản Việt đúng tập ID → hai TXT UTF-8. Không dùng phản hồi dịch giả.
- Codex CLI 0.169.0-alpha.11.1: đã đăng nhập ChatGPT, model/list trả đủ 8 model đã yêu cầu và supportedReasoningEfforts. account/rateLimits/read cung cấp cửa sổ 300 và 10080 phút. UI đọc dữ liệu thật, không tạo giá trị khi thiếu.
- Live: WAV Mandarin đưa vào ranh giới adapter microphone, phía sau dùng capture queue/journal/Streaming Paraformer/Silero/SenseVoice/Codex thật. Có interim, final, bản Việt và WAV đã lưu; mọi event dịch đến sau final tương ứng. Chỉ phần thiết bị đầu vào được thay trong script kiểm tra, không thay recognizer/translator.
- EXE đóng gói đầu: smoke exit 0; ASR/Codex/TXT/restore/SQLite integrity đạt; Qt QAudioDecoder tạo 89.472 mẫu từ fixture WAV, không lỗi codec. Report tại .test-data/frozen-selftest/selftest-report.json.
- Ở mốc ngày 14/11, một bản EXE (SHA-256 e9d2253b839588f548acf818da016e59ddb6dcca13dd54eb28d7615975f074b9) chạy smoke/ASR/Codex/WAV-MP3-M4A/TXT/SQLite thành công; report giữ tại .test-data/prior-frozen/validation.json. Một artifact sau đó bị Smart App Control chặn (WinError 4551), Code Integrity 3077/3033 cho thấy yêu cầu chữ ký. Không sửa chính sách Windows, không thêm chứng thư tự ký; chưa xác định được vì sao policy đánh giá khác nhau giữa các build. Kết quả bản EXE ngày 16/11 được ghi riêng ở đầu báo cáo.
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
