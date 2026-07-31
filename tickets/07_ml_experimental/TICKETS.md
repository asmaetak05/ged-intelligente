# 07 — ML expérimental et signaux d'anomalie

**Priorité du module : P2.** Ne commencer qu'après OCR/NLP, correction humaine et corpus annoté. Ce module est présenté comme expérimental tant qu'il n'est pas évalué.

## ML-01 — Construire un dataset d'apprentissage défendable

**État : À faire.** `ml/train_classifier.py` entraîne un SVM dès cinq dossiers ; la base observée contient seulement six insights ML, ce qui est insuffisant pour une validation sérieuse.

### Réalisation attendue

1. Définir la tâche exacte : par exemple catégorie de prestation, avec liste de classes stable et définition de chaque classe.
2. Exporter un dataset depuis les corrections humaines avec identifiant, texte autorisé, label, date, source et version.
3. Prévoir un minimum par classe et rejeter l'entraînement lorsqu'une classe est insuffisante.
4. Créer splits train/validation/test stratifiés, figés et non recouvrants.
5. Ajouter `docs/ML_DATASET_CARD.md` : origine, biais, langue, limites, transformations et droits d'usage.

### Critères d'acceptation

- aucun document de test ne se retrouve dans l'entraînement ;
- le dataset et ses splits sont versionnés ;
- le système refuse explicitement un entraînement insuffisant.

## ML-02 — Corriger le protocole de classification

**État : Partiel mais non validé.** Le SVM TF-IDF est un bon baseline, cependant lorsque moins de dix éléments sont présents, le code évalue sur les mêmes données que l'entraînement.

### Réalisation attendue

1. Modifier `ml/train_classifier.py` : supprimer le fallback train=test ; imposer split stratifié ou validation croisée.
2. Comparer une baseline règles/mots-clés, une régression logistique et le SVM existant.
3. Ajouter précision, rappel, F1 macro, F1 par classe et matrice de confusion.
4. Sérialiser avec le modèle : version code, hash dataset, classes, date, paramètres et métriques dans `ml/models/metadata.json`.
5. Modifier `ml/predict.py` pour retourner `non_disponible` si aucun modèle validé n'est présent.
6. Ajouter `tests/test_ml_evaluation.py` avec petit dataset synthétique.

### Critères d'acceptation

- aucun score n'est calculé sur les données d'entraînement ;
- la métrique affichée dans React provient des métadonnées du modèle ;
- une prédiction incertaine est présentée comme suggestion et non vérité.

## ML-03 — Repenser les anomalies comme signaux explicables

**État : Partiel mais non validé.** `ml/anomaly.py` utilise `IsolationForest(contamination=0.05)` sur montant/délai/caution et remplace les valeurs manquantes par zéro.

### Réalisation attendue

1. Ne jamais remplacer une valeur manquante par zéro ; exclure, imputer explicitement ou déclarer donnée insuffisante.
2. Créer d'abord `ml/business_rules.py` : ratios et seuils discutés avec un référent métier, avec explication lisible.
3. Garder Isolation Forest uniquement comme second signal ; ajouter score, variables utilisées, version et raison affichable.
4. Ajouter une décision analyste : confirmé, faux positif, à investiguer.
5. Mesurer précision des alertes sur un échantillon validé et afficher le taux de faux positifs.

### Critères d'acceptation

- une alerte indique pourquoi elle est générée ;
- aucune anomalie n'est assimilée à une non-conformité ;
- l'interface permet de corriger le signal ;
- le dashboard distingue règles métier et modèle statistique.

## ML-04 — Encadrer le réentraînement

**État : Partiel/risqué.** `/api/v1/ml/retrain` déclenche un sous-processus depuis l'API.

### Réalisation attendue

1. Déplacer le réentraînement dans le système de jobs du module ingestion, réservé à l'administrateur fonctionnel/technique.
2. Exiger validation des données et un seuil minimal avant lancement.
3. Ajouter journal de run : utilisateur, dataset, version, durée, métriques, modèle produit, succès/échec.
4. Permettre promotion/retour à la version précédente ; ne jamais remplacer silencieusement un modèle actif.
5. Ajouter interface de suivi dans `PredictorML.jsx` uniquement après les métriques réelles.

### Critères d'acceptation

- aucun `subprocess` ML n'est lancé sans job persisté et autorisation ;
- chaque modèle actif est identifiable et réversible ;
- la soutenance peut montrer les métriques et les limites du modèle.

