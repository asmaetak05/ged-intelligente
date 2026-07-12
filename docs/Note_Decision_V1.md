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

---

## 5. Décision Phase 1 — Choix du moteur BDD (12 juillet 2026)

**Contexte de la décision** : Au moment de l'audit (cf. `docs/ANALYSE_ET_PLAN_ACTION.md`),
l'API utilise **deux moteurs en parallèle** :

- `backend/database.py:7` → pointe PostgreSQL (`postgresql://admin:password@localhost:5432/ged_db`)
- `backend/main.py:30` → ouvre `ged.db` (SQLite brut via `sqlite3.connect()`)

Cette double architecture empêche l'API de fonctionner hors SQLite, mais les modèles
`backend/models.py` sont écrits pour PostgreSQL (TSVECTOR, ARRAY). Conséquence :
`Base.metadata.create_all(bind=engine)` (main.py:15) échoue silencieusement
si PostgreSQL n'est pas accessible, et tout le code de `main.py` lit `ged.db`
directement sans passer par les modèles ORM.

### Options évaluées

| Option | Avantages | Inconvénients |
|---|---|---|
| **A. PostgreSQL uniquement** (forcer Docker) | Modèles natifs, FTS GIN, scalable | Impose Docker au jury, démarrage plus lent |
| **B. SQLite uniquement** (réécrire modèles) | Zéro infra, démarrage instantané | FTS moins riche, pas de `ARRAY`/`TSVECTOR` natifs |
| **C. Bascule auto via `DATABASE_URL`** (recommandé) | Code identique, choix au runtime | Légère complexité dans `database.py` |

### Décision retenue : **Option C — Bascule automatique**

**Justification** :

1. La BDD contient déjà **12 AO** (cf. `ged.db.bak`) → on ne repart pas de zéro.
2. Le jury doit pouvoir lancer la démo en un `uvicorn backend.main:app` sans Docker.
3. SQLAlchemy 2.0 supporte SQLite et PostgreSQL de manière transparente.
4. Les types PostgreSQL-spécifiques (`TSVECTOR`, `ARRAY`) sont remplaçables :
   - `TSVECTOR` → `Text` (indexé, mais recherche en LIKE / LIKE %X%)
   - `ARRAY(String)` → `JSON` (équivalent pour ce POC)
5. PostgreSQL reste activable pour la démo "prod" via :
   ```bash
   export DATABASE_URL=postgresql://admin:password@localhost:5432/ged_db
   docker compose up -d db
   alembic upgrade head
   ```

**Conséquences techniques** (référence : `docs/implementation/phase-01-unification-bdd.md`) :

- T1.1 : réécrire `models.py` sans `TSVECTOR` ni `ARRAY` (utiliser `Text` et `JSON`).
- T1.2 : réécrire `database.py` pour détecter `DATABASE_URL` et choisir le driver.
- T1.4 : réécrire `main.py` (suppression des `sqlite3.connect`).
- T1.6 : configurer Alembic (les migrations fonctionnent en SQLite ET PostgreSQL).
- T1.8 : suppression du doublon `scripts/init_db.py` (déjà à 0 octet).

**Statut** : ✅ Validé le 12 juillet 2026.
**Ticket lié** : T0.4, T1.1, T1.2, T1.4, T1.6, T1.8.

