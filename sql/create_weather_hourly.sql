CREATE TABLE IF NOT EXISTS weather_hourly
(
    city            LowCardinality(String),  -- "moscow", "samara"
    city_name       String,                  -- "Москва", "Самара"
    ts              DateTime,                -- время часа
    temperature     Float32,                 -- температура, °C
    precipitation   Float32,                 -- осадки, мм
    wind_speed      Float32,                 -- скорость ветра, м/с
    wind_direction  Float32,                 -- направление ветра, градусы
    date            Date DEFAULT toDate(ts)  -- удобный ключ для партиционирования
)
ENGINE = MergeTree
PARTITION BY date
ORDER BY (city, ts);
