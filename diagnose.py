#!/usr/bin/env python3
"""
Quick diagnostic script to test Yahoo Finance connectivity
Run this to diagnose connection issues
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("Yahoo Finance Connectivity Diagnostic")
print("=" * 60)
print()

# Test 1: Check internet connectivity
print("1. Testing internet connectivity...")
try:
    import requests
    response = requests.get("https://www.google.com", timeout=5)
    if response.status_code == 200:
        print("   ✓ Internet connection OK")
    else:
        print(f"   ✗ Internet issue: status {response.status_code}")
except Exception as e:
    print(f"   ✗ Cannot connect to internet: {e}")
    sys.exit(1)

# Test 2: Check Yahoo Finance domain
print("\n2. Testing Yahoo Finance domain...")
try:
    response = requests.get("https://finance.yahoo.com", timeout=10)
    print(f"   ✓ Yahoo Finance reachable (status: {response.status_code})")
except Exception as e:
    print(f"   ✗ Cannot reach Yahoo Finance: {e}")

# Test 3: Test yfinance library
print("\n3. Testing yfinance library...")
try:
    import yfinance as yf
    print(f"   ✓ yfinance version: {yf.__version__}")
except Exception as e:
    print(f"   ✗ yfinance import failed: {e}")
    sys.exit(1)

# Test 4: Try to fetch data with different methods
print("\n4. Testing data fetch methods...")

print("\n   Method 1: Using Ticker.history()...")
try:
    ticker = yf.Ticker("AAPL")
    hist = ticker.history(period="5d")
    if not hist.empty:
        print(f"   ✓ Successfully fetched {len(hist)} days of data")
        print(f"     Latest close: ${hist['Close'].iloc[-1]:.2f}")
    else:
        print("   ✗ No data returned")
except Exception as e:
    print(f"   ✗ Failed: {e}")

print("\n   Method 2: Using download()...")
try:
    import pandas as pd
    from datetime import datetime, timedelta
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5)
    
    data = yf.download("AAPL", start=start_date, end=end_date, progress=False)
    if not data.empty:
        print(f"   ✓ Successfully downloaded {len(data)} days of data")
        print(f"     Latest close: ${data['Close'].iloc[-1]:.2f}")
    else:
        print("   ✗ No data returned")
except Exception as e:
    print(f"   ✗ Failed: {e}")

print("\n" + "=" * 60)
print("Diagnostic Summary")
print("=" * 60)

print("""
If all tests passed:
  ✓ Your setup is working! The earlier error might have been temporary.
  
If some tests failed:
  - Try again in a few minutes (rate limiting)
  - Check your internet connection
  - Check if you're behind a firewall/proxy
  - Yahoo Finance might be temporarily down
  
Next steps:
  1. Wait 5-10 minutes and try again
  2. Run: python test_setup.py
  3. Or skip to Docker: docker-compose up -d
""")

