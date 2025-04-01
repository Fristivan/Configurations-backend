from fastapi import APIRouter, Depends, Response, Request, HTTPException
from sqlalchemy.orm import Session
from app.auth.auth_service import login_user, get_db, get_current_user
from app.core.security import decode_token, create_access_token, create_refresh_token
from app.database.crud import create_user, get_user_by_email
from pydantic import BaseModel

router = APIRouter()

class UserRegister(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login")
def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    return login_user(user.email, user.password, db, response)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token provided")

    payload = decode_token(refresh_token)
    print(payload)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token({"sub": payload["sub"]})
    new_refresh_token = create_refresh_token({"sub": payload["sub"]})  # Генерируем новый refresh_token

    # Обновляем токены в куках
    response.set_cookie("access_token", new_access_token, httponly=True, max_age=3600)  # 1 час (3600 секунд)
    response.set_cookie("refresh_token", new_refresh_token, httponly=True, max_age=2592000)  # 30 дней

    return TokenResponse(access_token=new_access_token)


@router.post("/logout")
def logout(response: Response, user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не авторизован")

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return {"message": "Вы успешно вышли из системы"}



@router.get("/verify")
def verify_auth(user=Depends(get_current_user)):
    print(user)

    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    return {
        "isAuthenticated": True,
        "email": user.email,
    }