# 快速使用指南

## 🚀 5分钟快速开始

### 前置要求
- Docker 和 Docker Compose
- Python 3.11+ (如果要本地运行)

### 方式1: 使用Docker (推荐)

```bash
# 1. 克隆或进入项目目录
cd StockStatisticsCrawler

# 2. 启动服务
make start
# 或者
./start.sh

# 3. 查看日志
make logs

# 4. 停止服务
make stop
```

就这么简单！服务会自动:
- 启动MySQL数据库
- 初始化数据库表结构
- 按配置的时间定时获取股票数据
- 将数据存储到MySQL

### 方式2: 本地开发模式

```bash
# 1. 安装依赖
make install

# 2. 启动MySQL(使用Docker)
docker-compose up -d mysql

# 3. 运行测试
make test

# 4. 运行一次数据采集
make once

# 5. 运行定时调度模式
python src/main.py --mode scheduled
```

## 📊 查看数据

```bash
# 连接到MySQL
make db-shell

# 在MySQL中执行查询
SELECT * FROM stock_data ORDER BY date DESC LIMIT 10;
SELECT symbol, COUNT(*) as days, MIN(date) as from_date, MAX(date) as to_date 
FROM stock_data GROUP BY symbol;
```

## ⚙️ 配置

编辑 `.env` 文件 (如果不存在，从 `.env.example` 复制):

```bash
# 修改要跟踪的股票
STOCK_SYMBOLS=AAPL,MSFT,GOOGL,AMZN,TSLA,NVDA,META

# 修改调度时间 (Cron格式)
FETCH_SCHEDULE="0 0 * * *"  # 每天午夜
# FETCH_SCHEDULE="0 */6 * * *"  # 每6小时
# FETCH_SCHEDULE="0 9,16 * * 1-5"  # 工作日的9:00和16:00
```

修改后重启:
```bash
make restart
```

## 🛠️ 常用命令

```bash
make help           # 查看所有可用命令
make start          # 启动服务
make stop           # 停止服务
make restart        # 重启服务
make logs           # 查看日志
make once           # 运行一次数据采集
make test           # 测试系统
make db-shell       # 连接数据库
make db-backup      # 备份数据库
make clean          # 清理所有数据
```

## 📈 数据字段说明

每条股票记录包含:
- `symbol`: 股票代码 (如 AAPL)
- `date`: 日期
- `open_price`: 开盘价
- `high_price`: 最高价
- `low_price`: 最低价
- `close_price`: 收盘价
- `volume`: 成交量
- `market_cap`: 市值
- `pe_ratio`: 市盈率
- `turnover_rate`: 换手率

## 🌐 数据源

当前使用 **Yahoo Finance** (通过yfinance库):
- ✅ 免费
- ✅ 无需API密钥
- ✅ 数据丰富
- ✅ 可靠稳定

## 📝 日志位置

- Docker模式: `docker-compose logs -f app`
- 本地模式: `logs/stock_crawler.log`

## 🔍 故障排查

### 数据没有更新?
```bash
# 查看日志
make logs

# 手动运行一次
make once-docker
```

### 数据库连接失败?
```bash
# 检查MySQL是否运行
docker-compose ps

# 重启MySQL
docker-compose restart mysql
```

### 想要重新开始?
```bash
# 清理所有数据和容器
make clean

# 重新启动
make start
```

## 🚢 部署到生产环境

### 修改生产配置

1. 修改 `docker-compose.yml` 中的密码
2. 配置外部MySQL (RDS/云数据库)
3. 设置合适的重启策略

### 部署到云

```bash
# 构建镜像
docker build -t stock-crawler:latest .

# 推送到容器注册表
docker tag stock-crawler:latest your-registry/stock-crawler:latest
docker push your-registry/stock-crawler:latest

# 在云平台创建容器服务
# 配置环境变量指向云数据库
```

详细部署指南请查看 `DEVELOPMENT.md`

## 📚 扩展功能

### 添加更多股票
编辑 `.env`:
```bash
STOCK_SYMBOLS=AAPL,MSFT,GOOGL,AMZN,TSLA,NVDA,META,NFLX,AMD,INTC,CRM,ORCL
```

### 更改获取频率
编辑 `.env`:
```bash
# 每小时
FETCH_SCHEDULE="0 * * * *"

# 每天凌晨2点
FETCH_SCHEDULE="0 2 * * *"

# 工作日早上9点
FETCH_SCHEDULE="0 9 * * 1-5"
```

### 添加新数据源
参考 `DEVELOPMENT.md` 中的扩展指南

## 💡 提示

1. **首次运行**: 会获取过去30天的历史数据
2. **后续运行**: 只获取最新数据，避免重复
3. **数据去重**: 相同日期的数据会自动更新
4. **容错性**: 单个股票失败不影响其他股票

## 📞 需要帮助?

- 查看 `README.md` - 项目概述
- 查看 `DEVELOPMENT.md` - 开发指南
- 运行 `make help` - 查看命令
- 运行 `python test_setup.py` - 测试系统

祝使用愉快！ 📊✨

