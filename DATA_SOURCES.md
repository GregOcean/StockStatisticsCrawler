# 股票数据源对比和选择指南

## 📊 可用数据源总览

### 免费数据源

#### 1. Yahoo Finance (yfinance) ⭐ 当前使用

**优点**:
- ✅ 完全免费，无需API key
- ✅ 数据全面（价格、成交量、财务指标）
- ✅ 历史数据丰富
- ✅ Python库成熟稳定
- ✅ 支持全球市场

**缺点**:
- ❌ 有限流限制（~30-50请求/分钟）
- ❌ 偶尔不稳定
- ❌ 无官方支持
- ❌ 延迟数据（15-20分钟）

**适合场景**: 
- 中小规模应用（<100只股票）
- 每日更新（非实时）
- 个人项目

**限制**:
```
每分钟: ~30-50 请求
每小时: ~1000-2000 请求
每天: ~48000 请求
```

**集成难度**: ⭐ (已实现)

---

#### 2. Alpha Vantage ⭐⭐⭐ 推荐备选

**官网**: https://www.alphavantage.co/

**优点**:
- ✅ 免费500次API调用/天
- ✅ 官方API，稳定可靠
- ✅ 数据质量高
- ✅ 支持实时数据（付费）
- ✅ 技术指标API
- ✅ 新闻和情绪分析API

**缺点**:
- ⚠️ 需要注册获取API key
- ⚠️ 免费版每分钟5次调用限制
- ⚠️ 免费版每天500次限制

**定价**:
```
Free:        500 calls/day,  5 calls/minute
Premium:     $49.99/month,   75 calls/minute,  unlimited daily
Pro:         $149.99/month,  600 calls/minute, unlimited daily
```

**适合场景**:
- 50只以下股票（免费）
- 需要稳定API
- 对数据质量要求高

**集成难度**: ⭐⭐ (容易)

**示例代码**:
```python
import requests

API_KEY = 'your_key_here'
symbol = 'AAPL'
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}'
response = requests.get(url)
data = response.json()
```

---

#### 3. IEX Cloud ⭐⭐

**官网**: https://iexcloud.io/

**优点**:
- ✅ 免费50,000条消息/月
- ✅ 实时数据
- ✅ 官方API，稳定
- ✅ 文档完善
- ✅ WebSocket支持

**缺点**:
- ⚠️ 需要API key
- ⚠️ 免费额度有限
- ⚠️ 按"消息"计费，不是按请求

**定价**:
```
Free:      50,000 messages/month
Launch:    $9/month,  500,000 messages
Grow:      $19/month, 5,000,000 messages
Scale:     $99/month, 100,000,000 messages
```

**适合场景**:
- 小规模实时应用
- 需要WebSocket
- 对成本敏感

**集成难度**: ⭐⭐

---

#### 4. Polygon.io ⭐⭐⭐

**官网**: https://polygon.io/

**优点**:
- ✅ 免费层：5次API调用/分钟
- ✅ 实时和历史数据
- ✅ WebSocket支持
- ✅ 期权数据
- ✅ 新闻和基本面

**缺点**:
- ⚠️ 免费层非常有限
- ⚠️ 延迟数据（15分钟）

**定价**:
```
Free:      5 API calls/minute,    2 years historical
Starter:   $29/month,  unlimited,  2 years historical
Developer: $99/month,  unlimited,  full historical
Advanced:  $249/month, real-time,  full historical
```

**适合场景**:
- 需要期权数据
- 愿意付费的专业应用

**集成难度**: ⭐⭐

---

#### 5. Finnhub ⭐⭐

**官网**: https://finnhub.io/

**优点**:
- ✅ 免费60次API调用/分钟
- ✅ 实时数据
- ✅ 全球市场
- ✅ 新闻和财报
- ✅ 社交情绪数据

**缺点**:
- ⚠️ 免费版功能有限
- ⚠️ 历史数据不全

**定价**:
```
Free:   60 calls/minute
Starter: $59.99/month
Pro:    $149.99/month
```

**适合场景**:
- 需要情绪分析
- 国际市场

**集成难度**: ⭐⭐

---

#### 6. Twelve Data ⭐⭐

**官网**: https://twelvedata.com/

**优点**:
- ✅ 免费800次API调用/天
- ✅ 技术指标丰富
- ✅ 外汇和加密货币
- ✅ WebSocket支持

**缺点**:
- ⚠️ 每分钟8次调用限制
- ⚠️ 免费版延迟15分钟

**定价**:
```
Free:  800 calls/day,   8 calls/minute
Basic: $29/month,       800 calls/minute
Pro:   $79/month,       3000 calls/minute
```

**适合场景**:
- 需要技术指标
- 多资产类别

**集成难度**: ⭐⭐

---

#### 7. EOD Historical Data

**官网**: https://eodhistoricaldata.com/

**优点**:
- ✅ 丰富的历史数据
- ✅ 基本面数据详细
- ✅ 全球市场

**缺点**:
- ❌ 无免费层
- ⚠️ 较贵

**定价**:
```
All-World: $79.99/month
```

**适合场景**:
- 需要全球历史数据
- 基本面分析

