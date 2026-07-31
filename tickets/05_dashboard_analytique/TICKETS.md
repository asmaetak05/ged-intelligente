# 05 — Dashboard analytique et indicateurs de qualité

**Priorité du module : P1.** Chaque chiffre doit être calculé, défini et relié à son périmètre.

## ANA-01 — Définir et fiabiliser les KPI

**État : Partiel.** Des endpoints analytics existent dans `backend/main.py` et `Dashboard.jsx`, mais l'audit antérieur relevait des valeurs historiques/hardcodées et des définitions incomplètes.

### Réalisation attendue

1. Créer `docs/DICTIONNAIRE_KPI.md` : formule, source, filtres, fraîcheur, nullabilité, propriétaire pour chaque indicateur.
2. Auditer `get_dashboard`, `get_kpis`, `get_trends`, `get_delai_moyen`, `get_categories_distribution`, `get_top_buyers`.
3. Remplacer toute valeur de démonstration par une requête SQLAlchemy/repository testée.
4. Afficher `non disponible` au lieu de zéro lorsqu'une donnée manque.
5. Ajouter filtres temporels et cohérence entre dashboard, liste et export.

### Critères d'acceptation

- chaque carte KPI indique sa formule et sa période ;
- modifier un jeu de fixtures modifie les résultats attendus ;
- aucune valeur fixe de démo ne subsiste dans le dashboard.

## ANA-02 — Ajouter des indicateurs de qualité de pipeline

**État : À faire.** Le dashboard est surtout financier ; la qualité OCR/NLP et les échecs sont insuffisamment exposés.

### Réalisation attendue

1. Ajouter endpoints/repository : taux de jobs terminés, échecs par étape, durée moyenne, documents à vérifier, complétude par champ, corrections humaines, disponibilité source.
2. Créer `frontend-react/src/components/DataQualityDashboard.jsx` ou une section dédiée dans `Dashboard.jsx`.
3. Ajouter drill-down vers la liste des documents en erreur ou à revoir.
4. Documenter la différence entre confiance OCR technique, taux de complétude et F1 mesuré.

### Critères d'acceptation

- un administrateur peut identifier les documents bloqués ;
- un analyste voit les dossiers nécessitant correction ;
- aucun score de confiance n'est interprété abusivement comme qualité métier globale.

## ANA-03 — Tester agrégations et performance

**État : Partiel.** `tests/test_analytics.py` existe, mais le fonctionnement global des tests n'est pas vérifié et les volumes cibles ne sont pas définis.

### Réalisation attendue

1. Préparer fixtures déterministes avec organismes, régions, catégories, montants et dates.
2. Couvrir somme, moyenne, regroupement, période vide, valeurs nulles, pagination et droits d'accès.
3. Ajouter index de base adaptés aux filtres les plus utilisés après mesure.
4. Créer un script de benchmark sur 100, 1 000 puis 10 000 dossiers synthétiques non sensibles.
5. Documenter les limites et objectifs de réponse.

### Critères d'acceptation

- les calculs sont vérifiés par tests ;
- les endpoints ne régressent pas au-delà du seuil défini sur le jeu de benchmark ;
- les graphiques restent lisibles pour une période vide ou de grands nombres.

