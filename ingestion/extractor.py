import os
import zipfile
import json
import logging
from ocr.extract_native import read_docx, read_pdf
from ocr.extract_ocr import extract_text_from_scanned_pdf
from nlp.extract_entities import extract as extract_nlp

logging.basicConfig(level=logging.INFO)

def extract_zip(zip_path, extract_dir):
    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

def get_files_by_ext(directory, exts):
    result = []
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.startswith("~$"):
                continue
            if any(f.lower().endswith(ext) for ext in exts):
                result.append(os.path.join(root, f))
    return result

def save_text(numero, text):
    os.makedirs('data/processed/text', exist_ok=True)
    with open(f'data/processed/text/{numero}.txt', 'w', encoding='utf-8') as f:
        f.write(text)

def save_json(numero, data):
    os.makedirs('data/processed/json', exist_ok=True)
    with open(f'data/processed/json/{numero}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def process_archive(file_path, utiliser_llm=False, start_page=None, end_page=None):
    base_name = os.path.basename(file_path)
    numero_ordre = os.path.splitext(base_name)[0].replace('AO_', '')
    
    files_to_process = []
    if file_path.lower().endswith('.zip'):
        extract_dir = file_path.replace(".zip", "_extracted")
        try:
            extract_zip(file_path, extract_dir)
            files_to_process = get_files_by_ext(extract_dir, ['.docx', '.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.tif'])
        except Exception as e:
            logging.error(f"[{numero_ordre}] Impossible d'extraire le ZIP : {e}")
            return False, None, None, 0
    elif any(file_path.lower().endswith(ext) for ext in ['.docx', '.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.tif']):
        files_to_process = [file_path]
    else:
        logging.error(f"[{numero_ordre}] Format de fichier non supporte : {base_name}")
        return False, None, None, 0

    def file_priority(path):
        p_lower = path.lower()
        if 'avis' in p_lower:
            return 1
        elif 'rc' in p_lower or 'reglement' in p_lower:
            return 2
        elif 'cps' in p_lower:
            return 3
        return 4

    files_to_process.sort(key=file_priority)
    logging.info(f"[{numero_ordre}] {len(files_to_process)} document(s) trouvé(s) pour traitement.")

    full_text = ""
    if start_page and start_page > 1:
        try:
            with open(f'data/processed/text/{numero_ordre}.txt', 'r', encoding='utf-8') as f:
                full_text = f.read() + "\n"
        except Exception:
            pass

    total_pages_pdf = 0
    for f in files_to_process:
        fname = os.path.basename(f).lower()
        if f.lower().endswith('.docx'):
            text = read_docx(f)
            total_pages_pdf = max(total_pages_pdf, 1)
        elif f.lower().endswith('.pdf'):
            from ocr.extract_native import EncryptedPdfError
            try:
                text, needs_ocr = read_pdf(f)
                if needs_ocr:
                    # Pour les avis : scan complet (1-3 pages). Pour les gros CPS/RC : 5 pages suffisent pour les clauses financières
                    max_scan_pages = None if 'avis' in fname else (end_page or 5)
                    text, _, total_pages_pdf = extract_text_from_scanned_pdf(f, text, start_page=start_page, end_page=max_scan_pages)
                else:
                    total_pages_pdf = max(total_pages_pdf, 1)
            except EncryptedPdfError as e:
                logging.error(f"[{numero_ordre}] {e}")
                text = ""
        elif f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.tif')):
            try:
                import pytesseract
                from PIL import Image
                from ocr.preprocess import denoise, deskew
                img = Image.open(f)
                img = denoise(img)
                img = deskew(img)
                text = pytesseract.image_to_string(img, lang='fra+ara')
                total_pages_pdf = max(total_pages_pdf, 1)
            except Exception as e:
                logging.error(f"Erreur OCR image {f}: {e}")
                text = ""
        else:
            text = ""
        full_text += text + "\n"
        
    if total_pages_pdf == 0:
        total_pages_pdf = 1
        
    save_text(numero_ordre, full_text)

    if full_text.strip():
        extracted_data = extract_nlp(full_text)
        save_json(numero_ordre, extracted_data)
        
        # Format payload for DB
        ao_payload = {
            "numero_ordre": numero_ordre,
            "dossier_zip_source": base_name,
            "objet": "En cours d'analyse...",
            "maitre_ouvrage": "En cours...",
        }
        
        for k, v in extracted_data["fields"].items():
            ao_payload[k] = v["value"]
            
        return True, ao_payload, extracted_data, total_pages_pdf
    
    return False, None, None, total_pages_pdf

def main():
    raw_dir = "data/raw"
    if not os.path.exists(raw_dir):
        return
    zips = [f for f in os.listdir(raw_dir) if f.endswith('.zip')]
    logging.info(f"{len(zips)} archive(s) ZIP à traiter dans {raw_dir}/")

    reussis, echoues = 0, 0
    for f in zips:
        logging.info(f"--- Traitement de {f} ---")
        ok, payload, raw_fields, total_pages = process_archive(os.path.join(raw_dir, f))
        if ok:
            reussis += 1
            logging.info(f"Payload généré: {payload}")
        else:
            echoues += 1

    logging.info(f"\n=== Bilan extraction : {reussis} réussi(s), {echoues} échec(s) sur {len(zips)} ===")

if __name__ == "__main__":
    main()