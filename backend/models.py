from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
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
    reference = Column(String(100), nullable=True, index=True)
    titre_projet = Column(Text, nullable=False)
    organisme_acheteur = Column(String(255), nullable=False)
    categorie_prestation = Column(SQLEnum(CategorieMarche), nullable=True)

    # --- Volet financier ---
    montant = Column(Numeric(15, 2), nullable=True, index=True)
    budget_estimatif_mad = Column(Numeric(15, 2), nullable=True, index=True)
    caution_provisoire_mad = Column(Numeric(15, 2), nullable=True)
    caution_definitive_pct = Column(Numeric(4, 2), default=3.00)

    # --- Volet délais ---
    delai_execution_mois = Column(Integer, nullable=True)
    penalite_retard_mille = Column(Numeric(4, 2), default=1.00)
    date_parution = Column(Date, nullable=True, index=True)
    date_publication = Column(Date, nullable=True)
    date_limite = Column(Date, nullable=True, index=True)
    date_limite_depot = Column(DateTime, nullable=True, index=True)

    # --- Volet géographique ---
    ville_execution = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True, index=True)

    # --- Volet technique ---
    # ARRAY(String) n'est pas portable SQLite ; on utilise JSON (list[str] sérialisée).
    agreements_exiges = Column(JSON, nullable=True)
    seuil_technique_elimination = Column(Numeric(5, 2), nullable=True)

    # --- Indexation FTS : TSVECTOR est PostgreSQL-only ; on conserve un Text
    # --- qui sera peuplé/maintenu côté application. Le GIN index est ajouté
    # --- uniquement côté PostgreSQL via une migration Alembic dédiée.
    tsv_search = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document_source = relationship("Document", back_populates="marches")
    criteres_humains = relationship("CritereHumain", back_populates="marche", cascade="all, delete-orphan")
    ml_insights = relationship("MlInsight", back_populates="marche", cascade="all, delete-orphan")

    __table_args__ = (
        # Index simple portable SQLite + PostgreSQL. Le GIN/tsvector ne sera
        # ajouté que dans une migration Alembic conditionnelle au dialecte.
        Index('idx_marches_tsv', 'tsv_search'),
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

class ExtractionNlp(Base):
    __tablename__ = "extractions_nlp"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    field_name = Column(String(100), nullable=False)
    value = Column(Text, nullable=True)
    source = Column(String(50), nullable=True)
    score = Column(Numeric(5, 4), nullable=True)
    snippet = Column(Text, nullable=True)
    extracted_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("Document", backref="extractions")
