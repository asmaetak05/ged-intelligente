# Plan d'Exécution : Finalisation de la GED Intelligente (PFA)

Ce document décrit le plan technique précis pour l'implémentation des deux chantiers critiques finaux : le Dashboard React (Front-end) et le Full-Text Search PostgreSQL (Back-end).

---

## Tâche 1 : Développement du Dashboard React & Recharts (Front-end)

L'objectif est de remplacer l'interface web basique par une véritable application Single Page Application (SPA) professionnelle, respectant la maquette SaaS.

**Étape 1 : Architecture des Composants (Dossier `frontend-react/src/components/`)**
*   Création de `Sidebar.jsx` : Menu de navigation fixe avec icônes (`lucide-react`) contenant les liens vers (Tableau de bord, Recherche FTS, Explorateur, Monitoring).
*   Création de `Topbar.jsx` : Barre supérieure affichant le statut du système et l'utilisateur.
*   Création de `Layout.jsx` : Conteneur principal englobant Sidebar, Topbar et le contenu dynamique (React Router).

**Étape 2 : Implémentation de la Vue `Dashboard.jsx`**
*   **KPIs (Section 1) :** Création d'une grille de 4 "Widgets Cards" affichant les totaux financiers et le taux OCR.
*   **Graphiques (Section 2) :** Intégration de `Recharts` pour coder :
    *   Un `PieChart` pour la distribution des catégories (Travaux, Études...).
    *   Un `BarChart` pour le Top 10 des Acheteurs.
*   **Connexion API :** Utilisation d'`axios` pour lier ces composants aux routes FastAPI `/api/v1/analytics/kpis` et `/api/v1/analytics/distribution/categories`.

---

## Tâche 2 : Implémentation du Full Text Search PostgreSQL (Back-end)

L'objectif est de doter la base de données d'un moteur de recherche instantané (type Google) capable de fouiller dans les centaines de pages des CPS et RC sans ralentir le serveur.

**Étape 1 : Configuration de la Base de Données (`models.py`)**
*   Activation de l'extension `pg_trgm` dans la base PostgreSQL si nécessaire.
*   Ajout d'un Index `GIN` (Generalized Inverted Index) sur la colonne `tsv_search` de la table `Marche` pour garantir des performances de recherche en quelques millisecondes.

**Étape 2 : Création des Triggers de Vectorisation**
*   Création d'un événement SQLAlchemy (`listen(Marche, 'before_insert')`) ou d'un trigger SQL pur. 
*   **Logique :** À chaque insertion d'un marché, ce trigger va concaténer le titre du projet, le nom de la province, et surtout le *contenu brut* extrait par l'OCR, pour les passer dans la fonction `to_tsvector('french', text)`. PostgreSQL va ainsi "tokeniser" (raciniser) tous les mots.

**Étape 3 : Mise à jour de l'Endpoint de Recherche (`main.py`)**
*   Réécriture de la route `GET /api/v1/ged/search`.
*   **Requête SQL :** Au lieu d'utiliser un lent `LIKE '%mot%'`, l'API utilisera la syntaxe PostgreSQL FTS : `Marche.tsv_search.match(func.to_tsquery('french', query))`.
*   **Filtres conditionnels :** Ajout des filtres dynamiques (par catégorie, par seuil de budget) combinés à la recherche plein texte.
