# Stock Statistics Crawler

An extensible US stock data collection service that periodically fetches stock data from public APIs and stores it in a MySQL database.

## 📋 Project Overview

This is a foundational service designed specifically for collecting US stock data, providing data support for subsequent data analysis, visualization, strategy backtesting, and other applications.

**Main Use Cases:**
- Provide data source for Grafana Dashboard
- Support quantitative trading strategy backtesting
- Data foundation for stock filtering and alert systems
- Financial data analysis and research

## ✨ Features

- 📊 Fetch US stock data from multiple sources (price, PE ratio, market cap, turnover rate, etc.)
- 🗄️ Automatically store to MySQL database with deduplication and updates
- ⏰ Flexible scheduled tasks (supports Cron expressions)
- 🔌 Extensible data source architecture (currently supports Yahoo Finance, easy to add new sources)
- 🐳 Complete Docker support with one-click deployment
- ☁️ Cloud-native design, suitable for deployment on any cloud platform
- 📝 Detailed logging and error handling
- 🔄 Incremental updates to avoid duplicate data fetching
- 💪 Fault tolerance - single stock failure doesn't affect others

## Project Architecture

```
StockStatisticsCrawler/
├── src/
│   ├── config/          # Configuration management
│   ├── data_sources/    # Data source abstraction and implementations
│   ├── models/          # Data models
│   ├── storage/         # Storage layer abstraction and implementations
│   ├── scheduler/       # Task scheduling
│   └── main.py          # Main program entry
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Docker orchestration
└── .env                 # Environment variables
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose (recommended)
- Or Python 3.11+ (for local development)

### Method 1: Docker Deployment (Recommended)

```bash
# 1. Quick start
./start.sh
# or
make start

# 2. View logs
make logs

# 3. Stop services
make stop
```

### Method 2: Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start MySQL
docker-compose up -d mysql

# 3. Run tests
python test_setup.py

# 4. Run once
python src/main.py --mode once

# 5. Run scheduled mode
python src/main.py --mode scheduled
```

> 📖 For more detailed instructions, see [QUICKSTART.md](QUICKSTART.md)

## Configuration

### Environment Variables

- `DB_HOST`: MySQL host address
- `DB_PORT`: MySQL port
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `DB_NAME`: Database name
- `STOCK_SYMBOLS`: Stock symbols to track (comma-separated)
- `FETCH_SCHEDULE`: Data fetching Cron expression
- `DEFAULT_DATA_SOURCE`: Default data source (yfinance)

### Adding New Data Sources

1. Create a new data source class in `src/data_sources/`
2. Inherit from `BaseDataSource` abstract class
3. Implement the `fetch_stock_data()` method
4. Specify the new data source in configuration

## 📊 Data Model

Database Table: `stock_data`

| Field | Type | Description |
|------|------|------|
| symbol | VARCHAR(20) | Stock symbol (e.g., AAPL) |
| date | DATE | Trading date |
| open_price | FLOAT | Opening price |
| high_price | FLOAT | Highest price |
| low_price | FLOAT | Lowest price |
| close_price | FLOAT | Closing price |
| adj_close_price | FLOAT | Adjusted closing price |
| volume | INT | Trading volume |
| market_cap | FLOAT | Market capitalization |
| pe_ratio | FLOAT | Price-to-earnings ratio |
| turnover_rate | FLOAT | Turnover rate (%) |
| data_source | VARCHAR(50) | Data source |

**Index Design:**
- Primary key: `id`
- Unique index: `(symbol, date)` - Ensures no duplicate data
- Regular indexes: `date`, `created_at` - Optimizes query performance

## ☁️ Cloud Deployment

This project is designed for cloud deployment:

### AWS
```bash
# ECS/Fargate + RDS MySQL + CloudWatch
docker build -t stock-crawler .
# Push to ECR and configure ECS tasks
```

### Alibaba Cloud
```bash
# ACK + RDS MySQL + SLS
# Push to container registry and create deployment
```

### Google Cloud / Azure
- Cloud Run / Container Instances
- Cloud SQL / Azure Database for MySQL

> 📖 For detailed deployment guide, see [DEVELOPMENT.md](DEVELOPMENT.md)

## 🛠️ Common Commands

```bash
make help           # View all commands
make start          # Start services
make logs           # View logs
make stats          # View data statistics
make db-shell       # Connect to database
make db-backup      # Backup database
python utils.py stats   # View data statistics
python utils.py query AAPL  # Query AAPL data
```

## 🧪 Testing

```bash
# System test
python test_setup.py

# Run data collection once (test)
make once
```

## 📚 Documentation

- [QUICKSTART.md](QUICKSTART.md) - 5-minute quick start
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development and extension guide
- [queries.sql](queries.sql) - Common SQL query examples

## 🤝 Extensibility

### Adding New Data Sources

1. Create a new data source class inheriting from `BaseDataSource`
2. Implement required methods
3. Specify new data source in configuration

Framework already prepared, supports quick integration of:
- Alpha Vantage
- IEX Cloud
- Polygon.io
- Any other REST API

### Adding New Fields

1. Modify `src/models/stock_data.py` to add fields
2. Update data source implementation
3. Run service to automatically create/update table structure

## ⚙️ Tech Stack

- **Language**: Python 3.11+
- **Data Source**: yfinance (Yahoo Finance API)
- **Database**: MySQL 8.0 with SQLAlchemy ORM
- **Scheduling**: APScheduler
- **Configuration**: Pydantic Settings
- **Containers**: Docker & Docker Compose

## 📈 Use Cases

1. **Data Analysis**: Provide historical data for Jupyter Notebook
2. **Visualization**: Connect to Grafana/Metabase to create dashboards
3. **Quantitative Trading**: Strategy backtesting and signal generation
4. **Monitoring & Alerts**: Real-time alerts based on data changes
5. **Research**: Financial market analysis and research

## 🔒 Production Environment Recommendations

- Use cloud database services (RDS) instead of containerized MySQL
- Configure database backup strategy
- Enable monitoring and alerts
- Use environment variables to manage sensitive information
- Regularly check logs and data quality

## 📄 License

MIT License - Free to use, modify, and distribute

## 🙋 FAQ

**Q: Which stock markets are supported?**  
A: Currently supports US stocks. Yahoo Finance also supports other markets - can be configured through stock codes (e.g., 0700.HK for Tencent)

**Q: Data update frequency?**  
A: Updates once daily by default, configurable to any frequency (intraday updates on trading days, hourly, etc.)

**Q: Historical data range?**  
A: First run fetches 30 days of data, subsequent incremental updates. Can modify code to fetch longer historical data

**Q: How to connect to other applications?**  
A: All applications can directly connect to MySQL database to read data, no API needed

---

**Star ⭐ this project if it helps you!**
