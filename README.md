# OCR Application

A powerful desktop OCR application built with PyQt6 that provides advanced text extraction capabilities from images with real-time preview and extensive customization options.

![Application Preview](![Screenshot (9)](https://github.com/user-attachments/assets/be9e0f3c-22e1-48a0-a362-561e0cf4e2b1)
)

## Features

- 🖼️ **Interactive GUI** - User-friendly interface with real-time image preview
- 🔍 **Advanced OCR Engine** - Multiple OCR engine options (Legacy, LSTM, Combined)
- ⚙️ **Customizable Processing** - Extensive preprocessing and post-processing options
- 📝 **Spell Checking** - Built-in spell checking using PyEnchant
- 📊 **Progress Tracking** - Real-time progress monitoring
- 🎯 **High Accuracy** - Confidence score for extracted text
- 📋 **Rich Text Output** - Formatted results with metadata
- 🔄 **Multi-threaded Processing** - Non-blocking UI during OCR operations

## Prerequisites

Before running the application, ensure you have the following installed:

- Python 3.7 or higher
- Tesseract OCR engine
- Required Python packages:

```bash
pip install -r requirements.txt
```

### Required Packages
```txt name=requirements.txt
PyQt6
opencv-python
numpy
pytesseract
Pillow
pyenchant
```

## Installation

1. Clone the repository:
```bash
https://github.com/Ritinikhil/OCR-Engine.git
cd OCR-Engine
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Tesseract OCR:
   - **Windows**: Download and install from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - **Linux**: `sudo apt-get install tesseract-ocr`
   - **macOS**: `brew install tesseract`

4. Configure Tesseract path in the code:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Adjust path as needed
```

## Usage

1. Launch the application:
```bash
python main.py
```

2. Using the Application:
   - Click "Select Image" to choose an image file
   - Configure OCR settings:
     - OCR Engine Mode (Legacy/LSTM/Combined)
     - Page Segmentation Mode
     - Preprocessing options (Denoising, Deskewing)
     - Thresholding Method
     - Post-processing options (Spell Check)
   - Click "Process Image" to start OCR
   - View results in the text area

## Features in Detail

### OCR Engine Options
- **Legacy Engine**: Traditional Tesseract engine
- **LSTM Engine**: Neural network-based engine
- **Combined Mode**: Uses both engines for better accuracy

### Preprocessing Options
- **Denoising**: Reduces image noise
- **Deskewing**: Corrects image orientation
- **Thresholding Methods**: 
  - Adaptive: Better for varying lighting conditions
  - Otsu: Optimal for clear, binary images

### Post-processing Features
- Spell checking with PyEnchant
- Confidence scoring
- Timestamp logging
- Formatted output with metadata

## Error Handling

The application includes comprehensive error handling:
- Image loading validation
- Memory usage monitoring
- Process tracking
- Detailed error logging

## Logging

The application maintains detailed logs in `ocr_app.log`, including:
- Process completion status
- Error messages
- Confidence scores
- Timestamps

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) for the GUI framework
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for the OCR engine
- [OpenCV](https://opencv.org/) for image processing
- [PyEnchant](https://pyenchant.github.io/pyenchant/) for spell checking

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.
