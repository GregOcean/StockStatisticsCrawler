#!/usr/bin/env python3
"""
Utility script for common operations
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config import get_settings
from src.storage import MySQLStorage


def show_stats():
    """Show database statistics"""
    settings = get_settings()
    storage = MySQLStorage(settings.get_database_url())
    
    if not storage.connect():
        print("Failed to connect to database")
        return
    
    print("\n" + "=" * 60)
    print("Stock Data Statistics")
    print("=" * 60 + "\n")
    
    # Get symbols and their data counts
    from sqlalchemy import select, func
    from src.models import StockData
    
    session = storage.SessionLocal()
    
    try:
        # Total records
        total = session.query(func.count(StockData.id)).scalar()
        print(f"Total records: {total:,}")
        
        # Per symbol stats
        results = session.query(
            StockData.symbol,
            func.count(StockData.id).label('count'),
            func.min(StockData.date).label('min_date'),
            func.max(StockData.date).label('max_date')
        ).group_by(StockData.symbol).all()
        
        print(f"\nData by symbol ({len(results)} symbols):\n")
        print(f"{'Symbol':<10} {'Records':>10} {'From':>12} {'To':>12}")
        print("-" * 50)
        
        for row in results:
            print(f"{row.symbol:<10} {row.count:>10,} {str(row.min_date):>12} {str(row.max_date):>12}")
        
    finally:
        session.close()
        storage.disconnect()
    
    print()


def list_symbols():
    """List all tracked symbols"""
    settings = get_settings()
    print("\nConfigured stock symbols:")
    for symbol in settings.symbols_list:
        print(f"  - {symbol}")
    print()


def add_symbols(symbols: list):
    """Add new symbols to configuration"""
    print(f"\nTo add symbols: {', '.join(symbols)}")
    print("Please edit the .env file and add them to STOCK_SYMBOLS")
    print("Then restart the service: make restart")
    print()


def query_latest(symbol: str):
    """Query latest data for a symbol"""
    settings = get_settings()
    storage = MySQLStorage(settings.get_database_url())
    
    if not storage.connect():
        print("Failed to connect to database")
        return
    
    from sqlalchemy import select
    from src.models import StockData
    
    session = storage.SessionLocal()
    
    try:
        result = session.query(StockData).filter(
            StockData.symbol == symbol.upper()
        ).order_by(StockData.date.desc()).limit(10).all()
        
        if not result:
            print(f"\nNo data found for {symbol}")
            return
        
        print(f"\nLatest 10 records for {symbol}:")
        print("-" * 80)
        
        for record in result:
            print(f"{record.date} | Close: ${record.close_price:.2f} | "
                  f"Volume: {record.volume:,} | "
                  f"PE: {record.pe_ratio:.2f if record.pe_ratio else 'N/A'}")
        
    finally:
        session.close()
        storage.disconnect()
    
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Stock Crawler Utility Script"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Stats command
    subparsers.add_parser('stats', help='Show database statistics')
    
    # List command
    subparsers.add_parser('list', help='List configured symbols')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add new symbols')
    add_parser.add_argument('symbols', nargs='+', help='Symbol(s) to add')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query latest data for a symbol')
    query_parser.add_argument('symbol', help='Stock symbol to query')
    
    args = parser.parse_args()
    
    if args.command == 'stats':
        show_stats()
    elif args.command == 'list':
        list_symbols()
    elif args.command == 'add':
        add_symbols(args.symbols)
    elif args.command == 'query':
        query_latest(args.symbol)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

