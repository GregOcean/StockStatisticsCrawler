"""Application settings and configuration"""

from __future__ import annotations
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Database configuration
    # Option 1: Use individual fields
    db_host: str = Field(default="localhost", description="Database host")
    db_port: int = Field(default=3306, description="Database port")
    db_user: str = Field(default="root", description="Database user")
    db_password: str = Field(default="", description="Database password (store in .env, not in code)")
    db_name: str = Field(default="stock_data", description="Database name")
    
    # Option 2: Use full connection URL (takes precedence if provided)
    database_url: Optional[str] = Field(
        default=None, 
        description="Full database URL (e.g., mysql+pymysql://user:pass@host:port/dbname)"
    )
    
    # Scheduler configuration
    fetch_schedule: str = Field(
        default="0 0 * * *",
        description="Cron expression for data fetching schedule"
    )
    
    # Stock symbols to track
    stock_symbols: str = Field(
        default="AAPL,MSFT,GOOGL,AMZN,TSLA",
        description="Comma-separated list of stock symbols"
    )
    
    # Data source
    default_data_source: str = Field(
        default="yfinance",
        description="Default data source to use"
    )
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    
    # API Rate Limiting
    api_request_delay: float = Field(
        default=2.0,
        description="Delay in seconds between API requests"
    )
    api_max_retries: int = Field(
        default=5,
        description="Maximum number of retries for failed requests"
    )
    api_retry_delay: float = Field(
        default=10.0,
        description="Base delay in seconds between retries"
    )
    
    # Alpha Vantage configuration
    alphavantage_api_key: str = Field(
        default="",
        description="Alpha Vantage API key (optional, for Alpha Vantage data source)"
    )
    alphavantage_enabled: bool = Field(
        default=False,
        description="Enable Alpha Vantage as fallback data source"
    )
    
    def get_database_url(self) -> str:
        """
        Get database connection URL
        
        Priority:
        1. Use DATABASE_URL if provided in .env
        2. Otherwise, build from individual fields (DB_HOST, DB_USER, etc.)
        """
        if self.database_url:
            return self.database_url
        
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
    
    @property
    def symbols_list(self) -> List[str]:
        """Get list of stock symbols"""
        return [s.strip().upper() for s in self.stock_symbols.split(",")]


# Singleton instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings singleton"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

