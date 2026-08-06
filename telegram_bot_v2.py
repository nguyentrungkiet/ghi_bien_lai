import os
import sys
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
import json

# ===== GOOGLE SHEETS INTEGRATION =====
import gspread
from google.oauth2.service_account import Credentials

# Cấu hình Google Sheets
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "1rq1DDObItEtFeyyghv-Do-hPvYB_mwaTWihTJ8lfQCk")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Thống kê học phí")
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

# Học phí mỗi tháng (VNĐ)
HOC_PHI_MOI_THANG = int(os.getenv("HOC_PHI_MOI_THANG", "400000"))
# Học phí lớp 10, 11, 12 (VNĐ) - 500,000đ
HOC_PHI_LOP_10_12 = int(os.getenv("HOC_PHI_LOP_10_12", "500000"))

# Khởi tạo Google Sheets client
gc = None

# Lưu trữ pending confirmations (user_id -> data)
pending_receipts = {}

def init_google_sheets():
    """Khởi tạo kết nối Google Sheets"""
    global gc
    try:
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
            return False
    except Exception as e:
        print(f"❌ Lỗi kết nối Google Sheets: {e}")
        return False

def normalize_name(name):
    """Chuẩn hóa tên để so sánh (bỏ dấu, lowercase)"""
    import unicodedata
    name = name.lower().strip()
    name = unicodedata.normalize('NFD', name)
    name = ''.join(c for c in name if unicodedata.category(c) != 'Mn')
    name = ' '.join(name.split())
    return name

def tim_hoc_sinh_theo_ten(hoten):
    """
    Tìm học sinh trong Google Sheet chỉ theo họ tên
    Trả về danh sách các học sinh tìm thấy
    """
    if not gc:
        return []
    
    try:
        sheet = gc.open_by_key(GOOGLE_SHEET_ID).worksheet(GOOGLE_SHEET_NAME)
        records = sheet.get_all_values()
        
        header = records[0] if records else []
        
        # Tìm index của các cột
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
            return []
        
        hoten_normalized = normalize_name(hoten)
        results = []
        
        for row_num, row in enumerate(records[1:], start=2):
            if len(row) > max(idx_hoten, idx_lop, idx_thang):
                ten_trong_sheet = row[idx_hoten].strip()
                lop_trong_sheet = row[idx_lop].strip()
                
                ten_normalized = normalize_name(ten_trong_sheet)
                
                # So sánh tên (tìm gần đúng)
                if (hoten_normalized == ten_normalized or 
                    ten_normalized in hoten_normalized or 
                    hoten_normalized in ten_normalized):
                    
                    thang_da_dong = row[idx_thang].strip() if idx_thang < len(row) else "0"
                    
                    # Xử lý "Cả năm"
                    if thang_da_dong.lower() in ['cả năm', 'ca nam', 'full']:
                        thang_da_dong = 12
                    else:
                        try:
                            thang_da_dong = int(thang_da_dong)
                        except:
                            thang_da_dong = 0
                    
                    results.append({
                        'row_number': row_num,
                        'col_thang': idx_thang + 1,
                        'hoten': ten_trong_sheet,
                        'lop': lop_trong_sheet,
                        'thang_da_dong': thang_da_dong
                    })
        
        return results
    except Exception as e:
        print(f"❌ Lỗi tìm học sinh: {e}")
        return []

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

def lay_hoc_phi_theo_lop(lop):
    """
    Lấy học phí theo lớp
    Lớp 10, 11, 12: 500,000đ
    Các lớp khác: 400,000đ
    """
    if lop:
        lop_str = str(lop).strip()
        # Kiểm tra lớp 10, 11, 12
        if lop_str in ['10', '11', '12']:
            return HOC_PHI_LOP_10_12
    return HOC_PHI_MOI_THANG

def tinh_so_thang_dong(so_tien, lop=None):
    """Tính số tháng đóng dựa vào số tiền và lớp"""
    hoc_phi = lay_hoc_phi_theo_lop(lop)
    so_thang = so_tien / hoc_phi
    return math.ceil(so_thang)

