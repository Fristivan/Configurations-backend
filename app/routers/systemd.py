from typing import get_args, Optional, get_type_hints

from fastapi import APIRouter, Response, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.auth_service import get_current_user, check_user_limit, get_db, increment_user_requests
from app.services import render_template
from app.models.systemd_model import SystemdConfig

router = APIRouter()

@router.get("/form-metadata/systemd/")
def get_systemd_form_metadata():
    schema = SystemdConfig.schema()
    fields = []
    dependencies = {}

    # Определение зависимостей (если чекбокс включен, показываются связанные поля)
    dependency_map = {
        "restart_policy": ["restart_sec"],
    }

    # Берем реальные типы данных из модели `SystemdConfig`
    type_hints = get_type_hints(SystemdConfig)

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
        field["isAdvanced"] = not field["required"] and field_name not in ["description", "after", "exec_start"]

        # Если поле является чекбоксом, добавляем зависимости
        if field_name in dependency_map:
            dependencies[field_name] = dependency_map[field_name]

        fields.append(field)

    return {"fields": fields, "dependencies": dependencies}

@router.post("/generate/systemd/")
def generate_systemd(config: SystemdConfig, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    if not check_user_limit(db, user.id):
        raise HTTPException(status_code=403, detail="Request limit exceeded")

    systemd_service = render_template("systemd.j2", config.dict())
    increment_user_requests(db, user.id)
    return Response(content=systemd_service, media_type="text/plain")