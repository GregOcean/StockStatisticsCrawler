#!/usr/bin/env python3
"""
Yahoo Finance API Test Demo
独立测试模块，用于验证API有效性

Usage:
    python demo_api_test.py
"""

import sys
from datetime import datetime, timedelta


def test_basic_import():
    """测试基础导入"""
    print("\n" + "=" * 60)
    print("Test 1: Import yfinance")
    print("=" * 60)
    
    try:
        import yfinance as yf
        print(f"✓ yfinance imported successfully")
        print(f"  Version: {yf.__version__}")
        return True
    except ImportError as e:
        print(f"✗ Failed to import yfinance: {e}")
        print("\n  Fix: pip install yfinance")
        return False


def test_simple_ticker():
    """测试简单的ticker查询"""
    print("\n" + "=" * 60)
    print("Test 2: Simple Ticker Query")
    print("=" * 60)
    
    try:
        import yfinance as yf
        
        print("Creating ticker for AAPL...")
        ticker = yf.Ticker("AAPL")
        
        print("✓ Ticker object created")
        return ticker
    except Exception as e:
        print(f"✗ Failed: {e}")
        return None


def test_history_data(ticker=None):
    """测试历史数据获取"""
    print("\n" + "=" * 60)
    print("Test 3: Fetch Historical Data")
    print("=" * 60)
    
    if ticker is None:
        import yfinance as yf
        ticker = yf.Ticker("AAPL")
    
    try:
        print("Fetching last 5 days of data...")
        hist = ticker.history(period="5d")
        
        if hist.empty:
            print("✗ No data returned (empty DataFrame)")
            return False
        
        print(f"✓ Successfully fetched {len(hist)} days")
        print("\nData preview:")
        print(hist[['Open', 'High', 'Low', 'Close', 'Volume']].tail())
        
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_download_function():
    """测试download函数"""
    print("\n" + "=" * 60)
    print("Test 4: Using yf.download()")
    print("=" * 60)
    
    try:
        import yfinance as yf
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        print(f"Downloading AAPL data from {start_date.date()} to {end_date.date()}...")
        data = yf.download(
            "AAPL", 
            start=start_date, 
            end=end_date,
            progress=False
        )
        
        if data.empty:
            print("✗ No data returned")
            return False
        
        print(f"✓ Successfully downloaded {len(data)} days")
        print(f"  Date range: {data.index[0].date()} to {data.index[-1].date()}")
        print(f"  Latest close: ${data['Close'].iloc[-1]:.2f}")
        
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_symbols():
    """测试多个股票代码"""
    print("\n" + "=" * 60)
    print("Test 5: Multiple Symbols")
    print("=" * 60)
    
    try:
        import yfinance as yf
        
        symbols = ["AAPL", "MSFT", "GOOGL"]
        print(f"Testing symbols: {', '.join(symbols)}")
        
        results = {}
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                
                if not hist.empty:
                    price = hist['Close'].iloc[-1]
                    results[symbol] = f"${price:.2f}"
                    print(f"  ✓ {symbol}: ${price:.2f}")
                else:
                    results[symbol] = "No data"
                    print(f"  ✗ {symbol}: No data")
                    
            except Exception as e:
                results[symbol] = f"Error: {e}"
                print(f"  ✗ {symbol}: {e}")
        
        success_count = sum(1 for v in results.values() if v.startswith("$"))
        print(f"\nSuccess rate: {success_count}/{len(symbols)}")
        
        return success_count > 0
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def test_ticker_info():
    """测试ticker详细信息"""
    print("\n" + "=" * 60)
    print("Test 6: Ticker Detailed Info")
    print("=" * 60)
    
    try:
        import yfinance as yf
        
        print("Fetching AAPL info...")
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        
        if not info:
            print("✗ No info returned")
            return False
        
        print("✓ Info retrieved successfully")
        print("\nKey information:")
        
        fields = [
            ('symbol', 'Symbol'),
            ('longName', 'Company'),
            ('marketCap', 'Market Cap'),
            ('trailingPE', 'P/E Ratio'),
            ('sector', 'Sector'),
            ('industry', 'Industry'),
        ]
        
        for field, label in fields:
            value = info.get(field, 'N/A')
            if field == 'marketCap' and value != 'N/A':
                value = f"${value/1e9:.2f}B"
            print(f"  {label}: {value}")
        
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        print("\nNote: ticker.info often fails due to rate limiting")
        print("      This is normal - historical data is more reliable")
        return False


def test_network():
    """测试网络连接"""
    print("\n" + "=" * 60)
    print("Test 0: Network Connectivity")
    print("=" * 60)
    
    try:
        import requests
        
        print("Testing internet connection...")
        response = requests.get("https://www.google.com", timeout=5)
        if response.status_code == 200:
            print("✓ Internet connection OK")
        else:
            print(f"⚠ Unexpected status: {response.status_code}")
        
        print("\nTesting Yahoo Finance domain...")
        response = requests.get("https://finance.yahoo.com", timeout=10)
        print(f"✓ Yahoo Finance reachable (status: {response.status_code})")
        
        return True
    except Exception as e:
        print(f"✗ Network test failed: {e}")
        return False


def main():
    """运行所有测试"""
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "Yahoo Finance API Test Demo" + " " * 15 + "║")
    print("╚" + "=" * 58 + "╝")
    
    results = {}
    
    # Test 0: Network
    results['network'] = test_network()
    
    # Test 1: Import
    results['import'] = test_basic_import()
    if not results['import']:
        print("\n✗ Cannot proceed without yfinance. Install it first.")
        return 1
    
    # Test 2: Ticker
    ticker = test_simple_ticker()
    results['ticker'] = ticker is not None
    
    # Test 3: History
    results['history'] = test_history_data(ticker)
    
    # Test 4: Download
    results['download'] = test_download_function()
    
    # Test 5: Multiple symbols
    results['multiple'] = test_multiple_symbols()
    
    # Test 6: Info (optional, often fails)
    results['info'] = test_ticker_info()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    critical_tests = ['network', 'import', 'history', 'download']
    critical_passed = sum(results.get(test, False) for test in critical_tests)
    
    print("\nCritical tests (must pass):")
    for test in critical_tests:
        status = "✓ PASS" if results.get(test) else "✗ FAIL"
        print(f"  {test.capitalize():<15} {status}")
    
    print("\nOptional tests:")
    for test in ['ticker', 'multiple', 'info']:
        status = "✓ PASS" if results.get(test) else "✗ FAIL"
        print(f"  {test.capitalize():<15} {status}")
    
    print("\n" + "=" * 60)
    
    if critical_passed == len(critical_tests):
        print("✓ ALL CRITICAL TESTS PASSED!")
        print("\nYour Yahoo Finance API is working correctly.")
        print("You can proceed with the main application.")
        return 0
    else:
        print(f"✗ {len(critical_tests) - critical_passed} critical test(s) failed")
        print("\nPossible issues:")
        print("  1. Rate limiting - wait 5-10 minutes and try again")
        print("  2. Network/firewall blocking Yahoo Finance")
        print("  3. Yahoo Finance service temporarily down")
        print("  4. Missing dependencies - run: pip install yfinance requests")
        print("\nTroubleshooting:")
        print("  - Try again later (rate limits are temporary)")
        print("  - Check your internet connection")
        print("  - Try using a VPN if in a restricted region")
        print("  - See RATE_LIMIT.md for more information")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

