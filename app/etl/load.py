from typing import List, Dict
from datetime import datetime

from clickhouse_driver import Client

from app.config import (
    CLICKHOUSE_HOST,
    CLICKHOUSE_PORT,
    CLICKHOUSE_DB,
    CLICKHOUSE_USER,
    CLICKHOUSE_PASSWORD,
)
from app.etl.transform import run_transform_for_all_cities


def get_ch_client() -> Client:
    return Client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        user=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASSWORD,
        database=CLICKHOUSE_DB,
    )


def create_tables(client: Client) -> None:
    client.execute(
        """
        CREATE TABLE IF NOT EXISTS weather_hourly
        (
            city            LowCardinality(String),
            city_name       String,
            ts              DateTime,
            temperature     Float32,
            precipitation   Float32,
            wind_speed      Float32,
            wind_direction  Float32,
            date            Date DEFAULT toDate(ts)
        )
        ENGINE = MergeTree
        PARTITION BY date
        ORDER BY (city, ts)
        """
    )

    client.execute(
        """
        CREATE TABLE IF NOT EXISTS weather_daily
        (
            city            LowCardinality(String),
            city_name       String,
            date            Date,
            temp_min        Float32,
            temp_max        Float32,
            temp_avg        Float32,
            precip_sum      Float32,
            max_wind_speed  Float32,
            strong_wind     UInt8,
            heavy_precip    UInt8
        )
        ENGINE = MergeTree
        PARTITION BY date
        ORDER BY (city, date)
        """
    )


def load_hourly(client: Client, records: List[Dict]) -> None:
    if not records:
        print("Нет записей для weather_hourly")
        return

    data = []
    for r in records:
        ts = r["ts"]
        if isinstance(ts, str):
            ts = ts.replace("Z", "")
            ts = datetime.fromisoformat(ts)

        data.append(
            (
                r["city"],
                r["city_name"],
                ts,
                float(r["temperature"]),
                float(r["precipitation"]),
                float(r["wind_speed"]),
                float(r["wind_direction"]),
            )
        )

    client.execute(
        """
        INSERT INTO weather_hourly
            (city, city_name, ts, temperature, precipitation, wind_speed, wind_direction)
        VALUES
        """,
        data,
    )

    print(f"Вставлено в weather_hourly: {len(data)} строк")



def load_daily(client: Client, records: List[Dict]) -> None:
    if not records:
        print("Нет записей для weather_daily")
        return

    data = []
    for r in records:
        d = r["date"]
        if isinstance(d, str):
            d = datetime.fromisoformat(d).date()

        data.append(
            (
                r["city"],
                r["city_name"],
                d,
                float(r["temp_min"]),
                float(r["temp_max"]),
                float(r["temp_avg"]),
                float(r["precip_sum"]),
                float(r["max_wind_speed"]),
                int(r["strong_wind"]),
                int(r["heavy_precip"]),
            )
        )

    client.execute(
        """
        INSERT INTO weather_daily
            (city, city_name, date, temp_min, temp_max, temp_avg,
             precip_sum, max_wind_speed, strong_wind, heavy_precip)
        VALUES
        """,
        data,
    )

    print(f"Вставлено в weather_daily: {len(data)} строк")

def run_full_etl_once() -> None:
    hourly_records, daily_records = run_transform_for_all_cities()

    client = get_ch_client()
    create_tables(client)

    load_hourly(client, hourly_records)
    load_daily(client, daily_records)


if __name__ == "__main__":
    run_full_etl_once()
