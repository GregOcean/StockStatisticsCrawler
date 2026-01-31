"""
Test script to verify the application setup
Run this before deploying to ensure everything works
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import get_settings
from src.data_sources import YFinanceDataSource
from datetime import datetime, timedelta


def test_config():
    """Test configuration loading"""
    print("=" * 60)
    print("Testing Configuration...")
    print("=" * 60)
    
    try:
        settings = get_settings()
        print(f"✓ Configuration loaded successfully")
        print(f"  - Database: {settings.db_host}:{settings.db_port}/{settings.db_name}")
        print(f"  - Stock symbols: {settings.symbols_list}")
        print(f"  - Schedule: {settings.fetch_schedule}")
        print(f"  - Data source: {settings.default_data_source}")
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {str(e)}")
        return False


def test_data_source():
    """Test data source connectivity"""
    print("\n" + "=" * 60)
    print("Testing Data Source (Yahoo Finance)...")
    print("=" * 60)
    
    try:
        source = YFinanceDataSource()
        
        # Check availability
        if not source.is_available():
            print("✗ Yahoo Finance is not available")
            return False
        
        print("✓ Yahoo Finance is available")
        
        # Test fetching data for a known symbol
        print("\nFetching test data for AAPL...")
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=5)
        
        data = source.fetch_stock_data("AAPL", start_date, end_date)
        
        if data:
            print(f"✓ Successfully fetched {len(data)} records")
            print(f"\n  Sample record:")
            sample = data[0]
            print(f"  - Symbol: {sample.symbol}")
            print(f"  - Date: {sample.date}")
            print(f"  - Close: ${sample.close_price:.2f}" if sample.close_price else "  - Close: N/A")
            print(f"  - Volume: {sample.volume:,}" if sample.volume else "  - Volume: N/A")
            print(f"  - Market Cap: ${sample.market_cap:,.0f}" if sample.market_cap else "  - Market Cap: N/A")
            print(f"  - PE Ratio: {sample.pe_ratio:.2f}" if sample.pe_ratio else "  - PE Ratio: N/A")
            return True
        else:
            print("✗ No data returned")
            return False
    
    except Exception as e:
        print(f"✗ Data source test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_database_connection():
    """Test database connection (requires MySQL to be running)"""
    print("\n" + "=" * 60)
    print("Testing Database Connection...")
    print("=" * 60)
    
    try:
        from src.storage import MySQLStorage
        settings = get_settings()
        
        storage = MySQLStorage(settings.database_url)
        
        if storage.connect():
            print("✓ Database connection successful")
            storage.disconnect()
            return True
        else:
            print("✗ Database connection failed")
            print("  Make sure MySQL is running (docker-compose up -d mysql)")
            return False
    
    except Exception as e:
        print(f"✗ Database test failed: {str(e)}")
        print("  Make sure MySQL is running (docker-compose up -d mysql)")
        return False


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "Stock Crawler - System Test" + " " * 21 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    results = []
    
    # Test configuration
    results.append(("Configuration", test_config()))
    
    # Test data source
    results.append(("Data Source", test_data_source()))
    
    # Test database (optional if not running)
    results.append(("Database", test_database_connection()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:20s}: {status}")
    
    print()
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("✓ All tests passed! System is ready.")
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

