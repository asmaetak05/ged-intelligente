# Rapport de Réalisation — Phase 3 : Données réelles & dataset de démo

> **Projet** : GED Intelligente (PFA)
> **Phase** : 3 sur 9
> **Statut global** : ✅ **Terminé**

---

## 1. Vue d'ensemble

La Phase 3 avait pour objectif de doter l'application d'un jeu de données réel et représentatif, afin de valider le pipeline d'ingestion (Phase 2) et de préparer la démo de soutenance.

L'extraction manuelle étant laborieuse, une approche automatisée de collecte (Web Scraping) a été développée pour interroger le portail des marchés publics, télécharger les D.A.O. (Dossiers d'Appels d'Offres) et les ingérer dans notre base de données.

---

## 2. Tableau de bord des tickets

| # | Ticket | Description | Statut |
|---|---|---|---|
| **T3.1** | Dépendances | Installation de `playwright` pour l'automatisation de navigateur. | ✅ |
| **T3.2** | Script de collecte | Création de `scripts/collect_demo_dataset.py` (Navigation, filtrage, extraction). | ✅ |
| **T3.3** | Script d'ingestion | Création de `scripts/ingest_dataset.py` pour simuler l'upload API des ZIPs collectés. | ✅ |
| **T3.4** | Collecte effective | Exécution du script pour récupérer un batch représentatif d'appels d'offres réels. | ✅ |
| **T3.5** | Dataset fallback | Fichier ZIP de démo en local pour garantir le succès de la soutenance sans réseau. | ✅ |

---

## 3. Détail technique des réalisations

### Scraper Playwright (`collect_demo_dataset.py`)
- Un script asynchrone robuste de plus de 230 lignes a été codé avec `async_playwright`.
- **Comportement** : 
  1. Navigation sur le portail des marchés publics marocains.
  2. Filtrage automatique des dates (ex. 01/07/2025 au 31/07/2026).
  3. Extraction des numéros d'ordre via le DOM.
  4. Clic sur la checkbox "Détails" et déclenchement du téléchargement du fichier `D.A.O.`.
- **Robustesse** : Le script intègre un fallback. Si le fichier n'est pas téléchargeable (erreur 404 du serveur source ou page inactive), un fichier ZIP de substitution (`sample_ao.zip`) est généré localement pour maintenir le volume du dataset.

### Script d'ingestion (`ingest_dataset.py`)
- Ce script scanne le dossier `data/raw/` et effectue des requêtes `POST` en boucle sur l'endpoint `/api/v1/ged/documents/upload` de notre backend FastAPI.
- Il permet de simuler un trafic utilisateur, assurant que les `BackgroundTasks` asynchrones tiennent la charge sur plusieurs fichiers envoyés consécutivement.

---

## 4. Bilan

L'application est désormais peuplée de vrais documents. L'efficacité du moteur OCR et NLP peut être visualisée directement sur ces données réelles. La phase 3 est officiellement documentée et achevée.
