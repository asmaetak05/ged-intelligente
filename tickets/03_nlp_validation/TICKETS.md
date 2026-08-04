# 03 — Structuration NLP et validation humaine

**Priorité du module : P1.** C'est le cœur métier : toute valeur doit rester reliée à la source qui la justifie.

## NLP-01 — Stabiliser le schéma des champs métier

**État : Partiel.** `nlp/extract_entities.py` extrait de nombreux champs, avec des scores constants ; `backend/models.py` et l'API utilisent plusieurs noms pour les montants et dates.

### Réalisation attendue

1. Créer `docs/REFERENTIEL_CHAMPS_METIER.md` avec nom canonique, type, règles de normalisation, exemples FR/AR et caractère obligatoire.
2. Définir le noyau MVP : `numero_appel_offre`, `reference`, `objet`, `organisme_acheteur`, `date_parution`, `date_limite`, `montant_estimatif_mad`, `caution_provisoire_mad`, `delai_execution_mois`, `ville`, `region`, `qualification`, `agrement`.
3. Aligner `backend/models.py`, `backend/schemas/`, `nlp/extract_entities.py` et React sur ces noms canoniques.
4. Conserver séparément valeur brute et valeur normalisée.
5. Écrire les migrations nécessaires sans casser les données existantes.

### Critères d'acceptation

- un dictionnaire de données unique remplace les synonymes concurrents ;
- chaque champ a un type validé ;
- les nulls sont distingués des zéros et des valeurs inconnues.

## NLP-02 — Rendre l'extraction explicable et testable

**État : Partiel.** Les expressions régulières et spaCy existent, mais plusieurs scores sont des constantes de code et l'extraction arabe n'est pas démontrée.

### Réalisation attendue

1. Découper `nlp/extract_entities.py` en extracteurs par champ dans `nlp/extractors/`.
2. Chaque extracteur doit retourner : valeur brute, valeur normalisée, page, extrait, méthode, version de règle et statut de confiance.
3. Remplacer les scores décoratifs par une logique documentée : solidité du pattern, cohérence de contexte, validation référentiel ; sinon afficher `score_indisponible`.
4. Ajouter règles et tests FR/AR/bilingues dans `tests/nlp/`.
5. Ne pas invoquer spaCy si le modèle n'est pas installé : produire une dégradation explicitement tracée.

### Critères d'acceptation

- chaque valeur de fiche possède un extrait justificatif ;
- les règles critiques disposent de tests positifs et négatifs ;
- les limites arabes sont affichées dans la documentation ;
- l'absence du modèle spaCy ne fait pas tomber le pipeline.

## NLP-03 — Créer la revue et correction humaine

**État : À faire.** Le frontend montre les informations NLP mais ne propose pas de cycle complet accepter/corriger/rejeter.

### Réalisation attendue

1. Ajouter modèles/migrations `field_validations` et `field_corrections` : valeur initiale, valeur corrigée, décision, commentaire, utilisateur, date.
2. Créer routes sécurisées : liste de champs à vérifier, accepter, corriger, rejeter, historique.
3. Ajouter `frontend-react/src/components/ExtractionReview.jsx` et intégrer la revue dans `DocumentDetail.jsx`.
4. Afficher le document/page/extrait à côté du formulaire de validation.
5. Tracer toutes les décisions dans `AuditEvent`.
6. Ajouter tests API et tests React des trois décisions.

### Critères d'acceptation

- un analyste peut corriger un montant sans modifier l'original ;
- l'ancienne valeur reste consultable ;
- seules les personnes autorisées peuvent valider ;
- une correction est visible dans la fiche et l'audit.

## NLP-04 — Mesurer la qualité des extractions

**État : À faire.** Aucun protocole précision/rappel/F1 par champ.

### Réalisation attendue

1. Construire un jeu de référence issu des corrections humaines, versionné et anonymisé si nécessaire.
2. Créer `scripts/evaluate_nlp.py` avec précision, rappel et F1 par champ, langue et type de document.
3. Produire `docs/metrics/NLP_BASELINE.md`.
4. Définir les seuils : publication automatique, revue humaine, champ absent.

### Critères d'acceptation

- une extraction peut être comparée à une vérité terrain ;
- les métriques sont reproductibles et ne mélangent pas entraînement/démonstration ;
- le dashboard affiche la complétude et le taux de correction, non une « précision » inventée.

