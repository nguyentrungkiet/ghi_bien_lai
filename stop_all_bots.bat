@echo off
chcp 65001 >nul
echo ========================================
echo   DỪNG TẤT CẢ BOT TELEGRAM
echo ========================================
echo.

echo [Bước 1] Tìm tất cả Python process...
echo.
wmic process where "name='python.exe' or name='pythonw.exe'" get ProcessId,CommandLine
echo.

echo [Bước 2] Dừng tất cả Python...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
echo ✓ Đã gửi lệnh dừng
echo.

echo [Bước 3] Đợi 10 giây...
timeout /t 10 /nobreak
echo.

echo [Bước 4] Kiểm tra lại...
tasklist | findstr /I "python"
if %errorlevel% equ 0 (
    echo ⚠️ Vẫn còn Python đang chạy!
    echo Thử dừng bằng PID...
    for /f "tokens=2" %%a in ('tasklist ^| findstr /I "python"') do taskkill /F /PID %%a 2>nul
) else (
    echo ✓ Đã dừng hết tất cả bot!
)
echo.

echo [Bước 5] Đợi thêm 5 giây để Telegram cập nhật...
timeout /t 5 /nobreak
echo.

echo ========================================
echo   HOÀN TẤT! AN TOÀN ĐỂ CHẠY BOT MỚI
echo ========================================
echo.
pause
