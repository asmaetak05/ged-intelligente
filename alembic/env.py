"""Configuration Alembic pour le projet GED Intelligente.

Ce module est appelé par Alembic à chaque commande (``alembic upgrade``,
``alembic revision``, ``alembic downgrade``, ...). Il a deux
responsabilités :

1. **Injecter la bonne URL de connexion** : on récupère ``DATABASE_URL``
   depuis l'environnement (chargé via ``python-dotenv`` comme dans
   ``backend/database.py``) et on l'écrit dans la config Alembic.
   C'est *la même* URL que celle utilisée par l'application — il n'y a
   donc qu'une seule source de vérité.

2. **Pointer ``target_metadata``** sur ``Base.metadata`` (depuis
   ``backend.database``) afin que la commande ``alembic revision
   --autogenerate`` puisse comparer le schéma courant (déduit des
   modèles SQLAlchemy) avec l'état de la base pour générer la migration.

Voir ``docs/implementation/phase-01-unification-bdd.md`` (T1.6) et
``docs/installation.md`` pour le mode opératoire.
"""
from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from alembic import context

# ---------------------------------------------------------------------------
# Résolution du chemin et chargement de l'environnement
# ---------------------------------------------------------------------------
# ``alembic`` est lancé depuis la racine du projet ; on s'assure que la
# racine est dans ``sys.path`` pour que ``from backend.database import ...``
# fonctionne, quel que soit le CWD.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Charge un éventuel .env local (DATABASE_URL=...), sans écraser l'env
# existant (cohérent avec ``backend.database.load_dotenv(override=False)``).
load_dotenv(PROJECT_ROOT / ".env", override=False)

# ---------------------------------------------------------------------------
# Configuration Alembic
# ---------------------------------------------------------------------------
config = context.config

# Lecture de l'URL de la base depuis l'environnement. Si absente, on
# retombe sur le défaut SQLite (même fallback que ``backend.database``).
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ged.db")
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Configuration des loggers via alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Cible d'autogénération
# ---------------------------------------------------------------------------
# ``Base.metadata`` porte toutes les tables déclarées dans ``backend.models``
# (Document, Marche, OcrLog, CritereHumain, MlInsight). L'import de
# ``backend.models`` est *volontaire* : c'est l'effet de bord qui enregistre
# les classes dans ``Base.metadata``.
from backend.database import Base  # noqa: E402
import backend.models  # noqa: E402, F401  (effet de bord : enregistre les tables)

target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Modes offline / online
# ---------------------------------------------------------------------------
def run_migrations_offline() -> None:
    """Exécute les migrations en mode ``offline`` (génère du SQL sans se
    connecter). Utile pour générer un script SQL à appliquer manuellement
    sur une base inaccessible depuis la machine d'Alembic."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # On laisse Alembic gérer le rendu SQL brut (INSERT INTO
        # alembic_version) sans tenter de taper la ligne.
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Exécute les migrations en mode ``online`` (se connecte à la base
    pour de bon). C'est le mode standard, appelé par ``alembic upgrade
    head``."""
    # Construction d'un engine éphémère (NullPool : on rend la connexion
    # au pool d'Alembic après usage, ce qui évite les connexions idle
    # gardées ouvertes par la session CLI).
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Configuration du contexte de migration
        is_sqlite = DATABASE_URL.startswith("sqlite")
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # SQLite ne supporte pas ``ALTER TABLE`` complet : Alembic
            # doit passer par le mode "batch" qui fait un
            # ``CREATE TABLE new_xx + INSERT + DROP + RENAME``.
            render_as_batch=is_sqlite,
            # Compare le type des colonnes (utile pour Numeric/Date/etc.)
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
