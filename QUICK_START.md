# 🚀 HƯỚNG DẪN NHANH - 5 PHÚT DEPLOY LÊN RENDER.COM

## Bước 1️⃣: Upload code lên GitHub (2 phút)

### Dùng GitHub Desktop (dễ nhất):
1. Tải: https://desktop.github.com
2. Mở GitHub Desktop → "File" → "Add Local Repository"
3. Chọn thư mục: `D:\SourceCode\in biên lai`
4. Click "Publish repository" → Bỏ tick "Private" → "Publish"

✅ Xong! Code đã lên GitHub

## Bước 2️⃣: Deploy trên Render.com (3 phút)

1. **Truy cập:** https://render.com → Sign up with GitHub
2. **Tạo service:** Dashboard → "New" → "Background Worker"
3. **Chọn repo:** `bien-lai-bot` (hoặc tên bạn đặt)
4. **Cấu hình:**
   - Name: `bien-lai-bot`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python telegram_bot.py`
5. **Thêm Environment Variable:**
   - Key: `TELEGRAM_BOT_TOKEN`
   - Value: `8426267636:AAH4VFrILZ_A3vKMzDuzmGFkZbNJ4QZDjTs`
6. **Thêm logo (tùy chọn):**
   - Key: `LOGO_PATH`
   - Value: `logo.jpg`
7. **Click:** "Create Background Worker"

✅ Xong! Đợi 2-3 phút deploy

## Bước 3️⃣: Test Bot

1. Mở Telegram
2. Tìm bot của bạn
3. Gửi: `Nguyễn Văn A lớp 7 tháng 1 400k`
4. Nhận file PDF!

## 🎉 Hoàn tất!

Bot đã chạy 24/7 trên cloud miễn phí!

## ⚠️ Nếu logo không hiển thị:

**Cách 1: Upload logo lên GitHub**
1. Vào repo trên GitHub
2. Upload file `logo.jpg`
3. Click vào file → "Raw" → Copy URL
4. Trong Render → Environment → Edit `LOGO_PATH`
5. Paste URL vào: `https://raw.githubusercontent.com/USERNAME/bien-lai-bot/main/logo.jpg`
6. Restart service

**Cách 2: Bỏ logo**
1. Xóa biến `LOGO_PATH` trong Render
2. Restart service

## 📝 Cập nhật code sau này:

```bash
# Sửa code trên máy
# Sau đó:
git add .
git commit -m "Update"
git push
```

Render tự động deploy lại!

## 🆘 Troubleshooting:

**Bot không chạy:**
- Vào Render → Logs → Xem lỗi gì
- Kiểm tra TOKEN đã đúng chưa

**Lỗi build:**
- Kiểm tra file `requirements.txt` có đúng không
- Restart service

**Cần help:**
- Xem file DEPLOY_RENDER.md để biết chi tiết hơn
