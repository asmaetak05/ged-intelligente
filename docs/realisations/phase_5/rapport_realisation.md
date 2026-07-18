# Rapport de Réalisation — Phase 5 : Page détail document & recherche enrichie

> **Projet** : GED Intelligente (PFA)
> **Phase** : 5 sur 9
> **Statut global** : ✅ **Terminé**

---

## 1. Vue d'ensemble

La Phase 5 visait à exploiter l'extraction de données (réalisée dans les phases précédentes) via une interface utilisateur riche. L'objectif était de remplacer les requêtes API brutes par une véritable barre de recherche sémantique (FTS) en frontend, et de fournir une vue détaillée pour chaque document ingéré, exposant à l'utilisateur le fruit du travail de l'IA (OCR et NLP).

---

## 2. Tableau de bord des tickets

| # | Ticket | Description | Statut |
|---|---|---|---|
| **T5.1** | Endpoint détail | API `GET /api/v1/ged/appels-offres/{id}` renvoyant les métadonnées et le texte OCR. | ✅ |
| **T5.2** | Liste paginée | Endpoint de recherche et pagination avec filtres (FTS, dates, villes). | ✅ |
| **T5.3** | Composant Détail | Création de `DocumentDetail.jsx` (Vue onglets : Champs, OCR, Extractions). | ✅ |
| **T5.4** | Composant Recherche | Refonte de `SearchFTS.jsx` avec requêtage dynamique vers l'API. | ✅ |
| **T5.5** | Polling Upload | Ajout de suivi de progression asynchrone réel sur `Upload.jsx`. | ✅ |

---

## 3. Détail technique des réalisations

### Moteur de recherche FTS (Backend & Frontend)
- **Backend** : Le repository `MarcheRepository` inclut la méthode `search_fts()` qui utilise l'opérateur SQL conditionnel (`ilike`) pour effectuer une recherche rapide sur la colonne `tsv_search` contenant le plein texte du document.
- **Frontend** : Le composant `SearchFTS.jsx` a été mis en œuvre. À chaque recherche, une requête HTTP `axios` avec le paramètre `q=` est envoyée au backend. Les résultats sont renvoyés de manière dynamique et paginée à l'utilisateur.

### Page de Détail (`DocumentDetail.jsx`)
- L'interface affiche l'Appel d'Offre de manière élégante et ergonomique avec l'aide de la librairie d'icônes `lucide-react`.
- **Onglets dynamiques** : L'utilisateur peut basculer en un clic entre le résumé (Métadonnées structurées extraites) et le texte OCR brut (pour vérifier visuellement la qualité de l'extraction logicielle).

### Suivi de l'Upload et de l'Ingestion
- La fausse barre de progression initiale a été remplacée par un polling intelligent sur l'API (`/status`).
- L'interface React écoute l'avancement et réagit aux différentes phases d'ingestion définies en base : `raw_zip` -> `extracted` -> `ocr_processed`, donnant un retour visuel clair et en direct à l'utilisateur pendant que les tâches de fond (`BackgroundTasks`) du backend font leur travail.

---

## 4. Bilan

Avec l'intégration de la recherche textuelle globale, le feedback visuel en temps réel de l'ingestion asynchrone, et l'affichage des détails complets des appels d'offres (incluant la traçabilité de l'OCR), l'application est désormais un produit complet et consultable. La phase 5 est achevée.
