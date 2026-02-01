-- SQL schema for raw stock price data

CREATE TABLE IF NOT EXISTS stock_price_raw (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Primary key',
    
    stock_code VARCHAR(20) NOT NULL COMMENT 'Stock symbol/code',
    
    price_date_range VARCHAR(100) NULL COMMENT 'Date range of price data',
    
    time_granularity VARCHAR(50) NOT NULL COMMENT 'Time granularity: daily, weekly, monthly, etc.',
    
    crawl_save_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'When this data was crawled and saved',
    
    response_json TEXT NOT NULL COMMENT 'Original JSON response from API',
    
    data_source VARCHAR(50) NOT NULL COMMENT 'Data source: yfinance, alphavantage, polygon, etc.',
    
    api_function VARCHAR(100) NULL COMMENT 'API function/endpoint used',
    
    api_params TEXT NULL COMMENT 'API parameters used (JSON format)',
    
    response_status VARCHAR(20) NOT NULL DEFAULT 'success' COMMENT 'Response status: success, error, partial',
    
    error_message TEXT NULL COMMENT 'Error message if any',
    
    -- Indexes for efficient querying
    INDEX idx_stock_code (stock_code),
    INDEX idx_data_source (data_source),
    INDEX idx_crawl_time (crawl_save_time),
    INDEX idx_granularity (time_granularity),
    INDEX idx_stock_source (stock_code, data_source),
    INDEX idx_stock_source_time (stock_code, data_source, crawl_save_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Raw stock price data from various API sources';

-- Query examples

-- Get latest raw data for a stock
SELECT * FROM stock_price_raw
WHERE stock_code = 'AAPL' 
  AND data_source = 'alphavantage'
  AND response_status = 'success'
ORDER BY crawl_save_time DESC
LIMIT 1;

-- Get all successful fetches for a stock
SELECT 
    stock_code,
    data_source,
    time_granularity,
    price_date_range,
    crawl_save_time,
    api_function,
    CHAR_LENGTH(response_json) as json_size_bytes
FROM stock_price_raw
WHERE stock_code = 'AAPL'
  AND response_status = 'success'
ORDER BY crawl_save_time DESC;

-- Get failed fetches for debugging
SELECT 
    stock_code,
    data_source,
    crawl_save_time,
    error_message
FROM stock_price_raw
WHERE response_status = 'error'
ORDER BY crawl_save_time DESC
LIMIT 10;

-- Count records by source
SELECT 
    data_source,
    response_status,
    COUNT(*) as count
FROM stock_price_raw
GROUP BY data_source, response_status;

-- Get latest fetch time for each stock
SELECT 
    stock_code,
    data_source,
    MAX(crawl_save_time) as latest_fetch
FROM stock_price_raw
WHERE response_status = 'success'
GROUP BY stock_code, data_source
ORDER BY stock_code;

-- Find stocks with data in date range
SELECT 
    stock_code,
    data_source,
    price_date_range,
    crawl_save_time
FROM stock_price_raw
WHERE price_date_range LIKE '%2024%'
  AND response_status = 'success'
ORDER BY stock_code;

