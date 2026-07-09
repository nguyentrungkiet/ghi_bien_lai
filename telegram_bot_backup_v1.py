import os
import sys
from datetime import datetime
from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import re
import math

# ===== GOOGLE SHEETS INTEGRATION =====
import gspread
from google.oauth2.service_account import Credentials

# Cấu hình Google Sheets
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "1rq1DDObItEtFeyyghv-Do-hPvYB_mwaTWihTJ8lfQCk")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Thống kê học phí")
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

# Học phí mỗi tháng (VNĐ)
HOC_PHI_MOI_THANG = int(os.getenv("HOC_PHI_MOI_THANG", "350000"))

# Khởi tạo Google Sheets client
gc = None

def init_google_sheets():
    """Khởi tạo kết nối Google Sheets"""
    global gc
    try:
        # Kiểm tra nếu có credentials file
        if os.path.exists(GOOGLE_CREDENTIALS_FILE):
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            credentials = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=scopes)
            gc = gspread.authorize(credentials)
            print("✅ Kết nối Google Sheets thành công!")
            return True
        else:
            print(f"⚠️ Không tìm thấy file credentials: {GOOGLE_CREDENTIALS_FILE}")
            print("Bot sẽ chạy mà không có tính năng tra cứu học sinh")
            return False
    except Exception as e:
        print(f"❌ Lỗi kết nối Google Sheets: {e}")
        return False

def tim_hoc_sinh(hoten, lop):
    """
    Tìm học sinh trong Google Sheet theo họ tên và lớp
    Trả về: (row_number, ten_trong_sheet, thang_da_dong) hoặc None nếu không tìm thấy
    """
    if not gc:
        return None
    
    try:
        sheet = gc.open_by_key(GOOGLE_SHEET_ID).worksheet(GOOGLE_SHEET_NAME)
        records = sheet.get_all_values()
        
        # Tìm vị trí các cột (dòng đầu là header)
        header = records[0] if records else []
        
        # Tìm index của các cột (không phân biệt hoa thường)
        idx_hoten = -1
        idx_lop = -1
        idx_thang = -1
        
        for i, col in enumerate(header):
            col_lower = col.lower().strip()
            if 'họ' in col_lower and 'tên' in col_lower:
                idx_hoten = i
            elif col_lower == 'lớp':
                idx_lop = i
            elif col_lower == 'tháng':
                idx_thang = i
        
        if idx_hoten == -1 or idx_lop == -1 or idx_thang == -1:
            print(f"⚠️ Không tìm thấy đủ các cột cần thiết. Header: {header}")
            return None
        
        # Chuẩn hóa input để so sánh
        hoten_normalized = normalize_name(hoten)
        lop_normalized = normalize_lop(lop)
        
        # Tìm kiếm học sinh
        for row_num, row in enumerate(records[1:], start=2):  # Bắt đầu từ dòng 2 (bỏ header)
            if len(row) > max(idx_hoten, idx_lop, idx_thang):
                ten_trong_sheet = row[idx_hoten].strip()
                lop_trong_sheet = row[idx_lop].strip()
                
                ten_normalized = normalize_name(ten_trong_sheet)
                lop_sheet_normalized = normalize_lop(lop_trong_sheet)
                
                # So sánh (có thể tìm gần đúng)
                if (hoten_normalized == ten_normalized or 
                    ten_normalized in hoten_normalized or 
                    hoten_normalized in ten_normalized) and lop_normalized == lop_sheet_normalized:
                    
                    thang_da_dong = row[idx_thang].strip() if idx_thang < len(row) else "0"
                    
                    # Xử lý trường hợp "Cả năm" hoặc giá trị đặc biệt
                    if thang_da_dong.lower() in ['cả năm', 'ca nam', 'full', '12']:
                        thang_da_dong = 12  # Đã đóng đủ cả năm
                    else:
                        try:
                            thang_da_dong = int(thang_da_dong)
                        except:
                            thang_da_dong = 0
                    
                    return (row_num, idx_thang + 1, ten_trong_sheet, thang_da_dong)  # +1 vì Google Sheets đánh số từ 1
        
        return None
    except Exception as e:
        print(f"❌ Lỗi tìm học sinh: {e}")
        return None

def normalize_name(name):
    """Chuẩn hóa tên để so sánh (bỏ dấu, lowercase, bỏ khoảng trắng thừa)"""
    import unicodedata
    name = name.lower().strip()
    # Loại bỏ dấu tiếng Việt
    name = unicodedata.normalize('NFD', name)
    name = ''.join(c for c in name if unicodedata.category(c) != 'Mn')
    # Loại bỏ khoảng trắng thừa
    name = ' '.join(name.split())
    return name

