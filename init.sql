-- Initialize database schema and basic settings
-- This script runs automatically when MySQL container is first created

USE stock_data;

-- Set timezone
SET GLOBAL time_zone = '+00:00';
SET time_zone = '+00:00';

-- Optimize MySQL settings for stock data workload
SET GLOBAL innodb_buffer_pool_size = 256M;
SET GLOBAL max_connections = 200;

-- Grant additional privileges if needed
GRANT ALL PRIVILEGES ON stock_data.* TO 'stock_user'@'%';
FLUSH PRIVILEGES;

-- Log initialization
SELECT 'Database initialized successfully' AS status;

