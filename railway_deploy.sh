#!/bin/bash

# Railway Deployment Script for CoopHive Social Media Manager
echo "🚀 Starting Railway deployment..."

# Set environment to production
export DJANGO_SETTINGS_MODULE=coophive.settings_railway

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Initialize settings if needed
echo "⚙️ Initializing application settings..."
python manage.py init_settings

# Create super admins if they don't exist
echo "👑 Creating super admin users..."
python manage.py create_super_admins

# Verify deployment
echo "✅ Verifying deployment..."
python manage.py check --deploy

echo "🎉 Railway deployment completed successfully!"
echo "🌐 Your app should be available at: https://coophive-social-media-manager.up.railway.app"
