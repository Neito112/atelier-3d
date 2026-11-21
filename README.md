# Atelier 3D

[**Mở Atelier 3D**](https://neito112.github.io/atelier-3d/)

Nhập yêu cầu thiết kế và theo dõi phần mềm 3D dựng cảnh, chiếu sáng và render trên máy của bạn.

## Bắt đầu

1. Trong app, chọn **Blender → Tải bộ cài** để lấy `atelier_3d_blender.zip`.
2. Trong Blender 4.3+, mở **Edit → Preferences → Add-ons → Install from Disk**. Chọn tệp ZIP và bật **Atelier 3D Gateway**.
3. Trong cửa sổ 3D Viewport, nhấn **N**, mở tab **Atelier 3D** và bấm **Start gateway and open app**. App nhận mã kết nối của phiên này. Chọn **Kiểm tra kết nối** để xác nhận. Nếu trình duyệt hạn chế truy cập mạng nội bộ từ GitHub Pages, bấm **Open local app** trong Blender.
4. Bấm **Chạy cảnh mẫu Blender** để thử mà không cần tài khoản AI. Hoặc kết nối ChatGPT/chọn nhà cung cấp khác, nhập yêu cầu, rồi bấm **Dựng và render**.

Blender chạy trong một tiến trình nền. App hiển thị tiến độ, bản xem trước và ảnh cuối, đồng thời cung cấp nút tải `scene.blend` và `render.png`. Tiện ích lưu kết quả trong `Atelier 3D/outputs` ở thư mục người dùng. Mỗi lần chạy tạo một cảnh mới.

## Kết nối ChatGPT

1. Cài [Codex CLI chính thức](https://developers.openai.com/codex/cli), sau đó khởi động lại gateway. Có thể đặt `ATELIER_CODEX_BIN` nếu Blender hoặc gateway không tìm được lệnh `codex`.
2. Bấm **Kết nối ChatGPT**, rồi xác nhận tài khoản đang đăng nhập trên trang OpenAI vừa mở. Atelier sử dụng hồ sơ Codex riêng ở `~/.atelier-3d/codex`.
3. App hiển thị phần trăm **hạn mức Codex còn lại**, theo từng khoảng thời gian và thời điểm đặt lại nếu máy chủ cung cấp. Dùng **Làm mới hạn mức** để đọc lại.

ChatGPT chạy qua Codex App Server trên máy. Quyền xác thực nằm ở hồ sơ cục bộ. ChatGPT chỉ chuyển yêu cầu thành dữ liệu dựng hình; gateway xác thực dữ liệu và Blender thực thi bộ thao tác dựng cảnh.

## Nhà cung cấp AI khác

Mở nhóm **Nhà cung cấp AI khác**. Nhập mã model và API key hoặc đặt các biến môi trường bên dưới. Với API tương thích, nhập URL gốc trực tiếp trong app hoặc đặt biến cho gateway.

| Nhà cung cấp | Cấu hình gateway |
| --- | --- |
| OpenAI | `ATELIER_OPENAI_KEY` |
| Anthropic Claude | `ATELIER_ANTHROPIC_KEY` |
| API tương thích Anthropic Messages | `ATELIER_ANTHROPIC_COMPATIBLE_KEY`, `ATELIER_ANTHROPIC_COMPATIBLE_URL` |
| Google Gemini | `ATELIER_GEMINI_KEY` |
| OpenRouter | `ATELIER_OPENROUTER_KEY` |
| API tương thích OpenAI | `ATELIER_COMPATIBLE_KEY`, `ATELIER_COMPATIBLE_URL` |

API tương thích Anthropic nhận URL gốc như `https://api.example.com/v1` hoặc URL đầy đủ kết thúc bằng `/messages`. Gateway dùng định dạng Anthropic Messages và header `x-api-key` nếu có khóa. API key nhập trong giao diện giữ trong phiên trang, được gateway gửi đến đúng nhà cung cấp đã chọn.

## SketchUp, 3ds Max và phần mềm khác

1. Chọn phần mềm, bấm **Tải bộ cài** và giải nén gói gateway dùng chung. Trên Windows, chạy `start_gateway.cmd` với Python 3.10+ đã cài. Trên macOS/Linux, chạy `python3 bridge.py --open`.
2. Mở máy chủ MCP Streamable HTTP riêng của phần mềm. Dùng một máy chủ tin cậy hỗ trợ các chức năng dựng hình hoặc render cần thiết. Sau đó chọn phần mềm trên app, điền URL và bấm **Kiểm tra kết nối**.
3. Chọn các công cụ MCP cho phép chạy sau khi gửi yêu cầu. Nếu máy chủ gửi sự kiện tiến độ trong luồng POST và trả ảnh trong nội dung công cụ, app hiển thị tiến độ và ảnh.

Máy chủ ngoài cần CORS cho nguồn trang, gồm các header `Content-Type`, `Authorization`, `MCP-Protocol-Version`, `Mcp-Session-Id` và expose `Mcp-Session-Id` nếu có phiên. Gói gateway dành cho phần mềm ngoài chạy độc lập. SketchUp, 3ds Max và Corona cần bộ kết nối MCP phù hợp được cài riêng.

## Chạy và đóng gói từ mã nguồn

- Chạy `python3 bridge.py --open` để mở gateway cục bộ. Có thể truyền `--blender` kèm đường dẫn Blender.
- Sau khi sửa `index.html`, `bridge.py`, `chatgpt.py` hoặc nội dung tiện ích, chạy `python3 package_installers.py` để cập nhật tệp `installers.js`.
- Khi lưu trữ app ở một kho GitHub khác, cập nhật URL công khai trong nguồn và cấu hình nguồn CORS phù hợp. Triển khai GitHub Pages từ nhánh `main`, thư mục gốc.
