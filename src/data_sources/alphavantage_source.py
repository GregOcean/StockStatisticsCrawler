"""Alpha Vantage data source implementation"""

import logging
import time
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import requests

from .base import BaseDataSource, StockDataDTO

logger = logging.getLogger(__name__)


class AlphaVantageDataSource(BaseDataSource):
    """Alpha Vantage data source implementation"""
    
    # API configuration
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(
        self, 
        api_key: str,
        request_delay: float = 12.0,  # Free tier: 5 calls/minute = 12s delay
        max_retries: int = 3,
        retry_delay: float = 15.0
    ):
        super().__init__(source_name="alphavantage")
        self.api_key = api_key
        self.request_delay = request_delay
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        if not api_key:
            raise ValueError("Alpha Vantage API key is required")
        
        logger.info(
            f"AlphaVantage initialized with: delay={request_delay}s, "
            f"retries={max_retries}, api_key={'***' + api_key[-4:]}"
        )
    
    def fetch_raw_data(
        self,
        symbol: str,
        function: str = "TIME_SERIES_DAILY",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Fetch raw data from Alpha Vantage API
        
        Args:
            symbol: Stock ticker symbol
            function: API function (TIME_SERIES_DAILY, TIME_SERIES_WEEKLY, etc.)
            **kwargs: Additional API parameters
        
        Returns:
            Dictionary with raw response and metadata
        """
        for attempt in range(self.max_retries):
            try:
                # Add delay to respect rate limits
                time.sleep(self.request_delay)
                
                # Build request parameters
                params = {
                    'function': function,
                    'symbol': symbol,
                    'apikey': self.api_key,
                    **kwargs
                }
                
                logger.info(f"Fetching {function} data for {symbol} from Alpha Vantage...")
                
                # Make request
                response = requests.get(self.BASE_URL, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                # Check for API errors
                if 'Error Message' in data:
                    error_msg = data['Error Message']
                    logger.error(f"API Error for {symbol}: {error_msg}")
                    return {
                        'status': 'error',
                        'error_message': error_msg,
                        'response_json': json.dumps(data),
                        'api_function': function,
                        'api_params': json.dumps(params)
                    }
                
                # Check for rate limit message
                if 'Note' in data:
                    note_msg = data['Note']
                    if 'API call frequency' in note_msg or 'premium' in note_msg.lower():
                        logger.warning(f"Rate limit hit for {symbol}: {note_msg}")
                        if attempt < self.max_retries - 1:
                            wait_time = self.retry_delay * (attempt + 1)
                            logger.info(f"Retrying in {wait_time}s...")
                            time.sleep(wait_time)
                            continue
                        else:
                            return {
                                'status': 'error',
                                'error_message': f"Rate limit: {note_msg}",
                                'response_json': json.dumps(data),
                                'api_function': function,
                                'api_params': json.dumps(params)
                            }
                
                # Determine date range from response
                date_range = self._extract_date_range(data, function)
                
                # Success
                return {
                    'status': 'success',
                    'response_json': json.dumps(data),
                    'api_function': function,
                    'api_params': json.dumps(params),
                    'date_range': date_range,
                    'error_message': None
                }
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error for {symbol} (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (attempt + 1)
                    time.sleep(wait_time)
                else:
                    return {
                        'status': 'error',
                        'error_message': str(e),
                        'response_json': json.dumps({'error': str(e)}),
                        'api_function': function,
                        'api_params': json.dumps({'symbol': symbol, 'function': function})
                    }
        
        return {
            'status': 'error',
            'error_message': 'Max retries reached',
            'response_json': '{}',
            'api_function': function,
            'api_params': json.dumps({'symbol': symbol, 'function': function})
        }
    
    def _extract_date_range(self, data: Dict, function: str) -> Optional[str]:
        """Extract date range from API response"""
        try:
            # Map function to data key
            key_map = {
                'TIME_SERIES_DAILY': 'Time Series (Daily)',
                'TIME_SERIES_WEEKLY': 'Weekly Time Series',
                'TIME_SERIES_MONTHLY': 'Monthly Time Series',
                'TIME_SERIES_INTRADAY': 'Time Series (1min)',  # or 5min, 15min, etc.
            }
            
            time_series_key = None
            for key in key_map.values():
                if key in data:
                    time_series_key = key
                    break
            
            # Also check for intraday keys
            for key in data.keys():
                if key.startswith('Time Series'):
                    time_series_key = key
                    break
            
            if time_series_key and time_series_key in data:
                dates = list(data[time_series_key].keys())
                if dates:
                    dates_sorted = sorted(dates)
                    return f"{dates_sorted[0]} to {dates_sorted[-1]}"
            
            return None
        except Exception as e:
            logger.warning(f"Could not extract date range: {e}")
            return None
    
    def fetch_stock_data(
        self,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[StockDataDTO]:
        """
        Fetch stock data (for backward compatibility with old interface)
        Note: This is deprecated. Use fetch_raw_data() instead.
        """
        logger.warning(
            "fetch_stock_data() is deprecated for Alpha Vantage. "
            "Use fetch_raw_data() to get raw JSON responses."
        )
        return []
    
    def fetch_latest_stock_data(self, symbol: str) -> Optional[StockDataDTO]:
        """
        Fetch latest stock data (for backward compatibility)
        Note: This is deprecated. Use fetch_raw_data() instead.
        """
        logger.warning(
            "fetch_latest_stock_data() is deprecated for Alpha Vantage. "
            "Use fetch_raw_data() to get raw JSON responses."
        )
        return None
    
    def is_available(self) -> bool:
        """
        Check if Alpha Vantage API is available
        """
        try:
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': 'AAPL',
                'apikey': self.api_key
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if we got valid data (not an error)
            if 'Error Message' in data:
                logger.error(f"Alpha Vantage API error: {data['Error Message']}")
                return False
            
            if 'Note' in data and 'premium' in data['Note'].lower():
                logger.warning("Alpha Vantage rate limit hit, but API is available")
                return True
            
            return 'Time Series (Daily)' in data or 'Meta Data' in data
        
        except Exception as e:
            logger.error(f"Alpha Vantage availability check failed: {e}")
            return False

