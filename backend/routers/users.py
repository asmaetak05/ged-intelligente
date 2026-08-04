from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy.orm import Session

from backend.auth.auth_handler import get_password_hash, validate_password_policy
from backend.auth.rbac import RequireRole
from backend.database import get_db
from backend.models import Role, User

router = APIRouter(prefix='/api/v1/users', tags=['users'])

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    roles: List[str] = ['reader']

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    roles: Optional[List[str]] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    last_login_at: Optional[datetime] = None
    roles: List[str]
    model_config = ConfigDict(from_attributes=True)

def serialize(user: User) -> UserResponse:
    return UserResponse(id=user.id, username=user.username, email=user.email, is_active=user.is_active, last_login_at=user.last_login_at, roles=[role.name for role in user.roles])

def resolve_roles(names: List[str], db: Session) -> List[Role]:
    roles = db.query(Role).filter(Role.name.in_(names)).all()
    if len(roles) != len(set(names)):
        raise HTTPException(status_code=400, detail='One or more roles do not exist')
    return roles

@router.get('', response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db), current_user=Depends(RequireRole(['admin']))):
    return [serialize(user) for user in db.query(User).order_by(User.username).all()]

@router.post('', response_model=UserResponse)
def create_user(payload: UserCreate, db: Session = Depends(get_db), current_user=Depends(RequireRole(['admin']))):
    if db.query(User).filter(User.username == payload.username).first() or db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail='Username or email already registered')
    try:
        validate_password_policy(payload.password)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    user = User(username=payload.username, email=payload.email, hashed_password=get_password_hash(payload.password), roles=resolve_roles(payload.roles, db))
    db.add(user); db.commit(); db.refresh(user)
    return serialize(user)

@router.patch('/{user_id}', response_model=UserResponse)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), current_user=Depends(RequireRole(['admin']))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    if payload.email is not None:
        duplicate = db.query(User).filter(User.email == payload.email, User.id != user_id).first()
        if duplicate: raise HTTPException(status_code=400, detail='Email already registered')
        user.email = payload.email
    if payload.roles is not None: user.roles = resolve_roles(payload.roles, db)
    if payload.is_active is not None:
        if user.id == current_user.id and not payload.is_active: raise HTTPException(status_code=400, detail='Cannot deactivate your own account')
        user.is_active = payload.is_active
    db.commit(); db.refresh(user)
    return serialize(user)

@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(RequireRole(['admin']))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(status_code=404, detail='User not found')
    if user.id == current_user.id: raise HTTPException(status_code=400, detail='Cannot delete your own account')
    db.delete(user); db.commit()
