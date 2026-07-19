# 🎫 Lot 4 : NLP & Structuration Sémantique (NLP & Extraction)

## 📌 Présentation du Lot
Ce lot enrichit les capacités d'extraction du moteur NLP pour structurer des informations métier cruciales (types de procédures, qualifications requises et agréments ministériels), et optimise la précision de l'extraction de l'acheteur (maître d'ouvrage).

* **Complexité globale** : Medium
* **Composants impactés** : `nlp/` (fichiers existants et nouveaux), `backend/schemas.py`
* **Indépendance git** : Totale. Il travaille sur les règles sémantiques en amont de l'exposition API et n'affecte pas l'infrastructure ou l'interface frontend.

---

## 📋 Liste des Tickets Associés

### 1. NLP-01 — Extraction du type d'avis (8 valeurs officielles) 🔴
* **Priorité** : 🔴 P0
* **Effort** : M (3 j)
* **Composant** : `nlp/extract_typeavis.py`
* **Scénarios de test liés** : `ST-NL-009`, `ST-FT-015`
* **Description** : Identifier automatiquement le type de l'avis de marché (ex. Appel d'offres ouvert, restreint, concours, procédure simplifiée, etc.).
* **Travail** : Créer un dictionnaire de patterns regex et de synonymes pour cartographier les 8 typologies officielles de la réglementation marocaine.

### 2. NLP-02 — Extraction des qualifications requises (Q1-Q6 BTP) 🟠
* **Priorité** : 🟠 P1
* **Effort** : M (2 j)
* **Composant** : `nlp/extract_qualif.py`
* **Scénarios de test liés** : `ST-NL-010`, `ST-FT-013`
* **Description** : Extraire les qualifications et classifications exigées pour les entreprises de BTP (ex. Classe 1, qualification Q1, Q2, etc.) mentionnées dans le Règlement de Consultation (RC).
* **Travail** : Implémenter des expressions régulières robustes aux sauts de ligne et à la casse.

### 3. NLP-03 — Extraction des agréments ministériels exigés 🟠
* **Priorité** : 🟠 P1
* **Effort** : M (2 j)
* **Composant** : `nlp/extract_agrement.py`
* **Scénarios de test liés** : `ST-NL-011`, `ST-FT-014`
* **Description** : Analyser les sections relatives aux agréments exigés par le Ministère de l'Équipement pour les bureaux d'études et de contrôle (ex. agrément D9, D12).
* **Travail** : Concevoir des règles d'extraction structurées pour récupérer le domaine et la classe d'agrément.

### 4. NLP-16 — Optimisation de l'extraction de l'acheteur (Maître d'ouvrage) 🟠
* **Priorité** : 🟠 P1
* **Effort** : M (2 j)
* **Composant** : `nlp/extract_entities.py:84-94`
* **Scénarios de test liés** : `ST-NL-003`
* **Description** : Refactoriser le bloc d'extraction de l'acheteur public dans `extract_entities.py` pour éliminer un conflit d'exécution logique. Actuellement, si la recherche par spaCy est activée, le bloc de recherche par regex n'est jamais exécuté en secours.
* **Travail** : Implémenter un système de scoring combinant spaCy (reconnaissance sémantique d'entités) et Regex.

---

## 🛠️ Description des Travaux
1. **Création des modules d'extraction dans `nlp/`** :
   - Écrire `nlp/extract_typeavis.py`, `nlp/extract_qualif.py` et `nlp/extract_agrement.py`.
   - Les importer dans l'orchestrateur principal `nlp/extract_entities.py`.
2. **Développement des dictionnaires d'entités** :
   - Déclarer des expressions régulières précises basées sur des D.A.O. marocains types.

---

## 🧪 Critères de Validation et Non-régression
- **Test unitaire sémantique** : Créer `tests/test_nlp_extraction_avancee.py` contenant des extraits de textes réels de CPS et s'assurer que les classes d'agrément (ex. "D12") ou de qualification (ex. "Q3") sont correctement renvoyées dans le dictionnaire JSON de sortie.
- **Vérification de non-régression** : Lancer `pytest tests/test_nlp.py` et vérifier que les anciennes extractions (dates, montants) fonctionnent toujours sans erreur.
