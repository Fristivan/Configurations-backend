# payment_service.py
from yookassa import Configuration, Payment
import uuid
from app.config import settings

# Настройки YooKassa
Configuration.account_id = settings.CONFIGURATION_ACCOUNT_ID
Configuration.secret_key = settings.CONFIGURATION_SECRET_KEY
base_url = settings.BASE_URL


class PaymentProcessor:
    def __init__(self):
        self.orders = {}  # Временное хранилище заказов

    def create_payment(self, amount: str, description: str) -> dict:
        order_id = str(uuid.uuid4())
        idempotence_key = str(uuid.uuid4())

        payment = Payment.create({
            "amount": {
                "value": amount,
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"{base_url}?order_id={order_id}"
            },
            "capture": True,  # Важно: одностадийный платеж
            "description": description
        }, idempotence_key)

        self.orders[order_id] = {
            "status": "created",
            "payment_id": payment.id,
            "amount": amount,
            "description": description
        }

        return {
            "order_id": order_id,
            "payment_url": payment.confirmation.confirmation_url
        }

    def check_payment_status(self, order_id: str) -> dict:
        order = self.orders.get(order_id)
        if not order:
            return {"error": "Order not found"}

        payment = Payment.find_one(order["payment_id"])
        return {
            "order_id": order_id,
            "payment_status": payment.status,
            "amount": order["amount"],
            "description": order["description"]
        }