def parse_so_tien(text):
    """Parse số tiền từ text"""
    # Tìm số + đơn vị k/tr
    match = re.search(r'(\d+(?:[.,]\d+)?)\s*([kKtrTR]|triệu|nghìn)?', text, re.IGNORECASE)
    if match:
        so_tien = float(match.group(1).replace(',', '.'))
        don_vi = match.group(2) or ''
        
        if don_vi.lower() in ['k']:
            so_tien *= 1000
        elif don_vi.lower() in ['tr', 'triệu']:
            so_tien *= 1000000
        elif don_vi.lower() in ['nghìn']:
            so_tien *= 1000
        
        return int(so_tien)
    
    # Tìm số lớn (>= 100000)
    numbers = re.findall(r'\b(\d{6,})\b', text)
    if numbers:
        return int(numbers[-1])
    
    return None

# ===== FONT SETUP =====
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

LOGO_PATH = os.getenv("LOGO_PATH", "https://raw.githubusercontent.com/nguyentrungkiet/ghi_bien_lai/main/logo.jpg")
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID", "-1003625829454")

def tao_bien_lai_image(file_path, hoten, lop, thang_list, hocphi, ngay):
    """Tạo file ảnh biên lai"""
    try:
        width, height = 2480, 1754
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
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
        
        # Border
        border_margin = 80
        draw.rectangle(
            [border_margin, border_margin, width-border_margin, height-border_margin],
            outline='black', width=8
        )
        
        # Logo
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
                    logo.thumbnail((350, 350))
                    img.paste(logo, (150, y_pos), logo if logo.mode == 'RGBA' else None)
            except:
                pass
        
        # Title
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
        
        draw.text((left_margin, y_pos), "Họ và tên học sinh:", fill='black', font=font_regular)
        draw.text((left_margin + 800, y_pos), hoten, fill='black', font=font_bold)
        
        y_pos += 100
        draw.text((left_margin, y_pos), "Lớp:", fill='black', font=font_regular)
        draw.text((left_margin + 800, y_pos), lop, fill='black', font=font_bold)
        
        y_pos += 100
        draw.text((left_margin, y_pos), "Tháng học:", fill='black', font=font_regular)
        if len(thang_list) == 1:
            thang_text = str(int(thang_list[0][0]))
        else:
            thang_text = ", ".join([str(int(t[0])) for t in thang_list])
        draw.text((left_margin + 800, y_pos), thang_text, fill='black', font=font_bold)
        
        y_pos += 100
        draw.text((left_margin, y_pos), "Học phí:", fill='black', font=font_regular)
        draw.text((left_margin + 800, y_pos), f"{hocphi:,.0f} VNĐ", fill='black', font=font_bold)
        
        y_pos += 100
        draw.text((left_margin, y_pos), "Ngày đóng tiền:", fill='black', font=font_regular)
        draw.text((left_margin + 800, y_pos), ngay, fill='black', font=font_bold)
        
        # Gạch ngang
        y_pos += 80
        draw.line([(left_margin, y_pos), (width - left_margin, y_pos)], fill='black', width=3)
        
        # ĐÃ NHẬN
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
        
        img.save(file_path, 'PNG', quality=95)
        return True
    except Exception as e:
        print(f"Lỗi tạo ảnh: {e}")
        return False

