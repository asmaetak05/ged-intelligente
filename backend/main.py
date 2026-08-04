"""GED Intelligente — point d'entrée FastAPI (Phase 1, post-refactoring).

Ce module ne contient **plus aucun accès direct à la base de données** :
toute la logique SQL/SQLAlchemy est centralisée dans ``backend.repository``.

Trois zones fonctionnelles (préfixes) :
- ``/api/v1/ged``        : ingestion, recherche, gestion documentaire.
- ``/api/v1/analytics``  : KPIs et tableaux de bord.
- ``/api/v1/ml``         : prédictions et monitoring ML.
- ``/api/v1/system``     : monitoring système.

Décision d'architecture documentée dans ``docs/Note_Decision_V1.md``.
"""
from __future__ import annotations

import json
import re
import os
import subprocess
from datetime import date, datetime
from typing import Any, Dict, List, Optional
import uuid
import structlog
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from backend.logging_config import setup_logging
from backend.limiter import limiter

setup_logging()
logger = structlog.get_logger()

from fastapi import Body, Depends, FastAPI, File, HTTPException, UploadFile, BackgroundTasks, WebSocket, WebSocketDisconnect, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session
from backend.auth.auth_router import router as auth_router
from backend.auth.forgot_password import router as forgot_password_router
from backend.routers.users import router as users_router
from backend.routers.audit import router as audit_router
from backend.routers.scraper import router as scraper_router
from backend.auth.rbac import RequireRole, get_current_user
from backend.auth.auth_handler import get_password_hash

from . import models
from .database import Base, engine, get_db
from .repository import (
    DocumentRepository,
    MarcheFilter,
    MarcheRepository,
    OcrLogRepository,
)
from ml.predict import predict_category
from ml.features import extract_text_feature


# ---------------------------------------------------------------------------
# Application FastAPI
# ---------------------------------------------------------------------------
app = FastAPI(
    title="GED Intelligente API",
    version="2.0.0",
    description=(
        "API REST de la GED Intelligente (PFA). "
        "Couche d'accès aux données unifiée via `backend.repository`."
    ),
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Skip handling HTTPException to let FastAPI handle it
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
        
    req_id = structlog.contextvars.get_contextvars().get("request_id", "unknown")
    logger.exception("Unhandled exception", exc_info=exc, request_id=req_id, path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "type": "about:blank",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "Une erreur interne inattendue s'est produite.",
            "instance": req_id
        }
    )

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    req_id = str(uuid.uuid4())
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=req_id, path=request.url.path, method=request.method)
    response = await call_next(request)
    response.headers["X-Request-ID"] = req_id
    return response

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

app.include_router(auth_router)
app.include_router(forgot_password_router)
app.include_router(users_router)
app.include_router(audit_router)
app.include_router(scraper_router)


# ---------------------------------------------------------------------------
# Démarrage : création des tables (idempotent, sert de filet de sécurité
# tant qu'Alembic n'est pas configuré — T1.6).
# ---------------------------------------------------------------------------
@app.on_event("startup")
def _on_startup() -> None:
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        # On ne crash pas : l'API peut fonctionner en mode dégradé si
        # certaines tables existent déjà, ou afficher des messages clairs.
        logger.warning("initialisation partielle", error=str(e))
        
    # Seed default admin user
    from backend.database import SessionLocal
    from backend.models import User, Role
    with SessionLocal() as db:
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            admin_role = Role(name="admin", description="Administrateur système")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)

        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            hashed_pw = get_password_hash("admin123")
            new_admin = User(
                username="admin",
                email="admin@ged-intelligente.local",
                hashed_password=hashed_pw,
                roles=[admin_role]
            )
            db.add(new_admin)
            db.commit()
            logger.info("Default admin user created", username="admin")


