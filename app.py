
from flask import Flask, request, jsonify, render_template, send_file, render_template_string
from flask_sqlalchemy import SQLAlchemy
import string
import random
from fpdf import FPDF
import os
import smtplib
from email.message import EmailMessage
import PyPDF2
import ssl
import base64
import datetime
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import json
import re


app = Flask(__name__)

# SQLAlchemy configuration for PostgreSQL with URL-encoded password
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mydb_lwg8_user:InaUxSVvr50LjTwSA8iXzChEIRaO9CEG@dpg-d2k7ug3e5dus738ufen0-a.singapore-postgres.render.com/mydb_lwg8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from flask_cors import CORS
CORS(app)

# Define SQLAlchemy models
class Certificate(db.Model):
    __tablename__ = 'certificates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    certificate_number = db.Column(db.String(50), unique=True, nullable=False)

class CompletedIntern(db.Model):
    __tablename__ = 'completed_interns'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    certificate_number = db.Column(db.String(50), unique=True, nullable=False)
    domain = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.String(50), nullable=True)
    end_date = db.Column(db.String(50), nullable=True)

# Initialize database tables
with app.app_context():
    db.create_all()

def send_certificate_email(name, email, filepath, cert_type='offer_letter', start_date=None, end_date=None):
    generator = ProfessionalCertificateEmailGenerator()

    # Customize data for personalization
    personalization_data = {
        'start_date': start_date or 'Soon',
        'end_date': end_date or 'Later',
        'duration': '17',
        'projects_count': '3',
        'key_skills': 'problem-solving, teamwork, and creativity',
        'mentor_name': 'the project team',
        'name': name
    }

    subject, body, html_body = generator.generate_certificate_email(
        cert_type=cert_type,
        recipient_name=name,
        personalization_data=personalization_data
    )

    # Construct the email message
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = 'hraltruisty@gmail.com'
    msg['To'] = email
    msg.set_content(body)
    msg.add_alternative(html_body, subtype='html')

    # Attach the PDF certificate
    with open(filepath, 'rb') as f:
        file_data = f.read()
        file_name = os.path.basename(filepath)
        msg.add_attachment(file_data, maintype='application', subtype='pdf', filename=file_name)

    # Send email using Gmail's SMTP server
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login('hraltruisty@gmail.com', 'oryt atuj rsji ypnv')
            smtp.send_message(msg)
        print(f"[SUCCESS] Email sent to {email}")
    except Exception as e:
        print(f"[ERROR] Failed to send email to {email}: {str(e)}")

# Utility function to generate unique certificate number
def generate_certificate_number():
    metadata = "2025-AI"
    encoded = base64.b32encode(metadata.encode()).decode()[:6]
    uid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    cert_num = encoded + uid
    existing = Certificate.query.filter_by(certificate_number=cert_num).first()
    if not existing:
        return cert_num
    else:
        return generate_certificate_number()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/offer-form')
def offer_form():
    return render_template('generate.html')

