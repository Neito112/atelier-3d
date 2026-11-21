# Atelier 3D

Ứng dụng web tiếng Việt để lập kế hoạch bằng LLM và thực thi thao tác dựng hình, chiếu sáng, đặt camera và render trên máy làm việc qua MCP.

## Bắt đầu

1. Tải hai tệp `bridge.py` và `index.html` về cùng một thư mục. Máy làm việc cần Python 3.10+ và Blender. Trên Windows, mở PowerShell ở thư mục đó và chạy:

   ```powershell
   py bridge.py --blender "C:\Program Files\Blender Foundation\Blender 4.3\blender.exe"
   ```

   Thay đường dẫn bằng vị trí Blender thực tế. Nếu lệnh `blender` đã có trong PATH, chạy `py bridge.py` trên Windows hoặc `python3 bridge.py` trên macOS/Linux.

2. Mở [Atelier 3D trên GitHub Pages](https://neito112.github.io/atelier-3d/) và nhập mã ghép nối in trong cửa sổ bridge. Nếu trình duyệt chặn truy cập mạng nội bộ, mở ứng dụng từ bridge tại [127.0.0.1:8765](http://127.0.0.1:8765). Giữ cửa sổ bridge đang chạy.
3. Chọn **Nạp cảnh mẫu Blender**, xem các bước và bấm **Duyệt và chạy**. Luồng mẫu chạy không cần API key. Kết quả gồm `scene.blend` và `render.png`, nằm trong `outputs/<mã tác vụ>/` trên máy làm việc.
4. Để dùng AI, chọn nhà cung cấp, điền mã model và API key, nhập yêu cầu rồi chọn **Tạo kế hoạch bằng AI**. Kiểm tra JSON, sau đó bấm **Duyệt và chạy**. Mỗi tác vụ Blender tạo cảnh mới trong một tiến trình độc lập.

### Nhà cung cấp LLM

| Nhà cung cấp | Biến môi trường để dùng thay ô API key |
| --- | --- |
| OpenAI | `ATELIER_OPENAI_KEY` |
| Anthropic Claude | `ATELIER_ANTHROPIC_KEY` |
| Google Gemini | `ATELIER_GEMINI_KEY` |
| OpenRouter | `ATELIER_OPENROUTER_KEY` |
| API tương thích OpenAI, ví dụ Ollama | `ATELIER_COMPATIBLE_KEY` khi máy chủ yêu cầu và `ATELIER_COMPATIBLE_URL`, ví dụ `http://127.0.0.1:11434/v1` |

Bridge gửi yêu cầu và lược đồ công cụ đã chọn đến nhà cung cấp LLM. API key nhập trong ứng dụng chỉ giữ trong phiên trang và được gửi qua bridge đến nhà cung cấp đã chọn. Kế hoạch Blender là dữ liệu JSON đã kiểm tra, chạy bằng bộ thao tác có sẵn. API key và tệp đầu ra không cần đưa lên GitHub.

### SketchUp, 3ds Max và phần mềm khác

Cài và chạy máy chủ MCP của phần mềm đích, rồi điền URL Streamable HTTP và mã Bearer nếu cần. Máy chủ phải cho phép nguồn trang ứng dụng bằng CORS, bao gồm các header yêu cầu `Content-Type`, `Authorization`, `MCP-Protocol-Version`, `Mcp-Session-Id` và phải expose `Mcp-Session-Id` nếu có phiên. Sau khi nạp danh sách, đánh dấu các công cụ muốn dùng để lập kế hoạch. Có thể nhập trực tiếp JSON các bước rồi bấm **Duyệt và chạy**.

Kết nối này thực thi công cụ do máy chủ đích cung cấp. SketchUp, 3ds Max và Corona cần bộ kết nối riêng có đúng công cụ dựng và render. Phiên đầu hỗ trợ MCP Streamable HTTP, phản hồi JSON hoặc SSE của yêu cầu POST. Máy chủ chỉ có stdio hoặc HTTP+SSE đời cũ cần cổng chuyển đổi tương thích. Kết quả của máy chủ ngoài hiển thị dưới dạng phản hồi MCP. Khi một bước ngoài lỗi, ứng dụng dừng ở bước đó. Các bước đã chạy có thể đã thay đổi cảnh.

### Chạy ở kho GitHub khác

Trong **Settings → Pages**, chọn **Deploy from a branch → main → / (root)**. Chạy bridge với `--origin https://<tài-khoản>.github.io` nếu dùng tên miền tài khoản khác. GitHub Pages phục vụ giao diện tĩnh. Máy làm việc chạy Blender và giữ các tệp kết quả. MCP Blender tích hợp có địa chỉ `http://127.0.0.1:8765/mcp` và yêu cầu mã ghép nối dưới dạng Bearer token.
