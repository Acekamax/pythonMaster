import fitz  # PyMuPDF
from PIL import Image, ImageOps
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import tempfile
import os
import keras_ocr

def pdf_to_images(input_pdf_path):
    # Abre el archivo PDF
    pdf_document = fitz.open(input_pdf_path)
    image_paths = []

    for page_number in range(len(pdf_document)):
        # Obtiene la página del PDF
        page = pdf_document.load_page(page_number)
        
        # Convierte la página a una imagen
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Ajusta la matriz para alta resolución
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Guarda la imagen en un archivo temporal
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_img:
            img.save(temp_img, format='PNG')
            image_paths.append(temp_img.name)
    
    return image_paths

def correct_image_orientation(image_path):
    # Configura el detector OCR de Keras
    pipeline = keras_ocr.pipeline.Pipeline()

    # Lee la imagen y detecta texto
    image = Image.open(image_path)
    image_array = keras_ocr.tools.imgs_to_array([image])[0]
    prediction_groups = pipeline.recognize([image_array])

    # Ajusta la orientación de la imagen si es necesario
    if prediction_groups:
        # Aquí puedes analizar los resultados para determinar la orientación
        # Por simplicidad, asumimos que la imagen está en la orientación correcta.
        # Puedes usar una lógica más compleja para determinar la orientación correcta.
        # Ejemplo: Si la imagen parece estar al revés, rotarla 180 grados.
        text = ' '.join([word[0] for word in prediction_groups[0]])
        if 'some condition' in text:  # Reemplaza 'some condition' con tu propia lógica
            image = Image.open(image_path)
            image = ImageOps.exif_transpose(image)  # Ajusta la orientación basada en los metadatos EXIF
            image.save(image_path)
    
    return image_path

def images_to_pdf(image_paths, output_pdf_path):
    # Crea un archivo PDF en memoria usando ReportLab
    output = BytesIO()
    c = canvas.Canvas(output, pagesize=letter)
    
    for image_path in image_paths:
        # Corrige la orientación de la imagen si es necesario
        image_path = correct_image_orientation(image_path)
        
        # Añade la imagen al PDF
        c.drawImage(image_path, 0, 0, width=letter[0], height=letter[1])
        c.showPage()  # Añade una nueva página para la siguiente imagen

    c.save()
    
    # Guarda el archivo PDF resultante en el disco
    with open(output_pdf_path, 'wb') as f:
        f.write(output.getvalue())
    
    print(f"PDF creado: {output_pdf_path}")

def clean_up(image_paths):
    # Elimina los archivos temporales
    for image_path in image_paths:
        os.remove(image_path)

def main(input_pdf_path, output_pdf_path):
    # Convierte PDF a imágenes temporales
    image_paths = pdf_to_images(input_pdf_path)
    
    # Convierte imágenes a PDF
    images_to_pdf(image_paths, output_pdf_path)
    
    # Elimina las imágenes temporales
    clean_up(image_paths)

if __name__ == "__main__":
    input_pdf_path = r"C:\Users\dsrub\Desktop\python\proyecto OCR\TEST\01001.pdf"  # Reemplaza con la ruta de tu archivo PDF
    output_pdf_path = r"C:\Users\dsrub\Desktop\python\proyecto OCR\TEST\01001_procesed.pdf"  # Reemplaza con la ruta de tu archivo PDF resultante
    main(input_pdf_path, output_pdf_path)
