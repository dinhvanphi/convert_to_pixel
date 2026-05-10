# PNG to Pixel Art Converter

Dự án này giúp chuyển đổi các hình ảnh (PNG, JPG) thành dữ liệu Pixel Art (file JSON) kèm theo một giao diện Web đơn giản để thao tác và xem trước kết quả.

## 🛠 Yêu cầu hệ thống
- Máy tính đã cài đặt sẵn **Python 3** (khuyên dùng Python 3.9 trở lên).
- Trình duyệt web (Chrome, Safari, Edge...).

## 🚀 Hướng dẫn cài đặt và chạy dự án

### Bước 1: Cài đặt thư viện
Mở Terminal (trên Mac/Linux) hoặc Command Prompt/PowerShell (trên Windows) và trỏ đến thư mục chứa dự án này. Chạy lệnh sau để cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```
*(Nếu bạn dùng Mac/Linux và lệnh pip không hoạt động, hãy thử dùng `pip3 install -r requirements.txt`)*

### Bước 2: Khởi chạy Server
Sau khi cài đặt xong thư viện, chạy lệnh sau để khởi động Web Server:

```bash
python server.py
```
*(Nếu bạn dùng Mac/Linux, hãy thử dùng `python3 server.py`)*

### Bước 3: Mở giao diện Web
Sau khi chạy lệnh trên, Terminal sẽ hiện ra thông báo:
`🚀 Server running at http://localhost:8080/web_ui/index.html`

Bạn chỉ cần click vào đường link đó, hoặc mở trình duyệt lên và truy cập vào địa chỉ:
👉 **[http://localhost:8080/web_ui/index.html](http://localhost:8080/web_ui/index.html)**
