from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from backend.database import get_db
from backend.models import User, AuditEvent
from backend.auth.auth_handler import get_password_hash, verify_password, validate_password_policy, SECRET_KEY, ALGORITHM
from backend.auth.rbac import get_current_user
from backend.limiter import limiter
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/auth", tags=["auth_passwords"])

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

def log_audit(db: Session, action: str, user_id: int = None, resource_type: str = "auth", resource_id: str = None, ip_address: str = None):
    audit = AuditEvent(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()

@router.post("/forgot-password")
@limiter.limit("3/minute")
def forgot_password(request: Request, payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    ip = request.client.host if request.client else None
    if user:
        # Create a stateless JWT reset token valid for 15 minutes
        # We include the hashed_password in the token so that it becomes invalid once the password is changed
        expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode = {"sub": user.username, "exp": expire, "hash": user.hashed_password[-10:]}
        reset_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        # Simulate sending email
        logger.info("Sending password reset email", email=user.email, reset_token=reset_token)
        log_audit(db, "forgot_password_requested", user.id, ip_address=ip)
        
    # We always return the same message to avoid email enumeration attacks
    return {"message": "Si un compte est associé à cet email, un lien de réinitialisation vous a été envoyé."}

@router.post("/reset-password")
@limiter.limit("3/minute")
def reset_password(request: Request, payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else None
    try:
        token_data = jwt.decode(payload.token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = token_data.get("sub")
        hash_part: str = token_data.get("hash")
    except JWTError:
        raise HTTPException(status_code=400, detail="Token invalide ou expiré")
        
    user = db.query(User).filter(User.username == username).first()
    if not user or user.hashed_password[-10:] != hash_part:
        raise HTTPException(status_code=400, detail="Token invalide ou expiré")
        
    try:
        validate_password_policy(payload.new_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    user.hashed_password = get_password_hash(payload.new_password)
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()
    
    log_audit(db, "password_reset", user.id, ip_address=ip)
    return {"message": "Mot de passe réinitialisé avec succès."}

@router.post("/change-password")
def change_password(request: Request, payload: ChangePasswordRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ip = request.client.host if request.client else None
    
    if not verify_password(payload.old_password, current_user.hashed_password):
        log_audit(db, "change_password_failed", current_user.id, ip_address=ip)
        raise HTTPException(status_code=400, detail="Ancien mot de passe incorrect.")
        
    try:
        validate_password_policy(payload.new_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    current_user.hashed_password = get_password_hash(payload.new_password)
    db.commit()
    
    log_audit(db, "password_changed", current_user.id, ip_address=ip)
    return {"message": "Mot de passe modifié avec succès."}
