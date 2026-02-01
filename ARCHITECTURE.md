# Architecture Diagrams

## Overall System Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                      Stock Statistics Crawler                 │
│                    (Cloud-Ready Microservice)                 │
└───────────────────────────────────────────────────────────────┘
                              │
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Scheduler     │  │  Orchestrator   │  │   Storage       │
│  (APScheduler)  │─▶│    (main.py)    │─▶│   (MySQL)       │
│                 │  │                 │  │                 │
│ • Cron: Daily   │  │ • Fetch data    │  │ • Raw data      │
│ • 9:30 AM ET    │  │ • Error handle  │  │ • Parsed data   │
│ • Configurable  │  │ • Retry logic   │  │ • Deduplication │
└─────────────────┘  └─────────────────┘  └─────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
          ┌─────────────────┐  ┌─────────────────┐
          │  Data Sources   │  │    Storage      │
          └─────────────────┘  └─────────────────┘
                    │                   │
        ┌───────────┼───────────┐       │
        ▼           ▼           ▼       │
   ┌────────┐ ┌────────┐ ┌────────┐    │
   │YFinance│ │AlphaV. │ │Future..│    │
   └────────┘ └────────┘ └────────┘    │
        │           │           │       │
        └───────────┴───────────┴───────┘
                    │
                    ▼
        ┌────────────────────────┐
        │   MySQL Database       │
        │                        │
        │ ┌────────────────────┐ │
        │ │  stock_price_raw   │ │
        │ │  • Raw JSON        │ │
        │ │  • Multi-source    │ │
        │ └────────────────────┘ │
        │                        │
        │ ┌────────────────────┐ │
        │ │  stock_data        │ │
        │ │  • Parsed data     │ │
        │ │  • Structured      │ │
        │ └────────────────────┘ │
        └────────────────────────┘
```

## Data Flow: Raw-Data-First Approach

```
┌─────────────────────────────────────────────────────────────┐
│ Stage 1: Raw Data Collection (Immediate)                    │
└─────────────────────────────────────────────────────────────┘

    External APIs
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ YFinance │   │Alpha V.  │   │ Polygon  │
    │  (Free)  │   │(5req/min)│   │ (Future) │
    └─────┬────┘   └─────┬────┘   └─────┬────┘
          │              │              │
          │ JSON         │ JSON         │ JSON
          │              │              │
          └──────────────┼──────────────┘
                         │
                    Rate Limiting
                    Retry Logic
                    Error Handling
                         │
                         ▼
              ┌──────────────────────┐
              │  Raw JSON Response   │
              │  + Metadata          │
              │                      │
              │  {                   │
              │    response_json,    │
              │    stock_code,       │
              │    data_source,      │
              │    status,           │
              │    timestamp,        │
              │    api_params        │
              │  }                   │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  stock_price_raw     │
              │  (MySQL Table)       │
              │                      │
              │  • Preserves ALL     │
              │    original data     │
              │  • No data loss      │
              │  • Easy debugging    │
              │  • Reprocessable     │
              └──────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Stage 2: Data Parsing (Optional, Can be done later)        │
└─────────────────────────────────────────────────────────────┘

              ┌──────────────────────┐
              │  stock_price_raw     │
              │  (Raw JSON Storage)  │
              └──────────┬───────────┘
                         │
                    Read & Parse
                    (Flexible timing)
                         │
                         ▼
              ┌──────────────────────┐
              │   ETL Processor      │
              │                      │
              │  • Parse JSON        │
              │  • Validate data     │
              │  • Transform format  │
              │  • Handle errors     │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   stock_data         │
              │   (Structured)       │
              │                      │
              │  • symbol            │
              │  • date              │
              │  • open/high/low/... │
              │  • pe_ratio          │
              │  • market_cap        │
              └──────────────────────┘
```

## Multi-Source Data Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Data Source Layer                        │
│                   (Extensible Architecture)                  │
└─────────────────────────────────────────────────────────────┘

         Abstract Base Class: BaseDataSource
                     │
       ┌─────────────┼─────────────┬─────────────┐
       │             │             │             │
       ▼             ▼             ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  YFinance   │ │AlphaVantage │ │   Polygon   │ │     IEX     │
│   Source    │ │   Source    │ │   Source    │ │   Source    │
├─────────────┤ ├─────────────┤ ├─────────────┤ ├─────────────┤
│ • Free      │ │ • 5req/min  │ │ • Premium   │ │ • Premium   │
│ • Daily     │ │ • Multiple  │ │ • Realtime  │ │ • Realtime  │
│ • Rate      │ │   functions │ │ • Historical│ │ • Financial │
│   limited   │ │ • Historical│ │ • Options   │ │   data      │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
       │             │             │             │
       └─────────────┴─────────────┴─────────────┘
                     │
                     ▼
              fetch_raw_data()
                     │
                     ▼
         ┌────────────────────────────┐
         │  Unified Response Format   │
         │                            │
         │  {                         │
         │    status: str,            │
         │    response_json: str,     │
         │    api_function: str,      │
         │    api_params: str,        │
         │    date_range: str,        │
         │    error_message: str      │
         │  }                         │
         └────────────────────────────┘
                     │
                     ▼
         ┌────────────────────────────┐
         │   RawDataStorage           │
         │   (Single Storage Layer)   │
         │                            │
         │   Stores ALL sources in    │
         │   stock_price_raw table    │
         └────────────────────────────┘
```

