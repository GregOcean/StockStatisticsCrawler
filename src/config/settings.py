"""Application settings and configuration"""

from typing import List
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
    db_host: str = Field(default="localhost", description="Database host")
    db_port: int = Field(default=3306, description="Database port")
    db_user: str = Field(default="root", description="Database user")
    db_password: str = Field(default="", description="Database password")
    db_name: str = Field(default="stock_data", description="Database name")
    
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
    
    @property
    def database_url(self) -> str:
        """Generate database connection URL"""
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
    
    @property
    def symbols_list(self) -> List[str]:
        """Get list of stock symbols"""
        return [s.strip().upper() for s in self.stock_symbols.split(",")]


# Singleton instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get application settings singleton"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

