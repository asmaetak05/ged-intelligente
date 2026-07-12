# Guide Utilisateur - GED Intelligente

Bienvenue dans le guide utilisateur de la **GED Intelligente**, l'application qui vous permet de collecter, analyser et rechercher automatiquement des appels d'offres marocains à l'aide de l'Intelligence Artificielle.

## 1. Vue d'ensemble du Dashboard

À la connexion, la page d'accueil affiche un tableau de bord analytique mis à jour en temps réel :
- **Indicateurs Clés (KPIs)** : Volume total, taux de réussite de l'OCR (reconnaissance des textes), budget moyen.
- **Répartition par catégorie** : Un graphique circulaire classant les appels d'offres en Travaux, Fournitures, Études, Services.
- **Top Acheteurs** : Les organismes émettant le plus grand volume d'appels d'offres.
- **Tendances temporelles** : Volume de publication sur les 12 derniers mois.

## 2. Ingestion de nouveaux documents

1. Allez dans l'onglet **Upload**.
2. Glissez-déposez un dossier `.zip` contenant le Dossier de Consultation des Entreprises (DCE).
3. Une fois téléchargé, le serveur prend le relai. Il va :
   - Extraire le texte des PDF et fichiers Word (OCR).
   - Analyser le texte (NLP) pour isoler le titre, le maître d'ouvrage, les pénalités, etc.
   - Envoyer le texte à l'algorithme de Machine Learning pour prédire la catégorie et détecter des anomalies.
4. Une barre de progression vous indique le statut (Raw -> Traitement -> Succès).

## 3. Recherche Intelligente (Full Text Search)

1. Naviguez vers l'onglet **Explorateur** ou **Recherche**.
2. Saisissez des mots clés (ex: "matériel informatique"). Le moteur PostgreSQL Full-Text Search (ou SQLite FTS) retrouvera instantanément les documents pertinents.
3. Vous pouvez filtrer les résultats par région ou catégorie de prestation.

## 4. Détail d'un Appel d'Offres

En cliquant sur une ligne de résultat de recherche, vous accédez à la page détail :
- **Onglet Résumé** : Affichage des champs structurés extraits par l'IA (montant estimatif, délai, pénalités).
- **Onglet Prédiction ML** : Vous pouvez visualiser la catégorie qui a été assignée de manière automatisée et l'indice de confiance du modèle. Si une valeur atypique est détectée sur l'estimation financière, un avertissement rouge s'affiche.
- **Onglet Texte Brut** : Consultez l'intégralité du texte extrait par l'OCR sans avoir besoin d'ouvrir de document PDF.

## 5. Espace Intelligence Artificielle

En bas de la page, ou via l'onglet **Machine Learning**, vous avez accès à un bouton "Ré-entraîner le modèle". Si de nombreuses corrections humaines ont été apportées, cela relance un entraînement du modèle SVM en arrière-plan pour s'adapter à vos nouvelles données.
