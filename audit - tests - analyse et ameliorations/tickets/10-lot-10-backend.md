# Lot 10 : Améliorations Backend, API & Sécurité

## Tickets Détaillés

### AU-01 — Page Login (UI-11) 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | M (2 j) |
| **Sprint cible** | S1 |
| **Composant** | `frontend-react/src/components/Login.jsx` (à créer) |
| **Scénarios liés** | ST-AU-001..003 |
| **Travail** | 1. Formulaire email + password + bouton « Se connecter ».<br>2. `react-hook-form` + `zod` pour validation.<br>3. Stockage du JWT en `httpOnly cookie` (sécurisé).<br>4. Redirection vers `/` après login.<br>5. Lien « Mot de passe oublié ». |

### SE-01 — Helmet (headers HTTP) 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/main.py` |
| **Scénarios liés** | ST-SE-005, ST-API-018 |
| **Travail** | `from secure import Secure` ; middleware FastAPI qui ajoute `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Content-Security-Policy`. |

### AU-02 — Logout 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S1 |
| **Scénarios liés** | ST-E2E-001 |
| **Travail** | Bouton « Déconnexion » dans la Topbar ; appel `POST /auth/logout`. |

### SE-02 — HTTPS obligatoire (Let's Encrypt) 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | S (1 j) |
| **Sprint cible** | S4 |
| **Composant** | Nginx reverse proxy, `docker-compose.yml` |
| **Scénarios liés** | ST-SE-007 |
| **Travail** | 1. Certbot en cron.<br>2. Nginx : `return 301 https://$host$request_uri`. |

### B-03 — Rate limiting (slowapi) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/main.py` |
| **Scénarios liés** | ST-SE-009, ST-API-015 |
| **Travail** | `from slowapi import Limiter` ; `limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])` ; `@limiter.limit("5/minute")` sur `/auth/login`. |

### AU-03 — Mot de passe oublié (email + token) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/auth/forgot_password.py` |
| **Scénarios liés** | ST-AU-004 |
| **Travail** | 1. `POST /api/v1/auth/forgot-password` génère token (15 min).<br>2. Email via SMTP (MailHog en dev).<br>3. `POST /api/v1/auth/reset-password?token=...` met à jour le mot de passe.<br>4. Table `password_reset_token`. |

### SE-03 — Gestionnaire de secrets (Vault / Infisical) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S4 |
| **Composant** | `backend/config.py` |
| **Scénarios liés** | ST-SE-006 |
| **Travail** | 1. Remplacer `.env` par Vault.<br>2. `pydantic.BaseSettings` charge depuis Vault.<br>3. Tests : `grep -r "OPENAI_API_KEY" dist/` doit retourner 0 hit. |

### B-04 — Handler global d'exceptions (RFC 7807) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (1 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/main.py` |
| **Scénarios liés** | ST-API-017 |
| **Description** | Remplacer les `raise HTTPException(500)` par un format `application/problem+json` uniforme. |
| **Travail** | `@app.exception_handler(Exception)` qui retourne `{"type": "...", "title": "...", "status": ..., "detail": ..., "instance": request_id}`. |

### AU-04 — Changement de mot de passe 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (1 j) |
| **Sprint cible** | S1 |
| **Scénarios liés** | ST-AU-005 |
| **Travail** | Page `/profile` ; formulaire ancien + nouveau + confirmation ; validation complexité. |

### SE-04 — Tests OWASP ZAP automatisés 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S4 |
| **Composant** | `.github/workflows/owasp.yml` |
| **Travail** | Lancement `zap-baseline.py` en CI ; alerte si alertes HIGH. |

### B-05 — Logs structurés (structlog) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (1 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/logging_config.py` |
| **Scénarios liés** | ST-OPS-004, ST-IN-013 |
| **Description** | Remplacer tous les `print()` par `logger.info(event="...", request_id=...)`. |
| **Travail** | 1. `structlog.configure(processors=[add_log_level, JSONRenderer()])`.<br>2. Middleware qui injecte `request_id` dans le `contextvars`.<br>3. Tests : `assert '"event": "document_uploaded"' in log_output`. |

