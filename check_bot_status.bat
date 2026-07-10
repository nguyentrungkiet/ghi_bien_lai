@echo off
chcp 65001 >nul
echo ========================================
echo   KIỂM TRA BOT TELEGRAM
echo ========================================
echo.

echo [1] Kiểm tra Python đang chạy trên VPS này...
echo.
tasklist | findstr /I "python"
if %errorlevel% equ 0 (
    echo.
    echo Chi tiết process:
    wmic process where "name='python.exe' or name='pythonw.exe'" get ProcessId,CommandLine,CreationDate
    echo.
    echo ⚠️ CÓ BOT ĐANG CHẠY TRÊN VPS NÀY!
) else (
    echo ✓ Không có bot nào đang chạy trên VPS này
)
echo.

echo ========================================
echo [2] LƯU Ý QUAN TRỌNG
echo ========================================
echo.
echo Bot Telegram CHỈ cho phép 1 instance tại 1 thời điểm!
echo.
echo Kiểm tra các nơi sau:
echo.
echo 1. ✓ VPS này (đã kiểm tra ở trên)
echo 2. ❓ Render.com - Có deploy bot không?
echo 3. ❓ VPS khác - Có chạy bot không?
echo 4. ❓ Máy local - Có ai đang test không?
echo 5. ❓ Task Scheduler - Có task tự động không?
echo.
echo ========================================
echo [3] CÁCH XỬ LÝ
echo ========================================
echo.
echo Nếu bot đang chạy ở Render.com:
echo   - Vào Render Dashboard
echo   - Tạm dừng hoặc xóa service
echo.
echo Nếu bot đang chạy ở VPS khác:
echo   - Đăng nhập VPS đó
echo   - Chạy: taskkill /F /IM python.exe
echo.
echo Sau khi dừng HẾT bot ở mọi nơi:
echo   - Đợi 30 giây
echo   - Chạy bot mới trên VPS này
echo.
echo ========================================
pause
