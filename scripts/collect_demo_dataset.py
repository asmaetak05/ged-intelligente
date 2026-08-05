"""Script d'ingestion et de collecte automatique pour la GED Intelligente.

Ce script :
1. Récupère la liste des références d'appels d'offres depuis :
   - L'API de l'administration MEE (si MEE_API_URL est renseignée dans .env ou en argument)
   - OU un fichier d'export local (data/referentiel_mee.xlsx / data/referentiel_mee.json)
   - OU la liste des archives déjà présentes dans data/raw/
2. Télécharge automatiquement les dossiers D.A.O (ZIP / PDF) correspondants depuis le portail national (www.marchespublics.gov.ma).
3. Ingeste automatiquement les documents dans l'API backend FastAPI (OCR + NLP + BDD).
"""

import asyncio
import glob
import json
import os
import re
import sys
import httpx
from urllib.parse import urljoin
from playwright.async_api import async_playwright

# Configuration des URLs et chemins
API_GED_URL = os.getenv("API_GED_URL", "http://127.0.0.1:8000")
MEE_API_URL = os.getenv("MEE_API_URL", "") # URL de l'API de votre encadrante si disponible
REFERENTIEL_EXCEL = os.getenv("REFERENTIEL_EXCEL", "data/referentiel_mee.xlsx")
REFERENTIEL_JSON = os.getenv("REFERENTIEL_JSON", "data/referentiel_mee.json")
MARCHES_PUBLICS_URL = "https://www.marchespublics.gov.ma/index.php?page=entreprise.EntrepriseAdvancedSearch&AllCons"
RAW_DATA_DIR = "data/raw"

os.makedirs(RAW_DATA_DIR, exist_ok=True)


