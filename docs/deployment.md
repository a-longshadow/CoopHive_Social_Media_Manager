# Railway Deployment Guide

## Prerequisites
- Railway account
- GitHub repository
- PostgreSQL client (optional, for manual DB access)

## 1. Deployment Steps

### Step 1: Link Repository to Railway
1. Go to [Railway Dashboard](https://railway.app)
2. Click "New Project"
3. Choose "Deploy from GitHub repo"
4. Select your repository

### Step 2: Add PostgreSQL
1. Click "New Service" in your project
2. Choose "Database"
3. Select "PostgreSQL"
4. Railway will automatically add DATABASE_URL to your environment

### Step 3: Configure Environment Variables
In Railway dashboard, add these variables:

```bash
SECRET_KEY=your-secure-secret-key
DEBUG=True
ALLOWED_HOSTS=.railway.app,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://*.railway.app

# Social Media API Keys
LINKEDIN_CLIENT_ID=your-client-id
LINKEDIN_CLIENT_SECRET=your-client-secret
TWITTER_API_KEY=your-api-key
TWITTER_API_SECRET=your-api-secret
FARCASTER_KEY=your-farcaster-key
BLUESKY_HANDLE=your-handle
BLUESKY_APP_PASSWORD=your-app-password
```

### Step 4: Deploy
1. Railway will automatically deploy when you push to main
2. Wait for build to complete
3. Run migrations:
   ```bash
   # Using Railway CLI
   railway run python manage.py migrate
   ```

### Step 5: Verify Deployment
1. Check the deployment URL provided by Railway
2. Verify the admin interface works
3. Test social media integrations

## 2. Development Workflow

### Local to Production
1. Develop and test locally
2. Run deployment checks:
   ```bash
   python deploy_checklist.py
   ```
3. Push to main branch
4. Railway auto-deploys

### Database Management
- Railway provides PostgreSQL management interface
- Can connect using psql with provided credentials
- Automatic backups included

## 3. Troubleshooting

### Common Issues

#### Database Migrations
If migrations aren't applied:
```bash
railway run python manage.py migrate
```

#### Static Files
If static files aren't served:
1. Verify STATIC_ROOT setting
2. Run collectstatic:
   ```bash
   railway run python manage.py collectstatic --noinput
   ```

#### CSRF Errors
1. Check ALLOWED_HOSTS includes Railway domain
2. Verify CSRF_TRUSTED_ORIGINS configuration

#### API Integration Issues
1. Verify API keys in Railway environment variables
2. Check API service status
3. Review application logs in Railway dashboard

## 4. Monitoring

### Health Checks
- `/health/` endpoint provides system status
- Includes database connectivity check
- API integration status

### Logs
- Available in Railway dashboard
- Includes application and database logs
- Filterable by severity

## 5. Scaling

### Database
- Railway PostgreSQL auto-scales
- Monitoring available in dashboard

### Web Service
- Adjust resources in Railway dashboard
- Configure gunicorn workers as needed

## 6. Security Notes

- Keep DEBUG=True as per project requirements
- Ensure all sensitive data uses environment variables
- Regular security updates via requirements.txt
- Monitor Railway security advisories

## 7. Backup and Recovery

### Database Backups
- Automated by Railway PostgreSQL service
- Manual backup option available
- Point-in-time recovery supported

### Emergency Rollback
1. Railway dashboard → Deployments
2. Find last working deployment
3. Click "Redeploy"

## 8. Cost Management

### Free Tier
- Sufficient for development
- Limited hours per month

### Production
- Costs based on usage
- PostgreSQL separate pricing
- Monitor Railway dashboard for usage
