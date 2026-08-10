import random
import smtplib
import os
import httpx
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from zoneinfo import ZoneInfo
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.commerce import Booking


def generate_otp() -> str:
    """Sinh mã xác thực gồm 6 chữ số."""
    return "".join(random.choices("0123456789", k=6))


def send_smtp_email(to_email: str, subject: str, body: str) -> bool:
    """Gửi email trực tiếp qua SMTP Gmail."""
    smtp_pass = settings.smtp_password.split("#")[0].strip().strip('"').strip("'")
    from_email = settings.from_email.strip().strip('"').strip("'")
    smtp_host = settings.smtp_host.strip().strip('"').strip("'")

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    subtype = "html" if body.strip().startswith("<") else "plain"
    msg.attach(MIMEText(body, subtype, "utf-8"))

    try:
        server = smtplib.SMTP(smtp_host, settings.smtp_port, timeout=10)
        server.starttls()
        server.login(from_email, smtp_pass)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Lỗi khi gửi email SMTP: {e}")
        return False


def send_verification_email(to_email: str, code: str, email_type: str = "register") -> bool:
    """Gửi email chứa mã xác thực OTP qua SMTP Gmail."""
    if email_type == "forgot":
        subject = f"[{code}] Mã xác thực khôi phục mật khẩu CineAI"
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
        subject = f"[{code}] Mã xác nhận đăng ký tài khoản CineAI"
        body = f"""Chào bạn,

Cảm ơn bạn đã lựa chọn CineAI!
Mã xác nhận (OTP) để kích hoạt tài khoản của bạn là:

👉 {code} 👈

Mã xác thực có hiệu lực trong vòng 10 phút. Vui lòng không chia sẻ mã này với bất kỳ ai.

Nếu bạn không yêu cầu đăng ký tài khoản này, vui lòng bỏ qua email này.

Trân trọng,
Đội ngũ CineAI.
"""

    return send_smtp_email(to_email, subject, body)


def send_transactional_email(to_email: str, subject: str, body: str) -> bool:
    """Gửi email giao dịch (hóa đơn vé) qua SMTP."""
    return send_smtp_email(to_email, subject, body)


