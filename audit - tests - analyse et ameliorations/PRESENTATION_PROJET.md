# 📝 Présentation et Documentation du Projet — GED Intelligente (PFA)

Ce document fournit une vue d'ensemble complète et structurée du projet de **Gestion Électronique des Documents (GED) Intelligente** pour la gestion des marchés publics du Ministère de l'Équipement et de l'Eau du Maroc.

---

## 1. Description du Projet

### 1.1 Contexte
Ce projet a été réalisé dans le cadre d'un stage de **PFA (Projet de Fin d'Année)** d'une durée de 2 mois, effectué en deuxième année du cycle d'ingénieur afin de consolider les compétences acquises au cours du cursus. Ce stage s'est déroulé au sein de la **Direction des Systèmes d'Information (DSI)** du **Ministère de l'Équipement et de l'Eau du Maroc** (organisme d'accueil). 

Le projet vise à concevoir et développer une solution intelligente pour valoriser, indexer et structurer les données textuelles contenues dans les Dossiers d'Appels d'Offres (D.A.O.) et documents de marchés publics de l'organisme, qui sont habituellement publiés de manière non structurée sous forme de PDF numérisés ou natifs.

### 1.2 Problématique
Le portail des marchés publics publie quotidiennement des dizaines d'appels d'offres au format PDF. Ces documents contiennent des informations cruciales (budgets estimatifs, cautions provisoires, délais de réalisation, critères d'élimination technique, exigences d'agréments, etc.). N'étant ni indexés ni structurés, l'analyse de ces documents requiert une lecture manuelle fastidieuse, empêchant toute recherche sémantique globale ou analyse décisionnelle automatisée.

### 1.3 Objectifs du Système
1. **Automatisation de la Collecte** : Récupérer de façon ciblée les archives d'appels d'offres directement depuis le portail web public via un robot de scraping.
2. **OCR & Extraction de Texte** : Convertir les PDF textuels et scannés (souvent bilingues français/arabe) en texte brut exploitable.
3. **Analyse Sémantique NLP** : Identifier, extraire et normaliser automatiquement les entités d'intérêt (montants financiers, dates limites, villes d'exécution, etc.) grâce à des modèles de traitement du langage naturel.
4. **Recherche Plein Texte (FTS)** : Offrir une interface de recherche instantanée (type Google) capable de chercher dans le contenu textuel de centaines de pages de D.A.O.
5. **Business Intelligence (BI)** : Agréger les données financières et logistiques pour alimenter un tableau de bord décisionnel interactif.
6. **Intelligence Artificielle (ML)** : Catégoriser automatiquement les nouveaux appels d'offres et détecter les anomalies financières (ex. caution provisoire disproportionnée par rapport au montant estimé).

### 1.4 Ressources Utilisées
* **Base de données** : SQLite 3 pour les environnements de développement et de tests, et PostgreSQL pour la production (permettant une indexation FTS performante grâce à des index GIN).
* **Données Sources** : Les dossiers de marchés publics réels collectés et téléchargés directement depuis le portail d'étude officiel du Ministère de l'Équipement et de l'Eau : [appels-offres.equipement.gov.ma](http://appels-offres.equipement.gov.ma). Un jeu de données réel d'une vingtaine d'appels d'offres complets (contenant les documents de consultation tels que le CPS et le RC) a été collecté via Playwright pour alimenter et valider la plateforme.
* **Environnement** : Serveur d'API asynchrone Python et application web monopage (SPA) React en frontend.

---

## 2. Technologies Utilisées

La plateforme repose sur une stack moderne, découplée et hautement performante :

### 2.1 Backend & Base de données
* **Python 3.11+** : Langage principal du backend et des pipelines de données.
* **FastAPI** : Framework web asynchrone utilisé pour concevoir des APIs REST rapides, documentées automatiquement avec OpenAPI / Swagger.
* **SQLAlchemy 2.0** : ORM (Object-Relational Mapping) utilisé pour abstraire et unifier l'accès à la base de données.
* **Alembic** : Outil de gestion des migrations de base de données permettant de versionner le schéma SQL.
* **SQLite / PostgreSQL** : Moteurs de base de données relationnelle.

### 2.2 Ingestion, Scraping & Traitement de Documents
* **Playwright (Python)** : Outil d'automatisation de navigateur utilisé pour scrapper de manière robuste le portail ASP.NET des marchés publics (gestion de la pagination et téléchargement asynchrone des fichiers ZIP).
* **PyMuPDF (fitz)** : Utilisé pour extraire rapidement et fidèlement le texte des PDF natifs (vectoriels).
* **Tesseract OCR (5.x)** : Moteur de reconnaissance optique de caractères configuré pour les langues française et arabe pour traiter les documents scannés.

