import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings


def generate_otp() -> str:
    """Sinh mã xác thực gồm 6 chữ số."""
    return "".join(random.choices("0123456789", k=6))


def send_verification_email(to_email: str, code: str, email_type: str = "register") -> bool:
    """Gửi email chứa mã xác thực OTP qua SMTP Gmail.
    
    email_type có thể là 'register' (đăng ký) hoặc 'forgot' (khôi phục mật khẩu).
    """
    smtp_pass = settings.smtp_password.split("#")[0].strip().strip('"').strip("'")
    from_email = settings.from_email.strip().strip('"').strip("'")
    smtp_host = settings.smtp_host.strip().strip('"').strip("'")

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email

    if email_type == "forgot":
        msg["Subject"] = f"[{code}] Mã xác thực khôi phục mật khẩu CineAI"
        body = f"""Chào bạn,

Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản CineAI của bạn.
Mã xác thực (OTP) của bạn là:

👉 {code} 👈

Mã này có hiệu lực trong vòng 10 phút. Vui lòng không chia sẻ mã này với bất kỳ ai để bảo mật tài khoản.

Nếu bạn không gửi yêu cầu này, vui lòng bỏ qua email này để giữ nguyên mật khẩu cũ.

Trân trọng,
Đội ngũ CineAI.
"""
    else:
        msg["Subject"] = f"[{code}] Mã xác nhận đăng ký tài khoản CineAI"
        body = f"""Chào bạn,

Cảm ơn bạn đã lựa chọn CineAI!
Mã xác nhận (OTP) để kích hoạt tài khoản của bạn là:

👉 {code} 👈

Mã xác thực có hiệu lực trong vòng 10 phút. Vui lòng không chia sẻ mã này với bất kỳ ai.

Nếu bạn không yêu cầu đăng ký tài khoản này, vui lòng bỏ qua email này.

Trân trọng,
Đội ngũ CineAI.
"""

    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        server = smtplib.SMTP(smtp_host, settings.smtp_port)
        server.starttls()
        server.login(from_email, smtp_pass)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Lỗi khi gửi email SMTP: {e}")
        return False


