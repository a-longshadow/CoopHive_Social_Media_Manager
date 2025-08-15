# Railway Deployment Guide for CoopHive Social Media Manager

## 🚀 Quick Fix for "Application failed to respond"

Your Railway deployment is failing because of missing environment variables and configuration. Follow this guide to fix it.

## 📋 Required Environment Variables

### 1. Django Core Variables
Set these in Railway dashboard → Variables:

```bash
# Django Settings
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
DJANGO_SETTINGS_MODULE=coophive.settings_railway

# Host Configuration
ALLOWED_HOSTS=coophive-social-media-manager.up.railway.app,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://coophive-social-media-manager.up.railway.app
```

### 2. Email Configuration
```bash
# Email Settings (for super admin password reset)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=noreply@coophive.network
```

### 3. Google OAuth (for production domain)
```bash
# Google OAuth (update with production domain)
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
```

### 4. Domain Restriction
```bash
# Domain restriction for production
DOMAIN_RESTRICTION_ENABLED=True
ALLOWED_DOMAIN=coophive.network
```

## 🔧 Railway Configuration Steps

### Step 1: Add PostgreSQL Database
1. Go to Railway dashboard
2. Click "New Service" → "Database" → "PostgreSQL"
3. Railway will automatically add `DATABASE_URL` to your environment

### Step 2: Set Environment Variables
1. Go to your service in Railway dashboard
2. Click "Variables" tab
3. Add all the variables listed above
4. Click "Save"

### Step 3: Update Google OAuth for Production
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Update your OAuth 2.0 credentials
3. Add authorized redirect URI:
   ```
   https://coophive-social-media-manager.up.railway.app/accounts/google/login/callback/
   ```

### Step 4: Redeploy
1. In Railway dashboard, click "Deploy"
2. Wait for deployment to complete
3. Check logs for any errors

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. "Application failed to respond"
**Cause**: Missing environment variables or database connection issues
**Solution**: 
- Check Railway logs: `railway logs`
- Verify all environment variables are set
- Ensure PostgreSQL is connected

#### 2. Database Connection Errors
**Cause**: Missing `DATABASE_URL` or PostgreSQL not running
**Solution**:
- Add PostgreSQL service in Railway
- Verify `DATABASE_URL` is automatically set
- Check database is running

#### 3. Static Files Not Loading
**Cause**: Missing static file collection
**Solution**:
- Ensure `whitenoise` is in requirements.txt
- Static files are collected automatically during deployment

#### 4. Google OAuth Not Working
**Cause**: Wrong redirect URI or missing credentials
**Solution**:
- Update Google OAuth redirect URI for production domain
- Verify `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` are set

#### 5. Email Not Working
**Cause**: Missing email credentials
**Solution**:
- Set `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` in Railway
- Use Gmail app password, not regular password

## 📊 Monitoring and Debugging

### Check Railway Logs
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and check logs
railway login
railway link
railway logs
```

### Test Database Connection
```bash
# Connect to Railway database
railway connect
```

### Verify Environment Variables
```bash
# Check all environment variables
railway variables
```

## 🔒 Security Checklist

- [ ] `DEBUG=False` in production
- [ ] `SECRET_KEY` is secure and unique
- [ ] `ALLOWED_HOSTS` includes your Railway domain
- [ ] `CSRF_TRUSTED_ORIGINS` includes your Railway domain
- [ ] Google OAuth redirect URI updated for production
- [ ] Email credentials are secure (Gmail app password)
- [ ] Database is properly secured

## 🚀 Deployment Commands

### Manual Deployment (if needed)
```bash
# Set environment
export DJANGO_SETTINGS_MODULE=coophive.settings_railway

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Initialize settings
python manage.py init_settings

# Create super admins
python manage.py create_super_admins

# Check deployment
python manage.py check --deploy
```

## 📞 Getting Help

If you're still having issues:

1. **Check Railway logs** for specific error messages
2. **Verify all environment variables** are set correctly
3. **Test locally** with Railway settings: `DJANGO_SETTINGS_MODULE=coophive.settings_railway python manage.py runserver`
4. **Check database connectivity** with Railway PostgreSQL
5. **Verify Google OAuth** redirect URI is correct

## 🎉 Success Indicators

Your Railway deployment is working when:
- ✅ App responds at https://coophive-social-media-manager.up.railway.app
- ✅ Django admin is accessible
- ✅ Google OAuth login works
- ✅ Super admin users can log in
- ✅ n8n integration endpoints respond
- ✅ No errors in Railway logs

---

**This guide should fix your "Application failed to respond" error on Railway!**
