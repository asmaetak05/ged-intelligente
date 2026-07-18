# Phase 8 — Documentation & livrables

> **Effort** : 1,5 journée · **Risque** : faible · **Pré-requis** : Phases 1–7 terminées (démo fonctionnelle)

---

## T8.1 — `docs/installation.md`

**Description & objectif** : un externe peut cloner le repo et reproduire la démo en < 15 min.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `docs` | `MODIFY` | `docs/installation.md` (vide actuellement) :<br>1. **Prérequis** : Python 3.11+, Node 20+, Tesseract (apt: `tesseract-ocr tesseract-ocr-fra tesseract-ocr-ara`), poppler-utils, PostgreSQL 15 (optionnel).<br>2. **Cloner** : `git clone ... && cd ged-intelligente`<br>3. **Backend** :<br>   ```bash<br>   python -m venv .venv && source .venv/bin/activate<br>   pip install -r requirements.txt<br>   playwright install chromium<br>   python -m spacy download fr_core_news_sm<br>   ```<br>4. **Base de données** :<br>   ```bash<br>   # Option A : SQLite (par défaut)<br>   export DATABASE_URL=sqlite:///./ged.db<br>   alembic upgrade head<br>   # Option B : PostgreSQL via Docker<br>   docker compose up -d db<br>   export DATABASE_URL=postgresql://admin:password@localhost:5432/ged_db<br>   alembic upgrade head<br>   ```<br>5. **Données de démo** :<br>   ```bash<br>   python scripts/populate_db.py<br>   python -m ml.train_classifier<br>   ```<br>6. **Lancer l'API** :<br>   ```bash<br>   uvicorn backend.main:app --reload<br>   # API : http://localhost:8000<br>   # Docs : http://localhost:8000/docs<br>   ```<br>7. **Frontend** :<br>   ```bash<br>   cd frontend-react && npm install && npm run dev<br>   # UI : http://localhost:5173<br>   # ou build production servi par FastAPI sur /app/<br>   ```<br>8. **Tests** : `bash scripts/run_all_tests.sh` |

**Plan de vérification** :
- [ ] Un collègue qui suit la doc parvient à lancer la démo.
- [ ] Tous les chemins de fichiers sont valides.
- [ ] Les versions Python/Node sont précisées.

---

## T8.2 — `docs/user_guide.md`

**Description & objectif** : guide pas-à-pas pour utiliser l'application.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `docs` | `NEW` | `docs/user_guide.md` (≈ 200 lignes) :<br>1. **Dashboard** : ouvrir `/app/`, voir les 4 KPIs, top acheteurs, graphiques.<br>2. **Recherche** : barre de recherche + filtres (ville, organisme, catégorie, date).<br>3. **Détail** : cliquer sur un résultat → voir champs, texte OCR, extractions.<br>4. **Upload** : drag-and-drop un ZIP, suivre la progression, voir le document dans la liste.<br>5. **ML** : panneau "Prédictions" → liste des anomalies, possibilité de relancer un entraînement.<br>6. **Monitoring** : page `/monitoring` → uptime API, taille BDD, logs.<br>7. **Captures d'écran** (à intégrer) : 8–10 images annotées. |
| `docs` | `NEW` | `docs/images/` (dossier) avec captures d'écran. |
| `docs` | `NEW` | `docs/images/README.md` : légende de chaque capture. |

**Plan de vérification** :
- [ ] Le guide couvre les 5 écrans principaux.
- [ ] Chaque étape est illustrée par une capture.
- [ ] Un utilisateur novice peut compléter un parcours complet sans aide.

---

## T8.3 — `docs/architecture.md`

**Description & objectif** : expliquer les choix techniques.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `docs` | `NEW` | `docs/architecture.md` (≈ 300 lignes) :<br>1. **Vue d'ensemble** : schéma ASCII des 4 couches<br>2. **L1 — Collecte & OCR** : Playwright (pourquoi), PyMuPDF + Tesseract (pourquoi)<br>3. **L2 — NLP & ETL** : spaCy (pourquoi fr_core_news_sm), dateparser, regex vs LLM<br>4. **L3 — Backend** : FastAPI (pourquoi), SQLAlchemy (pourquoi), FTS (SQLite vs PostgreSQL)<br>5. **L4 — Frontend & ML** : React + Vite + Recharts, TF-IDF + LinearSVC + IsolationForest<br>6. **Décisions alternatives écartées** :<br>   - Pourquoi pas GPT pour tout ? (coût, latence, déterminisme)<br>   - Pourquoi pas PostgreSQL FTS GIN ? (gains marginaux à 30 AO)<br>   - Pourquoi pas un ETL (Airflow, Dagster) ? (overkill POC) |

**Plan de vérification** :
- [ ] Tous les choix sont justifiés.
- [ ] Le schéma ASCII est lisible en Markdown.

---

## T8.4 — Compléter `docs/realisations/`

**Description & objectif** : un README par module, daté.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `docs` | `MODIFY` | `docs/realisations/module_ingestion/README.md` : ajouter date, statut (✅ / ⚠️), points clés, points d'amélioration. |
| `docs` | `MODIFY` | `docs/realisations/module_backend/README.md` : idem. |
| `docs` | `MODIFY` | `docs/realisations/module_frontend/README.md` : idem. |
| `docs` | `MODIFY` | `docs/realisations/module_ia/README.md` : idem (refactor après Phase 6). |
| `docs` | `NEW` | `docs/realisations/README.md` : index des 4 modules. |

**Plan de vérification** :
- [ ] Chaque module a un README à jour.

---

## T8.5 — `README.md` racine

