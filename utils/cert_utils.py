import string
import random
import base64

def generate_certificate_number():
    metadata = "2025-AI"
    encoded = base64.b32encode(metadata.encode()).decode()[:6]
    uid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return encoded + uid