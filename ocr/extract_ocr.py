import logging
import os
import hashlib

try:
    import pytesseract
    from pdf2image import convert_from_path
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
except ImportError:
    pytesseract = None
    convert_from_path = None

CACHE_DIR = "data/ocr_cache"


def get_image_hash(img):
    """Calcule le hash SHA-256 d'une image PIL (OC-01)."""
    hasher = hashlib.sha256()
    hasher.update(img.tobytes())
    return hasher.hexdigest()


def get_cached_ocr(img_hash):
    """Récupère le texte OCRisé en cache s'il existe (OC-01)."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(CACHE_DIR, f"{img_hash}.txt")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logging.warning(f"[OCR Cache] Erreur lecture cache: {e}")
    return None


def save_ocr_cache(img_hash, text):
    """Sauvegarde le texte extrait par page en cache (OC-01)."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(CACHE_DIR, f"{img_hash}.txt")
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        logging.warning(f"[OCR Cache] Erreur écriture cache: {e}")


def extract_text_from_scanned_pdf(file_path, text=""):
    """Extrait le texte d'un PDF scanné avec prétraitement, bilinguisme et cache (OC-01, OC-05, OC-06)."""
    logging.info(f"PDF {file_path} semble être scanné. Lancement de l'OCR...")
    if pytesseract and convert_from_path:
        try:
            from ocr.preprocess import denoise, deskew
            
            poppler_bin = os.path.join(os.getcwd(), r'bin\poppler\poppler-24.02.0\Library\bin')
            images = convert_from_path(file_path, poppler_path=poppler_bin)
            
            for i, img in enumerate(images):
                img_hash = get_image_hash(img)
                cached_text = get_cached_ocr(img_hash)
                
                if cached_text is not None:
                    logging.info(f"[OCR] Page {i+1}/{len(images)} chargée depuis le cache.")
                    text += cached_text + "\n"
                    continue
                
                # Prétraitement d'image (OC-05)
                img_preprocessed = denoise(img)
                img_preprocessed = deskew(img_preprocessed)
                
                # OCR Bilingue FR+AR avec repli (OC-06)
                page_text = ""
                try:
                    page_text = pytesseract.image_to_string(img_preprocessed, lang='fra+ara')
                except Exception as e_lang:
                    logging.warning(f"[OCR] Échec fra+ara sur page {i+1}, repli sur fra : {e_lang}")
                    try:
                        page_text = pytesseract.image_to_string(img_preprocessed, lang='fra')
                    except Exception:
                        page_text = pytesseract.image_to_string(img_preprocessed)
                
                text += page_text + "\n"
                save_ocr_cache(img_hash, page_text)
                
        except Exception as e:
            logging.error(f"Erreur OCR (Tesseract/Poppler): {e}")
    else:
        logging.warning("Bibliothèques OCR non installées. Extraction impossible pour ce fichier.")
    return text, True
