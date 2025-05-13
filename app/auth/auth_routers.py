from fastapi import APIRouter, Depends, Response, Request, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.auth.auth_service import login_user, get_db, get_current_user
from app.core.security import decode_token, create_access_token, create_refresh_token
from app.config import settings

router = APIRouter(prefix="/auth")

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login")
def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    return login_user(user.email, user.password, db, response)

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: Request, response: Response):
    refresh_token_cookie = request.cookies.get("refresh_token")

    if not refresh_token_cookie:
        raise HTTPException(status_code=401, detail="No refresh token provided")

    payload = decode_token(refresh_token_cookie)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token({"sub": payload["sub"]})
    new_refresh_token = create_refresh_token({"sub": payload["sub"]})

    # Устанавливаем куки безопасно
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

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
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    return {
        "isAuthenticated": True,
        "email": user.email,
    }
