@echo off
REM Script tu dong pull code va restart bot
echo [%date% %time%] Bat dau cap nhat...

REM Di chuyen den thu muc du an
cd /d C:\ghi_bien_lai

REM Pull code moi tu GitHub
echo Dang pull code tu GitHub...
git pull origin main

REM Cho 2 giay
timeout /t 2 /nobreak >nul

REM Tat tat ca cac process Python dang chay
echo Dang restart bot...
taskkill /F /IM python.exe 2>nul

REM Cho 3 giay de process tat hoan toan
timeout /t 3 /nobreak >nul

REM Chay lai bot
echo Khoi dong bot...
start /min python telegram_bot.py

echo [%date% %time%] Hoan thanh!
