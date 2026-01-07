from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.security import generate_password_hash, check_password_hash
import os
import MySQLdb
import logging
import uuid
import secrets
import string
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
from flask import send_file
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from PIL import Image
import uuid
from flask_wtf import CSRFProtect
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import send_file, jsonify
from io import BytesIO
import traceback
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import io
from simple_pdf_generator import generate_simple_pdf
import MySQLdb
from flask import jsonify, request
import os
from flask import Flask
import pymysql
import os
from flask_login import UserMixin
UPLOAD_FOLDER = 'static/uploads/profile_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB



from datetime import datetime
import logging
logger = logging.getLogger(__name__)


# ==================== CONFIGURATION ====================

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app

app = Flask(__name__)

# Security
app.config['SECRET_KEY'] = os.getenv(
    'SECRET_KEY',
    'wellness-coach-secure-key-2024'  # fallback for local
)

# MySQL (Railway / Production)


# MySQL (Railway / Production)
# MySQL (Railway)
app.config['MYSQL_HOST'] = os.getenv('MYSQLHOST')
app.config['MYSQL_USER'] = os.getenv('MYSQLUSER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQLPASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQLDATABASE')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQLPORT', 3306))
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'





# Uploads
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Flask
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['DEBUG'] = False   # IMPORTANT for production


# Initialize extensions
mysql = MySQL(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'

# ==================== MODELS ====================
class User(UserMixin):
    def __init__(self, id, username, email, name, user_type, profile_image=None):
        self.id = id
        self.username = username
        self.email = email
        self.name = name
        self.user_type = user_type
        self.profile_image = profile_image

    @staticmethod
    def get_by_id(user_id, mysql):
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT id, username, email, name, user_type, profile_image FROM users WHERE id = %s",
            (user_id,)
        )
        row = cursor.fetchone()
        cursor.close()

        if row:
            return User(
                row["id"],
                row["username"],
                row["email"],
                row["name"],
                row["user_type"],
                row["profile_image"]
            )
        return None

    @staticmethod
    def update_profile(user_id, username, email, name, profile_image, mysql):
        try:
            cursor = mysql.connection.cursor()

            cursor.execute(
                "SELECT id FROM users WHERE (username=%s OR email=%s) AND id!=%s",
                (username, email, user_id)
            )
            if cursor.fetchone():
                cursor.close()
                return False, "Username or email already exists"

            if profile_image:
                cursor.execute("""
                    UPDATE users
                    SET username=%s, email=%s, name=%s, profile_image=%s
                    WHERE id=%s
                """, (username, email, name, profile_image, user_id))
            else:
                cursor.execute("""
                    UPDATE users
                    SET username=%s, email=%s, name=%s
                    WHERE id=%s
                """, (username, email, name, user_id))

            mysql.connection.commit()
            cursor.close()
            return True, "Profile updated successfully"

        except Exception as e:
            print("PROFILE UPDATE ERROR:", e)
            return False, "Error updating profile"
class User:
    def __init__(self, id, username, email, name, user_type, profile_image=None, created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.name = name
        self.user_type = user_type
        self.profile_image = profile_image
        self.created_at = created_at
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return str(self.id)

    @staticmethod
    def get(user_id, mysql_connection):
        try:
            cursor = mysql_connection.connection.cursor()
            cursor.execute(
                'SELECT id, username, email, name, user_type, profile_image, created_at FROM users WHERE id = %s',
                (user_id,)
            )
            user = cursor.fetchone()
            cursor.close()
            
            if user:
                return User(
                    id=user['id'],
                    username=user['username'],
                    email=user['email'],
                    name=user['name'],
                    user_type=user['user_type'],
                    profile_image=user['profile_image'],
                    created_at=user['created_at']
                )
            return None
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None

    @staticmethod
    def authenticate(email, password, mysql_connection):
        try:
            cursor = mysql_connection.connection.cursor()
            cursor.execute(
                'SELECT id, username, email, name, user_type, profile_image, password, created_at FROM users WHERE email = %s',
                (email,)
            )
            user = cursor.fetchone()
            cursor.close()
            
            if user and user['password']:
                logger.debug(f"Authenticating user: {email}")
                logger.debug(f"Stored password hash: {user['password'][:50]}...")
                
                # Check if password matches
                if check_password_hash(user['password'], password):
                    logger.debug(f"Password verification SUCCESS for {email}")
                    return User(
                        id=user['id'],
                        username=user['username'],
                        email=user['email'],
                        name=user['name'],
                        user_type=user['user_type'],
                        profile_image=user['profile_image'],
                        created_at=user['created_at']
                    )
                else:
                    logger.debug(f"Password verification FAILED for {email}")
            else:
                logger.debug(f"User not found or no password: {email}")
                
            return None
        except Exception as e:
            logger.error(f"Error authenticating user {email}: {e}", exc_info=True)
            return None

    @staticmethod
    def create(username, email, password, name, user_type='user', mysql_connection=None):
        try:
            cursor = mysql_connection.connection.cursor()
            
            # Check if user already exists
            cursor.execute(
                'SELECT id FROM users WHERE email = %s OR username = %s',
                (email, username)
            )
            existing_user = cursor.fetchone()
            
            if existing_user:
                cursor.close()
                return None, "Email or username already exists. Please use different credentials."
            
            # Create new user with consistent password hashing
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            logger.debug(f"Creating user {email} with hash: {hashed_password[:50]}...")
            
            cursor.execute(
                '''INSERT INTO users (username, email, password, name, user_type) 
                   VALUES (%s, %s, %s, %s, %s)''',
                (username, email, hashed_password, name, user_type)
            )
            
            mysql_connection.connection.commit()
            
            # Get the new user
            cursor.execute(
                'SELECT id, username, email, name, user_type FROM users WHERE id = LAST_INSERT_ID()'
            )
            new_user = cursor.fetchone()
            cursor.close()
            
            user_obj = User(
                id=new_user['id'],
                username=new_user['username'],
                email=new_user['email'],
                name=new_user['name'],
                user_type=new_user['user_type']
            )
            return user_obj, "Registration successful! Welcome to Wellness Coach."
            
        except Exception as e:
            logger.error(f"Error creating user {email}: {e}", exc_info=True)
            return None, "An error occurred during registration. Please try again."

    @staticmethod
    def update_profile(user_id, username, email, name, profile_image, mysql_connection):
        try:
            cursor = mysql_connection.connection.cursor()
            
            # Check for existing users with same email or username
            cursor.execute(
                '''SELECT id FROM users 
                   WHERE (email = %s OR username = %s) AND id != %s''',
                (email, username, user_id)
            )
            existing_user = cursor.fetchone()
            
            if existing_user:
                cursor.close()
                return False, "Username or email already exists. Please choose different ones."
            
            # Update user
            update_query = '''UPDATE users SET username = %s, email = %s, name = %s'''
            params = [username, email, name]
            
            if profile_image:
                update_query += ', profile_image = %s'
                params.append(profile_image)
            
            update_query += ' WHERE id = %s'
            params.append(user_id)
            
            cursor.execute(update_query, tuple(params))
            mysql_connection.connection.commit()
            cursor.close()
            return True, "Profile updated successfully!"
            
        except Exception as e:
            logger.error(f"Error updating profile for user {user_id}: {e}")
            return False, "An error occurred while updating profile."
        
        

    @staticmethod
    def update_profile(user_id, username, email, name, profile_image, mysql):
        """Update user profile"""
        try:
            cursor = mysql.connection.cursor()
            
            # Check if username or email already exists (excluding current user)
            cursor.execute(
                "SELECT id FROM users WHERE (username = %s OR email = %s) AND id != %s",
                (username, email, user_id)
            )
            existing_user = cursor.fetchone()
            
            if existing_user:
                return False, "Username or email already exists"
            
            # Update user profile
            if profile_image:
                cursor.execute(
                    """UPDATE users 
                       SET username = %s, email = %s, name = %s, profile_image = %s, updated_at = NOW() 
                       WHERE id = %s""",
                    (username, email, name, profile_image, user_id)
                )
            else:
                cursor.execute(
                    """UPDATE users 
                       SET username = %s, email = %s, name = %s, updated_at = NOW() 
                       WHERE id = %s""",
                    (username, email, name, user_id)
                )
            
            mysql.connection.commit()
            cursor.close()
            return True, "Profile updated successfully"
            
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            return False, "Error updating profile"

# ==================== HELPER FUNCTIONS ====================

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id, mysql)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
def save_profile_image(file, user_id):
    """Save uploaded profile image"""
    try:
        if not file or file.filename == '':
            return None
        
        # Secure the filename
        filename = secure_filename(file.filename)
        # Create unique filename
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'
        unique_filename = f"profile_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
        
        # Define upload folder
        upload_folder = os.path.join(app.root_path, 'static', 'uploads', 'profiles')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        return f"uploads/profiles/{unique_filename}"
    except Exception as e:
        logger.error(f"Error saving profile image: {str(e)}")
        return None
def save_profile_image(file, user_id):
    if file and file.filename and allowed_file(file.filename):
        try:
            original_filename = secure_filename(file.filename)
            ext = original_filename.rsplit('.', 1)[1].lower()
            filename = f"profile_{user_id}_{uuid.uuid4().hex[:8]}.{ext}"
            upload_folder = app.config['UPLOAD_FOLDER']
            
            # Create upload folder if it doesn't exist
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
                logger.info(f"Created upload folder: {upload_folder}")
            
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            logger.info(f"Profile image saved: {filepath}")
            return filename
        except Exception as e:
            logger.error(f"Error saving profile image: {e}")
    return None
@classmethod
def update_profile(cls, user_id, username, email, name, profile_image, mysql):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Check if username or email already exists (excluding current user)
        cursor.execute(
            "SELECT id FROM users WHERE (username = %s OR email = %s) AND id != %s",
            (username, email, user_id)
        )
        existing = cursor.fetchone()
        
        if existing:
            return False, "Username or email already exists"
        
        # Update user profile
        if profile_image:
            cursor.execute(
                """UPDATE users 
                   SET username = %s, email = %s, name = %s, profile_image = %s, updated_at = NOW() 
                   WHERE id = %s""",
                (username, email, name, profile_image, user_id)
            )
        else:
            cursor.execute(
                """UPDATE users 
                   SET username = %s, email = %s, name = %s, updated_at = NOW() 
                   WHERE id = %s""",
                (username, email, name, user_id)
            )
        
        mysql.connection.commit()
        cursor.close()
        
        return True, "Profile updated successfully"
        
    except Exception as e:
        mysql.connection.rollback()
        return False, f"Error updating profile: {str(e)}"