@app.route('/generate', methods=['POST'])
def generate_certificate():
    name = request.form.get('name')
    email = request.form.get('email')
    domain = request.form.get('domain')
    start_date = request.form.get('start_date')
    duration = request.form.get('duration')
    regno = request.form.get('regno')

    if not name or not email or not domain or not start_date or not duration or not regno:
        return jsonify({'error': 'All fields are required'}), 400
    
    cert_num = generate_certificate_number()

    class PDF(FPDF):
        def header(self):
            self.image('static/Intern_OL.jpg', 0, 0, 210, 297)
    pdf = PDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_margins(20, 20, 20)

    # Top-right date
    pdf.set_font("Arial", '', 12)
    current_date = datetime.datetime.now().strftime("%d-%m-%y")
    pdf.set_xy(159, 70)
    pdf.cell(40, 10, txt=f"DATE: {current_date}", border=0)

    # Top-left name line
    pdf.set_font("Arial", 'B', 12)
    pdf.set_xy(20, 80)
    pdf.cell(0, 10, txt=f"Dear {name},", ln=True)

    # Body paragraphs
    pdf.set_font("Arial", '', 13)
    pdf.set_xy(20, 95)
    para1 = (
        f"We are thrilled to inform you that you have been selected to participate in the Altruisty "
        f"Innovation Pvt Ltd Internship Program in the domain of {domain}. Congratulations!"
    )
    para2 = (
        f"The internship will commence on {start_date} and will last for a duration of "
        f"{duration}. During this time, you will have the opportunity to gain practical experience, learn from "
        f"industry experts, and collaborate with a team of domain professionals."
    )
    para3 = (
        "We are confident that your skills and dedication will contribute greatly to the success "
        "of our program, and we look forward to seeing the valuable contributions you will make."
    )
    pdf.multi_cell(170, 7, para1, 0, 'J')
    pdf.ln(4)
    pdf.multi_cell(170, 7, para2, 0, 'J')
    pdf.ln(4)
    pdf.multi_cell(170, 7, para3, 0, 'J')

    # Reg No at bottom
    pdf.set_font("Arial", 'B', 12)
    pdf.set_xy(150, 250)
    pdf.cell(0, 10, txt=f"Reg No - {regno}", align='L')

    # Save to temp file
    cert_filename = f"Altruisty_Offer_Letter_{name.replace(' ', '_')}.pdf"
    cert_path = os.path.join('certificates', cert_filename)
    os.makedirs('certificates', exist_ok=True)

    try:
        pdf.output(cert_path)
    except Exception as e:
        return jsonify({'error': f'Failed to generate certificate: {str(e)}'}), 500

    # Save to DB and send email (your original code)
    try:
        new_certificate = Certificate(name=name, email=email, certificate_number=cert_num)
        db.session.add(new_certificate)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Database error: {e}")
        return jsonify({'error': f'Failed to save certificate to database: {str(e)}'}), 500

    send_certificate_email(
        name, email, cert_path,
        cert_type='offer_letter',
        start_date=start_date,
        end_date=None  # if you want to calculate end_date from start+duration, let me know
    )

    # Directly send file to download in browser
    return send_file(
        cert_path,
        as_attachment=True,
        download_name=cert_filename,
        mimetype='application/pdf',
    )



@app.route('/completion-form')
def completion_form():
    return render_template('completion_form.html')

