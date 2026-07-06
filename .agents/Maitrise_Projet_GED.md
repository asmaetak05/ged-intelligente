# Maîtrise du Projet : GED Intelligente des Marchés Publics

Ce document récapitule les bases fondamentales à comprendre avant de débuter le développement du projet. Il sert de boussole technique et conceptuelle.

---

## 1. L'Entrée et la Sortie Exactes du Projet

Pour bien coder, il faut d'abord comprendre comment la donnée entre et comment elle doit ressortir.

### 📥 L'Entrée (Input)
L'entrée n'est **pas** un flux de données propre ou une base de données existante. L'entrée est le **Portail Web des appels d'offres**.
Concrètement, l'entrée est composée de :
- Des URL contenant des formulaires de recherche (Pages HTML ASP.NET).
- Des **Fichiers ZIP** téléchargés depuis ce portail.
- Des **Fichiers PDF** (contenus dans les ZIP) qui sont soit des documents numériques normaux, soit de simples images scannées (les plus difficiles à traiter).

### 📤 La Sortie (Output)
La sortie finale est une **Application Web Interactive (Plateforme GED)** permettant à un utilisateur final de :
- Rechercher un marché par mot-clé (ex: "Construction d'école à Casablanca").
- Visualiser les données structurées du document (Montant : 1 000 000 MAD, Date : 12/04/2026).
- Consulter un tableau de bord (Dashboard) affichant des statistiques globales (Graphiques sur les dépenses, répartition par région, etc.).
- Avoir une idée (Classification ML) du type de marché analysé de manière automatique.

---

## 2. Les Composants Clés du Projet (Architecture)

Le projet est divisé en 4 "couches" indépendantes. Chaque couche prend les données de la précédente, les transforme, et les donne à la suivante :

1. **Ingestion & Extraction (Le Mineur)** : Va sur internet, télécharge les ZIP, extrait les PDF, et lit le texte à l'intérieur (soit en lisant le texte directement, soit en "lisant l'image" avec l'OCR).
2. **NLP & ETL (Le Traducteur)** : Prend le texte brut et en déduit des informations. Par exemple, s'il voit "1 500 000,00 Dirhams", il comprend que c'est le `Montant`. Il stocke ensuite cela proprement dans la base de données.
3. **Le Backend / API (Le Serveur)** : C'est le pont. Il écoute les demandes du Frontend ("Donne-moi tous les marchés de 2025"), va interroger la base de données, et renvoie la réponse au format JSON.
4. **Le Frontend (La Vitrine)** : L'interface web qui affiche les données de l'API de manière esthétique (Tableaux, Graphiques, Formulaires).

---

## 3. Les Technologies et Notions à Maîtriser

Voici les concepts et les outils avec lesquels vous allez interagir. Il n'est pas nécessaire d'être un expert absolu dans tout, mais il faut en comprendre le rôle.

### 🕷️ A. Web Scraping (Collecte de données)
- **Notion** : Simuler le comportement d'un navigateur web pour lire le code HTML d'une page et télécharger des fichiers automatiquement.
- **Outils** : `requests` (pour faire les requêtes HTTP), `BeautifulSoup` (pour analyser le HTML).
- **À comprendre** : Comment fonctionnent les requêtes `GET` (récupérer une page) et `POST` (envoyer un formulaire de recherche).

### 📖 B. OCR (Reconnaissance Optique de Caractères)
- **Notion** : Transformer la photo d'un texte en véritable texte informatique modifiable.
- **Outils** : `Tesseract` (Moteur d'OCR), `PyMuPDF` (pour les PDF non scannés).
- **À comprendre** : L'OCR n'est jamais précis à 100%. Un "0" peut être confondu avec un "O". Il faudra nettoyer le texte après coup.

### 🧠 C. NLP (Traitement du Langage Naturel)
- **Notion** : Faire comprendre à l'ordinateur le sens du texte extrait.
- **Outils** : Expressions Régulières ou `Regex` (pour trouver des motifs exacts, ex: format d'une date JJ/MM/AAAA), `spaCy` (pour détecter des entités complexes comme le nom d'une entreprise).
- **À comprendre** : La différence entre la reconnaissance de motifs exacts (Regex) et la compréhension du langage (spaCy).

### 🗄️ D. Base de Données et ORM
- **Notion** : Stocker les données de façon relationnelle (en tables liées entre elles).
- **Outils** : `PostgreSQL` (La base de données puissante), `SQLAlchemy` (L'ORM).
- **À comprendre** : Ce qu'est un ORM. L'ORM vous permet de parler à la base de données en utilisant du code Python (Objets) plutôt que d'écrire des requêtes SQL "brutes".

### 🔌 E. API Backend
- **Notion** : Créer des points d'accès (URLs) pour que le Frontend puisse demander ou envoyer des données.
- **Outils** : `FastAPI`.
- **À comprendre** : Le fonctionnement des API REST (Méthodes HTTP : `GET`, `POST`, `PUT`, `DELETE`) et le format d'échange de données `JSON`.

### 💻 F. Frontend Moderne
- **Notion** : Créer l'interface utilisateur web dynamique (sans recharger la page).
- **Outils** : `React` (Création de composants UI), `Tailwind CSS` (Design et style rapide), `Recharts` (Graphiques).
- **À comprendre** : Le concept de "Composant" en React. Une barre de recherche est un composant, un tableau est un composant.

---

## 4. Questions Utiles à Garder en Tête (Pendant le développement)

Pour réussir ce MVP (Minimum Viable Product), posez-vous toujours ces questions avant de coder :

1. **"Est-ce que j'ai vraiment besoin de ML pour ça ?"**
   Souvent, une simple expression régulière (`Regex`) suffit pour extraire un numéro de marché. Ne sortez pas l'Intelligence Artificielle complexe si une règle simple fonctionne à 95%.
2. **"Comment gérer les erreurs d'OCR ?"**
   Prévoyez toujours dans votre base de données des champs permettant d'accueillir du texte imparfait. Ne forcez pas un type strict si vous n'êtes pas sûr de la qualité de la donnée.
3. **"Où stocker les PDF lourds ?"**
   Les PDF téléchargés ne doivent pas être stockés dans la base de données (qui deviendrait trop lourde), mais dans des dossiers (`data/raw/`). La base de données ne stockera que le *chemin* (le lien) vers ces fichiers.
4. **"Est-ce que je dois tout faire tout de suite ?"**
   **NON.** Testez votre pipeline complet sur **un seul document** d'abord. (Téléchargement d'un ZIP -> OCR -> Base de données -> Affichage sur le Web). Une fois que cela marche pour 1 document, on passe à 10, puis à 100.
