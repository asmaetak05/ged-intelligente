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

def read_pdf(file_path):
    text = ""
    if fitz:
        try:
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text()
            if len(text.strip()) > 100:
                return text, False
        except Exception as e:
            logging.error(f"Erreur lecture PDF (Digital) {file_path}: {e}")
    return text, True
