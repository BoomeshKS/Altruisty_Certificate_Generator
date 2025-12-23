import requests
from threading import Thread
from config import Config
import datetime

def log_to_sheet_async(name, email, cert_num, domain, start_date, end_date, regno):
    if not Config.GOOGLE_SCRIPT_URL:
        print("Warning: GOOGLE_SCRIPT_URL not set")
        return

    data = {
        "action": "add_completion",
        "name": name,
        "email": email,
        "certificate_number": cert_num,
        "domain": domain,
        "start_date": start_date,
        "end_date": end_date,
        "regno": regno,
        "issued_date": datetime.datetime.now().strftime("%d/%m/%Y")
    }

    def log():
        try:
            requests.post(Config.GOOGLE_SCRIPT_URL, json=data, timeout=10)
            print("Logged to Google Sheet")
        except Exception as e:
            print(f"Sheet log failed: {e}")

    Thread(target=log).start()