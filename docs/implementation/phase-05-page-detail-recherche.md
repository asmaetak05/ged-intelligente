# Phase 5 — Page détail document & recherche enrichie

> **Effort** : 1 journée · **Risque** : faible · **Pré-requis** : Phase 4 terminée

---

## T5.1 — Endpoint détail marché

**Description & objectif** : permettre au frontend d'afficher la fiche complète d'un AO (champs + texte OCR + fichier source).

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `backend` | `MODIFY` | `backend/main.py` : `GET /api/v1/ged/appels-offres/{numero_ordre}` retourne :<br>```json<br>{<br>  "marche": { ... tous les champs ... },<br>  "ocr": {<br>    "raw_text": "...",<br>    "confidence": 87.3,<br>    "engine": "Tesseract 5",<br>    "processed_at": "..."<br>  },<br>  "document": {<br>    "filename": "...",<br>    "storage_path": "data/raw/AO_001.zip",<br>    "size_kb": 1234<br>  },<br>  "extractions": [<br>    {"field": "objet", "value": "...", "source": "regex", "score": 0.9},<br>    ...<br>  ]<br>}<br>``` |

**Plan de vérification** :
- [ ] `GET /api/v1/ged/appels-offres/SF_22_2025` retourne 200 avec la structure ci-dessus.
- [ ] `GET /api/v1/ged/appels-offres/INEXISTANT` retourne 404.

---

## T5.2 — Liste paginée avec filtres

**Description & objectif** : remplacer la liste complète par une API paginée et filtrable.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `backend` | `MODIFY` | `backend/main.py` : `GET /api/v1/ged/appels-offres` accepte :<br>- `page=1` (défaut 1)<br>- `page_size=20` (défaut 20, max 100)<br>- `ville=Casablanca` (filtre partiel, ILIKE)<br>- `organisme=ANEP` (filtre partiel)<br>- `categorie=Travaux` (filtre exact)<br>- `date_min=2025-01-01`<br>- `date_max=2025-12-31`<br>- `q=route` (recherche FTS sur `objet` + `methode_notation`)<br>Retourne `{"items": [...], "total": 42, "page": 1, "page_size": 20, "pages": 3}`. |
| `backend` | `MODIFY` | `backend/schemas.py` : `MarcheFilter` (BaseModel) avec tous les champs ci-dessus. |
| `backend` | `MODIFY` | `backend/repository.py` : `MarcheRepository.list(filter: MarcheFilter) -> Tuple[List[Marche], int]`. |

**Plan de vérification** :
- [ ] `GET /api/v1/ged/appels-offres?page=1&page_size=5` retourne 5 items + `total=12`.
- [ ] `?ville=Casablanca` filtre correctement.
- [ ] `?q=route` retourne les AO contenant "route" dans l'objet.
- [ ] `?date_min=2025-06-01` exclut les AO avant juin 2025.

---

## T5.3 — Composant `DocumentDetail.jsx`

**Description & objectif** : afficher la fiche détaillée d'un AO (champs + texte OCR + extractions).

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `frontend` | `NEW` | `frontend-react/src/components/DocumentDetail.jsx` (≈ 200 lignes) :<br>1. Props : `numero_ordre` (récupéré via URL ou state)<br>2. Fetch `GET /api/v1/ged/appels-offres/{numero_ordre}`<br>3. Onglets (Tabs) :<br>   - **Champs** : tableau clé-valeur des champs du marché<br>   - **Texte OCR** : `<pre>` scrollable avec le `raw_text`<br>   - **Extractions** : tableau `(field, value, source, score, snippet)`<br>   - **Source** : lien vers le ZIP (si le serveur le sert)<br>4. Bouton retour vers la liste. |
| `frontend` | `MODIFY` | `frontend-react/src/App.jsx` : gérer la navigation (state-based) entre `SearchFTS` ↔ `DocumentDetail`. |

**Plan de vérification** :
- [ ] Cliquer sur un résultat de recherche ouvre `DocumentDetail` avec les données chargées.
- [ ] Si l'API retourne 404, message "Marché introuvable" + bouton retour.
- [ ] Le texte OCR est lisible (taille de police raisonnable, retour à la ligne).

