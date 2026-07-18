import numpy as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from backend.models import Marche
from backend.database import DATABASE_URL

def detect_anomalies(db_url=DATABASE_URL):
    """Run an Isolation Forest to detect anomalies on numeric fields."""
    eng = create_engine(db_url)
    with Session(eng) as session:
        marches = session.query(Marche).all()
        
    if len(marches) < 5:
        return []
        
    data = []
    ids = []
    for m in marches:
        # Default numeric values if null to avoid NaN
        montant = float(m.montant) if m.montant else 0.0
        delai = float(m.delai_execution_mois) if m.delai_execution_mois else 0.0
        caution = float(m.caution_provisoire_mad) if m.caution_provisoire_mad else 0.0
        
        data.append([montant, delai, caution])
        ids.append(m.id)
        
    X = np.array(data)
    
    # 5% contamination
    clf = IsolationForest(random_state=42, contamination=0.05)
    preds = clf.fit_predict(X)
    
    # preds: -1 for anomalies, 1 for normal
    anomalies = []
    for i, p in enumerate(preds):
        if p == -1:
            anomalies.append(ids[i])
            
    return anomalies
