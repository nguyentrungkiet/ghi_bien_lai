@echo off
chcp 65001 >nul
echo ========================================
echo   DỪNG CHỈ BOT BIÊN LAI
echo ========================================
echo.

echo [1] Tìm bot biên lai đang chạy...
echo.

:: Tìm process chứa telegram_bot
for /f "tokens=2" %%a in ('wmic process where "CommandLine like '%%telegram_bot%%'" get ProcessId ^| findstr /r "[0-9]"') do (
    echo Tìm thấy PID: %%a
    taskkill /F /PID %%a 2>nul
    if !errorlevel! equ 0 (
        echo ✓ Đã dừng bot biên lai PID %%a
    )
)

echo.
echo [2] Đợi 15 giây để Telegram cập nhật...
timeout /t 15 /nobreak >nul
echo ✓ Hoàn tất
echo.

echo ========================================
echo   AN TOÀN ĐỂ CHẠY BOT MỚI
echo ========================================
echo.
pause
