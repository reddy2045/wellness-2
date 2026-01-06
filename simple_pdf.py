from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from datetime import datetime

def create_simple_pdf(consultation_data, user_data):
    """Create a simple PDF using canvas API"""
    buffer = BytesIO()
    
    try:
        # Create canvas
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Set title
        c.setFont("Helvetica-Bold", 24)
        c.drawString(100, height - 100, "Wellness Coach Consultation")
        
        # Draw line
        c.setStrokeColorRGB(0.2, 0.6, 0.4)
        c.setLineWidth(2)
        c.line(100, height - 120, width - 100, height - 120)
        
        # Reference
        c.setFont("Helvetica", 12)
        c.drawString(100, height - 150, f"Reference: {consultation_data.get('reference', '#CONS-0000')}")
        c.drawString(100, height - 170, f"Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        
        # Consultation Details
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, height - 220, "Consultation Details")
        
        c.setFont("Helvetica", 12)
        y_pos = height - 250
        details = [
            f"Status: {consultation_data.get('status', 'Pending').title()}",
            f"Program: {consultation_data.get('program', 'General Inquiry')}",
            f"Submitted Date: {consultation_data.get('created_date', 'N/A')}",
            f"Submitted Time: {consultation_data.get('created_time', 'N/A')}"
        ]
        
        for detail in details:
            c.drawString(100, y_pos, detail)
            y_pos -= 25
        
        # Personal Information
        c.setFont("Helvetica-Bold", 16)
        y_pos -= 20
        c.drawString(100, y_pos, "Personal Information")
        
        c.setFont("Helvetica", 12)
        y_pos -= 30
        personal = [
            f"Name: {user_data.get('name', 'Not specified')}",
            f"Email: {user_data.get('email', 'Not specified')}",
            f"Phone: {consultation_data.get('phone', 'Not specified')}"
        ]
        
        for info in personal:
            c.drawString(100, y_pos, info)
            y_pos -= 25
        
        # Message
        c.setFont("Helvetica-Bold", 16)
        y_pos -= 20
        c.drawString(100, y_pos, "Your Message")
        
        c.setFont("Helvetica", 12)
        y_pos -= 30
        message = consultation_data.get('message', 'No message provided')
        
        # Split message into lines
        words = message.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            if len(' '.join(current_line)) > 80:
                lines.append(' '.join(current_line[:-1]))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw each line
        for line in lines[:20]:  # Limit to 20 lines
            if y_pos < 100:  # Start new page if needed
                c.showPage()
                y_pos = height - 100
                c.setFont("Helvetica", 12)
            
            c.drawString(100, y_pos, line)
            y_pos -= 20
        
        # Footer
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0.5, 0.5, 0.5)
        c.drawString(100, 50, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(100, 30, "© Wellness Coach - Confidential Document")
        
        # Save PDF
        c.save()
        
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
        
    except Exception as e:
        print(f"Simple PDF Error: {str(e)}")
        return None