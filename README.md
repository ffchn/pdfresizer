# PDF Compressor

A powerful Python tool to compress PDF files by reducing DPI and dimensions to achieve target file sizes (default: 1MB).

## Features

- **Smart Compression**: Automatically adjusts image quality and dimensions to reach target file size
- **Multiple Strategies**: Uses different compression approaches based on PDF content
- **DPI Reduction**: Reduces image DPI while maintaining visual quality
- **Dimension Scaling**: Scales images to reduce file size
- **Content Analysis**: Analyzes PDF structure to choose optimal compression strategy
- **Command Line Interface**: Easy-to-use CLI with customizable options
- **Python Module**: Can be imported and used in other Python projects

## Compression Strategies

The tool implements multiple compression approaches:

1. **Image Compression**: Reduces quality and scale of embedded images
2. **DPI Reduction**: Re-renders pages at lower DPI
3. **Metadata Removal**: Strips unnecessary metadata
4. **Flattening**: Converts entire pages to optimized images (aggressive)

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Quick Setup

1. **Create a virtual environment** (recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install PyMuPDF>=1.23.0 Pillow>=10.0.0
```

### Alternative Installation (with --user flag)

If you prefer not to use a virtual environment:

```bash
pip install --user PyMuPDF>=1.23.0 Pillow>=10.0.0
```

## Usage

### Command Line

**Note**: If using a virtual environment, activate it first:

```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Basic usage (target 1MB):

```bash
python pdf_compressor.py input.pdf
```

Specify output file:

```bash
python pdf_compressor.py input.pdf -o compressed.pdf
```

Custom target size:

```bash
python pdf_compressor.py input.pdf -s 0.5    # Target 0.5 MB
python pdf_compressor.py input.pdf -s 2.0    # Target 2.0 MB
```

### Python Module

```python
from pdf_compressor import PDFCompressor
from pdf_utils import PDFAnalyzer, PDFOptimizer

# Basic compression
compressor = PDFCompressor(target_size_mb=1.0)
output_file = compressor.compress_pdf("input.pdf")
print(f"Compressed: {output_file}")

# Advanced usage with analysis
analysis = PDFAnalyzer.analyze_pdf("input.pdf")
print(f"Pages: {analysis['page_count']}")
print(f"Images: {analysis['total_images']}")

# Apply specific optimizations
PDFOptimizer.remove_metadata("input.pdf", "no_metadata.pdf")
PDFOptimizer.flatten_pdf("input.pdf", "flattened.pdf", dpi=120)
```

## Examples

Run the example script to see different compression strategies in action:

```bash
# Activate virtual environment first (if using one)
source venv/bin/activate

# Run examples
python example_usage.py
```

Make sure to place a PDF file named `sample.pdf`, `test.pdf`, or `document.pdf` in the directory first.

## File Structure

```
├── pdf_compressor.py      # Main compression script
├── pdf_utils.py          # Utility functions and classes
├── example_usage.py      # Usage examples
├── requirements.txt      # Python dependencies
├── venv/                 # Virtual environment (created after setup)
└── README.md            # This file
```

## How It Works

### Compression Process

1. **Analysis**: The tool first analyzes the PDF to understand its structure:

   - Page count and dimensions
   - Number and size of embedded images
   - Content type (text-heavy, image-heavy, or mixed)
   - Estimated DPI of images

2. **Strategy Selection**: Based on the analysis, it chooses the optimal approach:

   - Image-heavy PDFs: Focus on image compression
   - Text-heavy PDFs: Use DPI reduction
   - Mixed content: Balanced approach

3. **Iterative Compression**: The tool tries different quality and scale settings:

   - Starts with high quality (95%) and gradually reduces
   - Applies scaling factors from 100% down to 40%
   - Stops when target size is achieved

4. **Fallback Methods**: If initial methods don't work:
   - Tries DPI reduction (from 150 to 50 DPI)
   - Uses more aggressive scaling
   - Falls back to page flattening if necessary

### Quality Preservation

The tool is designed to maintain visual quality while achieving compression:

- Uses high-quality JPEG compression with optimization
- Employs Lanczos resampling for image scaling
- Preserves text readability by avoiding over-compression
- Maintains aspect ratios during scaling

## Configuration

### Compression Levels

You can modify the compression parameters in `pdf_compressor.py`:

```python
self.quality_levels = [95, 85, 75, 65, 50, 40, 30, 20]  # JPEG quality levels
self.scale_factors = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4]  # Scaling factors
```

### DPI Settings

Adjust DPI levels for page rendering:

```python
dpi_levels = [150, 120, 100, 80, 60, 50]  # DPI options for rendering
```

## Troubleshooting

### Common Issues

1. **"Could not compress PDF to target size"**

   - Try a larger target size (e.g., 1.5 MB instead of 1.0 MB)
   - Use the flattening method for aggressive compression
   - Check if the PDF contains mostly vector graphics (harder to compress)

2. **Import errors**

   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version (3.7+ required)

3. **Poor quality output**
   - Increase target file size
   - Modify quality levels in the configuration
   - Use less aggressive scaling factors

### Performance Tips

- **Large PDFs**: The tool processes page by page, so large documents may take time
- **Image-heavy PDFs**: These compress better than text-only documents
- **Vector graphics**: PDFs with vector graphics may not compress as much

## Advanced Usage

### Custom Compression Strategy

```python
from pdf_compressor import PDFCompressor

class CustomCompressor(PDFCompressor):
    def __init__(self, target_size_mb=1.0):
        super().__init__(target_size_mb)
        # Custom quality levels for specific needs
        self.quality_levels = [90, 70, 50, 30]  # Fewer, larger steps
        self.scale_factors = [1.0, 0.8, 0.6, 0.4]  # More aggressive scaling

compressor = CustomCompressor(target_size_mb=0.8)
result = compressor.compress_pdf("large_file.pdf")
```

### Batch Processing

```python
import os
from pdf_compressor import PDFCompressor

def compress_directory(input_dir, output_dir, target_mb=1.0):
    """Compress all PDFs in a directory."""
    compressor = PDFCompressor(target_size_mb=target_mb)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.pdf'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"compressed_{filename}")

            try:
                compressor.compress_pdf(input_path, output_path)
                print(f"✅ Compressed: {filename}")
            except Exception as e:
                print(f"❌ Failed {filename}: {e}")

# Usage
compress_directory("input_pdfs/", "output_pdfs/", target_mb=1.0)
```

## Contributing

Feel free to contribute improvements:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source. Use it freely for personal or commercial projects.

## Support

If you encounter issues or have questions:

1. Check the troubleshooting section above
2. Review the example usage in `example_usage.py`
3. Examine the code comments for implementation details

---

**Note**: This tool works best with PDFs containing images. Text-only PDFs with vector graphics may have limited compression potential.
