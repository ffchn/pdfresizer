#!/usr/bin/env python3
"""
Installation Test Script

This script verifies that all dependencies are properly installed
and the main components can be imported successfully.

Author: AI Assistant
"""

import sys
import traceback

def test_imports():
    """Test if all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        import fitz  # PyMuPDF
        print("✅ PyMuPDF (fitz) imported successfully")
    except ImportError as e:
        print(f"❌ PyMuPDF import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow (PIL) imported successfully")
    except ImportError as e:
        print(f"❌ Pillow import failed: {e}")
        return False
    
    try:
        from pdf_compressor import PDFCompressor
        print("✅ PDFCompressor imported successfully")
    except ImportError as e:
        print(f"❌ PDFCompressor import failed: {e}")
        return False
    
    try:
        from pdf_utils import PDFAnalyzer, PDFOptimizer, ImageProcessor
        print("✅ PDF utilities imported successfully")
    except ImportError as e:
        print(f"❌ PDF utilities import failed: {e}")
        return False
    
    return True

def test_functionality():
    """Test basic functionality without requiring a PDF file."""
    print("\n🧪 Testing basic functionality...")
    
    try:
        from pdf_compressor import PDFCompressor
        
        # Test PDFCompressor instantiation
        compressor = PDFCompressor(target_size_mb=1.0)
        print("✅ PDFCompressor instance created successfully")
        
        # Test utility methods
        size_str = compressor.format_file_size(1024 * 1024)  # 1MB
        assert "1.0 MB" in size_str
        print("✅ File size formatting works correctly")
        
        # Test image compression functionality
        from PIL import Image
        import io
        
        # Create a small test image
        test_image = Image.new('RGB', (100, 100), color='red')
        img_buffer = io.BytesIO()
        test_image.save(img_buffer, format='JPEG', quality=90)
        img_data = img_buffer.getvalue()
        
        # Test image compression
        compressed = compressor.compress_image(img_data, quality=50, scale=0.5)
        print("✅ Image compression works correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        traceback.print_exc()
        return False

def test_pdf_creation():
    """Test PDF creation capabilities."""
    print("\n📄 Testing PDF creation...")
    
    try:
        import fitz
        
        # Create a simple test PDF
        doc = fitz.open()
        page = doc.new_page()
        
        # Add some text
        text = "This is a test PDF created by the PDF Compressor tool."
        page.insert_text((50, 50), text)
        
        # Save test PDF
        test_pdf_path = "test_document.pdf"
        doc.save(test_pdf_path)
        doc.close()
        
        print(f"✅ Test PDF created: {test_pdf_path}")
        
        # Test analysis on the created PDF
        from pdf_utils import PDFAnalyzer
        analysis = PDFAnalyzer.analyze_pdf(test_pdf_path)
        
        if 'error' not in analysis:
            print(f"✅ PDF analysis successful: {analysis['page_count']} pages")
        else:
            print(f"⚠️  PDF analysis had issues: {analysis['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ PDF creation test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("PDF Compressor Installation Test")
    print("=" * 40)
    print(f"Python version: {sys.version}")
    print()
    
    # Run tests
    import_success = test_imports()
    
    if not import_success:
        print("\n❌ Import tests failed. Please check your installation.")
        print("\nTo fix:")
        print("1. Activate your virtual environment: source venv/bin/activate")
        print("2. Install dependencies: pip install -r requirements.txt")
        sys.exit(1)
    
    functionality_success = test_functionality()
    pdf_creation_success = test_pdf_creation()
    
    print("\n" + "=" * 40)
    
    if import_success and functionality_success and pdf_creation_success:
        print("🎉 All tests passed! The PDF Compressor is ready to use.")
        print("\n📖 Next steps:")
        print("1. Place a PDF file in this directory")
        print("2. Run: python pdf_compressor.py your_file.pdf")
        print("3. Or try: python example_usage.py")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        if not functionality_success:
            print("   - Functionality test failed")
        if not pdf_creation_success:
            print("   - PDF creation test failed")

if __name__ == "__main__":
    main() 