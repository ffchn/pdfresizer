#!/usr/bin/env python3
"""
Example Usage Script for PDF Compressor

This script demonstrates how to use the PDF compression functionality
both as a standalone script and as a Python module.

Author: AI Assistant
"""

from pdf_compressor import PDFCompressor
from pdf_utils import PDFAnalyzer, PDFOptimizer
import os


def example_basic_compression():
    """Example of basic PDF compression usage."""
    print("=== Basic PDF Compression Example ===")
    
    # Replace with your actual PDF file path
    input_file = "sample.pdf"
    
    if not os.path.exists(input_file):
        print(f"Please place a PDF file named '{input_file}' in the current directory")
        return
    
    # Create compressor instance
    compressor = PDFCompressor(target_size_mb=1.0)
    
    try:
        # Compress the PDF
        output_file = compressor.compress_pdf(input_file)
        print(f"✅ Successfully compressed PDF: {output_file}")
        
        # Show before/after sizes
        original_size = compressor.get_file_size(input_file)
        compressed_size = compressor.get_file_size(output_file)
        
        print(f"Original size: {compressor.format_file_size(original_size)}")
        print(f"Compressed size: {compressor.format_file_size(compressed_size)}")
        print(f"Space saved: {compressor.format_file_size(original_size - compressed_size)}")
        
    except Exception as e:
        print(f"❌ Compression failed: {e}")


def example_advanced_compression():
    """Example of advanced compression with analysis."""
    print("\n=== Advanced PDF Compression Example ===")
    
    input_file = "sample.pdf"
    
    if not os.path.exists(input_file):
        print(f"Please place a PDF file named '{input_file}' in the current directory")
        return
    
    # Analyze the PDF first
    print("📊 Analyzing PDF structure...")
    analysis = PDFAnalyzer.analyze_pdf(input_file)
    
    if 'error' not in analysis:
        print(f"Pages: {analysis['page_count']}")
        print(f"Total images: {analysis['total_images']}")
        print(f"Average DPI: {analysis['average_dpi']:.1f}")
        print(f"Content type: {'Image-heavy' if analysis['image_heavy'] else 'Text-heavy' if analysis['text_heavy'] else 'Mixed'}")
        
        # Get recommended strategy
        strategy = PDFAnalyzer.recommend_strategy(analysis)
        print(f"Recommended strategy: {strategy}")
    
    # Apply different compression strategies
    compressor = PDFCompressor(target_size_mb=1.0)
    
    try:
        # Try basic compression first
        basic_output = "sample_basic_compressed.pdf"
        compressor.compress_pdf(input_file, basic_output)
        
        # Try with metadata removal
        metadata_output = "sample_no_metadata.pdf"
        PDFOptimizer.remove_metadata(input_file, metadata_output)
        
        # Try flattening for maximum compression
        flattened_output = "sample_flattened.pdf"
        PDFOptimizer.flatten_pdf(input_file, flattened_output, dpi=120)
        
        # Compare results
        print("\n📋 Compression Results:")
        original_size = os.path.getsize(input_file)
        
        results = [
            ("Original", input_file, original_size),
            ("Basic compression", basic_output, os.path.getsize(basic_output) if os.path.exists(basic_output) else 0),
            ("No metadata", metadata_output, os.path.getsize(metadata_output) if os.path.exists(metadata_output) else 0),
            ("Flattened", flattened_output, os.path.getsize(flattened_output) if os.path.exists(flattened_output) else 0)
        ]
        
        for name, path, size in results:
            if size > 0:
                size_str = PDFCompressor.format_file_size(None, size)
                reduction = ((original_size - size) / original_size * 100) if size < original_size else 0
                print(f"  {name}: {size_str} ({reduction:.1f}% reduction)")
        
    except Exception as e:
        print(f"❌ Advanced compression failed: {e}")


def example_custom_settings():
    """Example with custom compression settings."""
    print("\n=== Custom Settings Example ===")
    
    input_file = "sample.pdf"
    
    if not os.path.exists(input_file):
        print(f"Please place a PDF file named '{input_file}' in the current directory")
        return
    
    # Custom target sizes
    target_sizes = [0.5, 1.0, 2.0]  # MB
    
    for target_mb in target_sizes:
        print(f"\n🎯 Compressing to {target_mb} MB...")
        
        compressor = PDFCompressor(target_size_mb=target_mb)
        output_file = f"sample_compressed_{target_mb}mb.pdf"
        
        try:
            result = compressor.compress_pdf(input_file, output_file)
            final_size = compressor.get_file_size(result)
            print(f"   Result: {compressor.format_file_size(final_size)}")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")


def main():
    """Run all examples."""
    print("PDF Compressor Examples")
    print("=" * 50)
    
    # Check if we have a sample PDF
    sample_files = ["sample.pdf", "test.pdf", "document.pdf"]
    found_file = None
    
    for filename in sample_files:
        if os.path.exists(filename):
            found_file = filename
            break
    
    if not found_file:
        print("ℹ️  No sample PDF found. Please add a PDF file to test compression.")
        print("   Supported filenames: sample.pdf, test.pdf, document.pdf")
        print("\n📝 You can also use the script directly:")
        print("   python pdf_compressor.py your_file.pdf")
        print("   python pdf_compressor.py your_file.pdf -o compressed.pdf -s 1.5")
        return
    
    # Rename the found file to sample.pdf for consistency
    if found_file != "sample.pdf":
        import shutil
        shutil.copy2(found_file, "sample.pdf")
        print(f"📄 Using {found_file} as sample.pdf")
    
    # Run examples
    try:
        example_basic_compression()
        example_advanced_compression()
        example_custom_settings()
        
        print("\n✅ All examples completed!")
        print("\n🔧 Command Line Usage:")
        print("   python pdf_compressor.py input.pdf")
        print("   python pdf_compressor.py input.pdf -o output.pdf")
        print("   python pdf_compressor.py input.pdf -s 0.5  # Target 0.5 MB")
        
    except KeyboardInterrupt:
        print("\n⏹️  Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")


if __name__ == "__main__":
    main() 