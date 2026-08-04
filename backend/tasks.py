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
                        source_extractor=old_ext.source_extractor,
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

        # Initialiser ou récupérer OcrLog (OC-04)
        ocr_log = db.query(models.OcrLog).filter(models.OcrLog.document_id == document_id).first()
        if not ocr_log:
            ocr_log = models.OcrLog(
                document_id=document_id,
                engine_name="Pipeline OCR+NLP",
                confidence_score_avg=85.0,
                last_processed_page=0,
                total_pages=None
            )
            db.add(ocr_log)
            db.commit()
            db.refresh(ocr_log)

        # Reprise OCR par lot de 10 pages (OC-04)
        chunk_size = 10
        total_pages = ocr_log.total_pages or 1
        start_page = (ocr_log.last_processed_page or 0) + 1
        if start_page > total_pages:
            start_page = 1
        
        ok = False
        payload = None
        raw_fields = None
        
        while start_page <= total_pages:
            end_page = start_page + chunk_size - 1
            logging.info(f"[{doc.id}] Traitement des pages {start_page} à {end_page}...")
            
            ok, payload, raw_fields, total_pages_pdf = process_archive(file_path, start_page=start_page, end_page=end_page)
            
            if total_pages_pdf > 0:
                total_pages = total_pages_pdf
                ocr_log.total_pages = total_pages
                
            if not ok or end_page >= total_pages or start_page >= total_pages:
                ocr_log.last_processed_page = total_pages
                db.commit()
                break
                
            ocr_log.last_processed_page = min(end_page, total_pages)
            db.commit()
            start_page += chunk_size

        if not ok:
            doc.status = models.DocStatus.failed
            db.commit()
            return

        # Add or Update ExtractionNlp
        if raw_fields and "fields" in raw_fields:
            for field, data in raw_fields["fields"].items():
                ext = db.query(models.ExtractionNlp).filter(
                    models.ExtractionNlp.document_id == document_id,
                    models.ExtractionNlp.field_name == field
                ).first()
                if ext:
                    ext.value = str(data["value"]) if data["value"] else None
                    ext.source_extractor = data["source"]
                    ext.score = data["score"]
                    ext.snippet = data["snippet"]
                else:
                    ext = models.ExtractionNlp(
                        document_id=document_id,
                        field_name=field,
                        value=str(data["value"]) if data["value"] else None,
                        source_extractor=data["source"],
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

        if raw_fields and "low_quality" in raw_fields:
            doc.low_quality = raw_fields["low_quality"]

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
