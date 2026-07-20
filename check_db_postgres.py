from backend.database import SessionLocal
from backend import models

db = SessionLocal()

nb_documents = db.query(models.Document).count()
nb_marches = db.query(models.Marche).count()

print(f"Documents : {nb_documents}")
print(f"Marchés   : {nb_marches}")

print("\n--- Détail des marchés ---")
for m in db.query(models.Marche).all():
    print(f"  - {m.numero_appel_offre} | {m.titre_projet} | {m.organisme_acheteur} | {m.budget_estimatif_mad} MAD")

db.close()