import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, Base
from backend.models import AppelOffre

def init_db():
    print("Connexion à PostgreSQL et création des tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables creees avec succes !")
    except Exception as e:
        print(f"Erreur lors de la creation des tables : {e}")
        print("Avez-vous bien lance 'docker compose up -d' ?")

if __name__ == "__main__":
    init_db()
