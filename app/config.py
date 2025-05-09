import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Gemini API settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")

# Application settings
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Data paths
DATA_DIR = os.getenv("DATA_DIR", "./data")
PDF_SOURCE_DIR = os.getenv("PDF_SOURCE_DIR", "./data/raw")
PDF_PROCESSED_DIR = os.getenv("PDF_PROCESSED_DIR", "./data/processed")
VECTOR_STORE_DIR = os.getenv("VECTOR_STORE_DIR", "./data/vector_store")

# Ensure data directories exist
os.makedirs(PDF_SOURCE_DIR, exist_ok=True)
os.makedirs(PDF_PROCESSED_DIR, exist_ok=True)
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

# ETL settings
ETL_SCHEDULE_HOUR = int(os.getenv("ETL_SCHEDULE_HOUR", "2"))
ETL_DOWNLOAD_TIMEOUT = int(os.getenv("ETL_DOWNLOAD_TIMEOUT", "60"))

# Monitoring
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENABLE_METRICS = os.getenv("ENABLE_METRICS", "True").lower() == "true"

# Discord webhook for quality alerts
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", None)
