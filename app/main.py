import os

import uvicorn
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

from app.database.database import init_db, get_db
from app.mail.mail_reg_router import mail_router
from app.yookassa.payment_routers import router as payment_router
from app.routers import nginx, systemd, apache, postgresql, sshd, redis, dockerfile, docker_compose
from app.auth.auth_routers import router as auth_router
from app.auth.password_reset import password_reset_router
from app.user.user_router import router as user_router
from app.routers.configuration_router import router as configuration_router
from app.routers.service_template_router import router as service_template_router

from fastapi import FastAPI, Depends

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Список разрешенных источников
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    init_db()  # Запускаем создание таблиц

# Подключение маршрутов
app.include_router(nginx.router, tags=["Config Generator"])
app.include_router(dockerfile.router, tags=["Config Generator"])
app.include_router(docker_compose.router, tags=["Config Generator"])
app.include_router(systemd.router, tags=["Config Generator"])
app.include_router(apache.router, tags=["Config Generator"])
app.include_router(postgresql.router, tags=["Config Generator"])
app.include_router(sshd.router, tags=["Config Generator"])
app.include_router(redis.router, tags=["Config Generator"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(mail_router, tags=["Auth"])
app.include_router(password_reset_router, tags=["Auth"])
app.include_router(user_router, tags=["User"])
app.include_router(configuration_router, tags=["Save configurations"])
app.include_router(service_template_router, tags=["Info about configurations"])
app.include_router(payment_router, tags=["Payment"])
# Директория, где находятся сервисы
SERVICES_DIR = "app/routers"

@app.get("/services")
def get_services(db: Session = Depends(get_db)):
    from app.database.service_template_crud import get_all_service_templates
    templates = get_all_service_templates(db)
    return [
        {
            "id": tpl.service_id,
            "name": tpl.name,
            "description": tpl.description,
            "file_extension": tpl.file_extension
        }
        for tpl in templates
    ]

if __name__ == '__main__':
    uvicorn.run("app.main:app", reload=True)

