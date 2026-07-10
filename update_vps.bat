@echo off
chcp 65001 >nul
echo ========================================
echo   CẬP NHẬT BOT TELEGRAM TỪ GITHUB
echo ========================================
echo.

echo [1/4] Dừng bot đang chạy...
taskkill /F /IM python.exe 2>nul
if %errorlevel% equ 0 (
    echo ✓ Đã dừng bot cũ
) else (
    echo ✓ Không có bot nào đang chạy
)
echo.

echo [2/4] Cập nhật code từ GitHub...
cd C:\ghi_bien_lai
git pull origin main
if %errorlevel% neq 0 (
    echo ✗ Lỗi khi pull code từ GitHub!
    pause
    exit /b 1
)
echo ✓ Đã cập nhật code mới nhất
echo.

echo [3/4] Cài đặt/Cập nhật thư viện Python...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ✗ Lỗi khi cài đặt thư viện!
    pause
    exit /b 1
)
echo ✓ Đã cập nhật thư viện
echo.

echo [4/4] Khởi động bot...
echo ✓ Bot đang khởi động...
echo.
echo ========================================
echo   BOT ĐÃ SẴN SÀNG!
echo ========================================
echo.
python telegram_bot_v2.py
