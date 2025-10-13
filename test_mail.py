import smtplib
from email.message import EmailMessage

HOST = "mail.privateemail.com"
PORT = 465
USER = "info@elegant.global"
PASS = "ocof-gzrn-bssf-qbjn"

msg = EmailMessage()
msg["Subject"] = "SMTP Test"
msg["From"] = USER
msg["To"] = USER
msg.set_content("This is a test email from Python.")

try:
    print("Connecting to server...")
    with smtplib.SMTP_SSL(HOST, PORT, timeout=10) as server:
        server.set_debuglevel(1)
        server.login(USER, PASS)
        server.send_message(msg)
    print("✅ Email sent successfully!")
except Exception as e:
    print("❌ Failed:", e)
