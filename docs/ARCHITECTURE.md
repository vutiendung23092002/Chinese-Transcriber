# Kiến trúc ứng dụng

## Thành phần

- app.py: entry point, khóa một cửa sổ cho mỗi thư viện, logging, backup, chế độ portable và kiểm tra runtime.
- window.py / widgets.py / theme.py: shell PySide6, rail vẽ bằng QPainterPath, cột tác vụ cố định, theme và icon SVG. Không có trình duyệt nhúng.
- workspace.py: các trang native, điều phối tác vụ, timeline, playback, hiệu đính, glossary, thư viện và xác nhận xóa.
- settings_page.py: trang Cài đặt theo ảnh đã duyệt; sáu thẻ native, điều hướng nhóm, hạn mức thật, chọn model/effort, xem trước theme và hộp thoại cấu hình nâng cao. Không ghi đè lựa chọn mặc định trước khi nhấn Lưu.
- storage.py: SQLite, transaction, SHA-256, quan hệ nguồn/transcript/phiên bản, job và backup.
- audio.py: FFmpeg CPU, giải mã theo luồng mono 16 kHz, timestamp và xuất TXT nguyên tử.
- models.py / asr.py: tải/kiểm tra model, Silero VAD, SenseVoiceSmall và Streaming Paraformer.
- pipeline.py: điều phối chép lời file và dịch song song; hàng đợi bền trong SQLite, dừng/tiếp tục cùng transcript và version.
- recording.py: journal PCM, hàng đợi ghi riêng, ASR riêng, dịch riêng và phục hồi sau sự cố.
- microphone.py: nhận diện mic theo tên/trình điều khiển, tìm lại index trước khi mở và đo PCM gốc/cảnh báo tín hiệu; không lọc, khuếch đại hay sửa mẫu.
- codex.py: stdio JSON-RPC chính thức, xác minh model/effort, structured output, kiểm tra ID, retry và dừng.

## Luồng dữ liệu

Import → kiểm tra âm thanh → copy/hash tạm → đổi tên nguyên tử → transaction audio.

File ASR → FFmpeg đọc từng khối → Silero VAD xác định ranh giới mẫu → SenseVoice INT8 → transaction lưu segment và bản ghi hàng đợi dịch. Một thread riêng lấy các đoạn sẵn có để gửi Codex, tối đa 6 đoạn/lượt; producer ASR không chờ mạng. Chưa kết nối Codex vẫn dùng luồng chép lời cục bộ cũ.

Live → microphone PCM 16 kHz → hàng đợi ghi → journal flush/fsync định kỳ. Một nhánh đưa sang Paraformer cho interim và VAD/SenseVoice cho final; chỉ final được đưa sang hàng đợi Codex. Nếu ASR chậm/hỏng, ghi âm vẫn tiếp tục; cần chạy lại chép lời từ nguồn đã lưu để có đầy đủ kết quả.

Codex → kiểm tra quyền model/effort → dịch batch 6 đoạn (live: từng đoạn đã chốt) → xác thực schema/ID toàn batch → lưu các đoạn thành công → cập nhật phiên bản. Không tự thay model khi lỗi. Retry tối đa 3 lần với backoff.

## Tính nhất quán

SQLite bật foreign_keys, WAL và synchronous=FULL. Transaction ghi dùng BEGIN IMMEDIATE và lock nội bộ; một process giữ QLockFile cho mỗi thư viện. Kết quả đã hoàn tất được ghi trước khi job báo complete. Việc hủy giữ nguyên những phần đã lưu.

Tác vụ ghép dùng một job `transcribe_translate`, giữ snapshot model/effort/context/glossary trong version. Đoạn Trung và mục chờ dịch được ghi cùng transaction; khôi phục bổ sung mục chờ bị thiếu mà không ghi đè kết quả. Consumer đọc cờ producer hoàn tất trước khi chụp hàng đợi để không bỏ sót đoạn cuối trong race kết thúc. Lỗi dịch không hủy ASR. Coordinator chỉ kết thúc sau khi consumer dừng; UI không join thread. Khi tiếp tục ASR, VAD được chạy lại từ nguồn để giữ ranh giới và bỏ qua nhận dạng các đoạn đến mốc cuối đã lưu. Timer UI gộp cập nhật bảng tối đa khoảng 10 lần/giây.

Nguồn dùng tên SHA-256; nhiều transcript và version trỏ về một audio. Tệp import được fsync trước os.replace. Lỗi commit sau rename có thể để lại file mồ côi; không tạo record đang hoạt động trỏ tới file đã xóa. Không tự xóa file mồ côi.

Purge nguồn chỉ được thực hiện khi nguồn đã ở Thùng rác và không có version đang hoạt động. Metadata được commit xóa trước khi unlink nguồn; sự cố có thể để lại file mồ côi thay vì làm hỏng một record còn hoạt động. Các thao tác UI bị chặn khi đang có tác vụ dùng nguồn.

## Giới hạn chủ đích

Timestamp là ranh giới đoạn giọng nói theo sample/VAD, không phải căn chỉnh từng từ. Paraformer ở bộ được dùng không cung cấp timestamp. Một đoạn lời nói có thể gồm nhiều mệnh đề hoặc câu nếu người nói không nghỉ; không chia thời gian bằng cách chia đều số chữ.

Benchmark hiện là đo hiệu năng trên PC phát triển, không là đánh giá CER/WER học thuật hoặc bảo đảm độ chính xác. Người học có thể nghe lại, sửa và lưu phiên bản mới.
