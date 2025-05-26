#!/usr/bin/env python3
"""
Create Test PDF Script

This script creates a larger PDF with images to test compression capabilities.

Author: AI Assistant
"""

import fitz
from PIL import Image, ImageDraw, ImageFont
import io
import os


def create_large_test_pdf(output_path: str = "large_test.pdf"):
    """Create a test PDF with multiple pages and images."""
    
    doc = fitz.open()
    
    # Create 5 pages with different content
    for page_num in range(5):
        page = doc.new_page()
        
        # Add title text
        title = f"Test Page {page_num + 1}"
        page.insert_text((50, 50), title, fontsize=20)
        
        # Add description
        description = f"This is page {page_num + 1} of the test document. " * 5
        page.insert_text((50, 100), description, fontsize=12)
        
        # Create and insert a test image
        test_image = create_test_image(page_num)
        
        # Convert PIL image to bytes
        img_buffer = io.BytesIO()
        test_image.save(img_buffer, format='PNG')
        img_data = img_buffer.getvalue()
        
        # Insert image on page
        img_rect = fitz.Rect(50, 150, 300, 400)
        page.insert_image(img_rect, stream=img_data)
        
        # Add more text below image
        footer_text = f"Page {page_num + 1} footer content. " * 10
        page.insert_text((50, 450), footer_text, fontsize=10)
    
    # Save the PDF
    doc.save(output_path)
    doc.close()
    
    print(f"Created test PDF: {output_path}")
    print(f"File size: {os.path.getsize(output_path)} bytes")
    
    return output_path


def create_test_image(page_num: int) -> Image.Image:
    """Create a test image for the PDF."""
    
    # Create a colorful image
    width, height = 400, 300
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Draw colorful rectangles
    colors = ['red', 'green', 'blue', 'yellow', 'purple']
    color = colors[page_num % len(colors)]
    
    # Draw gradient-like rectangles
    for i in range(0, width, 20):
        for j in range(0, height, 20):
            # Create varying shades
            shade = (i + j) % 255
            rect_color = (shade, shade // 2, (255 - shade) % 255)
            draw.rectangle([i, j, i + 19, j + 19], fill=rect_color)
    
    # Draw some text on the image
    try:
        # Try to use a default font, fall back to basic if not available
        font = ImageFont.load_default()
    except:
        font = None
    
    draw.text((50, 50), f"Test Image {page_num + 1}", fill='black', font=font)
    draw.text((50, 100), "This is a test image with various colors", fill='white', font=font)
    
    # Draw some shapes
    draw.ellipse([200, 150, 350, 250], fill=color, outline='black', width=3)
    draw.rectangle([50, 200, 150, 280], fill='orange', outline='black', width=2)
    
    return image


def main():
    """Create test PDFs of different sizes."""
    
    print("Creating test PDFs...")
    
    # Create a large test PDF
    large_pdf = create_large_test_pdf("large_test.pdf")
    
    # Create a smaller test PDF
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Small Test PDF", fontsize=16)
    page.insert_text((50, 100), "This is a smaller test document for compression testing.", fontsize=12)
    
    # Add a simple image
    simple_image = Image.new('RGB', (200, 150), color='lightblue')
    draw = ImageDraw.Draw(simple_image)
    draw.rectangle([20, 20, 180, 130], fill='navy', outline='black')
    draw.text((50, 75), "Test", fill='white')
    
    img_buffer = io.BytesIO()
    simple_image.save(img_buffer, format='PNG')
    img_data = img_buffer.getvalue()
    
    img_rect = fitz.Rect(50, 150, 250, 300)
    page.insert_image(img_rect, stream=img_data)
    
    small_pdf_path = "small_test.pdf"
    doc.save(small_pdf_path)
    doc.close()
    
    print(f"Created small test PDF: {small_pdf_path}")
    print(f"File size: {os.path.getsize(small_pdf_path)} bytes")
    
    print("\n✅ Test PDFs created successfully!")
    print("\n🧪 You can now test compression with:")
    print(f"   python pdf_compressor.py {large_pdf} -s 1.0")
    print(f"   python pdf_compressor.py {small_pdf_path} -s 0.1")


if __name__ == "__main__":
    main() 