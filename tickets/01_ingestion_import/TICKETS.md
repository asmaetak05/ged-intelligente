# 01 — Collecte et import documentaire

**Priorité du module : P0/P1.** Ce module doit fonctionner sans dépendre du portail externe.

## ING-01 — Sécuriser et normaliser l'import

**État : Partiel.** `POST /api/v1/ged/documents/upload` accepte un ZIP, vérifie les quatre premiers octets, limite la taille à 100 Mo, stocke dans `data/raw` et calcule un SHA-256.

### Réalisation attendue

1. Extraire la validation dans `backend/services/file_validation.py`.
2. Accepter explicitement les types utiles : ZIP, PDF et DOCX ; rejeter tout autre format avec un message métier.
3. Ajouter contrôle MIME réel, taille compressée et taille décompressée, nombre de fichiers, protection zip-slip et archives chiffrées/non lisibles.
4. Générer un nom de stockage sûr indépendant du nom utilisateur ; conserver le nom original comme métadonnée.
5. Ajouter une zone de quarantaine `data/quarantine/` et un statut de rejet avec motif.
6. Écrire les tests : faux ZIP, ZIP slip, archive trop volumineuse, PDF valide, doublon exact.

### Critères d'acceptation

- un ZIP malveillant ne peut pas écrire hors du répertoire prévu ;
- les limites sont configurables par variables d'environnement ;
- tout rejet est visible avec un motif ;
- l'original, le hash, le type détecté et le nom source sont conservés.

## ING-02 — Modéliser le cycle de vie et les jobs persistants

**État : Partiel.** `BackgroundTasks` lance `backend.tasks.process_document_async`, mais il n'existe pas de modèle de job durable, de reprise ni de retry contrôlé.

### Réalisation attendue

1. Ajouter modèles et migration : `processing_jobs`, `processing_job_steps`, `attempt_count`, `started_at`, `finished_at`, `error_code`, `error_detail`.
2. Définir les états : `received`, `validated`, `extracting`, `ocr_running`, `nlp_running`, `indexing`, `review_required`, `completed`, `failed`, `quarantined`.
3. Créer `backend/services/job_service.py` avec transitions validées et journalisation.
4. Isoler l'exécution dans un worker. Pour le MVP, un worker Python lancé séparément est acceptable ; documenter l'évolution vers Celery/RQ/Arq.
5. Ajouter endpoints : création de job, lecture de statut détaillé, relance autorisée et liste des erreurs.
6. Mettre à jour `frontend-react/src/components/Upload.jsx` pour interroger `/status` et non `/preview`.

### Critères d'acceptation

- un redémarrage du serveur ne fait pas disparaître les jobs en attente ;
- un échec contient une cause et peut être relancé sans doublon ;
- l'interface affiche l'étape réelle et non un pourcentage simulé ;
- un test couvre succès, erreur et reprise.

## ING-03 — Rendre le scraper remplaçable et démontrable hors ligne

**État : Partiel/À vérifier.** Plusieurs scripts Playwright sont présents dans `ingestion/`; le portail communiqué ne résolvait pas au moment de l'audit.

### Réalisation attendue

1. Créer une interface `ingestion/connectors/base.py` avec méthodes `healthcheck`, `discover`, `download` et `normalize_metadata`.
2. Déplacer le scraper actuel dans `ingestion/connectors/equipement_portal.py` et centraliser les sélecteurs dans `config_selectors.json` versionné.
3. Créer `ingestion/connectors/local_replay.py` qui rejoue les archives présentes dans `data/samples/`.
4. Ajouter table `sources`/configuration avec URL, version de connecteur, disponibilité et dernière exécution.
5. Faire de `dry_run` une simulation qui ne télécharge pas et rapporte les dossiers détectés.
6. Ajouter tests avec fixtures HTML locales `ingestion/page_initiale.html` et `page_archives.html`.

### Critères d'acceptation

- la démonstration peut ingérer au moins cinq dossiers sans accès Internet ;
- une indisponibilité de source est visible dans le monitoring sans faire tomber l'API ;
- toute collecte possède source, URL, date, hash et version du connecteur ;
- les sélecteurs changent sans modification du cœur métier.

## ING-04 — Constituer un corpus de référence gouverné

**État : Partiel.** Des fichiers sont présents sous `data/`, mais le corpus et ses conditions d'usage ne sont pas documentés de façon opérationnelle.

### Réalisation attendue

1. Créer `data/samples/manifest.csv` et `data/samples/README.md` : identifiant, type, langue, qualité, provenance, date, hash, droits d'usage et statut d'anonymisation.
2. Préparer au moins 20 dossiers : natifs/scannés, français/arabe/bilingues, bons et mauvais scans.
3. Ajouter une version réduite et légitime à versionner ; stocker les fichiers lourds hors Git avec procédure de récupération.
4. Créer `scripts/load_demo_corpus.py` idempotent.

### Critères d'acceptation

- chaque document de démo est identifiable et traçable ;
- le corpus se charge depuis une base vide en une commande ;
- le même corpus sert aux tests, métriques et démonstration.

