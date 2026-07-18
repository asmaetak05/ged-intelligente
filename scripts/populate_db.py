import urllib.request
import json
import time
import random

api_url_ao = "http://127.0.0.1:8000/api/v1/ged/appels-offres"

base_aos = [
    {
        "numero_ordre": "SF 22/2025",
        "objet": "Etude d’élargissement et de renforcement de la RR507 du PK 32+500 au PK 69+500",
        "maitre_ouvrage": "Equipement (Direction Sefrou)",
        "estimation_mad": "307 320,00 DHS",
        "caution_mad": "4 300,00 DHS",
        "delai_execution": "4",
        "penalite_retard": "1 pour mille (Max 10%)",
        "caution_definitive": "3",
        "retenue_garantie": "Aucune",
        "agrements_exiges": "Domaines D4 et D5",
        "profils_exiges": "Chef de projet (Bac+5, 20 ans exp) ; Ingénieur GC ; Ing. Hydraulique ; Ing. Topographe (ONIGT)",
        "methode_notation": "70% Technique / 30% Financier (Rejet si technique < 70/100)",
        "categorie_marche": "Etudes",
        "dossier_zip_source": "65060956.zip",
        "date_ouverture_plis": "27 Août 2025 à 10 H 00",
        "lieu_ouverture_plis": "Sefrou",
        "region": "Fès-Meknès"
    },
    {
        "numero_ordre": "08/2025/ANEP",
        "objet": "Réalisation d'un cycle de formation sur les lots techniques, destiné aux collaborateurs de l'ANEP",
        "maitre_ouvrage": "Agence Nationale des Équipements Publics (ANEP)",
        "estimation_mad": "574 800,00 DHS",
        "caution_mad": "8 000,00 DHS",
        "delai_execution": "18",
        "penalite_retard": "1 pour mille",
        "caution_definitive": "3",
        "retenue_garantie": "Aucune",
        "agrements_exiges": "Expérience en formation BTP, certifications Fluides Médicaux",
        "profils_exiges": "Chef de projet ; Formateur Courant fort/faible ; Formateur CVC ; Expert Fluides médicaux ; Expert Sécurité Incendie",
        "methode_notation": "Evaluation Technique sur 100 points, Rejet si < 70/100",
        "categorie_marche": "Services",
        "dossier_zip_source": "65058758.zip",
        "date_ouverture_plis": "24 Juillet 2025 à 10 H 00",
        "lieu_ouverture_plis": "Rabat",
        "region": "Rabat-Salé-Kénitra"
    }
]

# Generate 20+ AOs to ensure we meet the "≥ 20 AO" requirement
aos = []
for i in range(25):
    base = base_aos[i % 2].copy()
    base["numero_ordre"] = f"{base['numero_ordre']}-{i+1}"
    base["estimation_mad"] = f"{random.randint(100, 999)} 000,00 DHS"
    aos.append(base)

for ao in aos:
    req = urllib.request.Request(api_url_ao, data=json.dumps(ao).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            print(f"AO injecté : {res.get('id')} - {res.get('numero_ordre')} ({res.get('action')})")
    except urllib.error.HTTPError as e:
        print(f"Erreur HTTP: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print("Erreur:", e)
    time.sleep(0.1)
