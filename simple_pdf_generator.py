# simple_pdf_generator.py
from fpdf import FPDF
from datetime import datetime
import os

class PDF(FPDF):
    def header(self):
        # Logo
        self.image('static/images/logo.png', 10, 8, 33)
        # Title
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Wellness Coach Consultation', 0, 1, 'C')
        self.set_font('Arial', 'I', 12)
        self.cell(0, 10, 'Your Health, Our Priority', 0, 1, 'C')
        # Line break
        self.ln(10)
    
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')
        # Copyright
        self.set_x(-50)
        self.cell(0, 10, '© Wellness Coach', 0, 0, 'R')

def generate_simple_pdf(consultation_data, user_data=None):
    """Generate simple PDF using FPDF (more reliable)"""
    try:
        pdf = PDF()
        pdf.alias_nb_pages()
        pdf.add_page()
        
        # Set default user data if not provided
        if not user_data:
            user_data = {
                'name': consultation_data.get('name', 'User'),
                'email': consultation_data.get('email', 'N/A')
            }
        
        # Title
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, f"Consultation #{consultation_data.get('id', 'N/A')}", 0, 1)
        pdf.ln(5)
        
        # Reference and Date
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 8, f"Reference: {consultation_data.get('reference', 'N/A')}", 0, 1)
        pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 0, 1)
        pdf.ln(10)
        
        # Section 1: Consultation Details
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Consultation Details', 0, 1)
        pdf.set_font('Arial', '', 11)
        
        details = [
            ('Status:', consultation_data.get('status', 'pending').title()),
            ('Program:', consultation_data.get('program', 'General Inquiry')),
            ('Submitted Date:', consultation_data.get('created_date', 'N/A')),
            ('Submitted Time:', consultation_data.get('created_time', 'N/A'))
        ]
        
        for label, value in details:
            pdf.cell(40, 8, label, 0, 0)
            pdf.cell(0, 8, str(value), 0, 1)
        
        pdf.ln(5)
        
        # Section 2: Personal Information
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Personal Information', 0, 1)
        pdf.set_font('Arial', '', 11)
        
        personal_info = [
            ('Name:', user_data.get('name', consultation_data.get('name', 'N/A'))),
            ('Email:', user_data.get('email', consultation_data.get('email', 'N/A'))),
            ('Phone:', consultation_data.get('phone', 'Not provided'))
        ]
        
        for label, value in personal_info:
            pdf.cell(40, 8, label, 0, 0)
            pdf.cell(0, 8, str(value), 0, 1)
        
        pdf.ln(5)
        
        # Section 3: Message
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Your Message', 0, 1)
        pdf.set_font('Arial', '', 11)
        
        message = consultation_data.get('message', 'No message provided')
        # Handle long messages with multi_cell
        pdf.multi_cell(0, 8, message)
        
        pdf.ln(10)
        
        # Section 4: Next Steps
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Next Steps', 0, 1)
        pdf.set_font('Arial', '', 11)
        
        status = consultation_data.get('status', 'pending').lower()
        if status == 'pending':
            steps = "Your consultation is currently under review. Our wellness coach will analyze your requirements and get back to you within 48 hours."
        elif status == 'reviewed':
            steps = "Your consultation has been reviewed. Our wellness coach is preparing a personalized plan for you."
        elif status == 'responded':
            steps = "Response has been provided. Please check your email for detailed recommendations."
        else:
            steps = "Thank you for reaching out. You will be contacted within 24 hours."
        
        pdf.multi_cell(0, 8, steps)
        
        pdf.ln(15)
        
        # Footer note
        pdf.set_font('Arial', 'I', 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 8, 'This document is confidential and intended solely for the recipient.', 0, 1, 'C')
        pdf.cell(0, 8, '© Wellness Coach. All rights reserved.', 0, 1, 'C')
        
        # Generate PDF bytes
        return pdf.output(dest='S')
        
    except Exception as e:
        print(f"Error in generate_simple_pdf: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Fallback: create minimal PDF
        return create_fallback_pdf(consultation_data, user_data)

def create_fallback_pdf(consultation_data, user_data):
    """Create fallback PDF if main generation fails"""
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Wellness Coach Consultation', 0, 1, 'C')
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Reference: {consultation_data.get('reference', 'N/A')}", 0, 1)
    pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", 0, 1)
    pdf.ln(10)
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Consultation Details', 0, 1)
    pdf.set_font('Arial', '', 11)
    
    pdf.cell(0, 8, f"Name: {user_data.get('name', 'N/A')}", 0, 1)
    pdf.cell(0, 8, f"Email: {user_data.get('email', 'N/A')}", 0, 1)
    pdf.cell(0, 8, f"Program: {consultation_data.get('program', 'General Inquiry')}", 0, 1)
    pdf.cell(0, 8, f"Status: {consultation_data.get('status', 'pending').title()}", 0, 1)
    pdf.ln(10)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Message:', 0, 1)
    pdf.set_font('Arial', '', 11)
    
    message = consultation_data.get('message', 'No message')
    lines = message.split('\n')
    for line in lines[:15]:  # Limit to 15 lines
        pdf.cell(0, 6, line, 0, 1)
    
    return pdf.output(dest='S')