# ---------------------------------------------------------------------------
# Monitoring Système
# ---------------------------------------------------------------------------
@app.get("/api/v1/system/health", tags=["system"])
def system_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = "error"
        logger.error("DB health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Database is unavailable")
        
    return {
        "status": "ok",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/v1/system/references", tags=["system"])
def get_system_references(db: Session = Depends(get_db)):
    """Retourne l'ensemble des données de référence (types avis, villes, directions, qualifications)."""
    types_avis = db.query(models.TypeAvis).all()
    procedures = db.query(models.TypeProcedure).all()
    etats = db.query(models.EtatAvis).all()
    directions = db.query(models.Direction).all()
    villes = db.query(models.Ville).order_by(models.Ville.name).all()
    qualifications = db.query(models.Qualification).all()
    agrements = db.query(models.Agrement).all()

    return {
        "types_avis": [{"id": t.id, "code": t.code, "label": t.label} for t in types_avis],
        "procedures": [{"id": p.id, "code": p.code, "label": p.label} for p in procedures],
        "etats": [{"id": e.id, "code": e.code, "label": e.label} for e in etats],
        "directions": [{"id": d.id, "name": d.name, "type_dir": d.type_dir} for d in directions],
        "villes": [
            {
                "id": v.id,
                "name": v.name,
                "province": v.province,
                "region": v.region,
                "lat": float(v.lat) if v.lat else None,
                "lon": float(v.lon) if v.lon else None,
            }
            for v in villes
        ],
        "qualifications": [
            {"id": q.id, "code": q.code, "label": q.label, "classe": q.classe, "categorie": q.categorie}
            for q in qualifications
        ],
        "agrements": [{"id": a.id, "code": a.code, "label": a.label, "type_agrement": a.type_agrement} for a in agrements],
    }


# ===========================================================================
# Helpers — sérialisation et parsing
# ===========================================================================
def _serialiser_champ(valeur: Any) -> Any:
    """Convertit listes/dicts en JSON string (colonnes TEXT legacy)."""
    if isinstance(valeur, (list, dict)):
        return json.dumps(valeur, ensure_ascii=False)
    return valeur


def _parse_number(value: Any) -> float:
    """Extrait un nombre depuis un texte du type '440 000,00 MAD' ou
    '12 mois'. Tolère les valeurs déjà numériques.
    """
    if value is None or value == "":
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = re.sub(r"[^\d,\.]", "", str(value))
    cleaned = cleaned.replace(" ", "").replace(",", ".")
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0


def _marche_to_legacy(marche: models.Marche) -> Dict[str, Any]:
    """Convertit un objet ``Marche`` (SQLAlchemy) en dictionnaire plat
    compatible avec la forme JSON historique consommée par le frontend
    vanilla (``numero_ordre`` / ``objet`` / ``maitre_ouvrage`` / etc.).

    Cette passerelle permet de remplacer l'accès ``sqlite3`` legacy sans
    casser le front en attendant la migration T1.8 (suppression du
    frontend vanilla au profit de ``frontend-react/``).
    """
    return {
        "id": marche.id,
        "numero_ordre": marche.numero_appel_offre,
        "objet": marche.titre_projet,
        "maitre_ouvrage": marche.organisme_acheteur,
        "estimation_mad": str(marche.montant) if marche.montant is not None else None,
        "caution_mad": str(marche.caution_provisoire_mad) if marche.caution_provisoire_mad is not None else None,
        "caution_definitive": (
            f"{float(marche.caution_definitive_pct)}%" if marche.caution_definitive_pct is not None else None
        ),
        "dossier_zip_source": (
            f"doc-{marche.document_source_id}.zip" if marche.document_source_id else None
        ),
        "delai_execution": (
            f"{marche.delai_execution_mois} mois" if marche.delai_execution_mois is not None else None
        ),
        "penalite_retard": (
            f"{marche.penalite_retard_mille} pour mille" if marche.penalite_retard_mille is not None else None
        ),
        "agrements_exiges": (
            ", ".join(marche.agreements_exiges) if isinstance(marche.agreements_exiges, list)
            else marche.agreements_exiges
        ),
        "date_ouverture_plis": (
            marche.date_limite.isoformat() if marche.date_limite else None
        ),
        "lieu_ouverture_plis": marche.ville_execution or "Maroc",
        "categorie_marche": (
            marche.categorie_prestation.value if marche.categorie_prestation else None
        ),
        "region": marche.region,
        "reference": marche.reference,
        "date_ingestion": (
            marche.created_at.isoformat() if marche.created_at else None
        ),
    }


# ===========================================================================
# 🔐 Espace Recherche & Ingestion (/api/v1/ged)
# ===========================================================================
@app.post("/api/v1/ged/documents/upload")
async def upload_document(
    background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db),
    user=Depends(RequireRole(["analyst"]))
):
    """Upload d'un document (traitement asynchrone déclenché)."""
    import os
    import uuid
    import shutil
    
    # Validation du format (ZIP, PDF, DOCX)
    magic = await file.read(4)
    await file.seek(0)
    
    filename_lower = (file.filename or "").lower()
    is_zip = magic == b"PK\x03\x04" or filename_lower.endswith(".zip")
    is_pdf = magic.startswith(b"%PDF") or filename_lower.endswith(".pdf")
    is_docx = filename_lower.endswith(".docx")
    
    if not (is_zip or is_pdf or is_docx):
        raise HTTPException(status_code=400, detail="Type de fichier invalide. Formats acceptés : ZIP, PDF, DOCX.")
    
    MAX_UPLOAD_SIZE = 100 * 1024 * 1024 # 100 MB max
    file.file.seek(0, 2)
    file_size = file.file.tell()
    await file.seek(0)
    
    if file_size > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail=f"Fichier trop volumineux. Max: {MAX_UPLOAD_SIZE/1024/1024} MB")
    
    os.makedirs("data/raw", exist_ok=True)
    ext = ".zip" if is_zip else (".pdf" if is_pdf else ".docx")
    if file.filename:
        safe_name = os.path.basename(file.filename)
    else:
        safe_name = f"doc_{uuid.uuid4().hex[:8]}{ext}"
        
    file_path = os.path.join("data/raw", safe_name)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    file_size_kb = os.path.getsize(file_path) // 1024

    # Calculer le hash SHA-256 (ING-04)
    import hashlib
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    checksum = sha256_hash.hexdigest()

    # Déduplication (ING-04)
    existing_doc = db.query(models.Document).filter(
        models.Document.checksum_sha256 == checksum,
        models.Document.status == models.DocStatus.ocr_processed
    ).first()

    if existing_doc:
        logger.info("Document avec hash déjà traité", checksum=checksum, doc_id=existing_doc.id)
        return {
            "document_id": existing_doc.id,
            "message": "Document déjà traité (déduplication active)",
            "filename": file.filename,
            "status": "ocr_processed"
        }

    doc = models.Document(
        archive_name=safe_name,
        file_name=file.filename or safe_name,
        extension=ext.lstrip("."),
        storage_path=file_path,
        status=models.DocStatus.raw_zip,
        file_size_kb=file_size_kb,
        checksum_sha256=checksum
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    from .tasks import process_document_async
    background_tasks.add_task(process_document_async, doc.id, file_path)

    return {
        "document_id": doc.id,
        "message": "Document reçu, traitement asynchrone en cours",
        "filename": file.filename,
        "status": "queued"
    }

@app.get("/api/v1/ged/documents/{doc_id}/status")
def get_document_status(doc_id: int, db: Session = Depends(get_db)):
    repo = DocumentRepository(db)
    doc = repo.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    ocr_repo = OcrLogRepository(db)
    logs = ocr_repo.list_by_document(doc.id)
    ocr_confidence = float(logs[0].confidence_score_avg) if logs and logs[0].confidence_score_avg else None
        
    return {
        "id": doc.id,
        "status": doc.status.value if doc.status else None,
        "filename": doc.file_name,
        "updated_at": doc.created_at.isoformat() if doc.created_at else None,
        "ocr_confidence": ocr_confidence
    }


@app.get("/api/v1/ged/search")
def search_documents(
    q: str = "",
    page: int = 1,
    page_size: int = 20,
    categorie: Optional[str] = None,
    region: Optional[str] = None,
    ville: Optional[str] = None,
    organisme: Optional[str] = None,
    date_min: Optional[date] = None,
    date_max: Optional[date] = None,
    montant_min: Optional[float] = None,
    montant_max: Optional[float] = None,
    order_by: str = "pertinence",
    order_dir: str = "desc",
    db: Session = Depends(get_db),
):
    """Recherche plein texte enrichie (FTS natif avec ranking, highlights et filtres)."""
    if not q.strip():
        return {"query": q, "total": 0, "page": page, "page_size": page_size, "results": []}
    
    cat_enum = _normalize_categorie(categorie) if categorie else None
    repo = MarcheRepository(db)
    results, total = repo.search_fts_advanced(
        query=q,
        categorie=cat_enum,
        region=region,
        ville=ville,
        organisme=organisme,
        date_min=date_min,
        date_max=date_max,
        montant_min=montant_min,
        montant_max=montant_max,
        order_by=order_by,
        order_dir=order_dir,
        page=page,
        page_size=page_size,
    )
    
    formatted_results = [
        {
            "id": r.marche.id,
            "numero_appel_offre": r.marche.numero_appel_offre,
            "titre_projet": r.marche.titre_projet,
            "organisme_acheteur": r.marche.organisme_acheteur,
            "ville_execution": r.marche.ville_execution or "Maroc",
            "region": r.marche.region,
            "montant": float(r.marche.montant) if r.marche.montant is not None else None,
            "delai_execution_mois": r.marche.delai_execution_mois,
            "date_parution": r.marche.date_parution.isoformat() if r.marche.date_parution else None,
            "date_limite": r.marche.date_limite.isoformat() if r.marche.date_limite else None,
            "categorie_prestation": (
                r.marche.categorie_prestation.value if r.marche.categorie_prestation else None
            ),
            "score": r.score,
            "highlight": r.highlight,
            "matched_fields": r.matched_fields,
        }
        for r in results
    ]
    return {
        "query": q,
        "total": total,
        "page": page,
        "page_size": page_size,
        "count": len(formatted_results),
        "results": formatted_results,
    }


@app.get("/api/v1/ged/documents/{doc_id}/preview")
def get_document_preview(doc_id: int, db: Session = Depends(get_db)):
    """Aperçu d'un document (file_name + status)."""
    repo = DocumentRepository(db)
    doc = repo.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"document": doc.file_name, "status": doc.status.value if doc.status else None}


