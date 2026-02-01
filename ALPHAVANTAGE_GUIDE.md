# Alpha Vantage Integration Guide

## Overview

Alpha Vantage is now integrated as an additional data source. Unlike the old approach of immediately parsing data into structured format, **we now store raw JSON responses first**, then parse them later.

## Key Design Changes

### 1. Raw Data Storage

We introduced a new table `stock_price_raw` with the following schema:

- `id` (PK): Auto-increment primary key
- `stock_code`: Stock symbol (e.g., "AAPL")
- `price_date_range`: Date range of data (e.g., "2024-01-01 to 2024-12-31")
- `time_granularity`: Time granularity (daily, weekly, monthly, intraday_1min, etc.)
- `crawl_save_time`: When data was fetched and saved
- `response_json`: **Original JSON response from API** (TEXT field)
- `data_source`: Data source identifier (alphavantage, yfinance, polygon, etc.)
- `api_function`: API function/endpoint used
- `api_params`: API parameters (JSON format)
- `response_status`: success, error, or partial
- `error_message`: Error details if any

### 2. Why Store Raw Data First?

**Advantages:**
- ✅ **Flexibility**: Parse data later based on actual structure
- ✅ **Completeness**: Retain all original data fields
- ✅ **Debugging**: Easy to inspect raw responses
- ✅ **Reprocessing**: Can re-parse historical data with new logic
- ✅ **Multi-source**: Different APIs have different schemas
- ✅ **Future-proof**: New fields from API don't break existing code

## Getting Started

### 1. Get Alpha Vantage API Key

1. Visit: https://www.alphavantage.co/support/#api-key
2. Sign up for a **free** API key
3. Free tier allows: **5 API calls per minute**, 500 calls per day

### 2. Configure Environment

Add to your `.env` file:

```bash
# Alpha Vantage Configuration
ALPHAVANTAGE_API_KEY=your_api_key_here
ALPHAVANTAGE_ENABLED=true

# Rate limiting (adjust based on your API tier)
API_REQUEST_DELAY=12.0  # 12 seconds = 5 calls/min for free tier
API_MAX_RETRIES=3
API_RETRY_DELAY=15.0
```

### 3. Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt
```

### 4. Run Example Script

```bash
python example_alphavantage.py
```

This will:
1. Check if Alpha Vantage API is available
2. Fetch daily data for AAPL, MSFT, GOOGL
3. Save raw JSON responses to `stock_price_raw` table
4. Query and display saved data

## Architecture

### Components

1. **AlphaVantageDataSource** (`src/data_sources/alphavantage_source.py`)
   - Implements `fetch_raw_data()` method
   - Returns dictionary with raw JSON and metadata
   - Handles rate limiting and retries
   - Extracts date ranges from responses

2. **RawDataStorage** (`src/storage/raw_storage.py`)
   - Stores raw JSON responses
   - Provides querying methods
   - Tracks success/error status

3. **StockPriceRaw Model** (`src/models/stock_price_raw.py`)
   - SQLAlchemy ORM model
   - Maps to `stock_price_raw` table
   - Includes indexes for efficient queries

### Data Flow

```
Alpha Vantage API
    ↓
fetch_raw_data()  (with rate limiting & retries)
    ↓
Raw JSON Response + Metadata
    ↓
save_raw_response()
    ↓
stock_price_raw table (MySQL)
    ↓
[Future] ETL Job: Parse & Transform
    ↓
[Future] Structured tables (stock_data, etc.)
```

## API Functions Supported

Alpha Vantage provides various functions:

### Time Series Functions

1. **TIME_SERIES_DAILY**
   - Daily stock prices (open, high, low, close, volume)
   - `outputsize`: "compact" (100 points) or "full" (20+ years)

2. **TIME_SERIES_WEEKLY**
   - Weekly aggregated data

3. **TIME_SERIES_MONTHLY**
   - Monthly aggregated data

4. **TIME_SERIES_INTRADAY**
   - Intraday data: 1min, 5min, 15min, 30min, 60min intervals
   - Limited to last 1-2 months

### Example Usage

```python
from src.data_sources.alphavantage_source import AlphaVantageDataSource
from src.storage.raw_storage import RawDataStorage

# Initialize
av = AlphaVantageDataSource(api_key="YOUR_KEY")
storage = RawDataStorage(database_url="mysql+pymysql://...")

# Fetch daily data
result = av.fetch_raw_data(
    symbol="AAPL",
    function="TIME_SERIES_DAILY",
    outputsize="compact"
)

