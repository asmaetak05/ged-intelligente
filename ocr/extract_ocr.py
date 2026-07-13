import logging
import os

try:
    import pytesseract
    from pdf2image import convert_from_path
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
except ImportError:
    pytesseract = None
    convert_from_path = None

def extract_text_from_scanned_pdf(file_path, text=""):
    logging.info(f"PDF {file_path} semble être scanné. Lancement de l'OCR...")
    if pytesseract and convert_from_path:
        try:
            poppler_bin = os.path.join(os.getcwd(), r'bin\poppler\poppler-24.02.0\Library\bin')
            images = convert_from_path(file_path, poppler_path=poppler_bin)
            for img in images:
                text += pytesseract.image_to_string(img)
        except Exception as e:
            logging.error(f"Erreur OCR (Tesseract/Poppler): {e}")
    else:
        logging.warning("Bibliothèques OCR non installées. Extraction impossible pour ce fichier.")
    return text, True