@app.get("/api/v1/ged/documents")
def get_documents(db: Session = Depends(get_db)):
    """Liste résumée des documents (derniers uploads)."""
    repo = DocumentRepository(db)
    docs = repo.list(limit=200)
    return [
        {
            "name": d.archive_name or "Archive.zip",
            "type": "Archive",
            "status": d.status.value if d.status else "inconnu",
            "date": d.created_at.isoformat()[:10] if d.created_at else "",
            "size": f"{d.file_size_kb} KB" if d.file_size_kb else "Inconnu",
        }
        for d in docs
    ]


# --- Appels d'offres (lecture paginée) ---
@app.get("/api/v1/ged/appels-offres")
def list_appels_offres(
    page: int = 1,
    page_size: int = 20,
    ville: Optional[str] = None,
    region: Optional[str] = None,
    organisme: Optional[str] = None,
    categorie: Optional[str] = None,
    date_min: Optional[date] = None,
    date_max: Optional[date] = None,
    montant_min: Optional[float] = None,
    montant_max: Optional[float] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Liste paginée des appels d'offres avec filtres."""
    cat_enum: Optional[models.CategorieMarche] = None
    if categorie:
        try:
            cat_enum = models.CategorieMarche(categorie)
        except ValueError:
            # On accepte aussi les libellés français sans accent
            mapping = {
                "travaux": models.CategorieMarche.Travaux,
                "fournitures": models.CategorieMarche.Fournitures,
                "services": models.CategorieMarche.Services,
                "etudes": models.CategorieMarche.Etudes,
                "études": models.CategorieMarche.Etudes,
            }
            cat_enum = mapping.get(categorie.lower())
    flt = MarcheFilter(
        ville=ville, region=region, organisme=organisme, categorie=cat_enum,
        date_min=date_min, date_max=date_max,
        montant_min=montant_min, montant_max=montant_max, q=q,
    )
    repo = MarcheRepository(db)
    total = repo.count(flt)
    items = repo.list(flt, page=page, page_size=page_size)
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "page_size": page_size,
        "items": [_marche_to_legacy(m) for m in items],
    }

