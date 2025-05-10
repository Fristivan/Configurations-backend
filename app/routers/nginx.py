from typing import get_args, Optional, get_type_hints

from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session

from app.database.database import init_db
from app.auth.auth_service import get_current_user, check_user_limit, increment_user_requests, get_db
from app.services import render_template
from app.models.nginx_model import NginxConfig
from app.database.models import User

router = APIRouter()


@router.get("/form-metadata/nginx/")
def get_nginx_form_metadata():
    schema = NginxConfig.schema()
    fields = []
    dependencies = {}

    # Определение зависимостей
    dependency_map = {
        "enable_ssl": ["ssl_certificate", "ssl_certificate_key"],
        "enable_logging": ["access_log", "error_log"],
        "enable_proxy": ["proxy_pass"],
        "enable_basic_auth": ["auth_user_file"],
        "enable_cors": ["cors_allowed_origins"],
    }

    # Берем реальные типы данных из модели `NginxConfig`
    type_hints = get_type_hints(NginxConfig)

    # Кастомное отображение типов для фронтенда
    type_mapping = {
        bool: "bool",
        int: "int",
        str: "str",
        list: "list",
        dict: "dict",
    }

    def get_real_type(field_name):
        """ Определяем точный тип данных, убирая `Optional[]` """
        annotation = type_hints.get(field_name, str)  # По умолчанию считаем строкой
        if hasattr(annotation, "__origin__") and annotation.__origin__ is Optional:
            annotation = get_args(annotation)[0]  # Достаем реальный тип данных из Optional[]
        return annotation

    for field_name, field_info in schema["properties"].items():
        # Получаем реальный тип данных без Optional[]
        python_type = get_real_type(field_name)
        mapped_type = type_mapping.get(python_type, "str")

        field = {
            "name": field_name,
            "label": field_name.replace("_", " ").capitalize(),
            "required": field_name in schema.get("required", []),
            "defaultValue": field_info.get("default", None),
            "description": field_info.get("description", ""),  # Добавляем описание
            "variableType": mapped_type  # Теперь берем реальный тип переменной!
        }

        # Определяем тип поля для формы
        if mapped_type == "bool":
            field["type"] = "checkbox"
        elif mapped_type == "int":
            field["type"] = "number"
        elif mapped_type == "list":
            field["type"] = "array"
        elif mapped_type == "dict":
            field["type"] = "json"
        else:
            field["type"] = "text"

        # Добавляем placeholder, если есть
        if "example" in field_info:
            field["placeholder"] = str(field_info["example"])

        # Определяем, является ли поле дополнительным
        field["isAdvanced"] = not field["required"] and not field_name.startswith("enable_")

        # Если поле является чекбоксом, добавляем зависимости
        if field_name in dependency_map:
            dependencies[field_name] = dependency_map[field_name]

        fields.append(field)

    return {"fields": fields, "dependencies": dependencies}


@router.post("/generate/nginx/")
def generate_nginx(config: NginxConfig, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    if not check_user_limit(db, user.id):
        raise HTTPException(status_code=403, detail="Request limit exceeded")
    # Генерируем конфигурацию
    nginx = render_template("nginx.j2", config.dict())
    # Учитываем запрос в БД
    increment_user_requests(db, user.id)
    return Response(content=nginx, media_type="text/plain")
