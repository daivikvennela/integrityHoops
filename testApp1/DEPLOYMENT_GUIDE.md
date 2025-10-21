# 🚀 Cloud Deployment Guide
## Basketball Cognitive Performance Dashboard

This guide will walk you through deploying your Flask application to various cloud platforms.

---

## 📋 Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Platform Options](#platform-options)
3. [Recommended: Render Deployment](#render-deployment-recommended)
4. [Alternative: Railway Deployment](#railway-deployment)
5. [Alternative: Heroku Deployment](#heroku-deployment)
6. [Alternative: AWS Deployment](#aws-deployment-advanced)
7. [Database Migration](#database-migration)
8. [Environment Variables](#environment-variables)
9. [Post-Deployment Steps](#post-deployment-steps)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Pre-Deployment Checklist

### 1. Security & Configuration
- [ ] Change the secret key in production
- [ ] Set up environment variables
- [ ] Configure allowed hosts
- [ ] Enable HTTPS/SSL
- [ ] Review file upload size limits

### 2. Database Considerations
- [ ] SQLite → PostgreSQL migration (recommended for production)
- [ ] Database backup strategy
- [ ] Migration scripts ready

### 3. Static Files
- [ ] All static files properly referenced
- [ ] CSS/JS files accessible
- [ ] File upload directories configured

### 4. Testing
- [ ] Test all routes locally
- [ ] Verify database connections
- [ ] Check file upload functionality
- [ ] Test analytics dashboard

---

## 🌐 Platform Options

| Platform | Difficulty | Cost | Best For |
|----------|-----------|------|----------|
| **Render** | ⭐ Easy | Free tier available | Quick deployment, PostgreSQL included |
| **Railway** | ⭐ Easy | $5/month usage | Modern UI, great DX |
| **Heroku** | ⭐⭐ Easy | $5-7/month | Established platform |
| **AWS (Elastic Beanstalk)** | ⭐⭐⭐ Medium | Pay as you go | Enterprise scale |
| **Google Cloud (App Engine)** | ⭐⭐⭐ Medium | Pay as you go | Google ecosystem |
| **Azure** | ⭐⭐⭐ Medium | Pay as you go | Microsoft ecosystem |
| **DigitalOcean** | ⭐⭐⭐⭐ Advanced | $12+/month | Full control, VPS |

---

## 🎨 Render Deployment (RECOMMENDED)

**Why Render?**
- ✅ Free tier with PostgreSQL
- ✅ Automatic HTTPS
- ✅ Simple deployment
- ✅ Git-based deploys
- ✅ Great for Flask apps

### Step-by-Step Guide

#### 1. Prepare Your Application

Create `render.yaml` in your project root:
```yaml
services:
  - type: web
    name: integrityhoops
    env: python
    buildCommand: pip install -r config/requirements.txt
    startCommand: gunicorn --chdir /Users/daivikvennela/workspace/testApp/IntegrityHoops/testApp1/src/core run_app:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.0
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: integrityhoops-db
          property: connectionString
      - key: FLASK_ENV
        value: production

databases:
  - name: integrityhoops-db
    databaseName: integrityhoops
    user: integrityhoops_user
```

#### 2. Update Your Application for PostgreSQL

Install PostgreSQL adapter:
```bash
pip install psycopg2-binary
```

Add to `config/requirements.txt`:
```
psycopg2-binary==2.9.9
```

#### 3. Create Production Config File

Create `src/core/config.py`:
```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # If DATABASE_URL starts with postgres://, change to postgresql://
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = '/tmp/uploads'  # Render uses ephemeral storage
    PROCESSED_FOLDER = '/tmp/processed'
    
class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

#### 4. Deploy to Render

1. **Push to GitHub** (if not already)
   ```bash
   git init
   git add .
   git commit -m "Prepare for deployment"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Sign up at render.com**
   - Go to https://render.com
   - Sign up with GitHub

3. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository
   - Configure:
     - **Name**: integrityhoops
     - **Environment**: Python 3
     - **Build Command**: `pip install -r config/requirements.txt`
     - **Start Command**: `cd testApp1 && gunicorn --bind 0.0.0.0:$PORT src.core.app:app`
     - **Instance Type**: Free

4. **Create PostgreSQL Database**
   - Click "New +" → "PostgreSQL"
   - Name: integrityhoops-db
   - Select Free tier
   - Copy the Internal Database URL

5. **Add Environment Variables**
   In your web service settings:
   - `DATABASE_URL`: (paste the internal database URL)
   - `SECRET_KEY`: (generate a random string)
   - `FLASK_ENV`: production
   - `PYTHON_VERSION`: 3.12.0

6. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)

#### 5. Access Your App
Your app will be available at: `https://integrityhoops.onrender.com`

---

## 🚂 Railway Deployment

Railway is another excellent option with a modern interface.

#### 1. Install Railway CLI
```bash
npm install -g @railway/cli
# or
brew install railway
```

#### 2. Login and Initialize
```bash
railway login
cd testApp1
railway init
```

#### 3. Add PostgreSQL Database
```bash
railway add --database postgresql
```

#### 4. Set Environment Variables
```bash
railway variables set SECRET_KEY=your-secret-key-here
railway variables set FLASK_ENV=production
```

#### 5. Create `railway.json`
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd testApp1 && gunicorn --bind 0.0.0.0:$PORT src.core.app:app",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 6. Deploy
```bash
railway up
```

Your app will be live at: `https://your-app.up.railway.app`

---

## 🟪 Heroku Deployment

#### 1. Install Heroku CLI
```bash
brew tap heroku/brew && brew install heroku
# or download from https://devcenter.heroku.com/articles/heroku-cli
```

#### 2. Login and Create App
```bash
heroku login
cd testApp1
heroku create integrityhoops
```

#### 3. Add PostgreSQL
```bash
heroku addons:create heroku-postgresql:mini
```

#### 4. Create Procfile
```
web: cd testApp1 && gunicorn src.core.app:app
```

#### 5. Create runtime.txt
```
python-3.12.0
```

#### 6. Set Environment Variables
```bash
heroku config:set SECRET_KEY=your-secret-key-here
heroku config:set FLASK_ENV=production
```

#### 7. Deploy
```bash
git push heroku main
heroku open
```

---

## ☁️ AWS Deployment (Advanced)

For AWS deployment using Elastic Beanstalk:

#### 1. Install EB CLI
```bash
pip install awsebcli
```

#### 2. Initialize EB
```bash
cd testApp1
eb init -p python-3.12 integrityhoops
```

#### 3. Create Environment
```bash
eb create integrityhoops-env
```

#### 4. Configure Database
- Go to AWS Console → RDS
- Create PostgreSQL database
- Update environment variables

#### 5. Deploy
```bash
eb deploy
```

---

## 🗄️ Database Migration

### From SQLite to PostgreSQL

#### Option 1: Using pgloader (Recommended)

1. **Install pgloader**
   ```bash
   brew install pgloader  # macOS
   # or
   apt-get install pgloader  # Linux
   ```

2. **Create migration script** (`migrate_db.load`):
   ```
   LOAD DATABASE
     FROM sqlite://testApp1/src/core/data/basketball.db
     INTO postgresql://username:password@hostname:5432/integrityhoops
   
   WITH include drop, create tables, create indexes, reset sequences
   
   SET work_mem to '16MB', maintenance_work_mem to '512 MB';
   ```

3. **Run migration**:
   ```bash
   pgloader migrate_db.load
   ```

#### Option 2: Manual Export/Import

1. **Export SQLite data**:
   ```bash
   sqlite3 basketball.db .dump > dump.sql
   ```

2. **Clean up SQL for PostgreSQL**:
   - Remove SQLite-specific commands
   - Update data types
   - Fix AUTOINCREMENT → SERIAL

3. **Import to PostgreSQL**:
   ```bash
   psql -h hostname -U username -d integrityhoops -f dump.sql
   ```

#### Option 3: Using Python Script

Create `migrate_to_postgres.py`:

```python
import sqlite3
import psycopg2
import os

# Source SQLite database
sqlite_conn = sqlite3.connect('testApp1/src/core/data/basketball.db')
sqlite_cursor = sqlite_conn.cursor()

# Destination PostgreSQL database
pg_conn = psycopg2.connect(os.environ['DATABASE_URL'])
pg_cursor = pg_conn.cursor()

# Get all tables
sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = sqlite_cursor.fetchall()

for table in tables:
    table_name = table[0]
    print(f"Migrating table: {table_name}")
    
    # Get all data from SQLite
    sqlite_cursor.execute(f"SELECT * FROM {table_name}")
    rows = sqlite_cursor.fetchall()
    
    # Get column names
    sqlite_cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in sqlite_cursor.fetchall()]
    
    # Insert into PostgreSQL
    placeholders = ','.join(['%s'] * len(columns))
    insert_query = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
    
    for row in rows:
        try:
            pg_cursor.execute(insert_query, row)
        except Exception as e:
            print(f"Error inserting row: {e}")
            continue
    
    pg_conn.commit()
    print(f"✓ Migrated {len(rows)} rows from {table_name}")

sqlite_conn.close()
pg_conn.close()
print("✓ Migration complete!")
```

Run with:
```bash
python migrate_to_postgres.py
```

---

## 🔐 Environment Variables

Create `.env.example` (template for team):
```bash
# Flask Configuration
SECRET_KEY=change-this-in-production
FLASK_ENV=production
DEBUG=False

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# File Upload
MAX_CONTENT_LENGTH=16777216  # 16MB in bytes
UPLOAD_FOLDER=/tmp/uploads
PROCESSED_FOLDER=/tmp/processed

# Application
APP_NAME=IntegrityHoops
HOST=0.0.0.0
PORT=8000
```

Create `.env` for local development (DO NOT COMMIT):
```bash
SECRET_KEY=dev-secret-key-for-local-only
FLASK_ENV=development
DEBUG=True
DATABASE_URL=sqlite:///basketball.db
```

Update `.gitignore`:
```
.env
*.db
__pycache__/
*.pyc
venv/
venv312/
/tmp/
*.log
```

---

## ✅ Post-Deployment Steps

### 1. Verify Deployment
- [ ] Can you access the homepage?
- [ ] Are all routes working?
- [ ] Can you upload files?
- [ ] Is the analytics dashboard loading?
- [ ] Are player management features working?

### 2. Set Up Monitoring
- Enable application monitoring (built-in on most platforms)
- Set up error tracking (Sentry.io)
- Configure log aggregation

### 3. Performance Optimization
- Enable caching
- Optimize database queries
- Compress static assets
- Set up CDN for static files (optional)

### 4. Custom Domain (Optional)
Most platforms support custom domains:
- Purchase domain (e.g., integrityhoops.com)
- Add CNAME record pointing to your app
- Enable SSL/HTTPS

### 5. Backups
- Set up automated database backups
- Export critical data regularly
- Test restore procedures

---

## 🔧 Troubleshooting

### Issue: App crashes on startup
**Solution**: Check logs
```bash
# Render
View logs in dashboard

# Railway
railway logs

# Heroku
heroku logs --tail
```

### Issue: Database connection fails
**Solution**: Verify DATABASE_URL
- Check environment variables
- Ensure PostgreSQL is running
- Verify connection string format

### Issue: Static files not loading
**Solution**: Check file paths
- Verify `static_folder` configuration
- Use absolute paths
- Check file permissions

### Issue: File uploads failing
**Solution**: Storage configuration
- Use cloud storage (S3, Cloudinary)
- Or configure ephemeral storage correctly
- Check MAX_CONTENT_LENGTH setting

### Issue: Slow performance
**Solutions**:
- Upgrade instance type
- Add database indexes
- Enable caching
- Use CDN for static files

---

## 📚 Additional Resources

### Documentation
- [Render Python Guide](https://render.com/docs/deploy-flask)
- [Railway Python Guide](https://docs.railway.app/languages/python)
- [Heroku Python Guide](https://devcenter.heroku.com/categories/python-support)
- [Flask Deployment Options](https://flask.palletsprojects.com/en/2.3.x/deploying/)

### Tools
- **Sentry**: Error tracking - https://sentry.io
- **Cloudinary**: Image hosting - https://cloudinary.com
- **AWS S3**: File storage - https://aws.amazon.com/s3/
- **Datadog**: Monitoring - https://www.datadoghq.com

---

## 🎯 Recommended Path for You

Based on your application, I recommend:

1. **Quick Start** (Today):
   - Deploy to **Render** (free tier)
   - Use PostgreSQL database (included)
   - Get a working URL immediately

2. **Phase 2** (Week 1):
   - Migrate SQLite data to PostgreSQL
   - Set up custom domain
   - Enable monitoring

3. **Phase 3** (Week 2):
   - Upgrade to paid tier if needed
   - Set up file storage (S3 or Cloudinary)
   - Implement caching
   - Add automated backups

4. **Future** (As needed):
   - Scale up infrastructure
   - Add load balancing
   - Implement CI/CD pipeline
   - Set up staging environment

---

## 🚀 Next Steps

1. Choose your platform (recommend: Render)
2. Follow the step-by-step guide above
3. Test thoroughly
4. Share your live URL!

**Questions?** Check the troubleshooting section or reach out for help.

Good luck with your deployment! 🎉

