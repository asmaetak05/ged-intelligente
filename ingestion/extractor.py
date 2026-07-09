import os
import zipfile
import re
import json
import urllib.request
import urllib.error
import logging
from docx import Document

logging.basicConfig(level=logging.INFO)

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import pytesseract
    from pdf2image import convert_from_path
except ImportError:
    pytesseract = None
    convert_from_path = None

try:
    import openai
    from dotenv import load_dotenv
    load_dotenv()
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")
    client = openai.OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None
except ImportError:
    client = None

# Route corrigée : correspond à la vraie route ajoutée dans backend/main.py
API_URL = "http://127.0.0.1:8000/api/v1/ged/appels-offres"


def extract_zip(zip_path, extract_dir):
    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)


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


def extract_nlp_regex(text):
    info = {}
    text_clean = re.sub(r'\s+', ' ', text)

    objet = re.search(r"objet\s*(?:de\s*l['’]?appel\s*d['’]?offres)?\s*[\:\-]\s*(.*?)(?=\. |Caution|Estimation)", text_clean, re.IGNORECASE)
    if objet:
        info["objet"] = objet.group(1).strip()

    caution = re.search(r"caution\s+provisoire[^0-9]*?([\d\s\.,]+)\s*(?:dhs|mad|dirhams?)", text_clean, re.IGNORECASE)
    if caution:
        info["caution_mad"] = caution.group(1).strip() + " MAD"

    delai = re.search(r"d[ée]lai d['’]ex[ée]cution[^0-9]*?([\d]+)\s*(mois|jours|semaines)", text_clean, re.IGNORECASE)
    if delai:
        info["delai_execution"] = f"{delai.group(1)} {delai.group(2)}"

    penalite = re.search(r"p[ée]nalit[ée][^0-9]*?([\d\.,]+)\s*(?:pour\s*mille|‰|%)", text_clean, re.IGNORECASE)
    if penalite:
        info["penalite_retard"] = f"{penalite.group(1)} pour mille par jour"

    return info


def extract_nlp_llm(text):
    if not client:
        return extract_nlp_regex(text)

    prompt = f"""
    Extrait les informations suivantes de ce texte de marché public et retourne les sous forme de JSON strict:
    - objet
    - maitre_ouvrage
    - estimation_mad
    - caution_mad
    - delai_execution
    - penalite_retard
    - caution_definitive
    - retenue_garantie
    - agrements_exiges
    - profils_exiges
    - methode_notation
    - categorie_marche
    - date_ouverture_plis
    - lieu_ouverture_plis

    Texte (extrait partiel):
    {text[:4000]}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logging.error(f"Erreur LLM : {e}")
        return extract_nlp_regex(text)


def get_files_by_ext(directory, exts):
    result = []
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.startswith("~$"):
                continue
            if any(f.lower().endswith(ext) for ext in exts):
                result.append(os.path.join(root, f))
    return result


def process_archive(zip_file_path, utiliser_llm=False):
    base_name = os.path.basename(zip_file_path)
    numero_ordre = base_name.replace('.zip', '').replace('AO_', '')
    extract_dir = zip_file_path.replace(".zip", "_extracted")

    try:
        extract_zip(zip_file_path, extract_dir)
    except Exception as e:
        logging.error(f"[{numero_ordre}] Impossible d'extraire le ZIP : {e}")
        return False

    files_to_process = get_files_by_ext(extract_dir, ['.docx', '.pdf'])
    logging.info(f"[{numero_ordre}] {len(files_to_process)} document(s) trouvé(s) dans l'archive.")

    ao_payload = {
        "numero_ordre": numero_ordre,
        "dossier_zip_source": base_name,
        "objet": "En cours d'analyse...",
        "maitre_ouvrage": "En cours...",
    }

    full_text = ""
    for f in files_to_process:
        if f.lower().endswith('.docx'):
            text = read_docx(f)
        elif f.lower().endswith('.pdf'):
            text, _ = read_pdf(f)
        else:
            text = ""
        full_text += text + "\n"

    if full_text.strip():
        extracted_data = extract_nlp_llm(full_text) if utiliser_llm else extract_nlp_regex(full_text)
        ao_payload.update({k: v for k, v in extracted_data.items() if v})

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(ao_payload, ensure_ascii=False).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            logging.info(f"[{numero_ordre}] ✅ {result.get('action', 'traité')} avec succès (id={result.get('id')})")
            return True
    except urllib.error.HTTPError as e:
        logging.error(f"[{numero_ordre}] ❌ Erreur API HTTP {e.code}: {e.read().decode('utf-8', errors='ignore')}")
        return False
    except Exception as e:
        logging.error(f"[{numero_ordre}] ❌ Erreur API : {e}")
        return False


def main():
    raw_dir = "data/raw"
    zips = [f for f in os.listdir(raw_dir) if f.endswith('.zip')]
    logging.info(f"{len(zips)} archive(s) ZIP à traiter dans {raw_dir}/")

    reussis, echoues = 0, 0
    for f in zips:
        logging.info(f"--- Traitement de {f} ---")
        ok = process_archive(os.path.join(raw_dir, f), utiliser_llm=False)
        if ok:
            reussis += 1
        else:
            echoues += 1

    logging.info(f"\n=== Bilan extraction : {reussis} réussi(s), {echoues} échec(s) sur {len(zips)} ===")


if __name__ == "__main__":
    main()