### AU-05 — Verrouillage de compte (5 tentatives) 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | S (1 j) |
| **Sprint cible** | S1 |
| **Scénarios liés** | ST-AU-006 |
| **Travail** | 1. Colonne `user.failed_login_attempts`, `user.locked_until`.<br>2. Après 5 échecs → blocage 15 min, email admin.<br>3. Logout des sessions actives. |

### B-06 — Versionner les schémas Pydantic 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (1 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/schemas/v1/` |
| **Travail** | Créer `schemas/v1/marche.py`, `schemas/v2/...` ; import via `from backend.schemas.v1 import MarcheCreate`. |

### AU-06 — Session timeout (30 min) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S1 |
| **Scénarios liés** | ST-AU-007 |
| **Travail** | JWT `exp = now() + 30min` ; refresh token sliding window. |

### B-07 — File de tâches persistante (Celery + Redis) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | L (5 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/celery_app.py` |
| **Scénarios liés** | ST-IN-005, ST-ML-005, ST-API-008/009 |
| **Description** | Remplacer `BackgroundTasks` (non persistant) par Celery avec Redis. |
| **Travail** | 1. `celery_app = Celery("ged", broker="redis://localhost:6379/0")`.<br>2. Tâches : `process_document_async`, `retrain_models`, `compute_embeddings`.<br>3. Suivi via `GET /api/v1/jobs/{id}` (statut Celery).<br>4. Tests : `assert task.status == "SUCCESS"`. |

### AU-07 — MFA (TOTP) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | V1 |
| **Scénarios liés** | Scénario E10 |
| **Travail** | 1. `pyotp.TOTP` ; QR code.<br>2. Colonne `user.mfa_secret`, `user.mfa_enabled`.<br>3. UI : setup MFA dans `/profile`. |

### B-09 — Cache Redis (dashboard, search) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/cache.py` |
| **Scénarios liés** | ST-DB-012, ST-PE-003 |
| **Travail** | 1. `@cache.cached(timeout=30)` sur `/api/v1/analytics/kpis`.<br>2. Invalidation sur `POST /api/v1/ged/appels-offres` (cache bust).<br>3. Tests : 2e appel < 50 ms (depuis cache). |

### B-10 — Health check profond 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/main.py:601` |
| **Scénarios liés** | ST-OPS-011 |
| **Travail** | `/api/v1/system/health` qui teste DB (`SELECT 1`) + Redis (`PING`) + MinIO (`stat` sur bucket). |


## Tickets Résumés (Pas de détails exhaustifs)

