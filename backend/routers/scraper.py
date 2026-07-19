from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import uuid

from backend.database import get_db
from backend.models import Source
from backend.auth.rbac import RequireRole
from backend.scraper_tasks import run_scraper_async

router = APIRouter(prefix="/api/v1/scraper", tags=["scraper"])

class RunResponse(BaseModel):
    message: str
    job_id: str
    dry_run: bool

@router.post("/run", response_model=RunResponse)
def run_scraper(
    background_tasks: BackgroundTasks, 
    source_id: int = Query(...), 
    dry_run: bool = Query(False),
    db: Session = Depends(get_db), 
    current_user = Depends(RequireRole(["admin", "analyst"]))
):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source introuvable")
        
    job_id = str(uuid.uuid4())
    background_tasks.add_task(run_scraper_async, source.id, dry_run)
    
    return RunResponse(
        message=f"Scraping asynchrone démarré pour {source.name}", 
        job_id=job_id,
        dry_run=dry_run
    )
