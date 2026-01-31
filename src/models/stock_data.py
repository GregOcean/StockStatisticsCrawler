"""Stock data model"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, Integer, DateTime, Date, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


class StockData(Base):
    """Stock data model for storing daily stock information"""
    
    __tablename__ = "stock_data"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Stock identification
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    date: Mapped[datetime] = mapped_column(Date, nullable=False, index=True)
    
    # Price data
    open_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    high_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    low_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    close_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    adj_close_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Volume and trading data
    volume: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Financial metrics
    market_cap: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pe_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    turnover_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Metadata
    data_source: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_symbol_date', 'symbol', 'date', unique=True),
        Index('idx_date', 'date'),
        Index('idx_created_at', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return (
            f"<StockData(symbol='{self.symbol}', date='{self.date}', "
            f"close={self.close_price})>"
        )

