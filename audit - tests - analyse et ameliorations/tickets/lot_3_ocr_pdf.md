# 🎫 Lot 3 : Traitement OCR & PDF (OCR & PDF Processing)

## 📌 Présentation du Lot
Ce lot améliore l'efficacité et la qualité de la reconnaissance de caractères (OCR) sur les documents numérisés, en ajoutant la gestion du bilinguisme (Français/Arabe), un cache des pages déjà traitées, et la tolérance aux pannes sur les gros PDF.

* **Complexité globale** : Medium
* **Composants impactés** : `ocr/`, `backend/tasks.py`
* **Indépendance git** : Excellente. Le traitement OCR est isolé dans son dossier et appelé asynchronement. Il n'y a pas d'impact sur le frontend ni sur les modèles de machine learning.

---

## 📋 Liste des Tickets Associés

### 1. OC-01 — Cache OCR (SHA-256 de page) 🟠
* **Priorité** : 🟠 P1
* **Effort** : M (2 j)
* **Composant** : `ocr/extract_ocr.py`, `backend/models.py`
* **Scénarios de test liés** : `ST-OC-001`, `ST-OC-002`
* **Description** : Pour éviter de refaire l'OCR d'un document déjà traité lors d'une ré-ingestion ou d'une correction, stocker le texte extrait indexé par le SHA-256 de l'image de la page.
* **Travail** : Vérifier la présence du hash avant d'appeler Tesseract.

### 2. OC-04 — Reprise OCR après crash (page par page) 🔴
* **Priorité** : 🔴 P0
* **Effort** : S (1 j)
* **Composant** : `backend/tasks.py`
* **Scénarios de test liés** : `ST-OC-009`
* **Description** : Pour les PDF volumineux (> 100 pages), si le serveur ou la tâche de fond crashe à la page 50, la reprise doit continuer à partir de la page 50 au lieu de recommencer depuis le début.
* **Travail** : Mettre à jour l'état de traitement de la tâche avec l'index de la dernière page validée dans `OcrLog`.

### 3. OC-05 — Prétraitement d'image avancé (denoise, deskew) 🟠
* **Priorité** : 🟠 P1
* **Effort** : M (2 j)
* **Composant** : `ocr/preprocess.py`
* **Scénarios de test liés** : `ST-OC-011`
* **Description** : Améliorer le taux de reconnaissance (WER/CER) pour les documents scannés de mauvaise qualité ou de biais.
* **Travail** : Utiliser OpenCV pour effectuer un redressement d'angle (deskew) et une réduction du bruit numérique (denoise) avant de passer l'image à Tesseract.

### 4. OC-06 — OCR bilingue FR/AR par page 🟠
* **Priorité** : 🟠 P1
* **Effort** : M (2 j)
* **Composant** : `ocr/extract_ocr.py`
* **Scénarios de test liés** : `ST-OC-005`, `ST-OC-015`
* **Description** : Les avis de marchés publics marocains contiennent souvent des parties en français et d'autres en arabe. Configurer Tesseract pour charger les deux langages simultanément.
* **Travail** : Configurer l'initialisation de pytesseract avec `lang='fra+ara'`.

---

## 🛠️ Description des Travaux
1. **Intégration d'OpenCV dans `ocr/preprocess.py`** :
   - Écrire les fonctions de nettoyage de l'image (seuillage adaptatif, suppression des lignes parasites).
2. **Refactoring de l'orchestrateur de tâches `backend/tasks.py`** :
   - Diviser le traitement du PDF en sous-tâches par lot de 10 pages.
   - Enregistrer le texte intermédiaire au fur et à mesure.

---

## 🧪 Critères de Validation et Non-régression
- **Test de bilinguisme** : Passer un PDF contenant un tableau avec des en-têtes en français et du contenu en arabe, et s'assurer que les caractères arabes ne sont pas convertis en symboles corrompus (garbage text).
- **Test de reprise** : Tuer le processus Celery / worker au milieu du traitement d'un long PDF, relancer, et vérifier dans les logs que le traitement redémarre à la page de coupure.
