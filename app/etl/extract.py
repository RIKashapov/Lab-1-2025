import io
import json
from typing import Dict, Any

import requests
from minio import Minio

from app.config import (
    OPEN_METEO_BASE_URL,
    CITIES,
    get_tomorrow_date_str,
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_BUCKET_RAW,
    MINIO_SECURE,
)


def get_minio_client() -> Minio:
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE,
    )


def fetch_weather_for_city(city_key: str) -> Dict[str, Any]:
    city = CITIES[city_key]
    tomorrow = get_tomorrow_date_str()

    params = {
        "latitude": city["lat"],
        "longitude": city["lon"],
        "hourly": "temperature_2m,precipitation,wind_speed_10m,wind_direction_10m",
        "timezone": "auto",
        "start_date": tomorrow,
        "end_date": tomorrow,
    }

    resp = requests.get(OPEN_METEO_BASE_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    data["_meta"] = {
        "city_key": city_key,
        "city_name": city["name"],
        "date": tomorrow,
    }

    return data


def save_raw_to_minio(city_key: str, data: Dict[str, Any]) -> str:
    client = get_minio_client()

    # Создаём бакет, если его ещё нет
    if not client.bucket_exists(MINIO_BUCKET_RAW):
        client.make_bucket(MINIO_BUCKET_RAW)

    date_str = data.get("_meta", {}).get("date", get_tomorrow_date_str())
    object_name = f"raw/{city_key}/{date_str}.json"

    payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
    payload_io = io.BytesIO(payload)

    client.put_object(
        MINIO_BUCKET_RAW,
        object_name,
        data=payload_io,
        length=len(payload),
        content_type="application/json",
    )

    return object_name


def run_extract_for_all_cities() -> None:
    for city_key in CITIES.keys():
        print(f"Загрузка прогноза для: {city_key}")
        data = fetch_weather_for_city(city_key)
        object_name = save_raw_to_minio(city_key, data)
        print(f"Сохранено в MinIO: s3://{MINIO_BUCKET_RAW}/{object_name}")


if __name__ == "__main__":
    run_extract_for_all_cities()
