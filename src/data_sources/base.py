"""Base data source abstract class"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime, date


class StockDataDTO:
    """Data Transfer Object for stock data"""
    
    def __init__(
        self,
        symbol: str,
        date: date,
        open_price: Optional[float] = None,
        high_price: Optional[float] = None,
        low_price: Optional[float] = None,
        close_price: Optional[float] = None,
        adj_close_price: Optional[float] = None,
        volume: Optional[int] = None,
        market_cap: Optional[float] = None,
        pe_ratio: Optional[float] = None,
        turnover_rate: Optional[float] = None,
        data_source: str = "unknown"
    ):
        self.symbol = symbol
        self.date = date
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.close_price = close_price
        self.adj_close_price = adj_close_price
        self.volume = volume
        self.market_cap = market_cap
        self.pe_ratio = pe_ratio
        self.turnover_rate = turnover_rate
        self.data_source = data_source
    
    def __repr__(self) -> str:
        return (
            f"<StockDataDTO(symbol='{self.symbol}', date='{self.date}', "
            f"close={self.close_price})>"
        )


class BaseDataSource(ABC):
    """Abstract base class for all data sources"""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
    
    @abstractmethod
    def fetch_stock_data(
        self,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[StockDataDTO]:
        """
        Fetch stock data for a given symbol
        
        Args:
            symbol: Stock ticker symbol
            start_date: Start date for data fetch (optional)
            end_date: End date for data fetch (optional)
        
        Returns:
            List of StockDataDTO objects
        """
        pass
    
    @abstractmethod
    def fetch_latest_stock_data(self, symbol: str) -> Optional[StockDataDTO]:
        """
        Fetch the latest stock data for a given symbol
        
        Args:
            symbol: Stock ticker symbol
        
        Returns:
            StockDataDTO object or None if not available
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the data source is available
        
        Returns:
            True if available, False otherwise
        """
        pass

