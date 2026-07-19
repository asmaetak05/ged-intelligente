# 🎫 Lot 7 : Frontend — Recherche & Filtrage Avancé (Search & FTS)

## 📌 Présentation du Lot
Ce lot enrichit l'expérience de recherche sémantique de l'utilisateur en ajoutant un panneau de filtres avancés, un bouton de réinitialisation rapide des critères, et la possibilité d'exporter les résultats trouvés au format CSV ou Excel.

* **Complexité globale** : Medium
* **Composants impactés** : `frontend-react/src/components/SearchFTS.jsx`, `frontend-react/src/components/AdvancedFilters.jsx` (nouveau)
* **Indépendance git** : Très bonne. Les modifications sont circonscrites à la vue de recherche et aux composants de filtrage associés.

---

## 📋 Liste des Tickets Associés

### 1. UI-04 — Bouton « Réinitialiser » sur les filtres de recherche 🔴
* **Priorité** : 🔴 P0
* **Effort** : S (0.5 j)
* **Composant** : `frontend-react/src/components/SearchFTS.jsx`
* **Scénarios de test liés** : `ST-FT-026`, `ST-E2E-010`
* **Description** : Permettre à l'utilisateur de vider instantanément tous ses filtres de recherche actifs (mots-clés, date, ville, budget) pour revenir à la liste globale par défaut.

### 2. UI-05 — Panneau de filtres avancés 🔴
* **Priorité** : 🔴 P0
* **Effort** : M (3 j)
* **Composant** : `frontend-react/src/components/AdvancedFilters.jsx`
* **Scénarios de test liés** : `ST-UI-016`, `ST-FT-013` à `ST-FT-016`
* **Description** : Créer un panneau rétractable proposant des filtres de recherche plus fins :
  - Recherche par type de procédure (ouvert, restreint).
  - Sélection des qualifications requises.
  - Saisie de la caution provisoire min/max.
  - Filtre par date d'ouverture des plis.

### 3. UI-07 — Export CSV / Excel des résultats de recherche 🔴
* **Priorité** : 🔴 P0
* **Effort** : M (2 j)
* **Composant** : `frontend-react/src/components/SearchFTS.jsx`
* **Scénarios de test liés** : `ST-FT-028`, `ST-FT-029`, `ST-E2E-009`
* **Description** : Ajouter un bouton permettant de télécharger les lignes de résultats courantes sous forme de fichier d'extraction CSV ou d'un classeur Excel (généré côté client ou via un flux binaire renvoyé par l'API).

### 4. UI-09 — Filtrage des résultats par état de l'avis (En cours, Clôturé) 🔴
* **Priorité** : 🔴 P0
* **Effort** : S (0.5 j)
* **Composant** : `frontend-react/src/components/AdvancedFilters.jsx`
* **Scénarios de test liés** : `ST-FT-016`
* **Description** : Permettre de filtrer les appels d'offres selon leur statut d'avancement administratif (Avis en cours, Résultats publiés, Annulé, Clôturé).

---

## 🛠️ Description des Travaux
1. **Création du composant de filtrage** :
   - Écrire `frontend-react/src/components/AdvancedFilters.jsx` avec des éléments d'interface interactifs (menus déroulants, sélecteurs de dates).
2. **Gestion de l'export client** :
   - Installer une bibliothèque légère (ex. `xlsx` ou parser CSV natif) ou appeler l'endpoint d'export backend et gérer le téléchargement du blob.

---

## 🧪 Critères de Validation et Non-régression
- **Test de réinitialisation** : Remplir 4 filtres différents, lancer la recherche, cliquer sur "Réinitialiser" et vérifier que l'URL/les inputs redeviennent vierges et que la liste globale par défaut est rechargée.
- **Vérification d'export** : Effectuer une recherche de test, cliquer sur "Exporter CSV" et vérifier que le navigateur déclenche le téléchargement d'un fichier `.csv` lisible contenant précisément les colonnes des résultats.