async def render_notification_email(db: AsyncSession, event_type: str, payload: dict) -> tuple[str, str]:
    """Render notification email subject and body (HTML or text)."""
    if event_type == "TICKET_ISSUED":
        booking_id_str = payload.get("booking_id")
        ticket_code = payload.get("ticket_code", "")
        
        if booking_id_str:
            try:
                booking = await db.get(Booking, uuid.UUID(booking_id_str))
                if booking:
                    # Timezone conversion to Vietnam time
                    vietnam_tz = ZoneInfo("Asia/Ho_Chi_Minh")
                    local_starts_at = booking.showtime.starts_at.astimezone(vietnam_tz)
                    weekdays_vi = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
                    weekday_name = weekdays_vi[local_starts_at.weekday()]
                    showtime_time = f"{local_starts_at.strftime('%H:%M')} - {weekday_name}, {local_starts_at.strftime('%d/%m/%Y')}"
                    
                    movie_title = booking.showtime.movie.title
                    branch_name = booking.showtime.auditorium.branch.name
                    auditorium_name = booking.showtime.auditorium.name
                    seats_list = ", ".join(f"{s.seat.seat_row}{s.seat.seat_number}" for s in booking.seats)
                    
                    combos_row = ""
                    if booking.combos:
                        combos_str = ", ".join(f"{c.combo_name} (x{c.quantity})" for c in booking.combos)
                        combos_row = f"""
                        <tr>
                            <td class="label">Combo bắp nước</td>
                            <td class="value">{combos_str}</td>
                        </tr>
                        """
                        
                    # Build QR code cards for each ticket
                    qr_cards_html = []
                    if booking.tickets:
                        for ticket in booking.tickets:
                            qr_data = f"{settings.frontend_url.rstrip('/')}/t/{ticket.scan_code}"
                            qr_img_src = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_data}"
                            qr_cards_html.append(f"""
                            <div class="qr-card">
                                <img src="{qr_img_src}" width="150" height="150" alt="Mã QR Ghế {ticket.seat_row}{ticket.seat_number}" />
                                <span>Ghế {ticket.seat_row}{ticket.seat_number}</span>
                            </div>
                            """)
                    else:
                        # Fallback to single QR code for booking
                        qr_data = booking.ticket_code or str(booking.id)
                        qr_img_src = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_data}"
                        qr_cards_html.append(f"""
                        <div class="qr-card">
                            <img src="{qr_img_src}" width="150" height="150" alt="Mã QR Vé" />
                            <span>Vé check-in</span>
                        </div>
                        """)
                        
                    qr_cards = "\n".join(qr_cards_html)
                    
                    # HTML template
                    html_body = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121212;
            color: #e0e0e0;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #1e1e1e;
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid #333333;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        }}
        .header {{
            background-color: #ff3344;
            padding: 24px;
            text-align: center;
        }}
        .header h1 {{
            color: #ffffff;
            margin: 0;
            font-size: 24px;
            font-weight: 700;
            letter-spacing: 1px;
        }}
        .content {{
            padding: 24px;
        }}
        .movie-card {{
            background: #2a2a2a;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 24px;
            border-left: 4px solid #ff3344;
        }}
        .movie-title {{
            font-size: 20px;
            font-weight: 700;
            color: #ffffff;
            margin: 0 0 8px 0;
        }}
        .showtime-info {{
            font-size: 14px;
            color: #aaaaaa;
            margin: 4px 0;
        }}
        .details-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 24px;
        }}
        .details-table td {{
            padding: 10px 0;
            border-bottom: 1px solid #333333;
            font-size: 14px;
        }}
        .details-table td.label {{
            color: #aaaaaa;
            width: 40%;
        }}
        .details-table td.value {{
            color: #ffffff;
            font-weight: 600;
            text-align: right;
        }}
        .ticket-code-box {{
            text-align: center;
            background: #2a2a2a;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 24px;
            border: 1px dashed #ff3344;
        }}
        .ticket-code {{
            font-size: 28px;
            font-weight: 800;
            color: #ff3344;
            letter-spacing: 2px;
            margin: 0;
        }}
        .qr-section {{
            text-align: center;
            margin-top: 24px;
            padding-top: 24px;
            border-top: 1px solid #333333;
        }}
        .qr-title {{
            font-size: 16px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 16px;
        }}
        .qr-grid {{
            display: inline-block;
        }}
        .qr-card {{
            display: inline-block;
            background: #ffffff;
            padding: 12px;
            border-radius: 12px;
            margin: 10px;
            text-align: center;
            vertical-align: top;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        .qr-card img {{
            display: block;
            margin: 0 auto 8px auto;
        }}
        .qr-card span {{
            font-size: 14px;
            font-weight: 700;
            color: #121212;
            display: block;
        }}
        .footer {{
            background-color: #171717;
            padding: 16px;
            text-align: center;
            font-size: 12px;
            color: #666666;
            border-top: 1px solid #333333;
        }}
        .footer a {{
            color: #ff3344;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>CINEAI - VÉ XEM PHIM ĐÃ PHÁT HÀNH</h1>
        </div>
        <div class="content">
            <p>Xin chào,</p>
            <p>Thanh toán thành công! Dưới đây là thông tin chi tiết vé xem phim của bạn:</p>
            
            <div class="movie-card">
                <div class="movie-title">{movie_title}</div>
                <div class="showtime-info"><strong>Rạp:</strong> {branch_name} - {auditorium_name}</div>
                <div class="showtime-info"><strong>Suất chiếu:</strong> {showtime_time}</div>
            </div>

            <div class="ticket-code-box">
                <p style="margin: 0 0 8px 0; font-size: 12px; color: #aaaaaa; text-transform: uppercase; letter-spacing: 1px;">Mã đặt vé (Check-in Code)</p>
                <div class="ticket-code">{ticket_code}</div>
            </div>

            <table class="details-table">
                <tr>
                    <td class="label">Ghế đã chọn</td>
                    <td class="value">{seats_list}</td>
                </tr>
                {combos_row}
                <tr>
                    <td class="label">Tổng tiền thanh toán</td>
                    <td class="value" style="color: #ff3344; font-size: 18px;">{booking.total_price:,.0f} VND</td>
                </tr>
            </table>

            <div class="qr-section">
                <div class="qr-title">MÃ QR ĐỂ VÀO PHÒNG CHIẾU</div>
                <p style="font-size: 13px; color: #aaaaaa; margin-bottom: 20px;">Vui lòng đưa mã QR dưới đây cho nhân viên soát vé tại rạp để quét mã vào phòng chiếu.</p>
                <div class="qr-grid">
                    {qr_cards}
                </div>
            </div>
        </div>
        <div class="footer">
            <p>Cảm ơn bạn đã lựa chọn dịch vụ của CineAI.</p>
            <p>Hotline: 1900-CINEAI | Email: <a href="mailto:support@cineai.vn">support@cineai.vn</a></p>
        </div>
    </div>
</body>
</html>"""
                    return f"CineAI - Vé xem phim của bạn {ticket_code}", html_body
            except Exception as e:
                print(f"Lỗi khi render email chi tiết: {e}")
                
        return "Vé CineAI đã được phát hành", f"Thanh toán thành công. Mã đặt vé: {ticket_code}."

    if event_type == "PAYMENT_RECONCILIATION_REQUIRED":
        html_body = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121212;
            color: #e0e0e0;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #1e1e1e;
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid #333333;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        }}
        .header {{
            background-color: #f59e0b;
            padding: 24px;
            text-align: center;
        }}
        .header h1 {{
            color: #ffffff;
            margin: 0;
            font-size: 24px;
            font-weight: 700;
            letter-spacing: 1px;
        }}
        .content {{
            padding: 24px;
            line-height: 1.6;
        }}
        .footer {{
            background-color: #171717;
            padding: 16px;
            text-align: center;
            font-size: 12px;
            color: #666666;
            border-top: 1px solid #333333;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>CINEAI - THÔNG BÁO KIỂM TRA GIAO DỊCH</h1>
        </div>
        <div class="content">
            <p>Xin chào,</p>
            <p>Khoản thanh toán của bạn đã được ghi nhận sau khi giữ chỗ hết hạn. CineAI đang tiến hành đối soát và sẽ hoàn tiền nếu không thể cấp vé.</p>
            <p>Chúng tôi sẽ cập nhật tình trạng giao dịch sớm nhất đến bạn.</p>
        </div>
        <div class="footer">
            <p>Cảm ơn bạn đã lựa chọn dịch vụ của CineAI.</p>
        </div>
    </div>
</body>
</html>"""
        return "Giao dịch CineAI đang được kiểm tra", html_body

    # Default fallback
    html_body = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121212;
            color: #e0e0e0;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #1e1e1e;
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid #333333;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        }}
        .header {{
            background-color: #ff3344;
            padding: 24px;
            text-align: center;
        }}
        .header h1 {{
            color: #ffffff;
            margin: 0;
            font-size: 24px;
            font-weight: 700;
            letter-spacing: 1px;
        }}
        .content {{
            padding: 24px;
            line-height: 1.6;
        }}
        .footer {{
            background-color: #171717;
            padding: 16px;
            text-align: center;
            font-size: 12px;
            color: #666666;
            border-top: 1px solid #333333;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>CINEAI - THÔNG BÁO</h1>
        </div>
        <div class="content">
            <p>{str(payload)}</p>
        </div>
        <div class="footer">
            <p>Cảm ơn bạn đã lựa chọn dịch vụ của CineAI.</p>
        </div>
    </div>
</body>
</html>"""
    return "Thông báo từ CineAI", html_body