**集成难度**: ⭐⭐

---

### 高级数据源（企业级）

#### 8. Quandl (Nasdaq Data Link)

**官网**: https://data.nasdaq.com/

**优点**:
- ✅ 数据质量最高
- ✅ 另类数据丰富
- ✅ 企业级支持

**缺点**:
- ❌ 价格昂贵
- ⚠️ 部分数据集免费

**适合场景**:
- 机构投资
- 量化基金

---

#### 9. Bloomberg API / Reuters

**优点**:
- ✅ 最全面的数据
- ✅ 实时新闻
- ✅ 专业级

**缺点**:
- ❌ 极其昂贵（$20,000+/年）
- ❌ 需要专业终端

**适合场景**:
- 金融机构
- 专业交易员

---

## 📈 推荐方案

### 方案1：免费组合（最推荐）⭐⭐⭐⭐⭐

**Yahoo Finance (主) + Alpha Vantage (备)**

```python
# 配置
PRIMARY_SOURCE = "yfinance"
FALLBACK_SOURCE = "alphavantage"

# 逻辑
try:
    data = fetch_from_yfinance(symbol)
except RateLimitError:
    data = fetch_from_alphavantage(symbol)
```

**优点**:
- ✅ 完全免费
- ✅ 可靠性高
- ✅ 互为备份

**缺点**:
- ⚠️ 需要申请Alpha Vantage API key
- ⚠️ Alpha Vantage每天500次限制

**适用场景**: 
- 个人项目
- 中小规模（<100只股票）
- 每日更新

---

### 方案2：付费稳定（推荐生产环境）⭐⭐⭐⭐

**Alpha Vantage Premium ($49.99/月)**

**优点**:
- ✅ 官方支持
- ✅ 75次/分钟，足够大部分需求
- ✅ 稳定可靠
- ✅ 实时数据

**适用场景**:
- 商业应用
- 100-500只股票
- 需要稳定性

---

### 方案3：大规模（专业级）⭐⭐⭐

**Polygon.io Developer ($99/月)**

**优点**:
- ✅ 无限API调用
- ✅ 实时数据
- ✅ 期权和衍生品数据
- ✅ 完整历史数据

**适用场景**:
- 500+只股票
- 需要实时数据
- 专业应用

---

## 🔧 集成建议

### 快速对比表

| 数据源 | 免费额度 | 价格 | 实时 | 历史 | 集成难度 | 推荐度 |
|--------|---------|------|------|------|---------|--------|
| Yahoo Finance | 无限* | 免费 | ❌ | ✅ | ⭐ | ⭐⭐⭐⭐ |
| Alpha Vantage | 500/天 | $49.99/月 | ✅ | ✅ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| IEX Cloud | 50k/月 | $9/月 | ✅ | ✅ | ⭐⭐ | ⭐⭐⭐ |
| Polygon.io | 5/分钟 | $29/月 | ⚠️ | ✅ | ⭐⭐ | ⭐⭐⭐⭐ |
| Finnhub | 60/分钟 | $59.99/月 | ✅ | ⚠️ | ⭐⭐ | ⭐⭐⭐ |
| Twelve Data | 800/天 | $29/月 | ⚠️ | ✅ | ⭐⭐ | ⭐⭐⭐ |

*有限流

---

## 💡 我的建议

### 如果是个人项目（<50只股票）:
**继续使用 Yahoo Finance**，配合我已经优化的限流策略。

优点：
- 完全免费
- 已经实现
- 满足需求

调整：
- 增加延迟到2-3秒
- 非高峰时段运行
- 分批获取（如需要）

---

### 如果需要更好的稳定性（50-200只股票）:
**添加 Alpha Vantage 作为备选**

实现方式：
1. 主要使用Yahoo Finance
2. 遇到限流时切换到Alpha Vantage
3. 每天500次足够作为备用

成本：免费（或$49.99/月如需更多）

---

### 如果是商业应用（200+只股票）:
**使用 Polygon.io Developer ($99/月)**

优点：
- 无限API调用
- 实时数据
- 专业支持
- 期权数据

或者：
**Alpha Vantage Premium ($49.99/月) + 分批策略**

---

## 🚀 下一步行动

### 选项1：继续优化当前方案（推荐）

```bash
# 1. 增加延迟
API_REQUEST_DELAY=3.0

# 2. 分批运行
# 早上运行第1批
# 中午运行第2批
# 下午运行第3批

# 3. 非交易时段运行
FETCH_SCHEDULE="0 2 * * *"  # 凌晨2点
```

### 选项2：添加Alpha Vantage备选

我可以帮你实现双数据源架构：
1. 主：Yahoo Finance（免费）
2. 备：Alpha Vantage（免费500次/天）

### 选项3：升级到付费服务

根据你的规模和需求，选择合适的付费服务。

---

## 📚 相关资源

- **Alpha Vantage文档**: https://www.alphavantage.co/documentation/
- **Polygon.io文档**: https://polygon.io/docs/
- **IEX Cloud文档**: https://iexcloud.io/docs/
- **Finnhub文档**: https://finnhub.io/docs/api

---

**你想要我帮你实现哪个方案？** 🤔

