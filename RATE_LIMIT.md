# Yahoo Finance API 限流问题说明和解决方案

## 问题

当你看到这个错误时：
```
429 Client Error: Too Many Requests
Yahoo Finance is not available
```

这是 Yahoo Finance 的反爬虫保护机制触发了。

## 原因

1. **短时间内请求太多** - Yahoo Finance 限制了免费 API 的访问频率
2. **IP 被临时限制** - 可能是你或同网络的其他人频繁访问导致
3. **地区限制** - 某些地区访问频率限制更严格

## 解决方案

### 1. 等待后重试（推荐）

```bash
# 等待 5 分钟
sleep 300

# 重新运行测试
source venv/bin/activate
python test_setup.py
```

### 2. 已添加的自动重试机制

代码已经更新，包含：
- ✅ **自动重试** - 遇到 429 错误会自动重试 3 次
- ✅ **指数退避** - 每次重试等待时间递增（5s, 10s, 15s）
- ✅ **请求延迟** - 每个请求之间自动延迟 1 秒

### 3. 调整请求参数

如果仍然遇到问题，可以编辑 `src/data_sources/yfinance_source.py`：

```python
# 增加延迟时间（在文件开头）
REQUEST_DELAY = 2.0      # 从 1.0 改为 2.0 秒
MAX_RETRIES = 5          # 从 3 改为 5 次
RETRY_DELAY = 10.0       # 从 5.0 改为 10.0 秒
```

### 4. 减少测试股票数量

编辑 `.env` 文件，减少测试的股票数量：

```bash
# 从多个股票
STOCK_SYMBOLS=AAPL,MSFT,GOOGL,AMZN,TSLA

# 改为只测试一个
STOCK_SYMBOLS=AAPL
```

### 5. 使用代理（高级）

如果经常遇到限流，可以考虑：
- 使用 VPN 或代理
- 使用付费的 Yahoo Finance API
- 使用其他数据源（Alpha Vantage, IEX Cloud）

## 最佳实践

### 开发测试时：
```bash
# 1. 只测试单个股票
STOCK_SYMBOLS=AAPL

# 2. 增加请求延迟
REQUEST_DELAY = 2.0

# 3. 避免频繁运行测试
# 先确保代码无误，再测试数据获取
```

### 生产环境：
```bash
# 1. 使用合理的调度频率
FETCH_SCHEDULE="0 0 * * *"  # 每天一次，而非每小时

# 2. 分批获取股票
# 如果有很多股票，可以分组分时段获取

# 3. 监控错误率
# 如果经常遇到 429，调整延迟时间
```

## 当前配置

项目已配置：
- ✅ 请求间隔：1 秒
- ✅ 自动重试：3 次
- ✅ 重试延迟：5/10/15 秒（递增）
- ✅ 优雅降级：限流时返回空数据而非崩溃

## 测试建议

第一次测试时：

```bash
# 1. 等待几分钟（让 IP 冷却）
sleep 300

# 2. 只测试配置
python -c "from src.config import get_settings; print(get_settings().symbols_list)"

# 3. 只测试数据库
# 跳过数据源测试，先确保数据库正常

# 4. 单独测试数据获取
source venv/bin/activate
python -c "
from src.data_sources import YFinanceDataSource
import time
ds = YFinanceDataSource()
time.sleep(5)  # 等待 5 秒
data = ds.fetch_stock_data('AAPL')
print(f'Fetched {len(data)} records')
"
```

## Yahoo Finance 使用限制

免费使用限制（大约）：
- 每分钟：~50 个请求
- 每小时：~2000 个请求
- 每天：~48000 个请求

超过限制会触发 429 错误。

## 替代方案

如果经常遇到限流，考虑其他数据源：

1. **Alpha Vantage** - 免费但需要 API key
2. **IEX Cloud** - 有免费额度
3. **Polygon.io** - 提供免费层级
4. **Finnhub** - 免费股票数据 API

项目设计支持轻松添加新数据源！

---

**现在就试试：**

```bash
# 等待 5 分钟后重试
sleep 300
source venv/bin/activate
python test_setup.py
```

