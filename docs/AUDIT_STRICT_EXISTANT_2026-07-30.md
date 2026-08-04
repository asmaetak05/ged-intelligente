# Audit strict de l'existant — GED intelligente

**Projet :** traitement intelligent des dossiers d'appels d'offres du Ministère de l'Équipement et de l'Eau du Maroc  
**Date de l'audit :** 30 juillet 2026  
**Nature de l'évaluation :** revue documentaire, revue statique du code, inventaire des données et tentatives d'exécution  
**Positionnement :** audit volontairement sévère ; une fonctionnalité non démontrée, non mesurée ou non testable est considérée comme non acquise.

## 1. Verdict exécutif

Le dépôt contient un **prototype académique substantiel**, mais il ne constitue ni une GED complète, ni un produit ministériel déployable, ni une solution d'IA validée. Il offre des briques utiles — scraper Playwright, extraction PDF/OCR, règles NLP, API FastAPI, interface React, modèles SQLAlchemy — assemblées de manière encore fragile.

La documentation surévalue fortement la maturité. Des termes comme « hautement performante », « recherche sémantique », « production PostgreSQL », « entraînement asynchrone » et « couverture 70 % » sont employés sans preuve reproductible. En soutenance, ces formulations exposent le projet à des objections faciles.

**Note stricte : 31/100.**  
**Niveau réel : POC technique en cours d'intégration.**  
**Décision : GO conditionnel pour une refonte vers un MVP de démonstration ; NO-GO pour pilote DSI ou production.**

## 2. Méthode et limites

Éléments contrôlés :

- `PRESENTATION_PROJET.md`, `README.md`, documentation d'architecture et ancien plan d'action ;
- backend, modèle de données, migrations, sécurité, ingestion, OCR, NLP, ML et frontend ;
- 7 365 lignes de Python/JavaScript environ et 37 tests Python déclarés ;
- bases SQLite présentes, artefacts de test et corpus local ;
- installation frontend et exécution de la suite backend ;
- accès au portail source communiqué.

Limites :

- le portail `appels-offres.equipement.gov.ma` ne résout pas son nom de domaine au jour de l'audit (`ERR_NAME_NOT_RESOLVED`) ;
- aucune instance PostgreSQL de production, aucune CI et aucun environnement de référence n'ont été fournis ;
- les tests n'ont pas pu être menés à terme dans l'environnement livré.

## 3. Score détaillé

| Domaine | Poids | Note | Appréciation stricte |
|---|---:|---:|---|
| Pertinence métier et cadrage | 12 | 7 | Problème réel, mais utilisateurs, décisions et frontières mal définis |
| Architecture et maintenabilité | 13 | 4 | Découpage apparent, backend central monolithique de 946 lignes |
| Ingestion et traçabilité | 12 | 5 | Travail réel sur Playwright, mais dépendance source et orchestration fragiles |
| OCR et qualité documentaire | 10 | 4 | Fallback utile, aucune campagne de mesure robuste |
| NLP et structuration | 10 | 3 | Règles intéressantes, scores largement constants et validation insuffisante |
| Recherche et analytique | 10 | 3 | Recherche `LIKE`, pas de vraie recherche sémantique ni ranking convaincant |
| ML et évaluation scientifique | 10 | 2 | Dataset minuscule, split fragile, aucune métrique sérieuse ni gouvernance |
| Sécurité et conformité | 10 | 1 | Plusieurs défauts critiques incompatibles avec un contexte ministériel |
| Tests et qualité logicielle | 8 | 1 | Badge 70 % non démontré ; suite bloquante et dépendances incomplètes |
| DevOps, exploitation et documentation | 5 | 1 | Docker incohérent, secrets faibles, pas de CI ni observabilité exploitable |
| **Total** | **100** | **31** | **POC, non déployable** |

## 4. Écarts entre le discours et les preuves

