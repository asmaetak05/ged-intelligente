# 🎫 Lot 2 : Ingestion & Scraping (Ingestion & Collect)

## 📌 Présentation du Lot
Ce lot fiabilise le robot de scraping Playwright chargé de collecter les avis du portail du Ministère. Il introduit le découplage des configurations, la reprise sur erreur, et la déduplication au moment de l'acquisition.

* **Complexité globale** : Medium
* **Composants impactés** : `ingestion/`, `backend/tasks.py`
* **Indépendance git** : Excellente. Tout le travail se concentre dans les scripts autonomes d'ingestion et les modules d'orchestration.

---

## 📋 Liste des Tickets Associés

### 1. ING-01 — Pool Playwright + parallélisation contrôlée 🟠
* **Priorité** : 🟠 P1
* **Effort** : M (3 j)
* **Composant** : `ingestion/playwright_scraper_batch.py`
* **Scénarios de test liés** : `ST-IN-001`
* **Description** : Remplacer l'instance de navigateur Playwright unique par un pool de workers asynchrones contrôlé. Gérer un sémaphore pour ne pas surcharger le site cible (limiter à 3 pages simultanées) afin d'éviter les bannissements IP.

### 2. ING-02 — Découplage des sélecteurs (Configuration Externe) 🔴
* **Priorité** : 🔴 P0
* **Effort** : S (1 j)
* **Composant** : `ingestion/config_selectors.json`, `ingestion/playwright_scraper_batch.py`
* **Scénarios de test liés** : `ST-IN-002`
* **Description** : Sortir tous les sélecteurs CSS/XPath en dur de Playwright du code et les placer dans un fichier de configuration externe JSON. Cela permet d'adapter le scraper en cas de mise à jour visuelle du portail officiel sans modifier le code source Python.

### 3. ING-03 — Reprise sur erreur (Checkpoint + Offset) 🔴
* **Priorité** : 🔴 P0
* **Effort** : M (2 j)
* **Composant** : `ingestion/playwright_scraper_batch.py`, `backend/models.py`
* **Scénarios de test liés** : `ST-IN-003`, `ST-IN-004`
* **Description** : En cas de coupure réseau ou d'arrêt inopiné, le scraper doit pouvoir reprendre là où il s'est arrêté.
* **Travail** :
  - Sauvegarder la dernière date de parution et le dernier index de page scrapé avec succès.
  - Lire ce checkpoint au démarrage du script.

### 4. ING-04 — Idempotence et Déduplication par Hash SHA-256 🔴
* **Priorité** : 🔴 P0
* **Effort** : S (1 j)
* **Composant** : `ingestion/extractor.py`, `backend/repository.py`
* **Scénarios de test liés** : `ST-IN-008`, `ST-DQ-001`
* **Description** : Avant de décompresser un D.A.O. ZIP ou de lancer l'OCR, calculer le hash SHA-256 du fichier téléchargé. Si le hash existe déjà en BDD, ignorer le fichier pour éviter les doublons de traitement CPU-vores.

---

## 🛠️ Description des Travaux
1. **Extraction de la configuration** :
   - Créer `ingestion/config_selectors.json` contenant les ID et classes des éléments de la page de recherche (`date_parution1`, `date_parution2`, `btn_rechercher`, etc.).
   - Modifier le scraper pour charger ce fichier via `json.load()`.
2. **Implémentation du Checkpoint** :
   - Écrire un fichier local temporaire ou une table de configuration pour stocker l'état du dernier scraping (date de début, date de fin, statut).
3. **Optimisation asynchrone** :
   - Utiliser `asyncio.Semaphore(3)` dans le script de scraping.

---

## 🧪 Critères de Validation et Non-régression
- **Simulation d'erreur** : Couper temporairement le scraper en milieu de course (via interruption `Ctrl+C`). Relancer et vérifier que le scraper reprend à l'offset de page sauvegardé.
- **Dédoublonnage** : Essayer d'ingérer le même fichier ZIP de test deux fois et s'assurer que le système logue un message d'avertissement et ignore la seconde exécution sans lever d'erreur.
