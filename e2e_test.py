import time
import os
import json
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def run_e2e_test():
    print("=== DÉBUT DU TEST DE BOUT EN BOUT ===")
    
    zip_path = "tests/fixtures/sample_ao.zip"
    if not os.path.exists(zip_path):
        print(f"Erreur : Le fichier de test {zip_path} n'existe pas.")
        return

    print(f"1. Envoi du fichier {zip_path} vers l'API d'upload...")
    with open(zip_path, "rb") as f:
        response = client.post("/api/v1/ged/documents/upload", files={"file": ("sample_ao.zip", f, "application/zip")})
    
    if response.status_code != 200:
        print(f"Erreur HTTP {response.status_code} lors de l'upload: {response.text}")
        return
        
    data = response.json()
    doc_id = data.get("document_id")
    print(f"   -> Résultat reçu : {data}")
    print(f"   -> Document ID assigné : {doc_id}")
    
    if not doc_id:
        print("Erreur : Aucun document_id n'a été retourné.")
        return

    print("\n2. Vérification du statut de traitement en boucle...")
    status = "queued"
    attempts = 0
    while status not in ["ocr_processed", "failed"] and attempts < 10:
        time.sleep(1) # Attendre 1 seconde
        attempts += 1
        res = client.get(f"/api/v1/ged/documents/{doc_id}/status")
        if res.status_code == 200:
            status_data = res.json()
            status = status_data.get("status")
            print(f"   [Tentative {attempts}] Statut actuel : {status}")
        else:
            print(f"   Erreur lors de la récupération du statut : {res.text}")
            break
            
    print(f"\n3. Traitement terminé avec le statut final : {status}")
    if status != "ocr_processed":
        print("   Le traitement n'a pas réussi. Échec du test.")
        return
        
    print("\n4. Récupération des appels d'offres depuis la base de données...")
    # L'appel d'offres a normalement pris le nom de fichier ou un numéro aléatoire.
    # On liste les plus récents
    res_ao = client.get("/api/v1/ged/appels-offres?page=1&page_size=5")
    if res_ao.status_code != 200:
        print(f"Erreur lors de la récupération des AO: {res_ao.text}")
        return
        
    ao_list = res_ao.json().get("items", [])
    print(f"   -> {len(ao_list)} appel(s) d'offres trouvés dans la liste récente.")
    if len(ao_list) > 0:
        recent_ao = ao_list[0]
        print("   Détail du dernier Appel d'Offres enregistré :")
        print(json.dumps(recent_ao, indent=2, ensure_ascii=False))
        numero = recent_ao.get("numero_ordre")
        
        print(f"\n5. Récupération des détails approfondis (incluant OCR Logs) pour l'AO : {numero}")
        res_detail = client.get(f"/api/v1/ged/appels-offres/{numero}")
        if res_detail.status_code == 200:
            detail = res_detail.json()
            print("   Logs OCR associés :")
            print(json.dumps(detail.get("ocr_logs", []), indent=2, ensure_ascii=False))
        else:
            print("   Impossible de récupérer les détails de cet appel d'offres.")
    else:
        print("   Aucun appel d'offres n'a été créé suite à l'ingestion.")
        
    print("\n=== FIN DU TEST DE BOUT EN BOUT ===")

if __name__ == "__main__":
    run_e2e_test()
