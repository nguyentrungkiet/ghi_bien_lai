# 🚀 HƯỚNG DẪN DEPLOY BOT LÊN RENDER.COM

## Bước 1: Chuẩn bị

### 1.1. Tạo tài khoản GitHub (nếu chưa có)
1. Truy cập https://github.com
2. Đăng ký tài khoản miễn phí

### 1.2. Upload code lên GitHub

**Cách 1: Dùng GitHub Desktop (dễ nhất)**
1. Tải GitHub Desktop: https://desktop.github.com
2. Đăng nhập GitHub
3. Click "File" → "New Repository"
   - Name: `bien-lai-bot`
   - Local Path: `D:\SourceCode\in biên lai`
4. Click "Create Repository"
5. Click "Publish repository" → Bỏ tick "Keep this code private" → "Publish"

**Cách 2: Dùng Git command line**
```bash
cd "D:\SourceCode\in biên lai"
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/USERNAME/bien-lai-bot.git
git push -u origin main
```

## Bước 2: Chuẩn bị Logo

**Quan trọng:** Logo cần được upload lên cloud vì Render.com không có file local

**Cách 1: Upload logo lên GitHub (khuyên dùng)**
1. Trong repo GitHub của bạn, click "Add file" → "Upload files"
2. Upload file `logo.jpg`
3. Commit
4. Click vào file logo, click "Raw" để lấy URL
5. Copy URL (dạng: `https://raw.githubusercontent.com/USERNAME/bien-lai-bot/main/logo.jpg`)

**Cách 2: Dùng dịch vụ hosting ảnh miễn phí**
- Imgur.com
- ImgBB.com
- Upload và lấy direct link

## Bước 3: Cập nhật đường dẫn Logo

Trong file `telegram_bot.py`, sửa dòng:
```python
LOGO_PATH = r"D:\SourceCode\in biên lai\logo.jpg"
```

Thành:
```python
LOGO_PATH = "logo.jpg"  # Nếu upload cùng repo
# Hoặc
LOGO_PATH = "https://raw.githubusercontent.com/USERNAME/bien-lai-bot/main/logo.jpg"  # URL từ GitHub
```

Commit và push thay đổi lên GitHub.

## Bước 4: Deploy trên Render.com

### 4.1. Tạo tài khoản Render
1. Truy cập https://render.com
2. Click "Get Started" → Sign up with GitHub
3. Cho phép Render truy cập GitHub

### 4.2. Tạo Web Service
1. Trong Dashboard, click "New" → "Background Worker"
2. Connect repository `bien-lai-bot`
3. Cấu hình:
   - **Name:** `bien-lai-bot`
   - **Region:** Singapore (gần VN nhất)
   - **Branch:** `main`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python telegram_bot.py`

### 4.3. Thêm Environment Variables
Click "Environment" → "Add Environment Variable":
```
Key: TELEGRAM_BOT_TOKEN
Value: 8426267636:AAH4VFrILZ_A3vKMzDuzmGFkZbNJ4QZDjTs
```

### 4.4. Deploy
1. Click "Create Background Worker"
2. Render sẽ tự động build và deploy
3. Đợi 2-3 phút
4. Kiểm tra Logs để xem bot đã chạy chưa

## Bước 5: Kiểm tra

1. Mở Telegram
2. Tìm bot của bạn
3. Gửi tin nhắn test: `Nguyễn Văn A lớp 7 tháng 1 400k`
4. Bot sẽ trả về file PDF!

## 🎉 Hoàn tất!

Bot của bạn đã chạy 24/7 trên cloud miễn phí!

## 📝 Lưu ý

### Giới hạn Free Plan Render.com:
- ✅ Chạy 24/7 miễn phí
- ⚠️ Có thể sleep sau 15 phút không hoạt động
- ✅ Tự động wake up khi có request
- ✅ 750 giờ/tháng miễn phí (đủ chạy cả tháng)

### Cập nhật code:
1. Sửa code trên máy local
2. Commit và push lên GitHub
3. Render sẽ tự động deploy lại (nếu bật Auto-Deploy)

### Xem logs:
- Vào Render Dashboard → Service → Logs
- Xem bot có chạy hay gặp lỗi

### Troubleshooting:

**Bot không phản hồi:**
- Kiểm tra Logs trên Render
- Kiểm tra TOKEN đã đúng chưa
- Kiểm tra service đang chạy (Status: Live)

**Lỗi font tiếng Việt:**
Bot đã được cấu hình tự động dùng font phù hợp cho Linux

**Logo không hiển thị:**
- Kiểm tra URL logo có đúng không
- Thử mở URL trên trình duyệt xem có tải được không

## 🔄 Cập nhật sau này

Mỗi khi bạn thay đổi code:
```bash
git add .
git commit -m "Mô tả thay đổi"
git push
```

Render sẽ tự động deploy phiên bản mới!

## 💡 Tips

1. **Monitor bot:** Vào Render Dashboard thường xuyên kiểm tra logs
2. **Backup:** Code đã được lưu trên GitHub, rất an toàn
3. **Scale up:** Nếu cần performance cao hơn, nâng cấp plan ($7/tháng)

## 🆘 Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra Logs trên Render
2. Kiểm tra repo GitHub có đầy đủ files không
3. Đảm bảo TOKEN và logo path đã đúng
