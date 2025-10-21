# Quick Render Deployment - Single User

**Time Required**: 30 minutes  
**Cost**: $0/month (Free tier)

---

## Quick Steps

### 1️⃣ GitHub (5 min)
```bash
cd /Users/daivikvennela/workspace/testApp/IntegrityHoops/testApp1
git init
git add .
git commit -m "Ready for Render"
git remote add origin https://github.com/YOUR_USERNAME/integrityhoops-basketball-dashboard.git
git push -u origin main
```

### 2️⃣ Render Database (5 min)
1. Go to https://render.com → Sign up with GitHub
2. New + → PostgreSQL
3. Name: `integrityhoops-db`, Plan: Free
4. Copy "Internal Database URL"

### 3️⃣ Render Web Service (10 min)
1. New + → Web Service
2. Connect repo: `integrityhoops-basketball-dashboard`
3. Settings:
   - Build: `pip install -r config/requirements.txt`
   - Start: `cd testApp1 && gunicorn --workers=2 --bind 0.0.0.0:$PORT --timeout 120 src.core.app:app`
   - Plan: Free

4. Environment Variables:
   ```
   SECRET_KEY = [Generate]
   FLASK_ENV = production
   DEBUG = False
   DATABASE_URL = [Paste Internal URL from step 2]
   PYTHON_VERSION = 3.12.0
   MAX_CONTENT_LENGTH = 16777216
   UPLOAD_FOLDER = /tmp/uploads
   PROCESSED_FOLDER = /tmp/processed
   ```

5. Click "Create Web Service"

### 4️⃣ Migrate Database (10 min)
```bash
# Get External Database URL from Render dashboard
export DATABASE_URL="paste-external-url-here"

# Backup
cp src/core/data/basketball.db basketball_backup_$(date +%Y%m%d).db

# Migrate
python migrate_to_postgres.py
```

### 5️⃣ Done! 🎉
Visit: `https://integrityhoops.onrender.com`

---

## Environment Variables Quick Copy

```
SECRET_KEY=[Click Generate]
FLASK_ENV=production
DEBUG=False
DATABASE_URL=[Paste from database]
PYTHON_VERSION=3.12.0
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=/tmp/uploads
PROCESSED_FOLDER=/tmp/processed
```

---

## Troubleshooting

**Build fails?** → Check logs, verify requirements.txt path  
**502 error?** → Check DATABASE_URL is set correctly  
**Migration fails?** → Use External URL (not Internal)  
**Slow first load?** → Normal! Cold start on free tier (~30s)

---

## Free Tier Features

✅ Automatic HTTPS  
✅ PostgreSQL database (256MB)  
✅ Auto-deploy on git push  
✅ Daily backups (7 days)  
✅ 100GB bandwidth/month  

⚠️ Cold starts after 15 min idle  
⚠️ Ephemeral file storage  

---

**Full guide**: See `RENDER_DEPLOYMENT_STEPS.md`

