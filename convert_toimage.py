import fitz  # PyMuPDF
from typing import List

def convert_pdf_to_images(pdf_bytes: bytes) -> List[bytes]:
    """
    Convierte cada página de un archivo PDF (proporcionado como bytes) en una lista de imágenes PNG (también como bytes).
    """
    images = []
    try:
        # Abrir el PDF desde el stream de bytes en memoria
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        # Iterar sobre cada página del documento
        for page_number in range(len(pdf_document)):
            page = pdf_document.load_page(page_number)
            
            # Renderizar la página a un pixmap (una representación de imagen en memoria)
            # Se usa una matriz de zoom para aumentar la resolución (DPI) y mejorar la calidad del OCR
            zoom_matrix = fitz.Matrix(2.0, 2.0) # Zoom 2x en cada dimensión = 300 DPI aprox.
            pix = page.get_pixmap(matrix=zoom_matrix)
            
            # Guardar el pixmap como bytes en formato PNG
            img_bytes = pix.tobytes("png")
            images.append(img_bytes)
            
    except Exception as e:
        print(f"Error al procesar el PDF: {e}")
        return []  # Devolver lista vacía en caso de error
        
    return images