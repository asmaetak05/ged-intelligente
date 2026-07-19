from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, AuditEvent
from datetime import datetime, timedelta, timezone
from backend.auth.auth_handler import verify_password, create_access_token, create_refresh_token, decode_token
from pydantic import BaseModel
from jose import JWTError
from fastapi import Request
from backend.limiter import limiter

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str

class RefreshRequest(BaseModel):
    refresh_token: str

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

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    ip = request.client.host if request.client else None
    
    if user:
        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            log_audit(db, "login_locked", user.id, ip_address=ip)
            raise HTTPException(status_code=403, detail="Account is temporarily locked. Try again later.")
            
        if not verify_password(form_data.password, user.hashed_password):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
                db.commit()
                log_audit(db, "account_locked", user.id, ip_address=ip)
                raise HTTPException(status_code=403, detail="Account locked due to multiple failed attempts.")
            db.commit()
            log_audit(db, "login_failed", user.id, ip_address=ip)
            raise HTTPException(status_code=401, detail="Incorrect username or password")
            
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
            
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.now(timezone.utc)
        db.commit()
        log_audit(db, "login_success", user.id, ip_address=ip)
    else:
        # User not found
        log_audit(db, "login_failed_not_found", resource_id=form_data.username, ip_address=ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    primary_role = user.roles[0].name if user.roles else "reader"
    access_token = create_access_token(data={"sub": user.username, "role": primary_role})
    refresh_token = create_refresh_token(data={"sub": user.username})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "role": primary_role}

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshRequest, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = decode_token(request.refresh_token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.is_active:
        raise credentials_exception
        
    primary_role = user.roles[0].name if user.roles else "reader"
    access_token = create_access_token(data={"sub": user.username, "role": primary_role})
    new_refresh_token = create_refresh_token(data={"sub": user.username})
    return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer", "role": primary_role}

@router.post("/logout")
def logout():
    # Stateless logout message
    return {"message": "Successfully logged out"}
