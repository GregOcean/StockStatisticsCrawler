# 部署前检查清单 ✅

在部署到生产环境前，请确保完成以下检查项：

## 1️⃣ 环境准备

- [ ] Docker 已安装并运行
- [ ] Docker Compose 已安装
- [ ] 有足够的磁盘空间（建议至少10GB）
- [ ] 网络可以访问 Yahoo Finance

## 2️⃣ 配置检查

- [ ] 复制 `.env.example` 到 `.env`
- [ ] 修改数据库密码（生产环境）
- [ ] 配置要跟踪的股票代码
- [ ] 设置合适的调度时间
- [ ] 确认日志级别设置

```bash
# 编辑 .env 文件
vim .env

# 必须配置的项目:
# DB_PASSWORD=your_secure_password_here
# STOCK_SYMBOLS=AAPL,MSFT,GOOGL,AMZN,TSLA
# FETCH_SCHEDULE="0 0 * * *"
```

## 3️⃣ 本地测试

```bash
# 1. 运行系统测试
python test_setup.py

# 预期结果: 所有测试通过
# ✓ Configuration
# ✓ Data Source  
# ✓ Database

# 2. 运行一次数据采集
python src/main.py --mode once

# 预期结果: 成功获取并存储数据
# 日志中应该看到类似:
# INFO - Fetched 5 records for AAPL
# INFO - Saved 5 records for AAPL
```

## 4️⃣ Docker测试

```bash
# 1. 构建镜像
docker-compose build

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f app

# 4. 验证数据
make db-shell
# 在MySQL中执行:
SELECT COUNT(*) FROM stock_data;
SELECT DISTINCT symbol FROM stock_data;
```

## 5️⃣ 数据验证

```bash
# 使用工具脚本检查
python utils.py stats

# 预期输出:
# Total records: XXX
# Data by symbol:
# AAPL       30 records  from 2026-01-01 to 2026-01-30
# ...
```

## 6️⃣ 生产环境配置

### 数据库配置

- [ ] 使用云数据库（RDS/云数据库）替代容器MySQL
- [ ] 配置数据库备份策略
- [ ] 设置数据库连接池大小
- [ ] 启用慢查询日志

### 应用配置

- [ ] 修改 `docker-compose.yml` 中的密码
- [ ] 设置 `restart: always` 策略
- [ ] 配置日志轮转
- [ ] 限制容器资源使用

```yaml
# docker-compose.yml 生产配置示例
services:
  app:
    restart: always
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 监控配置

- [ ] 配置日志收集（ELK/Loki）
- [ ] 设置性能监控（Prometheus）
- [ ] 配置告警通知
- [ ] 创建监控Dashboard

## 7️⃣ 安全检查

- [ ] 数据库密码强度足够（生产环境）
- [ ] 不在代码中硬编码密码
- [ ] `.env` 文件不提交到Git
- [ ] 数据库仅允许内网访问
- [ ] 容器使用非root用户运行

## 8️⃣ 备份策略

```bash
# 设置自动备份
0 2 * * * cd /path/to/project && make db-backup

# 或在 crontab 中:
crontab -e
# 添加:
0 2 * * * docker exec stock_mysql mysqldump -u stock_user -p stock_data > /backups/stock_data_$(date +\%Y\%m\%d).sql
```

## 9️⃣ 部署到云

### AWS ECS部署检查

- [ ] ECR仓库已创建
- [ ] 镜像已推送
- [ ] RDS MySQL已创建
- [ ] ECS任务定义已配置
- [ ] 环境变量已设置
- [ ] CloudWatch日志已配置

### 阿里云ACK部署检查

- [ ] 容器镜像服务已配置
- [ ] RDS MySQL已创建
- [ ] ACK集群已创建
- [ ] Deployment已配置
- [ ] ConfigMap/Secret已设置
- [ ] SLS日志服务已配置

## 🔟 运行验证

部署完成后验证：

```bash
# 1. 检查容器状态
docker-compose ps
# 所有服务应为 "Up"

# 2. 检查日志无错误
docker-compose logs app | grep ERROR
# 应该没有严重错误

# 3. 验证数据更新
docker-compose exec mysql mysql -u stock_user -pstock_password -e "
  SELECT symbol, MAX(date) as latest_date 
  FROM stock_data.stock_data 
  GROUP BY symbol;
"
# 应该看到最新日期的数据

# 4. 验证调度器运行
docker-compose logs app | grep "Starting scheduler"
# 应该看到调度器已启动
```

## 📋 故障排查清单

如果遇到问题：

### 数据库连接失败
```bash
# 检查MySQL是否运行
docker-compose ps mysql

# 检查网络连接
docker-compose exec app ping mysql

# 查看MySQL日志
docker-compose logs mysql
```

### 数据获取失败
```bash
# 测试网络连接
docker-compose exec app curl -I https://finance.yahoo.com

# 手动运行一次
docker-compose run app python src/main.py --mode once

# 查看详细日志
docker-compose logs -f app
```

### 调度器不执行
```bash
# 检查Cron表达式是否正确
# 检查时区设置
# 查看调度器日志
docker-compose logs app | grep scheduler
```

## ✅ 最终检查

部署完成后，确认以下几点：

- [ ] 服务正常运行 (docker-compose ps 显示 Up)
- [ ] 数据正常更新 (数据库中有最新数据)
- [ ] 日志正常输出 (无严重错误)
- [ ] 调度器正常工作 (按时执行任务)
- [ ] 监控告警已配置
- [ ] 备份策略已启用
- [ ] 文档已更新

## 🎉 部署完成

如果所有检查项都已完成，恭喜！你已成功部署股票数据采集服务。

### 日常维护

```bash
# 查看状态
make logs

# 查看数据统计
python utils.py stats

# 手动触发采集
docker-compose run app python src/main.py --mode once

# 备份数据
make db-backup

# 更新代码后重启
git pull
docker-compose build
docker-compose restart app
```

### 获取帮助

- 📖 查看文档: README.md, QUICKSTART.md, DEVELOPMENT.md
- 🔍 运行测试: python test_setup.py
- 📊 查看统计: python utils.py stats
- 📝 查看日志: make logs

---

**记住**: 定期检查日志、监控数据质量、及时备份！

