from django.apps import AppConfig
from django.db import connection


class UserAccountManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_account_manager'
    
    def ready(self):
        """Initialize super admin users when the app is ready."""
        # Only run during normal server startup, not during migrations or other commands
        import sys
        import os
        
        # Skip during migrations, collectstatic, and other management commands
        if any(cmd in sys.argv for cmd in ['migrate', 'makemigrations', 'collectstatic', 'test', 'check', 'shell']):
            return
        
        # Skip if we're running under certain conditions (only in development)
        if 'RUN_MAIN' not in os.environ and os.getenv('DEBUG', 'False').lower() == 'true':  # Skip during Django's auto-reload only in dev
            return
            
        # Import here to avoid circular imports
        try:
            from django.core.management import call_command
            import logging
            
            logger = logging.getLogger(__name__)
            
            # Use a delayed approach to avoid database access warnings
            def create_super_admins_delayed():
                try:
                    # Check if database is ready by trying a simple query
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    
                    # Try to access the database
                    User.objects.exists()
                    
                    # Database is ready, create super admins
                    call_command('create_super_admins', verbosity=0)
                    logger.info("Super admin users initialized successfully")
                    
                except Exception as e:
                    logger.debug(f"Super admin initialization skipped: {e}")
                    # Don't raise the exception to avoid breaking app startup
            
            # Schedule the creation for after app is fully ready
            import threading
            timer = threading.Timer(1.0, create_super_admins_delayed)
            timer.daemon = True
            timer.start()
            
            # Also try immediate creation for production
            try:
                create_super_admins_delayed()
            except Exception as e:
                logger.debug(f"Immediate super admin creation failed, will retry: {e}")
                
        except ImportError:
            # Management command not available yet
            pass
