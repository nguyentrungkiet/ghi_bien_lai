import os
import sys
from datetime import datetime
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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
# Khi deploy lên cloud, thay đổi thành:
# LOGO_PATH = "logo.jpg"  (nếu upload cùng code)
# hoặc LOGO_PATH = "https://url-logo-của-bạn.jpg"  (nếu dùng URL)
LOGO_PATH = os.getenv("LOGO_PATH", "logo.jpg")  # Ưu tiên lấy từ biến môi trường
DAM_MOC_PATH = ""  # Bỏ dấu mộc

# Kiểm tra xem file logo có tồn tại local không, nếu không thì có thể là URL
if LOGO_PATH and not LOGO_PATH.startswith("http") and not os.path.exists(LOGO_PATH):
    print(f"⚠️ Cảnh báo: Không tìm thấy logo tại {LOGO_PATH}")
    LOGO_PATH = ""  # Bỏ qua nếu không tìm thấy

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
        if LOGO_PATH and os.path.exists(LOGO_PATH):
            try:
                c.drawImage(LOGO_PATH, 3*cm, height-5*cm, width=3*cm, height=3*cm, preserveAspectRatio=True)
            except:
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
    welcome_text = """
🎓 **BIÊN LAI HỌC PHÍ TỰ ĐỘNG**

Chào mừng bạn! Bot này giúp tạo biên lai học phí nhanh chóng.

📝 **Cách sử dụng:**

**Siêu ngắn gọn (khuyên dùng):**
```
Huỳnh Trân lớp 8 tháng 7 350k
```

**Nhiều tháng (cách 1):**
```
Nguyễn Văn A lớp 7 tháng 1 tháng 2 tháng 3 450k
```

**Nhiều tháng (cách 2 - ngắn hơn):**
```
Nguyễn Văn A lớp 7 tháng 1+2+3 450k
```

**Hoặc đầy đủ:**
```
Họ tên: Nguyễn Văn A
Lớp: 7A
Tháng: 01/2026, 02/2026
Học phí: 1500000
```

**Đơn vị học phí:**
- `350k` = 350,000 đồng
- `1.5tr` = 1,500,000 đồng
- `350000` = 350,000 đồng

🚀 Gửi thông tin ngay để nhận biên lai PDF!
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
                    "`Nguyễn Văn A lớp 7 tháng 1 350k`",
                    parse_mode='Markdown'
                )
                return
            
            hoten = parts[0]
            lop = parts[1]
            thang_str = parts[2]
            hocphi_str = parts[3]
        else:
            # Định dạng tự nhiên: "Họ tên lớp X tháng Y số_tiền"
            import re
            
            # Tìm lớp (sau từ khóa "lớp" hoặc "lop")
            lop_match = re.search(r'l[oớ]p\s+(\w+)', text, re.IGNORECASE)
            if not lop_match:
                await update.message.reply_text(
                    "❌ Không tìm thấy thông tin lớp!\n\n"
                    "Ví dụ: `Nguyễn Văn A lớp 7 tháng 1 350k`",
                    parse_mode='Markdown'
                )
                return
            lop = lop_match.group(1)
            
            # Tìm tháng (sau từ khóa "tháng" hoặc "thang")
            # Hỗ trợ: "tháng 7", "tháng 7+8", "tháng 1 tháng 2"
            
            # Tìm pattern "tháng X+Y+Z" hoặc "tháng X"
            thang_plus_match = re.search(r'th[aá]ng\s+([\d+]+)', text, re.IGNORECASE)
            
            if thang_plus_match:
                # Xử lý dạng "7+8+9" hoặc "7"
                thang_str_raw = thang_plus_match.group(1)
                if '+' in thang_str_raw:
                    # Tách các tháng bằng dấu +
                    thang_matches = thang_str_raw.split('+')
                else:
                    # Chỉ có 1 tháng hoặc tìm nhiều lần "tháng X"
                    thang_matches = re.findall(r'th[aá]ng\s+(\d+(?:/\d+)?)', text, re.IGNORECASE)
            else:
                thang_matches = re.findall(r'th[aá]ng\s+(\d+(?:/\d+)?)', text, re.IGNORECASE)
            
            if not thang_matches:
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
        for item in thang_str.replace(" ", "").split(","):
            if "/" in item:
                parts = item.split("/")
                thang_list.append((parts[0].zfill(2), parts[1]))
        
        if not thang_list:
            await update.message.reply_text("❌ Định dạng tháng không đúng! Ví dụ: 01/2026 hoặc 01/2026, 02/2026")
            return
        
        # Parse học phí
        hocphi = float(hocphi_str.replace(",", "").replace(".", "").replace(" ", ""))
        
        # Ngày đóng tiền
        ngay = datetime.now().strftime("%d/%m/%Y")
        
        # Tạo file PDF
        await update.message.reply_text("⏳ Đang tạo biên lai...")
        
        thang_str_file = "_".join([f"{t[0]}{t[1]}" for t in thang_list])
        filename = f"BienLai_{hoten.replace(' ', '_')}_{thang_str_file}.pdf"
        file_path = filename
        
        success = tao_bien_lai_pdf(file_path, hoten, lop, thang_list, hocphi, ngay)
        
        if success and os.path.exists(file_path):
            # Gửi file PDF
            with open(file_path, 'rb') as f:
                await update.message.reply_document(
                    document=f,
                    filename=filename,
                    caption=f"✅ Biên lai học phí\n👤 {hoten}\n🏫 Lớp {lop}\n💰 {hocphi:,.0f} VNĐ"
                )
            
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
    
    # Tạo application
    application = Application.builder().token(TOKEN).build()
    
    # Đăng ký handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, xu_ly_tin_nhan))
    
    # Chạy bot
    print("🤖 Bot đang chạy...")
    print("📱 Hãy mở Telegram và chat với bot!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