def save_profile_image(file, user_id):
    """Save uploaded profile image"""
    try:
        if not file or file.filename == '':
            return None
        
        # Secure the filename
        filename = secure_filename(file.filename)
        # Create unique filename
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'
        unique_filename = f"profile_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
        
        # Define upload folder
        upload_folder = os.path.join(app.root_path, 'static', 'uploads', 'profiles')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        return f"uploads/profiles/{unique_filename}"
    except Exception as e:
        logger.error(f"Error saving profile image: {str(e)}")
        return None
def generate_consultation_pdf(consultation_data, user_data=None):
    """
    Generate PDF for consultation
    """
    buffer = io.BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
        title=f"Consultation {consultation_data.get('id', 'N/A')}"
    )
    
    # Container for PDF elements
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#059669'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=6
    )
    
    # Title
    elements.append(Paragraph("Wellness Coach Consultation Summary", title_style))
    elements.append(Spacer(1, 20))
    
    # Reference and Date
    reference = consultation_data.get('reference', f"#CONS-{consultation_data.get('id', '0000')}")
    elements.append(Paragraph(f"Reference: <b>{reference}</b>", normal_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", normal_style))
    elements.append(Spacer(1, 20))
    
    # Section 1: Consultation Overview
    elements.append(Paragraph("Consultation Overview", heading_style))
    print("DEBUG consultation_data:", consultation_data)
    created_date = consultation_data.get('created_date')
    created_time = consultation_data.get('created_time')
    if created_date:
        created_date = str(created_date)
    else:
        created_date = 'N/A'
    if created_time:
        created_time = str(created_time)
    else:
        created_time = 'N/A'
    overview_data = [
       ['Status:', consultation_data.get('status', 'Pending').title()],
        ['Program:', consultation_data.get('program', 'General Inquiry')],
        ['Submitted Date:', created_date],
        ['Submitted Time:', created_time]
    ]
    

    overview_table = Table(overview_data, colWidths=[1.5*inch, 4*inch])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#475569')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0'))
    ]))
    elements.append(overview_table)
    elements.append(Spacer(1, 15))
    
    # Section 2: Personal Information
    elements.append(Paragraph("Personal Information", heading_style))
    
    if user_data:
        personal_data = [
            ['Full Name:', user_data.get('name', 'N/A')],
            ['Email:', user_data.get('email', 'N/A')],
            ['Phone:', consultation_data.get('phone', 'Not provided')]
        ]
    else:
        personal_data = [
            ['Name:', consultation_data.get('name', 'N/A')],
            ['Email:', consultation_data.get('email', 'N/A')],
            ['Phone:', consultation_data.get('phone', 'Not provided')]
        ]
    
    personal_table = Table(personal_data, colWidths=[1.5*inch, 4*inch])
    personal_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#475569')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0'))
    ]))
    elements.append(personal_table)
    elements.append(Spacer(1, 15))
    
    # Section 3: Your Message
    elements.append(Paragraph("Your Message", heading_style))
    
    message = consultation_data.get('message', 'No message provided')
    if isinstance(message, str):
        message = message.replace('\n', '<br/>')
    message_para = Paragraph(f"<b>Message:</b><br/>{message}", normal_style)
    elements.append(message_para)
    elements.append(Spacer(1, 15))
    
    # Section 4: Next Steps
    elements.append(Paragraph("Next Steps", heading_style))
    
    status = consultation_data.get('status', 'pending').lower()
    if status == 'pending':
        steps = "Your consultation is currently under review. Our wellness coach will analyze your requirements and get back to you within 48 hours."
    elif status == 'reviewed':
        steps = "Your consultation has been reviewed. Our wellness coach is preparing a personalized plan for you."
    elif status == 'responded':
        steps = "Response has been provided. Please check your email for detailed recommendations."
    else:
       steps = "Thank you for reaching out. You will be contacted within 24 hours."
        
    
    steps_para = Paragraph(steps, normal_style)
    elements.append(steps_para)
    elements.append(Spacer(1, 20))
    
    # Footer note
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER,
        spaceBefore=20
    )
    
    elements.append(Paragraph("This document is confidential and intended solely for the recipient.", footer_style))
    elements.append(Paragraph("© Wellness Coach. All rights reserved.", footer_style))
    
    # Build PDF
    try:
        doc.build(elements)
        
        # Get PDF value
        pdf = buffer.getvalue()
        buffer.close()
        
        if len(pdf) < 100:  # Check if PDF is too small (likely empty)
            raise Exception("Generated PDF is too small or empty")
            
        return pdf
    except Exception as e:
        # Create a simple PDF as fallback
        return create_simple_pdf(consultation_data, user_data)

def create_simple_pdf(consultation_data, user_data=None):
    """Create a simple PDF as fallback"""
    buffer = io.BytesIO()
    from reportlab.pdfgen import canvas
    
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Set font
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Wellness Coach - Consultation Summary")
    
    c.setFont("Helvetica", 10)
    c.drawString(100, 720, f"Reference: {consultation_data.get('reference', 'N/A')}")
    c.drawString(100, 700, f"Date: {datetime.now().strftime('%B %d, %Y')}")
    c.drawString(100, 680, "=" * 50)
    
    y = 650
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, y, "Consultation Details")
    c.setFont("Helvetica", 10)
    
    y -= 30
    details = [
        ("Program:", consultation_data.get('program', 'General Inquiry')),
        ("Status:", consultation_data.get('status', 'pending').title()),
        ("Submitted:", consultation_data.get('created_date', 'N/A')),
    ]
    
    for label, value in details:
        c.drawString(100, y, f"{label} {value}")
        y -= 20
    
    if user_data:
        y -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, y, "Personal Information")
        c.setFont("Helvetica", 10)
        y -= 30
        c.drawString(100, y, f"Name: {user_data.get('name', 'N/A')}")
        y -= 20
        c.drawString(100, y, f"Email: {user_data.get('email', 'N/A')}")
    
    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, y, "Message")
    c.setFont("Helvetica", 10)
    y -= 20
    
    # Handle long message
    message = consultation_data.get('message', 'No message')
    lines = []
    words = message.split()
    line = ""
    for word in words:
        if len(line + " " + word) <= 80:
            line = line + " " + word if line else word
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    
    for line in lines[:15]:  # Limit to 15 lines
        c.drawString(100, y, line)
        y -= 15
    
    c.drawString(100, 100, "=" * 50)
    c.drawString(100, 80, "Generated by Wellness Coach System")
    
    c.save()
    
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def generate_consultation_pdf(consultation, user):
    """
    Generate PDF for consultation
    """
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
        title=f"Consultation {consultation['id']}"
    )
    
    # Container for PDF elements
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#059669'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#475569'),
        spaceAfter=10,
        spaceBefore=15
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=6
    )
    
    # Title
    elements.append(Paragraph("Wellness Coach Consultation Summary", title_style))
    elements.append(Spacer(1, 20))
    
    # Reference and Date
    elements.append(Paragraph(f"Reference: <b>#CONS-{consultation['id']:04d}</b>", normal_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", normal_style))
    elements.append(Spacer(1, 20))
    
    # Section 1: Consultation Overview
    elements.append(Paragraph("Consultation Overview", heading_style))

    created_at = consultation.get('created_at')

    overview_data = [
       ['Status:', consultation['status'].title()],
        ['Program:', consultation.get('program', 'General Inquiry')],
        ['Submitted Date:', created_at.strftime('%d %B %Y') if created_at else 'N/A'],
        ['Submitted Time:', created_at.strftime('%I:%M %p') if created_at else 'N/A']
    ]
    
    overview_table = Table(overview_data, colWidths=[1.5*inch, 4*inch])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#ace3b4")),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#59E045")),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0'))
    ]))
    elements.append(overview_table)
    elements.append(Spacer(1, 15))
    
    # Section 2: Personal Information
    elements.append(Paragraph("Personal Information", heading_style))
    
    personal_data = [
        ['Full Name:', user.name or user.username],
        ['Email:', user.email],
        ['Phone:', consultation.get('phone', 'Not provided')]
    ]
    
    personal_table = Table(personal_data, colWidths=[1.5*inch, 4*inch])
    personal_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#4F8735")),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0'))
    ]))
    elements.append(personal_table)
    elements.append(Spacer(1, 15))
    
    # Section 3: Goals and Objectives
    elements.append(Paragraph("Goals and Objectives", heading_style))
    
    goals_data = [
        ['Primary Goal:', consultation.get('goal', 'Not specified')],
        ['Desired Timeframe:', consultation.get('timeframe', 'Not specified')]
    ]
    
    goals_table = Table(goals_data, colWidths=[1.5*inch, 4*inch])
    goals_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#468348")),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0'))
    ]))
    elements.append(goals_table)
    elements.append(Spacer(1, 15))
    
    # Section 4: Your Message
    elements.append(Paragraph("Your Message", heading_style))
    
    # Clean and format the message
    message = consultation.get('message', '').replace('\n', '<br/>')
    message_para = Paragraph(f"<b>Message:</b><br/>{message}", normal_style)
    elements.append(message_para)
    elements.append(Spacer(1, 15))
    
    # Section 5: Next Steps
    elements.append(Paragraph("Next Steps", heading_style))
    
    status = consultation.get('status', 'pending').lower()
    if status == 'pending':
        steps = "Your consultation is currently under review. Our wellness coach will analyze your requirements and get back to you within 48 hours."
    elif status == 'reviewed':
        steps = "Your consultation has been reviewed. Our wellness coach is preparing a personalized plan for you."
    else:
        steps = "Response has been provided. Please check your email for detailed recommendations."
    
    steps_para = Paragraph(steps, normal_style)
    elements.append(steps_para)
    elements.append(Spacer(1, 20))
    
    # Footer note
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor("#6c8b64"),
        alignment=TA_CENTER,
        spaceBefore=20
    )
    
    elements.append(Paragraph("This document is confidential and intended solely for the recipient.", footer_style))
    elements.append(Paragraph("© Wellness Coach. All rights reserved.", footer_style))
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF value
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_profile_image(file, user_id):
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        raise ValueError('Invalid file type')
    
    if len(file.read()) > MAX_FILE_SIZE:
        raise ValueError('File too large')
    file.seek(0)  # Reset file pointer
    
    # Create unique filename
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{user_id}_{uuid.uuid4().hex[:8]}.{ext}"
    
    # Ensure upload directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Save file
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    # Optional: Resize image
    try:
        img = Image.open(filepath)
        img.thumbnail((400, 400))
        img.save(filepath)
    except Exception as e:
        print(f"Error resizing image: {e}")
    
    return filename

