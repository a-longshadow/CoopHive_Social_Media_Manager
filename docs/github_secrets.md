# GitHub Secrets Configuration

The following secrets need to be configured in GitHub repository settings for CI/CD:

## Required Secrets

### Railway Deployment
- `RAILWAY_TOKEN_STAGING`: API token for staging environment
- `RAILWAY_TOKEN_PROD`: API token for production environment
- `RAILWAY_SERVICE_STAGING`: Railway service name for staging
- `RAILWAY_SERVICE_PROD`: Railway service name for production

### Database Credentials
- `DB_USER`: Database user for tests
- `DB_PASSWORD`: Database password for tests
- `DB_NAME`: Database name for tests

### Django Settings
- `DJANGO_SECRET_KEY`: Django secret key
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DEBUG`: Set to 'True' for staging, 'False' for production

### Email Configuration
- `EMAIL_HOST_USER`: SMTP email user
- `EMAIL_HOST_PASSWORD`: SMTP email password

### Social Media API Keys
- `LINKEDIN_CLIENT_ID`: LinkedIn OAuth client ID
- `LINKEDIN_CLIENT_SECRET`: LinkedIn OAuth client secret
- `TWITTER_API_KEY`: Twitter API key
- `TWITTER_API_SECRET`: Twitter API secret
- `FARCASTER_KEY`: Farcaster API key
- `BLUESKY_HANDLE`: Bluesky handle
- `BLUESKY_APP_PASSWORD`: Bluesky app password

## How to Configure

1. Go to repository Settings
2. Navigate to Secrets and Variables -> Actions
3. Click "New repository secret"
4. Add each secret listed above

## Environment Configuration

The repository has two environments configured:

### Staging (develop branch)
- Uses staging Railway instance
- Debug mode enabled
- Less restrictive security settings

### Production (main branch)
- Uses production Railway instance
- Debug mode disabled
- Strict security settings
- Required reviewers for deployment
