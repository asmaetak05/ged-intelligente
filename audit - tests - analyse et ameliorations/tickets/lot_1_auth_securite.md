# 🎫 Lot 1 : Authentification & Sécurité (Auth & Security)

## 📌 Présentation du Lot
Ce lot vise à sécuriser la plateforme en mettant en œuvre le contrôle d'accès basé sur les rôles (RBAC), le protocole d'authentification par jetons JWT, et en durcissant la sécurité HTTP (CORS, en-têtes).

* **Complexité globale** : Medium
* **Composants impactés** : `backend/auth/` (nouveaux fichiers), `backend/models.py`, `backend/main.py`
* **Indépendance git** : Totale. Il ne modifie pas les flux de traitement des documents, l'OCR, le NLP ou les composants du tableau de bord. Il ajoute une couche d'authentification externe.

---

## 📋 Liste des Tickets Associés

### 1. B-01 — Authentification JWT 🔴
* **Priorité** : 🔴 P0
* **Effort** : M (3 j)
* **Composant** : `backend/auth/auth_handler.py`, `backend/auth/auth_router.py`
* **Scénarios de test liés** : `ST-AU-001` à `ST-AU-007`
* **Description** : Implémenter l'authentification sécurisée avec signature de Tokens JWT (Access Token, Refresh Token), le hachage des mots de passe avec bcrypt, et la gestion du logout (jetons révoqués).

### 2. B-02 — RBAC (Role-Based Access Control) 🔴
* **Priorité** : 🔴 P0
* **Effort** : M (2 j)
* **Composant** : `backend/auth/rbac.py`, `backend/models.py`
* **Scénarios de test liés** : `ST-AU-008` à `ST-AU-010`
* **Description** : Déclarer les tables `User`, `Role` et `Permission`. Gérer trois rôles utilisateurs distincts :
  * `reader` : Consultation et recherche uniquement.
  * `analyst` : Importation, NLP, ML et correction manuelle.
  * `admin` : Administration du pipeline, logs système et gestion des rôles.
* **Travail** : Implémenter le décorateur/dépendance FastAPI pour la validation des scopes.

### 3. B-08 — CORS strict et En-têtes de Sécurité 🟠
* **Priorité** : 🟠 P1
* **Effort** : S (1 j)
* **Composant** : `backend/main.py`
* **Scénarios de test liés** : `ST-SE-001` à `ST-SE-005`
* **Description** : Restreindre l'accès à l'API via un middleware CORS strict (whitelist paramétrable via variable d'environnement). Injecter des en-têtes de sécurité recommandés (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security`).

---

## 🛠️ Description des Travaux
1. **Création du module `backend/auth`** :
   - Écrire un routeur d'authentification avec les endpoints `/api/v1/auth/login`, `/api/v1/auth/refresh`, `/api/v1/auth/logout`.
   - Créer des dépendances pour extraire et valider le jeton JWT des en-têtes HTTP `Authorization: Bearer <token>`.
2. **Ajout des modèles BDD** :
   - Ajouter les entités `User` et `Role` dans `backend/models.py` et générer la migration Alembic associée.
3. **Sécurisation des routes existantes** :
   - Intégrer les dépendances de validation de jetons sur les routes d'ingestion (requérant `analyst`) et d'administration (requérant `admin`).

---

## 🧪 Critères de Validation et Non-régression
- **Validation unitaire** : Écrire `tests/test_auth.py` pour valider :
  - Génération et expiration de jetons JWT.
  - Rejet d'accès pour les routes protégées sans token ou avec un token invalide.
  - Restriction d'un rôle `reader` tentant d'appeler l'API de scraping.
- **Vérification CORS** : Simuler une requête d'origine non autorisée et s'assurer du code d'erreur HTTP 400/403.