def get_db_connection():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB"),
        port=int(os.getenv("MYSQL_PORT")),
        cursorclass=pymysql.cursors.DictCursor
    )

def init_database():
    """Initialize database with all required tables and sample data"""
    try:
        # First, ensure the database exists
        connection = MySQLdb.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD']
        )
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {app.config['MYSQL_DB']}")
        connection.commit()
        cursor.close()
        connection.close()
        
        logger.info(f"Database {app.config['MYSQL_DB']} ensured")
        
        # Now connect to the specific database
        cursor = mysql.connection.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                email VARCHAR(100) NOT NULL UNIQUE,
                name VARCHAR(100) NOT NULL,
                password VARCHAR(255) NOT NULL,
                user_type ENUM('user', 'admin') DEFAULT 'user',
                profile_image VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        ''')
        
        # Contact messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contact_messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                subject VARCHAR(200),
                message TEXT NOT NULL,
                status ENUM('new', 'read', 'replied') DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                price DECIMAL(10,2) NOT NULL,
                duration VARCHAR(50),
                features TEXT,
                available_offline BOOLEAN DEFAULT TRUE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        ''')
        
        # Reviews table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                username VARCHAR(100),
                rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
                review_text TEXT NOT NULL,
                status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Success stories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS success_stories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                title VARCHAR(200) NOT NULL,
                description TEXT NOT NULL,
                before_image VARCHAR(255),
                after_image VARCHAR(255),
                weight_lost DECIMAL(5,2),
                time_period VARCHAR(50),
                status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        # Consultations table
# Add this after other table creations in init_database()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS consultations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL,
        phone VARCHAR(20) NOT NULL,
        program VARCHAR(100) NOT NULL,
        goal VARCHAR(100) NOT NULL,
        timeframe VARCHAR(50),
        subject VARCHAR(200) NOT NULL,
        message TEXT NOT NULL,
        status ENUM('pending', 'reviewed', 'responded') DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        INDEX idx_user_id (user_id),
        INDEX idx_status (status)
    )
