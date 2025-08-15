# 🚀 Railway Deployment Fix Guide

## 🚨 IMMEDIATE FIX FOR "Application failed to respond"

Your Railway deployment is failing. Follow these steps **IN ORDER** to fix it.

## 📋 STEP 1: SET REQUIRED ENVIRONMENT VARIABLES

Go to your Railway dashboard → Variables and add these **EXACT** variables:

### 🔧 Core Django Settings
```bash
DJANGO_SETTINGS_MODULE=coophive.settings_railway
SECRET_KEY=django-insecure-your-very-secure-secret-key-change-this-in-production
DEBUG=False
PORT=8000
PYTHONPATH=.
```

### 🌐 Host Configuration
```bash
ALLOWED_HOSTS=coophive-social-media-manager.up.railway.app,localhost,127.0.0.1,.railway.app
CSRF_TRUSTED_ORIGINS=https://coophive-social-media-manager.up.railway.app,https://*.railway.app
```

### 📧 Email Configuration (Required for super admin access)
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=noreply@coophive.network
```

### 🔐 Domain Restriction
```bash
DOMAIN_RESTRICTION_ENABLED=True
ALLOWED_DOMAIN=coophive.network
```

### 🔑 Google OAuth (Update with production domain)
```bash
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
```

## 📋 STEP 2: ADD POSTGRESQL DATABASE

1. In Railway dashboard, click **"New Service"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway will automatically add `DATABASE_URL` to your environment

## 📋 STEP 3: UPDATE GOOGLE OAUTH FOR PRODUCTION

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to your OAuth 2.0 credentials
3. Add this authorized redirect URI:
   ```
   https://coophive-social-media-manager.up.railway.app/accounts/google/login/callback/
   ```

## 📋 STEP 4: REDEPLOY THE APPLICATION

1. In Railway dashboard, click **"Deploy"** or trigger a new deployment
2. Wait for deployment to complete (check logs for progress)
3. The app should now respond at: https://coophive-social-media-manager.up.railway.app/

## 🔍 STEP 5: CHECK RAILWAY LOGS

To see what's happening during deployment:

1. Go to Railway dashboard → Your service
2. Click **"Logs"** tab
3. Look for error messages

**Expected successful startup logs:**
```
🚀 Railway settings loaded successfully!
DEBUG: False
ALLOWED_HOSTS: ['coophive-social-media-manager.up.railway.app', ...]
DATABASE_URL: SET
SECRET_KEY: SET
```

## 🚨 COMMON ISSUES & FIXES

### Issue 1: "SECRET_KEY not set"
**Fix:** Add `SECRET_KEY` environment variable in Railway dashboard

### Issue 2: "Database connection failed"
**Fix:** Ensure PostgreSQL service is added and `DATABASE_URL` is set

### Issue 3: "ALLOWED_HOSTS error"
**Fix:** Verify `ALLOWED_HOSTS` includes your Railway domain

### Issue 4: "Static files not found"
**Fix:** Deployment command runs `collectstatic` automatically

### Issue 5: "Google OAuth not working"
**Fix:** Update redirect URI in Google Cloud Console

## 🎯 VERIFICATION CHECKLIST

After deployment, verify these work:

- [ ] App loads at https://coophive-social-media-manager.up.railway.app/
- [ ] Django admin accessible at `/admin/`
- [ ] Google OAuth login works at `/accounts/login/`
- [ ] Super admin users can log in (joe@coophive.network, levi@coophive.network)
- [ ] n8n API endpoints respond:
  - `/twitter/api/check-duplicate-tweet/` (POST)
  - `/twitter/api/receive-tweets/` (POST)

## 🔧 DEBUGGING COMMANDS

If you have Railway CLI installed:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and connect to your project
railway login
railway link

# Check logs
railway logs

# Check environment variables
railway variables

# Connect to database
railway connect
```

## 📞 EMERGENCY RECOVERY

If deployment still fails:

1. **Check Railway logs** for specific error messages
2. **Verify all environment variables** are set correctly
3. **Test locally** with Railway settings:
   ```bash
   export DJANGO_SETTINGS_MODULE=coophive.settings_railway
   python manage.py check --deploy
   python manage.py runserver
   ```

## ✅ SUCCESS INDICATORS

Your deployment is working when:

- ✅ Railway logs show "Railway settings loaded successfully!"
- ✅ App responds at production URL
- ✅ No error messages in Railway logs
- ✅ Database migrations complete successfully
- ✅ Static files are served correctly
- ✅ Super admin users can log in

---

## 🎉 WHAT THIS FIX DOES

1. **Creates production settings** (`coophive/settings_railway.py`)
2. **Configures Railway deployment** (`railway.json`, `Procfile`)
3. **Sets up PostgreSQL** database connection
4. **Handles static files** with Whitenoise
5. **Configures logging** for debugging
6. **Sets security headers** for production
7. **Runs migrations** and setup commands automatically

**Follow these steps exactly and your Railway deployment will work!**
