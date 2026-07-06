# Module Frontend (Interface Utilisateur)

## 1. Technologies et Socle
L'interface utilisateur a été développée avec **React 18** et packagée avec **Vite**, garantissant un temps de compilation ultra-rapide (HMR).
Le style visuel est assuré par **Tailwind CSS v4**, avec une approche "Minimaliste & Premium" (couleurs neutres Zinc, absence d'ombres lourdes, flat design).

## 2. Structure des Écrans (Routing React Router)
- **`/` (Dashboard)** : Vue d'ensemble stratégique. Utilisation de la librairie `Recharts` pour générer des diagrammes sectoriels (PieChart) et des historiques financiers (BarChart). Connectée à l'API Analytics.
- **`/search` (Recherche FTS)** : Moteur de recherche sémantique interrogeant la base de données.
- **`/explorer` (Explorateur)** : Tableau de suivi des documents ingérés et de leur statut de traitement (Extrait, En cours, Échec).
- **`/upload` (Ingestion)** : Composant Drag & Drop pour le téléversement des archives `.zip`. Intègre une barre de progression simulant le pipeline de traitement.
- **`/ml` (Predictor ML)** : Dashboard spécifique affichant les alertes de l'Intelligence Artificielle (Watchlist des classifications erronées).
- **`/monitoring` (DevOps)** : Terminal virtuel pour le suivi de l'état des serveurs et l'affichage des logs d'extraction en temps réel.

## 3. Communication Client-Serveur
La bibliothèque **Axios** gère toutes les requêtes HTTP asynchrones vers le backend FastAPI (`http://localhost:8000`), avec gestion d'erreurs intégrée.
