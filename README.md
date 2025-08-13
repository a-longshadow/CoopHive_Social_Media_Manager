# CoopHive Social Media Manager

A scalable Django-based social media management system for LinkedIn, Twitter (X.com), Farcaster, and Bluesky.

## 🚀 Features

- Multi-platform social media management
- Campaign-based content organization
- Scheduled posting
- Media asset management
- Analytics and engagement tracking
- REST API for integrations

## 📋 Supported Platforms

- LinkedIn
- Twitter (X.com)
- Farcaster
- Bluesky

## 🛠️ Quick Start

### Local Development
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (edit with your API keys)
cp .env.example .env  

# Set up Google OAuth (follow prompts)
python manage.py setup_google_oauth

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Production (Railway)
1. Fork/Clone repository
2. Link to Railway
3. Add PostgreSQL service
4. Configure environment variables
5. Deploy

## 🔐 Environment Variables

Required for production deployment:

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=True  # Required by project spec
ALLOWED_HOSTS=.railway.app,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://*.railway.app

# Database (auto-set by Railway)
DATABASE_URL=postgresql://...

# LinkedIn
LINKEDIN_CLIENT_ID=your-client-id
LINKEDIN_CLIENT_SECRET=your-client-secret

# Twitter (X.com)
TWITTER_API_KEY=your-api-key
TWITTER_API_SECRET=your-api-secret

# Farcaster
FARCASTER_KEY=your-farcaster-key

# Bluesky
BLUESKY_HANDLE=your-handle
BLUESKY_APP_PASSWORD=your-app-password
```

## 📚 Documentation

- [API Documentation](docs/api.md)
- [Development Guide](docs/development.md)
- [Deployment Guide](docs/deployment.md)
- [Testing Guide](docs/testing.md)

## 🧪 Testing

Run tests with:
```bash
# Run all tests
python manage.py test

# Run with coverage report
pytest --cov

# Run specific app tests
python manage.py test linkedin
python manage.py test twitter
python manage.py test farcaster
python manage.py test bluesky
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
