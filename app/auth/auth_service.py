from datetime import timedelta, datetime
from fastapi import HTTPException, Depends, Response, Request
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.database.crud import get_user_by_email
from app.database.database import SessionLocal
from app.database.models import User
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return None
    return user

def login_user(email: str, password: str, db: Session, response: Response):
    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})

    # Устанавливаем куки безопасно
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return {"message": "Login successful"}

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token is required")

    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    print(f"Аутентификация пользователя: {user.email}")
    return user

def reset_user_limit_if_needed(db: Session, user: User):
    now = datetime.utcnow()
    if now >= user.limit_reset_date:
        user.requests_this_month = 0
        user.limit_reset_date = now + timedelta(days=30)
        db.commit()

def check_user_limit(db: Session, user_id: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False

    reset_user_limit_if_needed(db, user)
    return user.requests_this_month < user.request_limit

def increment_user_requests(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.requests_this_month += 1
        db.commit()
