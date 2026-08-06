# Script kiểm tra và đề xuất file có thể xóa
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  KIỂM TRA FILE CÓ THỂ XÓA ĐỂ GIẢI PHÓNG BỘ NHỚ" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectPath = "C:\ghi_bien_lai"

if (!(Test-Path $projectPath)) {
    Write-Host "❌ Không tìm thấy thư mục: $projectPath" -ForegroundColor Red
    exit
}

cd $projectPath

Write-Host "[1] Kiểm tra dung lượng thư mục..." -ForegroundColor Yellow
Write-Host ""

# Kiểm tra tổng dung lượng
$totalSize = (Get-ChildItem -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "📊 Tổng dung lượng project: $([math]::Round($totalSize, 2)) MB" -ForegroundColor Green
Write-Host ""

# Liệt kê file lớn
Write-Host "[2] File lớn nhất (top 10):" -ForegroundColor Yellow
Get-ChildItem -Recurse -File | 
    Sort-Object Length -Descending | 
    Select-Object -First 10 | 
    ForEach-Object {
        $sizeMB = [math]::Round($_.Length / 1MB, 2)
        $sizeKB = [math]::Round($_.Length / 1KB, 0)
        if ($sizeMB -gt 0) {
            Write-Host "  📄 $($_.Name) - $sizeMB MB" -ForegroundColor White
        } else {
            Write-Host "  📄 $($_.Name) - $sizeKB KB" -ForegroundColor Gray
        }
    }
Write-Host ""

# File backup có thể xóa
Write-Host "[3] File backup (có thể xóa an toàn):" -ForegroundColor Yellow
$backupFiles = Get-ChildItem -Recurse -File | Where-Object { 
    $_.Name -like "*backup*" -or 
    $_.Name -like "*_old*" -or 
    $_.Name -like "*_v1*" -or
    $_.Name -like "*.bak"
}

if ($backupFiles) {
    $backupSize = ($backupFiles | Measure-Object -Property Length -Sum).Sum / 1KB
    foreach ($file in $backupFiles) {
        $sizeKB = [math]::Round($file.Length / 1KB, 0)
        Write-Host "  🗑️  $($file.Name) - $sizeKB KB" -ForegroundColor Yellow
    }
    Write-Host "  💾 Tổng: $([math]::Round($backupSize, 2)) KB" -ForegroundColor Green
} else {
    Write-Host "  ✅ Không có file backup" -ForegroundColor Green
}
Write-Host ""

# Thư mục __pycache__
Write-Host "[4] Thư mục cache Python (__pycache__):" -ForegroundColor Yellow
$pycacheDirs = Get-ChildItem -Recurse -Directory -Filter "__pycache__"
if ($pycacheDirs) {
    foreach ($dir in $pycacheDirs) {
        $size = (Get-ChildItem -Path $dir.FullName -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1KB
        Write-Host "  🗑️  $($dir.FullName) - $([math]::Round($size, 2)) KB" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✅ Không có thư mục cache" -ForegroundColor Green
}
Write-Host ""

# Thư mục .git
Write-Host "[5] Thư mục .git:" -ForegroundColor Yellow
$gitDir = Get-ChildItem -Directory -Filter ".git" -Force
if ($gitDir) {
    $gitSize = (Get-ChildItem -Path $gitDir.FullName -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "  📁 .git - $([math]::Round($gitSize, 2)) MB" -ForegroundColor White
    Write-Host "  ⚠️  Có thể xóa nếu không cần git (nhưng sẽ mất lịch sử)" -ForegroundColor Yellow
} else {
    Write-Host "  ✅ Không có thư mục .git" -ForegroundColor Green
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ĐỀ XUẤT XÓA FILE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ AN TOÀN XÓA:" -ForegroundColor Green
Write-Host "  • File backup: *backup*, *_old*, *_v1*" -ForegroundColor White
Write-Host "  • Thư mục __pycache__" -ForegroundColor White
Write-Host "  • File .pyc (compiled Python)" -ForegroundColor White
Write-Host ""

Write-Host "⚠️  CÓ THỂ XÓA (nếu không dùng):" -ForegroundColor Yellow
Write-Host "  • File .md (tài liệu)" -ForegroundColor White
Write-Host "  • Thư mục .git (mất lịch sử code)" -ForegroundColor White
Write-Host "  • File .bat không dùng" -ForegroundColor White
Write-Host ""

Write-Host "❌ KHÔNG XÓA:" -ForegroundColor Red
Write-Host "  • telegram_bot.py" -ForegroundColor White
Write-Host "  • telegram_bot_v2.py" -ForegroundColor White
Write-Host "  • credentials.json" -ForegroundColor White
Write-Host "  • requirements.txt" -ForegroundColor White
Write-Host "  • logo.jpg" -ForegroundColor White
Write-Host ""

# Hỏi có muốn xóa không
Write-Host "========================================" -ForegroundColor Cyan
$response = Read-Host "Bạn có muốn tự động xóa file backup và cache? (Y/N)"

if ($response -eq "Y" -or $response -eq "y") {
    Write-Host ""
    Write-Host "🗑️  Đang xóa file không cần thiết..." -ForegroundColor Yellow
    
    # Xóa file backup
    $deleted = 0
    $savedSpace = 0
    
    Get-ChildItem -Recurse -File | Where-Object { 
        $_.Name -like "*backup*" -or 
        $_.Name -like "*_old*" -or 
        $_.Name -like "*_v1*" -or
        $_.Name -like "*.bak"
    } | ForEach-Object {
        $savedSpace += $_.Length
        Remove-Item $_.FullName -Force
        Write-Host "  ✅ Đã xóa: $($_.Name)" -ForegroundColor Green
        $deleted++
    }
    
    # Xóa __pycache__
    Get-ChildItem -Recurse -Directory -Filter "__pycache__" | ForEach-Object {
        $cacheSize = (Get-ChildItem -Path $_.FullName -Recurse -File | Measure-Object -Property Length -Sum).Sum
        $savedSpace += $cacheSize
        Remove-Item $_.FullName -Recurse -Force
        Write-Host "  ✅ Đã xóa: $($_.FullName)" -ForegroundColor Green
        $deleted++
    }
    
    # Xóa file .pyc
    Get-ChildItem -Recurse -File -Filter "*.pyc" | ForEach-Object {
        $savedSpace += $_.Length
        Remove-Item $_.FullName -Force
        Write-Host "  ✅ Đã xóa: $($_.Name)" -ForegroundColor Green
        $deleted++
    }
    
    Write-Host ""
    Write-Host "✅ Hoàn thành!" -ForegroundColor Green
    Write-Host "📊 Đã xóa $deleted file/thư mục" -ForegroundColor Cyan
    Write-Host "💾 Giải phóng: $([math]::Round($savedSpace / 1KB, 2)) KB" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "ℹ️  Không xóa file nào." -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