| Affirmation actuelle | Preuve observée | Conclusion |
|---|---|---|
| Couverture minimale de 70 % | badge statique ; `pytest-cov` absent de l'environnement ; suite bloquée au-delà de 120 s | Non démontré, affirmation à retirer |
| Recherche « sémantique » / FTS | `MarcheRepository.search_fts` utilise des `LIKE`/`ILIKE` sur quelques colonnes | Recherche lexicale simple, ni sémantique ni FTS industriel |
| PostgreSQL en production | aucun environnement de production ; compose avec mot de passe `password` | Compatibilité visée, pas production |
| Plateforme hautement performante | aucun benchmark, test de charge ou SLO | Allégation marketing non recevable |
| OCR avec qualité suivie | extraction OCR présente, mais pas de corpus annoté ni CER/WER par langue | Qualité non quantifiée |
| ML de classification précis | entraînement autorisé dès 5 éléments, parfois entraînement et test sur les mêmes données | Résultats non scientifiquement valides |
| Détection d'anomalies financières | Isolation Forest sur montant/délai/caution avec zéros pour valeurs manquantes | Démonstrateur statistique, pas contrôle métier |
| Pipeline asynchrone | `BackgroundTasks` dans le processus web | différé, mais ni file durable, ni reprise, ni isolation worker |
| Portail source opérationnel | domaine non résolu le 30/07/2026 | dépendance externe indisponible et non maîtrisée |

## 5. Constats critiques — P0

### P0-1 — Sécurité incompatible avec un SI ministériel

- secret JWT de repli codé en dur : `my_super_secret_key_for_ged_intelligente` ;
- compte administrateur créé automatiquement avec `admin123` ;
- CORS par défaut à `*` avec `allow_credentials=True` ;
- mot de passe PostgreSQL `password` dans `docker-compose.yml` ;
- jeton de réinitialisation de mot de passe écrit dans les logs ;
- la majorité des routes GED, analytics, ML, monitoring et schéma sont publiques ;
- le token WebSocket passe dans la query string, donc peut finir dans des journaux ;
- aucun mécanisme démontré de rotation de secrets, révocation de refresh token ou session centralisée.

**Impact :** compromission des comptes, exposition de données, élévation de privilèges, fuite de jetons.  
**Exigence :** bloquer tout pilote avant correction, revue OWASP et test d'intrusion minimal.

### P0-2 — Le système n'est pas reproductible

- `requirements.txt` duplique près de 80 dépendances ;
- `structlog`, importé par l'API, n'est pas déclaré ;
- Python 3.11+ est annoncé, tandis que le Dockerfile utilise Python 3.10 ;
- chemin Tesseract Windows codé en dur ;
- aucun `pyproject.toml`, `pytest.ini`, `setup.cfg` ni pipeline CI ;
- l'installation frontend a échoué (`ENOTEMPTY`) et `vitest` restait introuvable ;
- `pytest` avec couverture échoue car le plugin n'est pas installé ;
- `pytest tests -q` n'a produit aucun résultat avant expiration à 60 s ; la suite globale dépasse 120 s.

**Impact :** une machine externe ne peut pas reproduire de façon fiable la démonstration.  
**Exigence :** créer un environnement propre à partir de zéro et en faire le seul critère de validation.

### P0-3 — La persistance et les migrations ne sont pas maîtrisées

- coexistence de création automatique `Base.metadata.create_all()` et d'Alembic ;
- échec de migration masqué au démarrage par un mode « dégradé » ;
- plusieurs bases de sauvegarde/test sont présentes, sans base runtime canonique versionnée ;
- une base de test de 311 Ko et `_test_models.db` sont suivies par Git ;
- le frontend et l'API conservent des formes de données « legacy » ;
- l'endpoint `/api/v1/system/health` est déclaré deux fois.

**Impact :** dérive de schéma, comportements différents selon les machines, données non traçables.

### P0-4 — Le pipeline n'est pas industriellement asynchrone

`BackgroundTasks` exécute le traitement dans le processus applicatif. Une panne ou un redémarrage perd l'état du travail. Il n'existe ni file durable, ni retry contrôlé, ni dead-letter queue, ni annulation, ni allocation de ressources, ni idempotence de chaque étape.

**Impact :** blocage de workers web, traitements perdus, doublons et diagnostic difficile.

### P0-5 — Dépendance critique à une source externe instable

Le portail ne répond pas via DNS le jour de l'audit. Le connecteur dépend en outre d'une interface ASP.NET et de sélecteurs conservés dans le dépôt. Les captures HTML constituent une aide de développement, pas un contrat d'interface.

**Impact :** la fonctionnalité de collecte peut devenir totalement indisponible sans défaut dans le code local.

## 6. Constats majeurs — P1

### 6.1 Le projet n'est pas encore une GED