# ===== TELEGRAM HANDLERS =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh /start"""
    sheets_status = "✅ Đã kết nối" if gc else "❌ Chưa kết nối"
    
    welcome_text = f"""
🎓 **BIÊN LAI HỌC PHÍ TỰ ĐỘNG**

📊 **Google Sheets:** {sheets_status}
💰 **Học phí:**
   • Lớp 5-9: {HOC_PHI_MOI_THANG:,}đ/tháng
   • Lớp 10-12: {HOC_PHI_LOP_10_12:,}đ/tháng

📝 **Cách sử dụng đơn giản:**

Chỉ cần gõ **tên học sinh** và **số tiền**:
```
Nguyễn Trung Kiệt 500k
```

Bot sẽ:
1. 🔍 Tự động tìm học sinh trong danh sách
2. 📋 Hiển thị thông tin và hỏi xác nhận
3. 🖨️ In biên lai nếu bạn đồng ý

**Đóng nhiều tháng:**
```
Lớp 5-9: 800k = 2 tháng
Lớp 10-12: 1000k = 2 tháng
```

🚀 Gửi thông tin ngay!
"""
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def xu_ly_tin_nhan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý tin nhắn từ người dùng"""
    text = update.message.text.strip()
    user_id = update.effective_user.id
    
    try:
        # Parse số tiền từ text
        so_tien = parse_so_tien(text)
        
        if not so_tien:
            await update.message.reply_text(
                "❌ Không tìm thấy số tiền!\n\n"
                "Vui lòng nhập theo mẫu:\n"
                "`Tên học sinh 400k`\n\n"
                "Ví dụ: `Nguyễn Văn A 400k`",
                parse_mode='Markdown'
            )
            return
        
        # Lấy tên (phần trước số tiền)
        # Loại bỏ số tiền và các ký tự liên quan
        hoten = re.sub(r'\d+(?:[.,]\d+)?\s*([kKtrTR]|triệu|nghìn)?', '', text).strip()
        hoten = re.sub(r'\s+', ' ', hoten).strip()
        
        if not hoten or len(hoten) < 2:
            await update.message.reply_text(
                "❌ Không tìm thấy tên học sinh!\n\n"
                "Vui lòng nhập theo mẫu:\n"
                "`Tên học sinh 400k`",
                parse_mode='Markdown'
            )
            return
        
        if not gc:
            await update.message.reply_text(
                "⚠️ Chưa kết nối Google Sheets!\n"
                "Vui lòng liên hệ admin để cấu hình.",
                parse_mode='Markdown'
            )
            return
        
        # Tìm học sinh
        await update.message.reply_text(f"🔍 Đang tìm kiếm **{hoten}**...", parse_mode='Markdown')
        
        results = tim_hoc_sinh_theo_ten(hoten)
        
        if not results:
            await update.message.reply_text(
                f"❌ Không tìm thấy học sinh **{hoten}** trong danh sách!\n\n"
                "📝 Vui lòng kiểm tra lại tên và nhập lại.",
                parse_mode='Markdown'
            )
            return
        
        if len(results) == 1:
            # Tìm thấy 1 học sinh - hiển thị thông tin và hỏi xác nhận
            hs = results[0]
            so_thang = tinh_so_thang_dong(so_tien)
            thang_bat_dau = hs['thang_da_dong'] + 1
            thang_ket_thuc = min(hs['thang_da_dong'] + so_thang, 12)
            
            if thang_bat_dau > 12:
                await update.message.reply_text(
                    f"⚠️ Học sinh **{hs['hoten']}** lớp **{hs['lop']}** đã đóng đủ học phí cả năm (tháng 12)!\n"
                    "Không thể xuất biên lai thêm.",
                    parse_mode='Markdown'
                )
                return
            
            # Tính lại số tháng thực tế nếu vượt quá tháng 12
            so_thang_thuc = thang_ket_thuc - hs['thang_da_dong']
            hoc_phi_lop = lay_hoc_phi_theo_lop(hs['lop'])
            hocphi_thuc = so_thang_thuc * hoc_phi_lop
            
            # Lưu thông tin pending
            pending_receipts[user_id] = {
                'hoten': hs['hoten'],
                'lop': hs['lop'],
                'row_number': hs['row_number'],
                'col_thang': hs['col_thang'],
                'thang_da_dong': hs['thang_da_dong'],
                'thang_bat_dau': thang_bat_dau,
                'thang_ket_thuc': thang_ket_thuc,
                'so_thang': so_thang_thuc,
                'hocphi': hocphi_thuc
            }
            
            # Tạo thông báo xác nhận
            if so_thang_thuc == 1:
                thang_text = f"tháng **{thang_bat_dau}**"
            else:
                thang_text = f"tháng **{thang_bat_dau}** đến tháng **{thang_ket_thuc}**"
            
            confirm_text = (
                f"✅ **Tìm thấy học sinh:**\n\n"
                f"👤 Họ tên: **{hs['hoten']}**\n"
                f"🏫 Lớp: **{hs['lop']}**\n"
                f"📅 Đã đóng đến: **tháng {hs['thang_da_dong']}**\n\n"
                f"📋 **Biên lai sẽ ghi:** {thang_text}\n"
                f"💰 **Số tiền:** {hocphi_thuc:,.0f} VNĐ ({so_thang_thuc} tháng)\n\n"
                f"❓ **Xác nhận in biên lai?**"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("✅ Đồng ý", callback_data="confirm_yes"),
                    InlineKeyboardButton("❌ Hủy", callback_data="confirm_no")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(confirm_text, parse_mode='Markdown', reply_markup=reply_markup)
        
        else:
            # Tìm thấy nhiều học sinh - yêu cầu chọn
            msg = f"🔍 Tìm thấy **{len(results)}** học sinh có tên tương tự:\n\n"
            
            keyboard = []
            for i, hs in enumerate(results[:5]):  # Giới hạn 5 kết quả
                msg += f"{i+1}. **{hs['hoten']}** - Lớp **{hs['lop']}** (đã đóng tháng {hs['thang_da_dong']})\n"
                
                # Lưu thông tin
                data_key = f"select_{i}"
                pending_receipts[f"{user_id}_{data_key}"] = {
                    'hoten': hs['hoten'],
                    'lop': hs['lop'],
                    'row_number': hs['row_number'],
                    'col_thang': hs['col_thang'],
                    'thang_da_dong': hs['thang_da_dong'],
                    'so_tien': so_tien
                }
                
                keyboard.append([InlineKeyboardButton(
                    f"{i+1}. {hs['hoten']} - Lớp {hs['lop']}", 
                    callback_data=data_key
                )])
            
            keyboard.append([InlineKeyboardButton("❌ Hủy", callback_data="confirm_no")])
            
            msg += "\n📌 Vui lòng chọn học sinh:"
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=reply_markup)
    
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text(f"❌ Lỗi: {str(e)}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý khi nhấn nút"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    if data == "confirm_no":
        # Xóa pending
        if user_id in pending_receipts:
            del pending_receipts[user_id]
        # Xóa các select options
        keys_to_delete = [k for k in pending_receipts.keys() if str(k).startswith(f"{user_id}_select_")]
        for k in keys_to_delete:
            del pending_receipts[k]
        
        await query.edit_message_text("❌ Đã hủy. Bạn có thể nhập lại thông tin.")
        return
    
    if data == "delete":
        try:
            await query.message.delete()
        except:
            pass
        return
    
    if data.startswith("select_"):
        # Người dùng chọn học sinh từ danh sách
        key = f"{user_id}_{data}"
        if key not in pending_receipts:
            await query.edit_message_text("❌ Phiên đã hết hạn. Vui lòng nhập lại.")
            return
        
        hs_data = pending_receipts[key]
        so_tien = hs_data['so_tien']
        
        so_thang = tinh_so_thang_dong(so_tien)
        thang_bat_dau = hs_data['thang_da_dong'] + 1
        thang_ket_thuc = min(hs_data['thang_da_dong'] + so_thang, 12)
        
        if thang_bat_dau > 12:
            await query.edit_message_text(
                f"⚠️ Học sinh **{hs_data['hoten']}** đã đóng đủ học phí cả năm!",
                parse_mode='Markdown'
            )
            return
        
        so_thang_thuc = thang_ket_thuc - hs_data['thang_da_dong']
        hoc_phi_lop = lay_hoc_phi_theo_lop(hs_data['lop'])
        hocphi_thuc = so_thang_thuc * hoc_phi_lop
        
        # Lưu thông tin pending
        pending_receipts[user_id] = {
            'hoten': hs_data['hoten'],
            'lop': hs_data['lop'],
            'row_number': hs_data['row_number'],
            'col_thang': hs_data['col_thang'],
            'thang_da_dong': hs_data['thang_da_dong'],
            'thang_bat_dau': thang_bat_dau,
            'thang_ket_thuc': thang_ket_thuc,
            'so_thang': so_thang_thuc,
            'hocphi': hocphi_thuc
        }
        
        # Xóa select options
        keys_to_delete = [k for k in pending_receipts.keys() if str(k).startswith(f"{user_id}_select_")]
        for k in keys_to_delete:
            del pending_receipts[k]
        
        if so_thang_thuc == 1:
            thang_text = f"tháng **{thang_bat_dau}**"
        else:
            thang_text = f"tháng **{thang_bat_dau}** đến tháng **{thang_ket_thuc}**"
        
        confirm_text = (
            f"✅ **Đã chọn học sinh:**\n\n"
            f"👤 Họ tên: **{hs_data['hoten']}**\n"
            f"🏫 Lớp: **{hs_data['lop']}**\n"
            f"📅 Đã đóng đến: **tháng {hs_data['thang_da_dong']}**\n\n"
            f"📋 **Biên lai sẽ ghi:** {thang_text}\n"
            f"💰 **Số tiền:** {hocphi_thuc:,.0f} VNĐ ({so_thang_thuc} tháng)\n\n"
            f"❓ **Xác nhận in biên lai?**"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Đồng ý", callback_data="confirm_yes"),
                InlineKeyboardButton("❌ Hủy", callback_data="confirm_no")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(confirm_text, parse_mode='Markdown', reply_markup=reply_markup)
        return
    
    if data == "confirm_yes":
        # In biên lai
        if user_id not in pending_receipts:
            await query.edit_message_text("❌ Phiên đã hết hạn. Vui lòng nhập lại thông tin.")
            return
        
        receipt_data = pending_receipts[user_id]
        
        await query.edit_message_text("⏳ Đang tạo biên lai...")
        
        # Tạo danh sách tháng
        current_year = datetime.now().year
        thang_list = []
        for t in range(receipt_data['thang_bat_dau'], receipt_data['thang_ket_thuc'] + 1):
            thang_list.append((f"{t:02d}", str(current_year)))
        
        # Tạo file ảnh
        ngay = datetime.now().strftime("%d/%m/%Y")
        thang_str_file = "_".join([f"{t[0]}{t[1]}" for t in thang_list])
        filename = f"BienLai_{receipt_data['hoten'].replace(' ', '_')}_{thang_str_file}.png"
        
        success = tao_bien_lai_image(
            filename, 
            receipt_data['hoten'], 
            receipt_data['lop'], 
            thang_list, 
            receipt_data['hocphi'], 
            ngay
        )
        
        if success and os.path.exists(filename):
            # Gửi biên lai
            keyboard = [[InlineKeyboardButton("🗑 Xóa tin nhắn", callback_data="delete")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            with open(filename, 'rb') as f:
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=f,
                    caption=f"✅ **Biên lai học phí**\n👤 {receipt_data['hoten']}\n🏫 Lớp {receipt_data['lop']}\n💰 {receipt_data['hocphi']:,.0f} VNĐ",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            
            # Cập nhật Google Sheet
            if cap_nhat_thang_da_dong(receipt_data['row_number'], receipt_data['col_thang'], receipt_data['thang_ket_thuc']):
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=f"📊 Đã cập nhật Google Sheets: tháng đã đóng → **{receipt_data['thang_ket_thuc']}**",
                    parse_mode='Markdown'
                )
            
            # Gửi vào group
            if GROUP_CHAT_ID:
                try:
                    if receipt_data['so_thang'] == 1:
                        thang_info = f"tháng {receipt_data['thang_bat_dau']}"
                    else:
                        thang_info = f"tháng {receipt_data['thang_bat_dau']} - {receipt_data['thang_ket_thuc']}"
                    
                    message = f"📋 **BIÊN LAI MỚI**\n\n👤 Họ tên: **{receipt_data['hoten']}**\n🏫 Lớp: **{receipt_data['lop']}**\n📅 Học phí {thang_info}\n💰 Số tiền: **{receipt_data['hocphi']:,.0f} VNĐ**\n🗓 Ngày đóng: {ngay}"
                    
                    with open(filename, 'rb') as f:
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
                os.remove(filename)
            except:
                pass
            
            # Xóa tin nhắn "Đang tạo biên lai..."
            try:
                await query.message.delete()
            except:
                pass
        else:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="❌ Có lỗi khi tạo biên lai. Vui lòng thử lại!"
            )
        
        # Xóa pending
        del pending_receipts[user_id]

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh /help"""
    await start(update, context)

