# 02 — Extraction documentaire et OCR bilingue

**Priorité du module : P0/P1.** Le but n'est pas seulement d'obtenir du texte, mais de connaître sa qualité et sa provenance.

## OCR-01 — Unifier la stratégie d'extraction

**État : Partiel.** `ocr/extract_native.py`, `ocr/extract_ocr.py` et `ingestion/extractor.py` se chevauchent ; certains chemins font appel directement à `pytesseract.image_to_string`.

### Réalisation attendue

1. Créer `ocr/service.py` comme unique point d'entrée : `extract_document(document_path, language_hint)`.
2. Définir un résultat typé : texte, pages, moteur utilisé, nombre de pages, durée, erreurs, qualité et version moteur.
3. Déléguer PDF natif à `extract_native.py`, OCR à `extract_ocr.py`, prétraitement à `preprocess.py`.
4. Faire une détection document/page par page : conserver le texte natif quand il est suffisant, OCRiser seulement les pages nécessaires.
5. Supprimer les appels OCR redondants de `ingestion/extractor.py` après migration.

### Critères d'acceptation

- toute extraction passe par une unique interface ;
- le résultat indique exactement quelle méthode a été appliquée par page ;
- un PDF natif n'est pas OCRisé inutilement ;
- un test couvre PDF natif, scan et document mixte.

## OCR-02 — Rendre Tesseract portable et configurable

**État : Partiel.** `ocr/extract_ocr.py` fixe le chemin `C:\Program Files\Tesseract-OCR\tesseract.exe`.

### Réalisation attendue

1. Lire `TESSERACT_CMD`, `TESSERACT_LANGUAGES`, `OCR_DPI` et `OCR_TIMEOUT` depuis la configuration.
2. Détecter au démarrage la disponibilité de Tesseract, Poppler et des langues `fra`/`ara`.
3. Ajouter endpoint interne ou commande de diagnostic ne révélant pas d'information sensible.
4. Mettre à jour Dockerfile, README et `docs/Checklist_Environnement.md`.
5. Ajouter des tests qui mockent l'absence de Tesseract et vérifient un échec métier clair.

### Critères d'acceptation

- aucun chemin absolu Windows dans le code métier ;
- la plateforme indique clairement si `fra` ou `ara` manque ;
- le même code fonctionne sous Windows et Docker Linux avec configuration adaptée.

## OCR-03 — Stocker qualité et preuve au niveau page

**État : À faire.** La table `OcrLog` stocke une confiance globale, mais le pipeline n'expose pas de qualité suffisante par page ni de métrique métier.

### Réalisation attendue

1. Ajouter modèle/migration `document_pages` : page, texte, moteur, langue, confiance technique, durée, image rendue optionnelle.
2. Utiliser `pytesseract.image_to_data` pour enregistrer une confiance technique par mot/page, distincte d'une exactitude métier.
3. Ajouter seuils configurables : `OCR_REVIEW_THRESHOLD` et statut `review_required`.
4. Créer endpoint de consultation des pages et afficher les pages faibles dans la fiche document.
5. Ajouter métriques : nombre de pages, pages OCR, confiance moyenne, pages à revoir.

### Critères d'acceptation

- une page problématique est localisable ;
- aucun score technique n'est présenté comme exactitude humaine ;
- l'utilisateur peut ouvrir une page et son texte associé.

## OCR-04 — Évaluer objectivement l'OCR

**État : À faire.** Aucun CER/WER ni jeu de vérité terrain n'est disponible.

### Réalisation attendue

1. Créer `data/ground_truth/` ou dépôt protégé contenant transcriptions validées des documents échantillons.
2. Créer `scripts/evaluate_ocr.py` qui calcule CER et WER par document, langue et type de PDF.
3. Générer `docs/metrics/OCR_BASELINE.md` avec date, corpus, version Tesseract, paramètres et résultats.
4. Définir les cas où l'OCR passe automatiquement, nécessite revue ou est rejeté.

### Critères d'acceptation

- un rapport reproductible est généré ;
- les résultats français, arabe et bilingue sont séparés ;
- la soutenance cite des métriques, pas seulement un score Tesseract.