''')
  # Check if admin user exists and create if not
        cursor.execute('SELECT id, password FROM users WHERE email = %s', ('admin@wellness.com',))
        admin_user = cursor.fetchone()
        
        admin_password = 'admin@7671'
        
        if not admin_user:
            # Create admin user with consistent password hashing
            logger.info("Creating admin user...")
            hashed_password = generate_password_hash(admin_password, method='pbkdf2:sha256')
            cursor.execute(
                '''INSERT INTO users (username, email, name, password, user_type) 
                   VALUES (%s, %s, %s, %s, %s)''',
                ('admin', 'admin@wellness.com', 'Wellness Admin', hashed_password, 'admin')
            )
            mysql.connection.commit()
            logger.info("✓ Admin user created successfully")
        else:
            # Verify admin password is properly hashed
            stored_hash = admin_user['password']
            logger.info(f"Admin exists with hash: {stored_hash[:50]}...")
            
            # If password doesn't verify, rehash it
            if not check_password_hash(stored_hash, admin_password):
                logger.info("Rehashing admin password...")
                hashed_password = generate_password_hash(admin_password, method='pbkdf2:sha256')
                cursor.execute(
                    'UPDATE users SET password = %s WHERE email = %s',
                    (hashed_password, 'admin@wellness.com')
                )
                mysql.connection.commit()
                logger.info("✓ Admin password rehashed")
        
        # Insert sample products if table is empty
        cursor.execute('SELECT COUNT(*) as count FROM products')
        product_count = cursor.fetchone()['count']
        if product_count == 0:
            sample_products = [
                ('Weight Loss Program', 'Complete 12-week weight loss transformation', 2999.00, '12 Weeks', 'Personalized meal plans, Weekly check-ins, Progress tracking'),
                ('Weight Gain Program', 'Healthy weight gain program', 3499.00, '8 Weeks', 'Calorie-dense meal plans, Strength training'),
                ('Personalized Nutrition Plan', 'Customized nutrition plan', 1999.00, '4 Weeks', 'Detailed diet charts, Recipe suggestions'),
                ('Fitness Coaching', 'One-on-one fitness coaching', 2499.00, '1 Month', 'Custom workout plans, Form correction'),
                ('Heart Health Program', 'Cardiovascular wellness program', 2799.00, '6 Weeks', 'BP monitoring, Heart-healthy recipes'),
                ('Mental Wellness', 'Stress management program', 2299.00, '8 Weeks', 'Meditation guides, Sleep improvement'),
                ('Diabetes Management', 'Diabetes control program', 3299.00, '12 Weeks', 'Sugar monitoring, Diabetic diet plans'),
                ('Post Pregnancy Weight Loss', 'Safe weight loss for mothers', 3799.00, '16 Weeks', 'Postpartum exercises, Gentle workouts')
            ]
            
            for product in sample_products:
                cursor.execute(
                    '''INSERT INTO products (name, description, price, duration, features) 
                       VALUES (%s, %s, %s, %s, %s)''',
                    product
                )
            logger.info(f"✓ {len(sample_products)} sample products inserted")
        
        # Insert sample reviews if table is empty
        cursor.execute('SELECT COUNT(*) as count FROM reviews')
        review_count = cursor.fetchone()['count']
        if review_count == 0:
            sample_reviews = [
                (1, 'Anjali Sharma', 5, 'I lost 12 kg in just 3 months! Highly recommended!'),
                (1, 'Rajesh Kumar', 5, 'Best investment in my health. Lost 15kg in 4 months!'),
                (1, 'Priya Reddy', 4, 'Great guidance for weight gain!'),
                (1, 'Suresh Verma', 5, 'Coach is very supportive and plans are practical.'),
                (1, 'Meena Patel', 5, 'Post-pregnancy weight loss was challenging, but this program made it easy.')
            ]
            
            for review in sample_reviews:
                cursor.execute(
                    '''INSERT INTO reviews (user_id, username, rating, review_text, status) 
                       VALUES (%s, %s, %s, %s, "approved")''',
                    review
                )
            logger.info(f"✓ {len(sample_reviews)} sample reviews inserted")
        
        # Insert sample success stories if table is empty
        cursor.execute('SELECT COUNT(*) as count FROM success_stories')
        story_count = cursor.fetchone()['count']
        if story_count == 0:
            sample_stories = [
                (1, 'My Weight Loss Journey', 'Lost 15kg in 3 months with proper diet and exercise.', 15.0, '3 Months'),
                (1, 'Diabetes Under Control', 'Reduced HbA1c from 8.5 to 6.2 with customized diet plan.', 8.5, '4 Months'),
                (1, 'Healthy Weight Gain', 'Gained 5kg of muscle mass with proper nutrition.', -5.0, '2 Months')
            ]
            
            for story in sample_stories:
                cursor.execute(
                    '''INSERT INTO success_stories (user_id, title, description, weight_lost, time_period, status) 
                       VALUES (%s, %s, %s, %s, %s, "approved")''',
                    story
                )
            logger.info(f"✓ {len(sample_stories)} sample success stories inserted")
        
        mysql.connection.commit()
        cursor.close()
        logger.info("✓ Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization error: {e}", exc_info=True)

# ==================== ROUTES ====================


@app.route('/')
def index():
    """Home page"""
    try:
        cursor = mysql.connection.cursor()
        
        # Get active products
        cursor.execute(
            '''SELECT id, name, description, price, duration, features 
               FROM products WHERE is_active = TRUE LIMIT 6'''
        )
        products = cursor.fetchall()
        
        # Get approved reviews
        cursor.execute(
            '''SELECT id, username, rating, review_text, created_at 
               FROM reviews WHERE status = "approved" ORDER BY created_at DESC LIMIT 6'''
        )
        reviews = cursor.fetchall()
        
        # Get approved success stories
        cursor.execute(
            '''SELECT id, title, description, before_image, after_image, weight_lost, time_period, created_at 
               FROM success_stories WHERE status = "approved" ORDER BY created_at DESC LIMIT 3'''
        )
        success_stories = cursor.fetchall()
        
        # Get statistics
        stats = {}
        cursor.execute('SELECT COUNT(*) as count FROM products WHERE is_active = TRUE')
        stats['programs'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE user_type = "user"')
        stats['users'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT AVG(rating) as avg_rating FROM reviews WHERE status = "approved"')
        avg_rating = cursor.fetchone()['avg_rating']
        stats['success_rate'] = round((avg_rating or 0) * 20, 1) if avg_rating else 0
        
        cursor.execute('SELECT COUNT(*) as count FROM reviews WHERE status = "approved"')
        stats['reviews'] = cursor.fetchone()['count']
        
        cursor.close()
        
        return render_template(
            'index.html',
            products=products,
            reviews=reviews,
            success_stories=success_stories,
            stats=stats
        )
        
    except Exception as e:
        logger.error(f"Error loading index: {e}", exc_info=True)
        return render_template(
            'index.html',
            products=[],
            reviews=[],
            success_stories=[],
            stats={'programs': 0, 'users': 0, 'success_rate': 0, 'reviews': 0}
        )

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        try:
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip().lower()
            name = request.form.get("name", "").strip() or username
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")

            # ---------- VALIDATION ----------
            if not username or not email or not password or not confirm_password:
                flash("All fields are required", "error")
                return redirect(url_for("register"))

            if len(username) < 3:
                flash("Username must be at least 3 characters", "error")
                return redirect(url_for("register"))

            if "@" not in email or "." not in email:
                flash("Invalid email address", "error")
                return redirect(url_for("register"))

            if len(password) < 6:
                flash("Password must be at least 6 characters", "error")
                return redirect(url_for("register"))

            if password != confirm_password:
                flash("Passwords do not match", "error")
                return redirect(url_for("register"))

            # ---------- DATABASE ----------
            cur = mysql.connection.cursor()

            # Check existing user
            cur.execute(
                "SELECT id FROM users WHERE email=%s OR username=%s",
                (email, username)
            )
            if cur.fetchone():
                cur.close()
                flash("Email or Username already exists", "error")
                return redirect(url_for("register"))

            hashed_password = generate_password_hash(password)

            # INSERT USER (name included – IMPORTANT)
            cur.execute(
                "INSERT INTO users (username, email, name, password, user_type) "
                "VALUES (%s, %s, %s, %s, %s)",
                (username, email, name, hashed_password, "user")
            )

            mysql.connection.commit()
            user_id = cur.lastrowid
            cur.close()

            # ---------- LOGIN USER ----------
            user = User(user_id, username, email, name, "user")
            login_user(user)

            flash("Registration successful! Welcome 🎉", "success")
            return redirect(url_for("index"))

        except Exception as e:
            print("REGISTER ERROR:", e)
            flash(str(e), "error")   # TEMP → shows real error
            return redirect(url_for("register"))

    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        flash('You are already logged in!', 'info')
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember_me = 'remember_me' in request.form

        logger.debug(f"Login attempt for email: {email}")

        if not email or not password:
            flash('Please enter both email and password!', 'error')
        else:
            user = User.authenticate(email, password, mysql)

            if user:
                login_user(user, remember=remember_me)
                flash(f'Welcome back, {user.name}!', 'success')
                
                # Redirect to admin panel if admin
                if user.user_type == 'admin':
                    logger.debug(f"Admin {email} logged in successfully")
                    return redirect(url_for('admin'))
                
                # Redirect to next page or index
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                flash('Invalid email or password. Please try again.', 'error')
                logger.debug(f"Login failed for email: {email}")

    return render_template('login.html')

@app.route('/admin-login-test')
def admin_login_test():
    """Test admin login directly"""
    email = 'admin@wellness.com'
    password = 'admin@7671'
    
    logger.info(f"Testing admin login: {email}")
    
    user = User.authenticate(email, password, mysql)
    if user:
        login_user(user, remember=True)
        flash(f'Welcome {user.name}! Admin login successful.', 'success')
        
        if user.user_type == 'admin':
            return redirect(url_for('admin'))
        else:
            flash('User is not an admin.', 'error')
            return redirect(url_for('index'))
    else:
        flash('Admin login failed. Please check credentials.', 'error')
        return redirect(url_for('login'))

@app.route('/demo-login')
def demo_login():
    """Demo login for testing"""
    email = 'admin@wellness.com'
    password = 'admin@7671'
    
    user = User.authenticate(email, password, mysql)
    if user:
        login_user(user, remember=True)
        flash(f'Welcome {user.name}! Demo login successful.', 'success')
        return redirect(url_for('index'))
    else:
        flash('Demo login failed. Please try regular login.', 'error')
        return redirect(url_for('login'))




reset_codes = {}

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        # Validate email format
        if not email or '@' not in email:
            flash('Please enter a valid email address', 'error')
            return render_template('forgot_password.html')
        
        # Check if user exists (check database in production)
        user_exists = check_user_exists(email)
        
        if not user_exists:
            flash('No account found with that email address', 'error')
            return render_template('forgot_password.html')
        
        # Generate 6-digit verification code
        code = ''.join(secrets.choice(string.digits) for _ in range(6))
        
        # Store code (15 minutes expiry)
        reset_codes[email] = {
            'code': code,
            'expires': datetime.now() + timedelta(minutes=15),
            'attempts': 0
        }
        
        # Send email with code (console simulation)
        print(f"Password reset code for {email}: {code}")
        
        # In production, implement email sending:
        # send_reset_email(email, code)
        
        # Store email in session
        session['reset_email'] = email
        email = session.get('reset_email')

        
        # Redirect to code entry page
        return redirect(url_for('reset_password'))
    
    return render_template('forgot_password.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    email = session.get('reset_email')
    
    if not email:
        flash('Please request a password reset first', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        # Get verification code from form
        verification_code = ''.join(
            request.form.get(f'code{i}', '') for i in range(6)
        )
        
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate code exists
        if email not in reset_codes:
            flash('Verification code expired. Please request a new one.', 'error')
            return render_template('reset_password.html', email=email)
        
        reset_data = reset_codes[email]
        
        # Check expiration
        if datetime.now() > reset_data['expires']:
            del reset_codes[email]
            flash('Verification code expired. Please request a new one.', 'error')
            return render_template('reset_password.html', email=email)
        
        # Check attempt limit
        if reset_data['attempts'] >= 3:
            del reset_codes[email]
            flash('Too many attempts. Please request a new code.', 'error')
            return render_template('reset_password.html', email=email)
        
        # Verify code
        if verification_code != reset_data['code']:
            reset_data['attempts'] += 1
            flash(f'Invalid verification code. {3 - reset_data["attempts"]} attempts remaining', 'error')
            return render_template('reset_password.html', email=email)
        
        # Validate password
        if not new_password or len(new_password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return render_template('reset_password.html', email=email)
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('reset_password.html', email=email)
        
        # Update user password in database
        success = update_user_password(email, new_password)
        
        if success:
            # Clear reset data
            del reset_codes[email]
            session.pop('reset_email', None)
            
            flash('Password reset successfully! You can now login with your new password.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Failed to reset password. Please try again.', 'error')
    
    return render_template('reset_password.html', email=email)

@app.route('/resend_code', methods=['POST'])
def resend_code():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400
        
        # Generate new code
        code = ''.join(secrets.choice(string.digits) for _ in range(6))
        
        # Update code in storage
        reset_codes[email] = {
            'code': code,
            'expires': datetime.now() + timedelta(minutes=15),
            'attempts': 0
        }
        
        # Resend code (console simulation)
        print(f"Resending reset code to {email}: {code}")
        
        return jsonify({'success': True, 'message': 'Verification code resent successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Helper functions (implement these for your database)
def check_user_exists(email):
    """Check if user exists in database"""
    # Query your database here
    # Return True if user exists
    return True  # Temporary for testing

def update_user_password(email, new_password):
    """Update user password in database"""
    # Update password in your database
    # Hash the password before storing
    # Return True if successful
    return True  # Temporary for testing

def send_reset_email(email, code):
    """Send password reset email"""
    # Implement email sending logic here
    # Use Flask-Mail or similar
    pass





@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')





@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        name = request.form.get('name', '').strip() or username
        profile_image = None
        
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename != '':
                profile_image = save_profile_image(file, current_user.id)
        
        success, message = User.update_profile(current_user.id, username, email, name, profile_image, mysql)
        
        if success:
            flash(message, 'success')
            # Update current_user object
            current_user.username = username
            current_user.email = email
            current_user.name = name
            if profile_image:
                current_user.profile_image = profile_image
        else:
            flash(message, 'error')
        
        return redirect(url_for('profile'))
    
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Get user's consultations from contact_messages table
        cursor.execute(
            '''SELECT id, name, email, phone, subject as program, 
                      message as goal, 
                      '' as timeframe, 
                      subject, 
                      message, 
                      IFNULL(status, 'pending') as status, 
                      DATE_FORMAT(created_at, "%%Y-%%m-%%d %%H:%%i:%%s") as created_at 
               FROM contact_messages 
               WHERE email = %s 
               ORDER BY created_at DESC''',
            (current_user.email,)
        )
        consultations = cursor.fetchall()
        
        # Convert string dates to datetime objects
        for consultation in consultations:
            if consultation.get('created_at'):
                try:
                    consultation['created_at'] = datetime.strptime(str(consultation['created_at']), "%Y-%m-%d %H:%M:%S")
                except:
                    consultation['created_at'] = datetime.now()
            # Set default values for missing fields
            if not consultation.get('program'):
                consultation['program'] = 'General Inquiry'
            if not consultation.get('goal'):
                consultation['goal'] = consultation.get('message', '')[:100] + '...' if len(consultation.get('message', '')) > 100 else consultation.get('message', '')
        
        # Get user's reviews
        cursor.execute(
            '''SELECT id, rating, review_text, status, created_at 
               FROM reviews WHERE user_id = %s ORDER BY created_at DESC''',
            (current_user.id,)
        )
        user_reviews = cursor.fetchall()
        
        # Convert review dates
        for review in user_reviews:
            if review.get('created_at') and isinstance(review['created_at'], str):
                try:
                    review['created_at'] = datetime.strptime(str(review['created_at']), "%Y-%m-%d %H:%M:%S")
                except:
                    review['created_at'] = datetime.now()
        
        # Get user's success stories
        cursor.execute(
            '''SELECT id, title, description, before_image, after_image, weight_lost, time_period, status, created_at 
               FROM success_stories WHERE user_id = %s ORDER BY created_at DESC''',
            (current_user.id,)
        )
        user_stories = cursor.fetchall()
        
        # Convert story dates
        for story in user_stories:
            if story.get('created_at') and isinstance(story['created_at'], str):
                try:
                    story['created_at'] = datetime.strptime(str(story['created_at']), "%Y-%m-%d %H:%M:%S")
                except:
                    story['created_at'] = datetime.now()
        
        cursor.close()
        
        return render_template(
            'profile.html',
            consultations=consultations,
            user_reviews=user_reviews,
            user_stories=user_stories
        )
        
    except Exception as e:
        logger.error(f"Error loading profile: {str(e)}", exc_info=True)
        flash('Error loading profile data. Please try again.', 'error')
        return render_template('profile.html', consultations=[], user_reviews=[], user_stories=[])


# Add this route for the print functionality
@app.route('/api/consultation/<int:consultation_id>/print') #one
@login_required
def print_consultation(consultation_id):
    """Get consultation details for printing"""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            '''SELECT id, name, email, phone, subject as program, 
                      message as goal, 
                      '' as timeframe, 
                      subject, 
                      message, 
                      IFNULL(status, 'pending') as status, 
                      DATE_FORMAT(created_at, "%%Y-%%m-%%d %%H:%%i:%%s") as created_at 
               FROM contact_messages 
               WHERE id = %s AND email = %s''',
            (consultation_id, current_user.email)
        )
        consultation = cursor.fetchone()
        cursor.close()
        
        if consultation:
            if consultation.get('created_at'):
                try:
                    consultation['created_at'] = datetime.strptime(str(consultation['created_at']), "%Y-%m-%d %H:%M:%S")
                except:
                    consultation['created_at'] = datetime.now()
            
            return render_template('print_consultation.html', consultation=consultation)
        else:
            return "Consultation not found", 404
    except Exception as e:
        logger.error(f"Error printing consultation: {str(e)}", exc_info=True)
        return "Error loading consultation details", 500


def save_profile_image(file, user_id):
    """Save uploaded profile image"""
    try:
        if not file or file.filename == '':
            return None
        
        # Secure the filename
        filename = secure_filename(file.filename)
        # Create unique filename
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'
        unique_filename = f"profile_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
        
        # Define upload folder
        upload_folder = os.path.join(app.root_path, 'static', 'uploads', 'profiles')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        return f"uploads/profiles/{unique_filename}"
    except Exception as e:
        logger.error(f"Error saving profile image: {str(e)}")
        return None




    
    
@app.route('/submit_review', methods=['POST'])
@login_required
def submit_review():
    """Submit a review"""
    try:
        rating = int(request.form.get('rating', 0))
        review_text = request.form.get('review_text', '').strip()
        
        if not review_text or rating < 1 or rating > 5:
            flash('Please provide a valid rating (1-5) and review text!', 'error')
            return redirect(url_for('index'))
        
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''INSERT INTO reviews (user_id, username, rating, review_text) 
               VALUES (%s, %s, %s, %s)''',
            (current_user.id, current_user.name, rating, review_text)
        )
        mysql.connection.commit()
        cursor.close()
        
        flash('Thank you for your review! It will be visible after approval.', 'success')
        
    except Exception as e:
        logger.error(f"Error submitting review: {e}", exc_info=True)
        flash('Error submitting review. Please try again.', 'error')
    
    return redirect(url_for('index'))

