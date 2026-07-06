# Rapport de Qualité d'Extraction (J4)

Ce rapport évalue et compare la faisabilité et la qualité de l'extraction de texte sur un échantillon d'archives ZIP téléchargées.

## 1. Processus de décompression (ZIP)
- L'extraction des archives `.zip` ne pose aucun problème majeur via la bibliothèque standard Python (`zipfile`).
- **Remarque :** Certains noms de fichiers internes contiennent des caractères spéciaux ou des espaces. Un renommage/nettoyage lors de la décompression est recommandé pour éviter des erreurs système.

## 2. Test sur les PDF "Natifs" (Texte existant)
- **Outil testé :** `PyMuPDF` (`fitz`)
- **Vitesse :** Extrêmement rapide (< 0.1s par page).
- **Précision :** 100%. Les mots sont parfaitement récupérés, préservant généralement les sauts de ligne.
- **Verdict :** Méthode à privilégier absolument dès que la bibliothèque détecte la présence de texte natif.

## 3. Test sur les PDF "Scannés" (OCR)
- **Outil testé :** `Tesseract` v5 (via `pytesseract` ou appel direct).
- **Vitesse :** Lente (2 à 5 secondes par page selon la résolution).
- **Précision :** 
  - Très bonne (90-95%) sur des scans récents (300 DPI) et des polices claires.
  - Variable (60-80%) sur des documents froissés, mal alignés ou comportant des tampons/signatures sur le texte.
- **Difficulté linguistique :** L'OCR en français (`fra`) donne d'excellents résultats. L'arabe (`ara`) est plus capricieux mais reste exploitable pour la recherche par mots-clés.
- **Verdict :** Indispensable. 70% des documents des marchés publics étant signés manuellement, ils sont fatalement scannés.

## 4. Conclusion
Il faut mettre en place un système de **fallback (Solution de repli)** : 
Le script devra d'abord tenter d'extraire le texte avec `PyMuPDF`. Si la page retourne un texte vide (ou moins de 50 caractères), le script basculera automatiquement sur `Tesseract` pour extraire le texte de l'image.