### 2.3 Traitement Automatique du Langage (NLP) & Machine Learning
* **spaCy (Modèle `fr_core_news_sm`)** : Moteur NLP industriel pour l'extraction sémantique et la tokenisation.
* **Regex (Expressions régulières)** : Utilisées pour l'extraction précise et typée des montants financiers (MAD) et des références réglementaires.
* **scikit-learn** :
  * `TfidfVectorizer` & `SVC` (SVM) : Utilisés pour la classification automatique de la catégorie de prestation du marché.
  * `IsolationForest` : Utilisé pour détecter les anomalies financières basées sur le montant, le cautionnement et le délai.
* **Joblib** : Outil de sérialisation pour sauvegarder et charger les modèles de Machine Learning entraînés.

### 2.4 Frontend & Visualisation (BI)
* **React 19** : Framework d'interface utilisateur pour bâtir une Single Page Application réactive et fluide.
* **Vite** : Outil de build nouvelle génération pour React, assurant un démarrage et un rechargement à chaud instantanés.
* **Tailwind CSS** : Framework CSS utilitaire pour concevoir une interface moderne, épurée et responsive respectant les codes esthétiques SaaS (Sleek Dark Mode, structures en grilles).
* **Recharts** : Bibliothèque de graphiques interactifs basée sur SVG, utilisée pour le tableau de bord analytique.
* **Axios** : Client HTTP pour communiquer avec l'API FastAPI du backend.

### 2.5 Qualité & Automatisation
* **Pytest & Pytest-cov** : Frameworks de tests unitaires et d'intégration assurant une couverture de code minimale de **70%** sur l'ensemble du projet.

---

## 3. Fonctionnalités par Module

Le système est découpé en plusieurs modules applicatifs :

