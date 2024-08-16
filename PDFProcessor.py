import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import numpy as np
import cv2
import os

class PDFProcessor:
    def __init__(self, input_folder, output_folder, zoom=2.0):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.zoom = zoom

        # Crear la carpeta de salida si no existe
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def extract_text_from_image(self, image):
        return pytesseract.image_to_string(image)

    def is_text_upside_down(self, text):
        words = text.split()
        normal_words = sum(1 for word in words if word.isalpha())
        upside_down_words = sum(1 for word in words if not word.isalpha())
        return upside_down_words > normal_words

    def remove_watermark(self, image):
        gray_image = image.convert('L')
        np_image = np.array(gray_image)
        _, binary_image = cv2.threshold(np_image, 200, 255, cv2.THRESH_BINARY_INV)
        processed_image = Image.fromarray(binary_image)
        return processed_image

    def detect_and_correct_pdf(self, file_path, output_path):
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(self.zoom, self.zoom))
            img = Image.open(io.BytesIO(pix.tobytes()))

            text = self.extract_text_from_image(img)
            if self.is_text_upside_down(text):
                print(f"Page {page_num + 1} is upside down, rotating...")
                img = img.rotate(180, expand=True)

            img = self.remove_watermark(img)

            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()

            rect = page.rect
            page.insert_image(rect, stream=img_bytes)

        doc.save(output_path)
        print(f"Processed PDF saved as {output_path}")

    def process_pdfs(self):
        for filename in os.listdir(self.input_folder):
            if filename.lower().endswith('.pdf'):
                input_path = os.path.join(self.input_folder, filename)
                output_path = os.path.join(self.output_folder, filename)
                print(f"Processing {input_path}...")
                self.detect_and_correct_pdf(input_path, output_path)

# Uso del procesador de PDF
if __name__ == "__main__":
    input_folder = 'input'
    output_folder = 'output'
    processor = PDFProcessor(input_folder, output_folder)
    processor.process_pdfs()
