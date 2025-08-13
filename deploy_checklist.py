#!/usr/bin/env python3
"""
Railway Deployment Checklist for CoopHive Social Media Manager
Run this before deploying to ensure everything is configured correctly.
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(".")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coophive.settings")
django.setup()

from django.conf import settings
from django.db import connections

def check_environment_variables():
    """Check critical environment variables."""
    print("\n🔑 Checking Environment Variables...")
    required_vars = {
        'SECRET_KEY': 'Django secret key',
        'DATABASE_URL': 'Railway PostgreSQL URL',
        'LINKEDIN_CLIENT_ID': 'LinkedIn OAuth client ID',
        'TWITTER_API_KEY': 'Twitter API key',
        'FARCASTER_KEY': 'Farcaster API key',
        'BLUESKY_HANDLE': 'Bluesky handle'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"❌ {var} - {description}")
    
    if missing_vars:
        print("Missing required environment variables:")
        for var in missing_vars:
            print(f"   {var}")
        return False
    
    print("✅ All required environment variables are set")
    return True

def check_database_connection():
    """Check database connectivity."""
    print("\n🗄️ Checking Database Connection...")
    try:
        connections['default'].cursor()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def check_railway_environment():
    """Check Railway-specific environment requirements."""
    print("\n🚂 Railway Environment Requirements...")
    print("   📋 Required environment variables in Railway dashboard:")
    print("   • DATABASE_URL (auto-populated by Railway Postgres)")
    print("   • SECRET_KEY (random 50-char string)")
    print("   • ALLOWED_HOSTS (include .railway.app domains)")
    print("   • CSRF_TRUSTED_ORIGINS (https://*.railway.app)")
    print("   • LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET")
    print("   • TWITTER_API_KEY and TWITTER_API_SECRET")
    print("   • FARCASTER_KEY")
    print("   • BLUESKY_HANDLE and BLUESKY_APP_PASSWORD")

def main():
    """Run all deployment checks."""
    print("🚀 CoopHive Social Media Manager - Railway Deployment Checklist")
    print("=" * 70)

    checks_passed = 0
    total_checks = 2

    # Run checks
    if check_environment_variables():
        checks_passed += 1

    if check_database_connection():
        checks_passed += 1

    # Show Railway environment info
    check_railway_environment()

    # Summary
    print("\n" + "=" * 70)
    print(f"📊 Deployment Readiness: {checks_passed}/{total_checks} checks passed")

    if checks_passed == total_checks:
        print("🎉 READY FOR DEPLOYMENT!")
        print("\n📋 Final steps:")
        print("1. Commit and push to GitHub")
        print("2. Railway will auto-deploy")
        print("3. Run migrations: python manage.py migrate (on Railway)")
        print("4. Test site at: https://coophive-social-media-manager-production.up.railway.app/")
    else:
        print("❌ NOT READY - Fix issues above before deploying")

if __name__ == "__main__":
    main()
