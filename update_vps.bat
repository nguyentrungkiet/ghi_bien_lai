@echo off
chcp 65001 >nul
echo ========================================
echo   CẬP NHẬT BOT TELEGRAM TỪ GITHUB
echo ========================================
echo.

echo [1/5] Dừng TẤT CẢ bot đang chạy...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
echo ✓ Đã dừng tất cả Python process
echo.

echo [2/5] Đợi 5 giây để đảm bảo dừng hoàn toàn...
timeout /t 5 /nobreak >nul
echo ✓ Đã đợi xong
echo.

echo [3/5] Cập nhật code từ GitHub...
cd C:\ghi_bien_lai
git pull origin main
if %errorlevel% neq 0 (
    echo ✗ Lỗi khi pull code từ GitHub!
    pause
    exit /b 1
)
echo ✓ Đã cập nhật code mới nhất
echo.

echo [4/5] Cài đặt/Cập nhật thư viện Python...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ✗ Lỗi khi cài đặt thư viện!
    pause
    exit /b 1
)
echo ✓ Đã cập nhật thư viện
echo.

echo [5/5] Khởi động bot...
echo ✓ Bot đang khởi động...
echo.
echo ========================================
echo   BOT ĐÃ SẴN SÀNG!
echo ========================================
echo.
echo ⚠️  CHỈ CHẠY 1 BOT DUY NHẤT!
echo ⚠️  KHÔNG MỞ NHIỀU CỬA SỔ!
echo.
python telegram_bot_v2.py