## Storage Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Storage Layer                           │
│                  (Dual Storage Strategy)                     │
└─────────────────────────────────────────────────────────────┘

         Abstract Base Class: BaseStorage
                     │
       ┌─────────────┴─────────────┐
       │                           │
       ▼                           ▼
┌──────────────────┐      ┌──────────────────┐
│ RawDataStorage   │      │ MySQLStorage     │
│ (Raw JSON)       │      │ (Structured)     │
├──────────────────┤      ├──────────────────┤
│ • store_raw()    │      │ • store_parsed() │
│ • get_latest()   │      │ • query_data()   │
│ • No parsing     │      │ • analytics      │
└────────┬─────────┘      └────────┬─────────┘
         │                         │
         ▼                         ▼
┌──────────────────┐      ┌──────────────────┐
│stock_price_raw   │      │  stock_data      │
├──────────────────┤      ├──────────────────┤
│ • id             │      │ • id             │
│ • stock_code     │      │ • symbol         │
│ • response_json  │◀─────┤ • date           │
│ • data_source    │ Parse│ • open           │
│ • time_gran.     │      │ • high           │
│ • crawl_time     │      │ • low            │
│ • status         │      │ • close          │
│ • error_msg      │      │ • volume         │
└──────────────────┘      │ • pe_ratio       │
                          │ • market_cap     │
                          │ • data_source    │
                          └──────────────────┘

Benefits of Dual Storage:
┌────────────────────────────────────────────────────┐
│ stock_price_raw         │ stock_data              │
├─────────────────────────┼─────────────────────────┤
│ ✅ Complete data        │ ✅ Query optimized      │
│ ✅ Reprocessable        │ ✅ Analytics ready      │
│ ✅ Source preservation  │ ✅ Fast aggregation     │
│ ✅ Debugging friendly   │ ✅ Dashboard friendly   │
│ ✅ Schema flexible      │ ✅ Schema consistent    │
└─────────────────────────┴─────────────────────────┘
```

## Rate Limiting & Retry Strategy

```
┌─────────────────────────────────────────────────────────────┐
│          Rate Limiting & Error Handling Flow                 │
└─────────────────────────────────────────────────────────────┘

                    API Request
                         │
                         ▼
              ┌──────────────────┐
              │  Pre-Request     │
              │  Delay           │
              │                  │
              │  Wait N seconds  │
              │  (Configurable)  │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  Send Request    │
              │  (with timeout)  │
              └────────┬─────────┘
                       │
          ┌────────────┼────────────┐
          │            │            │
    Success │      Rate Limit │  Network Error
          ▼            ▼            ▼
    ┌─────────┐  ┌─────────┐  ┌─────────┐
    │ Return  │  │ Retry?  │  │ Retry?  │
    │ Data    │  │ (3x)    │  │ (3x)    │
    └─────────┘  └────┬────┘  └────┬────┘
                      │            │
                      └────────────┘
                           │
                  Exponential Backoff
                  Wait: delay * (retry + 1)
                           │
                           ▼
                    ┌──────────────┐
                    │ Retry < Max? │
                    └──────┬───────┘
                           │
              ┌────────────┴────────────┐
              │                         │
            Yes                        No
              │                         │
              └──▶ Retry Request       │
                                        ▼
                              ┌─────────────────┐
                              │ Return Error    │
                              │ (Save to DB)    │
                              └─────────────────┘

Configuration (via .env):
┌──────────────────────────────────────────┐
│ API_REQUEST_DELAY  = 12.0  seconds      │
│ API_MAX_RETRIES    = 3     attempts     │
│ API_RETRY_DELAY    = 15.0  seconds      │
└──────────────────────────────────────────┘

Example Timeline:
┌────────────────────────────────────────────────────────┐
│ Time  │ Action                                         │
├───────┼────────────────────────────────────────────────┤
│ T+0s  │ Request 1 (AAPL)                              │
│ T+12s │ Request 2 (MSFT) - after delay                │
│ T+24s │ Request 3 (GOOGL) - after delay               │
│ T+24s │ ❌ Rate limit error                           │
│ T+39s │ Retry 1 (GOOGL) - after 15s backoff          │
│ T+39s │ ❌ Still rate limited                         │
│ T+69s │ Retry 2 (GOOGL) - after 30s backoff          │
│ T+69s │ ✅ Success                                    │
└────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Cloud Deployment Options                   │
└─────────────────────────────────────────────────────────────┘

Option 1: Docker Compose (Simple)
┌────────────────────────────────────────┐
│         Docker Host (VM/Cloud)         │
│  ┌──────────────────────────────────┐  │
│  │   docker-compose.yml             │  │
│  │  ┌────────────┐  ┌────────────┐  │  │
│  │  │    app     │  │   mysql    │  │  │
│  │  │  (Python)  │─▶│ (Database) │  │  │
│  │  └────────────┘  └────────────┘  │  │
│  │                                  │  │
│  │  Volumes: data persistence       │  │
│  │  Networks: isolated network      │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘

