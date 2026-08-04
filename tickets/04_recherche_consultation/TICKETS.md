# 04 — Recherche, fiche dossier et comparaison

**Priorité du module : P1.** Ce module rend la valeur métier visible ; il doit être fondé sur les données réellement extraites.

## SRC-01 — Remplacer le faux FTS par une recherche correctement qualifiée

**État : Partiel.** `backend/repository.py::search_fts` utilise `LIKE`/`ILIKE` sur titre, numéro, référence et texte ; le README parle de recherche sémantique.

### Réalisation attendue

1. À court terme, renommer l'interface et la documentation en « Recherche textuelle avancée ».
2. Ajouter une migration PostgreSQL pour une colonne `tsvector` et index GIN ; préserver une implémentation SQLite limitée pour le développement.
3. Créer une stratégie de tokenisation FR et documenter la stratégie arabe ; ne pas revendiquer de recherche sémantique sans embeddings évalués.
4. Ajouter ranking, snippets issus du texte réel et surlignage des termes.
5. Étendre `MarcheFilter` avec filtres validés, bornes et tri explicite.
6. Ajouter tests de pertinence et de pagination dans `tests/test_search.py`.

### Critères d'acceptation

- la recherche renvoie des extraits contenant effectivement les termes ;
- les filtres date/montant/ville/catégorie sont combinables ;
- le résultat est trié par pertinence ou par règle clairement annoncée ;
- README ne confond plus FTS et recherche sémantique.

## SRC-02 — Finaliser la fiche dossier traçable

**État : Partiel.** `frontend-react/src/components/DocumentDetail.jsx` charge un appel d'offres, mais les preuves par champ, les pages OCR, l'historique et les autorisations restent incomplets.

### Réalisation attendue

1. Étendre `GET /api/v1/ged/appels-offres/{numero}` avec document, pages, extractions, validations, audit simplifié et permissions.
2. Ajouter onglets : résumé, champs et preuves, texte/page, document original, historique.
3. Intégrer `ExtractionReview.jsx` du module NLP.
4. Ajouter téléchargement/aperçu du fichier source uniquement si l'utilisateur est autorisé.
5. Afficher les champs absents et les champs à vérifier sans les masquer.

### Critères d'acceptation

- chaque champ affiché renvoie à une preuve consultable ;
- aucun fichier original n'est exposé sans droit ;
- la fiche indique clairement les limites et erreurs de traitement ;
- un test e2e couvre recherche → fiche → preuve.

## SRC-03 — Ajouter comparaison et export maîtrisé

**État : Partiel.** Un endpoint `/api/v1/compare` et un export CSV/XLSX existent, mais les usages, permissions, format et trace d'audit sont insuffisamment cadrés.

### Réalisation attendue

1. Définir les champs comparables et leur libellé dans `docs/COMPARAISON_DOSSIERS.md`.
2. Créer `frontend-react/src/components/CompareMarches.jsx` : sélection de 2 à 3 dossiers, tableau des différences, liens vers preuves.
3. Sécuriser `/compare` et `/export`; ajouter filtres identiques à la recherche et journalisation des exports.
4. Limiter le volume d'export, nommer les colonnes, protéger contre l'injection CSV et préciser les données exclues.
5. Ajouter tests API et interface pour permissions, sélection invalide et contenu exporté.

### Critères d'acceptation

- deux dossiers sont comparables sans données simulées ;
- tout export est journalisé avec utilisateur, date et filtre ;
- les valeurs comparées conservent leur lien vers la source.

## SRC-04 — Centraliser la configuration API du frontend

**État : Partiel.** `src/api/axios.js` existe, mais `Upload.jsx`, `DocumentDetail.jsx`, `Explorer.jsx`, `Monitoring.jsx`, `PipelineAdmin.jsx`, `PredictorML.jsx` et `Login.jsx` contiennent encore des URLs localhost/127.0.0.1.

### Réalisation attendue

1. Étendre `frontend-react/src/api/axios.js` avec clients dédiés `gedApi`, `analyticsApi`, `authApi`.
2. Remplacer tous les `fetch` et Axios à URL absolue par ces clients.
3. Introduire `VITE_API_BASE_URL`, `VITE_WS_BASE_URL` et fichiers `.env.example` frontend.
4. Ajouter intercepteur d'authentification et gestion globale des erreurs 401/403/500.
5. Tester build avec une URL non localhost.

### Critères d'acceptation

- `rg` ne trouve plus d'URL `localhost:8000` ou `127.0.0.1:8000` hors configuration ;
- l'API peut être changée sans modifier de composant ;
- l'application gère proprement les erreurs d'autorisation.

