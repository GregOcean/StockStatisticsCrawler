"""Storage for raw API responses"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from src.models import StockPriceRaw, Base
from .base import BaseStorage

logger = logging.getLogger(__name__)


class RawDataStorage(BaseStorage):
    """Storage for raw API responses"""
    
    def __init__(self, database_url: str):
        """
        Initialize raw data storage
        
        Args:
            database_url: SQLAlchemy database URL
        """
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
    
    def connect(self) -> bool:
        """
        Establish connection to database
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info("Connecting to MySQL database for raw data storage...")
            self.engine = create_engine(
                self.database_url,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=3600,
            )
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(select(1))
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info("Successfully connected to database for raw data storage")
            return True
        
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}", exc_info=True)
            return False
    
    def disconnect(self) -> None:
        """Disconnect from database"""
        if self.engine:
            self.engine.dispose()
            logger.info("Disconnected from database")
    
    def initialize_schema(self) -> bool:
        """
        Initialize database schema
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.engine:
                logger.error("Cannot initialize schema: not connected to database")
                return False
            
            logger.info("Initializing database schema for raw data...")
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database schema initialized successfully")
            return True
        
        except Exception as e:
            logger.error(f"Failed to initialize schema: {str(e)}", exc_info=True)
            return False
    
    def save_raw_response(
        self,
        stock_code: str,
        response_json: str,
        data_source: str,
        time_granularity: str,
        price_date_range: Optional[str] = None,
        api_function: Optional[str] = None,
        api_params: Optional[str] = None,
        response_status: str = "success",
        error_message: Optional[str] = None
    ) -> bool:
        """
        Save raw API response to database
        
        Args:
            stock_code: Stock symbol/code
            response_json: Raw JSON response as string
            data_source: Data source name
            time_granularity: Time granularity (daily, weekly, etc.)
            price_date_range: Date range of data
            api_function: API function/endpoint used
            api_params: API parameters used
            response_status: Response status (success/error/partial)
            error_message: Error message if any
        
        Returns:
            True if saved successfully, False otherwise
        """
        if not self.SessionLocal:
            logger.error("Cannot save data: not connected to database")
            return False
        
        session = self.SessionLocal()
        
        try:
            raw_data = StockPriceRaw(
                stock_code=stock_code,
                price_date_range=price_date_range,
                time_granularity=time_granularity,
                crawl_save_time=datetime.utcnow(),
                response_json=response_json,
                data_source=data_source,
                api_function=api_function,
                api_params=api_params,
                response_status=response_status,
                error_message=error_message
            )
            
            session.add(raw_data)
            session.commit()
            
            logger.info(
                f"Saved raw data: {stock_code} from {data_source} "
                f"({time_granularity}, status={response_status})"
            )
            return True
        
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error while saving raw data: {str(e)}", exc_info=True)
            return False
        
        finally:
            session.close()
    
    def get_latest_raw_data(
        self,
        stock_code: str,
        data_source: str,
        time_granularity: str = "daily"
    ) -> Optional[StockPriceRaw]:
        """
        Get the latest raw data for a stock
        
        Args:
            stock_code: Stock symbol/code
            data_source: Data source name
            time_granularity: Time granularity
        
        Returns:
            StockPriceRaw object or None
        """
        if not self.SessionLocal:
            logger.error("Cannot retrieve data: not connected to database")
            return None
        
        session = self.SessionLocal()
        
        try:
            result = session.query(StockPriceRaw).filter(
                StockPriceRaw.stock_code == stock_code,
                StockPriceRaw.data_source == data_source,
                StockPriceRaw.time_granularity == time_granularity,
                StockPriceRaw.response_status == "success"
            ).order_by(StockPriceRaw.crawl_save_time.desc()).first()
            
            return result
        
        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving raw data: {str(e)}", exc_info=True)
            return None
        
        finally:
            session.close()
    
    # Implement required abstract methods from BaseStorage
    def save_stock_data(self, data: List[Any]) -> int:
        """Not used for raw data storage"""
        logger.warning("save_stock_data() called on RawDataStorage - not supported")
        return 0
    
    def get_stock_data(self, symbol: str, start_date=None, end_date=None) -> List[Any]:
        """Not used for raw data storage"""
        logger.warning("get_stock_data() called on RawDataStorage - not supported")
        return []
    
    def get_latest_date(self, symbol: str) -> Optional[Any]:
        """Not used for raw data storage"""
        logger.warning("get_latest_date() called on RawDataStorage - not supported")
        return None

