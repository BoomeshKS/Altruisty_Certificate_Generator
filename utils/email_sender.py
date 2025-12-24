# from email.message import EmailMessage
# import smtplib
# import ssl
# from config import Config

# def send_email(name, email, pdf_buffer, filename):
#     subject = "Your Internship Completion Certificate - Altruisty Innovation Pvt Ltd"

#     body = f"""
# Dear {name},

# Congratulations on successfully completing your internship with Altruisty Innovation Pvt Ltd!

# Please find your official Certificate of Completion attached.

# We wish you continued success in your career.

# Best Regards,
# Bhavithra A N
# HR & Executive Lead
# Altruisty Innovation Pvt Ltd
# 📞 8610604326
#     """

#     msg = EmailMessage()
#     msg["Subject"] = subject
#     msg["From"] = Config.FROM_EMAIL   # sender
#     msg["To"] = email                # recipient
#     msg.set_content(body)
#     msg.add_alternative(body.replace("\n", "<br>"), subtype="html")

#     pdf_buffer.seek(0)
#     msg.add_attachment(
#         pdf_buffer.read(),
#         maintype="application",
#         subtype="pdf",
#         filename=filename
#     )

#     print("📨 Sending email via Brevo SMTP...")

#     context = ssl.create_default_context()
#     try:
#         with smtplib.SMTP(
#             Config.SMTP_SERVER,
#             Config.SMTP_PORT,
#             timeout=10   # 🔑 prevents worker hang
#         ) as smtp:
#             smtp.starttls(context=context)
#             smtp.login(Config.SMTP_LOGIN, Config.SMTP_PASSWORD)
#             smtp.send_message(msg)

#         print(f"✅ Email sent successfully to {email}")

#     except Exception as e:
#         print(f"❌ Email failed: {e}")



import requests
import base64
from config import Config

def send_email(name, email, pdf_buffer, filename):
    """
    Sends email using Brevo HTTP API (NO SMTP)
    This is Render-safe and does not timeout
    """

    print("📨 Sending email via Brevo API...")

    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": Config.BREVO_API_KEY,
        "content-type": "application/json"
    }

    # Encode PDF to base64 (required by Brevo API)
    pdf_buffer.seek(0)
    encoded_pdf = base64.b64encode(pdf_buffer.read()).decode("utf-8")

    payload = {
        "sender": {
            "email": Config.FROM_EMAIL,
            "name": "Altruisty Innovation"
        },
        "to": [
            {
                "email": email,
                "name": name
            }
        ],
        "subject": "Your Internship Completion Certificate - Altruisty Innovation Pvt Ltd",
        "htmlContent": f"""
        <p>Dear {name},</p>

        <p>Congratulations on successfully completing your internship with
        <b>Altruisty Innovation Pvt Ltd</b>.</p>

        <p>Please find your official Certificate of Completion attached.</p>

        <p>We wish you continued success in your career.</p>

        <br>

        <p>
        Best Regards,<br>
        <b>Bhavithra A N</b><br>
        HR & Executive Lead<br>
        Altruisty Innovation Pvt Ltd<br>
        📞 8610604326
        </p>
        """,
        "attachment": [
            {
                "content": encoded_pdf,
                "name": filename
            }
        ]
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=10
    )

    if response.status_code >= 300:
        raise Exception(response.text)

    print(f"✅ Email sent via Brevo API to {email}")
