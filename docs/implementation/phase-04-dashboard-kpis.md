# Phase 4 — Dashboard décisionnel (KPIs réels)

> **Effort** : 1,5 journée · **Risque** : moyen · **Pré-requis** : Phases 1–3 terminées (données réelles en BDD)

---

## T4.1 — KPI `taux_reussite_ocr_pct` calculé

**Description & objectif** : remplacer la valeur hardcodée `98.5` par un calcul réel.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `backend` | `MODIFY` | `backend/repository.py` : ajouter `MarcheRepository.ocr_quality_pct() -> float` :<br>```python<br>def ocr_quality_pct(self) -> float:<br>    total = self.db.query(OcrLog).count()<br>    if total == 0:<br>        return None<br>    success = self.db.query(OcrLog).filter(OcrLog.confidence_score_avg >= 70).count()<br>    return round(100.0 * success / total, 1)<br>``` |
| `backend` | `MODIFY` | `backend/main.py` : `get_kpis()` utilise `repo.ocr_quality_pct()`. |

**Plan de vérification** :
- [ ] Insérer manuellement 2 `OcrLog` (confidence 90 et 50), `GET /api/v1/analytics/kpis` retourne `taux_reussite_ocr_pct=50.0`.
- [ ] Si la table est vide, retourne `null` (pas 0 trompeur).

---

## T4.2 — Top 10 acheteurs (au lieu de 4)

**Description & objectif** : respecter le plan, qui prévoit `Top 10`.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `backend` | `MODIFY` | `backend/repository.py` : `MarcheRepository.top_buyers(limit=10)`. |
| `backend` | `MODIFY` | `backend/main.py` : `get_top_buyers` accepte un query param `?limit=10` (défaut 10, max 50). |

**Plan de vérification** :
- [ ] Avec 12+ AO, `GET /api/v1/analytics/top-buyers` retourne jusqu'à 10 entrées.
- [ ] `?limit=3` retourne 3.

---

## T4.3 — Volume par période (trends)

**Description & objectif** : remplacer les 3 valeurs mockées `[10, 25, 15]` par un groupement mensuel réel.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `backend` | `MODIFY` | `backend/repository.py` : `MarcheRepository.by_month(months=12) -> List[dict]` :<br>```python<br>def by_month(self, months: int = 12):<br>    # SQLite : strftime('%Y-%m', date_publication)<br>    # PostgreSQL : date_trunc('month', date_publication)<br>    if self.db.bind.dialect.name == 'sqlite':<br>        sql = "SELECT strftime('%Y-%m', date_publication) AS month, COUNT(*) AS c, SUM(montant) AS volume FROM marches WHERE date_publication IS NOT NULL GROUP BY month ORDER BY month DESC LIMIT ?"<br>    else:<br>        sql = "SELECT to_char(date_trunc('month', date_publication), 'YYYY-MM') AS month, COUNT(*) AS c, SUM(montant) AS volume FROM marches WHERE date_publication IS NOT NULL GROUP BY month ORDER BY month DESC LIMIT %s"<br>    ...<br>``` |
| `backend` | `MODIFY` | `backend/main.py` : `get_trends(months=12)` retourne `{"months": [...], "volumes": [...], "counts": [...]}`. |

**Plan de vérification** :
- [ ] Avec 12 AO répartis sur 3 mois, `GET /api/v1/analytics/trends` retourne 3 mois, pas 3 valeurs en dur.

---

## T4.4 — Volume par catégorie + période

**Description & objectif** : ajouter le découpage par catégorie dans le temps (utile pour la démo).

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `backend` | `MODIFY` | `backend/repository.py` : `by_category_month()` retourne `[{"month": "2025-08", "Travaux": 3, "Services": 1, ...}]`. |
| `backend` | `MODIFY` | `backend/main.py` : `GET /api/v1/analytics/trends/by-category`. |

**Plan de vérification** :
- [ ] `GET /api/v1/analytics/trends/by-category` retourne un dict avec les 4 catégories.
- [ ] Si pas de données, retourne des zéros.

---

