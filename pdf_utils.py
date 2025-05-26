"""
PDF Utilities Module

This module contains utility functions for PDF manipulation and compression.
Provides additional compression strategies beyond the main compressor.

Author: AI Assistant
"""

import os
import fitz  # PyMuPDF
from typing import List, Tuple, Optional
from PIL import Image
import io


class PDFAnalyzer:
    """
    Utility class to analyze PDF content and structure.
    """
    
    @staticmethod
    def analyze_pdf(file_path: str) -> dict:
        """
        Analyze PDF structure and content to determine best compression strategy.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with analysis results
        """
        try:
            doc = fitz.open(file_path)
            analysis = {
                'page_count': doc.page_count,
                'total_images': 0,
                'image_sizes': [],
                'text_heavy': False,
                'image_heavy': False,
                'average_dpi': 0,
                'file_size': os.path.getsize(file_path)
            }
            
            total_image_area = 0
            total_page_area = 0
            total_dpi = 0
            dpi_count = 0
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                page_area = page.rect.width * page.rect.height
                total_page_area += page_area
                
                # Count images and their properties
                images = page.get_images()
                analysis['total_images'] += len(images)
                
                for img in images:
                    try:
                        # Extract image information
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        
                        # Calculate image size and DPI
                        image_bytes = len(base_image["image"])
                        analysis['image_sizes'].append(image_bytes)
                        
                        # Estimate DPI (simplified calculation)
                        img_width = base_image.get("width", 0)
                        img_height = base_image.get("height", 0)
                        
                        if img_width > 0 and img_height > 0:
                            # Estimate based on image dimensions
                            estimated_dpi = max(img_width, img_height) / 8.5  # Assume 8.5" max dimension
                            total_dpi += estimated_dpi
                            dpi_count += 1
                            
                            image_area = img_width * img_height
                            total_image_area += image_area
                            
                    except Exception:
                        continue
            
            # Determine content characteristics
            if total_image_area > 0:
                analysis['average_dpi'] = total_dpi / dpi_count if dpi_count > 0 else 0
                image_ratio = total_image_area / (total_page_area * doc.page_count) if total_page_area > 0 else 0
                analysis['image_heavy'] = image_ratio > 0.3  # More than 30% images
                analysis['text_heavy'] = image_ratio < 0.1   # Less than 10% images
            
            doc.close()
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def recommend_strategy(analysis: dict) -> str:
        """
        Recommend best compression strategy based on PDF analysis.
        
        Args:
            analysis: Result from analyze_pdf
            
        Returns:
            Recommended strategy string
        """
        if 'error' in analysis:
            return "basic"
        
        if analysis['image_heavy']:
            if analysis['average_dpi'] > 200:
                return "aggressive_image_compression"
            else:
                return "moderate_image_compression"
        elif analysis['text_heavy']:
            return "dpi_reduction"
        else:
            return "balanced"


class PDFOptimizer:
    """
    Advanced PDF optimization utilities.
    """
    
    @staticmethod
    def remove_metadata(input_path: str, output_path: str) -> bool:
        """
        Remove metadata to reduce file size.
        
        Args:
            input_path: Path to input PDF
            output_path: Path to output PDF
            
        Returns:
            True if successful
        """
        try:
            doc = fitz.open(input_path)
            
            # Clear metadata
            doc.set_metadata({})
            
            # Save without metadata
            doc.save(output_path, garbage=4, deflate=True, clean=True)
            doc.close()
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def remove_annotations(input_path: str, output_path: str) -> bool:
        """
        Remove annotations and interactive elements.
        
        Args:
            input_path: Path to input PDF
            output_path: Path to output PDF
            
        Returns:
            True if successful
        """
        try:
            doc = fitz.open(input_path)
            
            for page in doc:
                # Remove all annotations
                annots = page.annots()
                for annot in annots:
                    page.delete_annot(annot)
            
            doc.save(output_path, garbage=4, deflate=True, clean=True)
            doc.close()
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def flatten_pdf(input_path: str, output_path: str, dpi: int = 150) -> bool:
        """
        Flatten PDF by converting all content to images (aggressive compression).
        
        Args:
            input_path: Path to input PDF
            output_path: Path to output PDF
            dpi: Target DPI for flattening
            
        Returns:
            True if successful
        """
        try:
            doc = fitz.open(input_path)
            new_doc = fitz.open()
            
            zoom = dpi / 72.0
            matrix = fitz.Matrix(zoom, zoom)
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                
                # Render page as pixmap
                pix = page.get_pixmap(matrix=matrix)
                
                # Convert pixmap to JPEG using Pillow for quality control
                img_data = pix.tobytes("ppm")  # Get PPM format
                
                # Use Pillow to convert and compress
                pil_image = Image.open(io.BytesIO(img_data))
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                
                # Compress to JPEG
                output_buffer = io.BytesIO()
                pil_image.save(output_buffer, format='JPEG', quality=85, optimize=True)
                img_data = output_buffer.getvalue()
                
                # Create new page
                new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
                img_rect = new_page.rect
                new_page.insert_image(img_rect, stream=img_data)
            
            new_doc.save(output_path, garbage=4, deflate=True, clean=True)
            new_doc.close()
            doc.close()
            
            return True
        except Exception:
            return False


class ImageProcessor:
    """
    Specialized image processing for PDF content.
    """
    
    @staticmethod
    def optimize_image_for_pdf(image_data: bytes, target_size: int, 
                             min_quality: int = 20) -> bytes:
        """
        Optimize image specifically for PDF inclusion.
        
        Args:
            image_data: Original image bytes
            target_size: Target size in bytes
            min_quality: Minimum acceptable quality
            
        Returns:
            Optimized image bytes
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Try different quality levels
            for quality in range(95, min_quality - 1, -5):
                output = io.BytesIO()
                image.save(output, format='JPEG', quality=quality, optimize=True)
                
                if len(output.getvalue()) <= target_size:
                    return output.getvalue()
            
            # If still too large, try resizing
            scale_factors = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4]
            
            for scale in scale_factors:
                new_size = (int(image.width * scale), int(image.height * scale))
                resized = image.resize(new_size, Image.Resampling.LANCZOS)
                
                for quality in range(85, min_quality - 1, -5):
                    output = io.BytesIO()
                    resized.save(output, format='JPEG', quality=quality, optimize=True)
                    
                    if len(output.getvalue()) <= target_size:
                        return output.getvalue()
            
            # Fallback: return heavily compressed version
            output = io.BytesIO()
            final_size = (int(image.width * 0.3), int(image.height * 0.3))
            final_image = image.resize(final_size, Image.Resampling.LANCZOS)
            final_image.save(output, format='JPEG', quality=min_quality, optimize=True)
            
            return output.getvalue()
            
        except Exception:
            return image_data
    
    @staticmethod
    def calculate_optimal_dpi(original_size: int, target_size: int, 
                            current_dpi: int = 300) -> int:
        """
        Calculate optimal DPI to achieve target file size.
        
        Args:
            original_size: Original file size in bytes
            target_size: Target file size in bytes
            current_dpi: Current DPI estimate
            
        Returns:
            Recommended DPI
        """
        # Simple ratio-based calculation
        size_ratio = target_size / original_size
        
        # DPI reduction roughly proportional to square root of size ratio
        # (since DPI affects both width and height)
        dpi_ratio = size_ratio ** 0.5
        
        optimal_dpi = int(current_dpi * dpi_ratio)
        
        # Ensure reasonable bounds
        return max(50, min(optimal_dpi, 300)) 