-- Table for raw data
CREATE TABLE IF NOT EXISTS raw_bitcoin_data (
    timestamp BIGINT,
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
    quarter TEXT,
    avg_price NUMERIC,
    min_price NUMERIC,
    max_price NUMERIC,
    total_volume NUMERIC
);
