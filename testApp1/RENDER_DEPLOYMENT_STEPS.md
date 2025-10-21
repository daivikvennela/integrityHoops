# Render Deployment Steps - Ready to Deploy!

Your application has been updated for production deployment. Follow these steps to deploy to Render.

---

## ✅ Step 1: Create GitHub Repository (5 minutes)

1. **Go to GitHub**: https://github.com/new

2. **Create Repository**:
   - Name: `integrityhoops-basketball-dashboard`
   - Description: `Basketball Cognitive Performance Analytics Dashboard`
   - Visibility: **Private** (recommended)
   - Do NOT initialize with README (we have code already)
   - Click "Create repository"

3. **Push Your Code**:
   
   Open Terminal and run these commands from the `testApp1` directory:

   ```bash
   cd /Users/daivikvennela/workspace/testApp/IntegrityHoops/testApp1
   
   # Initialize git (if not already done)
   git init
   
   # Add all files
   git add .
   
   # Commit
   git commit -m "Initial commit: IntegrityHoops ready for Render deployment"
   
   # Add remote (replace YOUR_USERNAME with your GitHub username)
   git remote add origin https://github.com/YOUR_USERNAME/integrityhoops-basketball-dashboard.git
   
   # Push to GitHub
   git branch -M main
   git push -u origin main
   ```

   **Note**: If git asks for credentials, use your GitHub username and a Personal Access Token (not your password).

---

## ✅ Step 2: Create Render Account & Database (10 minutes)

### 2.1 Sign Up for Render

1. Go to: https://render.com
2. Click "Get Started"
3. Sign up using your GitHub account
4. Authorize Render to access your repositories

### 2.2 Create PostgreSQL Database

1. In Render dashboard, click **"New +"** → **"PostgreSQL"**

2. Configure database:
   - **Name**: `integrityhoops-db`
   - **Database**: `integrityhoops`
   - **User**: `integrityhoops_user`
   - **Region**: `Oregon` (or closest to you)
   - **PostgreSQL Version**: 16 (default)
   - **Plan**: **Free**

3. Click **"Create Database"**

4. ⚠️ **IMPORTANT**: Once created, go to the database page and copy:
   - **Internal Database URL** (starts with `postgres://`)
   - Save this for the next step!

---

## ✅ Step 3: Deploy Web Service (5 minutes)

### 3.1 Create Web Service

1. In Render dashboard, click **"New +"** → **"Web Service"**

2. **Connect Repository**:
   - Click "Connect" next to your GitHub repository
   - Select: `integrityhoops-basketball-dashboard`
   - Click "Connect"

### 3.2 Configure Web Service

Fill in these settings:

| Setting | Value |
|---------|-------|
| **Name** | `integrityhoops` |
| **Region** | `Oregon` (same as database) |
| **Branch** | `main` |
| **Root Directory** | (leave empty) |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r config/requirements.txt` |
| **Start Command** | `cd testApp1 && gunicorn --workers=2 --bind 0.0.0.0:$PORT --timeout 120 src.core.app:app` |
| **Plan** | **Free** |

### 3.3 Add Environment Variables

Scroll down to "Environment Variables" and add these:

| Key | Value | Notes |
|-----|-------|-------|
| `SECRET_KEY` | Click **"Generate"** button | Auto-generates secure key |
| `FLASK_ENV` | `production` | Type this exactly |
| `DEBUG` | `False` | Type this exactly |
| `DATABASE_URL` | Paste Internal URL from Step 2.2 | From your database |
| `PYTHON_VERSION` | `3.12.0` | Type this exactly |
| `MAX_CONTENT_LENGTH` | `16777216` | Type this exactly |
| `UPLOAD_FOLDER` | `/tmp/uploads` | Type this exactly |
| `PROCESSED_FOLDER` | `/tmp/processed` | Type this exactly |

### 3.4 Deploy!

1. Click **"Create Web Service"**
2. Render will start building and deploying (5-10 minutes)
3. Watch the logs - you'll see:
   - Installing dependencies
   - Starting gunicorn
   - "Your service is live" message

4. Once deployed, your app will be at: `https://integrityhoops.onrender.com`

---

## ✅ Step 4: Migrate Database (10 minutes)

Now we need to transfer your data from SQLite to PostgreSQL.

### 4.1 Get External Database URL

1. Go to your Render database page
2. Copy the **"External Database URL"** (different from Internal URL!)
3. It looks like: `postgres://user:password@host/database`

### 4.2 Backup Local Database

```bash
cd /Users/daivikvennela/workspace/testApp/IntegrityHoops/testApp1

# Create backup
cp src/core/data/basketball.db basketball_backup_$(date +%Y%m%d).db
```

### 4.3 Run Migration

```bash
# Set the database URL (paste your External URL)
export DATABASE_URL="paste-external-database-url-here"

# Activate virtual environment (if you have one)
# source venv/bin/activate

# Install PostgreSQL adapter (if not already installed)
pip install psycopg2-binary

# Run migration script
python migrate_to_postgres.py
```

