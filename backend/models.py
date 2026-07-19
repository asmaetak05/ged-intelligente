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
    Table,
    CheckConstraint
)
from sqlalchemy.orm import relationship, declared_attr
from sqlalchemy.sql import func
from .database import Base
import enum

# --- Enums Exists ---
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

# --- Mixins ---
class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

# --- Reference Tables ---
class TypeAvis(Base):
    __tablename__ = "type_avis"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    label = Column(String(255), nullable=False)

class TypeProcedure(Base):
    __tablename__ = "type_procedure"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    label = Column(String(255), nullable=False)

class EtatAvis(Base):
    __tablename__ = "etat_avis"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    label = Column(String(255), nullable=False)

class Direction(Base):
    __tablename__ = "direction"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type_dir = Column(String(50), nullable=True)
    parent_id = Column(Integer, ForeignKey("direction.id", ondelete="CASCADE"), nullable=True)
    
    parent = relationship("Direction", remote_side=[id], backref="children")

class Source(Base):
    __tablename__ = "source"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    base_url = Column(String(255), nullable=True)
    scraper_class = Column(String(100), nullable=True)
    schedule_cron = Column(String(50), nullable=True)
    selectors_json = Column(JSON, nullable=True)
    last_scrape_at = Column(DateTime(timezone=True), nullable=True)

class Ville(Base):
    __tablename__ = "ville"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    province = Column(String(255), nullable=True)
    region = Column(String(255), nullable=True)
    lat = Column(Numeric(9, 6), nullable=True)
    lon = Column(Numeric(9, 6), nullable=True)

class Qualification(Base):
    __tablename__ = "qualification"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    label = Column(String(255), nullable=False)
    classe = Column(String(50), nullable=True)
    categorie = Column(String(100), nullable=True)

class Agrement(Base):
    __tablename__ = "agrement"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    label = Column(String(255), nullable=False)
    type_agrement = Column(String(100), nullable=True)

# --- RBAC Tables ---
user_role_table = Table(
    "user_role",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
)

role_permission_table = Table(
    "role_permission",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
)

class Role(Base, TimestampMixin):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    
    users = relationship("User", secondary=user_role_table, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permission_table, back_populates="roles")

class Permission(Base, TimestampMixin):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    
    roles = relationship("Role", secondary=role_permission_table, back_populates="permissions")