## T4.5 — Délai moyen publication → date limite

**Description & objectif** : un KPI manquant identifié dans le rapport d'audit.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `backend` | `MODIFY` | `backend/repository.py` : `delai_moyen() -> float` :<br>```python<br>def delai_moyen(self):<br>    sql = "SELECT AVG(julianday(date_limite) - julianday(date_parution)) AS d FROM marches WHERE date_limite IS NOT NULL AND date_parution IS NOT NULL"<br>    return round(float(result), 1) if result else None<br>``` |
| `backend` | `MODIFY` | `backend/main.py` : `GET /api/v1/analytics/delai-moyen` retourne `{"delai_moyen_jours": 18.5, "sample_size": 12}`. |

**Plan de vérification** :
- [ ] Avec 3 AO où `date_limite - date_parution = 10, 20, 30`, le retour est `20.0`.
- [ ] Si pas de données, `null`.

---

## T4.6 — Tests des agrégations

**Description & objectif** : valider que les requêtes d'agrégation sont correctes.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `tests` | `NEW` | `tests/test_analytics.py` (≥ 6 tests) :<br>- `test_kpis_count_matches_db`<br>- `test_ocr_quality_pct`<br>- `test_top_buyers_limit`<br>- `test_trends_by_month`<br>- `test_trends_by_category`<br>- `test_delai_moyen` |

**Plan de vérification** :
- [ ] `pytest tests/test_analytics.py -v` → 6 passed.

---

## T4.7 — Refactor du composant Dashboard React

**Description & objectif** : supprimer toutes les valeurs hardcodées du composant `Dashboard.jsx`, brancher sur les nouvelles routes.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `frontend` | `MODIFY` | `frontend-react/src/components/Dashboard.jsx` :<br>1. Remplacer `taux_reussite_ocr_pct: 98.5` par fetch `GET /api/v1/analytics/kpis`.<br>2. Remplacer `top_buyers` (mocké) par fetch `GET /api/v1/analytics/top-buyers?limit=10`.<br>3. Remplacer `trends` (mocké) par fetch `GET /api/v1/analytics/trends`.<br>4. Ajouter graphique "Volume par catégorie" (bar chart horizontal) via Recharts. |
| `frontend` | `MODIFY` | `frontend-react/src/components/Dashboard.jsx` : ajouter `useEffect` + `useState` pour les chargements, indicateur de loading, gestion d'erreur. |

**Plan de vérification** :
- [ ] `npm run build` réussit.
- [ ] Au lancement, le dashboard affiche les chiffres réels (pas les mocks).
- [ ] Si l'API est arrêtée, un message d'erreur s'affiche (pas de crash).

---

## T4.8 — Tests E2E du dashboard

**Description & objectif** : valider le rendu visuel (snapshots).

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `repo` | `MODIFY` | `frontend-react/package.json` : ajouter `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `jsdom` |
| `repo` | `CMD` | `npm install` |
| `frontend` | `NEW` | `frontend-react/src/components/__tests__/Dashboard.test.jsx` (3 tests) :<br>- `test_renders_kpis`<br>- `test_renders_top_buyers`<br>- `test_handles_api_error` |
| `frontend` | `NEW` | `frontend-react/vitest.config.js` (config jsdom + setup). |

**Plan de vérification** :
- [ ] `npm test` → 3 passed.
- [ ] `npm run build` toujours OK.

---

## ✅ Critères de sortie de la Phase 4

- [ ] Aucun chiffre hardcodé dans `Dashboard.jsx`.
- [ ] `GET /api/v1/analytics/kpis` retourne un `taux_reussite_ocr_pct` qui varie selon les données.
- [ ] `GET /api/v1/analytics/top-buyers` retourne 10 entrées par défaut.
- [ ] `GET /api/v1/analytics/trends` retourne ≥ 3 mois de données réelles.
- [ ] `GET /api/v1/analytics/delai-moyen` retourne un nombre ou `null`.
- [ ] `pytest tests/test_analytics.py` → 6/6.
- [ ] `npm test` → 3/3.

**Effort total** : 1,5 jour ouvré.
