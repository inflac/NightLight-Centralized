# config.py
import logging
import os
from typing import List, Union

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from .logger import create_logger

# Load environment variables from .env file
load_dotenv(dotenv_path=".env", override=True)


class Config:
    """Base config class for the application"""

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///nightlight.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # General
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 5000))

    # Restx Configuration
    ERROR_404_HELP = False  # Disable route suggenstions on 404

    # Admin routes
    ENABLE_ADMIN_ROUTES = os.getenv("ENABLE_ADMIN_ROUTES", "false").lower() == "true"

    # Instagram encryption settings
    password = os.getenv("ENCRYPTION_PASSWORD")
    if not password:
        raise ValueError("ENCRYPTION_PASSWORD is not set in .env!")
    ENCRYPTION_PASSWORD: str = password  # Solution to make mypy recognize type str

    # Toggle generating API documentation
    __generate_api_doc = os.getenv("GENERATE_API_DOCUMENTATION", "false").lower() == "true"
    API_DOC_PATH = "/docs" if __generate_api_doc else False  # Set / if True, else False

    # CORS
    CORS_ALLOWED_WEBSITES = os.getenv("CORS_ALLOWED_WEBSITES", "")

    # File management
    UPLOAD_FOLDER = "./instance/nightlines"

    @classmethod
    def configure_cors(cls, app: Flask) -> None:
        """Configure CORS (Websites allowed to access the API)"""
        allowed_websites = cls.CORS_ALLOWED_WEBSITES
        if allowed_websites == "*":
            origins: Union[str, List[str]] = "*"
        elif isinstance(allowed_websites, str):
            # Filter only valid HTTP/HTTPS origins
            origins = [site.strip() for site in allowed_websites.split(",") if site.strip().startswith("http://") or site.strip().startswith("https://")]
        else:
            origins = ""
        CORS(app, origins=origins)

    @staticmethod
    def configure_logging() -> logging.Logger:
        """Configure and create a logger"""
        LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
        LOG_TO_FILE = os.getenv("LOG_TO_FILE", "false").lower() == "true"
        FILE_LOG_FORMAT = "" if os.getenv("FILE_LOG_FORMAT", "") != "json" else "json"

        return create_logger(LOG_TO_FILE, FILE_LOG_FORMAT, LOG_LEVEL)
