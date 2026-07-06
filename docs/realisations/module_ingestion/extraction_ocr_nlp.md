# Module d'Ingestion & Extraction Avancée (OCR / NLP)

## 1. Objectif du Module
Ce module constitue le cœur de la GED intelligente. Il est chargé de recevoir des archives brutes (ZIP, RAR) ou des documents isolés (PDF scannés, DOCX) et d'en extraire la donnée métier structurée.

## 2. Technologies Utilisées
- **Python (PyMuPDF / fitz)** : Lecture native des PDF textes.
- **Tesseract OCR / pdf2image** : Reconnaissance Optique de Caractères pour les documents scannés ou images.
- **Python `docx`** : Parsing des documents Word modernes (CPS, RC).
- **Regex & NLP Heuristique** : Expressions régulières avancées pour la détection des clauses clés (Budget, Délais, Agréments).
- **LLM Fallback (Google Gemini / OpenAI)** : Appel à l'IA générative en cas d'échec de la logique déterministe (fallback).

## 3. Flux de Traitement (Pipeline)
1. **Réception** : L'API FastAPI reçoit le fichier via upload (`python-multipart`).
2. **Décompression** : Le script extrait le ZIP, nettoie les fichiers systèmes Mac/Windows (`__MACOSX`, `Thumbs.db`).
3. **Routage Mime-Type** : Chaque document est routé vers le bon moteur (Word vers `docx`, PDF scanné vers Tesseract).
4. **Structuration** : Les données extraites sont standardisées dans un schéma Pydantic (`DocumentAOCreate`).
5. **Persistance** : Sauvegarde dans la base de données relationnelle.