@app.route('/generate-completion', methods=['POST'])
def generate_completion_certificate():
    name = request.form.get('name')
    email = request.form.get('email')
    domain = request.form.get('domain', 'Web Development')
    start_date = request.form.get('start_date', '08-07-2024')
    end_date = request.form.get('end_date', '08-11-2024')
    duration = request.form.get('duration', '4 months')
    regno = request.form.get('regno')
    cert_type = request.form.get('cert-type')

    if not name or not email:
        return jsonify({'error': 'Name and email are required'}), 400

    cert_num = generate_certificate_number()

    # Very basic gender guess based on name endings
    def guess_gender(name):
        if name.strip().split()[0].lower().endswith(('a', 'i')):
            return 'her'
        return 'his'

    gender_pronoun = guess_gender(name)
    name_first = name.split()[0]
    name_last = name.split()[-1] if len(name.split()) > 1 else ''

    class PDF(FPDF):
        def header(self):
            template_image = 'noseal.png' if cert_type == 'offline' else 'intern_CC.png'
            self.image(template_image, 0, 0, 210, 297)

    pdf = PDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    pdf.set_font("Arial", '', 12)

    # Top right date
    pdf.set_xy(159, 80)
    date_str = datetime.datetime.now().strftime("%d-%m-%y")
    pdf.cell(40, 10, txt=f"DATE: {date_str}", border=0)

    # Content
    pdf.set_xy(20, 100)
    pdf.set_font("Arial", '', 11)
    
    
    if cert_type == 'offline':
        paragraph1 = (
            f"This is to Certify that {name} has Successfully Completed a {duration} of Internship "
            f"at Altruisty Innovation Pvt Ltd, from {start_date} to {end_date}, in the Domain of "
            f"{domain}."
        )
        paragraph2 = (
            f"Throughout the Duration of the Internship, {name} has Demonstrated Remarkable "
            f"Growth and Development, Gaining Valuable Experience and Insights Into The Field of "
            f"{domain}."
        )
        paragraph3 = (
            "Their commitment to learning and adapting to new challenges reflects Altruisty's core "
            "values of excellence and innovation."
        )
        paragraph4 = (
            f"We hereby acknowledge {name} for {gender_pronoun} outstanding performance "
            f"and dedication during the internship tenure."
        )
    else:
        paragraph1 = (
            f"This is to certify that {name} has successfully completed {duration} of internship "
            f"with Altruisty Innovation Pvt Ltd. from {start_date} to {end_date}, in the domain of "
            f"{domain}."
        )
        paragraph2 = (
            f"Throughout the duration of the internship, {name} has demonstrated remarkable "
            "growth and development, gaining valuable experience and insights into the field of "
            f"{domain}."
        )
        paragraph3 = (
            "Their commitment to learning and adapting to new challenges reflects Altruisty's core "
            "values of excellence and innovation."
        )
        paragraph4 = (
            f"We hereby acknowledge {name} for {gender_pronoun} outstanding performance "
            f"and dedication during the internship tenure."
        )

    # Draw text
    pdf.multi_cell(170, 6, txt=paragraph1, border=0, align='J')
    pdf.ln(5)
    pdf.multi_cell(170, 6, txt=paragraph2, border=0, align='J')
    pdf.ln(5)
    pdf.multi_cell(170, 6, txt=paragraph3, border=0, align='J')
    pdf.ln(5)
    pdf.multi_cell(170, 6, txt=paragraph4, border=0, align='J')
    pdf.ln(15)

    pdf.set_xy(20, 260)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, txt=f"Certificate Number: {cert_num}", border=0, align='C')

    pdf.set_font("Arial", 'B', 12)
    pdf.set_xy(150, 250)
    pdf.cell(0, 10, txt=f"Reg No - {regno}", align='L')

    cert_filename = f"completion_certificate_{cert_num}.pdf"
    cert_path = os.path.join('certificates', cert_filename)
    os.makedirs('certificates', exist_ok=True)

    try:
        pdf.output(cert_path)
    except Exception as e:
        return jsonify({'error': f'Failed to generate certificate: {str(e)}'}), 500

    try:
        new_intern = CompletedIntern(
            name=name,
            email=email,
            certificate_number=cert_num,
            domain=domain,
            start_date=start_date,
            end_date=end_date
        )
        db.session.add(new_intern)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Database error: {e}")
        return jsonify({'error': f'Failed to save certificate to database: {str(e)}'}), 500

    # Only send email if cert_type is not 'offline'
    if cert_type == 'online':
        send_certificate_email(name, email, cert_path, cert_type='completion')

    return send_file(
        cert_path,
        as_attachment=True,
        download_name=f"Altruisty_Completion_Certificate_{name.replace(' ', '_')}.pdf",
        mimetype='application/pdf'
    )




