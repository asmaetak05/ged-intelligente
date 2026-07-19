# Lot 13 : Nouveaux Écrans & Améliorations Frontend

## Tickets Détaillés

### UI-06 — Tri configurable (date / montant / pertinence) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (1 j) |
| **Sprint cible** | S2 |
| **Composant** | `frontend-react/src/components/SearchFTS.jsx` |
| **Scénarios liés** | ST-FT-019..021, ST-UI-013 |
| **Travail** | Dropdown `sortBy=date|montant|pertinence` ; `orderDir=asc|desc`. |

### UI-08 — Surlignage des termes trouvés 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (1 j) |
| **Sprint cible** | S2 |
| **Composant** | `frontend-react/src/components/SearchResult.jsx` |
| **Scénarios liés** | ST-FT-022, ST-UI-011 |
| **Travail** | `dangerouslySetInnerHTML={{__html: result.highlight}}` (avec sanitize DOMPurify). |


## Tickets Résumés (Pas de détails exhaustifs)

| ID | Titre | Pri. | Effort | Sprint |
|---|---|---|---|---|
| UI-10 | | UI-10 | i18next FR/AR | 🟠 | M | S6 |
| E-10 | | E-10 | Authentification & Gestion des utilisateurs | 🔴 | L | S1 | AU-01, AU-08, BDD-10 |
| UI-11 | | UI-11 | Page Login | 🔴 | M | S1 |
| E-11 | | E-11 | Centre d'alertes & watchlist personnalisée | 🟡 | L | V1 | BDD-13, ING-09 |
| UI-12 | | UI-12 | Page Profil utilisateur | 🟠 | M | S1 |
| E-12 | | E-12 | Cartographie des AO (Leaflet) | 🟡 | L | V1 | BDD-05, B-30 |
| UI-13 | | UI-13 | Page Gestion des utilisateurs (admin) | 🟠 | M | S1 |
| E-13 | | E-13 | Comparateur d'appels d'offres | 🟡 | L | V1 | B-31, ML-04 |
| UI-14 | | UI-14 | Page Audit & Traçabilité | 🟡 | M | S1 |
| E-14 | | E-14 | Tableau de bord Acheteur | 🟡 | L | V1 | BDD-02, E16 |
| UI-15 | | UI-15 | Page Centre d'alertes (E11) | 🟡 | L | V1 |
| E-15 | | E-15 | Tableau de bord Fournisseur | 🟡 | L | V1 | E-11, ML-06 |
| UI-16 | | UI-16 | Page Cartographie (E12) | 🟡 | L | V1 |
| E-16 | | E-16 | Analytics Avancés (DataViz, drag & drop) | 🟡 | XL | V2 | D-09..D-20 |
| UI-17 | | UI-17 | Page Comparateur (E13) | 🟡 | L | V1 |
| E-17 | | E-17 | Prédictif & Prévisions (Prophet) | 🟡 | L | V1 | ML-18 |
| UI-18 | | UI-18 | Page Dashboard Acheteur (E14) | 🟡 | L | V1 |
| E-18 | | E-18 | Audit & Traçabilité | 🟠 | M | S1 | BDD-11, AU-10 |
| UI-19 | | UI-19 | Page Dashboard Fournisseur (E15) | 🟡 | L | V1 |
| E-19 | | E-19 | Labellisation collaborative | 🟡 | XL | V2 | ML-13, BDD-12 |
| UI-20 | | UI-20 | Page Analytics Avancés (E16) | 🟡 | L | V2 |
| E-20 | | E-20 | Catalogue des modèles ML | 🟡 | M | V1 | ML-07 |
| UI-21 | | UI-21 | Page Prédictif (E17) | 🟡 | L | V1 |
| E-21 | | E-21 | Notifications & Messagerie (WebSocket) | 🟡 | M | V2 | OPS-08, B-32 |
| UI-22 | | UI-22 | Page Labellisation (E19) | 🟡 | L | V2 |
| E-22 | | E-22 | Rapports programmés (PDF/Excel) | 🟡 | M | V1 | DOC-09 |
| UI-23 | | UI-23 | Page Catalogue ML (E20) | 🟡 | M | V1 |
| E-23 | | E-23 | Mobile-first & PWA | 🟡 | M | S6 | UI-26, OPS-15 |
| UI-24 | | UI-24 | Page Notifications (E21) | 🟡 | M | V2 |
| E-24 | | E-24 | Data Lineage & Quality | 🟡 | L | V2 | D-12, ML-08 |
| UI-25 | | UI-25 | Page Rapports programmés (E22) | 🟡 | M | V1 |
| UI-26 | | UI-26 | PWA installable (vite-plugin-pwa) | 🟡 | M | S6 |
| UI-27 | | UI-27 | Mode sombre/clair toggle | 🟠 | S | S2 |
| UI-28 | | UI-28 | Raccourcis clavier (`/` focus recherche) | 🟠 | S | S2 |
| UI-29 | | UI-29 | Lazy loading des routes (React.lazy) | 🟠 | S | S2 |
| UI-30 | | UI-30 | 404 / 403 / 500 pages | 🟠 | S | S1 |
| UI-31 | | UI-31 | `data-testid` partout (convention) | 🟠 | S | S1 |
| UI-32 | | UI-32 | Bundle visualizer (`vite-bundle-visualizer`) | 🟡 | S | S2 |
| UI-33 | | UI-33 | Storybook | 🟡 | M | S2 |
| UI-34 | | UI-34 | Tests Vitest + React Testing Library | 🟠 | M | S1-S6 |
| UI-35 | | UI-35 | Tests Cypress (≥ 20 scénarios) | 🟠 | L | S1-S6 |
| UI-36 | | UI-36 | Accessibilité (aria-label, focus visible) | 🟠 | M | S2 |
| UI-37 | | UI-37 | Notifications navigateur (Web Notifications API) | 🟡 | S | V1 |
| UI-38 | | UI-38 | Drag & drop widgets (E16) | 🟡 | M | V2 |
| UI-39 | | UI-39 | WebSocket Monitoring (logs temps réel) | 🟠 | M | S1 |
| UI-40 | | UI-40 | Heatmap calendrier des publications | 🟡 | M | V1 |