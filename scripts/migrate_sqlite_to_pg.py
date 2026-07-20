import sqlite3
from sqlalchemy.orm import Session
from backend.database import engine, get_db
from backend.models import Marche, Document, DocStatus, CategorieMarche
import json
import re

def parse_number(value):
    if not value:
        return 0
    cleaned = re.sub(r'[^\d,\.]', '', str(value))
    cleaned = cleaned.replace(' ', '').replace(',', '.')
    try:
        return float(cleaned) if cleaned else 0
    except ValueError:
        return 0

def migrate():
    # Connexion SQLite
    conn = sqlite3.connect('ged.db')
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM appels_offres").fetchall()
    conn.close()

    if not rows:
        print("Aucune donnée dans SQLite à migrer.")
        return

    # Connexion PostgreSQL via SQLAlchemy
    db = Session(bind=engine)

    try:
        migrated = 0
        for r in rows:
            numero_ordre = r["numero_ordre"]
            if not numero_ordre:
                continue

            # Vérifier si déjà migré
            existing = db.query(Marche).filter(Marche.numero_appel_offre == numero_ordre).first()
            if existing:
                continue

            archive_name = r["dossier_zip_source"] or "Archive.zip"
            doc = db.query(Document).filter(Document.archive_name == archive_name).first()
            if not doc:
                doc = Document(
                    archive_name=archive_name,
                    file_name=archive_name,
                    extension=".zip",
                    storage_path=f"data/raw/{archive_name}",
                    status=DocStatus.extracted
                )
                db.add(doc)
                db.commit()
                db.refresh(doc)

            budget = parse_number(r["estimation_mad"])
            caution = parse_number(r["caution_mad"])
            delai = parse_number(r["delai_execution"])

            cat_str = r["categorie_marche"] or ""
            cat_enum = None
            if "travaux" in cat_str.lower(): cat_enum = CategorieMarche.Travaux
            elif "fourniture" in cat_str.lower(): cat_enum = CategorieMarche.Fournitures
            elif "service" in cat_str.lower(): cat_enum = CategorieMarche.Services
            elif "étude" in cat_str.lower() or "etude" in cat_str.lower(): cat_enum = CategorieMarche.Etudes

            marche = Marche(
                document_source_id=doc.id,
                numero_appel_offre=numero_ordre,
                titre_projet=r["objet"] or "Titre Inconnu",
                organisme_acheteur=r["maitre_ouvrage"] or "Inconnu",
                budget_estimatif_mad=budget,
                caution_provisoire_mad=caution,
                delai_execution_mois=delai,
                ville_execution=r["lieu_ouverture_plis"],
                categorie_prestation=cat_enum
            )
            db.add(marche)
            migrated += 1
        
        db.commit()
        print(f" Migration réussie : {migrated} marché(s) copié(s) de SQLite vers PostgreSQL !")

    except Exception as e:
        db.rollback()
        print(f"Erreur de migration : {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
