# 📘 Fichier 1 — Évaluation de l'avancement & Scénarios de tests exhaustifs

> **Projet** : GED Intelligente — Gestion Électronique des Documents pour les marchés publics du Ministère de l'Équipement et de l'Eau du Maroc
> **Stage** : PFA (Projet de Fin d'Année), durée 2 mois
> **Organisme d'accueil** : Direction des Systèmes d'Information (DSI)
> **Document source** : `455102a7__845ed038-b493-49c1-873b-81fcb62ad79f.md`
> **Site de référence** : http://appels-offres.equipement.gov.ma/recherche/criteres.aspx
> **Version** : 1.0 — Référence pour la soutenance, la correction et l'audit qualité

> ⚠️ **Note méthodologique** : Le site ministériel bloque les robots d'extraction (captcha / anti-bot). La structure du formulaire `criteres.aspx` est donc reconstituée à partir (a) du document PFA qui décrit la cible de scraping, (b) des documents réglementaires publiés par le Ministère (décret n° 2-22-431, modèles d'avis 12 à 13-10), (c) du descriptif public du Portail National des Marchés Publics (marchespublics.gov.ma). Les scénarios marqués 🟢 Terrain doivent être rejoués sur le site réel pour validation finale.

---

## Table des matières

1. [Synthèse exécutive](#1-synthèse-exécutive)
2. [Cartographie du périmètre fonctionnel](#2-cartographie-du-périmètre-fonctionnel)
3. [Évaluation détaillée de l'avancement](#3-évaluation-détaillée-de-lavancement)
   - 3.1 [Avancement par couche technique](#31-avancement-par-couche-technique)
   - 3.2 [Avancement par module fonctionnel](#32-avancement-par-module-fonctionnel)
   - 3.3 [Avancement par écran / interface](#33-avancement-par-écran--interface)
   - 3.4 [Matrice de couverture vs référentiel du site ministériel](#34-matrice-de-couverture-vs-référentiel-du-site-ministériel)
   - 3.5 [Indicateurs qualité](#35-indicateurs-qualité)
4. [Analyse des écarts (gap analysis)](#4-analyse-des-écarts-gap-analysis)
5. [Risques et points de vigilance](#5-risques-et-points-de-vigilance)
6. [Scénarios de tests exhaustifs](#6-scénarios-de-tests-exhaustifs)
   - 6.1 [Stratégie et convention de nommage](#61-stratégie-et-convention-de-nommage)
   - 6.2 [Tests du module Ingestion & Scraping](#62-tests-du-module-ingestion--scraping)
   - 6.3 [Tests du module OCR & PDF natif](#63-tests-du-module-ocr--pdf-natif)
   - 6.4 [Tests du module NLP & Extraction](#64-tests-du-module-nlp--extraction)
   - 6.5 [Tests du module Recherche FTS](#65-tests-du-module-recherche-fts)
   - 6.6 [Tests du module Machine Learning](#66-tests-du-module-machine-learning)
   - 6.7 [Tests du Dashboard BI](#67-tests-du-dashboard-bi)
   - 6.8 [Tests par écran](#68-tests-par-écran)
   - 6.9 [Tests de sécurité et d'accès](#69-tests-de-sécurité-et-daccès)
   - 6.10 [Tests de performance](#610-tests-de-performance)
   - 6.11 [Tests d'API (FastAPI / OpenAPI)](#611-tests-dapi-fastapi--openapi)
   - 6.12 [Tests d'intégration bout-en-bout](#612-tests-dintégration-bout-en-bout)
   - 6.13 [Tests de régression visuelle](#613-tests-de-régression-visuelle)
7. [Critères d'acceptation globaux](#7-critères-dacceptation-globaux)
8. [Annexes](#8-annexes)

---

## 1. Synthèse exécutive

| Indicateur | Valeur | Commentaire |
|---|---|---|
| **Périmètre fonctionnel annoncé** | 9 écrans, 5 modules backend, pipeline OCR + NLP + ML complet | Conforme à un PFA ambitieux |
| **Taux d'achèvement estimé (MVP)** | **≈ 75–80 %** | Cœur pipeline + écrans principaux livrés, durcissement et analytics avancés à compléter |
| **Modules production-ready** | Ingestion, OCR natif, NLP regex/spaCy, FTS, Dashboard basique, ML SVM | OK sur dataset test (≈ 20 DAO) |
| **Modules partiellement livrés** | OCR arabe, IsolationForest, PipelineAdmin, Monitoring | Fonctionnels mais sans tests de charge ni exposition production |
| **Modules manquants ou à finaliser** | Authentification, RBAC, Audit log, observabilité, alerting, BI avancé | Voir Fichier 2 |
| **Conformité avec le formulaire ministériel** | ≈ 50 % des champs couverts | Manque qualification, agrément, type d'avis, état, date d'ouverture, etc. |
| **Qualité du code (couverture tests)** | 70 % revendiqués | À vérifier sur la base des tests réellement exécutés dans le pipeline CI |
| **Risque global** | 🟠 Moyen | Projet mature sur le cœur NLP/ML, à sécuriser sur la cohérence avec le site source et la scalabilité |

### Verdict global

Le projet réalise avec succès la **chaîne de valeur principale** (scraping → OCR → structuration → recherche → dashboard) et démontre une stack technique moderne et bien intégrée. La valeur BI est cependant **naïve** (4 KPI + 2 graphiques). Pour passer d'un prototype universitaire à une **vraie plateforme BI ministérielle**, il faut (a) aligner le modèle de données sur le formulaire complet `criteres.aspx`, (b) ajouter des dimensions analytiques, (c) industrialiser le pipeline et (d) renforcer la gouvernance (auth, audit, monitoring).

---

## 2. Cartographie du périmètre fonctionnel

### 2.1 Modules déclarés dans le document PFA

| # | Module | Rôle | Statut annoncé |
|---|---|---|---|
| M1 | Ingestion & Collecte (Scraper Playwright) | Récupérer les archives du portail | ✅ Livré |
| M2 | OCR & Native PDF (PyMuPDF + Tesseract) | Convertir PDF en texte | ✅ Livré |
| M3 | Structuration NLP (spaCy + Regex) | Extraire entités, montants, dates | ✅ Livré |
| M4 | Recherche FTS (index GIN Postgres) | Recherche plein texte + filtres | ✅ Livré |
| M5 | ML Classification + Anomalies | SVM + IsolationForest | ✅ Livré |
| M6 | API REST (FastAPI) | Exposer les services | ✅ Livré |
| M7 | SPA React (Vite + Tailwind) | Interface utilisateur | ✅ Livré |
| M8 | Tableau de bord BI (Recharts) | Visualisation | 🟡 Partiel |
| M9 | Pipeline d'admin & Monitoring | Outils ops | 🟡 Partiel |

### 2.2 Écrans déclarés

| # | Écran | Rôle | Statut |
|---|---|---|---|
| E1 | `LandingPage` | Portail d'entrée | ✅ |
| E2 | `Dashboard` | KPIs + camembert + bar chart | 🟡 |
| E3 | `SearchFTS` | Recherche plein texte | ✅ |
| E4 | `DocumentDetail` | Fiche détaillée par document | ✅ |
| E5 | `Explorer` | Liste fichiers physiques | ✅ |
| E6 | `Upload` | Import drag & drop | ✅ |
| E7 | `PredictorML` | Pilotage modèles IA | 🟡 |
| E8 | `Monitoring` | Logs & temps OCR | 🟡 |
| E9 | `PipelineAdmin` | Lancement scraper | 🟡 |

### 2.3 Champs du formulaire de référence `criteres.aspx` (reconstitués)

| # | Libellé probable (FR) | Type attendu | Couverte dans GED ? |
|---|---|---|---|
| 1 | Référence de l'avis | Input texte | ✅ (extraction NLP) |
| 2 | Mots clés / Objet | Input texte + autocomplétion | ✅ (FTS) |
| 3 | Maître d'ouvrage (acheteur) | Listbox / dropdown | ✅ |
| 4 | Direction / Service | Listbox hiérarchique | ❌ |
| 5 | Activité / Catégorie de prestation | Listbox | ✅ (catégorie SVM) |
| 6 | Type d'avis (ouvert, restreint, simplifié, avec présélection, concours, consultation architecturale, dialogue compétitif, bon de commande) | Listbox | ❌ |
| 7 | Type de procédure | Listbox | ❌ |
| 8 | Date de publication (du / au) | DatePicker × 2 | 🟡 (date_seule) |
| 9 | Date d'ouverture des plis (du / au) | DatePicker × 2 | ❌ |
| 10 | Date limite de remise des plis | DatePicker | ❌ |
| 11 | Lieu d'exécution (région / province / ville) | 3 Listbox en cascade | 🟡 (ville uniquement) |
| 12 | Qualifications requises | Listbox multi-sélection | ❌ |
| 13 | Agréments requis | Listbox multi-sélection | ❌ |
| 14 | Estimation budgétaire (min / max) | 2 inputs numériques | 🟡 (un seul min) |
| 15 | Caution provisoire (min / max) | 2 inputs numériques | ❌ (extraction oui, filtre non) |
| 16 | État de l'avis (en cours, clôturé, attribué, annulé, infructueux) | Listbox | ❌ |
| 17 | Source (ministère, EP, collectivité…) | Listbox | ❌ |
| 18 | Langue (FR / AR / bilingue) | Listbox | ❌ |
| 19 | Tri des résultats (date desc/asc, montant, référence) | Listbox | ❌ |
| 20 | Bouton « Rechercher » | Submit | ✅ |
| 21 | Bouton « Réinitialiser » | Reset | ❌ |
| 22 | Bouton « Télécharger DAO (ZIP) » | Action contextuelle | ✅ |
| 23 | Pagination des résultats | Liens / infinite scroll | ✅ |

> Total : **23 contrôles** sur le site source. La GED actuelle en couvre **5 complètement** et **3 partiellement**.

---

## 3. Évaluation détaillée de l'avancement

### 3.1 Avancement par couche technique

| Couche | Technologies | Avancement | Maturité | Commentaire |
|---|---|---|---|---|
| **Backend API** | Python 3.11, FastAPI, SQLAlchemy 2.0, Alembic | 85 % | Production-ready | Architecture propre, OpenAPI généré, migration versionnée. Manque middleware d'auth, rate-limiting, observabilité. |
| **Base de données** | SQLite (dev) / PostgreSQL (prod) | 80 % | Production-ready | FTS Postgres OK, mais pas de partitioning temporel ni d'archivage. |
| **Ingestion** | Playwright | 75 % | Prototype robuste | OK sur ~20 DAO, à valider sur des plages larges (≥ 1 an) et à paralléliser. |
| **OCR** | PyMuPDF + Tesseract 5 (FR + AR) | 70 % | Fonctionnel, perfectible | Détection auto du type de PDF (natif vs scanné) livrée. Pas de benchmarking qualité (CER, WER). |
| **NLP** | spaCy `fr_core_news_sm` + Regex | 75 % | Bon | Extraction montants, dates, villes OK. Manque reconnaissance des **modèles d'avis** et des **qualifications**. |
| **ML** | scikit-learn (SVM, IsolationForest) | 70 % | Prototype | SVM classifieur linéaire, dataset d'entraînement limité. Pas de pipeline de versionning (MLflow) ni de feature store. |
| **Frontend** | React 19, Vite, Tailwind, Recharts, Axios | 80 % | Bonne base | UI propre, mode sombre, responsive. Pas d'i18n, pas de gestion d'état avancée (Redux/Zustand), pas de tests composants. |
| **Qualité & tests** | Pytest, pytest-cov | 60 % | Insuffisant | 70 % revendiqués mais sans Cypress/Playwright côté front, pas de tests de charge, pas de tests E2E. |
| **Ops & déploiement** | Non mentionné | 30 % | À faire | Pas de Dockerfile, CI/CD, monitoring (Prometheus/Grafana), alertes. |
| **Sécurité** | Non mentionné | 20 % | Critique | Pas d'authentification, pas de RBAC, pas d'audit log. |

### 3.2 Avancement par module fonctionnel

#### M1 — Ingestion & Collecte

| Sous-fonctionnalité | État | Détail |
|---|---|---|
| Navigation Playwright sur le portail | ✅ | Confirmée sur 20 DAO |
| Gestion de la pagination | 🟡 | À valider sur 100+ pages |
| Téléchargement ZIP asynchrone | ✅ | `BackgroundTasks` FastAPI |
| Décompression archive | ✅ | |
| Déduplication des fichiers | 🟡 | Probable mais non documenté |
| Reprise sur erreur / idempotence | ❌ | Pas de mécanisme de reprise |
| Scraping incrémental | ❌ | Pas de watermark temporel |
| File d'attente (queue) persistante | 🟡 | `BackgroundTasks` non persistant |
| Logging des étapes | 🟡 | Basique |
| Planification (cron) | ❌ | Pas d'ordonnanceur |
| Multi-collectes parallèles | ❌ | Mono-thread |
| Proxy / rotation User-Agent | ❌ | Risque de blocage |

**Avancement M1 : 60 %**

#### M2 — OCR & PDF natif

| Sous-fonctionnalité | État |
|---|---|
| Détection PDF natif vs scanné | ✅ |
| Extraction texte natif (PyMuPDF) | ✅ |
| Prétraitement image (niveaux de gris, seuillage) | ✅ |
| OCR Tesseract FR | ✅ |
| OCR Tesseract AR | 🟡 (modèle arabe installé, qualité non auditée) |
| OCR bilingue (FR + AR par page) | ❌ |
| Stockage `OcrLog` (confiance moyenne) | ✅ |
| Temps de traitement par page | ✅ (Monitoring) |
| Reprise OCR après crash | ❌ |
| OCR multi-moteur (EasyOCR, PaddleOCR en backup) | ❌ |
| Métriques qualité (CER, WER) | ❌ |

**Avancement M2 : 65 %**

#### M3 — Structuration NLP

| Sous-fonctionnalité | État |
|---|---|
| Extraction référence | ✅ |
| Extraction objet | ✅ |
| Extraction maître d'ouvrage | ✅ |
| Extraction ville d'exécution | ✅ |
| Normalisation villes (provinces Maroc) | ✅ |
| Extraction montant estimé (MAD) | ✅ (regex multi-formats) |
| Extraction caution provisoire | ✅ |
| Extraction délai d'exécution | ✅ |
| Normalisation dates en ISO | ✅ |
| Extraction **type d'avis** (ouvert, restreint, etc.) | ❌ |
| Extraction **qualifications & agréments** | ❌ |
| Extraction **date d'ouverture des plis** | ❌ |
| Extraction **date limite de remise** | ❌ |
| Reconnaissance des **modèles d'avis 12 à 13-10** | ❌ |
| Reconnaissance **bilingue FR/AR** sur les entités | ❌ |
| Score de confiance par entité | 🟡 |

**Avancement M3 : 55 %**

#### M4 — Recherche FTS

| Sous-fonctionnalité | État |
|---|---|
| Index GIN Postgres | ✅ |
| Recherche plein texte | ✅ |
| Autocomplétion | ✅ |
| Filtre ville | ✅ |
| Filtre budget min/max | 🟡 (un seul min/max) |
| Filtre date de parution | 🟡 |
| Filtre catégorie | ✅ |
| Pagination | ✅ |
| Tri des résultats | ❌ |
| Surlignage des termes trouvés (highlight) | ❌ |
| Filtres avancés (qualif, agrément, type d'avis) | ❌ |
| Export des résultats (CSV, Excel) | ❌ |
| Recherche floue (fuzzy) | ❌ |
| Recherche par référence exacte | 🟡 |

**Avancement M4 : 60 %**

#### M5 — ML

| Sous-fonctionnalité | État |
|---|---|
| TF-IDF + SVM classifier | ✅ |
| Sauvegarde modèle (Joblib) | ✅ |
| Ré-entraînement asynchrone via API | ✅ |
| IsolationForest (anomalies financières) | ✅ |
| Watchlist classification humaine vs IA | ✅ |
| Métriques précision / recall / F1 | 🟡 (affichées partiellement) |
| Confusion matrix | ❌ |
| Feature importance | ❌ |
| Versioning des modèles (MLflow / DVC) | ❌ |
| A/B testing des modèles | ❌ |
| Pipeline de labellisation manuelle | 🟡 (Watchlist = embryon) |
| Explicabilité (SHAP / LIME) | ❌ |

**Avancement M5 : 55 %**

### 3.3 Avancement par écran / interface

| Écran | Complétude | UX | Données affichées | Note /10 |
|---|---|---|---|---|
| LandingPage | 90 % | Premium, identité visuelle soignée | Stats succinctes | 8/10 |
| Dashboard | 50 % | Correcte | 4 KPI + Pie + Bar | 5/10 |
| SearchFTS | 70 % | Bonne | Filtres basiques | 7/10 |
| DocumentDetail | 80 % | Très bon | Onglets riches | 8/10 |
| Explorer | 75 % | Bon | Tableau fichiers | 7/10 |
| Upload | 80 % | Bon | Drag & drop + polling | 8/10 |
| PredictorML | 50 % | Correcte | Métriques et watchlist | 5/10 |
| Monitoring | 50 % | Basique | Logs et temps OCR | 5/10 |
| PipelineAdmin | 50 % | Basique | Bouton scraping | 5/10 |
| **Moyenne pondérée** | | | | **6,4/10** |

### 3.4 Matrice de couverture vs référentiel du site ministériel

| Dimension site source | Couverture GED | Action |
|---|---|---|
| Recherche par référence | ✅ | Maintenir |
| Recherche par mots-clés | ✅ | Étendre (recherche floue, opérateurs) |
| Maître d'ouvrage | ✅ | Étendre (alias, hiérarchie) |
| Activité / Catégorie | ✅ | Étendre (sous-catégories) |
| Type d'avis | ❌ | **À ajouter** (priorité P0) |
| Type de procédure | ❌ | **À ajouter** (P0) |
| Date de publication | 🟡 | Étendre à date d'ouverture et date limite |
| Date d'ouverture des plis | ❌ | **À ajouter** (P0) |
| Date limite de remise | ❌ | **À ajouter** (P0) |
| Lieu d'exécution hiérarchique | 🟡 | Étendre à région/province/ville |
| Qualifications | ❌ | **À ajouter** (P0) |
| Agréments | ❌ | **À ajouter** (P0) |
| Estimation budgétaire | 🟡 | Étendre à min/max |
| Caution provisoire | ❌ | **À ajouter** (filtre + extraction) |
| État de l'avis | ❌ | **À ajouter** (P0) |
| Source | ❌ | À ajouter (P1) |
| Langue | ❌ | À ajouter (P1) |
| Tri des résultats | ❌ | À ajouter (P1) |
| Réinitialisation des filtres | ❌ | À ajouter (P0) |
| Téléchargement DAO | ✅ | Maintenir |
| Pagination | ✅ | Étendre (taille variable, lazy load) |
| Export | ❌ | À ajouter (P0) |
| Sauvegarde de recherche | ❌ | À ajouter (P1) |
| Alertes email | ❌ | À ajouter (P1) |

**Taux de couverture fonctionnel : ~50 %** des capacités du site source.

### 3.5 Indicateurs qualité

| KPI | Cible | Mesure actuelle | Verdict |
|---|---|---|---|
| Couverture de tests unitaires | ≥ 70 % | 70 % (revendiqué) | 🟢 |
| Tests d'intégration | ≥ 30 cas | Non documenté | 🟠 |
| Tests E2E (front) | ≥ 20 scénarios | 0 | 🔴 |
| Temps moyen de scraping par DAO | < 30 s | Non mesuré | 🟠 |
| Temps moyen OCR par page | < 5 s | Affiché mais pas de SLO | 🟠 |
| Précision extraction montants | ≥ 95 % | Non benchmarkée | 🔴 |
| Précision SVM classification | ≥ 85 % | Affichée mais pas de baseline | 🟠 |
| Taux de faux positifs anomalies | < 5 % | Non mesuré | 🔴 |
| Uptime API | ≥ 99 % | Non monitoré | 🔴 |
| Latence p95 recherche FTS | < 500 ms | Non mesuré | 🟠 |
| Conformité sécurité (auth, RBAC) | 100 % | 0 % | 🔴 |

---

## 4. Analyse des écarts (gap analysis)

### 4.1 Écarts fonctionnels (par priorité)

#### 🔴 P0 — Bloquants pour la mise en production

1. **Aucune authentification ni gestion de session** : tout le monde peut tout voir et tout faire.
2. **Aucun contrôle d'accès (RBAC)** : pas de distinction admin / analyste / lecteur.
3. **Pas d'audit log** : aucune traçabilité des actions sensibles (modification modèle, scraping manuel).
4. **Filtres de recherche incomplets** : impossible de filtrer par type d'avis, qualifications, agréments, état, dates clés.
5. **Pas d'export des résultats** (CSV/Excel) : incompatible avec un usage BI sérieux.
6. **Pas de tri configurable** des résultats de recherche.
7. **Pas de bouton Réinitialiser** sur le formulaire de recherche.
8. **Pas de gestion d'erreur visible** côté front (toast, fallback).
9. **Couverture E2E = 0** : risque de régression à chaque release.
10. **Pas de CI/CD documenté** : déploiement artisanal.

#### 🟠 P1 — Importants pour la BI

11. Pas de dimensions analytiques régionales (région/province).
12. Pas de comparaison temporelle (N vs N-1).
13. Pas de drill-down dans les graphiques.
14. Pas de prévisions / tendances.
15. Pas d'analyse par maître d'ouvrage avec courbes d'évolution.
16. Pas d'export PDF/PNG des graphiques.
17. Pas de filtre croisé dashboard ↔ recherche.
18. Pas de mode « multi-sélection » dans la watchlist ML.
19. Pas de labellisation en masse depuis l'UI.

#### 🟡 P2 — Améliorations UX

20. Pas d'i18n FR/AR.
21. Pas de mode contraste élevé / accessibilité.
22. Pas de favoris / recherche sauvegardée.
23. Pas de notifications push.
24. Pas de thème clair (uniquement dark mode).
25. Pas de raccourcis clavier.

### 4.2 Écarts techniques

| Domaine | Écart | Impact |
|---|---|---|
| Observabilité | Pas de métriques Prometheus, pas de tracing OpenTelemetry | Debug difficile en prod |
| Scalabilité | Pas de worker asynchrone dédié (Celery / RQ / Dramatiq) | Scraping bloque le thread API |
| Stockage | Pas de versioning des PDF sources, pas de stockage objet (S3/MinIO) | Risque de perte |
| Sécurité | Pas de chiffrement at rest, pas de secrets manager | Données sensibles exposées |
| Data quality | Pas de validation Great Expectations / Pandera | Données sales en BDD |
| Documentation API | OpenAPI auto-généré mais pas de guide d'usage | Adoption freinée |
| Versioning données | Pas de DVC, pas de DataWarehouse | Pas de time-travel |

---

## 5. Risques et points de vigilance

| # | Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Le site ministériel modifie sa structure HTML et casse le scraper | Élevée | Élevé | Tests de régression visuelle, abstraction des sélecteurs, alerting |
| R2 | Volume réel de DAO (milliers) fait tomber SQLite / pipeline | Élevée | Élevé | PostgreSQL prod, partitioning, batch asynchrone |
| R3 | OCR arabe de mauvaise qualité sur documents scannés | Élevée | Moyen | Modèle `ara` + prétraitement avancé + EasyOCR en fallback |
| R4 | Modèles ML biaisés par la distribution réelle | Moyenne | Élevé | Réentraînement périodique, monitoring drift, dataset d'audit |
| R5 | Extraction montants échoue sur formats exotiques | Moyenne | Élevé | Multi-regex + LLM de secours, validation humaine |
| R6 | Fuite de données sensibles (montants, cautions) | Faible | Critique | Auth, RBAC, audit, chiffrement |
| R7 | Indisponibilité prolongée du portail public | Faible | Élevé | Cache, reprise sur erreur, mode dégradé |
| R8 | Coût API LLM (si引入 pour fallback) | Moyenne | Moyen | Cache, batch, seuils de confiance |
| R9 | Perte de modèles ML entre déploiements | Faible | Élevé | Artefact registry, versioning, backup |
| R10 | Résultats faux positifs d'anomalies financières → méfiance utilisateur | Moyenne | Moyen | Explicabilité, seuils ajustables, validation humaine |

---

## 6. Scénarios de tests exhaustifs

### 6.1 Stratégie et convention de nommage

**Couches de test** (pyramide) :

```
        ┌─────────────────────┐
        │  Tests E2E (Cypress)│  ← Parcours utilisateur complet
        ├─────────────────────┤
        │  Tests d'intégration │  ← Modules combinés, BDD réelle
        │  (Pytest + TestClient│
        │   FastAPI)           │
        ├─────────────────────┤
        │  Tests unitaires     │  ← Fonctions pures, mocks
        │  (Pytest)            │  ← Couverture cible : 80 %+
        └─────────────────────┘
```

**Convention de nommage** : `T-XX-NNN-Description`
* `T-IN` Ingestion / scraping
* `T-OC` OCR / PDF
* `T-NL` NLP
* `T-FT` Full-text search
* `T-ML` Machine learning
* `T-DB` Dashboard / BI
* `T-UI` Interface par écran
* `T-AU` Authentification
* `T-SE` Sécurité
* `T-PE` Performance
* `T-API` API REST
* `T-E2E` End-to-end
* `T-RV` Régression visuelle

**Niveaux de priorité** :
* 🔴 **P0** : bloquant, à passer avant toute mise en production
* 🟠 **P1** : important, à passer avant la soutenance
* 🟡 **P2** : amélioration, à passer en sprint suivant

**Statuts possibles** : `PASS` / `FAIL` / `SKIP` / `BLOCKED`

---

### 6.2 Tests du module Ingestion & Scraping

#### T-IN-001 — Lancement manuel du scraper depuis PipelineAdmin 🔴
**Pré-conditions** : utilisateur sur l'écran PipelineAdmin, plage de dates valide.
**Étapes** :
1. Sélectionner une plage de dates (ex. 01/01/2024 → 31/01/2024).
2. Cliquer sur « Lancer le Scraping ».
3. Observer l'état du scraper.

**Résultat attendu** :
* Statut passe à `En cours` sous 2 s.
* Indicateur d'AO collectés incrémenté en temps réel.
* Bouton désactivé pendant l'exécution.
* À la fin : statut `Inactif`, nombre total d'AO cohérent avec le site.

**Critère de succès** : nombre collecté = nombre visible sur le site pour la même plage (± 2 % tolérance).

#### T-IN-002 — Scraping sans plage de dates 🟠
**Étapes** : cliquer « Lancer le Scraping » sans sélectionner de dates.
**Attendu** : message d'erreur de validation, pas de lancement silencieux.

#### T-IN-003 — Plage de dates inversée 🔴
**Étapes** : date début > date fin.
**Attendu** : erreur explicite, le scraper ne se lance pas.

#### T-IN-004 — Scraping de plage étendue (≥ 1 an) 🟠
**Étapes** : plage 01/01/2023 → 31/12/2023.
**Attendu** :
* Le scraper pagine correctement (≥ 10 pages).
* Aucune interruption sur timeout.
* Tous les fichiers ZIP sont téléchargés.
* Déduplication des doublons inter-pages.

#### T-IN-005 — Reprise après crash du scraper 🔴
**Étapes** : interrompre le scraper au milieu (kill -9), le relancer.
**Attendu** :
* Reprise depuis le dernier état stable.
* Pas de doublons en BDD.
* Logs de reprise visibles.

#### T-IN-006 — Téléchargement ZIP 🔴
**Attendu** : pour chaque AO, le ZIP contient le CPS, le RC et les annexes ; l'archive est sauvegardée sur disque avec hash SHA-256 enregistré.

#### T-IN-007 — Extraction des PDF depuis le ZIP 🟠
**Attendu** : chaque PDF est extrait, nommé de façon stable (`{ref}_{type}.pdf`), et indexé en BDD avec chemin relatif.

#### T-IN-008 — Détection des doublons entre exécutions 🟠
**Étapes** : relancer le scraping sur la même plage.
**Attendu** : aucun doublon créé (clé d'unicité sur référence).

#### T-IN-009 — Robustesse aux changements HTML du site 🔴
**Méthode** : utiliser un snapshot HTML du site (fichier fixture) et faire passer le scraper.
**Attendu** : sélecteurs découplés, au moins un test d'intégration par champ extrait.

#### T-IN-010 — Comportement en cas d'indisponibilité du site 🟠
**Attendu** : erreur HTTP capturée, message clair, retry exponentiel (3 essais, backoff 1s/2s/4s), alerte après échec définitif.

#### T-IN-011 — Pagination du site ministériel 🟠
**Attendu** : tous les résultats paginés sont parcourus, marque de fin détectée.

#### T-IN-012 — Extraction de la référence AO 🔴
**Attendu** : la référence correspond exactement à celle publiée (regex stricte, normalisation).

#### T-IN-013 — Logging des étapes de scraping 🟡
**Attendu** : chaque étape (URL visitée, bouton cliqué, fichier reçu) est loggée avec horodatage.

#### T-IN-014 — Limitation de débit (rate limiting) 🟡
**Attendu** : pas plus de 1 requête/seconde vers le site (politique de scraping responsable).

#### T-IN-015 — Exécution parallèle 🟡
**Attendu** : possibilité de lancer 2 workers en parallèle, pas de conflit d'écriture.

---

### 6.3 Tests du module OCR & PDF natif

#### T-OC-001 — Détection PDF natif vs scanné 🔴
**Fixture** : `pdf_textuel.pdf` (texte sélectionnable)ne.pdf` (image et `pdf_scan scannée).
**Attendu** :
* Natif : ratio texte/char > seuil (≥ 50 caractères par page en moyenne).
* Scanné : ratio < seuil, déclenche OCR.

#### T-OC-002 — Extraction native (PyMuPDF) 🔴
**Attendu** : texte extrait fidèle à l'original (comparaison SHA ou distance Levenshtein normalisée ≥ 95 %).

#### T-OC-003 — OCR sur PDF scanné en français 🔴
**Attendu** : texte OCRisé ≥ 90 % de précision (CER < 0,1) sur dataset de référence.

#### T-OC-004 — OCR sur PDF scanné en arabe 🟠
**Attendu** : texte OCRisé ≥ 80 % de précision sur dataset arabe.

#### T-OC-005 — OCR sur PDF bilingue FR/AR 🟠
**Attendu** : extraction des deux langues, séparateur logique présent.

#### T-OC-006 — Confiance OCR moyenne 🟠
**Attendu** : score `OcrLog.confidence` ∈ [0, 100], stocké par document.

#### T-OC-007 — Prétraitement d'image 🟡
**Fixture** : image à faible contraste, image inclinée.
**Attendu** : niveau de gris, binarisation, deskew appliqués (vérifier via hash d'image intermédiaire).

#### T-OC-008 — Performance OCR par page 🟠
**Attendu** : < 5 s par page en moyenne (SLI Monitoring), alerte si > 10 s.

#### T-OC-009 — OCR sur PDF de 200+ pages 🟠
**Attendu** : traitement complet sans crash mémoire (streaming PyMuPDF, batch OCR).

#### T-OC-010 — Reprise OCR après crash 🔴
**Attendu** : un document en cours d'OCR reprend à la dernière page traitée.

#### T-OC-011 — Caractères spéciaux et diacritiques 🟡
**Attendu** : reconnaissance correcte des accents français (é, è, ê, à) et des caractères arabes (ﷲ, ﷴ, ﷳ).

#### T-OC-012 — Tableaux et colonnes 🟡
**Attendu** : structure tabulaire préservée (sortie texte avec séparateurs, ou JSON structuré).

#### T-OC-013 — OCR sur PDF chiffré / protégé 🟠
**Attendu** : détection du chiffrement, message d'erreur explicite, pas de crash.

#### T-OC-014 — Métriques qualité CER/WER 🟡
**Attendu** : calcul automatique du CER par page, agrégé par document.

---

### 6.4 Tests du module NLP & Extraction

#### T-NL-001 — Extraction de la référence 🔴
**Corpus** : 20 DAO réels du dataset de test.
**Attendu** : ≥ 95 % de précision, ≥ 90 % de rappel.

#### T-NL-002 — Extraction de l'objet 🔴
**Attendu** : ≥ 90 % de précision, ≥ 85 % de rappel.

#### T-NL-003 — Extraction du maître d'ouvrage 🔴
**Attendu** : ≥ 90 % de précision, ≥ 85 % de rappel.

#### T-NL-004 — Extraction de la ville d'exécution 🟠
**Attendu** : ville correctement identifiée et normalisée (mapping provinces).

#### T-NL-005 — Extraction du montant estimé (MAD) 🔴
**Corpus** : 20 DAO avec montants variables.
**Attendu** :
* « 1 234 567,89 DH » → 1234567.89
* « un million deux cent mille dirhams » → 1200000
* « 1,2 M MAD » → 1200000
* Précision ≥ 95 %.

#### T-NL-006 — Extraction de la caution provisoire 🟠
**Attendu** : ≥ 90 % de précision.

#### T-NL-007 — Extraction du délai d'exécution 🟠
**Attendu** : « 6 mois » → 6 (mois), « 180 jours » → 180 (jours), normalisation ISO durée.

#### T-NL-008 — Normalisation des dates en ISO 🔴
**Attendu** :
* « 15/03/2024 » → `2024-03-15`
* « 15 mars 2024 » → `2024-03-15`
* « 15-03-24 » → `2024-03-15` (avec heuristique siècle).

#### T-NL-009 — Extraction du type d'avis 🔴
**Attendu** : classification en {ouvert, restreint, simplifié, avec présélection, concours, consultation, dialogue compétitif, bon de commande} avec ≥ 90 % de précision.

#### T-NL-010 — Extraction des qualifications 🟠
**Attendu** : identification des catégories (Qualification et Classification BTP, classes 1 à 6).

#### T-NL-011 — Extraction des agréments 🟠
**Attendu** : identification du type d'agrément et de la classe.

#### T-NL-012 — Extraction de la date d'ouverture des plis 🟠
**Attendu** : regex + heuristique (date + heure), ISO 8601.

#### T-NL-013 — Extraction de la date limite de remise 🟠
**Attendu** : idem, distinction claire avec date d'ouverture.

#### T-NL-014 — Reconnaissance bilingue FR/AR 🟠
**Attendu** : extraction des entités depuis la version arabe du document.

#### T-NL-015 — Score de confiance par entité 🟡
**Attendu** : chaque entité a un score ∈ [0, 1].

#### T-NL-016 — Robustesse aux fautes OCR 🟠
**Méthode** : injecter 5 % de bruit OCR simulé dans le texte, vérifier que l'extraction reste stable.

#### T-NL-017 — Détection de documents non conformes (sans entité clé) 🟠
**Attendu** : flag `low_quality = true` si moins de 3 entités extraites.

#### T-NL-018 — Idempotence de l'extraction 🟡
**Attendu** : relancer l'extraction sur le même document produit exactement les mêmes résultats.

#### T-NL-019 — Performance NLP par document 🟡
**Attendu** : < 3 s par document (SLO).

#### T-NL-020 — Audit des regex utilisées 🟡
**Attendu** : tests unitaires sur ≥ 50 patterns d'extraction variés.

---

### 6.5 Tests du module Recherche FTS

#### T-FT-001 — Recherche simple par mot-clé 🔴
**Étapes** : saisir « route » dans la barre de recherche.
**Attendu** : tous les documents contenant le mot « route » sont retournés.

#### T-FT-002 — Recherche par référence exacte 🟠
**Étapes** : saisir la référence complète d'un DAO.
**Attendu** : seul ce document est retourné, en première position.

#### T-FT-003 — Recherche multi-mots 🔴
**Étapes** : saisir « pont métallique ».
**Attendu** : documents contenant les deux mots (ET logique) ; expliquer le mode (AND/OR) à l'utilisateur.

#### T-FT-004 — Recherche par phrase exacte 🟠
**Étapes** : saisir `"voie de contournement"`.
**Attendu** : documents contenant l'expression exacte.

#### T-FT-005 — Opérateurs booléens 🟠
**Étapes** : saisir `route ET (pont OU viaduc) NON ferroviaire`.
**Attendu** : résultats conformes à l'algèbre booléenne.

#### T-FT-006 — Recherche floue (fuzzy) 🟡
**Étapes** : saisir « rout » (faute de frappe).
**Attendu** : suggestions et résultats incluant « route ».

#### T-FT-007 — Autocomplétion 🟠
**Attendu** : top 5 suggestions affichées sous 200 ms, basées sur l'historique et l'index.

#### T-FT-008 — Filtre par ville 🔴
**Attendu** : combinaison « route » + ville = résultats intersectés.

#### T-FT-009 — Filtre par budget min/max 🔴
**Étapes** : saisir 1 000 000 → 5 000 000.
**Attendu** : seulement les AO dont le montant extrait est dans la plage.

#### T-FT-010 — Filtre par date de publication 🟠
**Attendu** : AO publiés dans la plage.

#### T-FT-011 — Filtre par date d'ouverture des plis 🟠
**Attendu** : AO dont la date d'ouverture est dans la plage.

#### T-FT-012 — Filtre par date limite de remise 🟠
**Attendu** : AO dont la date limite est dans la plage.

#### T-FT-013 — Filtre par qualifications 🟠
**Attendu** : AO requérant la qualification sélectionnée.

#### T-FT-014 — Filtre par agréments 🟠
**Attendu** : AO requérant l'agrément sélectionné.

#### T-FT-015 — Filtre par type d'avis 🟠
**Attendu** : AO du type sélectionné.

#### T-FT-016 — Filtre par état (en cours, clôturé…) 🟠
**Attendu** : AO dans l'état sélectionné.

#### T-FT-017 — Filtre par maître d'ouvrage 🟠
**Attendu** : AO émis par l'organisme sélectionné.

#### T-FT-018 — Filtre par langue 🟡
**Attendu** : AO dans la langue sélectionnée.

#### T-FT-019 — Tri des résultats (date desc) 🟠
**Attendu** : résultats triés du plus récent au plus ancien.

#### T-FT-020 — Tri par montant 🟠
**Attendu** : tri croissant ou décroissant.

#### T-FT-021 — Tri par pertinence 🟠
**Attendu** : tri par score BM25 ou TF-IDF.

#### T-FT-022 — Surlignage des termes trouvés 🟠
**Attendu** : dans la preview du résultat, les mots-clés sont surlignés.

#### T-FT-023 — Pagination 🟠
**Attendu** : taille de page 20, navigation fonctionnelle, dernière page détectée.

#### T-FT-024 — Compteur de résultats 🔴
**Attendu** : « 142 résultats trouvés en 87 ms ».

#### T-FT-025 — Performance p95 🔴
**Attendu** : p95 latence < 500 ms pour 100 000 documents indexés.

#### T-FT-026 — Bouton Réinitialiser 🔴
**Attendu** : tous les filtres remis à zéro, résultats réinitialisés.

#### T-FT-027 — Sauvegarde de recherche 🟡
**Attendu** : possibilité d'enregistrer un set de filtres sous un nom.

#### T-FT-028 — Export CSV des résultats 🔴
**Attendu** : export conforme RGPD, encoding UTF-8, séparateur `,`.

#### T-FT-029 — Export Excel 🟠
**Attendu** : fichier `.xlsx` avec mise en forme (en-têtes, types).

#### T-FT-030 — Aucun résultat trouvé 🟠
**Attendu** : message « Aucun résultat. Essayez d'élargir vos critères. » + suggestions.

#### T-FT-031 — Recherche vide 🔴
**Attendu** : soit désactiver le bouton, soit retourner tous les documents (avec confirmation).

#### T-FT-032 — Sécurité FTS (injection SQL) 🔴
**Attendu** : aucune injection possible (ORM paramétré, escape des caractères spéciaux).

---

### 6.6 Tests du module Machine Learning

#### T-ML-001 — Entraînement SVM sur dataset d'entraînement 🔴
**Attendu** : le modèle converge, accuracy > 85 % sur jeu de validation.

#### T-ML-002 — Sauvegarde / chargement Joblib 🟠
**Attendu** : le modèle sérialisé est rechargé et donne les mêmes prédictions.

#### T-ML-003 — Classification d'un nouveau document 🟠
**Attendu** : catégorie prédite cohérente avec l'objet du DAO.

#### T-ML-004 — Score de confiance de classification 🟠
**Attendu** : probabilité ∈ [0, 1], affichée dans le détail.

#### T-ML-005 — Ré-entraînement asynchrone 🔴
**Attendu** : endpoint API, exécution en background, statut consultable.

#### T-ML-006 — IsolationForest sur données financières 🟠
**Attendu** : au moins 1 anomalie détectée sur un dataset synthétique incluant 1 % d'outliers.

#### T-ML-007 — Explicabilité des anomalies 🟠
**Attendu** : chaque alerte explique pourquoi (montant élevé + délai court + caution disproportionnée).

#### T-ML-008 — Watchlist des désaccords IA vs humain 🟠
**Attendu** : tableau des documents où la catégorie humaine ≠ catégorie IA.

#### T-ML-009 — Validation humaine depuis l'UI 🟠
**Attendu** : un admin peut corriger la catégorie, l'événement est tracé.

#### T-ML-010 — Métriques précision/rappel/F1 🟠
**Attendu** : affichées dans PredictorML avec dates d'évaluation.

#### T-ML-011 — Matrice de confusion 🟡
**Attendu** : heatmap affichée dans PredictorML.

#### T-ML-012 — Feature importance 🟡
**Attendu** : top 20 features TF-IDF pondérées par coefficient SVM.

#### T-ML-013 — Versioning des modèles 🟡
**Attendu** : chaque version taggée, possibilité de rollback.

#### T-ML-014 — Drift monitoring 🟡
**Attendu** : alerte si la distribution des features change significativement (KS test ou PSI).

#### T-ML-015 — A/B testing entre deux versions 🟡
**Attendu** : split du trafic, comparaison des métriques.

#### T-ML-016 — Biais géographique 🟡
**Attendu** : vérification que le modèle ne défavorise pas certaines régions.

#### T-ML-017 — Biais temporel 🟡
**Attendu** : vérification que le modèle ne se dégrade pas avec le temps (réentraînement planifié).

#### T-ML-018 — Robustesse aux inputs vides 🟠
**Attendu** : si le texte OCR est vide ou très court, le modèle retourne une classe par défaut + flag.

#### T-ML-019 — Latence inférence 🟡
**Attendu** : < 200 ms par document.

#### T-ML-020 — Test de régression modèle 🟡
**Méthode** : golden dataset avec prédictions attendues, comparaison après chaque réentraînement.

---

### 6.7 Tests du Dashboard BI

#### T-DB-001 — Affichage des 4 KPI principaux 🔴
**Attendu** : nombre de marchés, budget cumulé, délai moyen, taux OCR — chiffres cohérents avec la BDD.

#### T-DB-002 — Graphique camembert des catégories 🟠
**Attendu** : répartition cohérente, tooltip avec valeurs exactes, légende interactive.

#### T-DB-003 — Top 10 acheteurs par volume 🟠
**Attendu** : tri décroissant, valeurs correctes.

#### T-DB-004 — État vide (aucun document) 🟠
**Attendu** : message « Aucune donnée à afficher » + CTA « Importer un document ».

#### T-DB-005 — Chargement (loader / skeleton) 🟡
**Attendu** : skeleton screen pendant le fetch, pas d'écran blanc.

#### T-DB-006 — Filtre temporel sur le dashboard 🟠
**Attendu** : dropdown année/mois/trimestre, mise à jour des graphiques.

#### T-DB-007 — Filtre par catégorie 🟠
**Attendu** : mise à jour du camembert.

#### T-DB-008 — Drill-down (clic sur une part de camembert) 🟡
**Attendu** : ouverture d'une modale ou navigation vers la liste filtrée.

#### T-DB-009 — Comparaison N vs N-1 🟠
**Attendu** : indicateurs d'évolution (flèches haut/bas + %).

#### T-DB-010 — Export PNG des graphiques 🟡
**Attendu** : bouton de téléchargement de chaque chart.

#### T-DB-011 — Export PDF du dashboard 🟡
**Attendu** : génération d'un rapport PDF avec les graphiques.

#### T-DB-012 — Performance dashboard p95 🔴
**Attendu** : < 1 s pour le rendu initial.

#### T-DB-013 — Actualisation automatique 🟡
**Attendu** : WebSocket ou polling toutes les 30 s, animation de transition.

#### T-DB-014 — Cartographie du Maroc (carte choroplèthe) 🟡
**Attendu** : carte du Maroc colorée par région selon le volume financier ou le nombre d'AO.

#### T-DB-015 — Heatmap calendrier des publications 🟡
**Attendu** : type GitHub contributions, intensité par jour.

#### T-DB-016 — Funnel des étapes (publication → attribution) 🟡
**Attendu** : visualisation des étapes du cycle de vie d'un AO.

#### T-DB-017 — Tableau des anomalies détectées 🟡
**Attendu** : accès direct depuis le dashboard à la liste des AO atypiques.

#### T-DB-018 — Accessibilité (lecteur d'écran) 🟡
**Attendu** : `aria-label`, navigation clavier, contraste WCAG AA.

#### T-DB-019 — Responsive mobile 🟠
**Attendu** : layout adapté < 768 px, graphiques redimensionnés.

#### T-DB-020 — Internationalisation FR/AR des labels 🟡
**Attendu** : traduction complète des KPI, des axes, des tooltips.

---

### 6.8 Tests par écran

#### E1 — LandingPage
- T-UI-001 Affichage correct de la bannière 🔴
- T-UI-002 Statistiques en temps réel 🟠
- T-UI-003 Responsive mobile/tablette 🟠
- T-UI-004 Animations de transition 🟡

#### E2 — Dashboard
- T-DB-001 à T-DB-020 (voir 6.7)

#### E3 — SearchFTS
- T-FT-001 à T-FT-032 (voir 6.5) + tests UI :
- T-UI-010 Affichage de la liste des résultats 🔴
- T-UI-011 Mise en surbrillance des termes 🟠
- T-UI-012 Bouton « Voir le détail » fonctionnel 🔴
- T-UI-013 Tri interactif des colonnes 🟠
- T-UI-014 Pagination accessible 🟠

#### E4 — DocumentDetail
- T-UI-020 Affichage des 3 onglets 🔴
- T-UI-021 Téléchargement du PDF original 🔴
- T-UI-022 Téléchargement du texte OCR 🟠
- T-UI-023 Affichage des scores NLP 🟠
- T-UI-024 Affichage des anomalies ML 🟠
- T-UI-025 URL partageable (deep link) 🟠
- T-UI-026 Bouton « Imprimer » 🟡

#### E5 — Explorer
- T-UI-030 Liste paginée des fichiers 🔴
- T-UI-031 Filtrage par type 🟠
- T-UI-032 Filtrage par statut 🟠
- T-UI-033 Tri par date / taille / nom 🟠
- T-UI-034 Téléchargement direct 🟠
- T-UI-035 Suppression (avec confirmation) 🟠
- T-UI-036 Recherche dans l'explorer 🟠

#### E6 — Upload
- T-UI-040 Drag & drop multi-fichiers 🔴
- T-UI-041 File d'attente visuelle 🔴
- T-UI-042 Polling du statut 🟠
- T-UI-043 Barre de progression par fichier 🟠
- T-UI-044 Annulation d'un upload en cours 🟡
- T-UI-045 Gestion des erreurs (fichier trop gros, type invalide) 🟠
- T-UI-046 Notification finale (toast) 🟠
- T-UI-047 Limite de taille configurable 🟡

#### E7 — PredictorML
- T-UI-050 Affichage précision du modèle 🟠
- T-UI-051 Bouton « Ré-entraîner » avec confirmation 🟠
- T-UI-052 Watchlist interactive 🟠
- T-UI-053 Validation humaine en lot 🟡
- T-UI-054 Comparaison historique des modèles 🟡

#### E8 — Monitoring
- T-UI-060 Logs en temps réel (auto-refresh) 🟠
- T-UI-061 Filtre par niveau (INFO/WARN/ERROR) 🟠
- T-UI-062 Recherche dans les logs 🟠
- T-UI-063 Export des logs 🟡
- T-UI-064 Statistiques temps OCR 🟠
- T-UI-065 Alertes visuelles sur erreurs 🟠

#### E9 — PipelineAdmin
- T-UI-070 Sélection plage de dates 🟠
- T-UI-071 Lancement scraping (cf. T-IN-001) 🔴
- T-UI-072 Statut temps réel 🟠
- T-UI-073 Annulation d'un scraping en cours 🟡
- T-UI-074 Historique des exécutions 🟡

---

### 6.9 Tests de sécurité et d'accès

#### T-AU-001 — Accès sans authentification 🔴
**Attendu** (état cible) : redirection vers `/login`.

#### T-AU-002 — Login valide 🔴
**Attendu** : JWT émis, cookie httpOnly sécurisé, redirection vers LandingPage.

#### T-AU-003 — Login invalide 🔴
**Attendu** : message « Identifiants incorrects », pas d'indication sur le champ fautif.

#### T-AU-004 — Mot de passe oublié 🔴
**Attendu** :流程 par email avec token à durée limitée (15 min).

#### T-AU-005 — Changement de mot de passe 🟠
**Attendu** : impose l'ancien mot de passe, complexité (12+ caractères, majuscule, chiffre, spécial).

#### T-AU-006 — Verrouillage après 5 tentatives 🔴
**Attendu** : compte temporairement bloqué (15 min), alerte email.

#### T-AU-007 — Session expirée 🟠
**Attendu** : redirection vers login, message « Session expirée ».

#### T-AU-008 — RBAC : utilisateur `reader` 🟠
**Attendu** : peut consulter mais pas supprimer ni modifier.

#### T-AU-009 — RBAC : utilisateur `analyst` 🟠
**Attendu** : peut lancer le scraping et ré-entraîner les modèles.

#### T-AU-010 — RBAC : utilisateur `admin` 🔴
**Attendu** : accès complet, gestion des utilisateurs.

#### T-AU-011 — Audit log 🔴
**Attendu** : toute action sensible (login, modification modèle, suppression, scraping) est tracée.

#### T-SE-001 — Injection SQL 🔴
**Méthode** : envoyer `' OR 1=1 --` dans tous les champs de recherche.
**Attendu** : aucune injection, requêtes paramétrées.

#### T-SE-002 — XSS stocké 🔴
**Méthode** : injecter `<script>alert(1)</script>` dans le titre d'un document.
**Attendu** : échappé, pas d'exécution.

#### T-SE-003 — XSS réfléchi 🟠
**Méthode** : `?q=<script>alert(1)</script>` dans l'URL.
**Attendu** : échappé.

#### T-SE-004 — CSRF 🔴
**Méthode** : POST sans token CSRF.
**Attendu** : rejeté.

#### T-SE-005 — Headers de sécurité HTTP 🔴
**Attendu** : `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Content-Security-Policy`.

#### T-SE-006 — Exposition des secrets 🔴
**Méthode** : vérifier que les clés API ne fuient pas dans les bundles front.
**Attendu** : 0 secret exposé.

#### T-SE-007 — HTTPS obligatoire 🔴
**Attendu** : redirection HTTP → HTTPS.

#### T-SE-008 — CORS strict 🟠
**Attendu** : liste blanche de domaines, pas de `*`.

#### T-SE-009 — Rate limiting 🟠
**Attendu** : 100 req/min par IP, retour 429 au-delà.

#### T-SE-010 — Validation des uploads 🟠
**Attendu** : rejet des fichiers non PDF/ZIP, taille max configurable.

#### T-SE-011 — Logs non sensibles 🔴
**Attendu** : aucun mot de passe ni token dans les logs.

#### T-SE-012 — Chiffrement at rest 🟡
**Attendu** : BDD et stockage fichiers chiffrés (LUKS / KMS).

---

### 6.10 Tests de performance

#### T-PE-001 — Indexation de 1 000 documents 🟠
**Attendu** : < 1 h end-to-end (scraping + OCR + NLP + indexation FTS).

#### T-PE-002 — Indexation de 10 000 documents 🟠
**Attendu** : < 12 h, sans saturation mémoire.

#### T-PE-003 — Recherche FTS sur 10 000 docs 🔴
**Attendu** : p95 < 500 ms, p99 < 1 s.

#### T-PE-004 — Charge concurrente API (50 users) 🟠
**Attendu** : < 1 % d'erreurs, latence stable.

#### T-PE-005 — Charge concurrente (200 users) 🟡
**Attendu** : dégradation contrôlée, circuit breaker actif.

#### T-PE-006 — Mémoire OCR sur PDF 500 pages 🟡
**Attendu** : pic < 2 Go par worker.

#### T-PE-007 — Mémoire FTS sur 1 M de pages 🟡
**Attendu** : pic < 4 Go.

#### T-PE-008 — Cold start API 🟡
**Attendu** : < 3 s après déploiement.

#### T-PE-009 — Build front (Vite) 🟡
**Attendu** : < 30 s.

#### T-PE-010 — Bundle size front 🟡
**Attendu** : < 500 Ko gzippé.

#### T-PE-011 — Time to first byte (TTFB) 🟡
**Attendu** : < 200 ms.

#### T-PE-012 — Largest Contentful Paint (LCP) 🟠
**Attendu** : < 2,5 s sur 3G.

#### T-PE-013 — Cumulative Layout Shift (CLS) 🟠
**Attendu** : < 0,1.

#### T-PE-014 — First Input Delay (FID) 🟠
**Attendu** : < 100 ms.

#### T-PE-015 — Stress test scraping (site lent) 🟡
**Attendu** : timeouts bien gérés, pas de cascade d'échecs.

---

### 6.11 Tests d'API (FastAPI / OpenAPI)

#### T-API-001 — `GET /api/health` 🔴
**Attendu** : 200 OK, `{"status": "ok", "version": "x.y.z"}`.

#### T-API-002 — `GET /api/documents` 🔴
**Attendu** : pagination, filtres, JSON conforme au schéma OpenAPI.

#### T-API-003 — `GET /api/documents/{id}` 🔴
**Attendu** : 200 avec détails, 404 si inexistant.

#### T-API-004 — `POST /api/documents` (upload) 🔴
**Attendu** : 201 Created, ID retourné, validation multipart.

#### T-API-005 — `DELETE /api/documents/{id}` 🟠
**Attendu** : 204 No Content, suppression logique (soft delete) ou physique selon politique.

#### T-API-006 — `GET /api/search?q=...` 🔴
**Attendu** : 200, format `{results: [...], total: N, took_ms: 87}`.

#### T-API-007 — `GET /api/analytics/dashboard` 🟠
**Attendu** : KPIs et séries temporelles.

#### T-API-008 — `POST /api/ml/train` 🟠
**Attendu** : 202 Accepted, ID de job, suivi via `GET /api/ml/jobs/{id}`.

#### T-API-009 — `POST /api/scraper/run` 🟠
**Attendu** : 202 Accepted, job en background.

#### T-API-010 — `GET /api/scraper/status` 🟠
**Attendu** : statut courant, nombre collecté.

#### T-API-011 — Validation des schémas Pydantic 🔴
**Attendu** : 422 avec détails sur champs invalides.

#### T-API-012 — Documentation OpenAPI 🟠
**Attendu** : `/docs` Swagger UI, `/redoc` ReDoc, exemples cohérents.

#### T-API-013 — Versioning de l'API 🟡
**Attendu** : header `Accept: application/vnd.ged.v2+json` ou préfixe `/api/v1`.

#### T-API-014 — Idempotence des POST 🟡
**Attendu** : même requête répétée ne crée pas de doublon (Idempotency-Key).

#### T-API-015 — Rate limiting par utilisateur 🟠
**Attendu** : 429 au-delà du quota.

#### T-API-016 — Tests de contrat (Pact / Schemathesis) 🟡
**Attendu** : vérification automatique que le front consomme une API conforme.

---

### 6.12 Tests d'intégration bout-en-bout

#### T-E2E-001 — Parcours complet utilisateur « Lecteur » 🔴
1. Connexion avec compte `reader`.
2. Landing → Dashboard.
3. Recherche par mots-clés « pont ».
4. Ouverture du détail d'un document.
5. Téléchargement du PDF.
6. Déconnexion.

**Attendu** : parcours sans erreur, UI cohérente, audit log mis à jour.

#### T-E2E-002 — Parcours « Analyste » lance un scraping 🟠
1. Connexion `analyst`.
2. PipelineAdmin → plage de dates.
3. Lancer scraping.
4. Suivi temps réel.
5. Une fois terminé, aller sur Dashboard.
6. Vérifier que les nouveaux documents apparaissent.

#### T-E2E-003 — Parcours « Admin » ré-entraîne un modèle 🟠
1. Connexion `admin`.
2. PredictorML.
3. Lancer ré-entraînement.
4. Suivi du job.
5. Vérifier nouvelle précision.

#### T-E2E-004 — Parcours « Import manuel + labellisation » 🟠
1. Connexion `analyst`.
2. Upload d'un PDF.
3. Suivi de l'OCR + NLP temps réel.
4. Vérification des entités extraites.
5. Correction manuelle si nécessaire.

#### T-E2E-005 — Scénario d'anomalie détectée 🟡
1. Import d'un DAO avec caution disproportionnée (synthétique).
2. IsolationForest le flag.
3. Apparition dans PredictorML et Dashboard.
4. Notification (email + toast).

#### T-E2E-006 — Bascule FR/AR 🟡
1. Changement de langue.
2. Tous les écrans affichés en arabe (y compris graphiques, dates en chiffres arabes).
3. RTL layout actif.

#### T-E2E-007 — Mode dégradé (site inaccessible) 🟡
1. Couper l'accès au site ministériel (DNS blackhole).
2. Lancer scraping.
3. Erreur claire, retry, pas de crash.

#### T-E2E-008 — Multi-utilisateurs simultanés 🟡
**Outil** : Locust / k6, 50 virtual users.
**Attendu** : pas de conflit, base cohérente.

---

### 6.13 Tests de régression visuelle

#### T-RV-001 — Snapshot LandingPage (desktop) 🟠
**Outil** : Percy / Chromatic.
**Attendu** : diff < 0,1 %.

#### T-RV-002 — Snapshot Dashboard (mobile) 🟡
Idem.

#### T-RV-003 — Snapshot DocumentDetail (multilingue) 🟡
Idem avec FR et AR.

#### T-RV-004 — Thèmes (dark / light) 🟡
Vérifier les deux thèmes sur tous les écrans.

#### T-RV-005 — Composants critiques (boutons, modales, toasts) 🟡
Bibliothèque de composants Storybook avec snapshots.

---

## 7. Critères d'acceptation globaux

Le projet est considéré comme **prêt pour la mise en production** si et seulement si :

| Domaine | Critère |
|---|---|
| Couverture fonctionnelle | ≥ 90 % des champs du formulaire `criteres.aspx` sont couverts (cf. matrice §2.3) |
| Couverture de tests unitaires | ≥ 80 % (mesurée par `pytest-cov`) |
| Tests E2E (Cypress) | ≥ 20 scénarios passent en CI |
| Performance | p95 API < 500 ms, p95 FTS < 500 ms, p95 dashboard < 1 s |
| Sécurité | 100 % des tests T-AU-*** et T-SE-*** passent |
| Accessibilité | Score Lighthouse ≥ 90 |
| Documentation | README, guide d'utilisation, doc API, guide de déploiement |
| Observabilité | Logs structurés, métriques Prometheus, tracing OpenTelemetry |
| Internationalisation | FR complet, AR sur tous les écrans publics |
| Authentification | JWT + RBAC opérationnels |

**Sprint de fermeture cible** : 3 à 4 semaines après la soutenance pour transformer le PFA en MVP industrialisable.

---

## 8. Annexes

### 8.1 Jeu de données de test recommandé

| Dataset | Source | Taille | Usage |
|---|---|---|---|
| Golden set OCR | 20 DAO de référence du Ministère | 20 docs | Tests T-OC-*** |
| Golden set NLP | Mêmes 20 docs annotés manuellement | 20 docs | Tests T-NL-*** |
| Golden set ML | 200 docs labellisés | 200 docs | Tests T-ML-*** |
| Golden set FTS | 100 docs avec requêtes associées | 100 docs | Tests T-FT-*** |
| Stress test | 10 000 PDF aléatoires publics | 10 000 docs | Tests T-PE-*** |

### 8.2 Outils recommandés

| Domaine | Outil | Rôle |
|---|---|---|
| Tests unitaires | Pytest | Python |
| Tests API | Pytest + TestClient FastAPI | Intégration |
| Tests E2E | Cypress ou Playwright | UI |
| Couverture | pytest-cov | Mesurer |
| Régression visuelle | Percy / Chromatic / Playwright snapshots | UI |
| Charge | Locust / k6 | Performance |
| Sécurité OWASP | OWASP ZAP, Bandit, Trivy | Audit |
| Qualité code | Black, Ruff, mypy | Lint / types |
| Contract testing | Schemathesis, Pact | API contract |
| Monitoring | Prometheus, Grafana, Sentry | Production |

### 8.3 Checkliste d'exécution par sprint

```
Sprint N :
  [ ] Tous les tests P0 exécutés et PASSED
  [ ] Couverture ≥ cible
  [ ] Performance SLO respectée
  [ ] Démo fonctionnelle enregistrée
  [ ] Documentation mise à jour
  [ ] CHANGELOG.md incrémenté
  [ ] Tag Git + release notes
```

### 8.4 Glossaire

* **AO** : Appel d'Offres
* **DAO** : Dossier d'Appel d'Offres
* **CPS** : Cahier des Prescriptions Spéciales
* **RC** : Règlement de Consultation
* **FTS** : Full-Text Search
* **GIN** : Generalized Inverted Index (PostgreSQL)
* **CER / WER** : Character / Word Error Rate
* **PFA** : Projet de Fin d'Année
* **DSI** : Direction des Systèmes d'Information
* **SLA / SLO** : Service Level Agreement / Objective
* **RBAC** : Role-Based Access Control
* **BM25** : algorithme de ranking FTS
* **NER** : Named Entity Recognition
* **MLOps** : Machine Learning Operations
* **RTL** : Right-To-Left (layout arabe)

---

> **Conclusion Fichier 1** : Le projet PFA démontre une chaîne de valeur NLP/ML maîtrisée et une stack moderne. Le passage en production nécessite (1) l'alignement complet sur les champs du formulaire ministériel, (2) le durcissement de la sécurité et de l'observabilité, (3) une couverture de tests E2E et de performance, et (4) une discipline de qualité automatisée en CI.
