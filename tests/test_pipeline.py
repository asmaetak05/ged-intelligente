import pytest
import os
from backend.tasks import process_document_async
from backend import models

@pytest.fixture
def sample_zip_path():
    return os.path.abspath("tests/fixtures/sample_ao.zip")

def test_pipeline_runs_in_background(db_session, sample_zip_path):
    # Prepare dummy document
    doc = models.Document(
        archive_name="sample_ao.zip",
        file_name="sample_ao.zip",
        extension="zip",
        storage_path=sample_zip_path,
        status=models.DocStatus.raw_zip
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)
    
    # We test the background task logic directly
    process_document_async(doc.id, sample_zip_path, db_session)
    
    db_session.refresh(doc)
    
    # Check if doc status updated
    assert doc.status == models.DocStatus.ocr_processed

    # Check if OcrLog created
    ocr_log = db_session.query(models.OcrLog).filter(models.OcrLog.document_id == doc.id).first()
    assert ocr_log is not None
    assert float(ocr_log.confidence_score_avg) > 0

    # Check extractions
    exts = db_session.query(models.ExtractionNlp).filter(models.ExtractionNlp.document_id == doc.id).all()
    assert len(exts) > 0

def test_upload_creates_document(client, sample_zip_path):
    with open(sample_zip_path, "rb") as f:
        response = client.post("/api/v1/ged/documents/upload", files={"file": ("sample_ao.zip", f, "application/zip")})
    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    assert data["status"] == "queued"

def test_upload_corrupt_zip(client, tmp_path):
    corrupt_zip = tmp_path / "corrupt.zip"
    corrupt_zip.write_text("This is not a zip file")
    
    with open(corrupt_zip, "rb") as f:
        response = client.post("/api/v1/ged/documents/upload", files={"file": ("corrupt.zip", f, "application/zip")})
    assert response.status_code == 200
    doc_id = response.json()["document_id"]
    
    # Process it synchronously for testing
    from backend.tasks import process_document_async
    from backend.database import SessionLocal
    
    with SessionLocal() as db:
        process_document_async(doc_id, str(corrupt_zip), db)
        db.commit()
        
        doc = db.query(models.Document).filter_by(id=doc_id).first()
        assert doc.status == models.DocStatus.failed
