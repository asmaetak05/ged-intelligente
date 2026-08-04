"""Script de peuplement idempotent des tables de référence marocaines (BDD).

Seede les référentiels officiels :
- Types d'avis
- Types de procédures
- États des avis
- Arborescence des Directions du Ministère
- Villes et Régions avec coordonnées GPS
- Qualifications BTP officielles (Classes 1 à 5)
- Agréments des bureaux d'études
"""
from __future__ import annotations

import sys
import os

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from backend.database import SessionLocal, engine, Base
from backend.models import (
    TypeAvis,
    TypeProcedure,
    EtatAvis,
    Direction,
    Ville,
    Qualification,
    Agrement,
    Role,
    Permission,
)


def seed_reference_data():
    """Peuple la base de données avec les données de référence officielles."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("🌱 Début du peuplement des tables de référence...")

        # 1. Types d'Avis
        types_avis = [
            ("AO_OUVERT", "Avis d'appel d'offres ouvert"),
            ("AO_RESTREINT", "Avis d'appel d'offres restreint"),
            ("AO_PRESELECTION", "Avis d'appel d'offres avec présélection"),
            ("CONCOURS", "Avis de concours"),
            ("CONSULTATION_ARCHI", "Consultation architecturale"),
            ("AVIS_RECTIFICATIF", "Avis rectificatif"),
            ("AVIS_ANNULATION", "Avis d'annulation"),
        ]
        for code, label in types_avis:
            if not db.query(TypeAvis).filter_by(code=code).first():
                db.add(TypeAvis(code=code, label=label))
        db.commit()
        print(f"✅ Types d'avis vérifiés ({len(types_avis)} entrées).")

        # 2. Types de Procédure
        procedures = [
            ("PROC_OUVERTE", "Procédure ouverte (Rabais ou Majoration)"),
            ("PROC_OFFRE_PRIX", "Procédure sur offre de prix"),
            ("PROC_NEGOCIEE", "Procédure négociée avec publicité"),
            ("PROC_CONCOURS", "Procédure sur concours"),
            ("BON_COMMANDE", "Achat sur bon de commande"),
        ]
        for code, label in procedures:
            if not db.query(TypeProcedure).filter_by(code=code).first():
                db.add(TypeProcedure(code=code, label=label))
        db.commit()
        print(f"✅ Types de procédure vérifiés ({len(procedures)} entrées).")

        # 3. États d'Avis
        etats = [
            ("EN_COURS", "En cours de publication"),
            ("ATTRIBUE", "Marché attribué"),
            ("INFRUCTUEUX", "Appel d'offres infructueux"),
            ("ANNULE", "Procédure annulée"),
            ("REPORTE", "Date limite reportée"),
        ]
        for code, label in etats:
            if not db.query(EtatAvis).filter_by(code=code).first():
                db.add(EtatAvis(code=code, label=label))
        db.commit()
        print(f"✅ États d'avis vérifiés ({len(etats)} entrées).")

        # 4. Directions du Ministère
        directions_centrales = [
            ("Direction Générale des Routes (DGR)", "Centrale"),
            ("Direction Générale de l'Hydraulique (DGH)", "Centrale"),
            ("Direction des Ports et du Domaine Public Maritime (DPDPM)", "Centrale"),
            ("Direction des Affaires Techniques et des Relations avec la Profession (DATRP)", "Centrale"),
            ("Direction des Systèmes d'Information (DSI)", "Centrale"),
        ]
        for name, type_dir in directions_centrales:
            if not db.query(Direction).filter_by(name=name).first():
                db.add(Direction(name=name, type_dir=type_dir))
        db.commit()

        # Directions Régionales (DRE)
        regions_dre = [
            ("Direction Régionale de l'Équipement - Casablanca-Settat", "Régionale"),
            ("Direction Régionale de l'Équipement - Rabat-Salé-Kénitra", "Régionale"),
            ("Direction Régionale de l'Équipement - Tanger-Tétouan-Al Hoceïma", "Régionale"),
            ("Direction Régionale de l'Équipement - Marrakech-Safi", "Régionale"),
            ("Direction Régionale de l'Équipement - Fès-Meknès", "Régionale"),
            ("Direction Régionale de l'Équipement - Oriental", "Régionale"),
            ("Direction Régionale de l'Équipement - Souss-Massa", "Régionale"),
            ("Direction Régionale de l'Équipement - Béni Mellal-Khénifra", "Régionale"),
            ("Direction Régionale de l'Équipement - Drâa-Tafilalet", "Régionale"),
            ("Direction Régionale de l'Équipement - Guelmim-Oued Noun", "Régionale"),
            ("Direction Régionale de l'Équipement - Laâyoune-Sakia El Hamra", "Régionale"),
            ("Direction Régionale de l'Équipement - Dakhla-Oued Ed-Dahab", "Régionale"),
        ]
        for name, type_dir in regions_dre:
            if not db.query(Direction).filter_by(name=name).first():
                db.add(Direction(name=name, type_dir=type_dir))
        db.commit()
        print("✅ Directions centrales et régionales vérifiées.")

        # 5. Villes et Régions du Maroc (avec coordonnées GPS pour la cartographie)
        villes_maroc = [
            ("Rabat", "Rabat", "Rabat-Salé-Kénitra", 34.020882, -6.841650),
            ("Salé", "Salé", "Rabat-Salé-Kénitra", 34.053100, -6.798460),
            ("Kénitra", "Kénitra", "Rabat-Salé-Kénitra", 34.261010, -6.580200),
            ("Casablanca", "Casablanca", "Casablanca-Settat", 33.573110, -7.589843),
            ("Settat", "Settat", "Casablanca-Settat", 33.001030, -7.616620),
            ("El Jadida", "El Jadida", "Casablanca-Settat", 33.231630, -8.500710),
            ("Marrakech", "Marrakech", "Marrakech-Safi", 31.629472, -7.981084),
            ("Safi", "Safi", "Marrakech-Safi", 32.299380, -9.237180),
            ("Essaouira", "Essaouira", "Marrakech-Safi", 31.508490, -9.759500),
            ("Fès", "Fès", "Fès-Meknès", 34.018125, -5.007845),
            ("Meknès", "Meknès", "Fès-Meknès", 33.893520, -5.547270),
            ("Taza", "Taza", "Fès-Meknès", 34.213890, -4.010280),
            ("Tanger", "Tanger-Assilah", "Tanger-Tétouan-Al Hoceïma", 35.759465, -5.833954),
            ("Tétouan", "Tétouan", "Tanger-Tétouan-Al Hoceïma", 35.588890, -5.362550),
            ("Al Hoceïma", "Al Hoceïma", "Tanger-Tétouan-Al Hoceïma", 35.251650, -3.937240),
            ("Oujda", "Oujda-Angad", "Oriental", 34.681390, -1.908580),
            ("Nador", "Nador", "Oriental", 35.168130, -2.933520),
            ("Berkane", "Berkane", "Oriental", 34.920000, -2.320000),
            ("Agadir", "Agadir-Ida-Ou-Tanane", "Souss-Massa", 30.427755, -9.598107),
            ("Taroudant", "Taroudant", "Souss-Massa", 30.470280, -8.876950),
            ("Tiznit", "Tiznit", "Souss-Massa", 29.697400, -9.731620),
            ("Béni Mellal", "Béni Mellal", "Béni Mellal-Khénifra", 32.337250, -6.349830),
            ("Khénifra", "Khénifra", "Béni Mellal-Khénifra", 32.939440, -5.667500),
            ("Khouribga", "Khouribga", "Béni Mellal-Khénifra", 32.881080, -6.906300),
            ("Errachidia", "Errachidia", "Drâa-Tafilalet", 31.931940, -4.424440),
            ("Ouarzazate", "Ouarzazate", "Drâa-Tafilalet", 30.918940, -6.893410),
            ("Zagora", "Zagora", "Drâa-Tafilalet", 30.332410, -5.838380),
            ("Guelmim", "Guelmim", "Guelmim-Oued Noun", 28.986960, -10.057380),
            ("Tan-Tan", "Tan-Tan", "Guelmim-Oued Noun", 28.437990, -11.103210),
            ("Laâyoune", "Laâyoune", "Laâyoune-Sakia El Hamra", 27.125286, -13.162500),
            ("Boujdour", "Boujdour", "Laâyoune-Sakia El Hamra", 26.125830, -14.484720),
            ("Dakhla", "Oued Ed-Dahab", "Dakhla-Oued Ed-Dahab", 23.684770, -15.957980),
        ]
        for name, prov, reg, lat, lon in villes_maroc:
            if not db.query(Ville).filter_by(name=name).first():
                db.add(Ville(name=name, province=prov, region=reg, lat=lat, lon=lon))
        db.commit()
        print(f"✅ Villes et coordonnées GPS vérifiées ({len(villes_maroc)} villes).")

        # 6. Qualifications BTP officielles
        qualifs = [
            ("A1", "Terrassements généraux en grande masse", "Classe 1", "Terrassements"),
            ("A2", "Terrassements courants et préparatoires", "Classe 2", "Terrassements"),
            ("B1", "Ouvrages d'art exceptionnels (Ponts, Viaducs)", "Classe 1", "Ouvrages d'art"),
            ("B2", "Ouvrages d'art courants et dalots", "Classe 2", "Ouvrages d'art"),
            ("C1", "Chaussées autoroutières et voies expresses", "Classe 1", "Routes"),
            ("C2", "Revêtements et renforcement de chaussées", "Classe 2", "Routes"),
            ("D1", "Travaux maritimes et dragage", "Classe 1", "Ports & Maritime"),
            ("E1", "Bâtiments tous corps d'état", "Classe 1", "Bâtiment"),
            ("E2", "Gros œuvres et maçonnerie", "Classe 2", "Bâtiment"),
            ("F1", "Réseaux d'assainissement et adduction d'eau potable", "Classe 1", "Hydraulique"),
        ]
        for code, label, classe, cat in qualifs:
            if not db.query(Qualification).filter_by(code=code).first():
                db.add(Qualification(code=code, label=label, classe=classe, categorie=cat))
        db.commit()
        print(f"✅ Qualifications BTP vérifiées ({len(qualifs)} qualifications).")

        # 7. Agréments Bureaux d'Études
        agrements = [
            ("D1", "Études générales de structures et génie civil", "Bureaux d'études"),
            ("D2", "Études de ponts, viaducs et ouvrages d'art", "Bureaux d'études"),
            ("D3", "Études routières, autoroutières et de circulation", "Bureaux d'études"),
            ("D4", "Études géotechniques, forages et fondations", "Bureaux d'études"),
            ("D5", "Études hydrologiques, barrages et digues", "Bureaux d'études"),
            ("D6", "Études maritimes et portuaires", "Bureaux d'études"),
            ("D7", "Études d'impact sur l'environnement", "Environnement"),
        ]
        for code, label, type_agr in agrements:
            if not db.query(Agrement).filter_by(code=code).first():
                db.add(Agrement(code=code, label=label, type_agrement=type_agr))
        db.commit()
        print(f"✅ Agréments vérifiés ({len(agrements)} agréments).")

        print("🎉 Seeding des référentiels terminé avec succès !")

    except Exception as e:
        db.rollback()
        print(f"❌ Erreur lors du seeding : {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_reference_data()
