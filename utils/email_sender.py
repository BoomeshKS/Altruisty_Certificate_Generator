from threading import Thread
from email.message import EmailMessage
import smtplib
import ssl
from config import Config

def send_email_async(name, email, pdf_buffer, filename):
    subject = "🎉 Your Internship Completion Certificate - Altruisty Innovation Pvt Ltd"
    body = f"""
Dear {name},

Congratulations on successfully completing your internship with Altruisty Innovation Pvt Ltd!

Please find your official Certificate of Completion attached.

We wish you continued success in your career.

Best Regards,
Bhavithra A N
HR & Executive Lead
Altruisty Innovation Pvt Ltd
📞 8610604326 | ✉️ altruistybusiness@gmail.com
    """

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = Config.EMAIL_USER
    msg['To'] = email
    msg.set_content(body)
    msg.add_alternative(body.replace('\n', '<br>'), subtype='html')

    pdf_buffer.seek(0)
    msg.add_attachment(pdf_buffer.read(), maintype='application', subtype='pdf', filename=filename)

    def send():
        context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(Config.EMAIL_USER, Config.EMAIL_APP_PASSWORD)
                smtp.send_message(msg)
            print(f"[SUCCESS] Email sent to {email}")
        except Exception as e:
            print(f"[ERROR] Email failed: {e}")

    Thread(target=send).start()