@app.route('/submit_success_story', methods=['POST'])
@login_required
def submit_success_story():
    """Submit a success story"""
    try:
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        weight_lost = request.form.get('weight_lost', '0')
        time_period = request.form.get('time_period', '').strip()
        
        if not title or not description:
            flash('Title and description are required!', 'error')
            return redirect(url_for('index'))
        
        weight_lost_value = float(weight_lost) if weight_lost else 0
        before_image = None
        after_image = None
        
        # Handle before image
        if 'before_image' in request.files:
            file = request.files['before_image']
            if file and file.filename != '' and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"before_{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
                upload_folder = app.config['UPLOAD_FOLDER']
                
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                before_image = filename
        
        # Handle after image
        if 'after_image' in request.files:
            file = request.files['after_image']
            if file and file.filename != '' and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"after_{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
                upload_folder = app.config['UPLOAD_FOLDER']
                
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                after_image = filename
        
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''INSERT INTO success_stories 
               (user_id, title, description, before_image, after_image, weight_lost, time_period) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)''',
            (current_user.id, title, description, before_image, after_image, weight_lost_value, time_period)
        )
        mysql.connection.commit()
        cursor.close()
        
        flash('Your success story has been submitted for approval! Thank you for sharing.', 'success')
        
    except Exception as e:
        logger.error(f"Error submitting success story: {e}", exc_info=True)
        flash('Error submitting success story. Please try again.', 'error')
    
    return redirect(url_for('index'))



# Initialize MySQL


# ---------- HOME ----------


# ---------- CONTACT PAGE ----------
@app.route("/contact")
@login_required
def contact():
    """Contact/Consultation page - requires login"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT name, email FROM users WHERE id = %s',
            (current_user.id,)
        )
        user_data = cursor.fetchone()
        cursor.close()
        
        return render_template("contact.html", user=current_user, user_data=user_data)
    except Exception as e:
        logger.error(f"Error loading contact page: {e}")
        return render_template("contact.html", user=current_user, user_data=None)
    
    
def send_consultation_notification(consultation_id, name, email, program):
    try:
        subject = "New Consultation Request Received"

        body = f"""
New consultation request submitted.

Consultation ID : {consultation_id}
Name            : {name}
Email           : {email}
Program         : {program}

Please login to admin panel to review.
"""

        msg = MIMEMultipart()
        msg["From"] = current_app.config["MAIL_USERNAME"]
        msg["To"] = current_app.config["ADMIN_EMAIL"]
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(
            current_app.config["MAIL_SERVER"],
            current_app.config["MAIL_PORT"]
        )
        server.starttls()
        server.login(
            current_app.config["MAIL_USERNAME"],
            current_app.config["MAIL_PASSWORD"]
        )
        server.send_message(msg)
        server.quit()

    except Exception as e:
        raise e
  
    
    

# ---------- SUBMIT CONTACT ----------
@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    """Submit contact form"""
    try:
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Get additional fields if they exist
        program = request.form.get('interested_program', 'General Inquiry')
        goal = request.form.get('main_goal', 'Not specified')
        timeframe = request.form.get('target_timeframe', 'Not sure')

        # Validation
        if not all([name, email, subject, message]):
            return jsonify({'success': False, 'message': 'All required fields are required'}), 400
        
        # Clean phone number
        phone_clean = ''.join(filter(str.isdigit, phone)) if phone else ''
        if phone_clean and len(phone_clean) < 10:
            return jsonify({'success': False, 'message': 'Please enter a valid 10-digit phone number'}), 400
        
        if '@' not in email or '.' not in email:
            return jsonify({'success': False, 'message': 'Please enter a valid email address'}), 400

        # Get client IP and user agent
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')

        # Insert into database
        cursor = mysql.connection.cursor()
        
        # Try to get user_id if user is logged in
        user_id = None
        if current_user.is_authenticated:
            user_id = current_user.id
        
        # Insert into contact_messages table
        cursor.execute("""
            INSERT INTO contact_messages 
            (name, email, phone, subject, message, status, ip_address, user_agent, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            name,
            email,
            phone_clean if phone_clean else phone,
            subject,
            message,
            'new',
            ip_address,
            user_agent,
            datetime.now()
        ))

        mysql.connection.commit()
        cursor.close()

        return jsonify({
            'success': True,
            'message': 'Thank you! Your consultation request has been submitted successfully. We will contact you within 24 hours.'
        })

    except Exception as e:
        print("CONTACT ERROR:", str(e))
        return jsonify({
            'success': False,
            'message': 'An error occurred while submitting your message. Please try again later.'
        }), 500

# ==================== ADMIN ROUTES ====================

@app.route('/admin')
@login_required
def admin():
    """Admin dashboard"""
    if current_user.user_type != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    try:
        cursor = mysql.connection.cursor()
        
        # Get recent contact messages
        cursor.execute(
            '''SELECT id, name, email, phone, subject, message, status, created_at 
               FROM contact_messages ORDER BY created_at DESC LIMIT 10'''
        )
        messages = cursor.fetchall()
        
        # Get recent products
        cursor.execute(
            '''SELECT id, name, description, price, duration, features, available_offline, is_active, created_at 
               FROM products ORDER BY created_at DESC LIMIT 10'''
        )
        products = cursor.fetchall()
        
        # Get statistics
        stats = {}
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE user_type = "user"')
        stats['total_users'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM products WHERE is_active = TRUE')
        stats['total_products'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM contact_messages WHERE status = "new"')
        stats['new_messages'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM success_stories WHERE status = "approved"')
        stats['approved_stories'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM reviews WHERE status = "pending"')
        stats['pending_reviews'] = cursor.fetchone()['count']
        
        cursor.close()
        
        return render_template(
            'admin.html',
            messages=messages,
            products=products,
            stats=stats
        )
        
    except Exception as e:
        logger.error(f"Error loading admin panel: {e}", exc_info=True)
        flash('Error loading admin panel.', 'error')
        return render_template('admin.html', messages=[], products=[], stats={})




@app.route('/admin/consultation/<int:consultation_id>/update_status', methods=['POST'])
@login_required
def update_consultation_status(consultation_id):
    """Update consultation status"""
    if current_user.user_type != 'admin':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        status = request.form.get('status')
        if status not in ['pending', 'reviewed', 'responded']:
            return jsonify({'success': False, 'message': 'Invalid status'}), 400
        
        cursor = mysql.connection.cursor()
        cursor.execute(
            'UPDATE consultations SET status = %s WHERE id = %s',
            (status, consultation_id)
        )
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'success': True, 'message': f'Status updated to {status}'})
        
    except Exception as e:
        logger.error(f"Error updating consultation status: {e}")
        return jsonify({'success': False, 'message': 'Error updating status'}), 500




@app.route('/test-pdf')
def test_pdf():
    """Test PDF generation - to verify the problem"""
    try:
        from pdf_generator import generate_consultation_pdf
        
        # Create test data
        test_data = {
            'id': 999,
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '123-456-7890',
            'program': 'Weight Loss Program',
            'message': 'This is a test message for PDF generation.',
            'status': 'pending',
            'created_date': '2024-01-01',
            'created_time': '14:30',
            'reference': 'CONS-0999'
        }
        
        user_data = {
            'name': 'Test User',
            'email': 'test@example.com'
        }
        
        pdf_bytes = generate_consultation_pdf(test_data, user_data)
        
        if pdf_bytes:
            from io import BytesIO
            return send_file(
                BytesIO(pdf_bytes),
                as_attachment=True,
                download_name='test_pdf.pdf',
                mimetype='application/pdf'
            )
        else:
            return "PDF generation failed"
    except Exception as e:
        return f"Error: {str(e)}"




@app.route('/simple-pdf')
def simple_pdf():
    """Absolute simplest PDF that will always work"""
    from reportlab.pdfgen import canvas
    from io import BytesIO
    
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(612, 792))
    
    # Add some text
    c.setFont("Helvetica", 16)
    c.drawString(100, 700, "Wellness Coach Consultation")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, 650, "Test PDF - Should open in all readers")
    
    c.setFont("Helvetica", 10)
    c.drawString(100, 600, "Date: " + datetime.now().strftime("%Y-%m-%d"))
    c.drawString(100, 580, "This is a test PDF document.")
    
    c.showPage()
    c.save()
    
    buffer.seek(0)
    
    response = send_file(
        buffer,
        as_attachment=True,
        download_name='simple_test.pdf',
        mimetype='application/pdf'
    )
    
    return response



# Update the download route in your main Flask file
# Update the import at the top of your Flask file
from simple_pdf_generator import generate_simple_pdf

# Replace the download_consultation_pdf function completely with this:

# In your app.py, replace the PDF download route with this:

@app.route('/consultation/<int:consultation_id>/download')
@login_required
def download_consultation_pdf(consultation_id):
    """Download consultation as PDF - WORKING VERSION"""
    try:
        print(f"Starting PDF generation for consultation {consultation_id}")
        
        # Fetch consultation from database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        if current_user.user_type == 'admin':
            cursor.execute('''
                SELECT 
                    id, 
                    name, 
                    email, 
                    phone, 
                    subject, 
                    message, 
                    IFNULL(status, 'pending') as status,
                    DATE_FORMAT(created_at, "%%Y-%%m-%%d") as created_date,
                    DATE_FORMAT(created_at, "%%H:%%i") as created_time,
                    created_at
                FROM contact_messages 
                WHERE id = %s
            ''', (consultation_id,))
        else:
            cursor.execute('''
                SELECT 
                    id, 
                    name, 
                    email, 
                    phone, 
                    subject, 
                    message, 
                    IFNULL(status, 'pending') as status,
                    DATE_FORMAT(created_at, "%%Y-%%m-%%d") as created_date,
                    DATE_FORMAT(created_at, "%%H:%%i") as created_time,
                    created_at
                FROM contact_messages 
                WHERE id = %s AND email = %s
            ''', (consultation_id, current_user.email))
        
        consultation = cursor.fetchone()
        cursor.close()
        
        if not consultation:
            flash('Consultation not found or access denied', 'error')
            return redirect(url_for('profile'))
        
        print(f"Found consultation: {consultation['id']}")
        
        # Prepare data for PDF
        consultation_data = {
            'id': consultation['id'],
            'reference': f"CONS-{consultation['id']:04d}",
            'name': consultation['name'],
            'email': consultation['email'],
            'phone': consultation['phone'] or 'Not provided',
            'program': consultation['subject'] or 'General Inquiry',
            'subject': consultation['subject'] or 'General Inquiry',
            'message': consultation['message'] or 'No message provided',
            'status': consultation['status'] or 'pending',
            'created_date': consultation.get('created_date', 'N/A'),
            'created_time': consultation.get('created_time', 'N/A'),
        }
        
        # Prepare user data
        user_data = {
            'name': current_user.name or current_user.username,
            'email': current_user.email
        }
        
        # Generate PDF using the reliable function
        from pdf_generator import generate_consultation_pdf
        pdf_bytes = generate_consultation_pdf(consultation_data, user_data)
        
        if not pdf_bytes:
            raise ValueError("PDF generation returned empty")
        
        # Create filename (simple ASCII filename)
        filename = f"wellness_consultation_{consultation_id}.pdf"
        
        # Create response with proper headers
        response = send_file(
            io.BytesIO(pdf_bytes),
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
        # Add headers to ensure proper download
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.headers['Content-Length'] = len(pdf_bytes)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        print(f"PDF generated successfully: {len(pdf_bytes)} bytes")
        return response
        
    except Exception as e:
        print(f"PDF generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Last resort: create a very simple PDF
        try:
            from reportlab.pdfgen import canvas
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, 700, "Wellness Coach Consultation")
            c.setFont("Helvetica", 12)
            c.drawString(100, 650, f"Consultation ID: {consultation_id}")
            c.drawString(100, 625, f"Name: {current_user.name}")
            c.drawString(100, 600, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
            c.drawString(100, 550, "Could not generate detailed PDF.")
            c.drawString(100, 525, "Please contact support.")
            c.save()
            
            pdf_bytes = buffer.getvalue()
            filename = f"consultation_{consultation_id}_simple.pdf"
            
            return send_file(
                io.BytesIO(pdf_bytes),
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )
        except:
            flash('Failed to generate PDF. Please try again or contact support.', 'error')
            return redirect(url_for('profile'))




@app.route('/test-fpdf')
def test_fpdf():
    """Test FPDF generation"""
    try:
        from fpdf import FPDF
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Test PDF from FPDF', 0, 1, 'C')
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, 'This is a test PDF generated with FPDF.', 0, 1)
        pdf.cell(0, 10, f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1)
        
        pdf_bytes = pdf.output(dest='S')
        
        return send_file(
            BytesIO(pdf_bytes),
            as_attachment=True,
            download_name='test_fpdf.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        return f"Error: {str(e)}"









# Add this route for the print functionality
@app.route('/consultation/<int:consultation_id>/download2')
@login_required
def download_consultation_pdf_alt(consultation_id):
    """Alternative PDF download with fallback"""
    try:
        print(f"PDF Download (Alt) for consultation_id: {consultation_id}")
        
        # Fetch consultation data (same as before)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        if current_user.user_type == 'admin':
            cursor.execute(
                '''SELECT id, name, email, phone, subject as program, 
                          message, 
                          IFNULL(status, 'pending') as status, 
                          DATE_FORMAT(created_at, "%%Y-%%m-%%d") as created_date,
                          DATE_FORMAT(created_at, "%%I:%%i %%p") as created_time 
                   FROM contact_messages 
                   WHERE id = %s''',
                (consultation_id,)
            )
        else:
            cursor.execute(
                '''SELECT id, name, email, phone, subject as program, 
                          message, 
                          IFNULL(status, 'pending') as status, 
                          DATE_FORMAT(created_at, "%%Y-%%m-%%d") as created_date,
                          DATE_FORMAT(created_at, "%%I:%%i %%p") as created_time 
                   FROM contact_messages 
                   WHERE id = %s AND email = %s''',
                (consultation_id, current_user.email)
            )
        
        consultation = cursor.fetchone()
        cursor.close()
        
        if not consultation:
            return jsonify({'error': 'Consultation not found'}), 404
        
        # Prepare data
        consultation_data = {
            'id': consultation['id'],
            'program': consultation.get('program', 'General Inquiry'),
            'message': consultation.get('message', 'No message'),
            'status': consultation.get('status', 'pending'),
            'created_date': consultation.get('created_date', 'N/A'),
            'created_time': consultation.get('created_time', 'N/A'),
            'phone': consultation.get('phone', 'Not provided'),
            'reference': f"#CONS-{consultation['id']:04d}"
        }
        
        user_data = {
            'name': current_user.name or current_user.username,
            'email': current_user.email
        }
        
        # Try main generator first
        from pdf_generator import generate_consultation_pdf
        pdf_content = generate_consultation_pdf(consultation_data, user_data)
        
        # If main generator fails, try simple generator
        if not pdf_content or len(pdf_content) < 100:  # Check if PDF is too small
            print("Main generator failed, trying simple generator...")
            from simple_pdf import create_simple_pdf
            pdf_content = create_simple_pdf(consultation_data, user_data)
        
        if not pdf_content:
            raise Exception("Both PDF generators failed")
        
        # Create response
        response = send_file(
            BytesIO(pdf_content),
            as_attachment=True,
            download_name=f"consultation_{consultation_id}.pdf",
            mimetype='application/pdf'
        )
        
        response.headers['Content-Length'] = len(pdf_content)
        return response
        
    except Exception as e:
        print(f"PDF Download Error: {str(e)}")
        traceback.print_exc()
        # Return a very simple PDF as last resort
        return create_minimal_pdf(str(e))

def create_minimal_pdf(error_message):
    """Create a minimal PDF with just the error message"""
    from io import BytesIO
    from reportlab.pdfgen import canvas
    
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 700, "PDF Generation Error")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, 650, "Could not generate consultation PDF.")
    c.drawString(100, 625, "Error details:")
    
    c.setFont("Helvetica", 10)
    # Show truncated error message
    if len(error_message) > 100:
        error_message = error_message[:100] + "..."
    c.drawString(100, 600, error_message)
    
    c.drawString(100, 550, "Please try again or contact support.")
    
    c.save()
    
    pdf_data = buffer.getvalue()
    buffer.close()
    
    response = send_file(
        BytesIO(pdf_data),
        as_attachment=True,
        download_name="error.pdf",
        mimetype='application/pdf'
    )
    
    response.headers['Content-Length'] = len(pdf_data)
    return response


@app.route('/admin/users')
@login_required
def admin_users():
    """Admin users management"""
    if current_user.user_type != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''SELECT id, username, email, name, user_type, profile_image, created_at 
               FROM users ORDER BY created_at DESC'''
        )
        users = cursor.fetchall()
        
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE user_type = "user"')
        total_users = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE user_type = "admin"')
        total_admins = cursor.fetchone()['count']
        
        # Additional statistics for enhanced UI
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE DATE(created_at) = CURDATE()')
        new_users_today = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE user_type = "user"')
        active_users = cursor.fetchone()['count']  # You might want to add last_active field
        
        cursor.close()
        
        return render_template(
            'admin_users.html',
            users=users,
            total_users=total_users,
            total_admins=total_admins,
            new_users_today=new_users_today,
            active_users=active_users
        )
        
    except Exception as e:
        logger.error(f"Error loading admin users: {e}", exc_info=True)
        flash('Error loading users.', 'error')
        return render_template('admin_users.html', 
                             users=[], 
                             total_users=0, 
                             total_admins=0,
                             new_users_today=0,
                             active_users=0)