The script will:
- Connect to both databases
- Copy all tables and data
- Verify the migration
- Show you results

---

## ✅ Step 5: Verify Deployment (5 minutes)

### 5.1 Test Your Application

Visit your URL: `https://integrityhoops.onrender.com`

Test these features:
- ✅ Homepage loads
- ✅ Analytics dashboard displays (first tab)
- ✅ Navigate to SmartDash
- ✅ Navigate to Players
- ✅ Settings page works
- ✅ Try uploading a file (remember: ephemeral storage)

### 5.2 Check Logs

If anything doesn't work:
1. Go to Render dashboard → Your service → Logs
2. Look for error messages
3. Common issues are in the troubleshooting section below

---

## 🎉 You're Live!

Your application is now deployed at: `https://integrityhoops.onrender.com`

### Important Notes for Single User:

1. **Cold Starts**: App sleeps after 15 min of inactivity
   - First load after sleep takes ~30 seconds
   - This is normal for free tier
   - Subsequent loads are instant

2. **File Uploads**: Files are temporary
   - Uploaded files persist during normal operation
   - Deleted on app restart/redeploy
   - Perfect for single-user temporary analysis

3. **Database**: Your data is safe!
   - PostgreSQL has persistent storage
   - Automatic daily backups
   - Data survives restarts

4. **Cost**: $0/month
   - 100% free with limitations above
   - Upgrade to $7/month to remove cold starts

---

## 🔧 Troubleshooting

### Issue: "Build Failed"
**Check**:
- Verify `config/requirements.txt` exists
- Check build logs for specific error
- Ensure Python version matches `runtime.txt`

**Solution**: Review logs and fix any package conflicts

### Issue: "Application Error" or 502
**Check**:
- Review application logs in Render
- Verify start command is correct
- Check DATABASE_URL is set

**Solution**: Look for specific error in logs

### Issue: Database Connection Error
**Check**:
- Verify DATABASE_URL environment variable is set
- Ensure you used **Internal** Database URL for the web service
- Check database is in same region as web service

**Solution**: Re-copy the Internal Database URL to environment variables

### Issue: Migration Script Fails
**Check**:
- Are you using **External** Database URL? (not Internal)
- Is psycopg2-binary installed locally?
- Can you connect to database from your machine?

**Solution**: 
```bash
# Test connection
psql "your-external-database-url"
```

### Issue: Static Files Not Loading
**Check**:
- View page source, look at file paths
- Check browser console for 404 errors

**Solution**: Usually auto-fixed on redeploy

---

## 📊 Monitoring Your App

### Built-in Render Monitoring:

1. Go to your service → Metrics
2. You can see:
   - CPU usage
   - Memory usage
   - Request count
   - Response times

### Set Up Alerts:

1. Go to Settings → Notifications
2. Add your email
3. Get notified of:
   - Deployment failures
   - Service down
   - High error rates

---

## 🔄 Making Updates

After making code changes:

```bash
# Commit changes
git add .
git commit -m "Your change description"

# Push to GitHub
git push

# Render will auto-deploy! (takes 2-3 minutes)
```

Watch the deployment in Render dashboard.

---

## 🎯 Next Steps (Optional)

### Add Custom Domain
1. Render dashboard → Settings → Custom Domain
2. Add your domain (e.g., integrityhoops.com)
3. Update DNS records as shown
4. SSL certificate is automatic!

### Upgrade to Paid Tier
If cold starts are annoying:
1. Settings → Plan
2. Upgrade to Starter ($7/month)
3. No more cold starts!

### Add Permanent File Storage
For permanent file uploads:
1. Sign up for AWS S3 (free tier available)
2. Update application to use S3
3. Files persist forever

---

## 📝 Important URLs to Save

Create a note with:
- Production URL: `https://integrityhoops.onrender.com`
- Render Dashboard: `https://dashboard.render.com`
- GitHub Repo: `https://github.com/YOUR_USERNAME/integrityhoops-basketball-dashboard`
- Database Internal URL: (from Render dashboard)
- Database External URL: (for migrations)

---

## ✅ Success Checklist

- [ ] GitHub repository created and code pushed
- [ ] Render account created
- [ ] PostgreSQL database created
- [ ] Web service deployed successfully
- [ ] Environment variables configured
- [ ] Database migration completed
- [ ] Application accessible online
- [ ] All features tested and working
- [ ] Logs reviewed - no critical errors

---

## 🆘 Need Help?

1. **Check Render Logs**: Most issues show up here
2. **Review Documentation**: See `DEPLOYMENT_GUIDE.md` for detailed info
3. **Render Support**: https://render.com/docs
4. **Community**: Render has a community forum

---

**Congratulations on your deployment! 🚀🏀**

Your Basketball Cognitive Performance Dashboard is now live on the internet!

