-- 常用查询示例
-- 在MySQL中运行这些查询来分析股票数据

-- ======================================
-- 1. 基本查询
-- ======================================

-- 查看最新的10条记录
SELECT symbol, date, close_price, volume, market_cap, pe_ratio
FROM stock_data
ORDER BY date DESC, symbol
LIMIT 10;

-- 查看所有跟踪的股票及其数据量
SELECT 
    symbol,
    COUNT(*) as record_count,
    MIN(date) as earliest_date,
    MAX(date) as latest_date,
    DATEDIFF(MAX(date), MIN(date)) as days_span
FROM stock_data
GROUP BY symbol
ORDER BY symbol;

-- ======================================
-- 2. 价格分析
-- ======================================

-- 查看某个股票的最新价格和变化
SELECT 
    symbol,
    date,
    close_price,
    volume,
    LAG(close_price) OVER (PARTITION BY symbol ORDER BY date) as prev_close,
    ROUND((close_price - LAG(close_price) OVER (PARTITION BY symbol ORDER BY date)) / 
          LAG(close_price) OVER (PARTITION BY symbol ORDER BY date) * 100, 2) as change_pct
FROM stock_data
WHERE symbol = 'AAPL'
ORDER BY date DESC
LIMIT 10;

-- 查看所有股票的最新价格和日涨跌幅
WITH latest_two_days AS (
    SELECT 
        symbol,
        date,
        close_price,
        ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY date DESC) as rn
    FROM stock_data
)
SELECT 
    t1.symbol,
    t1.date as latest_date,
    t1.close_price as latest_price,
    t2.close_price as prev_price,
    ROUND((t1.close_price - t2.close_price) / t2.close_price * 100, 2) as change_pct
FROM latest_two_days t1
LEFT JOIN latest_two_days t2 ON t1.symbol = t2.symbol AND t2.rn = 2
WHERE t1.rn = 1
ORDER BY change_pct DESC;

-- ======================================
-- 3. 统计分析
-- ======================================

-- 计算过去30天的统计数据
SELECT 
    symbol,
    COUNT(*) as trading_days,
    ROUND(AVG(close_price), 2) as avg_price,
    ROUND(MIN(low_price), 2) as min_price,
    ROUND(MAX(high_price), 2) as max_price,
    ROUND(AVG(volume), 0) as avg_volume,
    ROUND(MAX(close_price) / MIN(close_price) * 100 - 100, 2) as price_range_pct
FROM stock_data
WHERE date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY symbol
ORDER BY price_range_pct DESC;

-- 计算移动平均线 (5日、20日)
SELECT 
    symbol,
    date,
    close_price,
    ROUND(AVG(close_price) OVER (
        PARTITION BY symbol 
        ORDER BY date 
        ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
    ), 2) as ma5,
    ROUND(AVG(close_price) OVER (
        PARTITION BY symbol 
        ORDER BY date 
        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    ), 2) as ma20
FROM stock_data
WHERE symbol = 'AAPL'
ORDER BY date DESC
LIMIT 30;

-- ======================================
-- 4. 市值和估值分析
-- ======================================

-- 查看最新市值排名
WITH latest_data AS (
    SELECT 
        symbol,
        market_cap,
        pe_ratio,
        close_price,
        ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY date DESC) as rn
    FROM stock_data
    WHERE market_cap IS NOT NULL
)
SELECT 
    symbol,
    ROUND(market_cap / 1e9, 2) as market_cap_billion,
    ROUND(pe_ratio, 2) as pe_ratio,
    close_price
FROM latest_data
WHERE rn = 1
ORDER BY market_cap DESC;

-- 查看PE估值最低的股票
WITH latest_data AS (
    SELECT 
        symbol,
        pe_ratio,
        close_price,
        market_cap,
        ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY date DESC) as rn
    FROM stock_data
    WHERE pe_ratio IS NOT NULL AND pe_ratio > 0
)
SELECT 
    symbol,
    ROUND(pe_ratio, 2) as pe_ratio,
    close_price,
    ROUND(market_cap / 1e9, 2) as market_cap_billion
FROM latest_data
WHERE rn = 1
ORDER BY pe_ratio ASC
LIMIT 10;

-- ======================================
-- 5. 成交量分析
-- ======================================

-- 查看成交量异常放大的股票 (最近一天 vs 30天平均)
WITH volume_stats AS (
    SELECT 
        symbol,
        date,
        volume,
        AVG(volume) OVER (
            PARTITION BY symbol 
            ORDER BY date 
            ROWS BETWEEN 30 PRECEDING AND 1 PRECEDING
        ) as avg_volume_30d,
        ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY date DESC) as rn
    FROM stock_data
)
SELECT 
    symbol,
    date,
    volume as latest_volume,
    ROUND(avg_volume_30d, 0) as avg_volume_30d,
    ROUND(volume / avg_volume_30d, 2) as volume_ratio
FROM volume_stats
WHERE rn = 1 AND avg_volume_30d > 0
ORDER BY volume_ratio DESC
LIMIT 10;

-- ======================================
-- 6. 数据质量检查
-- ======================================

-- 检查数据完整性
SELECT 
    symbol,
    COUNT(*) as total_records,
    SUM(CASE WHEN close_price IS NULL THEN 1 ELSE 0 END) as missing_close,
    SUM(CASE WHEN volume IS NULL THEN 1 ELSE 0 END) as missing_volume,
    SUM(CASE WHEN market_cap IS NULL THEN 1 ELSE 0 END) as missing_market_cap,
    SUM(CASE WHEN pe_ratio IS NULL THEN 1 ELSE 0 END) as missing_pe
FROM stock_data
GROUP BY symbol;

-- 查看数据更新情况
SELECT 
    symbol,
    MAX(date) as latest_data_date,
    DATEDIFF(CURDATE(), MAX(date)) as days_behind,
    MAX(updated_at) as last_update_time
FROM stock_data
GROUP BY symbol
ORDER BY latest_data_date DESC;

-- ======================================
-- 7. 导出数据
-- ======================================

-- 导出某个股票的完整历史数据
SELECT 
    date,
    open_price,
    high_price,
    low_price,
    close_price,
    adj_close_price,
    volume,
    market_cap,
    pe_ratio,
    turnover_rate
FROM stock_data
WHERE symbol = 'AAPL'
ORDER BY date;

-- 导出所有股票的最新数据 (可用于dashboard)
WITH latest_data AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY date DESC) as rn
    FROM stock_data
)
SELECT 
    symbol,
    date,
    close_price,
    volume,
    market_cap,
    pe_ratio,
    turnover_rate
FROM latest_data
WHERE rn = 1
ORDER BY symbol;

-- ======================================
-- 8. 性能优化查询
-- ======================================

-- 查看表大小和索引使用情况
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb,
    table_rows
FROM information_schema.TABLES
WHERE table_schema = 'stock_data' AND table_name = 'stock_data';

-- 查看索引统计
SHOW INDEX FROM stock_data;