# Add API endpoints for AJAX calls
@app.route('/admin/api/user/<int:user_id>')
@login_required
def get_user_api(user_id):
    if current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    cursor = mysql.connection.cursor()
    cursor.execute(
        '''SELECT id, username, email, name, user_type, created_at 
           FROM users WHERE id = %s''',
        (user_id,)
    )
    user = cursor.fetchone()
    cursor.close()
    
    if user:
        return jsonify(user)
    return jsonify({'error': 'User not found'}), 404

@app.route('/admin/api/user/save', methods=['POST'])
@login_required
def save_user_api():
    if current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = request.json
        cursor = mysql.connection.cursor()
        
        if 'id' in data:
            # Update existing user
            cursor.execute(
                '''UPDATE users SET username = %s, email = %s, name = %s, user_type = %s 
                   WHERE id = %s''',
                (data['username'], data['email'], data['name'], data['user_type'], data['id'])
            )
        else:
            # Create new user
            hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
            cursor.execute(
                '''INSERT INTO users (username, email, name, password, user_type) 
                   VALUES (%s, %s, %s, %s, %s)''',
                (data['username'], data['email'], data['name'], hashed_password, data['user_type'])
            )
        
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'success': True, 'message': 'User saved successfully'})
        
    except Exception as e:
        logger.error(f"Error saving user: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/api/user/<int:user_id>/delete', methods=['DELETE'])
@login_required
def delete_user_api(user_id):
    if current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        if user_id == current_user.id:
            return jsonify({'success': False, 'error': 'Cannot delete yourself'})
        
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'success': True, 'message': 'User deleted successfully'})
        
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        return jsonify({'success': False, 'error': str(e)})
@app.route('/admin/reviews')
@login_required
def admin_reviews():
    """Admin reviews management"""
    if current_user.user_type != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    try:
        cursor = mysql.connection.cursor()
        
        # Get all reviews
        cursor.execute(
            '''SELECT r.id, r.rating, r.review_text, r.status, r.created_at,
                      u.name as user_name, u.email as user_email
               FROM reviews r
               LEFT JOIN users u ON r.user_id = u.id
               ORDER BY r.created_at DESC'''
        )
        reviews = cursor.fetchall()
        
        # Get review statistics
        review_stats = {}
        
        # Count by status
        cursor.execute('SELECT COUNT(*) as count FROM reviews WHERE status = "pending"')
        review_stats['pending_reviews'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM reviews WHERE status = "approved"')
        review_stats['approved_reviews'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM reviews WHERE status = "rejected"')
        review_stats['rejected_reviews'] = cursor.fetchone()['count']
        
        # Get total reviews
        cursor.execute('SELECT COUNT(*) as count FROM reviews')
        review_stats['total_reviews'] = cursor.fetchone()['count']
        
        # Get average rating
        cursor.execute('SELECT AVG(rating) as avg_rating FROM reviews WHERE status = "approved"')
        avg_result = cursor.fetchone()['avg_rating']
        review_stats['average_rating'] = round(float(avg_result or 0), 1)
        
        # Get star distribution
        for i in range(1, 6):
            cursor.execute('SELECT COUNT(*) as count FROM reviews WHERE rating = %s', (i,))
            # Use string formatting in Python (not Jinja2)
            review_stats[f'{i}_star'] = cursor.fetchone()['count']
        
        cursor.close()
        
        return render_template(
            'admin_reviews.html',
            reviews=reviews,
            review_stats=review_stats
        )
        
    except Exception as e:
        logger.error(f"Error loading admin reviews: {e}", exc_info=True)
        flash('Error loading reviews.', 'error')
        return render_template('admin_reviews.html', reviews=[], review_stats={})
    
@app.route('/admin/bulk_approve_reviews', methods=['POST'])
@login_required
def bulk_approve_reviews():
    if current_user.user_type != 'admin':
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    try:
        data = request.json
        review_ids = data.get('review_ids', [])
        
        cursor = mysql.connection.cursor()
        cursor.execute(
            'UPDATE reviews SET status = "approved" WHERE id IN %s',
            (tuple(review_ids),)
        )
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'success': True, 'message': f'{len(review_ids)} reviews approved successfully'})
        
    except Exception as e:
        logger.error(f"Error bulk approving reviews: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/bulk_reject_reviews', methods=['POST'])
@login_required
def bulk_reject_reviews():
    if current_user.user_type != 'admin':
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    try:
        data = request.json
        review_ids = data.get('review_ids', [])
        
        cursor = mysql.connection.cursor()
        cursor.execute(
            'UPDATE reviews SET status = "rejected" WHERE id IN %s',
            (tuple(review_ids),)
        )
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'success': True, 'message': f'{len(review_ids)} reviews rejected successfully'})
        
    except Exception as e:
        logger.error(f"Error bulk rejecting reviews: {e}")
        return jsonify({'success': False, 'error': str(e)})




