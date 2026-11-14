# Tích hợp Codex CLI

Đã xác minh trực tiếp trên codex-cli 0.169.0-alpha.11.1. Schema JSON của chính bản CLI được sinh bằng công cụ generate-json-schema để đối chiếu; bản đóng gói không phụ thuộc file schema phát triển này.

## Giao thức dùng thật

Ứng dụng chạy codex.exe app-server --listen stdio:// với pipe riêng. Thứ tự: initialize → initialized → model/list. Model ID, nhãn và supportedReasoningEfforts lấy từ kết quả; không suy ra quyền tài khoản từ danh sách tên trong thiết kế.

Trước lượt dịch, ứng dụng đọc lại danh sách và xác minh cặp model/effort. Nó tạo thread ephemeral với sandbox read-only và approvalPolicy never. turn/start truyền model, effort, input và outputSchema theo schema CLI thực tế. Không dùng một cờ --effort tự chế.

JSON yêu cầu danh sách segments có id, vi và note. Chỉ chấp nhận đúng tập ID đã gửi, không trùng/thiếu/thừa, không dịch rỗng. Kết quả được ghép theo ID, không theo vị trí phản hồi. Prompt, glossary và chữ nguồn được bao thành dữ liệu, có chỉ dẫn không thực thi công cụ. Client từ chối yêu cầu công cụ/approval và dừng nếu phát hiện tác vụ công cụ.

## Model và effort

Giữ đủ tám tên trong phần cài đặt: GPT-6.1 Sol, GPT-6 Astra, GPT-6.1 Terra, GPT-6 Sol, GPT-6 Luna, GPT-5.6 Sol, GPT-5.6 Terra, GPT-5.6 Luna. Tên không được server xác nhận có nhãn chưa xác minh/không khả dụng; không thay nó bằng một model khác.

Các mức thực tế có thể nhiều hơn low/medium/high. UI chỉ cho gửi cặp được model/list xác nhận. Chọn mặc định trong Cài đặt, hoặc thiết lập riêng trước khi chạy File/Live.

## Đăng nhập

Ứng dụng dùng codex login status để đọc trạng thái, không đọc token hay nội dung auth.json. Nút Đăng nhập chạy codex login trong một process riêng; browser và xác thực do Codex quản lý. Có hướng dẫn và sao chép lệnh trong giao diện. Có thể dừng chờ đăng nhập bằng Dừng tác vụ.

## Hạn mức

account/rateLimits/read đã trả được các cửa sổ 300 và 10080 phút ở môi trường kiểm tra. Ứng dụng hiển thị phần trăm đã dùng và thời điểm reset thực, đổi tên cửa sổ theo windowDurationMins trả về. Nếu thiếu dữ liệu, chỉ hiển thị chưa thể đọc; không coi là 0% và không tạo quota giả.

Tài liệu chính thức: [App Server](https://learn.chatgpt.com/docs/app-server), [Developer commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli). Cần kiểm tra lại khi đổi phiên bản CLI vì đây là giao diện có thể thay đổi.