def normalize_lop(lop):
    """Chuẩn hóa lớp để so sánh (lấy số, bỏ chữ)"""
    # Lấy số đầu tiên trong chuỗi lớp
    match = re.search(r'(\d+)', str(lop))
    if match:
        return match.group(1)
    return str(lop).lower().strip()

def cap_nhat_thang_da_dong(row_number, col_number, thang_moi):
    """Cập nhật tháng đã đóng trong Google Sheet"""
    if not gc:
        return False
    
    try:
        sheet = gc.open_by_key(GOOGLE_SHEET_ID).worksheet(GOOGLE_SHEET_NAME)
        sheet.update_cell(row_number, col_number, thang_moi)
        print(f"✅ Đã cập nhật tháng {thang_moi} cho dòng {row_number}")
        return True
    except Exception as e:
        print(f"❌ Lỗi cập nhật Google Sheet: {e}")
        return False

def tinh_so_thang_dong(so_tien):
    """
    Tính số tháng đóng dựa vào số tiền
    Học phí: HOC_PHI_MOI_THANG/tháng
    """
    so_thang = so_tien / HOC_PHI_MOI_THANG
    return math.ceil(so_thang)  # Làm tròn lên

# Đăng ký font tiếng Việt
try:
    if sys.platform == 'win32':
        arial_path = r'C:\Windows\Fonts\arial.ttf'
        arial_bold_path = r'C:\Windows\Fonts\arialbd.ttf'
        pdfmetrics.registerFont(TTFont('Arial', arial_path))
        pdfmetrics.registerFont(TTFont('Arial-Bold', arial_bold_path))
        FONT_REGULAR = 'Arial'
        FONT_BOLD = 'Arial-Bold'
    else:
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
        FONT_REGULAR = 'DejaVuSans'
        FONT_BOLD = 'DejaVuSans-Bold'
except:
    FONT_REGULAR = 'Helvetica'
    FONT_BOLD = 'Helvetica-Bold'

# Đường dẫn logo và dấu mộc (cấu hình ở đây)
# Logo từ GitHub (hoạt động cả local và cloud)
LOGO_PATH = os.getenv("LOGO_PATH", "https://raw.githubusercontent.com/nguyentrungkiet/ghi_bien_lai/main/logo.jpg")
DAM_MOC_PATH = ""  # Bỏ dấu mộc

# Chat ID của group nhận thông báo (để trống nếu không muốn gửi)
# Để lấy chat_id: Thêm bot vào group, gửi tin nhắn bất kỳ, rồi truy cập:
# https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID", "-1003625829454")