@app.route('/admin/bulk_delete_reviews', methods=['POST'])
@login_required
def bulk_delete_reviews():
    if current_user.user_type != 'admin':
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    try:
        data = request.json
        review_ids = data.get('review_ids', [])
        
        cursor = mysql.connection.cursor()
        cursor.execute(
            'DELETE FROM reviews WHERE id IN %s',
            (tuple(review_ids),)
        )
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'success': True, 'message': f'{len(review_ids)} reviews deleted successfully'})
        
    except Exception as e:
        logger.error(f"Error bulk deleting reviews: {e}")
        return jsonify({'success': False, 'error': str(e)})





@app.route('/admin/messages')
@login_required
def admin_messages():
    """Admin contact messages management"""
    if current_user.user_type != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    try:
        cursor = mysql.connection.cursor()
        
        # Get all messages
        cursor.execute(
            '''SELECT id, name, email, phone, subject, message, status, created_at 
               FROM contact_messages 
               ORDER BY 
                   CASE 
                       WHEN status = 'new' THEN 1 
                       WHEN status = 'read' THEN 2 
                       ELSE 3 
                   END,
                   created_at DESC'''
        )
        messages = cursor.fetchall()
        
        # Get statistics
        cursor.execute('SELECT COUNT(*) as count FROM contact_messages WHERE status = "new"')
        pending_messages = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM contact_messages')
        total_messages = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM contact_messages WHERE status = "read"')
        read_messages = cursor.fetchone()['count']
        
        cursor.close()
        
        return render_template(
            'admin_messages.html',
            messages=messages,
            pending_messages=pending_messages,
            total_messages=total_messages,
            read_messages=read_messages
        )
        
    except Exception as e:
        logger.error(f"Error loading admin messages: {e}", exc_info=True)
        flash('Error loading messages.', 'error')
        return render_template('admin_messages.html', messages=[], pending_messages=0, total_messages=0, read_messages=0)