# Save raw response
if result['status'] == 'success':
    storage.save_raw_response(
        stock_code="AAPL",
        response_json=result['response_json'],
        data_source="alphavantage",
        time_granularity="daily",
        price_date_range=result.get('date_range'),
        api_function=result['api_function'],
        api_params=result['api_params'],
        response_status="success"
    )
```

## Querying Raw Data

### Get Latest Data

```python
latest = storage.get_latest_raw_data(
    stock_code="AAPL",
    data_source="alphavantage",
    time_granularity="daily"
)

if latest:
    import json
    data = json.loads(latest.response_json)
    # Process data...
```

### SQL Queries

```sql
-- Get latest successful fetch
SELECT * FROM stock_price_raw
WHERE stock_code = 'AAPL' 
  AND data_source = 'alphavantage'
  AND response_status = 'success'
ORDER BY crawl_save_time DESC
LIMIT 1;

-- Count by source
SELECT data_source, response_status, COUNT(*)
FROM stock_price_raw
GROUP BY data_source, response_status;
```

See `raw_data_schema.sql` for more query examples.

## Rate Limiting

### Free Tier Limits

- **5 API calls per minute**
- **500 API calls per day**

### Strategies

1. **Request Delay**
   - Set `API_REQUEST_DELAY=12.0` (12 seconds between calls)
   - Ensures < 5 calls per minute

2. **Retry Logic**
   - Automatic retries with exponential backoff
   - Configurable via `API_MAX_RETRIES` and `API_RETRY_DELAY`

3. **Batch Processing**
   - For fetching all stocks, spread over multiple days
   - Example: 500 stocks = 1 day for full batch

## Next Steps

### 1. Analyze Raw Data

```python
import json

# Load from database
latest = storage.get_latest_raw_data("AAPL", "alphavantage", "daily")
data = json.loads(latest.response_json)

# Inspect structure
print(json.dumps(data, indent=2))
```

### 2. Design Parsing Logic

Based on actual data structure, create parsers:

```python
def parse_alphavantage_daily(response_json: str) -> List[StockData]:
    """Parse Alpha Vantage daily response to structured data"""
    data = json.loads(response_json)
    
    time_series = data.get('Time Series (Daily)', {})
    
    results = []
    for date_str, values in time_series.items():
        results.append(StockData(
            symbol=...,
            date=date_str,
            open=float(values['1. open']),
            high=float(values['2. high']),
            low=float(values['3. low']),
            close=float(values['4. close']),
            volume=int(values['5. volume']),
            data_source='alphavantage'
        ))
    
    return results
```

### 3. Create ETL Jobs

Build scheduled jobs to:
1. Fetch raw data from APIs
2. Store in `stock_price_raw`
3. Parse and transform to structured tables
4. Handle errors gracefully

## Production Deployment

### Docker Compose

The existing `docker-compose.yml` already supports the new schema:

```bash
# Start services
make start

# Run example
docker-compose exec app python example_alphavantage.py
```

### Cloud Deployment

1. Set environment variables:
   ```bash
   ALPHAVANTAGE_API_KEY=your_key
   ALPHAVANTAGE_ENABLED=true
   API_REQUEST_DELAY=12.0
   ```

2. Initialize database:
   ```bash
   # Schema will be auto-created by SQLAlchemy
   # Or manually run: raw_data_schema.sql
   ```

3. Monitor rate limits and adjust delays

## Comparison: Old vs New Approach

### Old Approach (Structured Data)

```
API → Parse immediately → StockData table
```

**Problems:**
- ❌ Different APIs have different schemas
- ❌ Lose fields not in StockData model
- ❌ Hard to debug parsing issues
- ❌ Can't reprocess historical data

### New Approach (Raw Data First)

```
API → Save raw JSON → stock_price_raw table
                    ↓
         [Later] Parse → Structured tables
```

**Benefits:**
- ✅ Keep all original data
- ✅ Flexible parsing logic
- ✅ Easy debugging
- ✅ Can reprocess anytime
- ✅ Multi-source compatible

## Troubleshooting

### API Key Issues

```
Error: Invalid API call
```

**Solution:** Check your API key in `.env`

### Rate Limit Errors

```
Error: API call frequency limit reached
```

**Solution:** Increase `API_REQUEST_DELAY` or wait

### Database Connection

```
Error: Cannot connect to database
```

**Solution:** Check MySQL is running and credentials are correct

## Resources

- [Alpha Vantage Documentation](https://www.alphavantage.co/documentation/)
- [API Support](https://www.alphavantage.co/support/)
- [Pricing Plans](https://www.alphavantage.co/premium/)

## License

MIT

