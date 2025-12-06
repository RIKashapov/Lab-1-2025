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
    strong_wind     UInt8,   -- 1 если ветер > порога
    heavy_precip    UInt8    -- 1 если осадков > порога
)
ENGINE = MergeTree
PARTITION BY date
ORDER BY (city, date);
