"""Base storage abstract class"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date

from src.data_sources.base import StockDataDTO


class BaseStorage(ABC):
    """Abstract base class for all storage implementations"""
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to storage
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from storage"""
        pass
    
    @abstractmethod
    def initialize_schema(self) -> bool:
        """
        Initialize database schema/tables
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def save_stock_data(self, data: List[StockDataDTO]) -> int:
        """
        Save stock data to storage
        
        Args:
            data: List of StockDataDTO objects to save
        
        Returns:
            Number of records saved
        """
        pass
    
    @abstractmethod
    def get_stock_data(
        self,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[StockDataDTO]:
        """
        Retrieve stock data from storage
        
        Args:
            symbol: Stock ticker symbol
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
        
        Returns:
            List of StockDataDTO objects
        """
        pass
    
    @abstractmethod
    def get_latest_date(self, symbol: str) -> Optional[date]:
        """
        Get the latest date for which data exists for a symbol
        
        Args:
            symbol: Stock ticker symbol
        
        Returns:
            Latest date or None if no data exists
        """
        pass

