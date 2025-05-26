#!/usr/bin/env python3
"""
PDF Compressor Script

This script compresses PDF files by reducing DPI and dimensions to achieve
a target file size of 1MB or less.

Author: AI Assistant
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Tuple, Optional

import fitz  # PyMuPDF
from PIL import Image
import io


class PDFCompressor:
    """
    A class to compress PDF files by reducing DPI and dimensions.
    """
    
    def __init__(self, target_size_mb: float = 1.0):
        """
        Initialize the PDF compressor.
        
        Args:
            target_size_mb: Target file size in megabytes (default: 1.0)
        """
        self.target_size_bytes = target_size_mb * 1024 * 1024
        self.quality_levels = [95, 85, 75, 65, 50, 40, 30, 20]
        self.scale_factors = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4]
        
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes."""
        return os.path.getsize(file_path)
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def compress_image(self, image_data: bytes, quality: int = 85, scale: float = 1.0) -> bytes:
        """
        Compress an image by reducing quality and scale.
        
        Args:
            image_data: Original image data
            quality: JPEG quality (1-100)
            scale: Scale factor (0.1-1.0)
            
        Returns:
            Compressed image data
        """
        try:
            # Open image from bytes
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary (for JPEG compatibility)
            if image.mode in ('RGBA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Scale the image
            if scale < 1.0:
                new_size = (int(image.width * scale), int(image.height * scale))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Compress and save to bytes
            output_buffer = io.BytesIO()
            image.save(output_buffer, format='JPEG', quality=quality, optimize=True)
            
            return output_buffer.getvalue()
            
        except Exception as e:
            print(f"Warning: Could not compress image: {e}")
            return image_data
    
    def compress_pdf_images(self, input_path: str, output_path: str, quality: int = 85, scale: float = 1.0) -> bool:
        """
        Compress PDF by reducing image quality and scale using page re-rendering.
        
        Args:
            input_path: Path to input PDF
            output_path: Path to output PDF
            quality: Image quality (1-100)
            scale: Scale factor (0.1-1.0)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Open the PDF
            pdf_document = fitz.open(input_path)
            new_pdf = fitz.open()
            
            # Calculate matrix for scaling
            zoom = scale
            matrix = fitz.Matrix(zoom, zoom)
            
            # Process each page
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                
                # Check if page has images
                image_list = page.get_images()
                
                if image_list:
                    # Render page as image with scaling
                    pix = page.get_pixmap(matrix=matrix)
                    
                    # Convert to JPEG with quality control using Pillow
                    img_data = pix.tobytes("ppm")  # Get PPM format
                    
                    # Use Pillow to convert and compress
                    pil_image = Image.open(io.BytesIO(img_data))
                    if pil_image.mode != 'RGB':
                        pil_image = pil_image.convert('RGB')
                    
                    # Compress to JPEG
                    output_buffer = io.BytesIO()
                    pil_image.save(output_buffer, format='JPEG', quality=quality, optimize=True)
                    img_data = output_buffer.getvalue()
                    
                    # Create new page with the compressed image
                    new_page = new_pdf.new_page(width=page.rect.width * scale, 
                                              height=page.rect.height * scale)
                    
                    # Insert the image
                    img_rect = fitz.Rect(0, 0, new_page.rect.width, new_page.rect.height)
                    new_page.insert_image(img_rect, stream=img_data)
                else:
                    # Copy page as-is if no images (preserve text/vector graphics)
                    new_page = new_pdf.new_page(width=page.rect.width * scale, 
                                              height=page.rect.height * scale)
                    new_page.show_pdf_page(new_page.rect, pdf_document, page_num)
            
            # Save the compressed PDF
            new_pdf.save(output_path, garbage=4, deflate=True, clean=True)
            new_pdf.close()
            pdf_document.close()
            
            return True
            
        except Exception as e:
            print(f"Error compressing PDF: {e}")
            return False
    
    def compress_pdf_rendering(self, input_path: str, output_path: str, dpi: int = 150, scale: float = 1.0) -> bool:
        """
        Compress PDF by re-rendering pages at lower DPI.
        
        Args:
            input_path: Path to input PDF
            output_path: Path to output PDF
            dpi: Target DPI for rendering
            scale: Scale factor for final output
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Open the PDF
            pdf_document = fitz.open(input_path)
            new_pdf = fitz.open()
            
            # Calculate matrix for DPI scaling
            zoom = dpi / 72.0  # 72 is default DPI
            matrix = fitz.Matrix(zoom * scale, zoom * scale)
            
            # Process each page
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                
                # Render page as image
                pix = page.get_pixmap(matrix=matrix)
                
                # Convert pixmap to JPEG with quality control using Pillow
                img_data = pix.tobytes("ppm")  # Get PPM format first
                
                # Use Pillow to convert and compress
                pil_image = Image.open(io.BytesIO(img_data))
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                
                # Compress to JPEG
                output_buffer = io.BytesIO()
                pil_image.save(output_buffer, format='JPEG', quality=85, optimize=True)
                img_data = output_buffer.getvalue()
                
                # Create new page with the image
                new_page = new_pdf.new_page(width=page.rect.width * scale, 
                                          height=page.rect.height * scale)
                
                # Insert the image
                img_rect = fitz.Rect(0, 0, new_page.rect.width, new_page.rect.height)
                new_page.insert_image(img_rect, stream=img_data)
            
            # Save the new PDF
            new_pdf.save(output_path, garbage=4, deflate=True, clean=True)
            new_pdf.close()
            pdf_document.close()
            
            return True
            
        except Exception as e:
            print(f"Error in PDF rendering compression: {e}")
            return False
    
    def compress_pdf(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        Main method to compress PDF to target size.
        
        Args:
            input_path: Path to input PDF file
            output_path: Path to output PDF file (optional)
            
        Returns:
            Path to compressed PDF file
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Generate output path if not provided
        if output_path is None:
            input_file = Path(input_path)
            output_path = str(input_file.parent / f"{input_file.stem}_compressed{input_file.suffix}")
        
        original_size = self.get_file_size(input_path)
        print(f"Original file size: {self.format_file_size(original_size)}")
        print(f"Target size: {self.format_file_size(int(self.target_size_bytes))}")
        
        # If file is already smaller than target, just copy it
        if original_size <= self.target_size_bytes:
            import shutil
            shutil.copy2(input_path, output_path)
            print("File is already within target size!")
            return output_path
        
        # Try different compression strategies
        best_result = None
        best_size = float('inf')
        
        # Strategy 1: Image compression with various quality levels
        print("\nTrying image compression strategy...")
        for quality in self.quality_levels:
            for scale in self.scale_factors:
                temp_output = f"{output_path}.temp"
                
                if self.compress_pdf_images(input_path, temp_output, quality, scale):
                    current_size = self.get_file_size(temp_output)
                    
                    print(f"  Quality {quality}, Scale {scale:.1f}: {self.format_file_size(current_size)}")
                    
                    if current_size <= self.target_size_bytes:
                        if current_size < best_size or best_result is None:
                            best_result = temp_output
                            best_size = current_size
                        break
                
                # Clean up temp file if not the best result
                if os.path.exists(temp_output) and temp_output != best_result:
                    os.remove(temp_output)
            
            if best_result:
                break
        
        # Strategy 2: Re-rendering at lower DPI if image compression wasn't enough
        if not best_result:
            print("\nTrying DPI reduction strategy...")
            dpi_levels = [150, 120, 100, 80, 60, 50]
            
            for dpi in dpi_levels:
                for scale in self.scale_factors:
                    temp_output = f"{output_path}.temp2"
                    
                    if self.compress_pdf_rendering(input_path, temp_output, dpi, scale):
                        current_size = self.get_file_size(temp_output)
                        
                        print(f"  DPI {dpi}, Scale {scale:.1f}: {self.format_file_size(current_size)}")
                        
                        if current_size <= self.target_size_bytes:
                            if current_size < best_size or best_result is None:
                                best_result = temp_output
                                best_size = current_size
                            break
                    
                    # Clean up temp file if not the best result
                    if os.path.exists(temp_output) and temp_output != best_result:
                        os.remove(temp_output)
                
                if best_result:
                    break
        
        # Finalize the result
        if best_result:
            # Move the best result to final output path
            if best_result != output_path:
                import shutil
                shutil.move(best_result, output_path)
            
            final_size = self.get_file_size(output_path)
            compression_ratio = (1 - final_size / original_size) * 100
            
            print(f"\n✅ Compression successful!")
            print(f"Final size: {self.format_file_size(final_size)}")
            print(f"Compression ratio: {compression_ratio:.1f}%")
            
            return output_path
        else:
            raise Exception("Could not compress PDF to target size. Try a larger target size.")


def main():
    """Main function to handle command line arguments and execute compression."""
    parser = argparse.ArgumentParser(description="Compress PDF files to target size")
    parser.add_argument("input_file", help="Path to input PDF file")
    parser.add_argument("-o", "--output", help="Path to output PDF file")
    parser.add_argument("-s", "--size", type=float, default=1.0, 
                       help="Target size in MB (default: 1.0)")
    
    args = parser.parse_args()
    
    try:
        compressor = PDFCompressor(target_size_mb=args.size)
        output_file = compressor.compress_pdf(args.input_file, args.output)
        print(f"\nCompressed PDF saved as: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 