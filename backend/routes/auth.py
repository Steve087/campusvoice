from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.db_models import User
from models.schemas import RegisterRequest, LoginRequest, TokenResponse
from services.auth import (
    validate_email_domain, hash_password,
    verify_password, create_access_token
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    # 1. Validate email domain
    if not validate_email_domain(req.email):
        raise HTTPException(status_code=400, detail="Only @cec.ac.in emails allowed")

    # 2. Check if email already exists
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 3. Validate role
    if req.role not in ["student", "admin"]:
        raise HTTPException(status_code=400, detail="Role must be student or admin")

    # 4. Create user
    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        role=req.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 5. Return token immediately — no need to login separately
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(access_token=token, role=user.role)


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    # 1. Find user
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 2. Check password
    if not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 3. Check active
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")

    # 4. Return token
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(access_token=token, role=user.role)