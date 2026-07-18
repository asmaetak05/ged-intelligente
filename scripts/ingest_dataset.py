import glob
import os
import requests
import time

API_URL = "http://127.0.0.1:8000/api/v1/ged/documents/upload"
STATUS_URL = "http://127.0.0.1:8000/api/v1/ged/documents/{}/status"

def ingest_all():
    files = glob.glob("data/raw/*.*")
    if not files:
        print("Aucun fichier trouvé dans data/raw/.")
        return

    print(f"{len(files)} fichier(s) trouvé(s) pour ingestion.")
    reussis = 0
    
    for file_path in files:
        filename = os.path.basename(file_path)
        print(f"\nTraitement de : {filename}")
        
        try:
            with open(file_path, "rb") as f:
                files_payload = {"file": (filename, f, "application/zip")}
                response = requests.post(API_URL, files=files_payload)
            
            if response.status_code == 200:
                data = response.json()
                doc_id = data.get("document_id")
                print(f"[OK] Upload réussi ! Document ID: {doc_id}")
                
                # Optionnel : attendre la fin du traitement
                # while True:
                #    status_res = requests.get(STATUS_URL.format(doc_id))
                #    if status_res.status_code == 200:
                #        status = status_res.json().get("status")
                #        if status in ["ocr_processed", "failed"]:
                #            print(f"   Statut final : {status}")
                #            break
                #    time.sleep(2)
                
                reussis += 1
            else:
                print(f"[ERROR] Erreur d'upload HTTP {response.status_code} : {response.text}")
                
        except Exception as e:
            print(f"[ERROR] Erreur système : {e}")

    print(f"\n=== Bilan Ingestion : {reussis} sur {len(files)} réussi(s) ===")

if __name__ == "__main__":
    ingest_all()
