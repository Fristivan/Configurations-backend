from typing import List

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.auth.auth_service import get_db, get_current_user
from app.auth.password_reset import password_reset_router
from app.yookassa.payment_service import PaymentProcessor
from app.database.models import PaymentOrder, User  # твои ORM-модели
from datetime import datetime, timedelta

router = APIRouter(prefix="/payments")
processor = PaymentProcessor()

class PayRequest(BaseModel):
    amount: str
    plan: str   # например, 'premium' или 'professional'

class PaymentOrderResponse(BaseModel):
    order_id: str
    plan: str
    amount: str
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

@router.post("/create/")
def create_payment(
    req: PayRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1) создаём платёж в YooKassa
    res = processor.create_payment(req.amount, f"{req.plan} для {current_user.email}")

    # 2) сохраняем в БД связь order_id → user.id
    order = PaymentOrder(
      order_id=res["order_id"],
      user_id=current_user.id,
      plan=req.plan,
      amount=req.amount,
      status="created",
      created_at=datetime.utcnow()
    )
    db.add(order)
    db.commit()

    # 3) отдаем URL для редиректа
    return {"payment_url": res["payment_url"]}


@router.get("/{order_id}/status/")
def get_status(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1) находим заказ и проверяем, что он принадлежит этому пользователю
    order = db.query(PaymentOrder).filter_by(order_id=order_id, user_id=current_user.id).first()
    if not order:
        raise HTTPException(404, "Order not found")

    # 2) запрашиваем статус у YooKassa
    info = processor.check_payment_status(order_id)
    return {"payment_status": info["payment_status"]}


@router.post("/webhook/")
async def yookassa_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    obj = payload.get("object", {})
    order_id = obj.get("description", "").split()[-1]  # если ты в description запихал order_id
    status = obj.get("status")

    # 1) ищем заказ в БД
    order = db.query(PaymentOrder).filter_by(order_id=order_id).first()
    if not order:
        return {"error": "Unknown order"}

    # 2) если оплачено — активируем подписку
    if status == "succeeded":
        user = db.query(User).get(order.user_id)
        user.request_limit = 30 if order.plan == 'premium' else 60
        user.subscription_level = order.plan
        user.subscription_expiry = datetime.utcnow() + timedelta(days=30)
        order.status = "succeeded"
        db.commit()
    return {"ok": True}

@router.get("/", response_model=List[PaymentOrderResponse])
def list_user_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Возвращаем все заказы текущего пользователя
    orders = db.query(PaymentOrder).filter_by(user_id=current_user.id).all()
    return orders