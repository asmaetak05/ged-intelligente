import logging
from docx import Document

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

def read_docx(file_path):
    try:
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        logging.error(f"Erreur lecture DOCX {file_path}: {e}")
        return ""

class EncryptedPdfError(Exception):
    pass

def read_pdf(file_path):
    text = ""
    if fitz:
        try:
            doc = fitz.open(file_path)
            if doc.is_encrypted:
                raise EncryptedPdfError(f"Le document PDF {file_path} est chiffré.")
            for i in range(len(doc)):
                page = doc.load_page(i)
                text += page.get_text()
                page = None # Libérer la mémoire
            if len(text.strip()) > 100:
                return text, False
        except EncryptedPdfError as e:
            logging.error(e)
            raise
        except Exception as e:
            logging.error(f"Erreur lecture PDF (Digital) {file_path}: {e}")
    return text, True
