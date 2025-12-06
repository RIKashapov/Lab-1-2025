from typing import List, Dict, Tuple

from prefect import flow, task, get_run_logger

from app.etl.extract import run_extract_for_all_cities
from app.etl.transform import run_transform_for_all_cities
from app.etl.load import get_ch_client, create_tables, load_hourly, load_daily
from app.etl.notifications import send_forecast_notification

@task
def extract_task() -> None:
    logger = get_run_logger()
    logger.info("Начинаем этап Extract (Open-Meteo -> MinIO)")
    run_extract_for_all_cities()
    logger.info("Extract завершён")


@task
def transform_task() -> Tuple[List[Dict], List[Dict]]:
    logger = get_run_logger()
    logger.info("Начинаем этап Transform (MinIO -> нормализованные структуры)")

    hourly_records, daily_records = run_transform_for_all_cities()

    logger.info(
        f"Transform завершён: hourly={len(hourly_records)} записей, "
        f"daily={len(daily_records)} записей"
    )

    return hourly_records, daily_records


@task
def load_task(hourly_records: List[Dict], daily_records: List[Dict]) -> None:
    logger = get_run_logger()
    logger.info("Начинаем этап Load")

    client = get_ch_client()
    create_tables(client)

    load_hourly(client, hourly_records)
    load_daily(client, daily_records)

    logger.info("Load завершён")

@task
def notify_task(daily_records: List[Dict]) -> None:
    logger = get_run_logger()
    logger.info("Начинаем отправку уведомления в Telegram")
    send_forecast_notification(daily_records)
    logger.info("Уведомление отправлено")

@flow(name="weather_etl")
def weather_etl_flow() -> None:
    extract_task()
    hourly_records, daily_records = transform_task()
    load_task(hourly_records, daily_records)
    notify_task(daily_records)

if __name__ == "__main__":
    weather_etl_flow()
