from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean, Enum as SQLEnum, Numeric, Date, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TSVECTOR, ARRAY
from .database import Base
import enum

class DocStatus(str, enum.Enum):
    raw_zip = 'raw_zip'
    extracted = 'extracted'
    ocr_processed = 'ocr_processed'
    failed = 'failed'

class DocType(str, enum.Enum):
    Avis = 'Avis'
    CPS = 'CPS'
    RC = 'RC'
    Engagement = 'Engagement'
    Formulaire = 'Formulaire'
    Inconnu = 'Inconnu'

class CategorieMarche(str, enum.Enum):
    Travaux = 'Travaux'
    Fournitures = 'Fournitures'
    Services = 'Services'
    Etudes = 'Études'

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    archive_name = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    extension = Column(String(10), nullable=False)
    storage_path = Column(Text, nullable=False)
    inferred_type = Column(SQLEnum(DocType), default=DocType.Inconnu)
    status = Column(SQLEnum(DocStatus), default=DocStatus.raw_zip)
    file_size_kb = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    marches = relationship("Marche", back_populates="document_source")
    ocr_logs = relationship("OcrLog", back_populates="document", cascade="all, delete-orphan")

class Marche(Base):
    __tablename__ = "marches"

    id = Column(Integer, primary_key=True, index=True)
    document_source_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    numero_appel_offre = Column(String(50), unique=True, nullable=False, index=True)
    titre_projet = Column(Text, nullable=False)
    organisme_acheteur = Column(String(255), nullable=False)
    categorie_prestation = Column(SQLEnum(CategorieMarche), nullable=True)
    
    budget_estimatif_mad = Column(Numeric(15, 2), nullable=True, index=True)
    caution_provisoire_mad = Column(Numeric(15, 2), nullable=True)
    caution_definitive_pct = Column(Numeric(4, 2), default=3.00)
    delai_execution_mois = Column(Integer, nullable=True)
    penalite_retard_mille = Column(Numeric(4, 2), default=1.00)
    
    date_publication = Column(Date, nullable=True)
    date_limite_depot = Column(DateTime, nullable=True, index=True)
    ville_execution = Column(String(100), nullable=True)
    
    agreements_exiges = Column(ARRAY(String(50)), nullable=True)
    seuil_technique_elimination = Column(Numeric(5,2), nullable=True)
    
    tsv_search = Column(TSVECTOR, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document_source = relationship("Document", back_populates="marches")
    criteres_humains = relationship("CritereHumain", back_populates="marche", cascade="all, delete-orphan")
    ml_insights = relationship("MlInsight", back_populates="marche", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_marches_tsv', 'tsv_search', postgresql_using='gin'),
    )

class OcrLog(Base):
    __tablename__ = "ocr_logs"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    engine_name = Column(String(50), default='Tesseract 5')
    raw_text_extracted = Column(Text, nullable=True)
    confidence_score_avg = Column(Numeric(5, 2), nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    processed_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("Document", back_populates="ocr_logs")

class CritereHumain(Base):
    __tablename__ = "criteres_humains"

    id = Column(Integer, primary_key=True, index=True)
    marche_id = Column(Integer, ForeignKey("marches.id", ondelete="CASCADE"), nullable=False)
    profil_poste = Column(String(150), nullable=False)
    points_attribues = Column(Integer, nullable=True)
    experience_minimale_ans = Column(Integer, nullable=True)
    inscription_ordre_requise = Column(Boolean, default=False)

    marche = relationship("Marche", back_populates="criteres_humains")

class MlInsight(Base):
    __tablename__ = "ml_insights"

    id = Column(Integer, primary_key=True, index=True)
    marche_id = Column(Integer, ForeignKey("marches.id", ondelete="CASCADE"), nullable=False)
    predicted_categorie = Column(SQLEnum(CategorieMarche), nullable=True)
    classification_confidence = Column(Numeric(5, 4), nullable=True)
    is_anomaly = Column(Boolean, default=False)
    anomaly_score = Column(Numeric(5, 4), nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    marche = relationship("Marche", back_populates="ml_insights")