def send_booking_success_email(to_email: str, user_name: str, booking_data: dict) -> bool:
    """Gửi email thông báo đặt vé thành công kèm giao diện vé điện tử HTML đẹp mắt và mã QR."""
    smtp_pass = settings.smtp_password.split("#")[0].strip().strip('"').strip("'")
    from_email = settings.from_email.strip().strip('"').strip("'")
    smtp_host = settings.smtp_host.strip().strip('"').strip("'")

    ticket_code = booking_data.get("ticket_code", "")
    movie_title = booking_data.get("movie_title", "Phim")
    poster_url = booking_data.get("poster_url")
    branch_name = booking_data.get("branch_name", "")
    auditorium_name = booking_data.get("auditorium_name", "")
    starts_at_str = booking_data.get("starts_at")
    
    formatted_time = ""
    if starts_at_str:
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(starts_at_str)
            formatted_time = dt.strftime("%H:%M | %d/%m/%Y")
        except Exception:
            formatted_time = starts_at_str

    seats_list = booking_data.get("seats", [])
    seats_str = ", ".join(seats_list) if seats_list else "Chưa chọn ghế"

    combos = booking_data.get("combos", [])
    total_price = booking_data.get("total_price", 0)
    subtotal_price = booking_data.get("subtotal_price", 0)
    discount_amount = booking_data.get("discount_amount", 0)
    promotion_code = booking_data.get("promotion_code")

    # Xây dựng danh sách combo dạng HTML
    combos_html = ""
    if combos:
        combos_html = '<div class="combo-section"><div class="combo-title">Combo kèm theo</div>'
        for combo in combos:
            name = combo.get("name", "")
            qty = combo.get("quantity", 0)
            line_total = combo.get("line_total", 0)
            combos_html += f"""
            <div class="info-row">
                <div class="info-cell" style="padding: 6px 0; font-size: 13px; color: #94A3B8;">{name} (x{qty})</div>
                <div class="info-cell-val" style="padding: 6px 0; font-size: 13px; text-align: right; font-weight: bold; color: #FFFFFF;">{line_total:,.0f}đ</div>
            </div>
            """
        combos_html += "</div>"

    # Tạo QR Code URL
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={ticket_code}"

    # Dựng poster HTML
    poster_html = ""
    if poster_url:
        poster_html = f'<img src="{poster_url}" alt="{movie_title}" class="movie-poster" />'
    else:
        # Poster placeholder đẹp
        poster_html = f'<div style="width: 80px; height: 115px; background: #334155; border-radius: 8px; border: 1px solid #475569; display: flex; align-items: center; justify-content: center; text-align: center; font-size: 10px; color: #94A3B8; font-weight: bold; overflow: hidden; box-sizing: border-box; padding: 5px;">CineAI</div>'

    # Dựng promotion HTML nếu có
    promo_html = ""
    if discount_amount > 0:
        promo_html = f"""
        <div class="info-row">
            <div class="info-cell" style="padding: 6px 0; font-size: 13px; color: #94A3B8;">Khuyến mãi ({promotion_code or "Khác"})</div>
            <div class="info-cell-val" style="padding: 6px 0; font-size: 13px; text-align: right; font-weight: bold; color: #10B981;">-{discount_amount:,.0f}đ</div>
        </div>
        """

    # Giao diện HTML
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background-color: #0F172A;
      color: #E2E8F0;
      margin: 0;
      padding: 20px;
    }}
    .email-container {{
      max-width: 600px;
      margin: 0 auto;
      background-color: #1E293B;
      border-radius: 24px;
      overflow: hidden;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }}
    .header {{
      background: linear-gradient(135deg, #E11D48 0%, #BE123C 100%);
      padding: 30px;
      text-align: center;
    }}
    .header h1 {{
      margin: 0;
      font-size: 24px;
      color: #FFFFFF;
      font-weight: 800;
      letter-spacing: 1px;
    }}
    .header p {{
      margin: 5px 0 0 0;
      color: #FDA4AF;
      font-size: 14px;
    }}
    .content {{
      padding: 30px;
    }}
    .thank-you {{
      font-size: 14px;
      line-height: 1.6;
      margin-bottom: 25px;
      color: #94A3B8;
    }}
    .thank-you strong {{
      color: #FFFFFF;
    }}
    .ticket-card {{
      background-color: #0F172A;
      border: 1px solid #334155;
      border-radius: 20px;
      overflow: hidden;
      position: relative;
    }}
    .ticket-header {{
      padding: 20px;
      border-bottom: 2px dashed #334155;
      position: relative;
    }}
    .movie-info {{
      display: table;
      width: 100%;
    }}
    .movie-poster-cell {{
      display: table-cell;
      width: 90px;
      vertical-align: top;
    }}
    .movie-poster {{
      width: 80px;
      height: 115px;
      object-fit: cover;
      border-radius: 8px;
      border: 1px solid #475569;
    }}
    .movie-details-cell {{
      display: table-cell;
      vertical-align: top;
      padding-left: 15px;
    }}
    .movie-title {{
      font-size: 18px;
      font-weight: 800;
      color: #FFFFFF;
      margin: 0 0 8px 0;
    }}
    .ticket-meta {{
      font-size: 13px;
      color: #94A3B8;
      line-height: 1.5;
    }}
    .ticket-meta strong {{
      color: #E2E8F0;
    }}
    .ticket-body {{
      padding: 20px;
    }}
    .info-grid {{
      display: table;
      width: 100%;
      margin-bottom: 10px;
    }}
    .info-row {{
      display: table-row;
    }}
    .info-cell {{
      display: table-cell;
      padding: 6px 0;
      font-size: 13px;
      color: #94A3B8;
    }}
    .info-cell-val {{
      display: table-cell;
      padding: 6px 0;
      font-size: 13px;
      text-align: right;
      font-weight: bold;
      color: #FFFFFF;
    }}
    .combo-section {{
      border-top: 1px solid #334155;
      padding-top: 10px;
      margin-top: 10px;
    }}
    .combo-title {{
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: #64748B;
      margin-bottom: 5px;
      font-weight: bold;
    }}
    .payment-summary {{
      border-top: 1px solid #334155;
      padding-top: 15px;
      margin-top: 15px;
    }}
    .total-row {{
      display: table-row;
      font-size: 16px;
    }}
    .total-cell {{
      display: table-cell;
      font-weight: 800;
      color: #FDA4AF;
    }}
    .total-cell-val {{
      display: table-cell;
      text-align: right;
      font-weight: 800;
      color: #F43F5E;
      font-size: 18px;
    }}
    .qr-container {{
      text-align: center;
      padding: 25px 20px;
      background-color: #1E293B;
      border-top: 2px dashed #334155;
      position: relative;
    }}
    .qr-code {{
      background-color: #FFFFFF;
      padding: 10px;
      border-radius: 12px;
      display: inline-block;
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
      margin-bottom: 10px;
    }}
    .qr-code img {{
      display: block;
    }}
    .ticket-code-label {{
      font-size: 11px;
      text-transform: uppercase;
      color: #64748B;
      letter-spacing: 1px;
    }}
    .ticket-code-val {{
      font-family: 'Courier New', Courier, monospace;
      font-size: 18px;
      font-weight: 800;
      color: #FFFFFF;
      letter-spacing: 2px;
      margin-top: 2px;
    }}
    .footer {{
      text-align: center;
      padding: 20px;
      font-size: 12px;
      color: #64748B;
      border-top: 1px solid #334155;
    }}
    .footer a {{
      color: #FDA4AF;
      text-decoration: none;
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <div class="header">
      <h1>CineAI TICKET</h1>
      <p>Đặt vé thành công & xác nhận thanh toán</p>
    </div>
    <div class="content">
      <div class="thank-you">
        Chào <strong>{user_name}</strong>,<br><br>
        Cảm ơn bạn đã lựa chọn <strong>CineAI</strong>! Giao dịch đặt vé của bạn đã được xác nhận thanh toán thành công. Dưới đây là thông tin vé điện tử của bạn:
      </div>
      
      <div class="ticket-card">
        <div class="ticket-header">
          <div class="movie-info">
            <div class="movie-poster-cell">
              {poster_html}
            </div>
            <div class="movie-details-cell">
              <h2 class="movie-title">{movie_title}</h2>
              <div class="ticket-meta">
                Suất chiếu: <strong>{formatted_time}</strong><br>
                Rạp: <strong>{branch_name}</strong>
              </div>
            </div>
          </div>
        </div>
        
        <div class="ticket-body">
          <div class="info-grid">
            <div class="info-row">
              <div class="info-cell" style="padding: 6px 0; font-size: 13px; color: #94A3B8;">Phòng chiếu</div>
              <div class="info-cell-val" style="padding: 6px 0; font-size: 13px; text-align: right; font-weight: bold; color: #FFFFFF; text-transform: uppercase;">{auditorium_name}</div>
            </div>
            <div class="info-row">
              <div class="info-cell" style="padding: 6px 0; font-size: 13px; color: #94A3B8;">Ghế ngồi</div>
              <div class="info-cell-val" style="padding: 6px 0; font-size: 13px; text-align: right; font-weight: bold; color: #FFFFFF;">{seats_str}</div>
            </div>
            <div class="info-row">
              <div class="info-cell" style="padding: 6px 0; font-size: 13px; color: #94A3B8;">Tạm tính</div>
              <div class="info-cell-val" style="padding: 6px 0; font-size: 13px; text-align: right; font-weight: bold; color: #FFFFFF;">{subtotal_price:,.0f}đ</div>
            </div>
            {promo_html}
          </div>
          
          {combos_html}
          
          <div class="info-grid payment-summary" style="border-top: 1px solid #334155; padding-top: 15px; margin-top: 15px;">
            <div class="total-row" style="display: table-row; font-size: 16px;">
              <div class="total-cell" style="display: table-cell; font-weight: 800; color: #FDA4AF;">Tổng tiền</div>
              <div class="total-cell-val" style="display: table-cell; text-align: right; font-weight: 800; color: #F43F5E; font-size: 18px;">{total_price:,.0f}đ</div>
            </div>
          </div>
        </div>
        
        <div class="qr-container">
          <div class="qr-code" style="background-color: #FFFFFF; padding: 10px; border-radius: 12px; display: inline-block; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 10px;">
            <img src="{qr_url}" alt="QR Code" width="130" height="130" style="display: block;" />
          </div>
          <div class="ticket-code-label">Quét mã nhận vé tại quầy</div>
          <div class="ticket-code-val">{ticket_code}</div>
        </div>
      </div>
      
      <div class="thank-you" style="margin-top: 25px; text-align: center; font-size: 13px;">
        💡 <strong>Hướng dẫn nhận vé:</strong> Vui lòng mang email này (hoặc mã vé ở trên) đến quầy soát vé hoặc máy kiosk tại rạp <strong>{branch_name}</strong> trước giờ chiếu ít nhất 10 phút để nhận vé vào phòng chiếu.
      </div>
    </div>
    
    <div class="footer">
      Email này được gửi tự động từ hệ thống đặt vé CineAI.<br>
      Nếu có bất kỳ thắc mắc nào, vui lòng liên hệ bộ phận hỗ trợ của chúng tôi tại <a href="mailto:support@cineai.vn">support@cineai.vn</a>.<br>
      © 2026 CineAI. All rights reserved.
    </div>
  </div>
</body>
</html>
"""

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = f"[CineAI] Xác nhận đặt vé thành công - Mã vé: {ticket_code}"
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    try:
        server = smtplib.SMTP(smtp_host, settings.smtp_port)
        server.starttls()
        server.login(from_email, smtp_pass)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Lỗi khi gửi email SMTP thành công đặt vé: {e}")
        return False
