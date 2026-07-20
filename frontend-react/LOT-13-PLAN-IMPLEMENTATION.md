# 🗺️ Plan d'implémentation phasé — Lot 13 : Frontend

> **Périmètre** : Tous les tickets **UI-01..40** (40 tickets) + **E-10..24** (15 écrans) référencés dans `04-tickets-ameliorations.md` § 8 & § 14, complétés par les tickets transverses **F-04 (i18n)** et **F-05 (a11y)** qui sont implémentés côté frontend.
>
> **Date de rédaction** : 2026-07-19
> **Source de vérité** : `audit - tests - analyse et ameliorations/04-tickets-ameliorations.md`
> **Référence lot** : `audit - tests - analyse et ameliorations/tickets/13-lot-13-frontend.md`
> **Dossier done** : `audit - tests - analyse et ameliorations/tickets/done/`
>
> **Convention** : les tickets déplacés dans `tickets/done/` sont marqués `✅ FAIT`. Les autres sont à planifier.

---

## Table des matières

1. [État de l'art du frontend (juillet 2026)](#1-état-de-lart-du-frontend-juillet-2026)
2. [Tickets déjà livrés (`tickets/done/`)](#2-tickets-déjà-livrés-ticketsdone)
3. [Périmètre restant à implémenter](#3-périmètre-restant-à-implémenter)
4. [Vue d'ensemble — 5 phases](#4-vue-densemble--5-phases)
5. [Phase 1 — Fondations transverses (S1)](#5-phase-1--fondations-transverses-s1)
6. [Phase 2 — Recherche & UX (S2)](#6-phase-2--recherche--ux-s2)
7. [Phase 3 — Internationalisation & PWA (S6)](#7-phase-3--internationalisation--pwa-s6)
8. [Phase 4 — Plateforme V1 — Nouveaux écrans métier](#8-phase-4--plateforme-v1--nouveaux-écrans-métier)
9. [Phase 5 — Plateforme V2 — Analytics avancés & extensibilité](#9-phase-5--plateforme-v2--analytics-avancés--extensibilité)
10. [Critères d'acceptation transverses](#10-critères-dacceptation-transverses)
11. [Risques & hypothèses](#11-risques--hypothèses)
12. [Annexe — Matrice de traçabilité tickets → phases](#12-annexe--matrice-de-traçabilité-tickets--phases)

---

## 1. État de l'art du frontend (juillet 2026)

### 1.1 Stack technique confirmée

| Couche            | Technologie | Version | Statut |
|-------------------|---|---|---|
| Framework         | React | 19.2.7 | ✅ en place |
| Bundler           | Vite | 8.1.1 | ✅ en place |
| Routing           | react-router-dom | 7.18 | ✅ en place |
| State             | Zustand | 5.0 | ✅ `useUIStore` + `useAuthStore` (mais vide) |
| HTTP              | axios (client custom avec intercepteur) | 1.18 | ✅ en place |
| UI                | Tailwind CSS | 4.3 | ✅ en place |
| Charts            | Recharts     | 3.9 | ✅ utilisé (Dashboard, pie/bar) |
| Icons             | lucide-react | 1.23 | ✅ utilisé partout |
| Toasts            | sonner       | (non listé dans `package.json`) | ⚠️ **utilisé mais non installé** |
| Tests unitaires   | — | — | ❌ absent |
| Tests E2E         | — | — | ❌ absent |
| i18n              | — | — | ❌ absent |
| Auth (interceptor)| — | — | ❌ `useAuthStore` n'est pas branché à axios |
| PWA               | — | — | ❌ manifest absent |
| a11y              | — | — | ⚠️ aucune `aria-label`, aucun focus-ring |

### 1.2 Routes actuelles (`App.jsx`)

```
/                 → LandingPage (statique)
/dashboard        → Dashboard       (KPIs + 2 charts)
/search           → SearchFTS       (recherche + AdvancedFilters + export CSV)
/document/:numero → DocumentDetail  (Résumé + OCR tab)
/explorer         → Explorer        (liste fichiers)
/upload           → Upload          (drag & drop + 3 étapes de progression)
/ml               → PredictorML     (SVM, anomalies)
/monitoring       → Monitoring      (API/DB status + logs statiques)
/pipeline         → PipelineAdmin   (scrape/extract/ingest via WebSocket)
*                 → Placeholder     (page introuvable, sans 404 dédié)
```

**Routes manquantes** (UI-11, UI-12, UI-13, UI-14, E-18, E-11..24) — **15 écrans** à créer.

### 1.3 Couverture fonctionnelle actuelle

| Capacité | Implémentée | Manquante |
|---|---|---|
| Recherche plein texte | ✅ `SearchFTS` + `AdvancedFilters` | Tri configurable (UI-06), surlignage (UI-08) |
| Export CSV | ✅ `handleExportCSV` | Export Excel (UI-07 partiel — uniquement CSV) |
| Filtre par état | ✅ dropdown `statutAvis` | — |
| Skeleton de chargement | ✅ `Skeleton.jsx` | — |
| Reset recherche | ✅ `handleReset` | — |
| Auth UI | ❌ store vide, pas de page Login | UI-11, UI-12, UI-13 |
| 404/403/500 | ❌ Placeholder générique | UI-30 |
| Mode sombre | ❌ store flag mais pas appliqué | UI-27 |
| Raccourcis clavier | ❌ | UI-28 |
| Lazy loading routes | ❌ imports statiques | UI-29 |
| i18n | ❌ | UI-10, F-04 |
| PWA | ❌ | UI-26, E-23 |
| a11y | ❌ | UI-36, F-05 |
| Tests | ❌ | UI-34, UI-35 |
| `data-testid` | ❌ aucune convention | UI-31 |
| Bundle visualizer | ❌ | UI-32 |
| Storybook | ❌ | UI-33 |
| **15 écrans métier** | ❌ | E-10..24 |

---

## 2. Tickets déjà livrés (`tickets/done/`)

| ID | Titre | Composant impacté | Constat |
|---|---|---|---|
| ✅ UI-01 | Zustand stores globaux | `store/useUIStore.js`, `useAuthStore.js` | OK mais `useAuthStore` n'est pas branché à l'intercepteur axios |
| ✅ UI-02 | Intercepteur Axios + Toasts Sonner | `api/axios.js`, `App.jsx` | OK, `sonner` doit être ajouté à `package.json` |
| ✅ UI-03 | Skeleton de chargement | `components/Skeleton.jsx` | OK, utilisé dans `Dashboard` |
| ✅ UI-04 | Bouton « Réinitialiser » la recherche | `SearchFTS.jsx` | OK (`handleReset`) |
| ✅ UI-05 | Filtres avancés (6 champs) | `AdvancedFilters.jsx` | OK |
| ✅ UI-07 | Export CSV | `SearchFTS.jsx` | OK — **mais uniquement CSV** ; export Excel à ajouter si UI-07 reste dans le backlog |
| ✅ UI-09 | Filtre par état (4 statuts) | `AdvancedFilters.jsx` | OK |

**Statut** : **7/40 tickets Frontend terminés.** Le plan ci-dessous traite les **33 restants + 15 écrans**.

---

## 3. Périmètre restant à implémenter

| Catégorie | Nb tickets | Effort cumulé | Sprint cible |
|---|---|---|---|
| UI-06, UI-08 (recherche) | 2 | S + S | S2 |
| UI-10 (i18n) | 1 | M | S6 |
| UI-11, UI-12, UI-13, UI-14 (auth + admin) | 4 | 4 × M | S1 |
| UI-15..25 (15 nouveaux écrans) | 11 | 5×L + 6×M | V1 + V2 |
| UI-26 (PWA) | 1 | M | S6 |
| UI-27, UI-28, UI-29 (qualité vie) | 3 | 3 × S | S2 |
| UI-30 (404/403/500) | 1 | S | S1 |
| UI-31 (`data-testid`) | 1 | S | S1 |
| UI-32, UI-33 (Storybook + Bundle visualizer) | 2 | S + M | S2 |
| UI-34, UI-35 (Tests) | 2 | M + L | S1-S6 (transverse) |
| UI-36 (a11y) | 1 | M | S2 |
| UI-37, UI-38, UI-39, UI-40 (V1/V2) | 4 | 3×M + 1×M | V1 + V2 |
| E-10 (Auth + Users — front) | 1 | L | S1 |
| E-11, E-12, E-13, E-15, E-17, E-20, E-22 (V1) | 7 | 5×L + 2×M | V1 |
| E-14 (Dashboard Acheteur) | 1 | L | V1 |
| E-16, E-19, E-24 (V2 — drag & drop, labellisation, data lineage) | 3 | 2×XL + L | V2 |
| E-18 (Audit & Traçabilité) | 1 | M | S1 |
| E-21 (Notifications WebSocket) | 1 | M | V2 |
| E-23 (PWA mobile-first) | 1 | M | S6 |
| **Total** | **~48** | **≈ 130 pts** | **S1 → V2** |

---

## 4. Vue d'ensemble — 5 phases

```
Phase 1 (S1)   — Fondations transverses        ⏱ 2 semaines    🔴 P0
Phase 2 (S2)   — Recherche & UX                ⏱ 2 semaines    🟠 P1
Phase 3 (S6)   — i18n FR/AR + PWA mobile      ⏱ 2 semaines    🟠 P1
Phase 4 (V1)   — Plateforme (15 écrans métier) ⏱ 24 semaines   🟡 P2
Phase 5 (V2)   — Analytics avancés & extensibilité ⏱ 36 semaines 🟡 P2
```

**Logique de séquencement** :

```
S1 ─ fondations ─► S2 ─ complétion ─► S6 ─ portage ─► V1 ─ extension ─► V2
 │                  │                  │                │                 │
 UI-11..14,30,31    UI-06,08,27..29   UI-10,26        E-11..15,17,20,22  E-16,19,21,24
 UI-34 (bootstrap)  UI-32,33,36,34    E-23            UI-15..25,40      UI-20,22,38
 E-10, E-18                                                       F-06,07,10
```

**Dépendances bloquantes identifiées** :

| Ticket | Bloqué par | Action |
|---|---|---|
| UI-11 (Login) | AU-01 (backend), BDD-10 (table user) | Commencer par le **mock d'API** (login factice accepté) pour paralléliser |
| UI-12 (Profile), UI-13 (Users) | UI-11 | Enchaîner immédiatement |
| E-11 (Alertes) | ING-09 (webhooks), BDD-13 (subscriptions) | Stub en S6, brancher en V1 |
| E-12 (Cartographie) | B-30 (endpoint geo), BDD-05 (lat/lon) | Stub en V1 |
| E-13 (Comparateur) | B-31 (endpoint comparaison), ML-04 | Stub en V1 |
| E-16 (Drag & drop) | D-09..20 (data warehouse) | Pure V2 |
| E-19 (Labellisation) | ML-13, BDD-12 | Pure V2 |
| E-21 (WebSocket notifications) | OPS-08, B-32 | Pure V2 |
| E-22 (Rapports programmés) | DOC-09 | V1 |

---

## 5. Phase 1 — Fondations transverses (S1) 🔴

> **Objectif** : transformer l'app en plateforme authentifiée, testée, accessible aux lecteurs, et instrumentée.
> **Effort** : ≈ 35 pts · **Durée** : 2 semaines · **Équipe** : 1 dev senior + 1 dev junior

### 5.1 Livrables

| # | Ticket | Description | Effort | Fichiers |
|---|---|---|---|---|
| 1.1 | UI-11 🔴 | Page Login (formulaire email + password + validation, gestion des erreurs, redirection). | M | `pages/Login.jsx` (nouveau) |
| 1.2 | UI-12 🟠 | Page Profil utilisateur (informations, changement mot de passe, préférence langue/thème). | M | `pages/Profile.jsx` (nouveau) |
| 1.3 | UI-13 🟠 | Page Gestion des utilisateurs (admin) — table paginée, recherche, activation/désactivation. | M | `pages/Users.jsx` (nouveau) |
| 1.4 | UI-14 🟡 | Page Audit & Traçabilité (timeline des actions utilisateurs, filtres par type/IP). | M | `pages/Audit.jsx` (nouveau) |
| 1.5 | UI-30 🟠 | Pages 404 / 403 / 500 (designs + intégration au `Router`). | S | `pages/errors/{NotFound,Forbidden,ServerError}.jsx` (nouveau) |
| 1.6 | UI-31 🟠 | Convention `data-testid` sur tous les composants existants (Sidebar, Topbar, Dashboard, SearchFTS, Explorer, etc.). | S | Tous les `.jsx` (refactor) |
| 1.7 | UI-34 🟠 | Bootstrap Vitest + React Testing Library + 1er test (`Skeleton.test.jsx` + `Sidebar.test.jsx` en S1). | M | `vitest.config.js` (nouveau), `__tests__/` |
| 1.8 | E-10 🔴 | Authentification & Gestion des utilisateurs — wiring frontend (intercepteur Axios ↔ `useAuthStore`, route guards `<ProtectedRoute>`, redirection après login). | L | `api/axios.js`, `store/useAuthStore.js`, `App.jsx`, `components/ProtectedRoute.jsx` |
| 1.9 | E-18 🟠 | Écran Audit & Traçabilité = UI-14 (interface de consultation du log immuable AU-10). | M | inclus dans UI-14 |
| 1.10 | F-05 🟠 | Audit accessibilité de base : ajout `aria-label` aux boutons icon-only, `role` sur les listes, `alt` sur les images, focus visible. | M | transverse |

### 5.2 Dépendances techniques à installer

```bash
npm install --save sonner react-hook-form zod dompurify
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom \
  @testing-library/user-event jsdom @vitest/ui
```

⚠️ `sonner` est déjà utilisé — il faut l'**ajouter formellement à `package.json`**.

### 5.3 Tâches transverses

1. Créer `ProtectedRoute` qui :
   - Lit `isAuthenticated` depuis `useAuthStore`.
   - Redirige vers `/login` si non authentifié.
   - Vérifie le rôle pour les routes admin (`/users`).
2. Brancher `apiClient.interceptors.request` pour injecter le JWT (header `Authorization`).
3. Ajouter une **route publique** : `/login`, `/forgot-password`. Toutes les autres deviennent protégées.
4. Configurer la `baseURL` via `VITE_API_BASE_URL` (déjà prévu mais non documenté → créer `.env.example`).
5. Mettre en place un **mock auth** (MSW ou simple faux endpoint) pour pouvoir développer UI-11/12/13 sans attendre AU-01.

### 5.4 Critères d'acceptation Phase 1

- [ ] Un utilisateur peut se connecter via `/login` (mock accepté), un JWT factice est stocké dans le store + cookie httpOnly simulé.
- [ ] Toutes les routes sont protégées par `<ProtectedRoute>` (sauf `/login`).
- [ ] Les 3 pages d'erreur (404/403/500) sont accessibles et designées.
- [ ] Chaque composant interactif porte un `data-testid` au format `kebab-case` (cf. convention dans `cypress.config.js` à venir).
- [ ] `npm run test` lance Vitest ; ≥ 5 tests unitaires passent.
- [ ] L'application passe Lighthouse Accessibility ≥ 80.
- [ ] Tous les boutons icon-only ont un `aria-label`.

### 5.5 Ticket de sortie

> `Phase 1 livrée` — auth + RBAC + 4 nouveaux écrans + tests bootstrappés + a11y minimale.

---

## 6. Phase 2 — Recherche & UX (S2) 🟠

> **Objectif** : finaliser l'expérience de recherche et l'UX globale (tri, surlignage, raccourcis, lazy loading, mode sombre, outils dev).
> **Effort** : ≈ 20 pts · **Durée** : 2 semaines · **Équipe** : 1 dev senior

### 6.1 Livrables

| # | Ticket | Description | Effort | Fichiers |
|---|---|---|---|---|
| 2.1 | UI-06 🟠 | Tri configurable (date / montant / pertinence, asc/desc) — dropdown dans l'en-tête de `SearchFTS`, envoi en querystring `sort_by` et `order_dir`. | S | `SearchFTS.jsx` |
| 2.2 | UI-08 🟠 | Surlignage des termes trouvés dans le snippet (`<mark>` avec sanitize DOMPurify). | S | `SearchFTS.jsx` (+ `useAuthStore` non requis) |
| 2.3 | UI-27 🟠 | Mode sombre/clair toggle (Tailwind `dark:` + classe `dark` sur `<html>`, persistance `localStorage`). | S | `useUIStore.js`, `App.jsx`, tous les `.jsx` (refactor classes) |
| 2.4 | UI-28 🟠 | Raccourcis clavier (`/` focus recherche, `Esc` ferme les filtres, `g d` dashboard, `g s` search). | S | `hooks/useKeyboardShortcuts.js` (nouveau), `App.jsx` |
| 2.5 | UI-29 🟠 | Lazy loading des routes via `React.lazy` + `<Suspense fallback={<Skeleton/> >`. | S | `App.jsx` |
| 2.6 | UI-32 🟡 | Bundle visualizer (`rollup-plugin-visualizer` ou `vite-bundle-visualizer`). | S | `vite.config.js` |
| 2.7 | UI-33 🟡 | Storybook 8 (`@storybook/react-vite`) — 1 story par composant, controls + actions. | M | `.storybook/` (nouveau) |
| 2.8 | UI-36 🟠 | Accessibilité (focus visible custom, `aria-live` sur les toasts, contraste WCAG AA vérifié, navigation tab cohérente). | M | transverse |
| 2.9 | UI-34 (suite) | Tests Vitest : compléter la couverture des composants critiques (`SearchFTS`, `AdvancedFilters`, `Sidebar`, `Dashboard`, `DocumentDetail`, `Skeleton`, `Login`). Cible : ≥ 30 tests, ≥ 60 % de couverture sur les composants. | M | `__tests__/` |
| 2.10 | UI-07 (complément) | Ajouter export **Excel** (xlsx via `xlsx` ou `exceljs`) en plus du CSV. | S | `SearchFTS.jsx` |

### 6.2 Dépendances à installer

```bash
npm install --save dompurify xlsx
npm install --save-dev rollup-plugin-visualizer @storybook/react-vite storybook @vitest/coverage-v8
```

### 6.3 Détails d'implémentation

#### UI-06 — Tri configurable

```jsx
// SearchFTS.jsx
const SORT_OPTIONS = [
  { value: 'relevance', label: 'Pertinence' },
  { value: 'date_publication', label: 'Date de publication' },
  { value: 'montant', label: 'Montant' },
];
// State : sortBy, orderDir
// QueryString : sort_by, order_dir
```

#### UI-08 — Surlignage

```jsx
import DOMPurify from 'dompurify';
<span dangerouslySetInnerHTML={{
  __html: DOMPurify.sanitize(snippet.replace(
    new RegExp(`(${query})`, 'gi'),
    '<mark class="bg-yellow-200 px-0.5">$1</mark>'
  ))
}} />
```

#### UI-29 — Lazy loading

```jsx
const Dashboard = lazy(() => import('./components/Dashboard'));
const SearchFTS = lazy(() => import('./components/SearchFTS'));
// ...
<Suspense fallback={<Skeleton className="h-32" />}>
  <Routes>...</Routes>
</Suspense>
```

### 6.4 Critères d'acceptation Phase 2

- [ ] L'utilisateur peut trier les résultats par 3 critères dans 2 ordres (6 combinaisons).
- [ ] Les termes de la requête sont surlignés en jaune dans le snippet (validé par un test unitaire sur la fonction `highlight()`).
- [ ] Toggle dark/light fonctionne et persiste après refresh.
- [ ] `/` depuis n'importe quelle page met le focus sur l'input de recherche ; `Esc` ferme le panneau de filtres.
- [ ] Chaque route est un chunk séparé (vérifié dans `npm run build` → analyzer).
- [ ] Lighthouse Accessibility ≥ 90.
- [ ] Storybook lance 15+ stories.

### 6.5 Ticket de sortie

> `Phase 2 livrée` — recherche complète + UX moderne + outils dev (Storybook, bundle viz) + a11y ≥ 90.

---

## 7. Phase 3 — Internationalisation & PWA (S6) 🟠

> **Objectif** : rendre l'application bilingue FR/AR avec support RTL, installable en PWA, et mobile-responsive.
> **Effort** : ≈ 18 pts · **Durée** : 2 semaines · **Équipe** : 1 dev senior + 1 dev junior

### 7.1 Livrables

| # | Ticket | Description | Effort | Fichiers |
|---|---|---|---|---|
| 3.1 | UI-10 (F-04) 🟠 | i18next FR/AR — extraction de toutes les chaînes, configuration RTL, dates Hijri/Grégorien, format nombres en chiffres arabes. | M-L | `i18n/{fr,ar}.json`, `i18n.js` (nouveau), tous les `.jsx` |
| 3.2 | UI-26 🟡 | PWA installable (`vite-plugin-pwa`) — manifest, service worker, icônes, mode offline basique. | M | `vite.config.js`, `public/manifest.json`, `public/icons/` |
| 3.3 | E-23 🟡 | Mobile-first & PWA — refactor du layout (Sidebar collapsible en drawer, tableaux scrollables horizontalement, formulaires adaptés tactile). | M | `Sidebar.jsx`, `Topbar.jsx`, tous les écrans |
| 3.4 | UI-34 (suite) | Tests Vitest : ajouter tests i18n (changement de langue, RTL), tests PWA (mock `serviceWorker`). | M | `__tests__/` |
| 3.5 | UI-35 (bootstrap) | Cypress installé + 5 premiers scénarios E2E (login, search, filters, dashboard, document detail). | M | `cypress.config.js`, `cypress/e2e/` |

### 7.2 Dépendances à installer

```bash
npm install --save i18next react-i18next i18next-browser-languagedetector
npm install --save-dev vite-plugin-pwa workbox-window
npm install --save-dev cypress @testing-library/cypress
```

### 7.3 Détails d'implémentation

#### UI-10 — i18n

```
src/i18n/
  ├── fr.json          (≈ 250 clés)
  ├── ar.json          (≈ 250 clés)
  └── config.js        (i18next.init, fallbackLng='fr', lng détecté depuis localStorage)
```

Exemple d'extraction :
```jsx
// Avant
<h2>Recherche Sémantique</h2>

// Après
import { useTranslation } from 'react-i18next';
const { t } = useTranslation();
<h2>{t('search.title')}</h2>
```

RTL handling :
```jsx
// useUIStore : { isRTL, setRTL }
// App.jsx
useEffect(() => {
  document.documentElement.dir = i18n.language === 'ar' ? 'rtl' : 'ltr';
  document.documentElement.lang = i18n.language;
}, [i18n.language]);
```

#### UI-26 — PWA

```js
// vite.config.js
import { VitePWA } from 'vite-plugin-pwa';

plugins: [
  react(),
  VitePWA({
    registerType: 'autoUpdate',
    manifest: {
      name: 'GED Intelligente',
      short_name: 'GED',
      description: 'Plateforme de gestion électronique des documents',
      theme_color: '#10b981',
      icons: [
        { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png' },
        { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png' }
      ]
    }
  })
]
```

#### E-23 — Mobile-first

- Sidebar → drawer (icône hamburger en Topbar)
- Tableaux → `overflow-x-auto` + sticky first column
- Formulaires → inputs en pleine largeur, `type="tel"` pour téléphone marocain
- Grids → `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`

### 7.4 Critères d'acceptation Phase 3

- [ ] L'utilisateur peut switcher FR ↔ AR depuis un dropdown dans la Topbar.
- [ ] L'application passe en RTL automatique en AR (tous les composants).
- [ ] Les dates sont au format Hijri en AR, Grégorien en FR.
- [ ] L'application est installable (Chrome affiche la bannière « Installer GED Intelligente »).
- [ ] En mode avion, la LandingPage reste accessible.
- [ ] Sur iPhone 12 (375×812), toutes les pages sont utilisables sans scroll horizontal.
- [ ] `npm run cypress:open` lance 5 scénarios E2E passants.

### 7.5 Ticket de sortie

> `Phase 3 livrée` — bilingue FR/AR + PWA installable + mobile-first + 5 E2E tests.

---

## 8. Phase 4 — Plateforme V1 — Nouveaux écrans métier

> **Objectif** : livrer les 7 écrans V1 (E-11, E-12, E-13, E-14, E-15, E-17, E-20, E-22) qui transforment le PFA en plateforme décisionnelle.
> **Effort** : ≈ 60 pts · **Durée** : 24 semaines · **Équipe** : 2 devs seniors + 1 data scientist
> **Stratégie** : livraison **écran par écran** avec backend stub (MSW) en attendant les vrais endpoints.

### 8.1 Roadmap V1 (24 semaines, 6 jalons de 4 semaines)

| Jalon | Semaines | Écrans livrés | Backend requis |
|---|---|---|---|
| **V1.1** | S1-S4 | E-20 (Catalogue ML), E-22 (Rapports programmés) | ML-07, DOC-09 |
| **V1.2** | S5-S8 | E-12 (Cartographie Leaflet) | B-30, BDD-05 |
| **V1.3** | S9-S12 | E-11 (Centre d'alertes & watchlist) | BDD-13, ING-09 |
| **V1.4** | S13-S16 | E-13 (Comparateur d'AO) | B-31, ML-04 |
| **V1.5** | S17-S20 | E-14 (Dashboard Acheteur) + E-15 (Dashboard Fournisseur) | BDD-02, E-11, ML-06 |
| **V1.6** | S21-S24 | E-17 (Prédictif & Prévisions Prophet) | ML-18 |

### 8.2 Spécifications par écran

#### E-11 — Centre d'alertes & watchlist personnalisée 🟡 L

| Aspect | Détail |
|---|---|
| Route | `/alerts` |
| Fonctionnalités | (1) Liste des alertes (cards avec sévérité), (2) création d'une watchlist (mots-clés + critères), (3) historique des alertes déclenchées, (4) marquer comme lu/non lu, (5) abonnement email/push. |
| Composants | `pages/Alerts.jsx`, `components/AlertCard.jsx`, `components/WatchlistForm.jsx`, `hooks/useWebSocket.js` (pour alertes temps réel). |
| Scénarios | ST-E11-001..006 |
| Dépendance backend | `GET /api/v1/alerts`, `POST /api/v1/watchlists`, `WS /ws/alerts` |

#### E-12 — Cartographie des AO (Leaflet) 🟡 L

| Aspect | Détail |
|---|---|
| Route | `/map` |
| Fonctionnalités | (1) Carte Maroc centrée (lat 31.79, lng -7.09, zoom 6), (2) markers par AO (cluster si > 100), (3) popup avec résumé, (4) filtre latéral (région, catégorie, montant), (5) heatmap toggleable. |
| Composants | `pages/Map.jsx`, `components/MapFilters.jsx`, `components/AOPopup.jsx`. |
| Bibliothèque | `react-leaflet@4` + `leaflet.markercluster` + `leaflet.heat` |
| Dépendance backend | `GET /api/v1/ao/geo?bbox=...` |

#### E-13 — Comparateur d'appels d'offres 🟡 L

| Aspect | Détail |
|---|---|
| Route | `/compare?ids=A1,A2,A3` |
| Fonctionnalités | (1) Sélection de 2-5 AO (checkboxes dans la recherche), (2) tableau comparatif (montant, délai, caution, qualifications, organisme, ville), (3) radar chart (Recharts) sur les dimensions normalisées, (4) score de similarité (cosinus sur embeddings F-01). |
| Composants | `pages/Compare.jsx`, `components/CompareTable.jsx`, `components/CompareRadar.jsx`. |
| Dépendance backend | `POST /api/v1/ao/compare` (B-31), `GET /api/v1/embeddings/similarity` (F-01) |

#### E-14 — Tableau de bord Acheteur 🟡 L

| Aspect | Détail |
|---|---|
| Route | `/dashboard/buyer` |
| Fonctionnalités | (1) KPIs (nb AO publiés, nb soumissions reçues, taux d'attribution, économies réalisées), (2) graphique évolution mensuelle, (3) répartition par direction, (4) top 10 fournisseurs, (5) délais moyens par procédure. |
| Composants | `pages/BuyerDashboard.jsx`, `components/BuyerKPIs.jsx`, `components/BuyerCharts.jsx`. |
| Dépendance backend | `GET /api/v1/analytics/buyer` |

#### E-15 — Tableau de bord Fournisseur 🟡 L

| Aspect | Détail |
|---|---|
| Route | `/dashboard/supplier` |
| Fonctionnalités | (1) AO matchant mon profil (watchlist), (2) win/loss ratio, (3) montants cumulés, (4) timeline des AO à venir (alertes E-11 intégrées), (5) recommandations ML (ML-06). |
| Composants | `pages/SupplierDashboard.jsx`, `components/SupplierMatches.jsx`, `components/SupplierTimeline.jsx`. |
| Dépendance backend | `GET /api/v1/analytics/supplier`, `GET /api/v1/recommendations` (ML-06) |

#### E-17 — Prédictif & Prévisions (Prophet) 🟡 L

| Aspect | Détail |
|---|---|
| Route | `/predictive` |
| Fonctionnalités | (1) Sélecteur de variable cible (nb AO, montant cumulé, durée moyenne), (2) horizon de prévision (1, 3, 6, 12 mois), (3) graphique avec intervalle de confiance, (4) téléchargement CSV des prévisions, (5) métriques du modèle (MAPE, RMSE). |
| Composants | `pages/Predictive.jsx`, `components/ForecastChart.jsx`, `components/ModelMetrics.jsx`. |
| Dépendance backend | `GET /api/v1/predict/timeseries` (ML-18) |

#### E-20 — Catalogue des modèles ML 🟡 M

| Aspect | Détail |
|---|---|
| Route | `/ml/catalog` |
| Fonctionnalités | (1) Liste des modèles (SVM, Isolation Forest, Prophet, etc.), (2) pour chaque : description, métriques, date d'entraînement, bouton « réentraîner », (3) versionning (modèle v1.2 vs v1.1), (4) logs d'entraînement. |
| Composants | `pages/MLCatalog.jsx`, `components/ModelCard.jsx`, `components/ModelVersioning.jsx`. |
| Dépendance backend | `GET /api/v1/ml/models`, `POST /api/v1/ml/models/{id}/retrain` (ML-07) |

#### E-22 — Rapports programmés (PDF/Excel) 🟡 M

| Aspect | Détail |
|---|---|
| Route | `/reports` |
| Fonctionnalités | (1) Liste des rapports générés, (2) bouton « Créer un rapport » (sélecteur de template + fréquence + email), (3) prévisualisation HTML avant export, (4) téléchargement direct PDF/Excel, (5) planification (cron visuel). |
| Composants | `pages/Reports.jsx`, `components/ReportBuilder.jsx`, `components/ReportPreview.jsx`. |
| Dépendance backend | `GET /api/v1/reports`, `POST /api/v1/reports` (DOC-09) |

### 8.3 Sous-tickets UI-15..25, UI-37, UI-40

Ces sous-tickets correspondent à l'**implémentation frontend** des écrans E-11..24 :

| Ticket | Écran | Mapping |
|---|---|---|
| UI-15 | Page Centre d'alertes | E-11 |
| UI-16 | Page Cartographie | E-12 |
| UI-17 | Page Comparateur | E-13 |
| UI-18 | Page Dashboard Acheteur | E-14 |
| UI-19 | Page Dashboard Fournisseur | E-15 |
| UI-20 | Page Analytics Avancés (V2) | E-16 |
| UI-21 | Page Prédictif | E-17 |
| UI-22 | Page Labellisation (V2) | E-19 |
| UI-23 | Page Catalogue ML | E-20 |
| UI-24 | Page Notifications (V2) | E-21 |
| UI-25 | Page Rapports programmés | E-22 |
| UI-40 | Heatmap calendrier des publications | standalone |

### 8.4 Stratégie de développement parallèle

```
Frontend (V1)                         Backend
─────────────                         ───────
1. Stub MSW pour endpoints      ◄────►  Endpoints réels arrivent en V1.1-V1.6
2. Composants UI standalone           (BDD-02, B-30, B-31, ML-04, ML-18)
3. Connecteur final ◄─────────────────  Endpoint stable
```

### 8.5 Critères d'acceptation Phase 4

- [ ] Les 8 écrans V1 sont accessibles depuis le menu latéral.
- [ ] Chaque écran a un `data-testid` racine et 3+ tests Vitest.
- [ ] Lighthouse ≥ 85 sur chaque écran.
- [ ] 2+ scénarios Cypress E2E par écran.
- [ ] Au moins 1 capture Storybook par écran.
- [ ] Le support FR/AR fonctionne sur tous les écrans.

### 8.6 Ticket de sortie

> `Phase 4 livrée` — la plateforme couvre le cycle complet : ingestion → analyse → alerting → comparaison → prédiction.

---

## 9. Phase 5 — Plateforme V2 — Analytics avancés & extensibilité

> **Objectif** : ajouter les capacités « premium » : drag & drop BI, labellisation collaborative, data lineage, notifications temps réel, multi-tenant, signature électronique.
> **Effort** : ≈ 50 pts · **Durée** : 36 semaines · **Équipe** : 3 devs seniors + 1 data engineer + 1 UX

### 9.1 Roadmap V2 (3 jalons de 12 semaines)

| Jalon | Semaines | Écrans | Tickets |
|---|---|---|---|
| **V2.1** | S1-S12 | E-16 (Analytics Avancés drag & drop), E-21 (Notifications WebSocket) | UI-20, UI-24, UI-38 |
| **V2.2** | S13-S24 | E-19 (Labellisation collaborative), E-24 (Data Lineage) | UI-22, F-06, F-07, F-10 |
| **V2.3** | S25-S36 | API publique Open Data, signature électronique PAdES, multi-tenant UI | F-06, F-07, F-10 |

### 9.2 Spécifications des écrans V2

#### E-16 — Analytics Avancés (DataViz, drag & drop) 🟡 XL

| Aspect | Détail |
|---|---|
| Route | `/analytics` |
| Fonctionnalités | (1) Bibliothèque de widgets (KPI, bar, line, pie, heatmap, table) en sidebar, (2) zone canvas drag & drop, (3) configuration par widget (data source, dimensions, mesures, filtres), (4) sauvegarde de dashboards, (5) partage public, (6) export PNG/PDF. |
| Bibliothèque | `react-grid-layout` (drag & drop grid) + Recharts/Plotly (charts). |
| Effort | XL (> 2 semaines dev) |
| Tickets liés | UI-20, UI-38 |

#### E-19 — Labellisation collaborative 🟡 XL

| Aspect | Détail |
|---|---|
| Route | `/labeling` |
| Fonctionnalités | (1) File d'attente de documents à labelliser, (2) annotation par entity (catégorie, qualification, montant, dates), (3) consensus multi-annotateurs, (4) gold standard vs brouillon, (5) statistiques (Cohen's kappa inter-annotateurs), (6) export vers le dataset d'entraînement. |
| Effort | XL |
| Tickets liés | UI-22, ML-13, BDD-12 |

#### E-21 — Notifications & Messagerie (WebSocket) 🟡 M

| Aspect | Détail |
|---|---|
| Route | `/notifications` |
| Fonctionnalités | (1) Centre de notifications (cloche Topbar), (2) WebSocket `ws://.../ws/notifications`, (3) groupement par type, (4) actions rapides (lien direct vers l'AO), (5) mute/unmute, (6) sons différents par sévérité. |
| Effort | M |
| Tickets liés | UI-24, OPS-08, B-32 |

#### E-24 — Data Lineage & Quality 🟡 L

| Aspect | Détail |
|---|---|
| Route | `/lineage` |
| Fonctionnalités | (1) Graphe orienté source → transformations → tables → dashboards, (2) DAG interactif (zoom, pan, tooltips), (3) data quality par nœud (complétude, fraîcheur, exactitude), (4) alertes sur les nœuds défaillants. |
| Bibliothèque | `react-flow` (DAG) |
| Effort | L |
| Tickets liés | D-12, ML-08 |

### 9.3 Sous-tickets UI-37, UI-38, UI-39

| Ticket | Description | Effort | Phase |
|---|---|---|---|
| UI-37 | Notifications navigateur (Web Notifications API) | S | V2.1 (inclus dans E-21) |
| UI-38 | Drag & drop widgets (composant d'E-16) | M | V2.1 |
| UI-39 | WebSocket Monitoring (logs temps réel dans `Monitoring.jsx`) | M | V1 (déjà partiellement fait dans `PipelineAdmin` mais pas dans `Monitoring`) |
| UI-40 | Heatmap calendrier des publications (composant additionnel du Dashboard) | M | V1 (peut être livré en V1.6) |

⚠️ **UI-39 est déjà partiellement implémenté** : `PipelineAdmin.jsx` a un WebSocket console temps réel. Le ticket consiste à **uniformiser** dans `Monitoring.jsx` et à créer un vrai système de logs structurés.

### 9.4 Critères d'acceptation Phase 5

- [ ] L'utilisateur peut construire un dashboard custom en 5 minutes sans formation.
- [ ] 2 annotateurs peuvent labelliser le même document et voir le score de Cohen's kappa.
- [ ] Le graphe de lineage affiche tous les flux majeurs.
- [ ] Les notifications push arrivent en < 1 seconde après l'événement.

### 9.5 Ticket de sortie

> `Phase 5 livrée` — plateforme « enterprise-ready ».

---

## 10. Critères d'acceptation transverses

### 10.1 Qualité de code

- [ ] `npm run lint` (oxlint) passe sans warning.
- [ ] `npm run test` ≥ 80 % de couverture (couverture globale du frontend).
- [ ] `npm run cypress:run` ≥ 20 scénarios E2E verts.
- [ ] `npm run build` produit un bundle initial < 300 KB gzip.
- [ ] Lighthouse Performance ≥ 85, Accessibility ≥ 90, Best Practices ≥ 90, SEO ≥ 80.

### 10.2 UX / Accessibilité

- [ ] Navigation 100 % au clavier.
- [ ] Tous les écrans sont testés avec NVDA / VoiceOver.
- [ ] Contraste WCAG 2.1 AA partout.
- [ ] Focus visible sur tous les éléments interactifs.
- [ ] Aucune erreur `aria-*` dans la console.

### 10.3 i18n

- [ ] 0 chaîne en dur dans le code (vérifié par script `i18n-checker.js`).
- [ ] Layout RTL automatique en AR.
- [ ] Toutes les dates en format local.
- [ ] Nombres en chiffres arabes en AR.

### 10.4 PWA

- [ ] Score PWA Lighthouse ≥ 90.
- [ ] L'app fonctionne offline sur la LandingPage.
- [ ] Installable (Chrome + Safari iOS).

### 10.5 Sécurité

- [ ] JWT en cookie httpOnly (pas de localStorage).
- [ ] CSRF token sur tous les POST.
- [ ] DOMPurify sur tout `dangerouslySetInnerHTML`.
- [ ] CSP stricte en production.
- [ ] `npm audit` = 0 vulnérabilité haute.

### 10.6 Performance

- [ ] Lazy loading des routes (chunks séparés).
- [ ] Skeleton sur chaque fetch > 200 ms.
- [ ] Debounce de la recherche (300 ms).
- [ ] Pagination côté serveur (pas de client-side sur 10 000+ items).
- [ ] Images au format WebP + lazy loading `<img loading="lazy" />`.

---

## 11. Risques & hypothèses

### 11.1 Risques identifiés

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| Délai de livraison des endpoints backend (BDD-02, B-30, B-31, ML-04, ML-18) | Élevée | Élevé | MSW pour mocker les API ; backend et frontend développés en parallèle avec contrats stricts (OpenAPI). |
| Surcharge cognitive de l'utilisateur avec 15+ nouveaux écrans | Moyenne | Moyen | Onboarding guidé (coachmarks), sidebar groupée par thème, recherche globale. |
| Performance des cartes Leaflet avec > 5 000 markers | Moyenne | Élevé | Marker clustering, viewport filtering, backend aggregation. |
| Complexité drag & drop dashboard (E-16) | Élevée | Élevé | Limiter le MVP à 5 widgets, tester sur Chrome/Firefox/Safari. |
| Régression visuelle entre V1 et V2 | Moyenne | Moyen | Tests de régression visuelle (Playwright snapshots, T-03). |
| RTL casse certains composants custom | Moyenne | Moyen | Tester chaque nouveau composant en AR dès l'ajout, pas en fin de sprint. |

### 11.2 Hypothèses de travail

- **H1** : l'API backend est en FastAPI + PostgreSQL avec authentification JWT (cf. AU-01..06).
- **H2** : le portail `appels-offres.equipement.gov.ma` reste accessible (sinon le scraper est bloqué).
- **H3** : un environnement de staging (`https://ged-staging.equipement.gov.ma`) est disponible pour la V1.
- **H4** : les modèles ML sont entraînés et exposés via des endpoints FastAPI (ML-07).
- **H5** : le compte-rendu de la phase 3 (lot 11/12) confirme que les extractions OCR/NLP sont fiables à > 90 %.

### 11.3 Hors périmètre

- Application mobile native (React Native) — une PWA suffit en V1/V2.
- SSO Keycloak (AU-14) — V1+.
- Signature électronique PAdES (F-10) — V2.

---

## 12. Annexe — Matrice de traçabilité tickets → phases

### 12.1 Tickets Frontend (UI-01..40)

| ID | Titre | Phase | Sprint | Statut |
|---|---|---|---|---|
| UI-01 | Zustand stores | Phase 1 | S1 | ✅ FAIT |
| UI-02 | Intercepteur Axios + Toasts | Phase 1 | S1 | ✅ FAIT |
| UI-03 | Skeleton | Phase 1 | S1 | ✅ FAIT |
| UI-04 | Bouton Reset | Phase 1 | S1 | ✅ FAIT |
| UI-05 | Filtres avancés | Phase 1 | S1 | ✅ FAIT |
| UI-06 | Tri configurable | **Phase 2** | S2 | ⏳ À FAIRE |
| UI-07 | Export CSV | Phase 1 | S1 | ✅ FAIT (+ Excel en Phase 2) |
| UI-08 | Surlignage | **Phase 2** | S2 | ⏳ À FAIRE |
| UI-09 | Filtre par état | Phase 1 | S1 | ✅ FAIT |
| UI-10 | i18next FR/AR | **Phase 3** | S6 | ⏳ À FAIRE |
| UI-11 | Page Login | **Phase 1** | S1 | ⏳ À FAIRE |
| UI-12 | Page Profil | **Phase 1** | S1 | ⏳ À FAIRE |
| UI-13 | Page Users (admin) | **Phase 1** | S1 | ⏳ À FAIRE |
| UI-14 | Page Audit | **Phase 1** | S1 | ⏳ À FAIRE |
| UI-15 | Page Alertes | **Phase 4** | V1.3 | ⏳ À FAIRE |
| UI-16 | Page Cartographie | **Phase 4** | V1.2 | ⏳ À FAIRE |
| UI-17 | Page Comparateur | **Phase 4** | V1.4 | ⏳ À FAIRE |
| UI-18 | Page Dashboard Acheteur | **Phase 4** | V1.5 | ⏳ À FAIRE |
| UI-19 | Page Dashboard Fournisseur | **Phase 4** | V1.5 | ⏳ À FAIRE |
| UI-20 | Page Analytics Avancés | **Phase 5** | V2.1 | ⏳ À FAIRE |
| UI-21 | Page Prédictif | **Phase 4** | V1.6 | ⏳ À FAIRE |
| UI-22 | Page Labellisation | **Phase 5** | V2.2 | ⏳ À FAIRE |
| UI-23 | Page Catalogue ML | **Phase 4** | V1.1 | ⏳ À FAIRE |
| UI-24 | Page Notifications | **Phase 5** | V2.1 | ⏳ À FAIRE |
| UI-25 | Page Rapports programmés | **Phase 4** | V1.1 | ⏳ À FAIRE |
| UI-26 | PWA installable | **Phase 3** | S6 | ⏳ À FAIRE |
| UI-27 | Dark/Light toggle | **Phase 2** | S2 | ⏳ À FAIRE |
| UI-28 | Raccourcis clavier | **Phase 2** | S2 | ⏳ À FAIRE |
| UI-29 | Lazy loading routes | **Phase 2** | S2 | ⏳ À FAIRE |
| UI-30 | 404/403/500 | **Phase 1** | S1 | ⏳ À FAIRE |
| UI-31 | `data-testid` partout | **Phase 1** | S1 | ⏳ À FAIRE |
| UI-32 | Bundle visualizer | **Phase 2** | S2 | ⏳ À FAIRE |
| UI-33 | Storybook | **Phase 2** | S2 | ⏳ À FAIRE |
| UI-34 | Vitest + RTL | **Phase 1+2+3** | S1-S6 | ⏳ À FAIRE (bootstrap S1) |
| UI-35 | Cypress ≥ 20 scénarios | **Phase 3+4** | S1-S6 | ⏳ À FAIRE (bootstrap S1) |
| UI-36 | Accessibilité | **Phase 2** | S2 | ⏳ À FAIRE |
| UI-37 | Notifications navigateur | **Phase 5** | V2.1 | ⏳ À FAIRE |
| UI-38 | Drag & drop widgets | **Phase 5** | V2.1 | ⏳ À FAIRE |
| UI-39 | WebSocket Monitoring | **Phase 4** | V1 (déjà partiel PipelineAdmin) | ⏳ À FAIRE (uniformiser) |
| UI-40 | Heatmap calendrier | **Phase 4** | V1.6 | ⏳ À FAIRE |

### 12.2 Écrans fonctionnels (E-10..24)

| ID | Écran | Phase | Sprint | Statut |
|---|---|---|---|---|
| E-10 | Auth + Users (front) | Phase 1 | S1 | ⏳ À FAIRE |
| E-11 | Centre d'alertes | Phase 4 | V1.3 | ⏳ À FAIRE |
| E-12 | Cartographie | Phase 4 | V1.2 | ⏳ À FAIRE |
| E-13 | Comparateur | Phase 4 | V1.4 | ⏳ À FAIRE |
| E-14 | Dashboard Acheteur | Phase 4 | V1.5 | ⏳ À FAIRE |
| E-15 | Dashboard Fournisseur | Phase 4 | V1.5 | ⏳ À FAIRE |
| E-16 | Analytics Avancés | Phase 5 | V2.1 | ⏳ À FAIRE |
| E-17 | Prédictif | Phase 4 | V1.6 | ⏳ À FAIRE |
| E-18 | Audit & Traçabilité | Phase 1 | S1 | ⏳ À FAIRE (= UI-14) |
| E-19 | Labellisation | Phase 5 | V2.2 | ⏳ À FAIRE |
| E-20 | Catalogue ML | Phase 4 | V1.1 | ⏳ À FAIRE |
| E-21 | Notifications WebSocket | Phase 5 | V2.1 | ⏳ À FAIRE |
| E-22 | Rapports programmés | Phase 4 | V1.1 | ⏳ À FAIRE |
| E-23 | Mobile-first & PWA | Phase 3 | S6 | ⏳ À FAIRE |
| E-24 | Data Lineage | Phase 5 | V2.2 | ⏳ À FAIRE |

### 12.3 Synthèse

| Phase | Tickets Frontend (UI) | Écrans (E) | Total tickets | Effort (pts) | Durée |
|---|---|---|---|---|---|
| Phase 1 (S1) | UI-11, 12, 13, 14, 30, 31, 34 (bootstrap) | E-10, E-18 | 8 | ≈ 35 | 2 sem |
| Phase 2 (S2) | UI-06, 08, 27, 28, 29, 32, 33, 36 | — | 8 | ≈ 20 | 2 sem |
| Phase 3 (S6) | UI-10, 26, 34, 35 | E-23 | 5 | ≈ 18 | 2 sem |
| Phase 4 (V1) | UI-15, 16, 17, 18, 19, 21, 23, 25, 39, 40 | E-11, 12, 13, 14, 15, 17, 20, 22 | 18 | ≈ 60 | 24 sem |
| Phase 5 (V2) | UI-20, 22, 24, 37, 38 | E-16, 19, 21, 24 | 9 | ≈ 50 | 36 sem |
| **Total** | **40 UI** | **15 E** | **48 + transverses** | **≈ 183** | **66 sem (≈ 15 mois)** |

### 12.4 Notes sur la traçabilité

- **UI-31 (`data-testid`)** est transversal et doit être appliqué **au fur et à mesure** dans chaque phase, pas uniquement en S1.
- **UI-34 (Vitest)** et **UI-35 (Cypress)** sont bootstrappés en Phase 1 mais complétés progressivement jusqu'en V2.
- **E-18 et UI-14** sont un seul et même écran (Audit & Traçabilité).
- **UI-22 (Page Labellisation)** est l'implémentation frontend d'E-19.
- **UI-39 (WebSocket Monitoring)** est déjà partiellement implémenté dans `PipelineAdmin.jsx` mais doit être étendu à `Monitoring.jsx`.

---

> **Conclusion** : Le Lot 13 représente **48 livrables** sur **5 phases** totalisant **≈ 183 points** et **66 semaines-homme**. Les phases 1-3 (S1, S2, S6) traitent l'ensemble des **P0 + P1 Frontend** et peuvent être livrées en **6 semaines** par une équipe de 1-2 développeurs. Les phases 4-5 (V1, V2) correspondent à la **transformation en plateforme BI industrialisable** et s'étalent sur **15 mois** avec une équipe renforcée.
>
> Le séquencement proposé minimise les dépendances bloquantes (mock API en attendant le backend, scaffolds par écran), maximise la valeur livrée tôt (auth + UX en S1-S2, i18n + PWA en S6), et réserve les chantiers lourds (drag & drop, labellisation, multi-tenant) à la phase V2.