```
┌────────────────────────────────────────────────────────┐
│               INTERFACE REACT (L4)                      │
│  ┌───────────────┬───────────────────┬──────────────┐  │
│  │   Dashboard   │   Recherche FTS   │  Modèles ML  │  │
│  └───────┬───────┴─────────┬─────────┴──────┬───────┘  │
└──────────┼─────────────────┼────────────────┼──────────┘
           ▼                 ▼                ▼
┌────────────────────────────────────────────────────────┐
│                 FASTAPI BACKEND (L3)                   │
│  ┌───────────────────────┬──────────────────────────┐  │
│  │      Analytics        │     Recherche / GED      │  │
│  └───────────┬───────────┴─────────────┬────────────┘  │
└──────────────┼─────────────────────────┼───────────────┘
               ▼                         ▼
┌────────────────────────────────────────────────────────┐
│             PIPELINES OCR, NLP & ML (L2)               │
│  ┌───────────────────────┬──────────────────────────┐  │
│  │   Tesseract OCR       │   spaCy NLP Extraction   │  │
│  ├───────────────────────┼──────────────────────────┤  │
│  │   Classification SVM  │   Isolation Forest (ML)  │  │
│  └───────────────────────┴──────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

### 3.1 Module Ingestion & Collecte (Scraper)
* **Collecte automatisée** : Navigation automatique, gestion du formulaire de recherche du portail ministériel et scraping des archives par lot (batch).
* **Orchestrateur asynchrone** : Réception des fichiers ZIP/PDF via l'API, décompression en tâche de fond (`BackgroundTasks` FastAPI) pour ne pas bloquer l'utilisateur, et mise en file d'attente.

### 3.2 Module Traitement OCR & Native PDF
* **Détection du type de PDF** : Analyse des pages du document pour déterminer s'il s'agit d'un PDF natif (texte directement extractible) ou d'un PDF scanné (nécessitant l'OCR), optimisant ainsi le temps de traitement.
* **Extraction OCR Hybride** : Application d'un prétraitement d'image (niveaux de gris, seuillage) puis passage dans Tesseract OCR pour extraire chaque ligne de texte.
* **Journalisation et Qualité** : Suivi du taux de confiance moyen renvoyé par le moteur OCR et stockage dans la table `OcrLog` pour monitoring.

### 3.3 Module Structuration NLP
* **Extraction d'entités clés** : Extraction automatique de la référence du marché, de l'objet, du maître d'ouvrage (acheteur), et de la ville d'exécution.
* **Analyse financière** : Extraction du montant estimé en dirhams (MAD) et de la caution provisoire par expressions régulières multi-formats.
* **Normalisation des données** : Conversion des dates textuelles en dates ISO valides, et rapprochement des villes avec une liste officielle des provinces du Maroc.

### 3.4 Module Moteur de Recherche (FTS)
* **Recherche Plein Texte** : Moteur de recherche rapide capable de scanner l'ensemble des pages de texte OCR stockées en BDD.
* **Filtres Combinés** : Affinage des résultats de recherche par catégorie de prestation, par budget estimé minimum/maximum, par ville, ou par date.
* **Pagination dynamique** : Gestion fluide des résultats de recherche volumineux pour optimiser la mémoire du client.

### 3.5 Module Intelligence Artificielle & Machine Learning
* **Classification Automatique (SVM)** : Entraînement d'un classifieur linéaire SVM (Support Vector Machine) sur le texte OCRisé des D.A.O. pour attribuer automatiquement une catégorie de prestation (ex. Travaux routiers, Études techniques, Fournitures de bureau) au document importé.
* **Détection d'Anomalies Financières** : Analyse de la cohérence financière à l'aide d'une forêt d'isolement (`IsolationForest`) pour identifier des montants de caution anormaux ou des délais d'exécution irréalistes par rapport à la catégorie du marché.
* **Entraînement Asynchrone** : Endpoint API permettant de lancer le ré-entraînement périodique des modèles de ML au fur et à mesure de l'ingestion de nouveaux documents.

---

## 4. Écrans Actuels de l'Application

L'interface web est conçue comme un portail SaaS moderne avec un menu de navigation fixe à gauche (`Sidebar`), une barre supérieure d'état (`Topbar`), et un espace de travail central fluide.

### 4.1 Page d'Accueil (`LandingPage`)
* **Description** : Portail d'entrée de l'application offrant une identité visuelle soignée (typographie premium, arrière-plan texturé) et des boutons d'accès rapide vers les différents modules.
* **Éléments clés** : Bannière de présentation, cartes d'accès rapide, statistiques succinctes du système (nombre total de documents indexés).

### 4.2 Tableau de Bord Décisionnel (`Dashboard`)
* **Description** : L'écran analytique principal de Business Intelligence.
* **Éléments clés** :
  * **Widgets KPI** : Quatre cartes affichant le nombre de marchés, le budget cumulé (en Millions de MAD), le délai moyen d'exécution et le taux de réussite d'OCR.
  * **Graphique en Camembert (PieChart)** : Répartition des marchés par catégories d'activité (Études, Travaux, Fournitures, etc.).
  * **Graphique en Barres (BarChart)** : Top 10 des acheteurs publics classés par volume financier total.

### 4.3 Recherche Sémantique (`SearchFTS`)
* **Description** : Une interface de recherche de type moteur de recherche sur l'intégralité du texte extrait des appels d'offres.
* **Éléments clés** :
  * Barre de recherche avec autocomplétion.
  * Panneau latéral de filtres (Ville, budget min/max, date de parution).
  * Liste des résultats paginés montrant le titre du marché, la référence, l'acheteur, le budget, et un bouton d'accès aux détails.

### 4.4 Fiche de Détail d'un Appel d'Offres (`DocumentDetail`)
* **Description** : Vue exhaustive des données d'un document, organisée en onglets pour une lisibilité maximale.
* **Éléments clés** :
  * **Onglet Informations Générales** : Fiche d'identité du marché (référence, acheteur, montant estimé, caution, délai, ville, etc.).
  * **Onglet Texte Intégral OCR** : Conteneur de texte avec barre de défilement affichant le texte brut extrait du PDF.
  * **Onglet NLP & ML** : Détail des entités extraites automatiquement avec scores de confiance et indicateurs d'anomalies ML (alertes en rouge si le marché est classifié comme atypique).

### 4.5 Explorateur de Documents (`Explorer`)
* **Description** : Une table de type gestionnaire de fichiers pour consulter tous les documents physiques présents dans le système.
* **Éléments clés** :
  * Colonnes : Nom du fichier (avec icône selon le type), type (Archive ZIP, PDF), taille, date d'import et statut.
  * Statuts d'ingestion représentés par des badges de couleur (Succès, En cours, Échec).

### 4.6 Import de Documents (`Upload`)
* **Description** : Zone interactive permettant d'ajouter de nouvelles pièces au système.
* **Éléments clés** :
  * Zone de dépôt par glisser-déposer (Drag & Drop).
  * Liste des fichiers mis en file d'attente d'upload.
  * Polling dynamique affichant l'état de traitement de l'OCR et du NLP en temps réel pour chaque document téléversé.

### 4.7 Analyse Prédictive & Modèles ML (`PredictorML`)
* **Description** : Panneau de contrôle et de pilotage des modèles d'intelligence artificielle.
* **Éléments clés** :
  * Indicateur de précision courante du modèle SVM.
  * Nombre d'anomalies détectées dans la base de données.
  * Bouton d'action pour réentraîner les modèles en arrière-plan.
  * **Watchlist de Classification** : Tableau listant les désaccords entre la classification saisie par l'humain et la prédiction de l'IA (permettant aux administrateurs de corriger les erreurs de saisie).

### 4.8 Monitoring Système (`Monitoring`)
* **Description** : Page technique destinée à l'administrateur du système pour vérifier la santé de la plateforme.
* **Éléments clés** :
  * Journal de logs déroulant en direct.
  * Statistiques de temps de calcul (temps moyen de traitement d'une page en OCR).

### 4.9 Console d'Administration du Pipeline (`PipelineAdmin`)
* **Description** : Écran de pilotage pour lancer manuellement des collectes de données externes.
* **Éléments clés** :
  * Filtre de plage de dates pour le scraper.
  * Bouton "Lancer le Scraping" déclenchant le bot Playwright en arrière-plan.
  * Visualisation de l'état du scraper (Inactif, En cours, Nombre d'AO collectés).
