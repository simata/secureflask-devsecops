import os


class Config:
    """Application configuration loaded from environment variables."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    API_KEY_HEADER = "X-API-Key"
    ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*")