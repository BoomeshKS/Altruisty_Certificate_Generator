from fpdf import FPDF
from io import BytesIO
import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(BASE_DIR, '..', 'static', 'completion_bg.jpg')

def generate_completion_pdf(name, domain, start_date, end_date, duration, regno):
    pdf_buffer = BytesIO()

    class PDF(FPDF):
        def header(self):
            self.image(IMAGE_PATH, 0, 0, 210, 297)

    pdf = PDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_auto_page_break(False)

    # ---------------- DATE (Top Right) ----------------
    current_date = datetime.datetime.now().strftime("%d-%m-%y")
    pdf.set_font("Arial", '', 14)
    pdf.set_xy(140, 80)
    pdf.cell(50, 8, txt=f"DATE: {current_date}", align='R')

    # ---------------- Pronoun ----------------
    pronoun = 'Her' if name.strip().split()[0].lower().endswith(('a', 'i')) else 'His'

    # ---------------- BODY TEXT ----------------
    pdf.set_font("Arial", '', 13)

    left_margin = 10
    text_width = 180
    line_height = 7

    pdf.set_xy(left_margin, 95)

    para1 = (
        f"This is to Certify that {name} has Successfully Completed a {duration} of "
        f"Internship at Altruisty Innovation Pvt Ltd, from {start_date} to {end_date}, "
        f"in the Domain of {domain}."
    )
    pdf.multi_cell(text_width, line_height, para1, align='J')
    pdf.ln(6)

    para2 = (
        f"Throughout the Duration of the Internship, {name} has Demonstrated "
        f"Remarkable Growth and Development, Gaining Valuable Experience and "
        f"Insights Into The Field of {domain}."
    )
    pdf.multi_cell(text_width, line_height, para2, align='J')
    pdf.ln(6)

    para3 = (
        "Their commitment to learning and adapting to new challenges reflects "
        "Altruisty's core values of excellence and innovation."
    )
    pdf.multi_cell(text_width, line_height, para3, align='J')
    pdf.ln(6)

    para4 = (
        f"We hereby acknowledge {name} for {pronoun} outstanding performance "
        f"and dedication during the internship tenure."
    )
    pdf.multi_cell(text_width, line_height, para4, align='J')

    # ---------------- REG NUMBER (Bottom Right) ----------------
    pdf.set_font("Arial", 'B', 13)
    pdf.set_xy(135, 250)
    pdf.cell(60, 8, txt=f"REG:AIPLRP{regno.zfill(4)}", align='R')

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_buffer.write(pdf_bytes)
    pdf_buffer.seek(0)

    return pdf_buffer
