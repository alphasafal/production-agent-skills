import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    SECRET_KEY = "change-me-dev-secret"
    DEBUG = True

    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = int(os.environ.get("DB_PORT", "5432"))
    DB_NAME = "invoicing"
    DB_USER = "invoicing_app"
    DB_PASSWORD = "invoicing-dev-password"

    EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB upload limit for imports

    PAGE_SIZE = 50
