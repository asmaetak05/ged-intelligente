import logging

try:
    import pytesseract
    from pdf2image import convert_from_path
except ImportError:
    pytesseract = None
    convert_from_path = None

def extract_text_from_scanned_pdf(file_path, text=""):
    logging.info(f"PDF {file_path} semble être scanné. Lancement de l'OCR...")
    if pytesseract and convert_from_path:
        try:
            images = convert_from_path(file_path)
            for img in images:
                text += pytesseract.image_to_string(img, lang='fra+ara')
        except Exception as e:
            logging.error(f"Erreur OCR (Tesseract/Poppler peut-être absent du système): {e}")
    else:
        logging.warning("Bibliothèques OCR non installées. Extraction impossible pour ce fichier.")
    return text, True
