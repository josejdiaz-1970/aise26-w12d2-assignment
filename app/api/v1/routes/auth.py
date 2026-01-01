from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import UserCreate, UserLogin, UserResponse, TokenResponse
from app.db import crud
from app.db.models import User
from app.core.security import create_access_token
from app.core.exceptions import UnauthorizedError

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    return crud.create_user(db, user.email, user.password)


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    authenticated = crud.authenticate_user(db, user.email, user.password)
    if not authenticated:
        raise UnauthorizedError("Invalid credentials")

    token = create_access_token(
        {"sub": authenticated.id, "role": authenticated.role}
    )
    return {"access_token": token}
