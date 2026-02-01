# Yahoo Finance API 测试指南

## 🎯 快速测试

### 运行 API 测试 Demo

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行API测试demo（独立，快速）
python demo_api_test.py
```

这个demo会测试：
- ✅ 网络连接
- ✅ yfinance库导入
- ✅ 创建Ticker对象
- ✅ 获取历史数据
- ✅ 使用download函数
- ✅ 测试多个股票代码
- ✅ 获取股票详细信息

## 📊 测试输出示例

### 成功的输出：
```
╔══════════════════════════════════════════════════════════╗
║               Yahoo Finance API Test Demo                ║
╚══════════════════════════════════════════════════════════╝

============================================================
Test 0: Network Connectivity
============================================================
Testing internet connection...
✓ Internet connection OK

Testing Yahoo Finance domain...
✓ Yahoo Finance reachable (status: 200)

============================================================
Test 1: Import yfinance
============================================================
✓ yfinance imported successfully
  Version: 0.2.37

============================================================
Test 2: Simple Ticker Query
============================================================
Creating ticker for AAPL...
✓ Ticker object created

============================================================
Test 3: Fetch Historical Data
============================================================
Fetching last 5 days of data...
✓ Successfully fetched 5 days

Data preview:
                 Open       High        Low      Close     Volume
Date                                                              
2026-01-27  225.30  227.80  224.50  226.50   45123000
...

============================================================
Test Summary
============================================================

Critical tests (must pass):
  Network         ✓ PASS
  Import          ✓ PASS
  History         ✓ PASS
  Download        ✓ PASS

✓ ALL CRITICAL TESTS PASSED!

Your Yahoo Finance API is working correctly.
You can proceed with the main application.
```

### 失败的输出（限流）：
```
============================================================
Test 3: Fetch Historical Data
============================================================
Fetching last 5 days of data...
✗ Failed: 429 Client Error: Too Many Requests

============================================================
Test Summary
============================================================

✗ 1 critical test(s) failed

Possible issues:
  1. Rate limiting - wait 5-10 minutes and try again
  2. Network/firewall blocking Yahoo Finance
  3. Yahoo Finance service temporarily down
```

## 🔍 故障排查

### 如果测试失败：

1. **Rate Limiting (最常见)**
   ```bash
   # 等待5-10分钟
   sleep 300
   
   # 重试
   python demo_api_test.py
   ```

2. **网络问题**
   ```bash
   # 检查能否访问Yahoo
   curl -I https://finance.yahoo.com
   
   # 检查DNS
   ping finance.yahoo.com
   ```

3. **依赖缺失**
   ```bash
   # 重新安装依赖
   pip install -r requirements.txt
   
   # 或单独安装
   pip install yfinance requests pandas
   ```

4. **代理/防火墙问题**
   - 检查是否在公司网络（可能有限制）
   - 尝试使用个人网络或VPN
   - 配置代理（如需要）

## 📝 各测试项说明

### Test 0: Network Connectivity
- **作用**：检查基础网络连接
- **重要性**：必须通过
- **失败原因**：无网络、防火墙、DNS问题

### Test 1: Import yfinance
- **作用**：检查库是否正确安装
- **重要性**：必须通过
- **失败原因**：未安装或版本不兼容
- **修复**：`pip install yfinance`

### Test 2: Simple Ticker Query
- **作用**：创建Ticker对象
- **重要性**：基础测试
- **失败原因**：库导入失败

### Test 3: Fetch Historical Data ⭐
- **作用**：获取历史价格数据
- **重要性**：核心功能，必须通过
- **失败原因**：Rate limiting, 网络问题
- **这是最常失败的测试**

### Test 4: Using yf.download() ⭐
- **作用**：使用另一种方式获取数据
- **重要性**：核心功能，必须通过
- **失败原因**：Rate limiting, 网络问题

### Test 5: Multiple Symbols
- **作用**：测试批量获取
- **重要性**：可选
- **失败原因**：Rate limiting（更容易触发）

### Test 6: Ticker Detailed Info
- **作用**：获取公司详细信息
- **重要性**：可选（经常失败也正常）
- **说明**：这个API最不稳定，失败不影响主功能

## 🎯 使用场景

### 1. 首次安装后
```bash
# 验证环境配置正确
source venv/bin/activate
python demo_api_test.py
```

### 2. 遇到API问题时
```bash
# 快速诊断问题
python demo_api_test.py

# 如果失败，等待后重试
sleep 300
python demo_api_test.py
```

### 3. 部署前验证
```bash
# 在新服务器上验证API可用性
python demo_api_test.py
```

### 4. 调试数据获取问题
```bash
# 独立测试，不依赖数据库等其他组件
python demo_api_test.py
```

## 🆚 与其他测试的区别

| 测试脚本 | 用途 | 依赖 | 运行时间 |
|---------|------|------|---------|
| `demo_api_test.py` | 只测试API | 仅yfinance | 30秒 |
| `test_setup.py` | 完整系统测试 | 全部组件 | 1-2分钟 |
| `make once` | 实际运行一次 | 数据库+API | 2-5分钟 |

## 💡 建议的测试流程

```bash
# 1. 先运行API demo（最快）
python demo_api_test.py

# 2. 如果通过，运行完整测试
python test_setup.py

# 3. 如果都通过，实际运行
python src/main.py --mode once
```

## 🚀 下一步

如果 `demo_api_test.py` 通过：
- ✅ API 工作正常
- ✅ 可以运行完整测试
- ✅ 可以启动应用

如果失败：
- ⏰ 等待5-10分钟（rate limit）
- 🔍 检查网络连接
- 📚 查看 RATE_LIMIT.md
- 🐳 尝试使用Docker（可能更稳定）

---

**快速命令参考：**
```bash
python demo_api_test.py          # API测试
python test_setup.py             # 完整测试  
python src/main.py --mode once   # 实际运行
```

