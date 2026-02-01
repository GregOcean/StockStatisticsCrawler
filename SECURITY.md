# 🔐 Security Configuration Guide

## ⚠️ Database Password Security

### Problem
The default code had a hardcoded database password (`"123456"`), which is a **security risk** if committed to Git.

### Solution
Store sensitive credentials in `.env` file instead of code.

---

## ✅ What We Changed

### Before (Insecure)
```python
# src/config/settings.py
db_password: str = Field(default="123456", description="Database password")
```
❌ **Problem**: Password visible in Git history

### After (Secure)
```python
# src/config/settings.py
db_password: str = Field(default="", description="Database password (store in .env, not in code)")
```
✅ **Solution**: Password must be in `.env` file

---

## 🔧 Setup Instructions

### Step 1: Create `.env` File

In project root directory, create `.env`:

```bash
cd /Users/yang.wang/Documents/Personal_Project/StockStatisticsCrawler

# Create .env file
cat > .env << 'EOF'
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=stock_user
DB_PASSWORD=your_secure_password_here
DB_NAME=stock_data

# Stock Symbols
STOCK_SYMBOLS=AAPL,MSFT,GOOGL,AMZN,TSLA

# Schedule (9:30 AM ET, Monday-Friday)
FETCH_SCHEDULE=30 9 * * 1-5

# Data Source
DEFAULT_DATA_SOURCE=yfinance

# API Rate Limiting
API_REQUEST_DELAY=2.0
API_MAX_RETRIES=5
API_RETRY_DELAY=10.0

# Application
LOG_LEVEL=INFO
EOF
```

### Step 2: Update Your Password

Edit `.env` and replace `your_secure_password_here` with your actual password:

```bash
# Option 1: Using nano
nano .env

# Option 2: Using vim
vim .env

# Option 3: Using VS Code
code .env
```

### Step 3: Verify `.env` is Ignored by Git

```bash
# Check .gitignore contains .env
grep ".env" .gitignore
```

Should output:
```
.env
```

✅ If found, `.env` will NOT be committed to Git

---

## 🔒 Security Best Practices

### 1. ✅ Never Commit `.env` to Git

```bash
# .gitignore should contain:
.env
.env.local
.env.*.local
```

### 2. ✅ Use Strong Passwords

**Bad passwords:**
- ❌ `123456`
- ❌ `password`
- ❌ `stock123`

**Good passwords:**
- ✅ `K9mP#xL2$vN8qW!eR4tY` (random, 20+ chars)
- ✅ Use password generator

### 3. ✅ Different Passwords for Different Environments

```bash
# Development
DB_PASSWORD=dev_secure_password_xyz123

# Production (different!)
DB_PASSWORD=prod_very_secure_password_abc789
```

### 4. ✅ Check Git History

If you accidentally committed passwords before:

```bash
# Check if passwords are in Git history
git log --all --full-history --source -- src/config/settings.py

# If found, consider using git-filter-repo or BFG Repo-Cleaner
# to remove sensitive data from history
```

### 5. ✅ Use Environment Variables in Production

For cloud deployments, use platform-specific secrets management:

**Docker Compose:**
```yaml
services:
  app:
    environment:
      - DB_PASSWORD=${DB_PASSWORD}
```

**Kubernetes:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  password: <base64-encoded-password>
```

**AWS:**
- Use AWS Secrets Manager or Systems Manager Parameter Store

**GCP:**
- Use Secret Manager

**Azure:**
- Use Key Vault

---

## 📋 Checklist

Before committing code:

- [ ] ✅ `.env` file created with actual passwords
- [ ] ✅ `.env` is in `.gitignore`
- [ ] ✅ No hardcoded passwords in code
- [ ] ✅ `git status` does NOT show `.env` file
- [ ] ✅ Different passwords for dev/staging/prod
- [ ] ✅ Passwords are strong (16+ chars)

---

## 🧪 Test Configuration

### Test 1: Verify `.env` is Loaded

```python
# Quick test
from src.config.settings import get_settings

settings = get_settings()
print(f"DB User: {settings.db_user}")
print(f"DB Host: {settings.db_host}")
print(f"DB Password: {'*' * len(settings.db_password)}")  # Masked
print(f"Database URL: {settings.get_database_url()[:30]}...")  # Partial
```

### Test 2: Verify Git Ignores `.env`

```bash
# Should output nothing (empty)
git status | grep .env

# If .env appears, add it to .gitignore immediately
echo ".env" >> .gitignore
```

---

## 🚨 If Password Was Committed

If you accidentally committed a password to Git:

### Option 1: For Recent Commits (Not Pushed)

```bash
# Remove from last commit
git reset HEAD~1
git add .gitignore .env.example src/config/settings.py
git commit -m "fix: remove hardcoded passwords, use .env instead"
```

### Option 2: Already Pushed to GitHub

**⚠️ IMPORTANT: Change the password immediately!**

Even if you remove it from Git, it's still in the history.

```bash
# 1. Change the database password
mysql -u root -p
> ALTER USER 'stock_user'@'localhost' IDENTIFIED BY 'new_secure_password';

# 2. Update .env with new password

# 3. (Optional) Clean Git history
# Use BFG Repo-Cleaner or git-filter-repo
# See: https://rtyley.github.io/bfg-repo-cleaner/
```

---

## 📚 Related Files

- `.gitignore` - Ensures `.env` is not committed
- `src/config/settings.py` - Loads config from `.env`
- `.env.example` - Template for `.env` (safe to commit)
- `.env` - Actual credentials (**NEVER commit**)

---

## 🔗 References

- [The Twelve-Factor App: Config](https://12factor.net/config)
- [OWASP: Secure Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [GitHub: Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)

---

**Status**: ✅ Configuration secured! Passwords no longer hardcoded.

**Next Steps**:
1. Create `.env` file with actual credentials
2. Test the application
3. Verify `.env` is not tracked by Git

