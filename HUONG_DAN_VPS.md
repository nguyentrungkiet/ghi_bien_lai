# 🖥️ HƯỚNG DẪN CẬP NHẬT BOT TRÊN VPS WINDOWS

## 📥 Cập nhật code từ GitHub

### Cách 1: Dùng script tự động (Khuyên dùng)

```powershell
cd C:\ghi_bien_lai
git pull origin main
.\update_vps.bat
```

Script tự động sẽ:
- ✅ Dừng bot cũ
- ✅ Pull code mới
- ✅ Cài đặt thư viện
- ✅ Khởi động bot

---

### Cách 2: Cập nhật thủ công

```powershell
# 1. Dừng bot đang chạy
taskkill /F /IM python.exe

# 2. Di chuyển vào thư mục
cd C:\ghi_bien_lai

# 3. Pull code mới từ GitHub
git pull origin main

# 4. Cài đặt thư viện (nếu có cập nhật)
pip install -r requirements.txt

# 5. Khởi động bot
python telegram_bot_v2.py
```

---

## 🚀 Khởi động bot lần đầu

### Bước 1: Clone code từ GitHub

```powershell
# Di chuyển vào ổ C:
cd C:\

# Clone repository
git clone https://github.com/nguyentrungkiet/ghi_bien_lai.git

# Di chuyển vào thư mục
cd ghi_bien_lai
```

### Bước 2: Cài đặt Python (nếu chưa có)

- Tải Python 3.10+ từ: https://www.python.org/downloads/
- Tick chọn "Add Python to PATH" khi cài đặt

### Bước 3: Cài đặt thư viện

```powershell
cd C:\ghi_bien_lai
pip install -r requirements.txt
```

### Bước 4: Thêm file credentials.json

- Copy file `credentials.json` từ máy local
- Paste vào `C:\ghi_bien_lai\credentials.json`

### Bước 5: Thêm logo (tùy chọn)

- Copy file `logo.jpg` vào `C:\ghi_bien_lai\logo.jpg`

### Bước 6: Chạy bot

```powershell
python telegram_bot_v2.py
```

Hoặc để chạy ngầm (không hiển thị cửa sổ):

```powershell
pythonw telegram_bot_v2.py
```

---

## 🔄 Chạy bot tự động khi khởi động Windows

### Cách 1: Task Scheduler (Khuyên dùng)

1. Mở **Task Scheduler**
2. Click **Create Basic Task**
3. Đặt tên: `Telegram Bot - Biên Lai`
4. Trigger: **When the computer starts**
5. Action: **Start a program**
6. Program/script: `C:\Windows\System32\pythonw.exe`
7. Arguments: `C:\ghi_bien_lai\telegram_bot_v2.py`
8. Start in: `C:\ghi_bien_lai`
9. Finish

### Cách 2: Startup Folder

1. Tạo file `start_bot.bat` với nội dung:

```batch
@echo off
cd C:\ghi_bien_lai
pythonw telegram_bot_v2.py
```

2. Copy file vào: `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp`

---

## ⚙️ Cấu hình biến môi trường (tùy chọn)

Nếu muốn thay đổi học phí mà không sửa code:

```powershell
# Tạo biến môi trường hệ thống
[System.Environment]::SetEnvironmentVariable("HOC_PHI_MOI_THANG", "400000", "Machine")

# Hoặc chỉ cho session hiện tại
$env:HOC_PHI_MOI_THANG="400000"
```

---

## 🐛 Xử lý lỗi thường gặp

### Lỗi: "python is not recognized"

**Nguyên nhân:** Python chưa được thêm vào PATH

**Giải pháp:**
1. Cài lại Python và tick "Add to PATH"
2. Hoặc thêm PATH thủ công: `C:\Users\Administrator\AppData\Local\Programs\Python\Python3XX`

### Lỗi: "No module named telegram"

**Nguyên nhân:** Chưa cài thư viện

**Giải pháp:**
```powershell
pip install -r requirements.txt
```

### Lỗi: "credentials.json not found"

**Nguyên nhân:** Thiếu file credentials Google Sheets

**Giải pháp:**
- Copy file `credentials.json` vào `C:\ghi_bien_lai\`

### Lỗi: RuntimeError asyncio event loop

**Nguyên nhân:** Đã được fix trong phiên bản mới

**Giải pháp:**
```powershell
cd C:\ghi_bien_lai
git pull origin main
python telegram_bot_v2.py
```

---

## 📊 Kiểm tra bot đang chạy

```powershell
# Xem process Python
Get-Process python

# Xem chi tiết
Get-Process python | Format-List *

# Kiểm tra cổng mạng
netstat -ano | findstr python
```

---

## 🛑 Dừng bot

```powershell
# Dừng tất cả Python
taskkill /F /IM python.exe

# Hoặc dừng theo PID
taskkill /F /PID <PID_NUMBER>
```

---

## 📝 Xem log bot

Nếu bot chạy ngầm và cần xem log:

```powershell
# Chạy bot với output vào file
python telegram_bot_v2.py > bot_log.txt 2>&1
```

---

## 🔐 Bảo mật

1. **Không share file `credentials.json`**
2. **Không commit file này lên GitHub**
3. **Đặt mật khẩu cho VPS**
4. **Cập nhật Windows thường xuyên**

---

## 📞 Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra log trong terminal
2. Kiểm tra kết nối internet
3. Kiểm tra Telegram Bot Token còn hiệu lực
4. Kiểm tra Google Sheets credentials