---

## T5.4 — Pagination et filtres dans `SearchFTS.jsx`

**Description & objectif** : enrichir la recherche avec pagination et filtres UI.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `frontend` | `MODIFY` | `frontend-react/src/components/SearchFTS.jsx` :<br>1. Ajouter champs de filtre (ville, organisme, catégorie, date min/max)<br>2. Ajouter composant de pagination (boutons Prev/Next + page courante)<br>3. Modifier le `useEffect` pour passer tous les filtres à l'API<br>4. Bouton "Réinitialiser les filtres" |

**Plan de vérification** :
- [ ] Le filtrage par ville réduit le nombre de résultats.
- [ ] La pagination fonctionne (page 1, 2, 3).
- [ ] Le bouton "Réinitialiser" remet les filtres à zéro.

---

## T5.5 — Upload avec progression réelle

**Description & objectif** : remplacer la barre de progression factice par un polling du statut.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `frontend` | `MODIFY` | `frontend-react/src/components/Upload.jsx` :<br>1. Stocker `document_id` retourné par l'API<br>2. Lancer `setInterval(() => fetch(/status), 2000)`<br>3. Mettre à jour la barre de progression :<br>   - 0–33 % : `raw_zip` (upload en cours)<br>   - 33–66 % : `extracted` (OCR en cours)<br>   - 66–100 % : `ocr_processed` (terminé)<br>4. `clearInterval` quand statut final atteint<br>5. Afficher le `ocr_confidence` à la fin |

**Plan de vérification** :
- [ ] Uploader un ZIP de 200 Ko, la barre passe par les 3 paliers.
- [ ] À la fin, `ocr_confidence` est affiché.

---

## T5.6 — Tests frontend

**Description & objectif** : valider le rendu des nouveaux composants.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `frontend` | `NEW` | `frontend-react/src/components/__tests__/DocumentDetail.test.jsx` (3 tests) :<br>- `test_renders_marche_fields`<br>- `test_renders_ocr_text`<br>- `test_handles_404` |
| `frontend` | `NEW` | `frontend-react/src/components/__tests__/SearchFTS.test.jsx` (2 tests) :<br>- `test_pagination_works`<br>- `test_filters_trigger_refetch` |
| `frontend` | `MODIFY` | `frontend-react/src/components/__tests__/Upload.test.jsx` (1 test) : `test_polls_status_after_upload`. |

**Plan de vérification** :
- [ ] `npm test` → 6 nouveaux tests passed.

---

## T5.7 — Servir le frontend React depuis FastAPI

**Description & objectif** : supprimer le `mount("/")` vers le frontend vanilla (déjà fait en T1.8), servir le React build à la place.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `frontend` | `MODIFY` | `frontend-react/vite.config.js` : `base: '/app/'` (pour cohabiter avec l'API sous `/api/...`). |
| `frontend` | `CMD` | `cd frontend-react && npm run build` (produit `frontend-react/dist/`) |
| `backend` | `MODIFY` | `backend/main.py` : `app.mount("/app", StaticFiles(directory="frontend-react/dist", html=True), name="frontend")` |
| `backend` | `MODIFY` | `backend/main.py` : `app.get("/", include_in_schema=False)(lambda: RedirectResponse("/app"))` |

**Plan de vérification** :
- [ ] `http://localhost:8000/` redirige vers `/app/`.
- [ ] `http://localhost:8000/app/` affiche l'UI React.
- [ ] `http://localhost:8000/api/v1/ged/appels-offres` reste accessible.

---

## ✅ Critères de sortie de la Phase 5

- [ ] Cliquer sur un résultat de recherche ouvre la page détail avec texte OCR visible.
- [ ] La pagination fonctionne (3+ pages testées).
- [ ] Les filtres par ville/organisme/catégorie réduisent les résultats.
- [ ] L'upload affiche une progression réelle (pas factice).
- [ ] `npm test` → 100 % vert.
- [ ] `pytest tests/` → 100 % vert.
- [ ] Le frontend React est servi par FastAPI.

**Effort total** : 1 jour ouvré.