| ID | Titre | Pri. | Effort | Sprint |
|---|---|---|---|---|
| SE-05 | | SE-05 | Scan `pip-audit` + `npm audit` en CI | 🟠 | S | S1 |
| SE-06 | | SE-06 | Scan `trivy` des images Docker | 🟠 | S | S4 |
| SE-07 | | SE-07 | CSRF protection | 🟠 | S | S1 |
| AU-08 | | AU-08 | Page Gestion des utilisateurs (admin) | 🟠 | M | S1 |
| SE-08 | | SE-08 | Validation stricte des uploads (mime + size) | 🟠 | S | S1 |
| AU-09 | | AU-09 | Éditeur de rôles et permissions | 🟠 | M | S1 |
| SE-09 | | SE-09 | Sanitization des inputs (DOMPurify côté front) | 🟠 | S | S1 |
| AU-10 | | AU-10 | Audit log immuable | 🔴 | M | S1 |
| SE-10 | | SE-10 | Chiffrement at rest (LUKS ou KMS) | 🟡 | M | V1 |
| B-11 | | B-11 | Endpoint `GET /api/v1/system/schema` (déjà partiel) | 🟡 | S | S1 |
| AU-11 | | AU-11 | Politique de mot de passe configurable | 🟠 | S | S1 |
| SE-11 | | SE-11 | WAF (Cloudflare) | 🟡 | M | V1 |
| B-12 | | B-12 | Endpoint pagination `{items, total, page, size, took_ms}` (déjà partiel) | 🟢 | — | — |
| AU-12 | | AU-12 | Rate limiting par utilisateur | 🟠 | S | S1 |
| SE-12 | | SE-12 | Penetration testing annuel | 🟡 | XL | V1 |
| B-13 | | B-13 | Préfixe `/api/v1/` partout (déjà fait) | 🟢 | — | — |
| AU-13 | | AU-13 | GDPR / droit à l'oubli | 🟡 | M | V1 |
| SE-13 | | SE-13 | Backup chiffré BDD | 🟠 | S | S4 |
| B-14 | | B-14 | Standardiser `__tablename__` explicite | 🟠 | S | S1 |
| AU-14 | | AU-14 | SSO OIDC (Keycloak) | 🟡 | L | V1 |
| SE-14 | | SE-14 | Rotation des secrets JWT | 🟠 | S | S4 |
| B-15 | | B-15 | Champ `request_id` middleware UUID | 🟠 | S | S1 |
| AU-15 | | AU-15 | Historique de connexion (IP, géoloc) | 🟠 | S | S1 |
| SE-15 | | SE-15 | Politique CORS stricte (déjà traitée en B-08) | 🟠 | S | S1 |
| B-16 | | B-16 | OpenTelemetry auto-instrumentation | 🟡 | M | V1 |
| B-17 | | B-17 | `factory-boy` + `pytest-postgresql` | 🟠 | S | S1 |
| B-18 | | B-18 | Documentation OpenAPI enrichie | 🟡 | M | S4 |
| B-19 | | B-19 | Endpoint `GET /api/v1/analytics/dashboard` unifié | 🟠 | S | S3 |
| B-20 | | B-20 | Endpoint `POST /api/v1/ged/appels-offres/export?format=csv` | 🔴 | M | S2 |
| B-21 | | B-21 | Endpoint `GET /api/v1/ged/appels-offres/export?format=xlsx` | 🟠 | M | S2 |
| B-22 | | B-22 | Endpoint `POST /api/v1/auth/forgot-password` | 🟠 | S | S1 |
| B-23 | | B-23 | Endpoint `POST /api/v1/auth/reset-password` | 🟠 | S | S1 |
| B-24 | | B-24 | Endpoint `POST /api/v1/auth/change-password` | 🟠 | S | S1 |
| B-25 | | B-25 | Endpoint `GET /api/v1/users` (admin) | 🟠 | M | S1 |
| B-26 | | B-26 | Endpoint `POST /api/v1/users` (admin) | 🟠 | S | S1 |
| B-27 | | B-27 | Endpoint `DELETE /api/v1/users/{id}` (admin) | 🟠 | S | S1 |
| B-28 | | B-28 | Endpoint `GET /api/v1/audit/events` | 🟡 | M | S1 |
| B-29 | | B-29 | Endpoint `GET /api/v1/ml/metrics` | 🟠 | S | S5 |
| B-30 | | B-30 | Endpoint `GET /api/v1/geo/aggregates?level=region` | 🟡 | L | V1 |
| B-31 | | B-31 | Endpoint `GET /api/v1/compare?ids=1,2,3` | 🟡 | M | V1 |
| B-32 | | B-32 | Endpoint `GET /api/v1/alerts/feed` (WebSocket) | 🟡 | M | V1 |
| B-33 | | B-33 | Endpoint `POST /api/v1/webhooks` | 🟡 | S | V1 |
| B-34 | | B-34 | Endpoint `POST /api/v1/scraper/schedule` | 🟠 | M | S1 |
| B-35 | | B-35 | Endpoint `GET /api/v1/jobs/{id}` (suivi des tâches) | 🟠 | S | S1 |