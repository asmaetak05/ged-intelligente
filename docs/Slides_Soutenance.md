# Slides Soutenance - GED Intelligente

---

## Slide 1 : Titre
**GED Intelligente - Automatisation, IA et BI appliquées aux Appels d'Offres**
*Soutenance de Projet de Fin d'Études*

---

## Slide 2 : La Problématique
- **Contexte** : Des milliers de DCE (Dossiers de Consultation des Entreprises) publiés sous format PDF (souvent scannés).
- **Problème** : Données enfouies, impossibilité de faire des statistiques, perte de temps lors de la recherche.
- **Enjeu** : Extraire, structurer et visualiser l'information financière et technique.

---

## Slide 3 : La Solution Proposée
Une application web complète (GED Intelligente) :
1. **Un bot d'acquisition (Scraping)** pour aspirer le portail gouvernemental.
2. **Un pipeline OCR/NLP** pour extraire intelligemment l'objet, le maître d'ouvrage et les montants.
3. **Un moteur Machine Learning** pour la classification et la détection d'anomalies.
4. **Un tableau de bord BI (React)** pour la data visualisation.

---

## Slide 4 : Architecture L1 -> L4
*Insérer Schéma issu de `architecture.md`*
- Focus sur la modularité : chaque couche peut évoluer ou être remplacée indépendamment.
- Stack Technique : Python, FastAPI, SQLAlchemy, React JS, Scikit-learn, Tesseract.

---

## Slide 5 : Focus sur la pipeline OCR / NLP
**Pourquoi deux moteurs ?**
- `PyMuPDF` est exécuté en premier : très rapide (millisecondes), mais échoue si le PDF est une image scannée.
- Si le rendement texte est faible, le système lance un "Fallback" vers `Tesseract OCR` pour numériser l'image.
- Les données passent ensuite dans un algorithme Regex/spaCy pour extraire l'information ciblée (Montants, Dates).

---

## Slide 6 : Intelligence Artificielle
- **Baseline de Classification (SVM + TF-IDF)** : Prédiction automatique de la catégorie (Travaux, Fournitures...) basée sur l'analyse NLP du texte.
- **Détection d'Anomalies** : Modèle `IsolationForest` qui met en évidence les appels d'offres suspects financièrement (via un indicateur visuel sur l'interface).

---

## Slide 7 : Démonstration (Live Demo)
1. Affichage du Dashboard Analytics mis à jour en temps réel.
2. Lancement d'un Upload asynchrone (Mock fichier zip corrompu vs succès).
3. Utilisation de la barre de Recherche Sémantique (FTS).
4. Affichage d'un détail d'Appel d'Offre et de sa classification IA.

---

## Slide 8 : Fiabilité & Tests
- Filet de sécurité assuré par 31 tests unitaires (`pytest`).
- Taux de couverture de code (Coverage) atteignant **70%**.
- Validation systématique via requêtes client HTTPX sur l'API FastAPI.

---

## Slide 9 : Bilan & Perspectives
- **Objectif atteint** : Une application démontrable, fonctionnelle, robuste et scalable.
- **Evolutions futures** : Déploiement sur un environnement Cloud, Intégration de modèles génératifs de pointe (LLM) pour extraire de l'information complexe à faible volume d'erreurs.

---
**Merci pour votre attention ! Des questions ?**
