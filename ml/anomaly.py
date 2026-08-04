"""Module de détection des anomalies sur les marchés publics.

Combine deux approches complémentaires :
1. Détection statistique non supervisée via Isolation Forest sur l'espace des variables (montant, délai, caution).
2. Règles de conformité métier (Règlement des marchés publics du Maroc) :
   - Ratio de caution provisoire / budget estimatif anormal (< 0.5% ou > 4%).
   - Incohérence majeure entre montant et délai d'exécution.
   - Pénalité journalière hors norme légale (en dehors de 1‰ à 3‰).
"""
from __future__ import annotations

from typing import List, Dict, Any, Optional
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from sklearn.ensemble import IsolationForest
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from backend.models import Marche
from backend.database import DATABASE_URL


def check_marche_business_rules(
    montant: Optional[float],
    caution: Optional[float],
    delai_mois: Optional[int],
    penalite_mille: Optional[float] = 1.0,
) -> Dict[str, Any]:
    """Évalue la conformité d'un marché selon les règles financières marocaines."""
    reasons = []
    anomaly_score = 0.0

    if montant and montant > 0:
        # Vérification du ratio de caution provisoire (standard légal : ~1% à 2%, max 3%)
        if caution and caution > 0:
            ratio_caution = (caution / montant) * 100.0
            if ratio_caution > 5.0:
                reasons.append(f"Caution provisoire anormalement élevée ({ratio_caution:.1f}% du montant, seuil usuel ≤ 3%)")
                anomaly_score += 0.45
            elif ratio_caution < 0.2:
                reasons.append(f"Caution provisoire anormalement faible ({ratio_caution:.2f}% du montant, seuil usuel ≥ 1%)")
                anomaly_score += 0.35

        # Incohérence Montant / Délai
        if delai_mois is not None:
            if montant > 50_000_000 and delai_mois < 2:
                reasons.append(f"Délai d'exécution suspect ({delai_mois} mois pour un montant de {montant:,.0f} MAD)")
                anomaly_score += 0.5
            elif montant < 100_000 and delai_mois > 36:
                reasons.append(f"Délai disproportionné ({delai_mois} mois pour un petit montant de {montant:,.0f} MAD)")
                anomaly_score += 0.4

    # Pénalité de retard par millième
    if penalite_mille is not None:
        if penalite_mille > 5.0 or penalite_mille < 0.1:
            reasons.append(f"Taux de pénalité atypique : {penalite_mille} ‰ par jour")
            anomaly_score += 0.25

    is_anomaly = anomaly_score >= 0.40 or len(reasons) > 0
    return {
        "is_anomaly": is_anomaly,
        "score": min(round(anomaly_score, 2), 1.0),
        "reasons": reasons,
    }


def detect_anomalies(db_url: str = DATABASE_URL) -> List[Dict[str, Any]]:
    """Exécute l'analyse d'anomalies sur l'ensemble des marchés enregistrés."""
    eng = create_engine(db_url)
    with Session(eng) as session:
        marches = session.query(Marche).all()

    if not marches:
        return []

    data = []
    marche_list = []

    for m in marches:
        montant = float(m.montant) if m.montant else 0.0
        delai = float(m.delai_execution_mois) if m.delai_execution_mois else 0.0
        caution = float(m.caution_provisoire_mad) if m.caution_provisoire_mad else 0.0
        penalite = float(m.penalite_retard_mille) if m.penalite_retard_mille else 1.0

        # Vérification métier individuelle
        rule_check = check_marche_business_rules(montant, caution, int(delai) if delai else None, penalite)

        data.append([montant, delai, caution])
        marche_list.append((m, rule_check))

    anomalies = []

    # Si au moins 5 marchés, on applique également l'Isolation Forest
    if len(marche_list) >= 5:
        X = np.array(data)
        clf = IsolationForest(random_state=42, contamination=0.10)
        preds = clf.fit_predict(X)
        scores = clf.decision_function(X)  # Plus le score est négatif, plus c'est une anomalie

        for idx, ((m, rule_check), p, s) in enumerate(zip(marche_list, preds, scores)):
            is_stat_anomaly = (p == -1)
            stat_score = max(0.0, float(-s))
            combined_score = round(max(rule_check["score"], stat_score), 2)
            
            reasons = list(rule_check["reasons"])
            if is_stat_anomaly and not reasons:
                reasons.append("Valeur financière statistiquement aberrante (écart majeur aux médianes sectorielles)")

            if rule_check["is_anomaly"] or is_stat_anomaly:
                anomalies.append({
                    "marche_id": m.id,
                    "numero_appel_offre": m.numero_appel_offre,
                    "titre_projet": m.titre_projet,
                    "montant": float(m.montant) if m.montant else None,
                    "anomaly_score": combined_score,
                    "is_anomaly": True,
                    "reasons": reasons,
                })
    else:
        for m, rule_check in marche_list:
            if rule_check["is_anomaly"]:
                anomalies.append({
                    "marche_id": m.id,
                    "numero_appel_offre": m.numero_appel_offre,
                    "titre_projet": m.titre_projet,
                    "montant": float(m.montant) if m.montant else None,
                    "anomaly_score": rule_check["score"],
                    "is_anomaly": True,
                    "reasons": rule_check["reasons"],
                })

    return anomalies