def main():
    """Khởi chạy bot"""
    # Fix cho Windows Python 3.14+
    if sys.platform == 'win32':
        try:
            # Tạo event loop mới cho Windows
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        except:
            pass
    
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8426267636:AAH4VFrILZ_A3vKMzDuzmGFkZbNJ4QZDjTs")
    
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ CHƯA CẤU HÌNH BOT TOKEN!")
        return
    
    print("🔄 Đang kết nối Google Sheets...")
    init_google_sheets()
    
    # Cấu hình timeout dài hơn cho VPS có mạng chậm
    application = Application.builder().token(TOKEN).connect_timeout(30).read_timeout(30).write_timeout(30).pool_timeout(30).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, xu_ly_tin_nhan))
    
    print("🤖 Bot đang chạy...")
    print("📱 Hãy mở Telegram và chat với bot!")
    
    # Xóa webhook trước khi chạy polling (fix conflict) với retry
    max_retries = 3
    for attempt in range(max_retries):
        try:
            asyncio.get_event_loop().run_until_complete(application.bot.delete_webhook(drop_pending_updates=True))
            print("✅ Đã xóa webhook thành công!")
            break
        except Exception as e:
            print(f"⚠️ Lỗi khi xóa webhook (lần {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print("🔄 Thử lại sau 5 giây...")
                import time
                time.sleep(5)
            else:
                print("⚠️ Tiếp tục chạy bot mà không xóa webhook...")
    
    # Chạy polling với retry tự động và xử lý lỗi network
    print("🔄 Đang kết nối Telegram...")
    
    while True:
        try:
            application.run_polling(
                allowed_updates=Update.ALL_TYPES, 
                drop_pending_updates=True,
                pool_timeout=30,
                read_timeout=30,
                write_timeout=30,
                connect_timeout=30
            )
            break  # Nếu chạy thành công và thoát bình thường
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Lỗi kết nối: {error_msg}")
            
            # Kiểm tra nếu là lỗi network thì retry
            if "NetworkError" in error_msg or "timeout" in error_msg.lower() or "ReadError" in error_msg:
                print("⚠️ Lỗi mạng, thử kết nối lại sau 10 giây...")
                import time
                time.sleep(10)
                print("🔄 Đang thử kết nối lại...")
            else:
                # Lỗi khác thì dừng
                print(f"❌ Lỗi nghiêm trọng: {e}")
                raise

if __name__ == '__main__':
    # Retry toàn bộ bot nếu crash
    max_bot_retries = 5
    bot_retry_count = 0
    
    while bot_retry_count < max_bot_retries:
        try:
            main()
            break  # Nếu chạy thành công
        except KeyboardInterrupt:
            print("\n🛑 Đã dừng bot bởi người dùng.")
            break
        except Exception as e:
            bot_retry_count += 1
            print(f"\n❌ Bot gặp lỗi (lần {bot_retry_count}/{max_bot_retries}): {e}")
            if bot_retry_count < max_bot_retries:
                print("🔄 Khởi động lại bot sau 15 giây...")
                import time
                time.sleep(15)
            else:
                print("❌ Đã vượt quá số lần thử, dừng bot.")
                raise
