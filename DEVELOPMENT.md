# Stock Statistics Crawler - 开发指南

## 项目结构说明

```
StockStatisticsCrawler/
├── src/
│   ├── config/              # 配置管理
│   │   ├── __init__.py
│   │   └── settings.py      # 配置类(使用pydantic)
│   ├── data_sources/        # 数据源
│   │   ├── __init__.py
│   │   ├── base.py          # 数据源抽象基类
│   │   └── yfinance_source.py  # Yahoo Finance实现
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   └── stock_data.py    # 股票数据模型(SQLAlchemy)
│   ├── storage/             # 存储层
│   │   ├── __init__.py
│   │   ├── base.py          # 存储抽象基类
│   │   └── mysql_storage.py # MySQL实现
│   ├── scheduler/           # 任务调度
│   │   ├── __init__.py
│   │   └── job_scheduler.py # 调度器实现
│   ├── utils/               # 工具类
│   │   └── __init__.py      # 日志配置
│   └── main.py              # 主程序入口
├── requirements.txt         # Python依赖
├── .env                     # 环境变量配置
├── .env.example             # 环境变量模板
├── docker-compose.yml       # Docker编排
├── Dockerfile               # Docker镜像
├── init.sql                 # 数据库初始化脚本
├── start.sh                 # 快速启动脚本
├── test_setup.py            # 系统测试脚本
└── README.md                # 项目文档
```

## 快速开始

### 1. 本地测试(不用Docker)

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件,配置数据库连接

# 3. 启动MySQL(如果还没有)
# 方式1: 使用Docker
docker-compose up -d mysql

# 方式2: 使用本地MySQL
# 确保MySQL正在运行并创建了stock_data数据库

# 4. 运行测试脚本
python test_setup.py

# 5. 运行一次数据采集
python src/main.py --mode once

# 6. 运行定时调度模式
python src/main.py --mode scheduled
```

### 2. 使用Docker部署

```bash
# 快速启动(推荐)
./start.sh

# 或者手动启动
docker-compose up -d

# 查看日志
docker-compose logs -f app

# 停止服务
docker-compose down

# 只运行一次
docker-compose run app python src/main.py --mode once
```

## 扩展指南

### 添加新的数据源

1. 在 `src/data_sources/` 创建新文件,例如 `alphavantage_source.py`:

```python
from .base import BaseDataSource, StockDataDTO

class AlphaVantageDataSource(BaseDataSource):
    def __init__(self, api_key: str):
        super().__init__(source_name="alphavantage")
        self.api_key = api_key
    
    def fetch_stock_data(self, symbol, start_date=None, end_date=None):
        # 实现获取数据的逻辑
        pass
    
    def fetch_latest_stock_data(self, symbol):
        # 实现获取最新数据的逻辑
        pass
    
    def is_available(self):
        # 检查数据源是否可用
        pass
```

2. 在 `src/data_sources/__init__.py` 中导出:

```python
from .alphavantage_source import AlphaVantageDataSource
__all__ = [..., "AlphaVantageDataSource"]
```

3. 在 `src/main.py` 中使用:

```python
# 根据配置选择数据源
if self.settings.default_data_source == "alphavantage":
    self.data_source = AlphaVantageDataSource(api_key=...)
```

### 添加新的存储后端

类似地,在 `src/storage/` 目录下创建新的存储实现:

```python
from .base import BaseStorage

class PostgreSQLStorage(BaseStorage):
    # 实现PostgreSQL存储逻辑
    pass
```

### 修改调度频率

编辑 `.env` 文件中的 `FETCH_SCHEDULE`:

```bash
# 每小时执行一次
FETCH_SCHEDULE="0 * * * *"

# 每天凌晨2点执行
FETCH_SCHEDULE="0 2 * * *"

# 每周一凌晨执行
FETCH_SCHEDULE="0 0 * * 1"

