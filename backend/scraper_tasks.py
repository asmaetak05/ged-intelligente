import logging
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import time

from backend.database import SessionLocal
from backend.models import Source

def run_scraper_async(source_id: int, dry_run: bool = False):
    """
    Tâche asynchrone pour le scraper.
    """
    db = SessionLocal()
    try:
        source = db.query(Source).filter(Source.id == source_id).first()
        if not source:
            logging.error(f"Source {source_id} introuvable.")
            return

        logging.info(f"Démarrage du scraper pour la source {source.name} (dry_run={dry_run})")
        # Simuler un temps de scraping
        time.sleep(2)
        
        if not dry_run:
            source.last_scrape_at = datetime.now(timezone.utc)
            db.commit()
            logging.info("Scraping terminé, last_scrape_at mis à jour.")
        else:
            logging.info("Scraping terminé en mode prévisualisation. Aucune donnée n'a été modifiée.")
            
    except Exception as e:
        logging.error(f"Erreur durant le scraping : {e}")
    finally:
        db.close()
