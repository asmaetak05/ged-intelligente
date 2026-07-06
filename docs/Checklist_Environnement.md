# Checklist Environnement (J2)

| Composant | Statut | Commentaire |
| :--- | :--- | :--- |
| **Python** | ✅ Validé | Version 3.11.9 installée. Environnement virtuel `.venv` créé. |
| **Node.js** | ✅ Validé | Version 22.17.1 installée. (Au lieu de 20, mais compatible et meilleur). |
| **Git** | ✅ Validé | Version 2.54.0 installée. |
| **Dépendances Python** | ✅ Validé | `FastAPI`, `SQLAlchemy`, `PyMuPDF`, `Scikit-Learn`, etc. installés via le fichier `requirements.txt`. |
| **Modèle NLP (spaCy)** | ✅ Validé | Modèle `fr_core_news_sm` téléchargé avec succès pour le traitement du Français. |
| **Dépendances Frontend** | ✅ Validé | `React`, `Vite`, `Tailwind CSS v4` installés et configurés dans le dossier `frontend`. |
| **PostgreSQL / Docker** | ❌ À finaliser | Le fichier `docker-compose.yml` est prêt. **Action requise :** L'utilisateur doit installer Docker Desktop sous Windows pour lancer la base de données. |
| **Tesseract OCR** | ❌ À finaliser | Moteur d'OCR manquant dans le PATH. **Action requise :** L'utilisateur doit installer l'exécutable Windows (Tesseract-OCR) avec les packs de langue (fra, ara). |
