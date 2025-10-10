#!/usr/bin/env python3
"""
Simple script to create a test PDF file for testing community message PDF uploads
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

def create_test_pdf():
    """Create a simple test PDF file"""
    filename = "test_document.pdf"
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    # Create a simple PDF
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    
    # Add some content
    c.setFont("Helvetica", 16)
    c.drawString(100, height - 100, "Test Document for Community Messages")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 150, "This is a test PDF file created to demonstrate")
    c.drawString(100, height - 170, "the PDF upload functionality in the community messaging system.")
    
    c.drawString(100, height - 220, "Features tested:")
    c.drawString(120, height - 240, "• PDF file upload")
    c.drawString(120, height - 260, "• File size display")
    c.drawString(120, height - 280, "• PDF preview functionality")
    c.drawString(120, height - 300, "• Download/view functionality")
    
    c.save()
    print(f"Test PDF created: {filepath}")
    return filepath

if __name__ == "__main__":
    # Try to create the PDF
    try:
        create_test_pdf()
    except ImportError:
        print("reportlab not installed. Creating a simple text file instead...")
        # Create a simple text file as alternative
        with open("test_document.txt", "w") as f:
            f.write("Test Document for Community Messages\n")
            f.write("=====================================\n\n")
            f.write("This is a test file created to demonstrate\n")
            f.write("the file upload functionality in the community messaging system.\n\n")
            f.write("Features tested:\n")
            f.write("• File upload\n")
            f.write("• File size display\n")
            f.write("• File preview functionality\n")
            f.write("• Download/view functionality\n")
        print("Test text file created: test_document.txt")