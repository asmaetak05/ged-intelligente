"""Script d'importation massive du référentiel MEE (Excel 5000 marchés) dans la base de données GED Intelligente.
"""
import os
import sys
import pandas as pd
from datetime import datetime

# Ajouter le dossier racine au path python
sys.path.append(os.path.abspath("."))

from backend.database import SessionLocal
from backend.repository import MarcheRepository, DocumentRepository
from backend import models

EXCEL_PATH = "data/raw/referentiel_mee.xlsx.xlsx"

def importer_referentiel_excel():
    if not os.path.exists(EXCEL_PATH):
        print(f"Fichier {EXCEL_PATH} introuvable.")
        return

    print(f"Chargement de {EXCEL_PATH}...")
    df = pd.read_excel(EXCEL_PATH)
    print(f"{len(df)} lignes trouvées dans le fichier Excel.")

    db = SessionLocal()
    repo = MarcheRepository(db)
    
    insérés = 0
    mis_a_jour = 0

    for idx, row in df.iterrows():
        numero = str(row.get("Réf") or row.get("N°") or "").strip()
        if not numero or numero == "nan":
            continue

        objet = str(row.get("Objet") or "").strip()
        organisme = str(row.get("Organisme") or "").strip()
        ville = str(row.get("Ville") or "").strip()
        if ville == "nan": ville = "Maroc"
        
        estimation = row.get("Estimation")
        montant = float(estimation) if pd.notna(estimation) and isinstance(estimation, (int, float)) else None

        date_lim = row.get("Date limite")
        date_limite = None
        if pd.notna(date_lim):
            try:
                if isinstance(date_lim, datetime):
                    date_limite = date_lim.date()
                else:
                    date_limite = datetime.strptime(str(date_lim)[:10], "%Y-%m-%d").date()
            except Exception:
                pass

        payload = {
            "numero_appel_offre": numero,
            "titre_projet": objet if objet != "nan" else f"Appel d'offres N° {numero}",
            "organisme_acheteur": organisme if organisme != "nan" else "Ministère de l'Équipement et de l'Eau",
            "ville_execution": ville,
            "montant": montant,
            "budget_estimatif_mad": montant,
            "date_limite": date_limite
        }

        try:
            marche, action = repo.upsert(payload)
            if action == "created":
                insérés += 1
            else:
                mis_a_jour += 1
        except Exception as e:
            pass

        if (idx + 1) % 500 == 0:
            db.commit()
            print(f"Progression : {idx + 1} / {len(df)} marchés traités...")

    db.commit()
    db.close()
    print(f"\n[OK] Importation terminee : {insérés} nouveaux marches mees crees, {mis_a_jour} mis a jour.")

if __name__ == "__main__":
    importer_referentiel_excel()
