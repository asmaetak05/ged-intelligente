# Note de Décision - Sprint J5 : Modélisation et Base de Données

**Projet :** GED Intelligente
**Date :** 6 Juillet 2026
**Sujet :** Validation du dictionnaire de données et implémentation de la base de données.

## 1. Contexte technique
Lors du déploiement de la base de données (J5), nous avons constaté que l'environnement Docker n'était pas encore accessible globalement sur la machine de développement locale. 
**Décision architecturale :** Pour ne pas bloquer le développement de la couche d'intelligence artificielle, nous avons implémenté **SQLAlchemy**, un ORM (Object-Relational Mapper). Cela nous a permis d'initialiser immédiatement une base de données **SQLite locale** (`ged.db`), avec une compatibilité totale pour basculer sur **PostgreSQL** d'un simple changement de variable d'environnement (URL) lors du passage en production.

## 2. Dictionnaire de Données V1 (Modèle SQLAlchemy)
La table principale `appels_offres` a été créée avec les colonnes suivantes :

| Champ SQL | Type | Description / Origine |
| :--- | :--- | :--- |
| `id` | Integer (PK) | Identifiant unique interne |
| `numero_ordre` | String (Indexé)| Numéro d'ordre issu du portail (ex: 65060956) |
| `objet` | Text | Description complète extraite par l'IA des documents (.pdf, .docx) |
| `estimation_mad` | String | Montant estimé par l'État (capturé via expressions régulières/NLP) |
| `caution_mad` | String | Caution provisoire requise pour participer |
| `lieu_execution` | String | Province ou ville concernée |
| `fichier_source` | String | Traçabilité : Nom du fichier ZIP d'origine |
| `date_ingestion` | DateTime | Horodatage de l'intégration dans le système |

## 3. Avancées du jour
- [x] Détection automatique et extraction du texte des fichiers ZIP réels (Word/PDF).
- [x] Pipeline NLP (Regex de base) fonctionnel pour capturer le bloc "Objet".
- [x] Code base de données (Modèles ORM) et scripts d'initialisation développés.
- [x] Base de données locale générée et prête à recevoir des données.

## 4. Prochaines étapes (Sprint Semaine 2)
1. Brancher le script d'extraction (`extractor.py`) pour qu'il sauvegarde automatiquement les résultats (Objet, Montant, etc.) dans notre nouvelle base de données `ged.db`.
2. Mettre en place l'API (FastAPI) pour pouvoir consulter ces données via une interface web ou des requêtes HTTP.
3. Affiner l'IA (spaCy) pour les cas où le montant est difficile à lire dans des phrases complexes.

---
*Veuillez valider cette note de décision pour que nous puissions entamer l'intégration de la sauvegarde dans la BDD et le développement de l'API (J6/J7).*
