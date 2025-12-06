import os
from datetime import datetime, timedelta

# Базовый URL Open-Meteo
OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"

# Города и координаты
CITIES = {
    "moscow": {
        "name": "Москва",
        "lat": 55.7558,
        "lon": 37.6176,
    },
    "samara": {
        "name": "Самара",
        "lat": 53.1959,
        "lon": 50.1008,
    },
}

def get_tomorrow_date_str() -> str:
    tomorrow = datetime.utcnow().date() + timedelta(days=1)
    return tomorrow.strftime("%Y-%m-%d")


MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET_RAW = os.getenv("MINIO_BUCKET_RAW", "weather-raw")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "clickhouse")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", "9000"))
CLICKHOUSE_DB = os.getenv("CLICKHOUSE_DB", "weather")
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "user")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "password")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")