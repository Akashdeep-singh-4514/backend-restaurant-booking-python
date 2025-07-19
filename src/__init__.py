# src/__init__.py
import os

from dotenv import load_dotenv

# Load environment variables FIRST
if os.getenv("PYTHON_ENV") == "test":
    load_dotenv(dotenv_path=".env.test", override=True)
else:
    load_dotenv()

from .app import app

# Import logger and app after environment variables are loaded
from .config import logger  # Assuming logger is exposed via src/config/__init__.py

# Basic validation for essential environment variables
if not os.getenv("CORS_ALLOW_ORIGINS"):
    logger.warning(
        "CORS_ALLOW_ORIGINS environment not set. Defaulting to localhost in app.py."
    )

if not os.getenv("SQLALCHEMY_DATABASE_URI"):
    raise ValueError(
        "SQLALCHEMY_DATABASE_URI environment not set. Please check your .env file or environment."
    )

__all__ = ["app"]  # Only expose 'app' as the main entry point from 'src'
__version__ = "0.1.0"
__author__ = "Akashdeep singh"  # Your name
