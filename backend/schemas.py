from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ExtractionNLPBase(BaseModel):
    champ_extrait: str
    valeur_extraite: str
    confiance_ia: Optional[float] = None

class ExtractionNLPCreate(ExtractionNLPBase):
    pass

class ExtractionNLPResponse(ExtractionNLPBase):
    id: int
    date_traitement: datetime
    class Config:
        from_attributes = True

class DocumentAOBase(BaseModel):
    nom_fichier: str
    type_document: Optional[str] = None
    chemin_sauvegarde: Optional[str] = None
    contenu_brut: Optional[str] = None
    est_scanne: Optional[bool] = False

class DocumentAOCreate(DocumentAOBase):
    extractions: List[ExtractionNLPCreate] = []

class DocumentAOResponse(DocumentAOBase):
    id: int
    date_extraction: datetime
    extractions: List[ExtractionNLPResponse] = []
    class Config:
        from_attributes = True

class AppelOffreBase(BaseModel):
    numero_ordre: Optional[str] = None
    objet: Optional[str] = None
    maitre_ouvrage: Optional[str] = None
    estimation_mad: Optional[str] = None
    caution_mad: Optional[str] = None
    dossier_zip_source: Optional[str] = None
    delai_execution: Optional[str] = None
    penalite_retard: Optional[str] = None
    caution_definitive: Optional[str] = None
    retenue_garantie: Optional[str] = None
    agrements_exiges: Optional[str] = None
    profils_exiges: Optional[str] = None
    methode_notation: Optional[str] = None
    date_ouverture_plis: Optional[str] = None
    lieu_ouverture_plis: Optional[str] = None
    categorie_marche: Optional[str] = None

class AppelOffreCreate(AppelOffreBase):
    pass

class AppelOffreResponse(AppelOffreBase):
    id: int
    date_ingestion: datetime
    documents: List[DocumentAOResponse] = []
    class Config:
        from_attributes = True
