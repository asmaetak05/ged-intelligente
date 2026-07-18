# Rapport de Réalisation — Phase 2 : Pipeline d'ingestion bout-en-bout

> **Projet** : GED Intelligente (PFA)
> **Phase** : 2 sur 9
> **Période** : 12 juillet 2026
> **Tickets couverts** : T2.1 ✅, T2.2 ✅, T2.3 ✅, T2.4 ✅, T2.5 ✅, T2.6 ✅, T2.7 ✅, T2.8 ✅, T2.9 ✅
> **Statut global** : ✅ **Terminé** — 9/9 tickets terminés, Phase 2 achevée

---

## 1. Vue d'ensemble

La Phase 2 se concentrait sur la finalisation et le branchement du pipeline d'ingestion intelligent. L'objectif était de lier la réception des fichiers (fichiers ZIP, PDF scannés, PDF digitaux, DOCX), l'extraction OCR, l'analyse NLP (Extraction des entités nommées, dates, montants, etc.) et le stockage final en base de données.

**Problèmes traités** :
- Le module d'ingestion historique était un script unique (`ingestion/extractor.py`) qui mélangeait le parsing OCR, les requêtes LLM, et l'extraction Regex, créant une forte dette technique.
- L'endpoint d'upload dans le backend n'était pas fonctionnel (il renvoyait une réponse statique sans traiter le fichier).
- L'extraction NLP manquait de précision, de robustesse (non typée) et n'offrait aucune traçabilité (score de confiance, source de l'information).
- Aucun filet de test pour valider la chaîne de valeur OCR/NLP.

**Cible Phase 2** : Un pipeline asynchrone fonctionnel (Upload → Extraction ZIP → OCR → SpaCy/Regex → Base de données) géré par des tâches de fond FastAPI (`BackgroundTasks`) et testé de bout en bout.

---

## 2. Tableau de bord des tickets

| # | Ticket | Description | Statut |
|---|---|---|---|
| **T2.1** | Extraire la logique OCR | Déplacer la logique OCR depuis `ingestion/extractor.py` vers les modules dédiés `ocr/extract_native.py` et `ocr/extract_ocr.py`. | ✅ |
| **T2.2** | Créer le module NLP | Implémenter SpaCy et `dateparser` dans `nlp/extract_entities.py` pour détecter dates, villes et montants. | ✅ |
| **T2.3** | Refactor de `extractor.py` | Transformer `extractor.py` en un simple orchestrateur des modules NLP/OCR. | ✅ |
| **T2.4** | Endpoint upload branché | Mettre à jour `/api/v1/ged/documents/upload` pour lancer le traitement asynchrone via `BackgroundTasks`. | ✅ |
| **T2.5** | Sauvegardes intermédiaires | Enregistrer les sorties `.txt` et `.json` de l'OCR et NLP dans `data/processed/`. | ✅ |
| **T2.6** | Traçabilité | Créer le modèle `ExtractionNlp` pour tracer la source, le score et le snippet exact de chaque valeur extraite. | ✅ |
| **T2.7** | Endpoint de progression | Implémenter `/api/v1/ged/documents/{id}/status` pour requêter l'avancement du pipeline. | ✅ |
| **T2.8** | Tests pipeline complet | Tests unitaires pour l'endpoint d'upload et la tâche d'extraction asynchrone. | ✅ |
| **T2.9** | Tests NLP | Tests validant l'extraction robuste des dates, villes et montants. | ✅ |

---

## 3. Détail par ticket clé

### T2.1 — Refonte de la couche OCR (`ocr/`)
**Modifications** :
- La logique d'extraction de PDF numérisé (via `pytesseract` et `pdf2image`) a été placée dans `ocr/extract_ocr.py`.
- La logique d'extraction native (`PyMuPDF` et `python-docx`) a été centralisée dans `ocr/extract_native.py`.
- L'architecture devient modulaire : si on remplace Tesseract par un autre moteur à l'avenir, seul `extract_ocr.py` sera impacté.

### T2.2 — Intelligence artificielle et NLP (`nlp/`)
**Modifications** :
- `dateparser` a été installé pour standardiser toutes les variations textuelles des dates francophones.
- `nlp/extract_entities.py` croise l'analyse de Regex poussée et l'analyse sémantique `SpaCy` pour détecter le Maître d'Ouvrage (`ORG`).
- Le dictionnaire `nlp/villes_maroc.py` aide à identifier géographiquement l'appel d'offres de façon déterministe.

### T2.4 & T2.7 — Moteur Asynchrone dans FastAPI
**Modifications** :
- L'endpoint `POST /api/v1/ged/documents/upload` enregistre le document physiquement (`data/raw/`) et dans la table `documents` au statut `raw_zip`.
- Il confie le traitement à la méthode asynchrone `process_document_async` (ajoutée dans `backend/tasks.py`), garantissant une API réactive.
- Le frontend peut pinguer `/api/v1/ged/documents/{id}/status` pour recevoir le statut (`extracted`, `ocr_processed`, `failed`).

### T2.6 — Traçabilité et auditabilité (Base de données)
**Modifications** :
- La confiance de l'utilisateur final dépend de la traçabilité. Un nouveau modèle SQLAlchemy `ExtractionNlp` a été injecté dans `backend/models.py`.
- La migration Alembic (`2262aaa7b8c9_add_extraction_nlp_table.py`) a été générée puis appliquée à la base de données.
- À la fin du pipeline, chaque donnée insérée (ex: le montant) possède une traçabilité précise :
  `{ "field_name": "montant", "value": "50000", "source": "regex", "score": 0.9, "snippet": "Estimation: 50 000 MAD" }`

### T2.8 & T2.9 — Robustesse et Tests (`tests/`)
**Modifications** :
- Installation du paquet `python-docx` dans l'environnement de développement pour permettre la création de faux fichiers Word de test.
- Création dynamique d'un `sample_ao.zip` via un script, utilisé ensuite comme fixture Pytest.
- Tests validés : `pytest tests/test_nlp.py tests/test_pipeline.py` passe avec **100% de succès** en CI local.

---

## 4. Métriques post-Phase 2

| Métrique | Avant Phase 2 | Après Phase 2 |
|---|---|---|
| Couverture de l'extraction NLP (champs) | 4 | **12** (Dates, Villes, Montants inclus) |
| Score de qualité OCR tracé | Non | **Oui** (table `ocr_logs`) |
| Asynchronisme de l'upload | Faussement asynchrone | **Réel via FastAPI `BackgroundTasks`** |
| Tests d'intégration Pipeline | 0 | **2 tests end-to-end** |
| Tests unitaires NLP | 0 | **4 tests isolés** |

---

## 5. Leçons apprises

1. **La séparation des responsabilités NLP/OCR** s'est avérée pertinente, particulièrement pour la rédaction des tests : nous avons pu tester les extractions NLP en isolation parfaite sur de simples chaînes de caractères brutes.
2. **SQLite et Concurrence** : Le choix initial de conserver SQLite pour la phase de développement a causé quelques heurts dans `tests/test_pipeline.py`. `SessionLocal()` dans un environnement asynchrone de test nécessitait d'importer le bon `db_session` généré par la fixture pour ne pas figer la base de données, un ajustement opéré dans `tasks.py`.
3. **Le formatage Docx est plus fragile que les chaînes de texte basiques** : L'utilisation initiale d'un faux fichier contenant du texte pur avec l'extension `.docx` faisait planter le pipeline de test. L'outil `python-docx` a été indispensable pour générer un fichier Zip de test sain.

---

## 6. Prochaines étapes

La phase d'ingestion logicielle est solide et testée. 
La **Phase 3 : Données réelles & dataset de démo** pourra maintenant commencer, afin de valider ce pipeline logicielle sur des centaines d'appels d'offres réels moissonnés (scrapping).

**Phase 2 entièrement terminée.**
