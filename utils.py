import os
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def ensure_images_directory():
    """Создает папку images если она не существует"""
    if not os.path.exists('images'):
        os.makedirs('images')
        logger.info("Создана папка images")


def is_url(string):
    """Проверяет, является ли строка URL"""
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except:
        return False


def file_exists(file_path):
    """Проверяет существование локального файла"""
    return os.path.exists(file_path) and os.path.isfile(file_path)


def get_image_files():
    """Возвращает список всех изображений в папке images"""
    ensure_images_directory()
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    images = []

    for file in os.listdir('images'):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            images.append(file)

    return images