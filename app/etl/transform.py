import json
import io
from typing import Dict, Any, List, Tuple, Optional

from minio import Minio

from app.config import (
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


def load_raw_from_minio(city_key: str, date_str: Optional[str] = None) -> Dict[str, Any]:
    client = get_minio_client()
    if date_str is None:
        date_str = get_tomorrow_date_str()

    object_name = f"raw/{city_key}/{date_str}.json"

    response = client.get_object(MINIO_BUCKET_RAW, object_name)
    try:
        data_bytes = response.read()
    finally:
        response.close()
        response.release_conn()

    return json.loads(data_bytes.decode("utf-8"))


def normalize_hourly(city_key: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
    city = CITIES[city_key]

    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    precs = hourly.get("precipitation", [])
    wind_speeds = hourly.get("wind_speed_10m", [])
    wind_dirs = hourly.get("wind_direction_10m", [])

    rows: List[Dict[str, Any]] = []

    for t, temp, prec, ws, wd in zip(times, temps, precs, wind_speeds, wind_dirs):
        rows.append(
            {
                "city": city_key,
                "city_name": city["name"],
                "ts": t,                 # строка вида "2025-12-07T00:00"
                "temperature": float(temp),
                "precipitation": float(prec),
                "wind_speed": float(ws),
                "wind_direction": float(wd),
            }
        )

    return rows


def aggregate_daily(city_key: str, data: Dict[str, Any]) -> Dict[str, Any]:
    city = CITIES[city_key]
    meta = data.get("_meta", {})
    date_str = meta.get("date", get_tomorrow_date_str())

    hourly = data.get("hourly", {})
    temps = hourly.get("temperature_2m", []) or []
    precs = hourly.get("precipitation", []) or []
    wind_speeds = hourly.get("wind_speed_10m", []) or []

    if temps:
        temp_min = float(min(temps))
        temp_max = float(max(temps))
        temp_avg = float(sum(temps) / len(temps))
    else:
        temp_min = temp_max = temp_avg = None

    precip_sum = float(sum(precs)) if precs else 0.0
    max_wind_speed = float(max(wind_speeds)) if wind_speeds else 0.0

    STRONG_WIND_THRESHOLD = 10.0  # м/с
    HEAVY_PRECIP_THRESHOLD = 10.0  # мм/сутки

    strong_wind = 1 if max_wind_speed >= STRONG_WIND_THRESHOLD else 0
    heavy_precip = 1 if precip_sum >= HEAVY_PRECIP_THRESHOLD else 0

    return {
        "city": city_key,
        "city_name": city["name"],
        "date": date_str,
        "temp_min": temp_min,
        "temp_max": temp_max,
        "temp_avg": temp_avg,
        "precip_sum": precip_sum,
        "max_wind_speed": max_wind_speed,
        "strong_wind": strong_wind,
        "heavy_precip": heavy_precip,
    }


def run_transform_for_all_cities() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    all_hourly: List[Dict[str, Any]] = []
    all_daily: List[Dict[str, Any]] = []

    for city_key in CITIES.keys():
        print(f" Город: {city_key}")
        raw = load_raw_from_minio(city_key)
        hourly_rows = normalize_hourly(city_key, raw)
        daily_row = aggregate_daily(city_key, raw)

        print(f" hourly rows: {len(hourly_rows)}")
        print(f" daily row: {daily_row}")

        all_hourly.extend(hourly_rows)
        all_daily.append(daily_row)

    return all_hourly, all_daily


if __name__ == "__main__":
    hourly, daily = run_transform_for_all_cities()
    print(f"Всего почасовых записей: {len(hourly)}")
    print("Дневные записи:")
    for row in daily:
        print(row)
