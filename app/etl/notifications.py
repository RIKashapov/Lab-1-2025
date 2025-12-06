from typing import List, Dict
import requests

from app.config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID


def build_forecast_message(daily_records: List[Dict]) -> str:
    lines = []
    lines.append("📡 Прогноз погоды на завтра:\n")

    for r in daily_records:
        city_name = r["city_name"]
        date = r["date"]
        temp_min = r["temp_min"]
        temp_max = r["temp_max"]
        temp_avg = r["temp_avg"]
        precip_sum = r["precip_sum"]
        max_wind = r["max_wind_speed"]
        strong_wind = bool(r["strong_wind"])
        heavy_precip = bool(r["heavy_precip"])

        line = (
            f"<b>{city_name}</b> ({date})\n"
            f"Мин: {temp_min:.1f}°C, Макс: {temp_max:.1f}°C, Средняя: {temp_avg:.1f}°C\n"
            f"Осадки за день: {precip_sum:.1f} мм\n"
            f"Макс. ветер: {max_wind:.1f} м/с"
        )

        warnings = []
        if strong_wind:
            warnings.append("сильный ветер")
        if heavy_precip:
            warnings.append("сильные осадки")

        if warnings:
            line += "\n  " + " / ".join(warnings)

        lines.append(line + "\n")

    return "\n".join(lines)


def send_forecast_notification(daily_records: List[Dict]) -> None:
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram не настроен (нет TELEGRAM_TOKEN или TELEGRAM_CHAT_ID), уведомление пропущено")
        return

    text = build_forecast_message(daily_records)

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }

    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    print("Уведомление отправлено в Telegram")