def tao_bien_lai_image(file_path, hoten, lop, thang_list, hocphi, ngay):
    """Tạo file ảnh biên lai"""
    try:
        # Kích thước giảm một nửa chiều cao
        width, height = 2480, 1754
        
        # Tạo ảnh nền trắng
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Load fonts (Windows Arial hoặc fallback)
        try:
            if sys.platform == 'win32':
                font_regular = ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', 50)
                font_bold = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 50)
                font_title = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 100)
                font_small = ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', 35)
            else:
                font_regular = ImageFont.load_default()
                font_bold = ImageFont.load_default()
                font_title = ImageFont.load_default()
                font_small = ImageFont.load_default()
        except:
            font_regular = ImageFont.load_default()
            font_bold = ImageFont.load_default()
            font_title = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Vẽ border
        border_margin = 80
        draw.rectangle(
            [border_margin, border_margin, width-border_margin, height-border_margin],
            outline='black',
            width=8
        )
        
        # Logo (nếu có)
        y_pos = 150
        if LOGO_PATH:
            try:
                if LOGO_PATH.startswith('http'):
                    response = requests.get(LOGO_PATH, timeout=5)
                    if response.status_code == 200:
                        logo = Image.open(BytesIO(response.content))
                elif os.path.exists(LOGO_PATH):
                    logo = Image.open(LOGO_PATH)
                else:
                    logo = None
                
                if logo:
                    # Resize logo
                    logo.thumbnail((350, 350))
                    img.paste(logo, (150, y_pos), logo if logo.mode == 'RGBA' else None)
            except Exception as e:
                print(f"Không thể load logo: {e}")
        
        # Tiêu đề
        y_pos = 350
        title = "BIÊN LAI THU TIỀN"
        title_bbox = draw.textbbox((0, 0), title, font=font_title)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((width - title_width) / 2, y_pos), title, fill='black', font=font_title)
        
        # Số biên lai
        y_pos += 100
        so_bien_lai = f"Số: BL{datetime.now().strftime('%Y%m%d%H%M%S')}"
        draw.text((width - 800, y_pos), so_bien_lai, fill='black', font=font_small)
        
        # Thông tin
        y_pos = 650
        left_margin = 250
        
        # Họ tên
        draw.text((left_margin, y_pos), "Họ và tên học sinh:", fill='black', font=font_regular)
        draw.text((left_margin + 800, y_pos), hoten, fill='black', font=font_bold)
        
        # Lớp
        y_pos += 100
        draw.text((left_margin, y_pos), "Lớp:", fill='black', font=font_regular)
        draw.text((left_margin + 800, y_pos), lop, fill='black', font=font_bold)
        
        # Tháng học
        y_pos += 100
        draw.text((left_margin, y_pos), "Tháng học:", fill='black', font=font_regular)
        if len(thang_list) == 1:
            thang_text = str(int(thang_list[0][0]))
        else:
            thang_text = ", ".join([str(int(t[0])) for t in thang_list])
        draw.text((left_margin + 800, y_pos), thang_text, fill='black', font=font_bold)
        
        # Học phí
        y_pos += 100
        draw.text((left_margin, y_pos), "Học phí:", fill='black', font=font_regular)
        draw.text((left_margin + 800, y_pos), f"{hocphi:,.0f} VNĐ", fill='black', font=font_bold)
        
        # Ngày đóng
        y_pos += 100
        draw.text((left_margin, y_pos), "Ngày đóng tiền:", fill='black', font=font_regular)
        draw.text((left_margin + 800, y_pos), ngay, fill='black', font=font_bold)
        
        # Gạch ngang
        y_pos += 80
        draw.line([(left_margin, y_pos), (width - left_margin, y_pos)], fill='black', width=3)
        
        # ĐÃ NHẬN - màu đỏ
        y_pos += 120
        da_nhan = "ĐÃ NHẬN"
        try:
            font_da_nhan = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 80) if sys.platform == 'win32' else font_bold
        except:
            font_da_nhan = font_bold
        da_nhan_bbox = draw.textbbox((0, 0), da_nhan, font=font_da_nhan)
        da_nhan_width = da_nhan_bbox[2] - da_nhan_bbox[0]
        draw.text(((width - da_nhan_width) / 2, y_pos), da_nhan, fill='red', font=font_da_nhan)
        
        # Footer
        y_pos = height - 300
        footer1 = "Cảm ơn quý phụ huynh đã tin tưởng!"
        footer1_bbox = draw.textbbox((0, 0), footer1, font=font_small)
        footer1_width = footer1_bbox[2] - footer1_bbox[0]
        draw.text(((width - footer1_width) / 2, y_pos), footer1, fill='gray', font=font_small)
        
        y_pos += 60
        footer2 = f"Ngày in: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        footer2_bbox = draw.textbbox((0, 0), footer2, font=font_small)
        footer2_width = footer2_bbox[2] - footer2_bbox[0]
        draw.text(((width - footer2_width) / 2, y_pos), footer2, fill='gray', font=font_small)
        
        # Lưu ảnh
        img.save(file_path, 'PNG', quality=95)
        return True
    except Exception as e:
        print(f"Lỗi tạo ảnh: {e}")
        return False

