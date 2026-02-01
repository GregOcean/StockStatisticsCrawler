"""Raw stock price data model for storing unprocessed API responses"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Text, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column

from .stock_data import Base


class StockPriceRaw(Base):
    """Raw stock price data model for storing original API responses"""
    
    __tablename__ = "stock_price_raw"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Stock identification
    stock_code: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        index=True,
        comment="Stock symbol/code"
    )
    
    # Data metadata
    price_date_range: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Date range of price data, e.g., '2024-01-01 to 2024-12-31'"
    )
    
    time_granularity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Time granularity: daily, weekly, monthly, intraday_1min, intraday_5min, etc."
    )
    
    # Crawl metadata
    crawl_save_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="When this data was crawled and saved"
    )
    
    # Raw data
    response_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Original JSON response from API"
    )
    
    # Source tracking
    data_source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Data source: yfinance, alphavantage, polygon, etc."
    )
    
    # Additional metadata
    api_function: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="API function/endpoint used"
    )
    
    api_params: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="API parameters used (JSON format)"
    )
    
    response_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="success",
        comment="Response status: success, error, partial"
    )
    
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Error message if any"
    )
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_stock_source', 'stock_code', 'data_source'),
        Index('idx_crawl_time', 'crawl_save_time'),
        Index('idx_granularity', 'time_granularity'),
        Index('idx_stock_source_time', 'stock_code', 'data_source', 'crawl_save_time'),
    )
    
    def __repr__(self) -> str:
        return (
            f"<StockPriceRaw(stock_code='{self.stock_code}', "
            f"source='{self.data_source}', "
            f"granularity='{self.time_granularity}', "
            f"date_range='{self.price_date_range}')>"
        )

