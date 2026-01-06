# pdf_generator.py
import io
import logging
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

logger = logging.getLogger(__name__)

def generate_consultation_pdf(consultation_data, user_data=None):
    """
    Generate a clean, reliable PDF for consultation
    """
    try:
        # Create a BytesIO buffer
        buffer = io.BytesIO()
        
        # Create PDF document with simple settings
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40,
            title=f"Consultation {consultation_data.get('id', 'N/A')}"
        )
        
        # Container for PDF elements
        elements = []
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles with simple font names
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontName='Helvetica-Bold',
            fontSize=18,
            textColor=colors.black,
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=colors.black,
            spaceAfter=10,
            spaceBefore=15
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            textColor=colors.black,
            spaceAfter=8,
            leading=14
        )
        
        # Title
        elements.append(Paragraph("Wellness Coach Consultation Summary", title_style))
        elements.append(Spacer(1, 15))
        
        # Reference and Date
        reference = consultation_data.get('reference', f"CONS-{consultation_data.get('id', '0000')}")
        elements.append(Paragraph(f"Reference: {reference}", normal_style))
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", normal_style))
        elements.append(Spacer(1, 20))
        
        # Section 1: Consultation Overview
        elements.append(Paragraph("Consultation Overview", heading_style))
        
        # Format the date and time properly
        created_date = consultation_data.get('created_date', 'N/A')
        created_time = consultation_data.get('created_time', 'N/A')
        
        # If date/time are in database format, format them nicely
        if created_date != 'N/A' and created_time != 'N/A':
            try:
                # Try to parse if they're in database format
                if '-' in created_date and ':' in created_time:
                    # Already formatted by SQL query
                    pass
                else:
                    # Try to format from timestamp if needed
                    pass
            except:
                pass
        
        overview_data = [
            ['Status:', consultation_data.get('status', 'pending').title()],
            ['Program:', consultation_data.get('program', consultation_data.get('subject', 'General Inquiry'))],
            ['Submitted Date:', created_date],
            ['Submitted Time:', created_time]
        ]
        
        overview_table = Table(overview_data, colWidths=[1.5*inch, 4*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        elements.append(overview_table)
        elements.append(Spacer(1, 15))
        
        # Section 2: Personal Information
        elements.append(Paragraph("Personal Information", heading_style))
        
        # Use user data if available, otherwise fall back to consultation data
        if user_data:
            name = user_data.get('name', consultation_data.get('name', 'N/A'))
            email = user_data.get('email', consultation_data.get('email', 'N/A'))
        else:
            name = consultation_data.get('name', 'N/A')
            email = consultation_data.get('email', 'N/A')
        
        personal_data = [
            ['Full Name:', name],
            ['Email:', email],
            ['Phone:', consultation_data.get('phone', 'Not provided')]
        ]
        
        personal_table = Table(personal_data, colWidths=[1.5*inch, 4*inch])
        personal_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        elements.append(personal_table)
        elements.append(Spacer(1, 15))
        
        # Section 3: Message
        elements.append(Paragraph("Your Message", heading_style))
        
        message = consultation_data.get('message', 'No message provided')
        # Clean up the message
        if isinstance(message, str):
            # Replace HTML line breaks with newlines
            message = message.replace('<br>', '\n').replace('<br/>', '\n').replace('</br>', '\n')
            # Escape special characters
            message = message.replace('&nbsp;', ' ')
        
        # Create paragraph with proper line breaks
        message_para = Paragraph(f"<b>Message:</b><br/><br/>{message}", normal_style)
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
            fontName='Helvetica-Oblique',
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER,
            spaceBefore=20
        )
        
        elements.append(Paragraph("This document is confidential and intended solely for the recipient.", footer_style))
        elements.append(Paragraph("© Wellness Coach. All rights reserved.", footer_style))
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF value
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        # Verify PDF is valid
        if pdf_bytes.startswith(b'%PDF'):
            return pdf_bytes
        else:
            logger.error("Generated PDF does not start with PDF header")
            raise ValueError("Invalid PDF generated")
            
    except Exception as e:
        logger.error(f"Error in PDF generation: {str(e)}")
        # Fallback to simple PDF
        return create_simple_consultation_pdf(consultation_data, user_data)

def create_simple_consultation_pdf(consultation_data, user_data=None):
    """Create a simple, guaranteed-to-work PDF"""
    buffer = io.BytesIO()
    
    # Create canvas with simple settings
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "Wellness Coach Consultation Summary")
    
    # Reference and Date
    c.setFont("Helvetica", 10)
    reference = consultation_data.get('reference', f"CONS-{consultation_data.get('id', '0000')}")
    c.drawString(50, 730, f"Reference: {reference}")
    c.drawString(50, 715, f"Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    
    # Line
    c.line(50, 700, 550, 700)
    
    # Consultation Overview
    y = 680
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Consultation Overview")
    
    y -= 25
    c.setFont("Helvetica", 10)
    overview_items = [
        f"Status: {consultation_data.get('status', 'pending').title()}",
        f"Program: {consultation_data.get('program', consultation_data.get('subject', 'General Inquiry'))}",
        f"Submitted Date: {consultation_data.get('created_date', 'N/A')}",
        f"Submitted Time: {consultation_data.get('created_time', 'N/A')}"
    ]
    
    for item in overview_items:
        c.drawString(50, y, item)
        y -= 20
    
    # Personal Information
    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Personal Information")
    
    y -= 25
    c.setFont("Helvetica", 10)
    
    # Get name and email
    if user_data:
        name = user_data.get('name', consultation_data.get('name', 'N/A'))
        email = user_data.get('email', consultation_data.get('email', 'N/A'))
    else:
        name = consultation_data.get('name', 'N/A')
        email = consultation_data.get('email', 'N/A')
    
    personal_items = [
        f"Name: {name}",
        f"Email: {email}",
        f"Phone: {consultation_data.get('phone', 'Not provided')}"
    ]
    
    for item in personal_items:
        c.drawString(50, y, item)
        y -= 20
    
    # Message
    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Message")
    
    y -= 25
    c.setFont("Helvetica", 10)
    
    message = consultation_data.get('message', 'No message provided')
    # Break message into lines
    lines = []
    words = message.split()
    line = ""
    
    for word in words:
        if len(line) + len(word) + 1 <= 80:
            line = f"{line} {word}" if line else word
        else:
            lines.append(line)
            line = word
    
    if line:
        lines.append(line)
    
    # Display message (max 20 lines)
    for i, line in enumerate(lines[:20]):
        if y < 100:  # Don't go too low
            break
        c.drawString(50, y, line)
        y -= 15
    
    # Next Steps
    y = max(y, 100) - 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Next Steps")
    
    y -= 25
    c.setFont("Helvetica", 10)
    
    status = consultation_data.get('status', 'pending').lower()
    if status == 'pending':
        steps = "Your consultation is under review. We'll contact you within 48 hours."
    elif status == 'reviewed':
        steps = "Your consultation has been reviewed. Personalized plan is being prepared."
    elif status == 'responded':
        steps = "Response has been provided. Check your email for recommendations."
    else:
        steps = "Thank you for your consultation request."
    
    # Break steps into lines
    step_lines = []
    step_words = steps.split()
    step_line = ""
    
    for word in step_words:
        if len(step_line) + len(word) + 1 <= 80:
            step_line = f"{step_line} {word}" if step_line else word
        else:
            step_lines.append(step_line)
            step_line = word
    
    if step_line:
        step_lines.append(step_line)
    
    for line in step_lines:
        c.drawString(50, y, line)
        y -= 15
    
    # Footer
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, 50, "© Wellness Coach - Confidential Document")
    
    # Save the PDF
    c.save()
    
    # Get the PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes