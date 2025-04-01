from datetime import timedelta, datetime

from fastapi import HTTPException, Depends, Response, Request
from sqlalchemy.orm import Session
from app.database.crud import get_user_by_email
from app.database.database import SessionLocal
from app.core.security import create_access_token, create_refresh_token, decode_token
from passlib.context import CryptContext

from app.database.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def authenticate_user(db: Session, email: str, password: str):
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
    print(access_token)
    response.set_cookie("access_token", access_token, httponly=True, max_age=3600)
    response.set_cookie("refresh_token", refresh_token, httponly=True, max_age=30 * 24 * 60 * 60)

    return {"message": "Login successful"}


def get_current_user(request: Request, db: Session = Depends(get_db)):
    """ Декодирует токен из куков и получает пользователя из БД """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token is required")

    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.email == payload["sub"]).first()
    print(f"Аунтефикация Юзера {payload["sub"]}")
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def reset_user_limit_if_needed(db: Session, user: User):
    """ Проверяет, не пора ли сбросить лимит запросов """
    now = datetime.utcnow()

    if now >= user.limit_reset_date:  # Если лимит пора обновить
        user.requests_this_month = 0
        user.limit_reset_date = now + timedelta(days=30)  # Ставим новую дату сброса
        db.commit()





def check_user_limit(db: Session, user_id: int):
    """ Проверяет, не превысил ли пользователь лимит запросов и сбрасывает его если нужно """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False

    reset_user_limit_if_needed(db, user)  # Сбрасываем лимит, если нужно
    return user.requests_this_month < user.request_limit

def increment_user_requests(db: Session, user_id: int):
    """ Увеличивает количество использованных запросов пользователя """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.requests_this_month += 1
        db.commit()