Une GED implique au minimum classement, métadonnées gouvernées, version, droits, cycle de vie, conservation, consultation du fichier, audit et éventuellement workflow. Le dépôt est surtout une **plateforme d'ingestion et d'analyse documentaire**. Des tables annoncent certaines notions, mais les parcours complets ne sont pas démontrés.

Le nom peut être conservé pour la soutenance, à condition de parler de « prototype de GED analytique » et d'assumer les limites. Pour un cadrage professionnel, « Observatoire intelligent des dossiers d'appels d'offres » est plus exact.

### 6.2 Backend monolithique et contrats API faibles

- `backend/main.py` concentre routes, sérialisation legacy, exports, analytique, ML, monitoring et console ;
- payload de création en `Dict[str, Any]` au lieu d'un schéma Pydantic strict ;
- validation et erreurs hétérogènes ;
- pagination non bornée explicitement et export limité arbitrairement à 1 000 lignes ;
- noms métier multiples : `montant`, `budget_estimatif_mad`, `estimation_mad` ;
- absence de versionnement explicite des contrats et de tests de contrat frontend/backend.

### 6.3 Recherche mal qualifiée

Le moteur ne fournit pas : stemming français/arabe, tolérance aux variantes, ranking, surlignage issu du contenu, facettes fiables, synonymes métier, recherche vectorielle, requête bilingue ou explication de pertinence. Le « highlight » est fabriqué depuis les 50 premiers caractères du titre.

**Qualification correcte actuelle :** recherche textuelle simple et filtres structurés.

### 6.4 OCR sans dispositif de qualité

Points positifs : extraction native avant OCR, support annoncé `fra+ara`, prétraitement d'image et cache.  
Faiblesses : pas de typologie de documents, pas de vérité terrain, pas de CER/WER, pas de mesure par langue, pas de détection de rotation/tableaux, pas de seuil de revue humaine, pas de conservation systématique des coordonnées et pages sources.

Le score OCR ne doit pas être présenté comme « exactitude du document » : la confiance Tesseract n'est pas une mesure métier.

### 6.5 NLP largement fondé sur des règles

Les expressions régulières sont adaptées à un POC, mais :

- plusieurs scores (`0.8`, `0.9`) sont des constantes et non des probabilités calibrées ;
- le petit modèle spaCy français n'est pas un modèle spécifique aux marchés publics marocains ;
- l'arabe est OCRisé mais l'extraction sémantique arabe n'est pas démontrée ;
- aucune campagne précision/rappel/F1 par champ ;
- aucune interface complète de correction et réinjection des corrections ;
- normalisation géographique et référentiels insuffisamment gouvernés.

### 6.6 ML non défendable scientifiquement

- minimum de cinq dossiers pour entraîner un SVM ;
- en dessous de dix, test et entraînement portent sur les mêmes données ;
- pas de stratification, cross-validation, baseline naïve, matrice de confusion ou F1 macro ;
- modèle sérialisé sans version, hash du dataset, date, métriques ni registre ;
- `IsolationForest(contamination=0.05)` impose environ 5 % d'anomalies sans justification métier ;
- valeurs manquantes transformées en zéro, créant de fausses anomalies ;
- aucune explication de l'alerte ni validation par un expert.

**Recommandation :** retirer le mot « prédictif » tant qu'un protocole d'évaluation n'est pas disponible.

### 6.7 Frontend séduisant mais couplé au poste développeur

- URLs API répétées en dur entre `localhost` et `127.0.0.1` malgré un client Axios central ;
- WebSocket non sécurisé `ws://` ;
- absence de tests de parcours significatifs (un test Skeleton seulement visible) ;
- divergence de taille d'upload : 50 Mo frontend, 100 Mo backend ;
- le polling d'upload interroge l'aperçu plutôt que l'endpoint de statut ;
- dépendance à une image Unsplash distante pour la page d'accueil ;
- accessibilité, internationalisation arabe/RTL et responsive non démontrés.

### 6.8 Données réelles insuffisamment gouvernées

La base `ged.db.bak2` contient 42 marchés, 15 documents, 18 logs OCR, 76 extractions NLP et 6 insights ML. C'est utile pour une démo, mais insuffisant pour valider un modèle. Il manque : catalogue du corpus, provenance par objet, date de collecte, licence/condition d'utilisation, hash, taux de complétude, split train/test gelé et dictionnaire de labels.

## 7. Points réellement valorisables

