"""Yahoo Finance data source implementation"""

import logging
import time
from typing import List, Optional
from datetime import datetime, date, timedelta
import yfinance as yf
import pandas as pd

from .base import BaseDataSource, StockDataDTO

logger = logging.getLogger(__name__)


class YFinanceDataSource(BaseDataSource):
    """Yahoo Finance data source implementation"""
    
    def __init__(self, request_delay: float = 2.0, max_retries: int = 5, retry_delay: float = 10.0):
        super().__init__(source_name="yfinance")
        self.request_delay = request_delay
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        logger.info(
            f"YFinance initialized with: delay={request_delay}s, "
            f"retries={max_retries}, retry_delay={retry_delay}s"
        )
    
    def fetch_stock_data(
        self,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[StockDataDTO]:
        """
        Fetch stock data from Yahoo Finance with rate limiting and retry
        
        Args:
            symbol: Stock ticker symbol
            start_date: Start date for data fetch
            end_date: End date for data fetch
        
        Returns:
            List of StockDataDTO objects
        """
        for attempt in range(self.max_retries):
            try:
                return self._fetch_with_retry(symbol, start_date, end_date)
            except Exception as e:
                if "429" in str(e) or "Too Many Requests" in str(e):
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (attempt + 1)
                        logger.warning(
                            f"Rate limit hit for {symbol}, retrying in {wait_time}s "
                            f"(attempt {attempt + 1}/{self.max_retries})"
                        )
                        time.sleep(wait_time)
                        continue
                logger.error(f"Error fetching data for {symbol}: {str(e)}", exc_info=True)
                return []
        
        logger.error(f"Max retries reached for {symbol}")
        return []
    
    def _fetch_with_retry(
        self,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[StockDataDTO]:
        """Internal method to fetch data with rate limiting"""
        try:
            # Add delay to avoid hitting rate limits
            time.sleep(self.request_delay)
            # Set default dates if not provided
            if end_date is None:
                end_date = date.today()
            if start_date is None:
                start_date = end_date - timedelta(days=30)  # Default to last 30 days
            
            logger.info(
                f"Fetching data for {symbol} from {start_date} to {end_date}"
            )
            
            # Create ticker object
            ticker = yf.Ticker(symbol)
            
            # Fetch historical data
            hist = ticker.history(start=start_date, end=end_date)
            
            if hist.empty:
                logger.warning(f"No historical data found for {symbol}")
                return []
            
            # Get additional info
            info = ticker.info
            market_cap = info.get('marketCap')
            pe_ratio = info.get('trailingPE') or info.get('forwardPE')
            
            # Convert to StockDataDTO list
            results = []
            for idx, row in hist.iterrows():
                # Calculate turnover rate if possible
                turnover_rate = None
                if market_cap and row.get('Volume') and row.get('Close'):
                    try:
                        # Rough approximation: (Volume * Price) / Market Cap
                        turnover_rate = (row['Volume'] * row['Close']) / market_cap * 100
                    except (ZeroDivisionError, TypeError):
                        pass
                
                stock_data = StockDataDTO(
                    symbol=symbol.upper(),
                    date=idx.date(),
                    open_price=float(row['Open']) if not pd.isna(row['Open']) else None,
                    high_price=float(row['High']) if not pd.isna(row['High']) else None,
                    low_price=float(row['Low']) if not pd.isna(row['Low']) else None,
                    close_price=float(row['Close']) if not pd.isna(row['Close']) else None,
                    adj_close_price=float(row['Close']) if not pd.isna(row['Close']) else None,
                    volume=int(row['Volume']) if not pd.isna(row['Volume']) else None,
                    market_cap=market_cap,
                    pe_ratio=pe_ratio,
                    turnover_rate=turnover_rate,
                    data_source=self.source_name
                )
                results.append(stock_data)
            
            logger.info(f"Fetched {len(results)} records for {symbol}")
            return results
        
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}", exc_info=True)
            return []
    
    def fetch_latest_stock_data(self, symbol: str) -> Optional[StockDataDTO]:
        """
        Fetch the latest stock data for a given symbol
        
        Args:
            symbol: Stock ticker symbol
        
        Returns:
            StockDataDTO object or None
        """
        try:
            logger.info(f"Fetching latest data for {symbol}")
            
            # Fetch last 5 days to ensure we get at least one trading day
            end_date = date.today()
            start_date = end_date - timedelta(days=5)
            
            results = self.fetch_stock_data(symbol, start_date, end_date)
            
            if results:
                # Return the most recent data
                return max(results, key=lambda x: x.date)
            
            return None
        
        except Exception as e:
            logger.error(
                f"Error fetching latest data for {symbol}: {str(e)}",
                exc_info=True
            )
            return None
    
    def is_available(self) -> bool:
        """
        Check if Yahoo Finance is available by testing a simple query
        
        Returns:
            True if available, False otherwise
        """
        try:
            # Use a simpler check to avoid rate limits
            ticker = yf.Ticker("AAPL")
            # Just try to get basic history instead of full info
            hist = ticker.history(period="1d")
            return not hist.empty
        except Exception as e:
            # If we get rate limited, consider it "available" but warn
            if "429" in str(e) or "Too Many Requests" in str(e):
                logger.warning(f"Yahoo Finance rate limited (will retry later): {str(e)}")
                return True  # Consider it available, just rate limited
            logger.error(f"Yahoo Finance is not available: {str(e)}")
            return False

