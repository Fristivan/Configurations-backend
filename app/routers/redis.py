from typing import get_args, Optional, get_type_hints

from fastapi import APIRouter, HTTPException, Response, Depends
from sqlalchemy.orm import Session

from app.auth.auth_service import check_user_limit, get_db, get_current_user, increment_user_requests
from app.services import render_template
from app.models.redis_model import RedisConfig

router = APIRouter()

@router.get("/form-metadata/redis")
def get_redis_form_metadata():
    schema = RedisConfig.schema()
    fields = []
    dependencies = {}

    dependency_map = {
        "enable_logging": ["loglevel"],
        "enable_ssl": ["ssl_cert_file", "ssl_key_file"],
        "enable_replication": ["slaveof"],
    }

    fields = []
    type_hints = get_type_hints(RedisConfig)

    type_mapping = {
        bool: "bool",
        int: "int",
        str: "str",
        list: "list",
        dict: "dict",
    }

    def get_real_type(field_name):
        annotation = type_hints.get(field_name, str)
        if hasattr(annotation, "__origin__") and annotation.__origin__ is Optional:
            annotation = get_args(annotation)[0]
        return annotation

    schema = RedisConfig.schema()
    dependencies = {}

    for field_name, field_info in schema["properties"].items():
        python_type = type_hints.get(field_name, str)

        # Проверка и очистка типа Optional
        if hasattr(python_type, "__origin__") and python_type.__origin__ is Optional:
            python_type = get_args(python_type)[0]

        mapped_type = type_mapping.get(python_type, "str")

        field = {
            "name": field_name,
            "label": field_name.replace("_", " ").capitalize(),
            "required": field_name in schema.get("required", []),
            "defaultValue": field_info.get("default", None),
            "description": field_info.get("description", ""),
            "variableType": mapped_type
        }

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

        if "example" in field_info:
            field["placeholder"] = str(field_info["example"])

        field["isAdvanced"] = not field["required"] and not field_name.startswith("enable_")

        if field_name in dependency_map:
            dependencies[field_name] = dependency_map[field_name]

        fields.append(field)

    return {"fields": fields, "dependencies": dependencies}

@router.post("/generate/redis")
def generate_redis(config: RedisConfig, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    if not check_user_limit(db, user.id):
        raise HTTPException(status_code=403, detail="Request limit exceeded")

    if not config.bind:
        raise HTTPException(status_code=400, detail="bind is required")

    redis_config = render_template("redis.j2", config.dict())
    increment_user_requests(db, user.id)
    return Response(content=redis_config, media_type="text/plain")