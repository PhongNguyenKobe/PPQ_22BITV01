import random
import smtplib
import os
import httpx
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings


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
    msg.attach(MIMEText(body, "plain", "utf-8"))

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

