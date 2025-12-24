from email.message import EmailMessage
import smtplib
import ssl
from config import Config

def send_email(name, email, pdf_buffer, filename):
    subject = "Your Internship Completion Certificate - Altruisty Innovation Pvt Ltd"

    body = f"""
Dear {name},

Congratulations on successfully completing your internship with Altruisty Innovation Pvt Ltd!

Please find your official Certificate of Completion attached.

We wish you continued success in your career.

Best Regards,
Bhavithra A N
HR & Executive Lead
Altruisty Innovation Pvt Ltd
📞 8610604326
    """

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = Config.FROM_EMAIL   # sender
    msg["To"] = email                # recipient
    msg.set_content(body)
    msg.add_alternative(body.replace("\n", "<br>"), subtype="html")

    pdf_buffer.seek(0)
    msg.add_attachment(
        pdf_buffer.read(),
        maintype="application",
        subtype="pdf",
        filename=filename
    )

    print("📨 Sending email via Brevo SMTP...")

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as smtp:
            smtp.starttls(context=context)
            smtp.login(Config.SMTP_LOGIN, Config.SMTP_PASSWORD)
            smtp.send_message(msg)

        print(f"✅ Email sent successfully to {email}")

    except Exception as e:
        print(f"❌ Email failed: {e}")