- problématique concrète à forte valeur : rendre exploitables des dossiers d'appels d'offres peu structurés ;
- séparation conceptuelle ingestion / OCR / NLP / API / interface ;
- prise en compte des PDF natifs et scannés ;
- premier support bilingue côté OCR ;
- structure SQLAlchemy et migrations déjà amorcées ;
- interface React plus riche qu'un simple écran de démonstration ;
- traçabilité partielle via hash, logs OCR et extractions NLP ;
- tests unitaires et d'intégration déjà esquissés ;
- corpus local suffisant pour préparer une démonstration hors ligne.

Ces éléments justifient une consolidation. Ils ne justifient pas les qualificatifs de production.

## 8. Plan d'action priorisé

### Phase 0 — Rebaseliner et sécuriser (semaine 1)

1. Geler les fonctionnalités pendant la stabilisation.
2. Retirer les affirmations non mesurées de la présentation et du README.
3. Faire échouer le démarrage si `JWT_SECRET_KEY`, admin bootstrap ou configuration sensible manquent.
4. Supprimer le mot de passe admin par défaut et le secret JWT de repli.
5. Protéger toutes les routes sauf login et health minimal ; définir une matrice RBAC.
6. Ne plus logger les tokens ; passer les WebSockets sous TLS et token court.
7. Dédupliquer et séparer les dépendances runtime/dev ; déclarer `structlog`.
8. Aligner Python, Docker et documentation sur une version unique.
9. Ajouter `pyproject.toml`, configuration pytest, lint et CI.

**Sortie :** installation propre, API qui démarre, secret obligatoire, tests de smoke verts.

### Phase 1 — Rendre le socle reproductible (semaines 2–3)

1. Décomposer `main.py` en routers/services/repositories/schemas.
2. Supprimer `create_all` du runtime et rendre Alembic obligatoire.
3. Nettoyer les artefacts suivis par Git et créer des fixtures minimales.
4. Centraliser l'URL API frontend et configurer dev/test/prod.
5. Ajouter contrats Pydantic stricts, pagination bornée et format d'erreur unique.
6. Créer une CI : install, migration, lint, tests backend, tests frontend, build, audit dépendances.
7. Documenter un quickstart réellement exécuté sur machine vierge.

**Sortie :** clone → installation → migration → tests → build sans intervention manuelle.

### Phase 2 — Fiabiliser l'ingestion documentaire (semaines 4–5)

1. Définir un connecteur source abstrait et versionné.
2. Ajouter mode replay depuis pages/corpus locaux pour survivre à l'indisponibilité du portail.
3. Remplacer `BackgroundTasks` par une file durable et un worker séparé.
4. Modéliser un job et ses étapes : collecté, téléchargé, validé, extrait, OCR, NLP, indexé, rejeté.
5. Ajouter retry borné, timeouts, idempotence, checksum, quarantaine et reprise.
6. Sécuriser ZIP/PDF : zip-slip, bombes ZIP, limite décompressée, MIME réel, antivirus si cible institutionnelle.
7. Capturer provenance, URL, date, hash et version du connecteur.

**Sortie :** 100 dossiers rejoués deux fois sans doublons, avec 100 % des états explicables.

### Phase 3 — Mesurer OCR et extraction (semaines 6–8)

1. Constituer un corpus annoté stratifié : natif/scanné, français/arabe/mixte, qualité basse/haute.
2. Mesurer CER/WER OCR et précision/rappel/F1 par champ métier.
3. Conserver page, zone et extrait justificatif pour chaque valeur.
4. Ajouter revue humaine : accepter, corriger, rejeter, commenter.
5. Introduire seuils par champ et statut « à vérifier ».
6. Versionner règles, modèles, référentiels et résultats.

**Cibles MVP :** F1 ≥ 0,90 pour référence/date/montant sur corpus validé ; 100 % des champs sensibles avec preuve de source.

### Phase 4 — Recherche et exploitation métier (semaines 9–10)

1. Implémenter un vrai index PostgreSQL FTS français, stratégie arabe, ranking et snippets.
2. Distinguer recherche lexicale, filtres et recherche sémantique expérimentale.
3. Ajouter facettes, requêtes sauvegardées, export audité et comparaison de dossiers.
4. Construire des KPIs avec définition, formule, périmètre, fraîcheur et qualité.
5. Tester pertinence sur 30–50 requêtes métier annotées (Recall@10, nDCG@10).

**Sortie :** résultats classés et explicables, aucun KPI sans définition.

