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

- 📊 **Multi-source data collection**: Yahoo Finance, Alpha Vantage, and extensible for more sources
- 🗄️ **Raw data storage**: Store original JSON responses for flexibility
- 📦 **Structured data**: Parse raw data to structured format (optional)
- ⏰ Flexible scheduled tasks (supports Cron expressions)
- 🔌 Extensible data source architecture
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
│   │   ├── base.py           # Abstract base class
│   │   ├── yfinance_source.py    # Yahoo Finance
│   │   └── alphavantage_source.py # Alpha Vantage
│   ├── models/          # Data models
│   │   ├── stock_data.py         # Structured data model
│   │   └── stock_price_raw.py    # Raw data model
│   ├── storage/         # Storage layer abstraction and implementations
│   │   ├── base.py           # Abstract base class
│   │   ├── mysql_storage.py  # Structured data storage
│   │   └── raw_storage.py    # Raw data storage
│   ├── scheduler/       # Task scheduling
│   └── main.py          # Main program entry
├── example_alphavantage.py  # Alpha Vantage demo
├── demo_api_test.py        # Yahoo Finance API test
├── requirements.txt         # Python dependencies
├── docker-compose.yml      # Docker orchestration
└── .env                    # Environment variables
```

### Data Flow Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Scheduler (APScheduler)            │
│              (Cron: 9:30 AM ET Daily)               │
└─────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────┐
│              Data Orchestrator (main.py)            │
└─────────────────────────────────────────────────────┘
                           │
          ┌────────────────┴────────────────┐
          ▼                                  ▼
┌──────────────────────┐       ┌──────────────────────┐
│   Data Sources       │       │   Storage Layer      │
│   ├─ YFinance        │       │   ├─ RawDataStorage  │
│   ├─ Alpha Vantage   │───────┤   └─ MySQLStorage    │
│   └─ [Future...]     │       │                      │
└──────────────────────┘       └──────────────────────┘
          │                                  │
          └──────────────┬───────────────────┘
                         ▼
              ┌────────────────────┐
              │   MySQL Database   │
              │   ├─ stock_data    │
              │   └─ stock_price_raw│
              └────────────────────┘
```

**Two-Stage Data Flow:**

1. **Stage 1: Raw Data Collection**
   - APIs → Raw JSON → `stock_price_raw` table
   - Preserves all original data
   - Source: yfinance, alphavantage, etc.

2. **Stage 2: Data Parsing (Optional)**
   - Raw JSON → Parser → Structured data → `stock_data` table
   - Flexible parsing based on actual data
   - Can reprocess historical data anytime

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

### ⚠️ Security: Database Password

**Never hardcode passwords in code!** Store them in `.env` file:

```bash
# Create .env file (already in .gitignore)
cp .env.example .env

# Edit and set your secure password
nano .env
```

See [SECURITY.md](SECURITY.md) for detailed security best practices.

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
# View all available commands
make help

# Development
make setup              # Setup virtual environment and install dependencies
make test               # Full system test
make test-api           # Test Yahoo Finance API validity (30s)
make test-alphavantage  # Test Alpha Vantage integration

# Docker Services
make start          # Start services
make logs           # View logs
make stop           # Stop services
make restart        # Restart application
make once           # Run data collection once
make clean          # Clean up containers and volumes

# Database
make db-shell       # Connect to MySQL shell
make db-backup      # Backup database

# Utilities
python utils.py stats       # View data statistics
python utils.py query AAPL  # Query AAPL data
```

## 🧪 Testing

```bash
# Test Yahoo Finance API (quick check, 30 seconds)
python demo_api_test.py
# OR
make test-api

# Test Alpha Vantage integration
python example_alphavantage.py
# OR
make test-alphavantage

# Full system test
python test_setup.py
# OR
make test

# Run data collection once (test)
make once
```

## 📚 Documentation

### Getting Started
- [QUICKSTART.md](QUICKSTART.md) - 5-minute quick start guide
- [README.md](README.md) - Project overview and features
- [SECURITY.md](SECURITY.md) - 🔐 **Security best practices** (passwords, credentials)

### Development & Extension
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development guide and best practices
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and data flow diagrams

### Data Sources
- [ALPHAVANTAGE_GUIDE.md](ALPHAVANTAGE_GUIDE.md) - Alpha Vantage integration guide
- [DATA_SOURCES.md](DATA_SOURCES.md) - Alternative data sources (Polygon, IEX, etc.)

### API & Rate Limiting
- [RATE_LIMIT.md](RATE_LIMIT.md) - Handling API rate limits
- [API_TEST.md](API_TEST.md) - API testing and diagnostics

### Database
- [queries.sql](queries.sql) - Common SQL query examples
- [raw_data_schema.sql](raw_data_schema.sql) - Raw data table schema and queries

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
