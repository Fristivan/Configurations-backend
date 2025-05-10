from typing import get_type_hints, Optional, get_args

from fastapi import APIRouter, Response, HTTPException, Depends
from sqlalchemy.orm import Session
from app.services import render_template
from app.models.sshd_model import SSHConfig
from app.auth.auth_service import get_current_user, check_user_limit, increment_user_requests, get_db
from app.database.database import SessionLocal

router = APIRouter()
@router.get("/form-metadata/sshd/")
def get_ssh_form_metadata():
    schema = SSHConfig.schema()
    fields = []
    dependencies = {}

    # Определение зависимостей
    dependency_map = {
        "password_authentication": ["permit_empty_passwords"],
        "pubkey_authentication": ["authorized_keys_file"],
    }

    # Берем реальные типы данных из модели `SSHConfig`
    type_hints = get_type_hints(SSHConfig)

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
        if hasattr(annotation, "__origin__") or annotation.__origin__ is Optional:
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
        field["isAdvanced"] = not field["required"] and field_name not in ["port", "protocol", "permit_root_login"]

        # Если поле является чекбоксом, добавляем зависимости
        if field_name in dependency_map:
            dependencies[field_name] = dependency_map[field_name]

        fields.append(field)

    return {"fields": fields, "dependencies": dependencies}

@router.post("/generate/sshd/")
def generate_ssh(config: SSHConfig, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    if not check_user_limit(db, user.id):
        raise HTTPException(status_code=403, detail="Request limit exceeded")
    sshd_config = render_template("sshd.j2", config.dict())
    increment_user_requests(db, user.id)
    return Response(content=sshd_config, media_type="text/plain")
