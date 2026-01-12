# 🤖 HƯỚNG DẪN SETUP BOT TELEGRAM

Bot Telegram giúp tạo biên lai học phí tự động, chỉ cần chat là có PDF ngay!

## 📋 Bước 1: Tạo Bot trên Telegram

1. Mở Telegram, tìm kiếm `@BotFather`
2. Gửi lệnh `/newbot`
3. Đặt tên bot: `Biên Lai Học Phí Bot` (hoặc tên khác bạn thích)
4. Đặt username bot: `bienlai_hocphi_bot` (phải kết thúc bằng `_bot` hoặc `Bot`)
5. BotFather sẽ gửi cho bạn TOKEN, giống như: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
6. **Copy token này!**

## 🔧 Bước 2: Cấu hình Bot

### Cách 1: Sửa file config
Mở file `config_bot.py` và dán token vào:
```python
TELEGRAM_BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
```

### Cách 2: Dùng biến môi trường (khuyên dùng)
```bash
# Windows PowerShell
$env:TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"

# Windows CMD
set TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### (Tùy chọn) Thêm logo và dấu mộc
Trong file `telegram_bot.py`, sửa dòng:
```python
LOGO_PATH = r"d:\logo.png"  # Đường dẫn logo của bạn
DAM_MOC_PATH = r"d:\dau_moc.png"  # Đường dẫn dấu mộc của bạn
```

## 📦 Bước 3: Cài đặt thư viện

```bash
pip install -r requirements_bot.txt
```

Hoặc:
```bash
pip install python-telegram-bot reportlab pillow
```

## 🚀 Bước 4: Chạy Bot

```bash
python telegram_bot.py
```

Nếu thành công, bạn sẽ thấy:
```
🤖 Bot đang chạy...
📱 Hãy mở Telegram và chat với bot!
```

## 💬 Bước 5: Sử dụng Bot

### Mở Telegram và tìm bot của bạn
Tìm username bot bạn đã tạo (ví dụ: `@bienlai_hocphi_bot`)

### Gửi lệnh /start
Bot sẽ hướng dẫn chi tiết

### Gửi thông tin học sinh

**Cách 1: Ngắn gọn (khuyên dùng)**
```
Nguyễn Văn A, 7A, 01/2026, 1500000
```

**Cách 2: Đầy đủ**
```
Họ tên: Nguyễn Văn A
Lớp: 7A
Tháng: 01/2026
Học phí: 1500000
```

**Nhiều tháng:**
```
Nguyễn Văn A, 7A, 01/2026, 02/2026, 03/2026, 4500000
```

### Nhận file PDF
Bot sẽ tự động tạo và gửi file PDF biên lai cho bạn!

## 📝 Ví dụ

**Input:**
```
Trần Thị B, 8B, 01/2026, 02/2026, 3000000
```

**Output:**
- File PDF: `BienLai_Tran_Thi_B_012026_022026.pdf`
- Hiển thị đầy đủ thông tin với font tiếng Việt
- Logo và dấu mộc (nếu đã cấu hình)

## ⚙️ Các lệnh Bot

- `/start` - Bắt đầu và xem hướng dẫn
- `/help` - Xem hướng dẫn sử dụng

## 🔒 Bảo mật

- **KHÔNG** chia sẻ TOKEN của bot với ai
- TOKEN giống như mật khẩu để điều khiển bot
- Nếu bị lộ TOKEN, vào @BotFather và dùng `/revoke` để tạo token mới

## 🛠️ Troubleshooting

### Lỗi: "CHƯA CẤU HÌNH BOT TOKEN"
→ Bạn chưa điền TOKEN. Xem lại Bước 2.

### Lỗi: "Invalid token"
→ TOKEN sai hoặc chưa đúng định dạng. Kiểm tra lại token từ BotFather.

### Bot không phản hồi
→ Kiểm tra bot có đang chạy không? Xem terminal có báo lỗi không?

### Font tiếng Việt bị lỗi
→ Kiểm tra có font Arial trong `C:\Windows\Fonts\` không.

## 💡 Tips

- Giữ cửa sổ terminal mở để bot tiếp tục hoạt động
- Bot sẽ dừng nếu bạn đóng terminal
- Muốn bot chạy 24/7, cần deploy lên server (Heroku, Railway, VPS...)
- File PDF được tạo tạm và tự động xóa sau khi gửi

## 🌟 Tính năng

✅ Nhận thông tin qua chat
✅ Tự động tạo PDF với font tiếng Việt
✅ Hỗ trợ nhiều tháng cùng lúc
✅ Tự động đặt tên file theo học sinh
✅ Gửi file PDF trực tiếp qua Telegram
✅ Không cần lưu trữ, file tự động xóa

## 🆘 Hỗ trợ

Nếu gặp vấn đề, kiểm tra:
1. Token có đúng không?
2. Thư viện đã cài đầy đủ chưa?
3. Bot có đang chạy không?
4. Định dạng tin nhắn có đúng không?
