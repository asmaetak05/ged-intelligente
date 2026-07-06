# Dictionnaire de Données V1 (GED Marchés Publics)

Ce document définit les champs qui seront extraits et stockés en base de données.

## Table `marches` (Données Métier)

| Champ | Type SQL | Description | Source d'extraction | Priorité |
| :--- | :--- | :--- | :--- | :--- |
| `id` | SERIAL | Identifiant unique interne | Généré (BDD) | - |
| `document_id` | INTEGER | Lien vers le document brut (ZIP/PDF) | Relationnel | - |
| `reference` | VARCHAR | Référence de l'appel d'offre (ex: 01/2026/EQUIP) | Regex sur le texte OCR | Obligatoire |
| `titre` / `objet` | TEXT | Description des travaux ou services | NLP (spaCy) + Regex | Obligatoire |
| `organisme` | VARCHAR | L'entité qui lance l'AO | NLP (spaCy) | Obligatoire |
| `categorie` | VARCHAR | Travaux, Fournitures, Services, Études | Scraping / ML baseline | Obligatoire |
| `date_parution` | DATE | Date de publication de l'AO | Scraping / dateparser | Obligatoire |
| `date_limite` | DATE | Date de clôture pour postuler | Scraping / dateparser | Obligatoire |
| `estimation` | NUMERIC | Montant estimé en MAD | Regex + Normalisation | Important |
| `caution_provisoire`| NUMERIC | Montant de la garantie demandée | Regex + Normalisation | Optionnel |
| `ville` / `region` | VARCHAR | Lieu d'exécution du marché | Scraping / NLP | Important |

## Table `documents` (Traçabilité)

| Champ | Type SQL | Description |
| :--- | :--- | :--- |
| `id` | SERIAL | Identifiant unique |
| `source_url` | TEXT | Lien exact vers le portail |
| `file_path` | TEXT | Chemin local du fichier ZIP (`data/raw/...`) |
| `document_type` | VARCHAR | AAO, Résultat, PV, Rectificatif |
| `status` | VARCHAR | Statut du traitement (nouveau, ocr_fait, extrait) |
