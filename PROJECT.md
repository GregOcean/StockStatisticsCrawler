# 项目总览

## 📁 完整项目结构

```
StockStatisticsCrawler/
│
├── 📄 核心配置文件
│   ├── requirements.txt          # Python依赖包
│   ├── .env.example              # 环境变量模板
│   ├── .gitignore                # Git忽略规则
│   ├── Dockerfile                # Docker镜像构建文件
│   ├── docker-compose.yml        # Docker编排配置
│   └── init.sql                  # MySQL初始化脚本
│
├── 📚 文档
│   ├── README.md                 # 项目说明（主文档）
│   ├── QUICKSTART.md             # 5分钟快速上手
│   ├── DEVELOPMENT.md            # 开发和扩展指南
│   └── PROJECT.md                # 本文件 - 项目总览
│
├── 🔧 工具脚本
│   ├── start.sh                  # 快速启动脚本
│   ├── test_setup.py             # 系统测试脚本
│   ├── utils.py                  # 实用工具脚本
│   ├── queries.sql               # SQL查询示例
│   └── Makefile                  # Make命令集合
│
└── 📦 源代码 (src/)
    ├── __init__.py
    ├── main.py                   # 主程序入口
    │
    ├── config/                   # 配置管理模块
    │   ├── __init__.py
    │   └── settings.py           # 应用配置类
    │
    ├── models/                   # 数据模型层
    │   ├── __init__.py
    │   └── stock_data.py         # 股票数据ORM模型
    │
    ├── data_sources/             # 数据源层（可扩展）
    │   ├── __init__.py
    │   ├── base.py               # 数据源抽象基类
    │   └── yfinance_source.py    # Yahoo Finance实现
    │
    ├── storage/                  # 存储层（可扩展）
    │   ├── __init__.py
    │   ├── base.py               # 存储抽象基类
    │   └── mysql_storage.py      # MySQL存储实现
    │
    ├── scheduler/                # 任务调度模块
    │   ├── __init__.py
    │   └── job_scheduler.py      # 调度器实现
    │
    └── utils/                    # 工具模块
        └── __init__.py           # 日志配置
```

## 🏗️ 架构设计

### 设计原则

1. **分层架构**: 清晰的模块划分，职责单一
2. **抽象基类**: 易于扩展新的数据源和存储后端
3. **配置驱动**: 通过环境变量灵活配置
4. **容器化**: 支持Docker部署，易于迁移
5. **错误处理**: 完善的异常捕获和日志记录

### 核心组件

```
┌─────────────────────────────────────────────────────────┐
│                     StockCrawlerApp                      │
│                      (main.py)                           │
└─────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │  Config  │    │  Scheduler│    │  Logger  │
    │ Settings │    │  (Cron)  │    │  (Utils) │
    └──────────┘    └──────────┘    └──────────┘
            │               │               │
            └───────────────┼───────────────┘
                            │
            ┌───────────────┼───────────────┐
            │                               │
            ▼                               ▼
    ┌───────────────┐              ┌───────────────┐
    │  Data Source  │              │    Storage    │
    │   (Abstract)  │              │   (Abstract)  │
    └───────────────┘              └───────────────┘
            │                               │
            ▼                               ▼
    ┌───────────────┐              ┌───────────────┐
    │   YFinance    │              │     MySQL     │
    │ Implementation│              │ Implementation│
    └───────────────┘              └───────────────┘
            │                               │
            └───────────────┬───────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  StockDataDTO │
                    │   (Transfer)  │
                    └───────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  StockData    │
                    │   (Model)     │
                    └───────────────┘
```

### 数据流

```
1. 定时触发
   └─> Scheduler.fetch_and_store_data()

2. 获取数据
   └─> DataSource.fetch_stock_data(symbol)
       └─> Yahoo Finance API
       └─> 返回 List[StockDataDTO]

3. 存储数据
   └─> Storage.save_stock_data(data)
       └─> 检查是否存在
       └─> 插入或更新
       └─> MySQL Database

4. 日志记录
   └─> Logger记录各个步骤的状态
```

## 🔄 工作流程

### 启动流程

