from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.auth.auth_service import get_current_user, get_db
from app.database.models import User

router = APIRouter()

@router.get("/account/info")
def get_account_info(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    return {
        "id": user.id,
        "email": user.email,
        "subscription_level": user.subscription_level,
        "subscription_expiry": user.subscription_expiry,
        "requests_this_month": user.requests_this_month,
        "request_limit": user.request_limit,
        "limit_reset_date": user.limit_reset_date.isoformat(),
    }
