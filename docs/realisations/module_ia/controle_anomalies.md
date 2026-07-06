# Module d'Intelligence Artificielle & Contrôle ML

## 1. Objectif du Module IA
Dans un contexte de marchés publics, les erreurs de saisie humaine (mauvaise catégorisation d'un marché) sont fréquentes. Ce module utilise le Machine Learning pour vérifier la cohérence des données extraites.

## 2. Modèles Déployés
- **Isolation Forest** : Algorithme de détection d'anomalies non-supervisé. Il identifie les Appels d'Offres dont le budget ou les délais sont mathématiquement "hors norme" par rapport à leur catégorie.
- **Support Vector Machine (SVM) / RandomForest** : Modèle de classification supervisée entraîné sur les données historiques. Il "lit" l'objet du marché et prédit la catégorie réelle (Travaux, Fournitures, Études).

## 3. Pipeline de "Watchlist"
Si l'humain saisit qu'un marché concerne des "Fournitures", mais que l'IA détecte la présence de "Bordereau de prix de main d'œuvre" et le classifie à 94.2% comme "Travaux", le système lève une **Alerte**.
Cette alerte est affichée sur l'écran **Predictor ML** de l'interface, permettant à un contrôleur humain d'auditer et de corriger le dossier.
