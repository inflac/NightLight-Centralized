# config.py
import os
import logging

from dotenv import load_dotenv
from flask_cors import CORS


# General Configuration
load_dotenv()  # Load environment variables from .env file

# Configuration class
class Config:
    """Base config class for the application."""
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///nightlight.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # HOST and PORT from .env or default values
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))

    @staticmethod
    def configure_cors(app):
        allowed_websites = os.getenv("ALLOWED_WEBSITES")
        if allowed_websites == "*":
            origins = "*"
        elif isinstance(allowed_websites, str):
            origins = [site.strip() for site in allowed_websites.split(",") if site.strip()]
        else:
            origins = ""
        CORS(app, origins=origins)

    @staticmethod
    def configure_logging():
        """Sets up basic logging configuration."""
        logging.basicConfig(level=logging.DEBUG)