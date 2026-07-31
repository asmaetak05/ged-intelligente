# 00 — Socle qualité, sécurité et reproductibilité

**Priorité du module : P0.** Aucun autre module ne doit être déclaré finalisé avant celui-ci.

## SQ-01 — Retirer les secrets et comptes dangereux

**État : Partiel — défauts critiques identifiés.**

### Existant

- `backend/auth/auth_handler.py` utilise un secret JWT de repli codé en dur.
- `backend/main.py` crée automatiquement le compte `admin` avec le mot de passe `admin123`.
- `docker-compose.yml` contient le mot de passe PostgreSQL `password`.
- `backend/auth/forgot_password.py` écrit le jeton de reset dans les logs.

### Réalisation attendue

1. Modifier `backend/auth/auth_handler.py` : refuser le démarrage si `JWT_SECRET_KEY` est absent ou trop court ; ne garder aucun secret de repli.
2. Modifier `backend/main.py` : supprimer la création automatique d'un admin en production ; créer un script d'initialisation explicite réservé au développement.
3. Modifier `docker-compose.yml` et `.env.example` : utiliser des variables obligatoires, sans mot de passe réel.
4. Modifier `backend/auth/forgot_password.py` : ne jamais logger le jeton ; retourner un message générique et brancher un adaptateur de notification simulé/testable.
5. Ajouter `tests/test_security_config.py` pour tester l'absence de valeurs de repli.

### Critères d'acceptation

- l'API refuse de démarrer sans secret JWT valide ;
- aucun `admin123`, `my_super_secret` ou `password` par défaut n'est trouvable avec `rg` ;
- aucun log applicatif ne contient de reset token ;
- le compte administrateur de démo est créé uniquement par une commande documentée hors production.

## SQ-02 — Protéger les routes et formaliser le RBAC

**État : Partiel.** Les routes utilisateurs, audit, scraper et upload sont protégées, mais la majorité des routes GED, analytics, ML et monitoring ne le sont pas.

### Réalisation attendue

1. Créer `docs/MATRICE_RBAC.md` : rôles `lecteur`, `analyste`, `administrateur_fonctionnel`, `administrateur_technique` et droits par endpoint.
2. Ajouter les dépendances `RequireRole` dans les routes de `backend/main.py`, ou déplacer les routes vers `backend/routers/ged.py`, `analytics.py`, `ml.py`, `system.py` avec dépendances au niveau du router.
3. Rendre `/api/v1/system/schema` inaccessible hors administrateur technique ; limiter `/health` à une réponse non sensible.
4. Protéger les exports et les accès au texte OCR intégral.
5. Ajouter une matrice de tests 401/403/200 dans `tests/test_rbac.py`.

### Critères d'acceptation

- chaque endpoint métier a un rôle documenté ;
- les rôles non autorisés reçoivent 403 ; les anonymes reçoivent 401 ;
- l'OpenAPI indique les mécanismes de sécurité ;
- aucun endpoint ne révèle schéma, fichier ou contenu métier sans autorisation.

## SQ-03 — Rendre l'installation et les tests reproductibles

**État : À faire.** `requirements.txt` contient un bloc de dépendances dupliqué ; `structlog` est importé mais absent des dépendances ; `pytest-cov` était indisponible dans l'environnement ; les tests ne sont pas configurés.

### Réalisation attendue

1. Remplacer `requirements.txt` par des dépendances dédupliquées, séparées en `requirements.txt` et `requirements-dev.txt`, ou adopter `pyproject.toml`.
2. Ajouter les dépendances réellement importées : notamment `structlog`, `slowapi`, `python-jose`, `passlib`/`bcrypt`, `email-validator`.
3. Créer `pytest.ini` avec `testpaths = tests` pour empêcher pytest d'explorer `.venv`.
4. Ajouter `.github/workflows/ci.yml` ou une CI équivalente : installation, lint, tests backend, tests frontend et build React.
5. Aligner README, Dockerfile et runtime sur une unique version Python supportée ; supprimer le chemin Windows codé en dur de `ocr/extract_ocr.py`.
6. Ajouter `scripts/verify_project.ps1` qui exécute les contrôles locaux.

### Critères d'acceptation

- un clone propre réussit : installation Python, `pytest tests -q`, tests frontend et `npm run build` ;
- le temps et la sortie de chaque commande sont documentés ;
- aucun package n'est déclaré deux fois ;
- le Dockerfile utilise la même version majeure de Python que la documentation.

## SQ-04 — Unifier les migrations et les contrats API

**État : Partiel.** Alembic existe, mais `backend/main.py` appelle aussi `Base.metadata.create_all()` au démarrage. La création d'un appel d'offres utilise `Dict[str, Any]`.

### Réalisation attendue

1. Supprimer `Base.metadata.create_all()` du démarrage applicatif et rendre `alembic upgrade head` obligatoire.
2. Créer `backend/schemas/ged.py` : `MarcheCreate`, `MarcheUpdate`, `MarcheRead`, `DocumentRead`, `ApiError`.
3. Remplacer `Dict[str, Any]` du endpoint de création par les schémas Pydantic.
4. Éliminer progressivement `_marche_to_legacy` et aligner les noms : choisir une seule représentation pour montant/budget/estimation.
5. Ajouter `tests/test_migrations.py` et des tests de validation des schémas.

### Critères d'acceptation

- une base vide créée uniquement par Alembic permet de démarrer l'API ;
- une requête invalide retourne une erreur structurée 422 ;
- aucune création implicite de tables en production ;
- les noms des champs API sont documentés dans `docs/Dictionnaire_Donnees_V2.md`.