@app.route('/admin/stories')
@login_required
def admin_stories():
    """Admin success stories management"""
    if current_user.user_type != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    try:
        cursor = mysql.connection.cursor()
        
        cursor.execute(
            '''SELECT s.id, s.title, s.description, s.before_image, s.after_image, 
                      s.weight_lost, s.time_period, s.status, s.created_at,
                      u.name as user_name, u.email as user_email
               FROM success_stories s
               LEFT JOIN users u ON s.user_id = u.id
               ORDER BY s.created_at DESC'''
        )
        stories = cursor.fetchall()
        
        stats = {}
        cursor.execute('SELECT COUNT(*) as count FROM success_stories WHERE status = "pending"')
        stats['pending_stories'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM success_stories WHERE status = "approved"')
        stats['approved_stories'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM success_stories WHERE status = "rejected"')
        stats['rejected_stories'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM success_stories')
        stats['total_stories'] = cursor.fetchone()['count']
        
        cursor.close()
        
        # Pass the current datetime to the template as 'now'
        return render_template(
            'admin_stories.html',
            stories=stories,
            stats=stats,
            now=datetime.now()  # Add this line
        )
        
    except Exception as e:
        logger.error(f"Error loading admin stories: {e}", exc_info=True)
        flash('Error loading success stories.', 'error')
        return render_template('admin_stories.html', stories=[], stats={}, now=datetime.now())  # Add now here too

@app.route('/admin/approve_review/<int:review_id>')
@login_required
def approve_review(review_id):
    """Approve a review"""
    if current_user.user_type != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE reviews SET status = "approved" WHERE id = %s', (review_id,))
        mysql.connection.commit()
        cursor.close()
        flash('Review approved successfully!', 'success')
    except Exception as e:
        logger.error(f"Error approving review {review_id}: {e}")
        flash('Error approving review.', 'error')
    
    return redirect(url_for('admin_reviews'))



@app.route('/admin/reject_review/<int:review_id>')
@login_required
def reject_review(review_id):
    """Reject a review"""
    if current_user.user_type != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE reviews SET status = "rejected" WHERE id = %s', (review_id,))
        mysql.connection.commit()
        cursor.close()
        flash('Review rejected successfully!', 'success')
    except Exception as e:
        logger.error(f"Error rejecting review {review_id}: {e}")
        flash('Error rejecting review.', 'error')
    
    return redirect(url_for('admin_reviews'))

@app.route('/admin/approve_story/<int:story_id>')
@login_required
def approve_story(story_id):
    """Approve a success story"""
    if current_user.user_type != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE success_stories SET status = "approved" WHERE id = %s', (story_id,))
        mysql.connection.commit()
        cursor.close()
        flash('Success story approved successfully!', 'success')
    except Exception as e:
        logger.error(f"Error approving story {story_id}: {e}")
        flash('Error approving story.', 'error')
    
    return redirect(url_for('admin_stories'))

@app.route('/admin/reject_story/<int:story_id>')
@login_required
def reject_story(story_id):
    """Reject a success story"""
    if current_user.user_type != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE success_stories SET status = "rejected" WHERE id = %s', (story_id,))
        mysql.connection.commit()
        cursor.close()
        flash('Success story rejected successfully!', 'success')
    except Exception as e:
        logger.error(f"Error rejecting story {story_id}: {e}")
        flash('Error rejecting story.', 'error')
    
    return redirect(url_for('admin_stories'))

@app.route('/admin/mark_message_read/<int:message_id>')
@login_required
def mark_message_read(message_id):
    """Mark message as read"""
    if current_user.user_type != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE contact_messages SET status = "read" WHERE id = %s', (message_id,))
        mysql.connection.commit()
        cursor.close()
        flash('Message marked as read!', 'success')
    except Exception as e:
        logger.error(f"Error marking message {message_id} as read: {e}")
        flash('Error marking message as read.', 'error')
    
    return redirect(url_for('admin_messages'))

@app.route('/admin/mark_message_replied/<int:message_id>')
@login_required
def mark_message_replied(message_id):
    """Mark message as replied"""
    if current_user.user_type != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE contact_messages SET status = "replied" WHERE id = %s', (message_id,))
        mysql.connection.commit()
        cursor.close()
        flash('Message marked as replied!', 'success')
    except Exception as e:
        logger.error(f"Error marking message {message_id} as replied: {e}")
        flash('Error marking message as replied.', 'error')
    
    return redirect(url_for('admin_messages'))

@app.route('/admin/delete_message/<int:message_id>')
@login_required
def delete_message(message_id):
    """Delete contact message"""
    if current_user.user_type != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM contact_messages WHERE id = %s', (message_id,))
        mysql.connection.commit()
        cursor.close()
        flash('Message deleted successfully!', 'success')
    except Exception as e:
        logger.error(f"Error deleting message {message_id}: {e}")
        flash('Error deleting message.', 'error')
    
    return redirect(url_for('admin_messages'))

@app.route('/admin/add_product', methods=['POST'])
@login_required
def add_product():
    """Add new product (admin only)"""
    if current_user.user_type != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('admin'))
    
    try:
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = float(request.form.get('price', 0))
        duration = request.form.get('duration', '').strip()
        available_offline = 'available_offline' in request.form
        
        if not name or price <= 0:
            flash('Product name and valid price are required!', 'error')
            return redirect(url_for('admin'))
        
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''INSERT INTO products (name, description, price, duration, available_offline) 
               VALUES (%s, %s, %s, %s, %s)''',
            (name, description, price, duration, available_offline)
        )
        mysql.connection.commit()
        cursor.close()
        
        flash(f'Product "{name}" added successfully!', 'success')
        
    except Exception as e:
        logger.error(f"Error adding product: {e}")
        flash('Error adding product.', 'error')
    
    return redirect(url_for('admin'))

@app.route('/admin/update_product/<int:product_id>', methods=['POST'])
@login_required
def update_product(product_id):
    """Update product (admin only)"""
    if current_user.user_type != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('admin'))
    
    try:
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = float(request.form.get('price', 0))
        duration = request.form.get('duration', '').strip()
        available_offline = 'available_offline' in request.form
        is_active = 'is_active' in request.form
        
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''UPDATE products 
               SET name = %s, description = %s, price = %s, duration = %s, 
                   available_offline = %s, is_active = %s 
               WHERE id = %s''',
            (name, description, price, duration, available_offline, is_active, product_id)
        )
        mysql.connection.commit()
        cursor.close()
        
        flash(f'Product "{name}" updated successfully!', 'success')
        
    except Exception as e:
        logger.error(f"Error updating product: {e}")
        flash('Error updating product.', 'error')
    
    return redirect(url_for('admin'))

@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    """Delete product (admin only)"""
    if current_user.user_type != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('admin'))
    
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM products WHERE id = %s', (product_id,))
        mysql.connection.commit()
        cursor.close()
        
        flash('Product deleted successfully!', 'success')
        
    except Exception as e:
        logger.error(f"Error deleting product: {e}")
        flash('Error deleting product.', 'error')
    
    return redirect(url_for('admin'))

# ==================== PUBLIC ROUTES ====================

@app.route('/programs')
def programs():
    """Programs listing page"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''SELECT id, name, description, price, duration, features, available_offline 
               FROM products WHERE is_active = TRUE ORDER BY price'''
        )
        programs = cursor.fetchall()
        cursor.close()
        
        return render_template('programs.html', programs=programs)
        
    except Exception as e:
        logger.error(f"Error loading programs: {e}", exc_info=True)
        flash('Error loading programs.', 'error')
        return render_template('programs.html', programs=[])

@app.route('/success_stories')
def success_stories():
    """Success stories page"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''SELECT id, title, description, before_image, after_image, weight_lost, time_period, created_at 
               FROM success_stories WHERE status = "approved" ORDER BY created_at DESC'''
        )
        stories = cursor.fetchall()
        cursor.close()
        
        return render_template('success_stories.html', stories=stories)
        
    except Exception as e:
        logger.error(f"Error loading success stories: {e}", exc_info=True)
        flash('Error loading success stories.', 'error')
        return render_template('success_stories.html', stories=[])

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    try:
        cursor = mysql.connection.cursor()
        
        cursor.execute('SELECT COUNT(*) as total_users FROM users WHERE user_type = "user"')
        total_users = cursor.fetchone()['total_users']
        
        cursor.execute('SELECT COUNT(*) as total_products FROM products WHERE is_active = TRUE')
        total_products = cursor.fetchone()['total_products']
        
        cursor.execute('SELECT COUNT(*) as total_reviews FROM reviews WHERE status = "approved"')
        total_reviews = cursor.fetchone()['total_reviews']
        
        cursor.execute('SELECT AVG(rating) as avg_rating FROM reviews WHERE status = "approved"')
        avg_rating = cursor.fetchone()['avg_rating']
        success_rate = round((avg_rating or 0) * 20, 1)
        
        cursor.close()
        
        return jsonify({
            'total_users': total_users,
            'total_products': total_products,
            'total_reviews': total_reviews,
            'success_rate': success_rate,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
        
@app.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html"), 500

# ==================== DEBUG & DIAGNOSTIC ROUTES ====================


@app.route('/debug/test-password', methods=['POST'])
def debug_test_password():
    """Test password verification"""
    email = request.form.get('email')
    password = request.form.get('password')
    
    user = User.authenticate(email, password, mysql)
    
    if user:
        return f"""
        <h1>Password Test Result</h1>
        <p> Password verification SUCCESSFUL for {email}</p>
        <p>User: {user.name} ({user.user_type})</p>
        <p><a href="/debug/admin-check">Back to Debug</a></p>
        """
    else:
        return f"""
        <h1>Password Test Result</h1>
        <p> Password verification FAILED for {email}</p>
        <p><a href="/debug/admin-check">Back to Debug</a></p>
        """

@app.route('/debug/reset-admin-password')
def reset_admin_password():
    """Reset admin password to default"""
    try:
        cursor = mysql.connection.cursor()
        
        admin_password = 'admin@7671'
        hashed_password = generate_password_hash(admin_password, method='pbkdf2:sha256')
        
        # Check if admin exists
        cursor.execute("SELECT id FROM users WHERE email = 'admin@wellness.com'")
        admin = cursor.fetchone()
        
        if admin:
            # Update existing admin
            cursor.execute(
                "UPDATE users SET password = %s WHERE email = 'admin@wellness.com'",
                (hashed_password,)
            )
            action = "updated"
        else:
            # Create new admin
            cursor.execute(
                '''INSERT INTO users (username, email, name, password, user_type) 
                   VALUES (%s, %s, %s, %s, %s)''',
                ('admin', 'admin@wellness.com', 'Wellness Admin', hashed_password, 'admin')
            )
            action = "created"
        
        mysql.connection.commit()
        cursor.close()
        
        return f"""
        <h1>Admin Password Reset</h1>
        <p>✅ Admin password {action} successfully!</p>
        <p>Email: admin@wellness.com</p>
        <p>Password: admin@7671</p>
        <p>Hash: {hashed_password[:50]}...</p>
        <p><a href="/debug/admin-check">Check Admin Details</a></p>
        <p><a href="/admin-login-test">Test Admin Login</a></p>
        """
        
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>"

@app.route('/debug/test-contact-form')
def debug_test_contact_form():
    """Simple test contact form"""
    return """
    <html>
    <head><title>Test Contact Form</title></head>
    <body>
        <h2>Test Contact Form</h2>
        <form method="POST" action="/contact">
            <input type="text" name="name" placeholder="Name" required><br>
            <input type="email" name="email" placeholder="Email" required><br>
            <input type="text" name="phone" placeholder="Phone (optional)"><br>
            <input type="text" name="subject" placeholder="Subject" required><br>
            <textarea name="message" placeholder="Message" required></textarea><br>
            <button type="submit">Send Message</button>
        </form>
    </body>
    </html>
    """

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def page_not_found(e):
    """404 error handler"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """500 error handler"""
    logger.error(f"Internal server error: {e}", exc_info=True)
    return render_template('500.html'), 500

@app.errorhandler(413)
def request_entity_too_large(e):
    """413 error handler for large files"""
    flash('File size too large. Maximum size is 16MB.', 'error')
    return redirect(request.url)

# ==================== APPLICATION STARTUP ====================

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Print startup banner
    print("\n" + "=" * 60)
    print("WELLNESS COACH APPLICATION")
    print("=" * 60)
    print(f"Database: {app.config['MYSQL_DB']}")
    print(f"Host: {app.config['MYSQL_HOST']}")
    print(f"User: {app.config['MYSQL_USER']}")
    print("=" * 60)
    print("Admin Credentials:")
    print("  Email: admin@wellness.com")
    print("  Password: admin@7671")
    print("=" * 60)
    print("Debug URLs:")
    print("  /debug/admin-check - Check admin credentials")
    print("  /debug/reset-admin-password - Reset admin password")
    print("  /admin-login-test - Direct admin login test")
    print("  /debug/test-contact-form - Test contact form")
    print("=" * 60)
    print("CONTACT ROUTE HIT")

    
    # Initialize database
    try:
        with app.app_context():
            init_database()
        print(" Database initialized successfully")
    except Exception as e:
        print(f" Database initialization error: {e}")
    
    print("=" * 60)
    print("Starting server at http://localhost:5800")
    print("=" * 60 + "\n")
    
    # Run the application

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)












