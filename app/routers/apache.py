from typing import get_args, Optional, get_type_hints

from fastapi import APIRouter, HTTPException, Response, Depends
from sqlalchemy.orm import Session

from app.auth.auth_service import increment_user_requests, check_user_limit, get_db, get_current_user
from app.services import render_template
from app.models.apache_model import ApacheConfig

router = APIRouter()

@router.get("/form-metadata/apache")
def get_apache_form_metadata():
    schema = ApacheConfig.schema()
    fields = []
    dependencies = {}

    # Определение зависимостей
    dependency_map = {
        "ssl_enabled": ["ssl_certificate_file", "ssl_certificate_key_file", "ssl_chain_file", "ssl_protocols", "ssl_ciphers", "ssl_session_cache"],
        "proxy_pass": ["proxy_path"],
    }

    # Берем реальные типы данных из модели `ApacheConfig`
    type_hints = get_type_hints(ApacheConfig)

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
        field["isAdvanced"] = not field["required"] and field_name not in ["port", "server_name", "document_root"]

        # Если поле является чекбоксом, добавляем зависимости
        if field_name in dependency_map:
            dependencies[field_name] = dependency_map[field_name]

        fields.append(field)

    return {"fields": fields, "dependencies": dependencies}

@router.post("/generate/apache")
def generate_apache(config: ApacheConfig, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    if not check_user_limit(db, user.id):
        raise HTTPException(status_code=403, detail="Request limit exceeded")

    if not config.server_name or not config.document_root:
        raise HTTPException(status_code=400, detail="ServerName и DocumentRoot обязательны")

    apache_conf = render_template("apache.j2", config.dict())
    increment_user_requests(db, user.id)
    return Response(content=apache_conf, media_type="text/plain")