def charger_references_depuis_fichier():
    """Charge les références depuis un fichier Excel ou JSON local."""
    references = []
    
    # 1. Vérifier si un fichier JSON existe
    if os.path.exists(REFERENTIEL_JSON):
        try:
            with open(REFERENTIEL_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        ref = item.get("ref") or item.get("numero") or item.get("numero_ordre")
                        if ref:
                            references.append({
                                "ref": str(ref).strip(),
                                "objet": item.get("objet", ""),
                                "organisme": item.get("organisme", "")
                            })
            print(f"[Catalogue] {len(references)} référence(s) chargée(s) depuis {REFERENTIEL_JSON}")
            return references
        except Exception as e:
            print(f"[Catalogue] Erreur lecture {REFERENTIEL_JSON}: {e}")

    # 2. Chercher le fichier Excel sur plusieurs chemins possibles
    chemins_excel = [
        "data/raw/referentiel_mee.xlsx.xlsx",
        "data/raw/referentiel_mee.xlsx",
        REFERENTIEL_EXCEL
    ]
    fichier_trouve = next((p for p in chemins_excel if os.path.exists(p)), None)

    if fichier_trouve:
        try:
            import pandas as pd
            df = pd.read_excel(fichier_trouve)
            # Chercher les colonnes correspondantes
            col_ref = next((c for c in df.columns if any(k in c.lower() for k in ["n°", "ref", "num"])), None)
            col_obj = next((c for c in df.columns if "objet" in c.lower()), None)
            col_org = next((c for c in df.columns if any(k in c.lower() for k in ["organisme", "acheteur", "maitre"])), None)
            
            if col_ref:
                for _, row in df.iterrows():
                    ref = row[col_ref]
                    if pd.notna(ref) and str(ref).strip():
                        references.append({
                            "ref": str(ref).strip(),
                            "objet": str(row[col_obj]) if col_obj and pd.notna(row[col_obj]) else "",
                            "organisme": str(row[col_org]) if col_org and pd.notna(row[col_org]) else ""
                        })
            print(f"[Catalogue] {len(references)} référence(s) chargée(s) depuis {REFERENTIEL_EXCEL}")
            return references
        except Exception as e:
            print(f"[Catalogue] Erreur lecture {REFERENTIEL_EXCEL}: {e}")

    return references


async def charger_references_depuis_api():
    """Interroge l'API du site d'administration MEE s'il est configuré."""
    if not MEE_API_URL:
        return []
    
    print(f"[API MEE] Interrogation de l'API : {MEE_API_URL}...")
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(MEE_API_URL)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("items") or data.get("data") or data if isinstance(data, list) else []
                refs = []
                for item in items:
                    ref = item.get("ref") or item.get("numero") or item.get("numero_ordre")
                    if ref:
                        refs.append({
                            "ref": str(ref).strip(),
                            "objet": item.get("objet", ""),
                            "organisme": item.get("organisme", "")
                        })
                print(f"[API MEE] {len(refs)} marché(s) récupéré(s) depuis l'API.")
                return refs
            else:
                print(f"[API MEE] Erreur HTTP {resp.status_code}")
    except Exception as e:
        print(f"[API MEE] Impossible de contacter l'API MEE ({e}). Utilisation du mode secours.")
    return []


async def rechercher_et_telecharger_marchepublics(context, marquis_info):
    """Recherche un marché sur marchespublics.gov.ma et télécharge le fichier D.A.O (ZIP/PDF)."""
    ref = marquis_info["ref"]
    objet = marquis_info.get("objet", "")
    page = await context.new_page()
    
    try:
        print(f"\n[{ref}] Recherche sur marchespublics.gov.ma...")
        await page.goto(MARCHES_PUBLICS_URL, timeout=45000)
        await page.wait_for_load_state("networkidle")
        
        # Sélectionner le statut 'Tous les statuts' pour trouver les marchés archivés/clôturés
        try:
            select_statut = page.locator("select[name*='statut']").first
            if await select_statut.count() > 0:
                await select_statut.select_option(value="ALL")
        except Exception:
            pass

        # Saisir le mot-clé de recherche (Objet ou Référence)
        mot_cle = ref
        if not re.search(r"\d", ref) and objet:
            mot_cle = " ".join(objet.split()[:3]) # 3 premiers mots de l'objet
            
        search_input = page.locator("input[name*='keyword']").first
        if await search_input.count() > 0:
            await search_input.fill(mot_cle)
            await page.click("input[type='submit'][value*='Rechercher'], button:has-text('Rechercher')")
            await page.wait_for_load_state("networkidle")
            
        # Vérifier si des résultats existent
        no_result = await page.locator("text='Aucun résultat'").count()
        if no_result > 0:
            print(f"[{ref}] Aucun résultat trouvé sur le portail public pour '{mot_cle}'.")
            return None
            
        # Chercher le lien 'Accéder à la consultation' ou 'Télécharger'
        detail_link = page.locator("a:has-text('Accéder à la consultation'), a:has-text('Détails')").first
        if await detail_link.count() > 0:
            await detail_link.click()
            await page.wait_for_load_state("networkidle")
            
            # Chercher le lien DCE / D.A.O
            dce_link = page.locator("a:has-text('DCE'), a:has-text('D.A.O'), a:has-text('Télécharger le dossier')").first
            if await dce_link.count() > 0:
                async with page.expect_download(timeout=30000) as download_info:
                    await dce_link.click()
                download = await download_info.value
                safe_ref = re.sub(r"[^\w\-]", "_", ref)
                file_path = os.path.join(RAW_DATA_DIR, f"AO_{safe_ref}.zip")
                await download.save_as(file_path)
                print(f"[{ref}] [OK] Fichier D.A.O téléchargé : {file_path}")
                return file_path
                
        return None

    except Exception as e:
        print(f"[{ref}] Exception durant le téléchargement : {e}")
        return None
    finally:
        await page.close()


async def ingerer_dans_ged_fastapi(chemin_fichier):
    """Envoie le fichier téléchargé à l'API GED FastAPI pour OCR, NLP et stockage BDD."""
    if not os.path.exists(chemin_fichier):
        return False
        
    url_upload = f"{API_GED_URL}/api/v1/ged/documents/upload"
    print(f"[GED FastAPI] Ingestion automatique de {os.path.basename(chemin_fichier)}...")
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            with open(chemin_fichier, "rb") as f:
                files = {"file": (os.path.basename(chemin_fichier), f, "application/zip")}
                resp = await client.post(url_upload, files=files)
                if resp.status_code == 200:
                    data = resp.json()
                    print(f"[GED FastAPI] [OK] Succès ! Document ID: {data.get('document_id')} | Statut: {data.get('status')}")
                    return True
                else:
                    print(f"[GED FastAPI] Erreur HTTP {resp.status_code} : {resp.text}")
    except Exception as e:
        print(f"[GED FastAPI] Erreur de connexion à l'API ({API_GED_URL}): {e}")
    return False


async def main():
    print("==========================================================================")
    print("   [PIPELINE] INGESTION AUTOMATIQUE - GED INTELLIGENTE MEE")
    print("==========================================================================")

    # 1. Charger les références depuis l'API MEE ou un fichier local
    references = await charger_references_depuis_api()
    if not references:
        references = charger_references_depuis_fichier()

    # 2. Secours : Si aucune référence trouvée, utiliser les fichiers locaux déjà présents dans data/raw/
    fichiers_locaux = glob.glob(os.path.join(RAW_DATA_DIR, "*.zip")) + glob.glob(os.path.join(RAW_DATA_DIR, "*.pdf"))
    
    print(f"\n[INFO] Bilan des ressources disponibles :")
    print(f"   - {len(references)} reference(s) dans le catalogue/API MEE")
    print(f"   - {len(fichiers_locaux)} fichier(s) ZIP/PDF deja presents dans {RAW_DATA_DIR}/")

    # 3. Si des références existent, lancer Playwright pour télécharger les D.A.O. manquants
    if references:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(accept_downloads=True)
            
            for item in references[:10]: # Limité aux 10 premiers pour la démonstration
                chemin = await rechercher_et_telecharger_marchepublics(context, item)
                if chemin:
                    await ingerer_dans_ged_fastapi(chemin)
                await asyncio.sleep(1)
            await browser.close()
            
    # 4. Ingestion automatique de tous les fichiers locaux présents dans data/raw/ vers l'API GED
    elif fichiers_locaux:
        print(f"\n[INFO] Traitement du lot local ({len(fichiers_locaux)} fichiers)...")
        for fpath in fichiers_locaux[:15]: # Ingeste les 15 premiers pour la démo
            if not fpath.endswith("corrupt.zip"):
                await ingerer_dans_ged_fastapi(fpath)
                await asyncio.sleep(0.5)

    print("\n[OK] Traitement du pipeline termine avec succes !")

if __name__ == "__main__":
    asyncio.run(main())
