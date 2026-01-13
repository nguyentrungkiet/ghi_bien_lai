# 🚀 HƯỚNG DẪN DEPLOY BOT LÊN VPS

## Bước 1: Chuẩn bị VPS

### 1.1. Yêu cầu tối thiểu
- **OS:** Ubuntu 20.04/22.04 hoặc CentOS 7/8
- **RAM:** 512MB (khuyên dùng 1GB)
- **Disk:** 10GB
- **Python:** 3.8+

### 1.2. SSH vào VPS
```bash
ssh root@VPS_IP
# hoặc
ssh username@VPS_IP
```

## Bước 2: Cài đặt môi trường

### 2.1. Update hệ thống
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS
sudo yum update -y
```

### 2.2. Cài Python và các công cụ cần thiết
```bash
# Ubuntu/Debian
sudo apt install -y python3 python3-pip git

# CentOS
sudo yum install -y python3 python3-pip git
```

### 2.3. Cài đặt thư viện hệ thống cho ReportLab
```bash
# Ubuntu/Debian
sudo apt install -y python3-dev libjpeg-dev zlib1g-dev

# CentOS
sudo yum install -y python3-devel libjpeg-devel zlib-devel
```

## Bước 3: Setup Git và GitHub

### 3.1. Upload code lên GitHub (trên máy Windows)

**Cách 1: Dùng GitHub Desktop**
1. Tải GitHub Desktop: https://desktop.github.com
2. Đăng nhập GitHub
3. Click "File" → "New Repository"
   - Name: `bien-lai-bot`
   - Local Path: `D:\SourceCode\in biên lai`
4. Click "Create Repository"
5. Click "Publish repository"

**Cách 2: Dùng Git command (PowerShell)**
```powershell
cd "D:\SourceCode\in biên lai"
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/USERNAME/bien-lai-bot.git
git push -u origin main
```

### 3.2. Clone code từ GitHub lên VPS
```bash
# SSH vào VPS
cd ~
git clone https://github.com/USERNAME/bien-lai-bot.git
cd bien-lai-bot
```

## Bước 4: Cài đặt dependencies

```bash
cd ~/bien-lai-bot
pip3 install -r requirements.txt
```

## Bước 5: Upload Logo lên VPS

**Cách 1: Dùng SCP (trên Windows PowerShell)**
```powershell
scp "D:\SourceCode\in biên lai\logo.jpg" username@VPS_IP:~/bien-lai-bot/
```

**Cách 2: Dùng WinSCP hoặc FileZilla**
- Tải WinSCP: https://winscp.net
- Connect vào VPS
- Upload file `logo.jpg` vào folder `~/bien-lai-bot/`

**Cách 3: Upload cùng Git**
```powershell
# Trên Windows
cd "D:\SourceCode\in biên lai"
git add logo.jpg
git commit -m "Add logo"
git push
```
```bash
# Trên VPS
cd ~/bien-lai-bot
git pull
```

## Bước 6: Chạy Bot

### 6.1. Test chạy thử
```bash
cd ~/bien-lai-bot
python3 telegram_bot.py
```

Nhấn `Ctrl+C` để dừng.

### 6.2. Chạy bot dưới nền với Screen
```bash
# Cài screen
sudo apt install screen -y  # Ubuntu
sudo yum install screen -y  # CentOS

# Tạo session
screen -S telegram-bot

# Chạy bot
cd ~/bien-lai-bot
python3 telegram_bot.py

# Nhấn Ctrl+A, sau đó nhấn D để detach
# Bot sẽ tiếp tục chạy dưới nền
```

**Các lệnh screen hữu ích:**
```bash
screen -ls                    # Xem danh sách session
screen -r telegram-bot        # Attach lại session
screen -X -S telegram-bot quit  # Dừng session
```

### 6.3. Chạy bot với systemd (khuyên dùng)

Tạo file service:
```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

Nội dung:
```ini
[Unit]
Description=Telegram Bot Bien Lai
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/bien-lai-bot
ExecStart=/usr/bin/python3 /root/bien-lai-bot/telegram_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Lưu file (Ctrl+O, Enter, Ctrl+X).

Kích hoạt service:
```bash
sudo systemctl daemon-reload
sudo systemctl start telegram-bot
sudo systemctl enable telegram-bot
sudo systemctl status telegram-bot
```

**Các lệnh quản lý service:**
```bash
sudo systemctl start telegram-bot    # Khởi động
sudo systemctl stop telegram-bot     # Dừng
sudo systemctl restart telegram-bot  # Restart
sudo systemctl status telegram-bot   # Xem trạng thái
sudo journalctl -u telegram-bot -f   # Xem log
```

## Bước 7: Workflow Update Code

### 7.1. Trên máy Windows (Local)

```powershell
cd "D:\SourceCode\in biên lai"

