from typing import get_args, Optional, get_type_hints

from fastapi import APIRouter, HTTPException, Response, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.auth_service import get_db, get_current_user, check_user_limit, increment_user_requests
from app.services import render_template
from app.models.docker_models import DockerfileConfig, DockerComposeConfig, ServiceConfig

router = APIRouter()

@router.get("/form-metadata/docker-compose/")
def get_docker_compose_form_metadata():
    schema = DockerComposeConfig.schema()
    fields = []
    dependencies = {}

    # Определение зависимостей (если чекбокс включен, показываются связанные поля)
    dependency_map = {
        "enable_networks": ["networks"],
        "enable_volumes": ["volumes"],
        "enable_build": ["build"],
        "enable_ports": ["ports"],
        "enable_depends_on": ["depends_on"],
    }

    # Берем реальные типы данных из модели `DockerComposeConfig`
    type_hints = get_type_hints(DockerComposeConfig)
    service_type_hints = get_type_hints(ServiceConfig)  # Для вложенных полей `services`

    # Кастомное отображение типов для фронтенда
    type_mapping = {
        bool: "bool",
        int: "int",
        str: "str",
        list: "list",
        dict: "dict",
    }

    def get_real_type(field_name, type_source):
        """ Определяем точный тип данных, убирая `Optional[]` """
        annotation = type_source.get(field_name, str)  # По умолчанию считаем строкой
        if hasattr(annotation, "__origin__") and annotation.__origin__ is Optional:
            annotation = get_args(annotation)[0]  # Достаем реальный тип данных из Optional[]
        return annotation

    def process_field(field_name, field_info, parent="", required_fields=set(), type_source=type_hints):
        """Обрабатывает каждое поле схемы, включая вложенные параметры"""
        full_name = f"{parent}.{field_name}" if parent else field_name
        python_type = get_real_type(field_name, type_source)
        mapped_type = type_mapping.get(python_type, "str")

        field = {
            "name": full_name,
            "label": field_name.replace("_", " ").capitalize(),
            "required": field_name in required_fields,
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

        # Определяем, является ли поле расширенным
        field["isAdvanced"] = not field["required"] and full_name not in ["version", "services.image"]

        # Если поле является чекбоксом, добавляем зависимости
        if full_name in dependency_map:
            dependencies[full_name] = dependency_map[full_name]

        fields.append(field)

    # Определяем **Только необходимые обязательные поля**
    required_fields = {"version"}  # Основной параметр Docker Compose

    # Обрабатываем поля верхнего уровня
    for field_name, field_info in schema["properties"].items():
        if field_name == "services":
            # Разбираем вложенные параметры services (из ServiceConfig)
            service_schema = ServiceConfig.schema()
            for sub_field_name, sub_field_info in service_schema["properties"].items():
                # **Только image обязательно**
                required_service_fields = {"image"}  # Только image является обязательным
                process_field(sub_field_name, sub_field_info, parent="services",
                              required_fields=required_service_fields, type_source=service_type_hints)
        else:
            process_field(field_name, field_info, required_fields=required_fields)

    return {"fields": fields, "dependencies": dependencies}



# 📌 Генерация docker-compose.yml
@router.post("/generate/docker-compose/")
def generate_docker_compose(config: DockerComposeConfig, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    if not check_user_limit(db, user.id):
        raise HTTPException(status_code=403, detail="Request limit exceeded")

    if not config.services:
        raise HTTPException(status_code=400, detail="Services cannot be empty")

    docker = render_template("docker-compose.j2", config.dict())
    increment_user_requests(db, user.id)
    return Response(content=docker, media_type="text/plain")