**Description & objectif** : point d'entrée visible.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `repo` | `MODIFY` | `README.md` :<br>1. **Titre + tagline** : "GED Intelligente — Transformation des marchés publics en base exploitable"<br>2. **Badges** : coverage, build, Python version<br>3. **GIF démo** (à capturer) : dashboard en action<br>4. **Architecture** : miniature du schéma<br>5. **Quickstart** : 5 lignes pour lancer<br>6. **Documentation** : liens vers `installation.md`, `user_guide.md`, `architecture.md`<br>7. **Stack** : liste des technologies<br>8. **Statut** : "MVP validé, développement en cours"<br>9. **Auteur** : nom, encadrant, école |

**Plan de vérification** :
- [ ] Le README est lisible sur GitHub sans rendu Markdown.
- [ ] Le GIF de démo est lisible (taille < 5 Mo).

---

## T8.6 — Rapport de stage

**Description & objectif** : livrable central de l'évaluation.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `docs` | `NEW` | `docs/Rapport_Stage.pdf` (30–50 pages) :<br>1. **Introduction** (1 p.)<br>2. **Contexte et problématique** (3 p.)<br>3. **État de l'art** (5 p.) : OCR, NLP, FTS, BI, ML<br>4. **Conception** (8 p.) : architecture, choix techniques, schéma BDD<br>5. **Réalisation** (15 p.) : screenshots, code snippets, métriques<br>6. **Résultats** (5 p.) : 30 AO ingérés, taux OCR 87 %, accuracy ML 92 %<br>7. **Discussion** (3 p.) : limites, écarts vs plan initial, justifications<br>8. **Conclusion et perspectives** (2 p.)<br>9. **Bibliographie** (1 p.)<br>10. **Annexes** (5 p.) : extraits de logs, captures, scripts |
| `docs` | `NEW` | `docs/Rapport_Stage.md` (version source Markdown) |

**Plan de vérification** :
- [ ] Le PDF est généré sans erreur (pandoc ou équivalent).
- [ ] Le rapport est relu (zéro faute), signé, daté.

---

## T8.7 — Slides de soutenance

**Description & objectif** : support visuel pour la présentation.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `docs` | `NEW` | `docs/Slides_Soutenance.pdf` (12–15 slides) :<br>1. **Titre** : nom, école, encadrant, date<br>2. **Pitch** (30 s) : "GED Intelligente transforme des PDF non structurés en base SQL exploitable, avec BI et ML."<br>3. **Contexte** : volumes, problème<br>4. **Démo 1** : Dashboard (KPIs réels)<br>5. **Démo 2** : Recherche + détail document<br>6. **Démo 3** : Upload → OCR → DB en live<br>7. **Démo 4** : ML (prédictions + anomalies)<br>8. **Architecture** : schéma 4 couches<br>9. **Stack technique**<br>10. **Résultats** : chiffres clés<br>11. **Limites assumées**<br>12. **Perspectives**<br>13. **Bilan personnel**<br>14. **Q&R** |
| `docs` | `NEW` | `docs/Slides_Soutenance.md` (source) ou `.pptx` |

**Plan de vérification** :
- [ ] 12–15 slides, format 16:9.
- [ ] Démos capturées (pas de live risqué).
- [ ] Le pitch tient en 30 s (chronométré).

---

## T8.8 — Scénario de démo

**Description & objectif** : un script minute par minute.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `docs` | `NEW` | `docs/Scenario_Demo.md` (≈ 50 lignes) :<br>```markdown<br># Scénario démo — 5 minutes<br>## 0:00–0:30 — Pitch<br>- Slide 2<br>- Dire : "Voici la démo..."<br>## 0:30–1:30 — Dashboard<br>- Ouvrir /app/<br>- Montrer les 4 KPIs<br>- Montrer le top 10 acheteurs<br>## 1:30–2:30 — Recherche<br>- Taper "route" → 5 résultats<br>- Filtrer par ville "Casablanca"<br>- Cliquer sur le 1er → détail<br>## 2:30–3:30 — Détail document<br>- Montrer le texte OCR<br>- Montrer les extractions avec score<br>## 3:30–4:30 — Upload live<br>- Drag-drop un ZIP de data/samples/<br>- Suivre la progression (raw_zip → ocr_processed)<br>- Voir le nouveau AO dans la liste<br>## 4:30–5:00 — ML<br>- Ouvrir PredictorML.jsx<br>- Montrer les anomalies détectées<br>- Lancer un retrain<br>``` |

**Plan de vérification** :
- [ ] Le scénario est chronométré (≤ 5 min).
- [ ] Chaque action correspond à un écran ou endpoint précis.
- [ ] Le binôme sait qui parle et qui clique à chaque instant.

---

## T8.9 — `CHANGELOG.md` final

**Description & objectif** : historique du projet.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `docs` | `MODIFY` | `docs/CHANGELOG.md` : ajouter une entrée récapitulative pour chaque phase (0 à 9), avec date et livrables. |

**Plan de vérification** :
- [ ] Le changelog est lisible et couvre l'ensemble des phases.

---

## ✅ Critères de sortie de la Phase 8

- [ ] `docs/installation.md` permet de relancer le projet from scratch.
- [ ] `docs/user_guide.md` couvre tous les écrans.
- [ ] `docs/architecture.md` justifie tous les choix.
- [ ] `Rapport_Stage.pdf` (30–50 p.) est relu et finalisé.
- [ ] `Slides_Soutenance.pdf` (12–15 slides) est prêt.
- [ ] `Scenario_Demo.md` est chronométré ≤ 5 min.
- [ ] `README.md` est l'attractif de la page GitHub.

**Effort total** : 1,5 jour ouvré.
