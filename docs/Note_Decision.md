# Note de Décision (J5)

**Projet :** GED Intelligente des Marchés Publics
**Date :** Juillet 2026

Suite aux travaux d'exploration et de tests réalisés lors de la première semaine, l'équipe de développement acte les décisions techniques suivantes pour la suite du projet :

## 1. Choix Technologiques Validés
- **Base de Données :** PostgreSQL 16 est retenu pour sa fonction "Full Text Search" (FTS) intégrée, vitale pour ce projet. (Réf : `docker-compose.yml` créé).
- **Backend / API :** Python 3.11 avec FastAPI pour sa vitesse de développement et son typage (Pydantic).
- **Extraction PDF :** Stratégie hybride validée : `PyMuPDF` en priorité (pour la performance), et `Tesseract OCR` en solution de repli pour les images scannées.

## 2. Définition du MVP (Minimum Viable Product)
Le périmètre des 4 prochaines semaines sera restreint pour garantir un livrable fonctionnel :
1. Téléchargement automatique des ZIP via Scraping.
2. Extraction hybride (Natif/OCR).
3. Structuration NLP (`spaCy` + `regex`) sur un Dictionnaire de Données restreint (Titre, Référence, Montant, Dates, Organisme).
4. API de consultation et Frontend basique (Recherche).

**Ce qui est repoussé / non prioritaire :**
- L'OCR avancé sur l'Arabe (Tesseract Arabe sera testé mais non garanti).
- Les modèles complexes de Machine Learning : seront abordés uniquement si l'API et la BDD sont 100% stables. (Le ML de base se limitera à une classification thématique).

---
*Fin de la Phase Cadrage (Semaine 1).*