### Phase 5 — ML gouverné, ou suppression assumée (semaines 11–12)

1. Définir la décision réellement assistée par chaque modèle.
2. Obtenir un dataset labellisé suffisant ; sinon rester sur règles explicables.
3. Comparer baseline mots-clés, régression/logistique et SVM.
4. Utiliser split stratifié gelé, validation croisée, F1 macro et matrice de confusion.
5. Pour les anomalies, combiner règles réglementaires/métier et modèle statistique explicable.
6. Versionner dataset, code, modèle, métriques et seuil ; surveiller la dérive.
7. Interdire toute décision automatique : l'outil signale, l'agent valide.

### Phase 6 — Pilote DSI (3 à 6 mois)

1. Revue d'architecture, sécurité, données et exploitation par la DSI.
2. SSO/RBAC institutionnel, TLS, sauvegardes, restauration et journalisation immuable.
3. Tests de charge, sécurité, reprise après incident et accessibilité.
4. Pilote limité avec utilisateurs nommés et critères d'arrêt.
5. Mesurer temps gagné, taux de correction, adoption et faux positifs.
6. Décision go/no-go production sur preuves.

## 9. Backlog synthétique

| Priorité | Élément | Critère d'acceptation |
|---|---|---|
| P0 | Secrets et admin bootstrap | aucun secret faible ; démarrage refusé sans config |
| P0 | Protection API | matrice RBAC testée sur 100 % des routes |
| P0 | Build reproductible | CI verte depuis un clone propre |
| P0 | Migrations | une seule chaîne Alembic, aucun `create_all` runtime |
| P0 | Source indisponible | mode replay local documenté et testé |
| P1 | Worker durable | retry/reprise/idempotence démontrés |
| P1 | Corpus annoté | provenance, labels et split versionnés |
| P1 | Qualité OCR/NLP | CER/WER et F1 par langue/champ publiés |
| P1 | Recherche réelle | index, ranking, snippets et métriques de pertinence |
| P1 | Revue humaine | correction traçable jusqu'à l'extrait source |
| P2 | ML | baseline battue avec protocole reproductible |
| P2 | Pilote | sécurité, performance, exploitation et adoption validées |

## 10. Indicateurs de pilotage

| Axe | Indicateur | Cible avant pilote |
|---|---|---:|
| Reproductibilité | build CI réussi | 100 % |
| Pipeline | jobs terminaux sans intervention | ≥ 98 % |
| Déduplication | doublons après replay | 0 |
| OCR | CER français/arabe par classe | seuil défini et publié |
| Extraction | F1 par champ critique | ≥ 0,90 sur champs simples |
| Traçabilité | valeurs avec page/extrait/version | 100 % |
| Recherche | Recall@10 sur requêtes annotées | ≥ 0,90 |
| Sécurité | vulnérabilités critiques/hautes ouvertes | 0 |
| Exploitation | restauration testée | succès documenté |
| Utilité | réduction du temps de recherche | ≥ 40 % lors du pilote |

## 11. Risques à tenir explicitement

| Risque | Probabilité | Impact | Réponse |
|---|---|---|---|
| portail indisponible ou modifié | élevée | critique | connecteurs, monitoring, replay, corpus local |
| documents hétérogènes et arabes | élevée | élevé | corpus stratifié, mesure par langue, revue humaine |
| données insuffisantes pour ML | élevée | élevé | règles explicables, collecte/annotation, pas de promesse prédictive |
| confusion entre aide et contrôle réglementaire | moyenne | critique | libellé « signal », validation humaine, explication |
| fuite de documents ou comptes | moyenne | critique | RBAC, secrets, chiffrement, audits |
| démo non reproductible | élevée | élevé | CI, image versionnée, scénario hors ligne |
| dette du monolithe | élevée | moyen | découpage progressif par domaine |

## 12. Formulation honnête pour la soutenance

> Nous avons développé un prototype de plateforme d'ingestion et d'analyse documentaire appliqué aux dossiers d'appels d'offres. Le prototype démontre la collecte, l'extraction PDF/OCR, la structuration de champs et leur restitution dans une interface. Les performances OCR, NLP et ML restent à valider sur un corpus annoté ; la sécurité, l'industrialisation et la gouvernance constituent les prochaines étapes avant tout pilote DSI.

Cette formulation est plus crédible que la présentation actuelle et transforme les limites en perspectives de travail maîtrisées.

