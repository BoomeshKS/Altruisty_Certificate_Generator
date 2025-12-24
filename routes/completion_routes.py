from flask import Blueprint, request, jsonify, render_template, send_file
from utils.pdf_generator import generate_completion_pdf
from utils.email_sender import send_email
from utils.sheet_logger import log_to_sheet_async
from utils.cert_utils import generate_certificate_number
from io import BytesIO
import threading

completion_bp = Blueprint('completion', __name__)

@completion_bp.route('/')
def index():
    return render_template('index.html')

@completion_bp.route('/completion-form')
def completion_form():
    return render_template('completion_form.html')


@completion_bp.route('/generate-completion', methods=['POST'])
def generate_completion():
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        domain = request.form.get('domain')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        duration = request.form.get('duration', '3 Month')
        regno = request.form.get('regno')

        if not all([name, email, domain, start_date, end_date, regno]):
            return jsonify({'error': 'All fields are required'}), 400

        cert_num = generate_certificate_number()

        # Generate PDF
        pdf_buffer = generate_completion_pdf(
            name, domain, start_date, end_date, duration, regno
        )

        filename = f"Altruisty_Completion_Certificate_{name.replace(' ', '_')}.pdf"

        # Log to Google Sheet (already async)
        log_to_sheet_async(name, email, cert_num, domain, start_date, end_date, regno)

        # ✅ SEND EMAIL ASYNC (THIS IS THE KEY FIX)
        if request.form.get('cert-type') == 'online':
            pdf_copy = BytesIO(pdf_buffer.getvalue())

            threading.Thread(
                target=send_email,
                args=(name, email, pdf_copy, filename),
                daemon=True
            ).start()

        # Return PDF immediately (email runs in background)
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        print("🔥 SERVER ERROR:", e)
        return jsonify({'error': 'Server error'}), 500
