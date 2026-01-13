# Hướng dẫn Kết nối Google Sheets

## Tính năng mới

Bot đã được nâng cấp với tính năng **tự động tra cứu học sinh** từ Google Sheets:

- Nhập `Nguyễn Trung Kiệt lớp 7 350k` → Bot tự động:
  1. Tìm học sinh trong danh sách
  2. Xác định tháng đã đóng
  3. Tạo biên lai cho tháng tiếp theo
  4. Cập nhật lại Google Sheet

## Cấu trúc Google Sheet

Sheet **"Thống kê học phí"** cần có các cột:
| STT | Họ và tên | Tháng | Lớp |
|-----|-----------|-------|-----|
| 1 | Nguyễn Trung Kiệt | 3 | 7 |
| 2 | Lê Thị Hoa | 1 | 8 |

- **Tháng**: Số tháng đã đóng học phí (1-12)

## Cách tạo Google Service Account

### Bước 1: Tạo Project trên Google Cloud

1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo project mới hoặc chọn project có sẵn

### Bước 2: Bật Google Sheets API

1. Vào **APIs & Services** > **Library**
2. Tìm **Google Sheets API** và bật
3. Tìm **Google Drive API** và bật

### Bước 3: Tạo Service Account

1. Vào **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **Service Account**
3. Đặt tên (ví dụ: `bien-lai-bot`)
4. Click **Create and Continue** > **Done**

### Bước 4: Tạo Key JSON

1. Click vào Service Account vừa tạo
2. Vào tab **Keys**
3. Click **Add Key** > **Create new key** > **JSON**
4. File `credentials.json` sẽ được tải về

### Bước 5: Đặt file credentials

1. Đổi tên file tải về thành `credentials.json`
2. Đặt vào thư mục chứa bot (`in biên lai/credentials.json`)

### Bước 6: Share Google Sheet

1. Mở Google Sheet của bạn
2. Click **Share**
3. Thêm email của Service Account (có dạng `xxx@xxx.iam.gserviceaccount.com`)
4. Chọn quyền **Editor**

## Cấu hình biến môi trường (tùy chọn)

```bash
# ID của Google Sheet (lấy từ URL)
GOOGLE_SHEET_ID=1rq1DDObItEtFeyyghv-Do-hPvYB_mwaTWihTJ8lfQCk

# Tên sheet trong file
GOOGLE_SHEET_NAME=Thống kê học phí

# Đường dẫn file credentials
GOOGLE_CREDENTIALS_FILE=credentials.json

# Học phí mỗi tháng (VNĐ)
HOC_PHI_MOI_THANG=350000
```

## Cách lấy Google Sheet ID

URL: `https://docs.google.com/spreadsheets/d/1rq1DDObItEtFeyyghv-Do-hPvYB_mwaTWihTJ8lfQCk/edit`

ID: `1rq1DDObItEtFeyyghv-Do-hPvYB_mwaTWihTJ8lfQCk`

## Tính năng tự động tính tháng

- Học phí mỗi tháng: **350,000 VNĐ**
- Đóng **350k** = 1 tháng
- Đóng **700k** = 2 tháng
- Đóng **1,050k** = 3 tháng
- ...

Ví dụ: Học sinh đã đóng đến tháng 3, đóng thêm 700k → Biên lai ghi tháng 4, 5 và cập nhật Sheet thành tháng 5.

## Kiểm tra kết nối

Khi chạy bot, nếu kết nối thành công sẽ hiện:
```
✅ Kết nối Google Sheets thành công!
```

Nếu chưa có file credentials:
```
⚠️ Không tìm thấy file credentials: credentials.json
Bot sẽ chạy mà không có tính năng tra cứu học sinh
```

## Sử dụng

### Cách 1: Tự động tra cứu (MỚI - Khuyên dùng)
```
Nguyễn Trung Kiệt lớp 7 350k
```

### Cách 2: Chỉ định tháng (cũ)
```
Nguyễn Trung Kiệt lớp 7 tháng 4 350k
```

### Đóng nhiều tháng
```
Nguyễn Trung Kiệt lớp 7 1050k
```
(1,050k = 3 tháng)
