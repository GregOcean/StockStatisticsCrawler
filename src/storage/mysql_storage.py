"""MySQL storage implementation"""

import logging
from typing import List, Optional
from datetime import date
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.models import StockData, Base
from src.data_sources.base import StockDataDTO
from .base import BaseStorage

logger = logging.getLogger(__name__)


class MySQLStorage(BaseStorage):
    """MySQL storage implementation using SQLAlchemy"""
    
    def __init__(self, database_url: str):
        """
        Initialize MySQL storage
        
        Args:
            database_url: SQLAlchemy database URL
        """
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
    
    def connect(self) -> bool:
        """
        Establish connection to MySQL database
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info("Connecting to MySQL database...")
            self.engine = create_engine(
                self.database_url,
                echo=False,
                pool_pre_ping=True,  # Enable connection health checks
                pool_recycle=3600,   # Recycle connections after 1 hour
            )
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(select(1))
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info("Successfully connected to MySQL database")
            return True
        
        except Exception as e:
            logger.error(f"Failed to connect to MySQL: {str(e)}", exc_info=True)
            return False
    
    def disconnect(self) -> None:
        """Disconnect from MySQL database"""
        if self.engine:
            self.engine.dispose()
            logger.info("Disconnected from MySQL database")
    
    def initialize_schema(self) -> bool:
        """
        Initialize database schema/tables
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.engine:
                logger.error("Cannot initialize schema: not connected to database")
                return False
            
            logger.info("Initializing database schema...")
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database schema initialized successfully")
            return True
        
        except Exception as e:
            logger.error(f"Failed to initialize schema: {str(e)}", exc_info=True)
            return False
    
    def save_stock_data(self, data: List[StockDataDTO]) -> int:
        """
        Save stock data to MySQL database
        
        Args:
            data: List of StockDataDTO objects to save
        
        Returns:
            Number of records saved
        """
        if not data:
            logger.warning("No data to save")
            return 0
        
        if not self.SessionLocal:
            logger.error("Cannot save data: not connected to database")
            return 0
        
        saved_count = 0
        session = self.SessionLocal()
        
        try:
            for dto in data:
                try:
                    # Check if record exists
                    existing = session.query(StockData).filter(
                        StockData.symbol == dto.symbol,
                        StockData.date == dto.date
                    ).first()
                    
                    if existing:
                        # Update existing record
                        existing.open_price = dto.open_price
                        existing.high_price = dto.high_price
                        existing.low_price = dto.low_price
                        existing.close_price = dto.close_price
                        existing.adj_close_price = dto.adj_close_price
                        existing.volume = dto.volume
                        existing.market_cap = dto.market_cap
                        existing.pe_ratio = dto.pe_ratio
                        existing.turnover_rate = dto.turnover_rate
                        existing.data_source = dto.data_source
                        logger.debug(f"Updated existing record: {dto.symbol} {dto.date}")
                    else:
                        # Insert new record
                        stock_data = StockData(
                            symbol=dto.symbol,
                            date=dto.date,
                            open_price=dto.open_price,
                            high_price=dto.high_price,
                            low_price=dto.low_price,
                            close_price=dto.close_price,
                            adj_close_price=dto.adj_close_price,
                            volume=dto.volume,
                            market_cap=dto.market_cap,
                            pe_ratio=dto.pe_ratio,
                            turnover_rate=dto.turnover_rate,
                            data_source=dto.data_source
                        )
                        session.add(stock_data)
                        logger.debug(f"Inserted new record: {dto.symbol} {dto.date}")
                    
                    saved_count += 1
                
                except IntegrityError as e:
                    logger.warning(
                        f"Duplicate entry for {dto.symbol} on {dto.date}, skipping"
                    )
                    session.rollback()
                    continue
            
            session.commit()
            logger.info(f"Successfully saved/updated {saved_count} records")
        
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error while saving data: {str(e)}", exc_info=True)
        
        finally:
            session.close()
        
        return saved_count
    
    def get_stock_data(
        self,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[StockDataDTO]:
        """
        Retrieve stock data from MySQL database
        
        Args:
            symbol: Stock ticker symbol
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
        
        Returns:
            List of StockDataDTO objects
        """
        if not self.SessionLocal:
            logger.error("Cannot retrieve data: not connected to database")
            return []
        
        session = self.SessionLocal()
        results = []
        
        try:
            query = session.query(StockData).filter(StockData.symbol == symbol)
            
            if start_date:
                query = query.filter(StockData.date >= start_date)
            if end_date:
                query = query.filter(StockData.date <= end_date)
            
            query = query.order_by(StockData.date)
            
            for record in query.all():
                dto = StockDataDTO(
                    symbol=record.symbol,
                    date=record.date,
                    open_price=record.open_price,
                    high_price=record.high_price,
                    low_price=record.low_price,
                    close_price=record.close_price,
                    adj_close_price=record.adj_close_price,
                    volume=record.volume,
                    market_cap=record.market_cap,
                    pe_ratio=record.pe_ratio,
                    turnover_rate=record.turnover_rate,
                    data_source=record.data_source
                )
                results.append(dto)
            
            logger.info(f"Retrieved {len(results)} records for {symbol}")
        
        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving data: {str(e)}", exc_info=True)
        
        finally:
            session.close()
        
        return results
    
    def get_latest_date(self, symbol: str) -> Optional[date]:
        """
        Get the latest date for which data exists for a symbol
        
        Args:
            symbol: Stock ticker symbol
        
        Returns:
            Latest date or None if no data exists
        """
        if not self.SessionLocal:
            logger.error("Cannot retrieve latest date: not connected to database")
            return None
        
        session = self.SessionLocal()
        
        try:
            result = session.query(func.max(StockData.date)).filter(
                StockData.symbol == symbol
            ).scalar()
            
            return result
        
        except SQLAlchemyError as e:
            logger.error(
                f"Database error while getting latest date: {str(e)}",
                exc_info=True
            )
            return None
        
        finally:
            session.close()

