# В app/utils/image_utils.py

import base64
from pathlib import Path
from fastapi import UploadFile


def convert_image_to_base64(image_file: UploadFile) -> str:
    """Конвертирует загруженное изображение в строку Base64"""
    file_content = image_file.file.read()
    encoded = base64.b64encode(file_content)
    return encoded.decode('utf-8')


def convert_file_path_to_base64(file_path: str) -> str:
    """Конвертирует изображение из файловой системы в строку Base64"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Файл {file_path} не найден")

    with open(file_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read())
        return encoded.decode('utf-8')