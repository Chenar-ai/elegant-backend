from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database import get_db
from app.models import Admin
from app.schemas.admin import AdminCreate, AdminLogin, TokenResponse
from app.utils import verify_password, create_access_token
from datetime import datetime, timedelta



router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

@router.post("/signup")
def admin_signup(admin_data: AdminCreate, db: Session = Depends(get_db)):
    hashed_pw = get_password_hash(admin_data.password)

    new_admin = Admin(
        name=admin_data.name,
        email=admin_data.email,
        hashed_password=hashed_pw
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return {"message": "Admin created successfully", "id": new_admin.id}


@router.post("/login", response_model=TokenResponse)
def admin_login(payload: AdminLogin, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.email == payload.email).first()
    if not admin or not verify_password(payload.password, admin.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    expire = datetime.utcnow() + timedelta(minutes=60)
    access_token = create_access_token({
        "sub": admin.email,
        "role": "admin",
        "id": admin.id
    })
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 3600
    }

@router.post("/logout")
def admin_logout():
    return {"message": "Logged out successfully"}






