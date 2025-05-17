# payment_service.py
from yookassa import Configuration, Payment
import uuid
from app.config import settings

# Настройки YooKassa
Configuration.account_id = settings.CONFIGURATION_ACCOUNT_ID
Configuration.secret_key = settings.CONFIGURATION_SECRET_KEY
base_url = settings.BASE_URL


class PaymentProcessor:
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
            "description": description,
            "metadata": {
                "order_id": order_id  # <-- сохраняем заказ
            }
        }, idempotence_key)
        return {
            "order_id": order_id,
            "payment_url": payment.confirmation.confirmation_url
        }

    def check_payment_status(self, payment_id: str):
        payment = Payment.find_one(payment_id)
        return {
            "payment_status": payment.status,
            "amount": payment.amount["value"],
            "currency": payment.amount["currency"],
            "description": payment.description,
            "created_at": payment.created_at,
            "paid": payment.paid,
            "metadata": payment.metadata
        }