@app.route('/verify', methods=['GET', 'POST'])
def verify_certificate():
    result = None
    if request.method == 'POST':
        if 'certificate' not in request.files:
            result = "No file part"
            return render_template('verify.html', result=result)
        file = request.files['certificate']
        if file.filename == '':
            result = "No selected file"
            return render_template('verify.html', result=result)
        if file:
            filepath = os.path.join('uploads', file.filename)
            os.makedirs('uploads', exist_ok=True)
            file.save(filepath)
            try:
                with open(filepath, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()
                print("Extracted text from PDF:", text)
            except Exception as e:
                result = f"Error reading PDF: {str(e)}"
                os.remove(filepath)
                return render_template('verify.html', result=result)
            name = None
            cert_num = None
            cert_type = request.form.get('cert_type', 'offer_letter')
            match_name = None
            if cert_type == 'completion':
                match_name = re.search(r"This is to certify that\s+([A-Za-z\s]+?)\s+has successfully completed", text, re.IGNORECASE)
            if not match_name:
                match_name = re.search(r"Dear\s+([A-Za-z\s\.]+)", text, re.IGNORECASE)
            if not match_name:
                match_name_alt = re.search(r"Presented to:\s*\n?(.*)", text, re.IGNORECASE)
                if match_name_alt:
                    name = match_name_alt.group(1).strip()
                else:
                    name = None
            else:
                name = match_name.group(1).strip()
            match_cert = re.search(r"Certificate Number:\s*(\S+)", text, re.IGNORECASE)
            if match_cert:
                cert_num = match_cert.group(1).strip()
            print(f"Parsed name: {name}, certificate number: {cert_num}")
            if not name:
                name = None
            if not cert_num:
                cert_num = ""
            cert_type = request.form.get('cert_type', 'offer_letter')
            try:
                if cert_type == 'offer_letter':
                    record = Certificate.query.filter_by(name=name, certificate_number=cert_num).first()
                elif cert_type == 'completion':
                    record = CompletedIntern.query.filter_by(name=name, certificate_number=cert_num).first()
                else:
                    result = "Invalid certificate type"
                    return render_template('verify.html', result=result)
                result = "Original" if record else "Duplicate"
            except Exception as e:
                result = f"Database error: {str(e)}"
            os.remove(filepath)
    return render_template('verify.html', result=result)

class CertificateType(Enum):
    OFFER_LETTER = "offer_letter"
    COMPLETION = "completion"
    ACHIEVEMENT = "achievement"
    PARTICIPATION = "participation"
    EXCELLENCE = "excellence"
    LEADERSHIP = "leadership"
    CUSTOM = "custom"

@dataclass
class EmailTemplate:
    subject: str
    greeting: str
    main_content: str
    closing: str
    signature: str
    tone: str
    priority: str

class ProfessionalCertificateEmailGenerator:
    def __init__(self):
        self.templates = self._initialize_templates()
        self.personalization_data = {}
        self.branding_config = self._load_branding_config()

    def _initialize_templates(self) -> Dict[CertificateType, EmailTemplate]:
        return {
            CertificateType.OFFER_LETTER: EmailTemplate(
                subject="📋Your Internship Offer Letter",
                greeting="Dear {name},",
#                 main_content="""
# We are absolutely thrilled to extend this internship opportunity to you!

# Your application stood out among hundreds of candidates, and we're excited to have someone with your passion and potential join the Altruisty Innovation family.

# 📋 **What's Next:**
# • Review your comprehensive offer letter attached
# • Complete onboarding materials (deadline: {deadline})
# • Join our welcome orientation on {start_date}

# This is just the beginning of an incredible journey that will shape your professional future. We can't wait to see the amazing contributions you'll make to our team!
#                 """,
                main_content="""
Thank you for joining Altruisty! We’re thrilled to have you on board. We hope it will be a fulfilling and enriching experience for you.

Feel free to reach out to us for any assistance during your internship. Your offer letter is attached for your reference.

We encourage you to share this exciting opportunity on LinkedIn and in the WhatsApp group to celebrate this milestone!
                """,
                closing="Welcome aboard,",
                signature="Hr & Business Analyst, Altruisty,\n\t8610604326",
                tone="enthusiastic",
                priority="high"
            ),


            CertificateType.COMPLETION: EmailTemplate(
                subject="📋Your Completion Certificate",
                greeting="Dear {name},",
                main_content="""
I hope this email finds you well. Congratulations on successfully completing your internship with Altruisty!

As a token of recognition for your dedication and hard work, please find attached your Certificate of Completion for the internship. This certificate acknowledges your contributions and the skills you demonstrated during your time with us.

We are grateful for your efforts and commitment to the projects you undertook. It has been a pleasure having you on the team, and we wish you the very best in all your future endeavors.

Should you need any further assistance or recommendations, please feel free to reach out.
                """,
                closing="Best regards,\n aboard,",
                signature="Hr & Business Analyst, Altruisty \n 8610604326",
                tone="celebratory",
                priority="high"
            ),

            CertificateType.ACHIEVEMENT: EmailTemplate(
                subject="🌟 Outstanding Achievement Recognition - You're Exceptional!",
                greeting="Dear {name},",
                main_content="""
Excellence deserves recognition, and today we celebrate YOU!

Your exceptional performance in {achievement_area} has set a new standard of excellence. This achievement certificate represents not just what you've accomplished, but the dedication and passion you bring to everything you do.

🏅 **Recognition Details:**
• Achievement Category: {category}
• Recognition Level: {level}
• Awarded by: {awarding_body}

Your commitment to excellence inspires everyone around you. This certificate is our way of saying thank you for raising the bar and showing what's possible when talent meets determination.
                """,
                closing="In recognition of your excellence,",
                signature="Certificate Authority Board\n🎖️ Honoring Outstanding Achievement",
                tone="formal_celebratory",
                priority="medium"
            ),

            CertificateType.PARTICIPATION: EmailTemplate(
                subject="🤝 Thank You for Your Valuable Participation!",
                greeting="Dear {name},",
                main_content="""
Your active participation has made all the difference!

Thank you for being an engaged and valuable contributor to {event_name}. Your insights, questions, and collaborative spirit enriched the experience for everyone involved.

📝 **Event Summary:**
• Duration: {duration}
• Your Contribution: {contribution_highlights}
• Key Learnings: {key_takeaways}

We hope this experience has been as valuable for you as your participation was for us. Your certificate of participation is attached as a recognition of your commitment to continuous learning and growth.
                """,
                closing="With appreciation,",
                signature="Event Coordination Team\n🌐 Fostering Learning Communities",
                tone="appreciative",
                priority="medium"
            ),

            CertificateType.EXCELLENCE: EmailTemplate(
                subject="💎 Excellence Award - You've Set the Gold Standard!",
                greeting="Dear {name},",
                main_content="""
Extraordinary performance deserves extraordinary recognition!

You have consistently demonstrated excellence that goes far beyond expectations. This certificate of excellence is awarded to individuals who embody the highest standards of {excellence_domain}.

🏆 **Excellence Criteria Met:**
• Exceptional Quality: {quality_metrics}
• Leadership Impact: {leadership_examples}
• Innovation Contribution: {innovation_highlights}

Your commitment to excellence has not only achieved remarkable results but has also inspired others to reach new heights. You are truly setting the gold standard in your field.
                """,
                closing="In honor of your exceptional achievements,",
                signature="Excellence Recognition Committee\n👑 Celebrating Peak Performance",
                tone="prestigious",
                priority="high"
            ),

            CertificateType.LEADERSHIP: EmailTemplate(
                subject="👑 Leadership Recognition - Inspiring Others Through Example",
                greeting="Dear {name},",
                main_content="""
True leadership is about inspiring others to achieve greatness, and you exemplify this every day!

Your leadership certificate recognizes not just what you've accomplished, but how you've empowered others to succeed alongside you. Your ability to {leadership_strength} has made a lasting impact on everyone you've worked with.

🌟 **Leadership Impact Areas:**
• Team Development: {team_achievements}
• Strategic Vision: {vision_implementation}
• Mentorship Excellence: {mentorship_impact}

Great leaders are remembered not for what they achieved alone, but for what they helped others achieve. Thank you for being that kind of leader.
                """,
                closing="In recognition of your inspiring leadership,",
                signature="Leadership Development Institute\n🚀 Developing Tomorrow's Leaders",
                tone="inspirational",
                priority="high"
            )
        }

    def _load_branding_config(self) -> Dict:
        return {
            "primary_color": "#2E86AB",
            "secondary_color": "#A23B72",
            "accent_color": "#F18F01",
            "logo_url": "https://altruisty.in/static/images/logo.png",            
            "social_media": {
                "linkedin": "https://linkedin.com/company/altruisty",
                "twitter": "@Altruisty",
                "website": "https://altruisty.in/"
            },
            "footer_tagline": "Empowering Innovation • Building Futures • Creating Impact"
        }
    
    def generate_certificate_email(self, 
                                 cert_type: str, 
                                 recipient_name: str,
                                 personalization_data: Optional[Dict] = None,
                                 custom_template: Optional[Dict] = None) -> Tuple[str, str, str]:
        try:
            certificate_type = CertificateType(cert_type.lower())
        except ValueError:
            certificate_type = CertificateType.CUSTOM
        
        if custom_template:
            template = self._create_custom_template(custom_template)
        else:
            template = self.templates.get(certificate_type, self._get_default_template())
        
        person_data = personalization_data or {}
        person_data['name'] = recipient_name
        person_data.setdefault('date', datetime.datetime.now().strftime("%B %d, %Y"))
        
        subject = self._personalize_content(template.subject, person_data)
        body = self._generate_text_body(template, person_data)
        html_body = self._generate_html_body(template, person_data)
        
        return subject, body, html_body
    
    def _personalize_content(self, content: str, data: Dict) -> str:
        try:
            return content.format(**data)
        except KeyError as e:
            missing_key = str(e).strip("'")
            data[missing_key] = f"[{missing_key}]"
            return content.format(**data)
    
    def _generate_text_body(self, template: EmailTemplate, data: Dict) -> str:
        sections = [
            self._personalize_content(template.greeting, data),
            "",
            self._personalize_content(template.main_content.strip(), data),
            "",
            template.closing,
            template.signature,
            "",
            "---",
            self.branding_config["footer_tagline"]
        ]
        return "\n".join(sections)
    
    def _generate_html_body(self, template: EmailTemplate, data: Dict) -> str:
        greeting = self._personalize_content(template.greeting, data)
        main_content = self._personalize_content(template.main_content.strip(), data)
        return render_template(
            'email_template.html',
            primary_color=self.branding_config['primary_color'],
            accent_color=self.branding_config['accent_color'],
            secondary_color=self.branding_config['secondary_color'],
            logo_url=self.branding_config['logo_url'],
            greeting=greeting,
            main_content=self._format_html_content(main_content),
            closing=template.closing,
            signature=template.signature.replace(chr(10), '<br>'),
            website=self.branding_config['social_media']['website'],
            linkedin=self.branding_config['social_media']['linkedin'],
            footer_tagline=self.branding_config['footer_tagline']
        )
    
    def _format_html_content(self, content: str) -> str:
        content = content.replace('• ', '<li>')
        content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
        content = content.replace('\n\n', '</p><p>')
        content = content.replace('\n', '<br>')
        if not content.startswith('<p>'):
            content = f'<p>{content}</p>'
        return content
    
    def _get_default_template(self) -> EmailTemplate:
        return EmailTemplate(
            subject="📋 Your Certificate is Ready!",
            greeting="Dear {name},",
            main_content="We're pleased to provide your certificate. Please find it attached to this email.\n\nThank you for your participation and dedication.",
            closing="Best regards,",
            signature="Certification Team\n🎓 Recognizing Achievement",
            tone="professional",
            priority="medium"
        )
    
    def _create_custom_template(self, custom_data: Dict) -> EmailTemplate:
        return EmailTemplate(
            subject=custom_data.get('subject', 'Your Certificate'),
            greeting=custom_data.get('greeting', 'Dear {name},'),
            main_content=custom_data.get('content', 'Please find your certificate attached.'),
            closing=custom_data.get('closing', 'Best regards,'),
            signature=custom_data.get('signature', 'Certificate Team'),
            tone=custom_data.get('tone', 'professional'),
            priority=custom_data.get('priority', 'medium')
        )
    
    def generate_batch_emails(self, recipients: List[Dict]) -> List[Dict]:
        results = []
        for recipient in recipients:
            try:
                subject, body, html_body = self.generate_certificate_email(
                    cert_type=recipient.get('cert_type', 'custom'),
                    recipient_name=recipient.get('name', 'Valued Participant'),
                    personalization_data=recipient.get('data', {}),
                    custom_template=recipient.get('custom_template')
                )
                results.append({
                    'recipient': recipient['name'],
                    'email': recipient.get('email', 'unknown@example.com'),
                    'subject': subject,
                    'body': body,
                    'html_body': html_body,
                    'status': 'success'
                })
            except Exception as e:
                results.append({
                    'recipient': recipient.get('name', 'Unknown'),
                    'email': recipient.get('email', 'unknown@example.com'),
                    'status': 'error',
                    'error': str(e)
                })
        return results
    
    def get_analytics_data(self) -> Dict:
        return {
            'available_templates': len(self.templates),
            'template_types': [t.value for t in CertificateType],
            'branding_configured': bool(self.branding_config),
            'features': [
                'Multi-template support',
                'HTML email generation',
                'Batch processing',
                'Custom template creation',
                'Advanced personalization',
                'Professional styling',
                'Social media integration'
            ]
        }

if __name__ == '__main__':
    app.run(debug=True)