"""Main application entry point"""

import sys
import logging
from datetime import datetime, timedelta
from typing import List

from src.config import get_settings
from src.data_sources import YFinanceDataSource
from src.storage import MySQLStorage
from src.scheduler import JobScheduler
from src.utils import setup_logging

logger = logging.getLogger(__name__)


class StockCrawlerApp:
    """Main application class for stock data crawler"""
    
    def __init__(self):
        """Initialize the application"""
        self.settings = get_settings()
        self.data_source = None
        self.storage = None
        self.scheduler = None
        
        # Setup logging
        setup_logging(log_level=self.settings.log_level)
    
    def initialize(self) -> bool:
        """
        Initialize all components
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing Stock Crawler Application...")
            
            # Initialize data source
            logger.info(f"Initializing data source: {self.settings.default_data_source}")
            self.data_source = YFinanceDataSource()
            
            if not self.data_source.is_available():
                logger.error("Data source is not available")
                return False
            
            # Initialize storage
            logger.info("Initializing storage...")
            self.storage = MySQLStorage(self.settings.database_url)
            
            if not self.storage.connect():
                logger.error("Failed to connect to storage")
                return False
            
            if not self.storage.initialize_schema():
                logger.error("Failed to initialize database schema")
                return False
            
            # Initialize scheduler
            logger.info("Initializing scheduler...")
            self.scheduler = JobScheduler()
            
            logger.info("Application initialized successfully")
            return True
        
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}", exc_info=True)
            return False
    
    def fetch_and_store_data(self) -> None:
        """Fetch data for all configured symbols and store in database"""
        try:
            logger.info("=" * 60)
            logger.info(f"Starting data fetch job at {datetime.now()}")
            
            symbols = self.settings.symbols_list
            logger.info(f"Fetching data for {len(symbols)} symbols: {symbols}")
            
            total_saved = 0
            
            for symbol in symbols:
                try:
                    logger.info(f"Processing {symbol}...")
                    
                    # Get latest date in database
                    latest_date = self.storage.get_latest_date(symbol)
                    
                    # Determine date range
                    if latest_date:
                        start_date = latest_date + timedelta(days=1)
                        logger.info(f"Latest data for {symbol}: {latest_date}")
                    else:
                        # Fetch last 30 days for new symbols
                        start_date = datetime.now().date() - timedelta(days=30)
                        logger.info(f"No existing data for {symbol}, fetching last 30 days")
                    
                    # Fetch data
                    data = self.data_source.fetch_stock_data(
                        symbol=symbol,
                        start_date=start_date
                    )
                    
                    if data:
                        # Save to database
                        saved = self.storage.save_stock_data(data)
                        total_saved += saved
                        logger.info(f"Saved {saved} records for {symbol}")
                    else:
                        logger.warning(f"No new data available for {symbol}")
                
                except Exception as e:
                    logger.error(
                        f"Error processing {symbol}: {str(e)}",
                        exc_info=True
                    )
                    continue
            
            logger.info(f"Data fetch job completed. Total records saved: {total_saved}")
            logger.info("=" * 60)
        
        except Exception as e:
            logger.error(f"Error in fetch_and_store_data: {str(e)}", exc_info=True)
    
    def run_once(self) -> None:
        """Run data fetch once and exit"""
        try:
            if not self.initialize():
                logger.error("Initialization failed, exiting")
                sys.exit(1)
            
            logger.info("Running in one-time mode")
            self.fetch_and_store_data()
            
            logger.info("One-time run completed successfully")
        
        except Exception as e:
            logger.error(f"Error in run_once: {str(e)}", exc_info=True)
            sys.exit(1)
        
        finally:
            if self.storage:
                self.storage.disconnect()
    
    def run_scheduled(self) -> None:
        """Run with scheduler for periodic data fetching"""
        try:
            if not self.initialize():
                logger.error("Initialization failed, exiting")
                sys.exit(1)
            
            # Add scheduled job
            self.scheduler.add_cron_job(
                func=self.fetch_and_store_data,
                cron_expression=self.settings.fetch_schedule,
                job_id="fetch_stock_data",
                job_name="Fetch Stock Data"
            )
            
            # Run immediately on startup
            logger.info("Running initial data fetch...")
            self.fetch_and_store_data()
            
            # Start scheduler (blocking)
            logger.info("Starting scheduled mode...")
            self.scheduler.start()
        
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        
        except Exception as e:
            logger.error(f"Error in run_scheduled: {str(e)}", exc_info=True)
            sys.exit(1)
        
        finally:
            if self.scheduler:
                self.scheduler.shutdown()
            if self.storage:
                self.storage.disconnect()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Stock Statistics Crawler - Fetch and store stock data"
    )
    parser.add_argument(
        '--mode',
        choices=['once', 'scheduled'],
        default='scheduled',
        help='Run mode: once (single run) or scheduled (continuous with cron)'
    )
    
    args = parser.parse_args()
    
    app = StockCrawlerApp()
    
    if args.mode == 'once':
        app.run_once()
    else:
        app.run_scheduled()


if __name__ == "__main__":
    main()

