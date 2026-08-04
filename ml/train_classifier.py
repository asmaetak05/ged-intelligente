"""Entraînement et calibration du classifieur NLP des marchés publics marocains.

Catégories cibles :
- Travaux (routes, terrassements, ponts, bâtiments, assainissement, barrages)
- Fournitures (équipements, véhicules, matériel informatique, mobilier, pièces)
- Services (gardiennage, nettoyage, maintenance, transport, télécoms)
- Études (maîtrise d'œuvre, contrôle technique, études géotechniques, topographie, architecture)
"""
from __future__ import annotations

import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from ml.features import get_tfidf_vectorizer, extract_text_feature
from backend.models import Marche
from backend.database import DATABASE_URL

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
CLASSIFIER_PATH = os.path.join(MODELS_DIR, "classifier.joblib")
METRICS_PATH = os.path.join(MODELS_DIR, "metrics.json")

# Dataset d'amorçage pour les marchés publics marocains
SEED_DATASET = [
    # Travaux
    ("Travaux de construction et d'élargissement de la voie express Rabat-Kénitra Direction des Routes", "Travaux"),
    ("Travaux de renforcement et de réhabilitation de la chaussée RN9 Direction Provinciale Ouarzazate", "Travaux"),
    ("Construction d'un pont en béton précontraint sur Oued Tensift Direction des Ouvrages d'Art", "Travaux"),
    ("Travaux de terrassement, assainissement et voirie pour la zone logistique Casablanca", "Travaux"),
    ("Construction d'un barrage collinaire pour la retenue des eaux de crue Province de Taroudant", "Travaux"),
    ("Travaux de dragage et confortement de la jetée du port de Safi Direction des Ports", "Travaux"),
    ("Réalisation des travaux de gros œuvres et étanchéité pour les locaux administratifs", "Travaux"),
    ("Travaux d'adduction en eau potable et pose de canalisations Direction de l'Hydraulique", "Travaux"),

    # Fournitures
    ("Acquisition de véhicules utilitaires et camions citernes pour le parc régional", "Fournitures"),
    ("Fourniture et installation d'équipements informatiques, serveurs et baies de stockage DSI", "Fournitures"),
    ("Achat de matériel de mesure hydrologique et stations météo automatiques", "Fournitures"),
    ("Fourniture de liants bitumineux et enrobés à chaud pour l'entretien routier", "Fournitures"),
    ("Acquisition de mobilier de bureau et équipement pour les délégations provinciales", "Fournitures"),
    ("Fourniture de logiciels de cartographie SIG et licences d'exploitation", "Fournitures"),
    ("Achat d'équipements de sécurité maritime et balisage portuaire", "Fournitures"),

    # Services
    ("Prestations de gardiennage et sécurité des bâtiments et locaux du ministère", "Services"),
    ("Nettoyage, hygiène et entretien des locaux des directions régionales et centrales", "Services"),
    ("Maintenance préventive et corrective du parc de climatisation et groupes électrogènes", "Services"),
    ("Services de transport du personnel et location de véhicules avec chauffeurs", "Services"),
    ("Prestations d'hébergement cloud, infogérance et sauvegarde sécurisée", "Services"),
    ("Assurance tous risques chantiers et flotte automobile du ministère", "Services"),

    # Études
    ("Étude d'impact environnemental et social pour le projet de dédoublement autoroutier", "Études"),
    ("Mission de maîtrise d'œuvre et suivi des travaux de construction du viaduc", "Études"),
    ("Études géotechniques, sondages et essais en laboratoire pour les fondations du barrage", "Études"),
    ("Étude hydrologique et modélisation hydraulique du bassin versant de Sebou", "Études"),
    ("Assistance technique et ordonnancement, pilotage et coordination (OPC) du chantier", "Études"),
    ("Étude d'opportunité et schéma directeur de développement du réseau routier rural", "Études"),
    ("Contrôle technique des structures et vérification des notes de calcul génie civil", "Études"),
]


def train_category_classifier(db_url: str = DATABASE_URL) -> bool:
    """Entraîne ou ré-entraîne le classifieur de catégories et sauvegarde les artefacts."""
    os.makedirs(MODELS_DIR, exist_ok=True)

    X, y = [], []

    # 1. Charger les données réelles de la base
    try:
        eng = create_engine(db_url)
        with Session(eng) as session:
            marches = session.query(Marche).filter(Marche.categorie_prestation.isnot(None)).all()
            for m in marches:
                feat = extract_text_feature(m)
                if feat:
                    X.append(feat)
                    y.append(m.categorie_prestation.value)
    except Exception as e:
        print(f"Warning: Impossible de lire la BDD ({e}), utilisation du jeu de données synthétique.")

    # 2. Compléter avec le seed dataset marocain pour la robustesse
    for text, label in SEED_DATASET:
        X.append(text.lower())
        y.append(label)

    # 3. Séparation apprentissage / test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    # 4. Pipeline TF-IDF + Régression Logistique calibrée
    pipeline = Pipeline([
        ('tfidf', get_tfidf_vectorizer()),
        ('clf', LogisticRegression(C=1.0, max_iter=1000, random_state=42))
    ])

    pipeline.fit(X_train, y_train)

    # 5. Évaluation des métriques
    y_pred = pipeline.predict(X_test)
    accuracy = float(accuracy_score(y_test, y_pred))
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

    metrics = {
        "accuracy": accuracy,
        "sample_count": len(X),
        "classes": list(set(y)),
        "report": report,
    }

    # 6. Sauvegarde du modèle et des métriques
    joblib.dump(pipeline, CLASSIFIER_PATH)
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    print(f"[OK] Modele ML entraine sur {len(X)} echantillons (Precision test : {accuracy*100:.1f}%).")
    print(f"[INFO] Modele sauvegarde dans {CLASSIFIER_PATH}")
    return True


if __name__ == "__main__":
    train_category_classifier()
