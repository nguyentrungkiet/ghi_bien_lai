# 🤖 Bot Telegram In Biên Lai Học Phí

Bot Telegram tự động tạo và gửi biên lai học phí PDF chỉ bằng một tin nhắn đơn giản!

## ✨ Tính năng

- 📝 Nhập thông tin siêu ngắn gọn: `Nguyễn Văn A lớp 7 tháng 1 400k`
- 📄 Tự động tạo PDF biên lai chuyên nghiệp
- 🇻🇳 Hỗ trợ font tiếng Việt hoàn hảo
- 🖼️ Tích hợp logo trường học
- 📅 Tự động lấy ngày đóng tiền
- 💰 Hỗ trợ nhiều đơn vị: k (nghìn), tr (triệu)
- 📊 Đóng nhiều tháng cùng lúc: `tháng 1+2+3`

## 🚀 Sử dụng

Gửi tin nhắn cho bot theo một trong các cách sau:

**Cách 1: Siêu ngắn**
```
Huỳnh Trân lớp 8 tháng 7 400k
```

**Cách 2: Nhiều tháng với dấu +**
```
Nguyễn Văn A lớp 7 tháng 1+2+3 1200k
```

**Cách 3: Đầy đủ**
```
Họ tên: Nguyễn Văn A
Lớp: 7A
Tháng: 01/2026, 02/2026
Học phí: 1500000
```

Bot sẽ tự động gửi lại file PDF biên lai!

## 🛠️ Cài đặt Local

### Yêu cầu
- Python 3.8+
- Token bot từ @BotFather

### Các bước

1. Clone repository
```bash
git clone https://github.com/USERNAME/bien-lai-bot.git
cd bien-lai-bot
```

2. Cài đặt thư viện
```bash
pip install -r requirements.txt
```

3. Cấu hình token
```bash
# Windows
$env:TELEGRAM_BOT_TOKEN="YOUR_TOKEN_HERE"

# Linux/Mac
export TELEGRAM_BOT_TOKEN="YOUR_TOKEN_HERE"
```

4. Chạy bot
```bash
python telegram_bot.py
```

## ☁️ Deploy lên Cloud

Xem hướng dẫn chi tiết trong [DEPLOY_RENDER.md](DEPLOY_RENDER.md)

**Tóm tắt:**
1. Push code lên GitHub
2. Tạo tài khoản Render.com
3. Tạo Background Worker từ repo
4. Thêm biến môi trường `TELEGRAM_BOT_TOKEN`
5. Deploy!

Bot sẽ chạy 24/7 miễn phí trên cloud.

## 📝 Cấu trúc Project

```
├── telegram_bot.py          # Bot chính
├── requirements.txt         # Python dependencies
├── runtime.txt             # Python version cho Render
├── start.sh                # Script khởi động
├── logo.jpg                # Logo trường học
├── DEPLOY_RENDER.md        # Hướng dẫn deploy
└── README.md               # File này
```

## 🎨 Tùy chỉnh

### Thay đổi Logo
- Thay file `logo.jpg` bằng logo của bạn
- Hoặc set biến môi trường `LOGO_PATH` với URL logo

### Thay đổi định dạng biên lai
Chỉnh sửa hàm `tao_bien_lai_pdf()` trong `telegram_bot.py`

## 🐛 Troubleshooting

**Bot không phản hồi:**
- Kiểm tra token có đúng không
- Kiểm tra bot có đang chạy không

**Font tiếng Việt bị lỗi:**
- Trên Windows: Tự động dùng Arial
- Trên Linux/Cloud: Tự động dùng DejaVu Sans
- Fallback: Helvetica

**Logo không hiển thị:**
- Kiểm tra file `logo.jpg` có tồn tại không
- Hoặc dùng URL logo

## 📄 License

MIT License - Tự do sử dụng và chỉnh sửa

## 💖 Credits

Made with ❤️ for schools and parents