Option 2: Kubernetes (Scalable)
┌────────────────────────────────────────┐
│       Kubernetes Cluster (EKS/GKE)     │
│  ┌──────────────────────────────────┐  │
│  │  Deployment: stock-crawler       │  │
│  │  ┌────────┐  ┌────────┐          │  │
│  │  │ Pod 1  │  │ Pod 2  │ (HA)     │  │
│  │  └───┬────┘  └───┬────┘          │  │
│  │      └───────────┘               │  │
│  │           │                      │  │
│  │           ▼                      │  │
│  │  ┌─────────────────┐             │  │
│  │  │  Service (LB)   │             │  │
│  │  └────────┬────────┘             │  │
│  │           │                      │  │
│  │           ▼                      │  │
│  │  ┌─────────────────┐             │  │
│  │  │  MySQL (RDS)    │             │  │
│  │  └─────────────────┘             │  │
│  │                                  │  │
│  │  ConfigMap: env vars             │  │
│  │  Secret: API keys                │  │
│  │  CronJob: scheduled tasks        │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘

Option 3: Serverless (Cost-effective)
┌────────────────────────────────────────┐
│       Serverless Architecture          │
│  ┌──────────────────────────────────┐  │
│  │  CloudWatch Events / EventBridge │  │
│  │  (Cron: 9:30 AM ET daily)        │  │
│  └──────────────┬───────────────────┘  │
│                 │                      │
│                 ▼                      │
│  ┌──────────────────────────────────┐  │
│  │  Lambda / Cloud Function         │  │
│  │  (Python with dependencies)      │  │
│  └──────────────┬───────────────────┘  │
│                 │                      │
│                 ▼                      │
│  ┌──────────────────────────────────┐  │
│  │  RDS MySQL / Aurora Serverless   │  │
│  └──────────────────────────────────┘  │
│                                        │
│  Benefits:                             │
│  • Pay per execution                   │
│  • Auto-scaling                        │
│  • No server management                │
└────────────────────────────────────────┘
```

## Project Structure

```
StockStatisticsCrawler/
│
├── src/                          # Source code
│   ├── config/                   # Configuration
│   │   ├── __init__.py
│   │   └── settings.py           # Pydantic settings
│   │
│   ├── data_sources/             # Data source implementations
│   │   ├── __init__.py
│   │   ├── base.py               # Abstract base class
│   │   ├── yfinance_source.py    # Yahoo Finance
│   │   └── alphavantage_source.py # Alpha Vantage ✨ NEW
│   │
│   ├── models/                   # Database models
│   │   ├── __init__.py
│   │   ├── stock_data.py         # Structured data model
│   │   └── stock_price_raw.py    # Raw data model ✨ NEW
│   │
│   ├── storage/                  # Storage implementations
│   │   ├── __init__.py
│   │   ├── base.py               # Abstract base class
│   │   ├── mysql_storage.py      # Structured storage
│   │   └── raw_storage.py        # Raw data storage ✨ NEW
│   │
│   ├── scheduler/                # Task scheduling
│   │   ├── __init__.py
│   │   └── job_scheduler.py      # APScheduler wrapper
│   │
│   ├── utils/                    # Utilities
│   │   └── __init__.py
│   │
│   └── main.py                   # Application entry point
│
├── example_alphavantage.py       # Alpha Vantage demo ✨ NEW
├── demo_api_test.py              # Yahoo Finance API test
├── test_setup.py                 # System test
├── utils.py                      # CLI utilities
│
├── requirements.txt              # Python dependencies
├── setup.sh                      # Setup script
├── Makefile                      # Common commands
│
├── Dockerfile                    # Docker image
├── docker-compose.yml            # Docker orchestration
├── init.sql                      # Database initialization
├── raw_data_schema.sql           # Raw data schema ✨ NEW
│
├── .env                          # Environment variables
├── .gitignore                    # Git ignore rules
│
├── README.md                     # Project overview
├── QUICKSTART.md                 # Quick start guide
├── DEVELOPMENT.md                # Development guide
├── ALPHAVANTAGE_GUIDE.md         # Alpha Vantage guide ✨ NEW
├── ALPHAVANTAGE_INTEGRATION.md   # Integration summary ✨ NEW
├── ALPHAVANTAGE_集成总结.md       # 中文总结 ✨ NEW
├── DATA_SOURCES.md               # Data sources list
├── RATE_LIMIT.md                 # Rate limiting guide
├── API_TEST.md                   # API testing guide
├── CONFIG_GUIDE.md               # Configuration guide
├── PROJECT.md                    # Project structure
├── CHECKLIST.md                  # Deployment checklist
├── SUMMARY.md                    # Summary
└── LICENSE                       # MIT License

✨ NEW = Added in Alpha Vantage integration
```

---

**Legend:**
- `─▶` : Data flow
- `│` : Hierarchy
- `┌─┐` : Component boundary
- `✅` : Benefit/Feature
- `❌` : Error/Problem
- `✨` : New/Highlighted