# Cron格式: 分 时 日 月 周几
```

## 云部署指南

### AWS部署

```bash
# 1. 使用ECR存储镜像
aws ecr create-repository --repository-name stock-crawler
docker build -t stock-crawler .
docker tag stock-crawler:latest <your-ecr-url>/stock-crawler:latest
docker push <your-ecr-url>/stock-crawler:latest

# 2. 使用RDS MySQL
# 在AWS控制台创建RDS MySQL实例

# 3. 使用ECS/Fargate运行容器
# 配置环境变量指向RDS
```

### 阿里云部署

```bash
# 1. 容器镜像服务
docker login --username=<your-username> registry.cn-hangzhou.aliyuncs.com
docker build -t stock-crawler .
docker tag stock-crawler:latest registry.cn-hangzhou.aliyuncs.com/<namespace>/stock-crawler:latest
docker push registry.cn-hangzhou.aliyuncs.com/<namespace>/stock-crawler:latest

# 2. 使用RDS MySQL
# 在阿里云控制台创建RDS实例

# 3. 使用容器服务ACK或ECI运行
```

### 使用Kubernetes

创建 `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: stock-crawler
spec:
  replicas: 1
  selector:
    matchLabels:
      app: stock-crawler
  template:
    metadata:
      labels:
        app: stock-crawler
    spec:
      containers:
      - name: stock-crawler
        image: your-registry/stock-crawler:latest
        env:
        - name: DB_HOST
          value: "your-mysql-host"
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
```

## 数据库Schema

表名: `stock_data`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键,自增 |
| symbol | VARCHAR(20) | 股票代码 |
| date | DATE | 日期 |
| open_price | FLOAT | 开盘价 |
| high_price | FLOAT | 最高价 |
| low_price | FLOAT | 最低价 |
| close_price | FLOAT | 收盘价 |
| adj_close_price | FLOAT | 调整收盘价 |
| volume | INT | 成交量 |
| market_cap | FLOAT | 市值 |
| pe_ratio | FLOAT | PE比率 |
| turnover_rate | FLOAT | 换手率(%) |
| data_source | VARCHAR(50) | 数据源 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

索引:
- PRIMARY KEY (id)
- UNIQUE KEY (symbol, date)
- KEY (date)
- KEY (created_at)

## 常见问题

### Q: 如何查看数据库中的数据?

```bash
# 连接到MySQL容器
docker-compose exec mysql mysql -u stock_user -p stock_data

# 查询数据
SELECT * FROM stock_data ORDER BY date DESC LIMIT 10;
SELECT symbol, COUNT(*) as count FROM stock_data GROUP BY symbol;
```

### Q: 如何添加更多股票?

编辑 `.env` 文件:
```bash
STOCK_SYMBOLS=AAPL,MSFT,GOOGL,AMZN,TSLA,NVDA,META,NFLX,AMD,INTC
```

然后重启服务:
```bash
docker-compose restart app
```

### Q: 数据获取失败怎么办?

1. 查看日志: `docker-compose logs app`
2. 检查网络连接
3. 验证股票代码是否正确
4. Yahoo Finance可能有访问限制,考虑添加延迟或使用其他数据源

### Q: 如何备份数据?

```bash
# 备份数据库
docker-compose exec mysql mysqldump -u stock_user -p stock_data > backup.sql

# 恢复数据库
docker-compose exec -T mysql mysql -u stock_user -p stock_data < backup.sql
```

## 监控和告警

建议集成以下工具:
- **Prometheus**: 采集指标
- **Grafana**: 可视化监控
- **AlertManager**: 告警通知

示例指标:
- 每日成功采集的股票数量
- 数据采集耗时
- 数据库写入成功率
- API调用失败率

## 性能优化

1. **批量插入**: 当前已实现批量保存
2. **并发获取**: 可以使用多线程/协程并发获取多个股票
3. **缓存策略**: 对于不变的历史数据可以添加缓存
4. **数据库索引**: 已创建必要索引,可根据查询需求调整

## 许可证

MIT License

