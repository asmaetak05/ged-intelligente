import logging
from sqlalchemy.orm import Session
from datetime import datetime
import json
import urllib.request
import os

from . import models
from ingestion.extractor import process_archive
from .database import SessionLocal

def process_document_async(document_id: int, file_path: str, db: Session = None):
    db_close = False
    if db is None:
        db = SessionLocal()
        db_close = True
    try:
        doc = db.query(models.Document).filter(models.Document.id == document_id).first()
        if not doc:
            return

        # Déduplication et Cache OCR au niveau document (OC-01)
        if doc.checksum_sha256:
            cached_doc = db.query(models.Document).filter(
                models.Document.checksum_sha256 == doc.checksum_sha256,
                models.Document.status == models.DocStatus.ocr_processed,
                models.Document.id != doc.id
            ).first()
            if cached_doc:
                logging.info(f"[{doc.id}] Cache OCR document touché! Copie des extractions depuis le document ID {cached_doc.id}")
                
                # Copier OcrLog
                old_ocr_log = db.query(models.OcrLog).filter(models.OcrLog.document_id == cached_doc.id).first()
                if old_ocr_log:
                    ocr_log = models.OcrLog(
                        document_id=doc.id,
                        engine_name=old_ocr_log.engine_name,
                        confidence_score_avg=old_ocr_log.confidence_score_avg
                    )
                    db.add(ocr_log)
                
                # Copier Extractions
                old_exts = db.query(models.ExtractionNlp).filter(models.ExtractionNlp.document_id == cached_doc.id).all()
                for old_ext in old_exts:
                    ext = models.ExtractionNlp(
                        document_id=doc.id,
                        field_name=old_ext.field_name,
                        value=old_ext.value,
                        source=old_ext.source,
                        score=old_ext.score,
                        snippet=old_ext.snippet
                    )
                    db.add(ext)
                
                # Lier à un marché existant si présent
                old_marche = db.query(models.Marche).filter(models.Marche.document_source_id == cached_doc.id).first()
                if old_marche:
                    old_marche.document_source_id = doc.id
                
                doc.status = models.DocStatus.ocr_processed
                db.commit()
                return

        doc.status = models.DocStatus.extracted
        db.commit()

        # Run extraction
        ok, payload, raw_fields = process_archive(file_path)
        
        if not ok:
            doc.status = models.DocStatus.failed
            db.commit()
            return

        # Add OcrLog
        confidence = 0.85 # Heuristic for now
        ocr_log = models.OcrLog(
            document_id=document_id,
            engine_name="Pipeline OCR+NLP",
            confidence_score_avg=confidence * 100
        )
        db.add(ocr_log)

        # Add ExtractionNlp
        if raw_fields and "fields" in raw_fields:
            for field, data in raw_fields["fields"].items():
                ext = models.ExtractionNlp(
                    document_id=document_id,
                    field_name=field,
                    value=str(data["value"]) if data["value"] else None,
                    source=data["source"],
                    score=data["score"],
                    snippet=data["snippet"]
                )
                db.add(ext)

        db.commit()

        # Send to API to create/update Marche
        if payload:
            try:
                from backend.main import create_or_update_appel_offre
                res = create_or_update_appel_offre(payload, db)
                marche_id = res.get("id")
                if marche_id:
                    # Link document to marche
                    marche = db.query(models.Marche).filter(models.Marche.id == marche_id).first()
                    if marche:
                        marche.document_source_id = document_id
            except Exception as e:
                logging.error(f"Error creating marche: {e}")

        doc.status = models.DocStatus.ocr_processed
        db.commit()

    except Exception as e:
        logging.error(f"Error in process_document_async: {e}")
        doc = db.query(models.Document).filter(models.Document.id == document_id).first()
        if doc:
            doc.status = models.DocStatus.failed
            db.commit()
    finally:
        if db_close:
            db.close()
