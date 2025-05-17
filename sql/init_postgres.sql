-- Table for raw data
CREATE TABLE IF NOT EXISTS raw_bitcoin_data (
    timestamp NUMERIC,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume NUMERIC
);

-- Table for staged data
CREATE TABLE IF NOT EXISTS staged_bitcoin_data (
    datetime TIMESTAMP,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume NUMERIC
);

-- Table for aggregated data
CREATE TABLE IF NOT EXISTS aggregated_bitcoin_data (
    year INT,
    quarter INT,
    avg_open NUMERIC,
    avg_close NUMERIC,
    min_low NUMERIC,
    max_high NUMERIC,
    total_volume NUMERIC,
    count_days INT
);
