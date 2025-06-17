import sys
import os
import cv2
import numpy as np
import pytesseract
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel,
                             QFileDialog, QVBoxLayout, QHBoxLayout, QWidget,
                             QProgressBar, QMessageBox, QComboBox, QSpinBox,
                             QCheckBox, QTextEdit, QGroupBox, QSlider)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
import enchant
from PIL import Image
import json
import logging
from datetime import datetime


class OCRThread(QThread):
    progress = pyqtSignal(int)
    result = pyqtSignal(str)
    preview = pyqtSignal(QImage)
    error = pyqtSignal(str)

    def __init__(self, image_path, settings):
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

        super().__init__()
        self.image_path = image_path
        self.settings = settings
        self.dictionary = enchant.Dict("en_US")

    # Modify the image processing section to include memory checks:
    # Modify the image processing section to include memory checks:
    def preprocess_image(self, image):
        try:
            # Add size check
            if image.size > 1e8:  # 100MB limit
                raise ValueError("Image too large to process")

            # Add memory monitoring
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()

            # Release memory explicitly
            image = None

            return gray
        except Exception as e:
            logging.error(f"Memory error during preprocessing: {str(e)}")
            raise

    def post_process_text(self, text):
        """Advanced text post-processing"""
        try:
            lines = text.split('\n')
            processed_lines = []

            for line in lines:
                words = line.split()
                processed_words = []

                for word in words:
                    # Apply corrections only to words longer than 2 characters
                    if len(word) > 2:
                        # Check if the word is already correct
                        if not self.dictionary.check(word):
                            # Get suggestions and use the first one if available
                            suggestions = self.dictionary.suggest(word)
                            if suggestions:
                                # Use Levenshtein distance to find the closest match
                                processed_words.append(suggestions[0])
                                continue

                    processed_words.append(word)

                processed_lines.append(' '.join(processed_words))

            return '\n'.join(processed_lines)
        except Exception as e:
            logging.error(f"Post-processing error: {str(e)}")
            raise

    # Add this to your application
    def closeEvent(self, event):
        # Clean up resources
        if self.ocr_thread:
            self.ocr_thread.quit()
            self.ocr_thread.wait()
        super().closeEvent(event)

    def run(self):
        try:
                # Load image
            image = cv2.imread(self.image_path)
            if image is None:
                raise ValueError("Failed to load image")

            self.progress.emit(10)

                # Preprocess image
            processed_image = self.preprocess_image(image)

                # Convert to PIL Image for preview
            height, width = processed_image.shape
            bytes_per_line = width
            q_img = QImage(processed_image.data, width, height, bytes_per_line, QImage.Format.Format_Grayscale8)
            self.preview.emit(q_img)

            self.progress.emit(40)

                # Configure Tesseract parameters
                # Change from using index directly to using appropriate OEM value
            oem_values = [1, 1, 3]  # Map combo box index to OEM values (LSTM only, LSTM only, Default)
            custom_config = f'--oem {oem_values[self.settings["ocr_engine"]]} --psm {self.settings["page_segmentation"] + 1}'

                # Perform OCR
            text = pytesseract.image_to_string(processed_image, config=custom_config)

            self.progress.emit(70)

            # Get confidence scores
            confidence_data = pytesseract.image_to_data(processed_image, config=custom_config,
                                                        output_type=pytesseract.Output.DICT)

            # Calculate average confidence
            confidences = [int(conf) for conf in confidence_data['conf'] if conf != '-1']
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            # Prepare result with metadata
            result = {
                'text': text,
                'confidence': avg_confidence,
                'timestamp': datetime.now().isoformat(),
                'settings': self.settings
            }

            self.result.emit(json.dumps(result))
            self.progress.emit(100)

        except Exception as e:
            self.error.emit(str(e))
            logging.error(f"OCR error: {str(e)}")


class AdvancedOCRApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            filename='ocr_app.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def initUI(self):
        self.setWindowTitle('Unity OCR Application')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
            QLabel {
                font-size: 14px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                margin-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left panel for settings
        left_panel = QVBoxLayout()

        # Image selection
        select_file_btn = QPushButton('Select Image')
        select_file_btn.clicked.connect(self.select_image)
        left_panel.addWidget(select_file_btn)

        # OCR Settings group
        ocr_settings_group = QGroupBox("OCR Settings")
        ocr_settings_layout = QVBoxLayout()

        # OCR Engine Mode
        self.ocr_engine_combo = QComboBox()
        self.ocr_engine_combo.addItems(['Legacy Engine', 'LSTM Engine', 'Legacy + LSTM'])
        ocr_settings_layout.addWidget(QLabel('OCR Engine:'))
        ocr_settings_layout.addWidget(self.ocr_engine_combo)

        # Page Segmentation Mode
        self.psm_combo = QComboBox()
        self.psm_combo.addItems([
            'Auto', 'Single Block', 'Single Line',
            'Single Word', 'Single Char', 'Sparse Text'
        ])
        ocr_settings_layout.addWidget(QLabel('Page Segmentation:'))
        ocr_settings_layout.addWidget(self.psm_combo)

        ocr_settings_group.setLayout(ocr_settings_layout)
        left_panel.addWidget(ocr_settings_group)

        # Preprocessing Settings group
        preproc_group = QGroupBox("Preprocessing")
        preproc_layout = QVBoxLayout()

        self.denoise_cb = QCheckBox('Apply Denoising')
        self.deskew_cb = QCheckBox('Apply Deskewing')
        self.threshold_combo = QComboBox()
        self.threshold_combo.addItems(['Adaptive', 'Otsu'])

        preproc_layout.addWidget(self.denoise_cb)
        preproc_layout.addWidget(self.deskew_cb)
        preproc_layout.addWidget(QLabel('Thresholding Method:'))
        preproc_layout.addWidget(self.threshold_combo)

        preproc_group.setLayout(preproc_layout)
        left_panel.addWidget(preproc_group)

        # Post-processing Settings group
        postproc_group = QGroupBox("Post-processing")
        postproc_layout = QVBoxLayout()

        self.spellcheck_cb = QCheckBox('Enable Spell Check')
        postproc_layout.addWidget(self.spellcheck_cb)

        postproc_group.setLayout(postproc_layout)
        left_panel.addWidget(postproc_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        left_panel.addWidget(self.progress_bar)

        # Process button
        self.process_btn = QPushButton('Process Image')
        self.process_btn.clicked.connect(self.process_image)
        self.process_btn.setEnabled(False)
        left_panel.addWidget(self.process_btn)

        main_layout.addLayout(left_panel)

        # Right panel for preview and results
        right_panel = QVBoxLayout()

        # Image preview
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(400, 300)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet('border: 1px solid #BDBDBD;')
        right_panel.addWidget(self.preview_label)

        # Results text area
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        right_panel.addWidget(self.results_text)

        main_layout.addLayout(right_panel)

        self.image_path = None
        self.ocr_thread = None

    def select_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        if file_name:
            self.image_path = file_name
            self.preview_image(file_name)
            self.process_btn.setEnabled(True)

    def preview_image(self, image_path):
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(
            self.preview_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.preview_label.setPixmap(scaled_pixmap)

    def get_settings(self):
        return {
            'ocr_engine': self.ocr_engine_combo.currentIndex(),
            'page_segmentation': self.psm_combo.currentIndex(),
            'denoise': self.denoise_cb.isChecked(),
            'deskew': self.deskew_cb.isChecked(),
            'threshold_method': self.threshold_combo.currentText().lower(),
            'post_process': self.spellcheck_cb.isChecked()
        }

    def process_image(self):
        if not self.image_path:
            return

        self.process_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        settings = self.get_settings()

        # Create and start the OCR thread
        self.ocr_thread = OCRThread(self.image_path, settings)
        self.ocr_thread.progress.connect(self.update_progress)
        self.ocr_thread.result.connect(self.show_results)
        self.ocr_thread.preview.connect(self.update_preview)
        self.ocr_thread.error.connect(self.show_error)
        self.ocr_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_preview(self, qimage):
        pixmap = QPixmap.fromImage(qimage)
        scaled_pixmap = pixmap.scaled(
            self.preview_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.preview_label.setPixmap(scaled_pixmap)

    def show_results(self, result_json):
        result = json.loads(result_json)

        # Format the results
        formatted_result = (
            f"OCR Results:\n"
            f"============\n\n"
            f"Confidence Score: {result['confidence']:.2f}%\n"
            f"Timestamp: {result['timestamp']}\n\n"
            f"Extracted Text:\n"
            f"-------------\n"
            f"{result['text']}\n"
        )

        self.results_text.setText(formatted_result)
        self.process_btn.setEnabled(True)

        # Log the results
        logging.info(f"OCR completed - Confidence: {result['confidence']:.2f}%")

    def show_error(self, error_message):
        self.process_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")
        self.progress_bar.setValue(0)
        logging.error(f"Error during OCR: {error_message}")


def main():
    app = QApplication(sys.argv)
    window = AdvancedOCRApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
