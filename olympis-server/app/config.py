import os
from pathlib import Path
from typing import List

# Database configuration
POSTGRES_DB = os.getenv("POSTGRES_DB", "olympis")
POSTGRES_USER = os.getenv("POSTGRES_USER", "olympis")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "olympis")
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_ECHO = True

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# S3 configuration
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")

# API configuration
API_TITLE = os.getenv("API_TITLE", "Olympis API")
API_DEBUG = os.getenv("API_DEBUG", "False").lower() == "true"
API_VERSION = os.getenv("API_VERSION", "1.0.0")
API_ROOT_PATH = os.getenv("API_ROOT_PATH", "")

# CORS configuration
CORS_ORIGINS: List[str] = [
    "http://localhost:5173",
    "http://localhost:3000",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS = ["*"]
CORS_EXPOSE_HEADERS = ["*"]

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4")
