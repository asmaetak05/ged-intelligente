"""Configuration de la couche d'accès aux données.

Ce module choisit dynamiquement le moteur de base de données en fonction
de la variable d'environnement ``DATABASE_URL`` :

* ``sqlite:///...``  (défaut en dev) : SQLite via fichier local, mono-thread safe.
* ``postgresql://...`` (cible prod)  : PostgreSQL via driver psycopg2/psycopg.

L'objectif est d'avoir un code applicatif identique quel que soit le
moteur : tout passe par ``engine`` / ``SessionLocal`` / ``Base`` / ``get_db``.

Décision d'architecture documentée dans ``docs/Note_Decision_V1.md``
(section 5 « Décision Phase 1 — Choix du moteur BDD »).
"""
from __future__ import annotations

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Charge un éventuel .env local (non versionné) pour surcharger les défauts.
# En production (Docker), DATABASE_URL vient de l'environnement du conteneur
# et .env n'existe pas : le `override=False` garantit qu'on ne ré-écrase pas
# une valeur déjà fournie par le shell.
load_dotenv(override=False)

# ---------------------------------------------------------------------------
# Construction de l'URL de connexion
# ---------------------------------------------------------------------------
# Défaut : SQLite local (``./ged.db`` à la racine du projet).
# Toute URL commençant par ``sqlite`` déclenchera la branche SQLite.
# Toute autre URL (postgresql, mysql, ...) passe par les connect_args
# standard de SQLAlchemy.
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ged.db")

_IS_SQLITE: bool = DATABASE_URL.startswith("sqlite")


def _build_engine(url: str) -> Engine:
    """Construit un engine SQLAlchemy adapté au driver ciblé.

    Pour SQLite, on désactive la vérification ``check_same_thread`` afin de
    permettre l'usage de l'engine depuis plusieurs threads (notamment
    depuis le thread principal FastAPI et les BackgroundTasks).

    Pour PostgreSQL (et autres), on laisse SQLAlchemy choisir ses défauts :
    pool de connexions, gestion transactionnelle, etc.
    """
    if url.startswith("sqlite"):
        # ``check_same_thread=False`` est requis par SQLite quand l'engine
        # est partagé entre threads (cas FastAPI / uvicorn). Sécurité
        # compensée par le ``with`` dans ``get_db()``.
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            echo=False,
            future=True,
        )
    # PostgreSQL (psycopg2 ou psycopg) — pool par défaut.
    return create_engine(url, echo=False, future=True, pool_pre_ping=True)


engine: Engine = _build_engine(DATABASE_URL)

# ---------------------------------------------------------------------------
# Session & base déclarative
# ---------------------------------------------------------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

Base = declarative_base()


# ---------------------------------------------------------------------------
# Dépendance FastAPI
# ---------------------------------------------------------------------------
def get_db():
    """Fournit une ``Session`` SQLAlchemy par requête HTTP.

    Usage :::

        @app.get("/...")
        def endpoint(db: Session = Depends(get_db)):
            ...

    Le ``try/finally`` garantit la fermeture systématique, même en cas
    d'exception, pour éviter les fuites de connexion sur PostgreSQL.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Helpers (utile pour Alembic en T1.6 et pour le seed en T1.7)
# ---------------------------------------------------------------------------
def get_database_url() -> str:
    """Expose l'URL courante (utile pour les logs de démarrage et Alembic)."""
    return DATABASE_URL


def is_sqlite() -> bool:
    """Indique si l'engine actuel est un SQLite (utile pour les migrations
    conditionnelles — voir T1.6 : le GIN/tsvector ne sera créé que si on est
    sur PostgreSQL)."""
    return _IS_SQLITE


def is_postgresql() -> bool:
    """Indique si l'engine actuel est un PostgreSQL."""
    return DATABASE_URL.startswith(("postgresql", "postgres"))


__all__ = [
    "DATABASE_URL",
    "engine",
    "SessionLocal",
    "Base",
    "get_db",
    "get_database_url",
    "is_sqlite",
    "is_postgresql",
]
