import os
import sys

# Ensure backend module is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import SessionLocal, engine
from backend.models import (
    Base, TypeAvis, TypeProcedure, EtatAvis, Direction,
    Source, Ville, Qualification, Agrement, Role, Permission
)

def seed_data():
    with SessionLocal() as db:
        print("Seeding Roles & Permissions...")
        roles = {
            "admin": "Administrateur système",
            "analyst": "Analyste des données",
            "reader": "Lecteur"
        }
        for role_name, desc in roles.items():
            if not db.query(Role).filter(Role.name == role_name).first():
                db.add(Role(name=role_name, description=desc))
        
        perms = ["scraper:run", "ml:retrain", "user:manage"]
        for p in perms:
            if not db.query(Permission).filter(Permission.code == p).first():
                db.add(Permission(code=p, description=f"Permission {p}"))
        
        print("Seeding TypeAvis...")
        types_avis = {
            "AOO": "Appel d'Offres Ouvert",
            "AOR": "Appel d'Offres Restreint",
            "AC": "Achat sur Bons de Commande"
        }
        for code, label in types_avis.items():
            if not db.query(TypeAvis).filter(TypeAvis.code == code).first():
                db.add(TypeAvis(code=code, label=label))

        print("Seeding TypeProcedure...")
        procs = {
            "AO": "Appel d'Offres",
            "CN": "Concours",
            "PN": "Procédure Négociée"
        }
        for code, label in procs.items():
            if not db.query(TypeProcedure).filter(TypeProcedure.code == code).first():
                db.add(TypeProcedure(code=code, label=label))

        print("Seeding EtatAvis...")
        etats = {
            "EC": "En cours",
            "CL": "Clôturé",
            "AN": "Annulé"
        }
        for code, label in etats.items():
            if not db.query(EtatAvis).filter(EtatAvis.code == code).first():
                db.add(EtatAvis(code=code, label=label))

        print("Seeding Directions...")
        # Ministère de l'Equipement et de l'Eau
        mee = db.query(Direction).filter(Direction.name == "Ministère de l'Équipement et de l'Eau").first()
        if not mee:
            mee = Direction(name="Ministère de l'Équipement et de l'Eau", type_dir="Ministere")
            db.add(mee)
            db.commit()
            db.refresh(mee)
            
        directions = ["DGR", "DRE", "DPETL"]
        for d in directions:
            if not db.query(Direction).filter(Direction.name == d).first():
                db.add(Direction(name=d, type_dir="Direction", parent_id=mee.id))
        
        print("Seeding Villes...")
        villes = ["Rabat", "Casablanca", "Marrakech", "Tanger"]
        for v in villes:
            if not db.query(Ville).filter(Ville.name == v).first():
                db.add(Ville(name=v))
                
        db.commit()
        print("Seed completed successfully!")

if __name__ == "__main__":
    seed_data()