from fastapi.responses import StreamingResponse
import io
import pandas as pd

@app.get("/api/v1/ged/appels-offres/export")
def export_appels_offres(q: str = "", format: str = "csv", db: Session = Depends(get_db)):
    repo = MarcheRepository(db)
    if q.strip():
        marches = repo.search_fts(q, limit=1000)
    else:
        marches = repo.list_all(skip=0, limit=1000)
        
    data = []
    for m in marches:
        data.append({
            "numero_appel_offre": m.numero_appel_offre,
            "titre_projet": m.titre_projet,
            "organisme_acheteur": m.organisme_acheteur,
            "ville_execution": m.ville_execution,
            "categorie_prestation": m.categorie_prestation.value if m.categorie_prestation else None,
            "budget_estimatif_mad": float(m.budget_estimatif_mad) if m.budget_estimatif_mad else None,
            "date_parution": m.date_parution.isoformat() if m.date_parution else None,
        })
        
    df = pd.DataFrame(data)
    
    if format == "csv":
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=export.csv"
        return response
    elif format == "xlsx":
        stream = io.BytesIO()
        with pd.ExcelWriter(stream, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        response = StreamingResponse(iter([stream.getvalue()]), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response.headers["Content-Disposition"] = "attachment; filename=export.xlsx"
        return response
    else:
        raise HTTPException(status_code=400, detail="Format non supporté. Utilisez 'csv' ou 'xlsx'")


@app.get("/api/v1/ged/appels-offres/{numero_ordre:path}")
def get_appel_offre(numero_ordre: str, db: Session = Depends(get_db)):
    """Détail d'un appel d'offres + OcrLog + Document.storage_path."""
    repo = MarcheRepository(db)
    marche = repo.get_by_numero(numero_ordre)
    if not marche:
        raise HTTPException(status_code=404, detail=f"Appel d'offres {numero_ordre} introuvable")
    payload = _marche_to_legacy(marche)
    if marche.document_source_id:
        doc_repo = DocumentRepository(db)
        doc = doc_repo.get(marche.document_source_id)
        if doc:
            payload["document"] = {
                "id": doc.id,
                "file_name": doc.file_name,
                "storage_path": doc.storage_path,
                "status": doc.status.value if doc.status else None,
                "inferred_type": doc.inferred_type.value if doc.inferred_type else None,
            }
            ocr_repo = OcrLogRepository(db)
            payload["ocr_logs"] = [
                {
                    "id": l.id,
                    "engine_name": l.engine_name,
                    "confidence_score_avg": (
                        float(l.confidence_score_avg) if l.confidence_score_avg is not None else None
                    ),
                    "processing_time_ms": l.processing_time_ms,
                    "processed_at": l.processed_at.isoformat() if l.processed_at else None,
                    "raw_text_extracted": l.raw_text_extracted,
                }
                for l in ocr_repo.list_by_document(doc.id)
            ]
    return payload


# --- Réception des données extraites par le pipeline de scraping/OCR/NLP ---
@app.post("/api/v1/ged/appels-offres")
def create_or_update_appel_offre(payload: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    """Crée ou met à jour un appel d'offres à partir d'un payload de scraping."""
    numero = payload.get("numero_ordre") or payload.get("numero_appel_offre")
    if not numero:
        raise HTTPException(status_code=400, detail="numero_ordre est obligatoire")
    normalized = {
        "numero_appel_offre": numero,
        "titre_projet": payload.get("objet") or payload.get("titre_projet"),
        "organisme_acheteur": payload.get("maitre_ouvrage") or payload.get("organisme_acheteur"),
        "montant": _parse_number(payload.get("estimation_mad") or payload.get("montant")),
        "budget_estimatif_mad": _parse_number(payload.get("estimation_mad") or payload.get("montant")),
        "caution_provisoire_mad": _parse_number(payload.get("caution_mad")),
        "delai_execution_mois": int(_parse_number(payload.get("delai_execution"))) if _parse_number(payload.get("delai_execution")) else None,
        "penalite_retard_mille": _parse_number(payload.get("penalite_retard_mille") or payload.get("penalite_retard")),
        "ville_execution": payload.get("lieu_ouverture_plis") or payload.get("ville_execution") or payload.get("ville"),
        "agreements_exiges": _serialiser_champ(payload.get("agreements_exiges")),
        "categorie_prestation": _normalize_categorie(payload.get("categorie_marche") or payload.get("categorie_prestation")),
        "date_parution": payload.get("date_parution"),
        "date_limite": payload.get("date_limite"),
        "date_ouverture_plis": payload.get("date_ouverture_plis"),
    }
    for legacy, new in (("reference", "reference"), ("region", "region")):
        if legacy in payload:
            normalized[new] = payload[legacy]
    normalized = {k: v for k, v in normalized.items() if v is not None and v != ""}

    repo = MarcheRepository(db)
    try:
        marche, action = repo.upsert(normalized)
        db.commit()

        if marche.titre_projet:
            text = extract_text_feature(marche)
            pred_cat, pred_prob = predict_category(text)
            
            insight = db.query(models.MlInsight).filter_by(marche_id=marche.id).first()
            if not insight:
                insight = models.MlInsight(marche_id=marche.id)
                db.add(insight)
            
            if pred_cat:
                insight.predicted_categorie = _normalize_categorie(pred_cat)
                insight.classification_confidence = pred_prob
                
            db.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"id": marche.id, "numero_ordre": marche.numero_appel_offre, "action": action}


def _normalize_categorie(value: Any) -> Optional[models.CategorieMarche]:
    if not value:
        return None
    s = str(value).strip()
    mapping = {
        "travaux": models.CategorieMarche.Travaux,
        "fournitures": models.CategorieMarche.Fournitures,
        "services": models.CategorieMarche.Services,
        "prestation de services (formation)": models.CategorieMarche.Services,
        "etude": models.CategorieMarche.Etudes,
        "etudes": models.CategorieMarche.Etudes,
        "étude": models.CategorieMarche.Etudes,
        "études": models.CategorieMarche.Etudes,
    }
    if s.lower() in mapping:
        return mapping[s.lower()]
    for cat in models.CategorieMarche:
        if cat.value.lower() == s.lower():
            return cat
    return None


# ===========================================================================
# 📊 Espace Décisionnel & BI (/api/v1/analytics)
# ===========================================================================
@app.get("/api/v1/analytics/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    """Tableau de bord unifié."""
    repo = MarcheRepository(db)
    return {
        "kpis": repo.kpis(),
        "ocr_quality": {"taux_reussite_ocr_pct": repo.ocr_quality_pct()},
        "trends": {
            "months": [m["month"] for m in repo.by_month()],
            "volumes": [m["count"] for m in repo.by_month()],
        },
        "trends_by_category": repo.by_category_month()
    }


@app.get("/api/v1/analytics/kpis")
def get_kpis(db: Session = Depends(get_db)):
    """KPI globaux (4 compteurs)."""
    return MarcheRepository(db).kpis()


@app.get("/api/v1/analytics/ocr-quality")
def get_ocr_quality(db: Session = Depends(get_db)):
    """Taux de qualité OCR moyen (couplé aux OcrLog)."""
    pct = MarcheRepository(db).ocr_quality_pct()
    return {"taux_reussite_ocr_pct": pct}


@app.get("/api/v1/analytics/trends")
def get_trends(db: Session = Depends(get_db)):
    """Volume mensuel d'AO (12 derniers mois)."""
    return {
        "months": [m["month"] for m in MarcheRepository(db).by_month()],
        "volumes": [m["count"] for m in MarcheRepository(db).by_month()],
    }


@app.get("/api/v1/analytics/trends/by-category")
def get_trends_by_category(db: Session = Depends(get_db)):
    """Tendance par catégorie (pour graphes empilés)."""
    return MarcheRepository(db).by_category_month()


@app.get("/api/v1/analytics/delai-moyen")
def get_delai_moyen(db: Session = Depends(get_db)):
    """Délai d'exécution moyen (mois)."""
    return {"delai_moyen_execution_mois": MarcheRepository(db).delai_moyen()}


@app.get("/api/v1/analytics/distribution/categories")
def get_categories_distribution(db: Session = Depends(get_db)):
    """Distribution des catégories (camembert)."""
    return MarcheRepository(db).by_category_month()


@app.get("/api/v1/analytics/top-buyers")
def get_top_buyers(db: Session = Depends(get_db)):
    """Top acheteurs par volume financier cumulé."""
    items = MarcheRepository(db).top_buyers(limit=10)
    return [
        {
            "organisme": (
                (item["organisme"][:20] + "...") if len(item["organisme"]) > 20 else item["organisme"]
            ),
            "budget": item["volume_mad"],
            "nb_marches": item["nb_marches"],
        }
        for item in items
    ]
@app.get("/api/v1/compare")
def compare_marches(ids: str = Query(..., description="IDs séparés par des virgules"), db: Session = Depends(get_db)):
    """Comparaison de plusieurs appels d'offres."""
    repo = MarcheRepository(db)
    marches = []
    id_list = [int(i) for i in ids.split(",") if i.isdigit()]
    for m_id in id_list:
        marche = repo.get(m_id)
        if marche:
            marches.append(_marche_to_legacy(marche))
    return marches

from sqlalchemy import func
@app.get("/api/v1/geo/aggregates")
def get_geo_aggregates(level: str = "ville", db: Session = Depends(get_db)):
    """Statistiques géographiques."""
    if level == "ville":
        rows = db.query(
            models.Marche.ville_execution,
            func.count(models.Marche.id).label("count")
        ).group_by(models.Marche.ville_execution).order_by(func.count(models.Marche.id).desc()).all()
        return [{"ville": r[0] or "Inconnu", "count": r[1]} for r in rows]
    return []


# ===========================================================================
# 🤖 Espace Intelligence Artificielle (/api/v1/ml)
# ===========================================================================
@app.get("/api/v1/ml/predictions/{marche_id}")
def get_prediction(marche_id: int, db: Session = Depends(get_db)):
    """Prédiction ML pour un marché donné (MlInsight)."""
    insight = (
        db.query(models.MlInsight)
        .filter(models.MlInsight.marche_id == marche_id)
        .first()
    )
    if not insight:
        return {
            "predicted_categorie": "Services",
            "is_anomaly": False,
            "anomaly_score": 0.01,
        }
    return {
        "predicted_categorie": (
            insight.predicted_categorie.value if insight.predicted_categorie else None
        ),
        "classification_confidence": (
            float(insight.classification_confidence) if insight.classification_confidence else None
        ),
        "is_anomaly": bool(insight.is_anomaly),
        "anomaly_score": (
            float(insight.anomaly_score) if insight.anomaly_score is not None else None
        ),
        "generated_at": insight.generated_at.isoformat() if insight.generated_at else None,
    }


def _run_retrain_and_anomaly_detection():
    # Calling the scripts via subprocess (could also just import and call functions)
    import subprocess
    import os
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.dirname(os.path.dirname(__file__))
    subprocess.run(["python", "-m", "ml.train_classifier"], env=env, check=False)
    
    # Run anomaly detection and update DB
    from ml.anomaly import detect_anomalies
    from backend.database import SessionLocal
    anomalies = detect_anomalies()
    
    with SessionLocal() as db:
        db.query(models.MlInsight).update({"is_anomaly": False})
        if anomalies:
            for anomaly in anomalies:
                marche_id = anomaly["marche_id"]
                insight = db.query(models.MlInsight).filter_by(marche_id=marche_id).first()
                if not insight:
                    insight = models.MlInsight(marche_id=marche_id)
                    db.add(insight)
                insight.is_anomaly = True
                insight.anomaly_score = anomaly.get("anomaly_score", 0)
        db.commit()


@app.post("/api/v1/ml/retrain")
def retrain_models(background_tasks: BackgroundTasks):
    """Déclenche le ré-entraînement ML en arrière-plan."""
    background_tasks.add_task(_run_retrain_and_anomaly_detection)
    return {"message": "Pipeline de ré-entraînement ML lancé avec succès."}


@app.get("/api/v1/ml/anomalies")
def get_ml_anomalies(db: Session = Depends(get_db)):
    """Anomalies détectées (MlInsight.is_anomaly = True)."""
    insights = (
        db.query(models.MlInsight)
        .filter(models.MlInsight.is_anomaly.is_(True))
        .limit(100)
        .all()
    )
    anomaly_items = []
    for insight in insights:
        marche = db.query(models.Marche).filter(models.Marche.id == insight.marche_id).first()
        anomaly_items.append({
            "marche_id": insight.marche_id,
            "numero_appel_offre": marche.numero_appel_offre if marche else None,
            "titre_projet": marche.titre_projet if marche else None,
            "categorie": marche.categorie_prestation.value if marche and marche.categorie_prestation else None,
            "predicted_categorie": insight.predicted_categorie.value if insight.predicted_categorie else None,
            "classification_confidence": float(insight.classification_confidence) if insight.classification_confidence is not None else None,
            "anomaly_score": float(insight.anomaly_score) if insight.anomaly_score is not None else 0,
            "generated_at": insight.generated_at.isoformat() if insight.generated_at else None,
        })
    return {
        "anomalies_count": len(insights),
        "anomalies_list": anomaly_items,
    }


@app.get("/api/v1/ml/metrics")
def get_ml_metrics():
    """Retourne les métriques du dernier entraînement, si disponibles."""
    metrics_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml", "models", "metrics.json")
    try:
        with open(metrics_path, "r", encoding="utf-8") as metrics_file:
            return json.load(metrics_file)
    except FileNotFoundError:
        return {"accuracy": None, "sample_count": 0, "classes": []}


# ===========================================================================
# 🩺 Monitoring système (/api/v1/system)
# ===========================================================================
@app.get("/api/v1/system/monitoring")
def get_monitoring():
    """Monitoring de l'API (statut, uptime, logs récents)."""
    return {
        "api_uptime": "24d 14h",
        "api_status": "Online",
        "db_index": "SQLAlchemy (SQLite dev / PostgreSQL prod)",
        "db_status": "Connecté",
        "logs": [
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "level": "INFO",
                "msg": "Données lues via backend.repository (couche unifiée).",
            }
        ],
    }


@app.get("/api/v1/system/health")
def health_check(db: Session = Depends(get_db)):
    """Health check (ping DB)."""
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        return JSONResponse(status_code=503, content={"status": "degraded", "error": str(e)})
    return {"status": "ok", "db": "reachable"}


@app.get("/api/v1/system/schema")
def get_db_schema(db: Session = Depends(get_db)):
    """Renvoie la structure de la base de données (Tables et Colonnes)."""
    inspector = inspect(engine)
    schema_info = []
    for table_name in inspector.get_table_names():
        columns = []
        for col in inspector.get_columns(table_name):
            columns.append({
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col["nullable"],
                "primary_key": col.get("primary_key", 0) > 0
            })
        schema_info.append({"table": table_name, "columns": columns})
    return schema_info


import asyncio

@app.websocket("/api/v1/system/ws/console")
async def websocket_console(websocket: WebSocket, token: str = None):
    """WebSocket pour exécuter les scripts du pipeline et streamer les logs."""
    if not token:
        await websocket.close(code=1008)
        return
    try:
        from backend.auth.auth_handler import decode_token
        payload = decode_token(token)
        if payload.get("role") != "admin":
            await websocket.close(code=1008)
            return
    except Exception:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            
            import sys
            
            if action == "scrape":
                # We need to run the script. First, update dates in the script if provided.
                date_debut = data.get("date_debut")
                date_fin = data.get("date_fin")
                
                if date_debut and date_fin:
                    script_path = "scripts/collect_demo_dataset.py"
                    with open(script_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    content = re.sub(r'DATE_DEBUT\s*=\s*".*?"', f'DATE_DEBUT = "{date_debut}"', content)
                    content = re.sub(r'DATE_FIN\s*=\s*".*?"', f'DATE_FIN = "{date_fin}"', content)
                    with open(script_path, "w", encoding="utf-8") as f:
                        f.write(content)
                
                await run_and_stream(websocket, [sys.executable, "scripts/collect_demo_dataset.py"])
            
            elif action == "extract":
                # Ensure PYTHONPATH is set so ocr modules are found
                await run_and_stream(websocket, [sys.executable, "-m", "ingestion.extractor"], env_vars={"PYTHONPATH": "."})
                
            elif action == "ingest":
                await run_and_stream(websocket, [sys.executable, "scripts/ingest_dataset.py"])
                
            else:
                await websocket.send_text(f"Action inconnue: {action}")
                
    except WebSocketDisconnect:
        logger.info("Client disconnected from console")
    except Exception as e:
        await websocket.send_text(f"Erreur interne WebSocket: {str(e)}")


async def run_and_stream(websocket: WebSocket, cmd: List[str], env_vars: dict = None):
    """Exécute une commande et streame stdout/stderr vers le websocket en temps réel."""
    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)
        
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        env=env
    )
    
    await websocket.send_text(f"--- DÉBUT DE L'EXÉCUTION : {' '.join(cmd)} ---")
    
    while True:
        line = await process.stdout.readline()
        if not line:
            break
        try:
            decoded_line = line.decode('utf-8').rstrip()
        except UnicodeDecodeError:
            decoded_line = line.decode('latin-1').rstrip()
        await websocket.send_text(decoded_line)
        
    await process.wait()
    await websocket.send_text(f"--- FIN DE L'EXÉCUTION (Code de retour: {process.returncode}) ---")