1. **初始化配置** - 加载环境变量
2. **连接数据库** - 建立MySQL连接
3. **初始化Schema** - 创建表（如果不存在）
4. **设置调度器** - 配置定时任务
5. **首次执行** - 立即执行一次数据获取
6. **进入调度** - 按Cron表达式定期执行

### 数据获取流程

```
foreach symbol in configured_symbols:
    1. 查询数据库最新日期
    2. 确定获取范围（最新日期+1 到 今天）
    3. 调用数据源API获取数据
    4. 转换为StockDataDTO列表
    5. 保存到数据库（去重/更新）
    6. 记录日志
    7. 处理下一个symbol
```

## 🎯 设计亮点

### 1. 可扩展性

**添加新数据源**:
```python
# 只需实现BaseDataSource接口
class NewDataSource(BaseDataSource):
    def fetch_stock_data(self, symbol, start_date, end_date):
        # 实现逻辑
        pass
```

**添加新存储**:
```python
# 只需实现BaseStorage接口
class PostgresStorage(BaseStorage):
    def save_stock_data(self, data):
        # 实现逻辑
        pass
```

### 2. 数据一致性

- 使用 `(symbol, date)` 唯一索引避免重复
- 自动处理更新：存在则更新，不存在则插入
- 事务保护确保数据完整性

### 3. 容错机制

- 单个股票失败不影响其他股票
- 数据库连接池和健康检查
- 详细的错误日志和堆栈追踪
- 优雅的关闭和资源清理

### 4. 性能优化

- 增量更新，只获取新数据
- 批量插入减少数据库交互
- 数据库索引优化查询
- 连接池复用减少开销

## 🚀 部署策略

### 开发环境
```bash
# 本地开发
python src/main.py --mode once
```

### 测试环境
```bash
# Docker单机部署
docker-compose up -d
```

### 生产环境
```yaml
# Kubernetes部署
- 使用云数据库（RDS）
- 配置资源限制
- 启用日志收集
- 设置监控告警
```

## 📊 监控指标

建议监控的关键指标:

1. **数据采集指标**
   - 每日成功采集的股票数量
   - 数据获取成功率
   - API调用延迟

2. **存储指标**
   - 数据库写入成功率
   - 数据库容量使用
   - 表记录数增长

3. **系统指标**
   - 应用内存使用
   - CPU使用率
   - 日志错误率

4. **业务指标**
   - 数据新鲜度（最新数据的日期）
   - 数据完整性（缺失的交易日）
   - 数据质量（NULL值比例）

## 🔐 安全考虑

1. **敏感信息**
   - 数据库密码通过环境变量配置
   - 不在代码中硬编码凭证
   - .env文件不提交到版本控制

2. **网络安全**
   - 使用HTTPS API
   - 数据库使用内网访问
   - 容器间使用专用网络

3. **数据安全**
   - 定期备份数据库
   - 使用参数化查询防止SQL注入
   - 设置适当的数据库权限

## 🧪 测试策略

1. **单元测试** (待实现)
   - 测试各个模块的独立功能
   - Mock外部依赖

2. **集成测试**
   - `test_setup.py` 测试完整流程
   - 验证数据源连接
   - 验证数据库操作

3. **端到端测试**
   - `make once` 运行完整采集流程
   - 验证数据准确性

## 📈 未来扩展

### 短期计划
- [ ] 添加更多数据源（Alpha Vantage, IEX）
- [ ] 支持更多金融指标（dividend, split, earnings）
- [ ] 添加数据质量检查
- [ ] 实现数据导出功能（CSV, JSON）

### 中期计划
- [ ] Web管理界面
- [ ] RESTful API接口
- [ ] 实时数据流支持
- [ ] 数据清洗和标准化

### 长期计划
- [ ] 支持加密货币数据
- [ ] 支持全球股市
- [ ] 机器学习数据准备
- [ ] 分布式采集架构

## 🤝 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📞 技术支持

- 查看文档: README.md, QUICKSTART.md, DEVELOPMENT.md
- 运行测试: `python test_setup.py`
- 查看日志: `make logs` 或 `logs/stock_crawler.log`

---

**项目状态**: ✅ 生产就绪

**最后更新**: 2026-01

**维护者**: Stock Data Team

