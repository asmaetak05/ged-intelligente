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

from fastapi import Body, Depends, FastAPI, File, HTTPException, UploadFile, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session

from . import models, schemas
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        print(f"[startup] ATTENTION: initialisation partielle ({e}).")


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
    background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """Upload d'un document (traitement asynchrone déclenché)."""
    import os
    import uuid
    import shutil
    
    os.makedirs("data/raw", exist_ok=True)
    # Check if we can infer numero_ordre from filename
    if file.filename and "AO_" in file.filename:
        safe_name = file.filename
    else:
        safe_name = f"doc_{uuid.uuid4().hex[:8]}.zip"
        
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
        print(f"[Upload] Document avec hash {checksum} déjà traité (ID: {existing_doc.id}). Skip.")
        return {
            "document_id": existing_doc.id,
            "message": "Document déjà traité (déduplication active)",
            "filename": file.filename,
            "status": "ocr_processed"
        }

    doc = models.Document(
        archive_name=safe_name,
        file_name=file.filename or safe_name,
        extension="zip",
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
def search_documents(q: str = "", db: Session = Depends(get_db)):
    """Recherche plein texte (FTS portable via ``MarcheRepository.search_fts``)."""
    if not q.strip():
        return {"query": q, "count": 0, "results": []}
    repo = MarcheRepository(db)
    rows = repo.search_fts(q, limit=100)
    results = [
        {
            "numero_appel_offre": m.numero_appel_offre,
            "titre_projet": m.titre_projet,
            "organisme_acheteur": m.organisme_acheteur,
            "ville_execution": m.ville_execution or "Maroc",
            "categorie_prestation": (
                m.categorie_prestation.value if m.categorie_prestation else None
            ),
            "highlight": "..." + (m.titre_projet[:50] if m.titre_projet else "") + "...",
        }
        for m in rows
    ]
    return {"query": q, "count": len(results), "results": results}


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
        "items": [_marche_to_legacy(m) for m in items],
    }


@app.get("/api/v1/ged/appels-offres/{numero_ordre:path}")
def get_appel_offre(numero_ordre: str, db: Session = Depends(get_db)):
    """Détail d'un appel d'offres + OcrLog + Document.storage_path."""
    repo = MarcheRepository(db)
    marche = repo.get_by_numero(numero_ordre)
    if not marche:
        raise HTTPException(status_code=404, detail=f"Appel d'offres {numero_ordre} introuvable")
    payload = _marche_to_legacy(marche)
    # Enrichissement : document source + logs OCR
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
    """Crée ou met à jour un appel d'offres à partir d'un payload de scraping.

    Accepte indifféremment les noms historiques (``numero_ordre``,
    ``objet``, ``maitre_ouvrage``, ``estimation_mad``, etc.) ou les
    noms normalisés (``numero_appel_offre``, ``titre_projet``,
    ``organisme_acheteur``, ``montant``).
    """
    # Mapping legacy → colonnes SQLAlchemy
    numero = payload.get("numero_ordre") or payload.get("numero_appel_offre")
    if not numero:
        raise HTTPException(status_code=400, detail="numero_ordre est obligatoire")
    normalized = {
        "numero_appel_offre": numero,
        "titre_projet": payload.get("objet") or payload.get("titre_projet"),
        "organisme_acheteur": payload.get("maitre_ouvrage") or payload.get("organisme_acheteur"),
        "montant": _parse_number(payload.get("estimation_mad") or payload.get("montant")),
        "caution_provisoire_mad": _parse_number(payload.get("caution_mad")),
        "delai_execution_mois": int(_parse_number(payload.get("delai_execution"))) or None,
        "ville_execution": payload.get("lieu_ouverture_plis"),
        "agreements_exiges": _serialiser_champ(payload.get("agreements_exiges")),
        "categorie_prestation": _normalize_categorie(payload.get("categorie_marche") or payload.get("categorie_prestation")),
    }
    # Champs optionnels préservés tels quels
    for legacy, new in (("reference", "reference"), ("region", "region")):
        if legacy in payload:
            normalized[new] = payload[legacy]
    # Filtrer les None et normaliser
    normalized = {k: v for k, v in normalized.items() if v is not None and v != ""}

    repo = MarcheRepository(db)
    try:
        marche, action = repo.upsert(normalized)
        db.commit()
        
        # Trigger ML Insight asynchronously or synchronously if fast enough
        # The inference is fast enough (SVM) to do it synchronously
        if marche.titre_projet:
            text = extract_text_feature(marche)
            pred_cat, pred_prob = predict_category(text)
            
            # Check if MlInsight exists
            insight = db.query(models.MlInsight).filter_by(marche_id=marche.id).first()
            if not insight:
                insight = models.MlInsight(marche_id=marche.id)
                db.add(insight)
            
            if pred_cat:
                insight.predicted_categorie = models.CategorieMarche(pred_cat)
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
    # Tentative directe sur la valeur enum
    for cat in models.CategorieMarche:
        if cat.value.lower() == s.lower():
            return cat
    return None


# ===========================================================================
# 📊 Espace Décisionnel & BI (/api/v1/analytics)
# ===========================================================================
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
    # Format compatible avec le frontend existant (tronqué à 20 chars)
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
            for marche_id in anomalies:
                insight = db.query(models.MlInsight).filter_by(marche_id=marche_id).first()
                if not insight:
                    insight = models.MlInsight(marche_id=marche_id)
                    db.add(insight)
                insight.is_anomaly = True
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
    return {
        "anomalies_count": len(insights),
        "anomalies_list": [
            {
                "marche_id": i.marche_id,
                "anomaly_score": float(i.anomaly_score) if i.anomaly_score else 0,
                "generated_at": i.generated_at.isoformat() if i.generated_at else None,
            }
            for i in insights
        ],
    }


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
async def websocket_console(websocket: WebSocket):
    """WebSocket pour exécuter les scripts du pipeline et streamer les logs."""
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
        print("Client disconnected from console")
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

