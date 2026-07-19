from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional

from backend.database import get_db
from backend.models import User, Role
from backend.auth.rbac import RequireRole
from backend.auth.auth_handler import get_password_hash, validate_password_policy

router = APIRouter(prefix="/api/v1/users", tags=["users"])

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    roles: List[str] = ["reader"]

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    roles: List[str]

    class Config:
        orm_mode = True

@router.get("", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db), current_user = Depends(RequireRole(["admin"]))):
    users = db.query(User).all()
    result = []
    for u in users:
        result.append(UserResponse(
            id=u.id,
            username=u.username,
            email=u.email,
            is_active=u.is_active,
            roles=[r.name for r in u.roles]
        ))
    return result

@router.post("", response_model=UserResponse)
def create_user(payload: UserCreate, db: Session = Depends(get_db), current_user = Depends(RequireRole(["admin"]))):
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
        
    try:
        validate_password_policy(payload.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    db_roles = []
    for role_name in payload.roles:
        r = db.query(Role).filter(Role.name == role_name).first()
        if not r:
            raise HTTPException(status_code=400, detail=f"Role '{role_name}' does not exist")
        db_roles.append(r)
        
    new_user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        roles=db_roles
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        is_active=new_user.is_active,
        roles=[r.name for r in new_user.roles]
    )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user = Depends(RequireRole(["admin"]))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
        
    db.delete(user)
    db.commit()
    return