class User(Base, TimestampMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    mfa_secret = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    roles = relationship("Role", secondary=user_role_table, back_populates="users")

# --- M:N Associations for Marche ---
marche_qualification_table = Table(
    "marche_qualification",
    Base.metadata,
    Column("marche_id", Integer, ForeignKey("marches.id", ondelete="CASCADE"), primary_key=True),
    Column("qualification_id", Integer, ForeignKey("qualification.id", ondelete="CASCADE"), primary_key=True)
)

marche_agrement_table = Table(
    "marche_agrement",
    Base.metadata,
    Column("marche_id", Integer, ForeignKey("marches.id", ondelete="CASCADE"), primary_key=True),
    Column("agrement_id", Integer, ForeignKey("agrement.id", ondelete="CASCADE"), primary_key=True)
)

# --- Main Entities ---
class Document(Base, TimestampMixin):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    archive_name = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    extension = Column(String(10), nullable=False)
    storage_path = Column(Text, nullable=False)
    storage_uri = Column(String(512), nullable=True) # e.g., s3://bucket/path
    checksum_sha256 = Column(String(64), nullable=True, index=True)
    inferred_type = Column(SQLEnum(DocType), default=DocType.Inconnu)
    status = Column(SQLEnum(DocStatus), default=DocStatus.raw_zip)
    file_size_kb = Column(Integer, nullable=True)
    low_quality = Column(Boolean, server_default='0', nullable=False)
    
    marches = relationship("Marche", back_populates="document_source")
    ocr_logs = relationship("OcrLog", back_populates="document", cascade="all, delete-orphan")
    extractions = relationship("ExtractionNlp", back_populates="document", cascade="all, delete-orphan")

class VersionHistory(Base):
    __tablename__ = "version_history"
    id = Column(Integer, primary_key=True, index=True)
    marche_id = Column(Integer, ForeignKey("marches.id", ondelete="CASCADE"), nullable=False)
    checksum_sha256 = Column(String(64), nullable=False)
    file_uri = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    marche = relationship("Marche", backref="versions")

class Marche(Base, TimestampMixin):
    __tablename__ = "marches"
    id = Column(Integer, primary_key=True, index=True)
    document_source_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    
    numero_appel_offre = Column(String(50), unique=True, nullable=False, index=True)
    reference = Column(String(100), nullable=True, index=True)
    titre_projet = Column(Text, nullable=False)
    organisme_acheteur = Column(String(255), nullable=False)
    categorie_prestation = Column(SQLEnum(CategorieMarche), nullable=True)
    
    # Nouvelles colonnes liées au formulaire
    typeavis_id = Column(Integer, ForeignKey("type_avis.id", ondelete="SET NULL"), nullable=True)
    procedure_id = Column(Integer, ForeignKey("type_procedure.id", ondelete="SET NULL"), nullable=True)
    etat_id = Column(Integer, ForeignKey("etat_avis.id", ondelete="SET NULL"), nullable=True)
    date_ouverture_plis = Column(DateTime, nullable=True)
    langue = Column(String(5), nullable=True)
    province_nom = Column(String(100), nullable=True)
    direction_id = Column(Integer, ForeignKey("direction.id", ondelete="SET NULL"), nullable=True)
    modele_reference = Column(String(50), nullable=True)
    low_quality = Column(Boolean, default=False)
    
    source_id = Column(Integer, ForeignKey("source.id", ondelete="SET NULL"), nullable=True)
    ville_id = Column(Integer, ForeignKey("ville.id", ondelete="SET NULL"), nullable=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

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

    # --- Volet géographique (legacy kept for compat, but overridden by ville_id) ---
    ville_execution = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True, index=True)

    # --- Volet technique ---
    agreements_exiges = Column(JSON, nullable=True) # Legacy array of strings
    seuil_technique_elimination = Column(Numeric(5, 2), nullable=True)

    # FTS
    tsv_search = Column(Text, nullable=True)

    # Relationships
    document_source = relationship("Document", back_populates="marches")
    criteres_humains = relationship("CritereHumain", back_populates="marche", cascade="all, delete-orphan")
    ml_insights = relationship("MlInsight", back_populates="marche", cascade="all, delete-orphan")
    
    type_avis = relationship("TypeAvis")
    type_procedure = relationship("TypeProcedure")
    etat_avis = relationship("EtatAvis")
    direction = relationship("Direction")
    source = relationship("Source")
    ville = relationship("Ville")
    created_by = relationship("User")
    
    qualifications = relationship("Qualification", secondary=marche_qualification_table)
    agrements = relationship("Agrement", secondary=marche_agrement_table)

    __table_args__ = (
        Index('idx_marches_tsv', 'tsv_search'),
        CheckConstraint("length(numero_appel_offre) > 0", name="chk_numero_appel_offre_len"),
        CheckConstraint("langue IN ('FR', 'AR', 'BI')", name="chk_langue_enum"),
    )

class OcrLog(Base, TimestampMixin):
    __tablename__ = "ocr_logs"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    engine_name = Column(String(50), default='Tesseract 5')
    raw_text_extracted = Column(Text, nullable=True)
    confidence_score_avg = Column(Numeric(5, 2), nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    last_processed_page = Column(Integer, default=0)
    total_pages = Column(Integer, nullable=True)
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

class MlInsight(Base, TimestampMixin):
    __tablename__ = "ml_insights"
    id = Column(Integer, primary_key=True, index=True)
    marche_id = Column(Integer, ForeignKey("marches.id", ondelete="CASCADE"), nullable=False)
    predicted_categorie = Column(SQLEnum(CategorieMarche), nullable=True)
    classification_confidence = Column(Numeric(5, 4), nullable=True)
    is_anomaly = Column(Boolean, default=False)
    anomaly_score = Column(Numeric(5, 4), nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    marche = relationship("Marche", back_populates="ml_insights")

class ExtractionNlp(Base, TimestampMixin):
    __tablename__ = "extractions_nlp"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    field_name = Column(String(100), nullable=False)
    value = Column(Text, nullable=True)
    source_extractor = Column(String(50), nullable=True)
    score = Column(Numeric(5, 4), nullable=True)
    snippet = Column(Text, nullable=True)
    extracted_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("Document", back_populates="extractions")

# --- Audit & Analytics Tables ---
class AuditEvent(Base):
    __tablename__ = "audit_event"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    request_id = Column(String(100), nullable=True)
    payload_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SavedSearch(Base, TimestampMixin):
    __tablename__ = "saved_search"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    filters_json = Column(JSON, nullable=False)

class Alert(Base, TimestampMixin):
    __tablename__ = "alert"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    filters_json = Column(JSON, nullable=False)
    frequency = Column(String(50), nullable=False) # e.g. daily, weekly, real-time
    channels_json = Column(JSON, nullable=False) # e.g. ["email", "in_app"]
    is_active = Column(Boolean, default=True)

class AlertDelivery(Base, TimestampMixin):
    __tablename__ = "alert_delivery"
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alert.id", ondelete="CASCADE"), nullable=False)
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
    results_count = Column(Integer, nullable=False, default=0)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    channel = Column(String(50), nullable=False)