# Sửa code...

# Commit và push
git add .
git commit -m "Update: mô tả thay đổi"
git push origin main
```

### 7.2. Trên VPS

**Cách 1: Update thủ công**
```bash
# SSH vào VPS
ssh username@VPS_IP

cd ~/bien-lai-bot
git pull origin main

# Restart bot
sudo systemctl restart telegram-bot
```

**Cách 2: Tạo script tự động**
```bash
nano ~/update-bot.sh
```

Nội dung:
```bash
#!/bin/bash
cd ~/bien-lai-bot
git pull origin main
sudo systemctl restart telegram-bot
echo "Bot updated successfully!"
```

Cho phép thực thi:
```bash
chmod +x ~/update-bot.sh
```

Sau này chỉ cần chạy:
```bash
~/update-bot.sh
```

**Cách 3: Auto-update với cron (nâng cao)**
```bash
# Mở crontab
crontab -e

# Thêm dòng này để auto-update mỗi 5 phút
*/5 * * * * cd ~/bien-lai-bot && git pull origin main && systemctl restart telegram-bot
```

## Bước 8: Kiểm tra và Debug

### 8.1. Xem log realtime
```bash
# Với systemd
sudo journalctl -u telegram-bot -f

# Với screen
screen -r telegram-bot
```

### 8.2. Kiểm tra bot có chạy không
```bash
ps aux | grep telegram_bot.py
```

### 8.3. Xem port đang dùng
```bash
netstat -tulpn | grep python
```

## Bước 9: Bảo mật

### 9.1. Tạo user riêng (không dùng root)
```bash
sudo adduser botuser
sudo usermod -aG sudo botuser
su - botuser
```

### 9.2. Setup SSH key
```powershell
# Trên Windows
ssh-keygen -t ed25519 -C "your_email@example.com"
type $env:USERPROFILE\.ssh\id_ed25519.pub
```

```bash
# Trên VPS
mkdir -p ~/.ssh
nano ~/.ssh/authorized_keys
# Paste public key vào
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### 9.3. Disable password login (sau khi test SSH key)
```bash
sudo nano /etc/ssh/sshd_config
# Sửa: PasswordAuthentication no
sudo systemctl restart sshd
```

## Troubleshooting

### Lỗi: Module not found
```bash
pip3 install -r requirements.txt --upgrade
```

### Lỗi: Permission denied
```bash
sudo chmod +x telegram_bot.py
sudo chown -R $USER:$USER ~/bien-lai-bot
```

### Lỗi: Bot không trả lời
```bash
# Kiểm tra log
sudo journalctl -u telegram-bot -n 50

# Kiểm tra token
cat telegram_bot.py | grep BOT_TOKEN
```

### Lỗi: Logo không tìm thấy
```bash
# Kiểm tra file tồn tại
ls -la ~/bien-lai-bot/logo.jpg

# Update đường dẫn trong telegram_bot.py
LOGO_PATH = "/root/bien-lai-bot/logo.jpg"  # Đường dẫn tuyệt đối
```

## Tóm tắt Workflow Hàng ngày

```
┌─────────────┐
│ Local (Win) │
│  Sửa code   │
└──────┬──────┘
       │
       │ git push
       ▼
┌─────────────┐
│   GitHub    │
│  Repository │
└──────┬──────┘
       │
       │ git pull
       ▼
┌─────────────┐
│     VPS     │
│  Restart    │
└─────────────┘
```

**Lệnh nhanh:**
```bash
# Local
git add . && git commit -m "update" && git push

# VPS (hoặc dùng script)
ssh user@vps "cd ~/bien-lai-bot && git pull && sudo systemctl restart telegram-bot"
```

## Lưu ý quan trọng

1. ⚠️ **Không commit token:** Tạo file `.gitignore` và thêm `config_bot.py` nếu chứa token
2. 🔒 **Backup thường xuyên:** `git push` là một dạng backup
3. 📊 **Monitor bot:** Cài `htop` để theo dõi: `sudo apt install htop`
4. 🔄 **Update Python packages:** `pip3 list --outdated` để kiểm tra
5. 💾 **Disk space:** Kiểm tra bằng `df -h`

## Liên hệ & Hỗ trợ

- Nếu có lỗi, xem log: `sudo journalctl -u telegram-bot -n 100`
- Test bot local trước khi push lên VPS
- Giữ một backup code ở local

---
**Chúc bạn deploy thành công! 🎉**
