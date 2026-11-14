# Lưu trữ và phục hồi

Thư viện mặc định: %LOCALAPPDATA%/ChineseTranscriber. Tham số --data-dir chọn đường dẫn riêng; --portable đặt data cạnh EXE.

| Thành phần | Vai trò |
|---|---|
| audio/ | File nguồn mang tên SHA-256, lưu một lần |
| recordings/ | Journal PCM và WAV tạm cho phiên đang thu/phục hồi |
| library.sqlite3 | Metadata, transcript, segment, version, glossary, job và settings |
| library.sqlite3-wal / -shm | Cơ chế WAL của SQLite khi đang chạy |
| backups/ | Bản sao lưu SQLite nhất quán |
| models/ | Model người dùng tải, nếu không dùng bộ kèm portable |
| work/ | Thư mục làm việc trống dành cho process dịch Codex |
| application.log | Lỗi ứng dụng; không ghi token đăng nhập |

audio → nhiều transcripts → nhiều segments. audio + transcript → nhiều versions. translations gắn bằng cặp version_id / segment_id; phiên bản giữ model, effort, context và bản chụp glossary.

Xóa mềm dùng deleted timestamp có độ phân giải microsecond để phân nhóm khôi phục. Khôi phục nguồn chỉ khôi phục các phiên bản được xóa cùng nhóm, không tự khôi phục bản đã bị xóa từ trước.

Job có running, complete, failed, interrupted. Khi mở lại, running được đổi thành interrupted, đoạn đang dịch trở về queued; nội dung complete được giữ. Recordings được ghi độc lập với ASR/Codex, flush/fsync định kỳ khoảng một giây. Lỗi điện đột ngột vẫn có thể mất phần chưa fsync; không hứa không mất bất kỳ mẫu cuối nào.

Không đổi tên/xóa file nguồn trong audio bằng tay. Sao lưu hoặc chuyển toàn bộ thư viện khi ứng dụng đã đóng. Backup SQLite không chứa các file audio, cần sao chép cả audio khi muốn bản sao lưu đầy đủ.
