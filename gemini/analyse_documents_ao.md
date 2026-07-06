# Analyse des Documents de l'Appel d'Offres & Ingénierie d'Extraction

Ce document synthétise les données cruciales extraites du lot d'Appel d'Offres **N° SF 22/2025** (Objet : *Etude d’élargissement et de renforcement de la RR507 du PK 32+500 au PK 69+500*), et définit la méthode technique pour automatiser le traitement de ces archives ZIP.

---

## 1. Synthèse des Informations Extraites par l'IA

Au lieu d'obliger l'utilisateur à lire des centaines de pages, voici ce que l'analyse automatisée a permis d'isoler en croisant les différents fichiers :

### 📄 L'Avis d'Appel d'Offres (Le Résumé Public)
*   **Maître d'Ouvrage :** Ministère de l'Equipement et de l'Eau (Sefrou).
*   **Date limite (Ouverture des plis) :** 27 Août 2025 à 10 H 00.
*   **Budget estimatif (État) :** 307 320,00 DHS.
*   **Caution provisoire :** 4 300,00 DHS.

### 📕 Le CPS - Cahier des Prescriptions Spéciales (Le Contrat)
*   **Délai d'exécution :** 4 mois.
*   **Pénalités de retard :** 1 pour mille (1/1000) par jour de retard (Plafonné à 10%).
*   **Cautionnement définitif :** 3% du montant initial du marché.
*   **Retenue de garantie :** Aucune.

### 📘 Le RC - Règlement de Consultation (Les Règles du Jeu)
*   **Agréments exigés :** Certificats d’agrément dans les domaines **D4** et **D5** (Éliminatoire).
*   **Formule de notation :** Note Globale = (70% Technique) + (30% Financière). *Élimination si Note Technique < 70/100*.
*   **Seuils Financiers :** Rejet si l'offre est +20% (excessive) ou -25% (anormalement basse) par rapport à l'estimation (307 320 DHS).
*   **Profils Humains exigés (Note Technique sur 85 pts) :**
    *   *Chef de projet (35 pts)* : Ing. d'État Génie Civil, idéalement >20 ans d'expérience.
    *   *Ingénieur Génie Civil (20 pts)*.
    *   *Ingénieur en Hydraulique (20 pts)*.
    *   *Ingénieur Topographe (10 pts)* : Inscription obligatoire à l'Ordre (ONIGT).

### 📓 Les Modèles (Déclaration sur l'Honneur & Acte d'Engagement)
*   Ce sont des **formulaires vierges**. Ils ne contiennent aucune règle supplémentaire à cette étape. 
*   *Utilité future :* L'IA pourra les analyser via OCR une fois qu'ils seront remplis et signés par les entreprises concurrentes pour extraire leur offre financière (Montant TTC proposé).

---

## 2. Méthodologie Technique : Comment manipuler ces archives ZIP et fichiers Word ?

Pour industrialiser cette extraction (ce que fait notre script `extractor.py`), voici l'architecture technique exacte à mettre en place pour manipuler les ZIP du portail des marchés publics :

### Étape A : Décompression Sécurisée
1.  **Module `zipfile` (Python) :** Réception du fichier `.zip` téléchargé.
2.  **Extraction en mémoire ou disque temporaire :** Le script désarchive le contenu dans un dossier temporaire.
3.  **Filtrage :** Ignorer les fichiers temporaires de Windows/Office (ceux qui commencent par `~$`) qui font planter les lecteurs.

### Étape B : Traitement des Fichiers (Trois formats distincts)
Dans les marchés publics, on retrouve très souvent le vieux format binaire de 1997, le format XML moderne, et des PDFs scannés. Ils ne se lisent pas de la même manière :
1.  **Le format moderne `.docx` (Ex: Le CPS Sefrou) :**
    *   Il s'agit techniquement d'un ZIP contenant du XML (OOXML).
    *   **Outil :** La bibliothèque Python `python-docx` permet de parcourir directement l'arbre du document et d'en extraire le texte proprement.
2.  **Le vieux format `.doc` (Ex: L'Avis et le RC Sefrou) :**
    *   C'est un format binaire propriétaire (OLE2).
    *   **Outil sous Windows :** Utilisation de l'API COM (`win32com.client`) pour piloter Microsoft Word en arrière-plan.
3.  **Les fichiers `.pdf` scannés (Ex: Avis, CPS et RC de l'ANEP) :**
    *   Il arrive fréquemment (comme pour le lot 65058758) que les administrations impriment, signent, puis scannent les documents. Le PDF résultant ne contient aucune couche de texte, uniquement des images.
    *   **Outil obligatoire :** Un moteur d'OCR (Optical Character Recognition) tel que **Tesseract** (via `pytesseract`) ou une API Cloud Vision / Document AI est indispensable pour extraire le texte avant l'analyse sémantique. Sans OCR, l'extraction est impossible.

### Étape C : Pipeline d'Extraction d'Intelligence Artificielle
Une fois le texte brut récupéré, on applique l'intelligence :
1.  **Nettoyage (Clean-up) :** Retrait des espaces multiples, sauts de lignes inutiles, et normalisation de l'encodage (UTF-8).
2.  **Extraction Regex (Rapide et déterministe) :** Pour les données très normées (ex: *"Délai d'exécution : 4 mois"*), les expressions régulières (`re.search`) sont extrêmement rapides et fiables à 99%.
3.  **Analyse Sémantique (Optionnelle mais puissante) :** Utilisation de bibliothèques NLP (spaCy) ou d'appels à un LLM externe pour comprendre des tableaux complexes (comme la grille de notation de l'équipe technique dans le RC).
4.  **Ingestion Base de données :** Le script formate ces entités trouvées en JSON et les envoie (via requête HTTP POST) vers notre API FastAPI pour alimenter le Dashboard.
