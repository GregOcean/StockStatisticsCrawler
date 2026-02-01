"""Example script for fetching raw data from Alpha Vantage"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config.settings import get_settings
from src.data_sources.alphavantage_source import AlphaVantageDataSource
from src.storage.raw_storage import RawDataStorage

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function to demonstrate Alpha Vantage integration"""
    
    logger.info("=== Alpha Vantage Raw Data Example ===")
    
    # Load settings
    settings = get_settings()
    
    # Check if Alpha Vantage is configured
    if not settings.alphavantage_api_key:
        logger.error(
            "Alpha Vantage API key not configured. "
            "Please set ALPHAVANTAGE_API_KEY in .env file"
        )
        logger.info("\nTo get a free API key:")
        logger.info("1. Visit: https://www.alphavantage.co/support/#api-key")
        logger.info("2. Sign up for a free API key")
        logger.info("3. Add to .env: ALPHAVANTAGE_API_KEY=your_key_here")
        return
    
    # Initialize Alpha Vantage data source
    logger.info("Initializing Alpha Vantage data source...")
    av_source = AlphaVantageDataSource(
        api_key=settings.alphavantage_api_key,
        request_delay=settings.api_request_delay,
        max_retries=settings.api_max_retries,
        retry_delay=settings.api_retry_delay
    )
    
    # Check availability
    logger.info("Checking Alpha Vantage API availability...")
    if not av_source.is_available():
        logger.error("Alpha Vantage API is not available")
        return
    
    logger.info("✅ Alpha Vantage API is available")
    
    # Initialize storage
    logger.info("Initializing raw data storage...")
    storage = RawDataStorage(database_url=settings.get_database_url())
    
    if not storage.connect():
        logger.error("Failed to connect to database")
        return
    
    logger.info("✅ Connected to database")
    
    # Initialize schema
    if not storage.initialize_schema():
        logger.error("Failed to initialize database schema")
        return
    
    logger.info("✅ Database schema initialized")
    
    # Test fetching data for a few stocks
    test_symbols = ["AAPL", "MSFT", "GOOGL"]
    
    for symbol in test_symbols:
        logger.info(f"\n--- Fetching data for {symbol} ---")
        
        # Fetch daily data
        result = av_source.fetch_raw_data(
            symbol=symbol,
            function="TIME_SERIES_DAILY",
            outputsize="compact"  # Last 100 data points
        )
        
        if result['status'] == 'success':
            logger.info(f"✅ Successfully fetched data for {symbol}")
            
            # Save to database
            saved = storage.save_raw_response(
                stock_code=symbol,
                response_json=result['response_json'],
                data_source="alphavantage",
                time_granularity="daily",
                price_date_range=result.get('date_range'),
                api_function=result.get('api_function'),
                api_params=result.get('api_params'),
                response_status=result['status'],
                error_message=result.get('error_message')
            )
            
            if saved:
                logger.info(f"✅ Saved raw data for {symbol} to database")
            else:
                logger.error(f"❌ Failed to save data for {symbol}")
        else:
            logger.error(f"❌ Failed to fetch data for {symbol}: {result.get('error_message')}")
            
            # Still save error response for debugging
            storage.save_raw_response(
                stock_code=symbol,
                response_json=result['response_json'],
                data_source="alphavantage",
                time_granularity="daily",
                api_function=result.get('api_function'),
                api_params=result.get('api_params'),
                response_status="error",
                error_message=result.get('error_message')
            )
    
    # Query latest data
    logger.info("\n--- Querying latest data ---")
    for symbol in test_symbols:
        latest = storage.get_latest_raw_data(
            stock_code=symbol,
            data_source="alphavantage",
            time_granularity="daily"
        )
        
        if latest:
            logger.info(
                f"{symbol}: {latest.response_status}, "
                f"date_range={latest.price_date_range}, "
                f"saved_at={latest.crawl_save_time}"
            )
        else:
            logger.info(f"{symbol}: No data found")
    
    # Cleanup
    storage.disconnect()
    logger.info("\n=== Example completed ===")
    logger.info("\nNext steps:")
    logger.info("1. Check database table 'stock_price_raw' for saved data")
    logger.info("2. Analyze the raw JSON responses")
    logger.info("3. Design parsing logic based on actual data structure")
    logger.info("4. Create ETL jobs to transform raw data to structured format")


if __name__ == "__main__":
    main()