def tao_bien_lai_pdf(file_path, hoten, lop, thang_list, hocphi, ngay):
    """Tạo file PDF biên lai"""
    try:
        c = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4
        
        # Vẽ border
        c.setStrokeColorRGB(0.2, 0.2, 0.2)
        c.setLineWidth(2)
        c.rect(2*cm, 2*cm, width-4*cm, height-4*cm)
        
        # Logo (nếu có)
        if LOGO_PATH:
            try:
                if LOGO_PATH.startswith('http'):
                    # Download logo từ URL
                    response = requests.get(LOGO_PATH, timeout=5)
                    if response.status_code == 200:
                        img_data = BytesIO(response.content)
                        c.drawImage(img_data, 3*cm, height-5*cm, width=3*cm, height=3*cm, preserveAspectRatio=True)
                elif os.path.exists(LOGO_PATH):
                    # Logo local
                    c.drawImage(LOGO_PATH, 3*cm, height-5*cm, width=3*cm, height=3*cm, preserveAspectRatio=True)
            except Exception as e:
                print(f"Không thể load logo: {e}")
                pass
        
        # Tạo chuỗi hiển thị tháng (chỉ hiển thị tháng, không hiển thị năm)
        if len(thang_list) == 1:
            thang_display = f"tháng {int(thang_list[0][0])}"
        else:
            thang_display = f"các tháng {', '.join([str(int(t[0])) for t in thang_list])}"
        
        # Tiêu đề
        c.setFont(FONT_BOLD, 24)
        c.drawCentredString(width/2, height-4*cm, "BIÊN LAI THU TIỀN")
        
        c.setFont(FONT_REGULAR, 12)
        c.drawCentredString(width/2, height-5*cm, f"Học phí {thang_display}")
        
        # Số biên lai
        so_bien_lai = f"BL{datetime.now().strftime('%Y%m%d%H%M%S')}"
        c.setFont(FONT_REGULAR, 10)
        c.drawRightString(width-3*cm, height-6*cm, f"Số: {so_bien_lai}")
        
        # Thông tin
        y_pos = height - 8*cm
        c.setFont(FONT_REGULAR, 13)
        
        c.drawString(3*cm, y_pos, "Họ và tên học sinh:")
        c.setFont(FONT_BOLD, 13)
        c.drawString(10*cm, y_pos, hoten)
        
        y_pos -= 1.2*cm
        c.setFont(FONT_REGULAR, 13)
        c.drawString(3*cm, y_pos, "Lớp:")
        c.setFont(FONT_BOLD, 13)
        c.drawString(10*cm, y_pos, lop)
        
        y_pos -= 1.2*cm
        c.setFont(FONT_REGULAR, 13)
        c.drawString(3*cm, y_pos, "Tháng học:")
        c.setFont(FONT_BOLD, 13)
        if len(thang_list) == 1:
            c.drawString(10*cm, y_pos, str(int(thang_list[0][0])))
        else:
            thang_text = ", ".join([str(int(t[0])) for t in thang_list])
            c.drawString(10*cm, y_pos, thang_text)
        
        y_pos -= 1.2*cm
        c.setFont(FONT_REGULAR, 13)
        c.drawString(3*cm, y_pos, "Học phí:")
        c.setFont(FONT_BOLD, 14)
        c.drawString(10*cm, y_pos, f"{hocphi:,.0f} VNĐ")
        
        y_pos -= 1.2*cm
        c.setFont(FONT_REGULAR, 13)
        c.drawString(3*cm, y_pos, "Ngày đóng tiền:")
        c.setFont(FONT_BOLD, 13)
        c.drawString(10*cm, y_pos, ngay)
        
        # Gạch ngang
        y_pos -= 0.8*cm
        c.setLineWidth(1)
        c.line(3*cm, y_pos, width-3*cm, y_pos)
        
        # Xác nhận - ĐÃ NHẬN màu đỏ in đậm
        y_pos -= 2*cm
        c.setFont(FONT_BOLD, 16)
        c.setFillColorRGB(0.8, 0, 0)  # Màu đỏ
        c.drawCentredString(width/2, y_pos, "ĐÃ NHẬN")
        c.setFillColorRGB(0, 0, 0)  # Đổi lại màu đen cho phần sau
        
        # Footer
        y_pos -= 2*cm
        c.setFont(FONT_REGULAR, 9)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawCentredString(width/2, 3.2*cm, "Cảm ơn quý phụ huynh đã tin tưởng!")
        c.drawCentredString(width/2, 2.7*cm, f"Ngày in: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        c.save()
        return True
    except Exception as e:
        print(f"Lỗi tạo PDF: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh /start - Hướng dẫn sử dụng"""
    
    # Kiểm tra Google Sheets có kết nối không
    sheets_status = "✅ Đã kết nối" if gc else "❌ Chưa kết nối"
    
    welcome_text = f"""
🎓 **BIÊN LAI HỌC PHÍ TỰ ĐỘNG**

Chào mừng bạn! Bot này giúp tạo biên lai học phí nhanh chóng.

📊 **Google Sheets:** {sheets_status}

📝 **Cách sử dụng:**

**🆕 TỰ ĐỘNG TRA CỨU (khuyên dùng):**
```
Nguyễn Trung Kiệt lớp 7 350k
```
Bot sẽ tự động:
- Tra cứu học sinh trong danh sách
- Xác định tháng tiếp theo cần đóng
- Tạo biên lai và cập nhật Google Sheet

**Đóng nhiều tháng:**
```
Nguyễn Văn A lớp 7 700k
```
(700k = 2 tháng với học phí {HOC_PHI_MOI_THANG:,}/tháng)

**Nhiều tháng (cũ - chỉ định tháng):**
```
Nguyễn Văn A lớp 7 tháng 1+2+3 1050k
```

**Đơn vị học phí:**
- `350k` = 350,000 đồng
- `1.05tr` = 1,050,000 đồng
- `350000` = 350,000 đồng

🚀 Gửi thông tin ngay để nhận biên lai!
"""
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def xu_ly_tin_nhan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý tin nhắn từ người dùng"""
    text = update.message.text.strip()
    
    try:
        # Parse dữ liệu
        # Hỗ trợ 3 định dạng:
        # 1. "Họ tên: xxx\nLớp: xxx\nTháng: xxx\nHọc phí: xxx"
        # 2. "họ tên, lớp, tháng, học phí" (phân cách bởi dấu phẩy)
        # 3. "họ tên lớp X tháng Y số_tiền" (tự nhiên)
        # 4. MỚI: "họ tên lớp X số_tiền" (tự động tra cứu tháng)
        
        hoten = None
        lop = None
        thang_str = None
        hocphi_str = None
        auto_lookup = False  # Flag đánh dấu có tự động tra cứu không
        
        if ":" in text:
            # Định dạng có nhãn
            lines = text.split('\n')
            data = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    data[key.strip().lower()] = value.strip()
            
            hoten = data.get('họ tên') or data.get('ho ten') or data.get('hoten')
            lop = data.get('lớp') or data.get('lop')
            thang_str = data.get('tháng') or data.get('thang')
            hocphi_str = data.get('học phí') or data.get('hoc phi') or data.get('hocphi')
        elif "," in text and text.count(',') >= 3:
            # Định dạng ngắn gọn, cách nhau bởi dấu phẩy
            parts = [p.strip() for p in text.split(',')]
            if len(parts) < 4:
                await update.message.reply_text(
                    "❌ Định dạng không đúng!\n\n"
                    "Vui lòng gửi theo mẫu:\n"
                    "`Nguyễn Văn A, 7A, 01/2026, 1500000`\n\n"
                    "Hoặc tự nhiên hơn:\n"
                    "`Nguyễn Văn A lớp 7 350k`",
                    parse_mode='Markdown'
                )
                return
            
            hoten = parts[0]
            lop = parts[1]
            thang_str = parts[2]
            hocphi_str = parts[3]
        else:
            # Định dạng tự nhiên: "Họ tên lớp X tháng Y số_tiền" hoặc "Họ tên lớp X số_tiền"
            
            # Tìm lớp (sau từ khóa "lớp" hoặc "lop")
            lop_match = re.search(r'l[oớ]p\s+(\w+)', text, re.IGNORECASE)
            if not lop_match:
                await update.message.reply_text(
                    "❌ Không tìm thấy thông tin lớp!\n\n"
                    "Ví dụ: `Nguyễn Văn A lớp 7 350k`",
                    parse_mode='Markdown'
                )
                return
            lop = lop_match.group(1)
            
            # Tìm học phí (ưu tiên tìm số có đơn vị k/tr ở cuối câu)
            # Pattern 1: Số + k/tr (ưu tiên cao nhất)
            hocphi_match = re.search(r'(\d+(?:[.,]\d+)?)\s*([kKtrTR]|triệu|triẹu|nghìn|nghin)(?:\s|$)', text, re.IGNORECASE)
            
            if not hocphi_match:
                # Pattern 2: Số lớn không có đơn vị (>= 100,000)
                numbers = re.findall(r'\b(\d{6,})\b', text)
                if numbers:
                    so_tien = float(numbers[-1])
                    don_vi = ''
                else:
                    await update.message.reply_text(
                        "❌ Không tìm thấy thông tin học phí!\n\n"
                        "Ví dụ: `350k` hoặc `350000` hoặc `1.05tr`",
                        parse_mode='Markdown'
                    )
                    return
            else:
                so_tien = float(hocphi_match.group(1).replace(',', '.'))
                don_vi = hocphi_match.group(2) or ''
            
            # Chuyển đổi đơn vị
            if don_vi and don_vi.lower() in ['k']:
                so_tien = so_tien * 1000
            elif don_vi and don_vi.lower() in ['tr', 'triệu', 'triẹu']:
                so_tien = so_tien * 1000000
            elif don_vi and don_vi.lower() in ['nghìn', 'nghin']:
                so_tien = so_tien * 1000
            
            hocphi_str = str(int(so_tien))
            
            # Tìm họ tên (phần trước "lớp")
            hoten_match = re.match(r'^(.+?)\s+l[oớ]p', text, re.IGNORECASE)
            if hoten_match:
                hoten = hoten_match.group(1).strip()
            else:
                hoten = text.split()[0]  # Lấy từ đầu tiên
            
            # Kiểm tra xem có chỉ định tháng không
            thang_plus_match = re.search(r'th[aá]ng\s+([\d+]+)', text, re.IGNORECASE)
            
            if thang_plus_match:
                # Có chỉ định tháng - xử lý như cũ
                thang_str_raw = thang_plus_match.group(1)
                current_year = datetime.now().year
                
                if '+' in thang_str_raw:
                    thang_matches = thang_str_raw.split('+')
                else:
                    thang_matches = re.findall(r'th[aá]ng\s+(\d+(?:/\d+)?)', text, re.IGNORECASE)
                
                if thang_matches:
                    thang_list_temp = []
                    for t in thang_matches:
                        if '/' not in t:
                            thang_list_temp.append(f"{int(t):02d}/{current_year}")
                        else:
                            thang_list_temp.append(t)
                    thang_str = ", ".join(thang_list_temp)
            else:
                # KHÔNG có chỉ định tháng -> TỰ ĐỘNG TRA CỨU GOOGLE SHEETS
                auto_lookup = True
        
        # Kiểm tra dữ liệu cơ bản
        if not all([hoten, lop, hocphi_str]):
            await update.message.reply_text("❌ Thiếu thông tin! Vui lòng nhập đầy đủ họ tên, lớp và học phí.")
            return
        
        # Parse học phí
        hocphi = float(hocphi_str.replace(",", "").replace(".", "").replace(" ", ""))
        
        # ===== XỬ LÝ TỰ ĐỘNG TRA CỨU =====
        if auto_lookup:
            if not gc:
                await update.message.reply_text(
                    "⚠️ Chức năng tra cứu tự động chưa được kích hoạt.\n"
                    "Vui lòng chỉ định tháng:\n"
                    f"`{hoten} lớp {lop} tháng X {int(hocphi):,}`",
                    parse_mode='Markdown'
                )
                return
            
            # Tìm học sinh trong Google Sheet
            result = tim_hoc_sinh(hoten, lop)
            
            if not result:
                await update.message.reply_text(
                    f"❌ Không tìm thấy học sinh **{hoten}** lớp **{lop}** trong danh sách!\n\n"
                    "Vui lòng kiểm tra lại thông tin hoặc chỉ định tháng:\n"
                    f"`{hoten} lớp {lop} tháng X {int(hocphi):,}`",
                    parse_mode='Markdown'
                )
                return
            
            row_number, col_number, ten_trong_sheet, thang_da_dong = result
            
            # Tính số tháng đóng dựa vào số tiền
            so_thang_dong = tinh_so_thang_dong(hocphi)
            
            # Tính tháng mới (từ tháng đã đóng + 1 đến tháng mới)
            thang_bat_dau = thang_da_dong + 1
            thang_ket_thuc = thang_da_dong + so_thang_dong
            
            # Kiểm tra giới hạn tháng 1-12
            if thang_bat_dau > 12:
                await update.message.reply_text(
                    f"⚠️ Học sinh **{ten_trong_sheet}** đã đóng đủ học phí đến tháng 12!\n"
                    "Không thể xuất biên lai thêm.",
                    parse_mode='Markdown'
                )
                return
            
            if thang_ket_thuc > 12:
                thang_ket_thuc = 12
                so_thang_thuc_dong = thang_ket_thuc - thang_da_dong
                hocphi_thuc = so_thang_thuc_dong * HOC_PHI_MOI_THANG
                await update.message.reply_text(
                    f"⚠️ Chỉ có thể đóng đến tháng 12.\n"
                    f"Số tháng thực tế: **{so_thang_thuc_dong}** tháng (tháng {thang_bat_dau} - {thang_ket_thuc})\n"
                    f"Học phí: **{hocphi_thuc:,.0f} VNĐ**",
                    parse_mode='Markdown'
                )
                hocphi = hocphi_thuc
            
            # Tạo danh sách tháng
            current_year = datetime.now().year
            thang_list_temp = []
            for t in range(thang_bat_dau, thang_ket_thuc + 1):
                thang_list_temp.append(f"{t:02d}/{current_year}")
            thang_str = ", ".join(thang_list_temp)
            
            # Sử dụng tên trong sheet để đảm bảo chính xác
            hoten = ten_trong_sheet
            
            # Thông báo tìm thấy học sinh
            await update.message.reply_text(
                f"✅ Tìm thấy học sinh: **{ten_trong_sheet}**\n"
                f"📚 Lớp: **{lop}**\n"
                f"📅 Đã đóng đến tháng: **{thang_da_dong}**\n"
                f"💰 Số tiền đóng: **{hocphi:,.0f} VNĐ** ({so_thang_dong} tháng)\n"
                f"📋 Sẽ ghi biên lai: tháng **{thang_bat_dau}**" + (f" - **{thang_ket_thuc}**" if so_thang_dong > 1 else ""),
                parse_mode='Markdown'
            )
        
        # Parse tháng (cho cả trường hợp auto và manual)
        thang_list = []
        invalid_months = []
        
        if thang_str:
            for item in thang_str.replace(" ", "").split(","):
                if "/" in item:
                    parts = item.split("/")
                    month = int(parts[0])
                    year = parts[1]
                    
                    # Kiểm tra tháng hợp lệ (1-12)
                    if month < 1 or month > 12:
                        invalid_months.append(str(month))
                    else:
                        thang_list.append((parts[0].zfill(2), year))
                await update.message.reply_text(
                    "❌ Không tìm thấy thông tin tháng!\n\n"
                    "Ví dụ: `Nguyễn Văn A lớp 7 tháng 1 350k`\n"
                    "Hoặc: `Nguyễn Văn A lớp 7 tháng 7+8 350k`",
                    parse_mode='Markdown'
                )
                return
            
            # Tạo chuỗi tháng (thêm năm hiện tại nếu chưa có)
            current_year = datetime.now().year
            thang_list_temp = []
            for t in thang_matches:
                if '/' not in t:
                    thang_list_temp.append(f"{int(t):02d}/{current_year}")
                else:
                    thang_list_temp.append(t)
            thang_str = ", ".join(thang_list_temp)
            
            # Tìm học phí (ưu tiên tìm số có đơn vị k/tr ở cuối câu)
            # Pattern 1: Số + k/tr (ưu tiên cao nhất)
            hocphi_match = re.search(r'(\d+(?:[.,]\d+)?)\s*([kKtrTR]|triệu|triẹu|nghìn|nghin)(?:\s|$)', text, re.IGNORECASE)
            
            if not hocphi_match:
                # Pattern 2: Số lớn không có đơn vị (>= 100,000)
                numbers = re.findall(r'\b(\d{6,})\b', text)
                if numbers:
                    hocphi_match = (numbers[-1], '')  # Lấy số cuối cùng
                    so_tien = float(hocphi_match[0])
                    don_vi = ''
                else:
                    await update.message.reply_text(
                        "❌ Không tìm thấy thông tin học phí!\n\n"
                        "Ví dụ: `350k` hoặc `350000` hoặc `1.5tr`",
                        parse_mode='Markdown'
                    )
                    return
            else:
                so_tien = float(hocphi_match.group(1).replace(',', '.'))
                don_vi = hocphi_match.group(2) or ''
            
            # Chuyển đổi đơn vị
            if don_vi and don_vi.lower() in ['k']:
                so_tien = so_tien * 1000
            elif don_vi and don_vi.lower() in ['tr', 'triệu', 'triẹu']:
                so_tien = so_tien * 1000000
            elif don_vi and don_vi.lower() in ['nghìn', 'nghin']:
                so_tien = so_tien * 1000
            
            hocphi_str = str(int(so_tien))
            
            # Tìm họ tên (phần trước "lớp")
            hoten_match = re.match(r'^(.+?)\s+l[oớ]p', text, re.IGNORECASE)
            if hoten_match:
                hoten = hoten_match.group(1).strip()
            else:
                hoten = text.split()[0]  # Lấy từ đầu tiên
        
        # Kiểm tra dữ liệu
        if not all([hoten, lop, thang_str, hocphi_str]):
            await update.message.reply_text("❌ Thiếu thông tin! Vui lòng nhập đầy đủ họ tên, lớp, tháng và học phí.")
            return
        
        # Parse tháng
        thang_list = []
        invalid_months = []
        
        for item in thang_str.replace(" ", "").split(","):
            if "/" in item:
                parts = item.split("/")
                month = int(parts[0])
                year = parts[1]
                
                # Kiểm tra tháng hợp lệ (1-12)
                if month < 1 or month > 12:
                    invalid_months.append(str(month))
                else:
                    thang_list.append((parts[0].zfill(2), year))
        
        # Nếu có tháng không hợp lệ, báo lỗi
        if invalid_months:
            await update.message.reply_text(
                f"❌ Tháng không hợp lệ: {', '.join(invalid_months)}\n\n"
                "⚠️ Tháng phải từ 1 đến 12!\n\n"
                "Ví dụ đúng:\n"
                "• `Nguyễn Văn A lớp 7 350k` (tự động tra cứu)\n"
                "• `Huỳnh Trân lớp 8 tháng 12 350k`\n"
                "• `Lê Thị B lớp 9 tháng 1+2+3 1050k`",
                parse_mode='Markdown'
            )
            return
        
        if not thang_list:
            await update.message.reply_text("❌ Định dạng tháng không đúng! Ví dụ: 01/2026 hoặc 01/2026, 02/2026")
            return
        
        # Ngày đóng tiền
        ngay = datetime.now().strftime("%d/%m/%Y")
        
        # Tạo file ảnh
        await update.message.reply_text("⏳ Đang tạo biên lai...")
        
        thang_str_file = "_".join([f"{t[0]}{t[1]}" for t in thang_list])
        filename = f"BienLai_{hoten.replace(' ', '_')}_{thang_str_file}.png"
        file_path = filename
        
        success = tao_bien_lai_image(file_path, hoten, lop, thang_list, hocphi, ngay)
        
        if success and os.path.exists(file_path):
            # Gửi file ảnh cho người dùng với nút xóa
            keyboard = [[InlineKeyboardButton("🗑 Xóa tin nhắn này", callback_data="delete")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            with open(file_path, 'rb') as f:
                sent_message = await update.message.reply_photo(
                    photo=f,
                    caption=f"✅ Biên lai học phí\n👤 {hoten}\n🏫 Lớp {lop}\n💰 {hocphi:,.0f} VNĐ",
                    reply_markup=reply_markup
                )
            
            # ===== CẬP NHẬT GOOGLE SHEETS SAU KHI XUẤT BIÊN LAI =====
            if auto_lookup and gc:
                thang_moi = thang_ket_thuc  # Tháng cao nhất đã đóng
                if cap_nhat_thang_da_dong(row_number, col_number, thang_moi):
                    await update.message.reply_text(
                        f"📊 Đã cập nhật Google Sheets: tháng đã đóng → **{thang_moi}**",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text(
                        "⚠️ Không thể cập nhật Google Sheets. Vui lòng cập nhật thủ công!",
                        parse_mode='Markdown'
                    )
            
            # Gửi vào group (nếu có cấu hình)
            if GROUP_CHAT_ID:
                try:
                    # Format thông tin tháng
                    if len(thang_list) == 1:
                        thang_info = f"tháng {int(thang_list[0][0])}"
                    else:
                        thang_info = f"các tháng {', '.join([str(int(t[0])) for t in thang_list])}"
                    
                    # Tạo nội dung tin nhắn
                    message = f"📋 **BIÊN LAI MỚI**\n\n👤 Họ tên: **{hoten}**\n🏫 Lớp: **{lop}**\n📅 Học phí {thang_info}\n💰 Số tiền: **{hocphi:,.0f} VNĐ**\n🗓 Ngày đóng: {ngay}"
                    
                    # Gửi ảnh và thông tin vào group
                    with open(file_path, 'rb') as f:
                        await context.bot.send_photo(
                            chat_id=GROUP_CHAT_ID,
                            photo=f,
                            caption=message,
                            parse_mode='Markdown'
                        )
                except Exception as e:
                    print(f"⚠️ Không thể gửi vào group: {e}")
            
            # Xóa file tạm
            try:
                os.remove(file_path)
            except:
                pass
        else:
            await update.message.reply_text("❌ Có lỗi khi tạo biên lai. Vui lòng thử lại!")
    
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {str(e)}\n\nVui lòng kiểm tra lại định dạng tin nhắn!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh /help"""
    await start(update, context)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý khi nhấn nút"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "delete":
        # Xóa tin nhắn biên lai
        try:
            await query.message.delete()
            # Xóa cả tin nhắn yêu cầu của người dùng (nếu có thể)
            if query.message.reply_to_message:
                await query.message.reply_to_message.delete()
        except Exception as e:
            await query.message.reply_text(f"⚠️ Không thể xóa tin nhắn: {str(e)}")

def main():
    """Khởi chạy bot"""
    # Lấy token từ biến môi trường hoặc nhập trực tiếp
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8426267636:AAH4VFrILZ_A3vKMzDuzmGFkZbNJ4QZDjTs")
    
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ CHƯA CẤU HÌNH BOT TOKEN!")
        print("\nCách lấy token:")
        print("1. Mở Telegram, tìm @BotFather")
        print("2. Gửi lệnh /newbot và làm theo hướng dẫn")
        print("3. Copy token và dán vào file này hoặc đặt biến môi trường TELEGRAM_BOT_TOKEN")
        return
    
    # Khởi tạo Google Sheets
    print("🔄 Đang kết nối Google Sheets...")
    init_google_sheets()
    
    # Tạo application
    application = Application.builder().token(TOKEN).build()
    
    # Đăng ký handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, xu_ly_tin_nhan))
    
    # Chạy bot
    print("🤖 Bot đang chạy...")
    print("📱 Hãy mở Telegram và chat với bot!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
