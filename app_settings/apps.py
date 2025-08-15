from django.apps import AppConfig
from django.db import connection


class AppSettingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_settings'
    verbose_name = 'Application Settings'
    
    def ready(self):
        """Auto-initialize settings when the app is ready."""
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
            def init_settings_delayed():
                try:
                    # Check if database is ready by trying a simple query
                    from app_settings.models import AppSetting
                    
                    # Try to access the database
                    AppSetting.objects.exists()
                    
                    # Database is ready, initialize settings
                    call_command('init_settings', verbosity=0)
                    logger.info("Application settings initialized successfully")
                    
                    # Also setup Google OAuth if needed
                    try:
                        call_command('setup_google_oauth', verbosity=0)
                        logger.info("Google OAuth setup completed")
                    except Exception as e:
                        logger.debug(f"Google OAuth setup skipped: {e}")
                    
                except Exception as e:
                    logger.debug(f"Settings initialization skipped: {e}")
                    # Don't raise the exception to avoid breaking app startup
            
            # Schedule the initialization for after app is fully ready
            import threading
            timer = threading.Timer(2.0, init_settings_delayed)  # Slightly longer delay for settings
            timer.daemon = True
            timer.start()
            
            # Also try immediate initialization for production
            try:
                init_settings_delayed()
            except Exception as e:
                logger.debug(f"Immediate initialization failed, will retry: {e}")
                
        except ImportError:
            # Management command not available yet
            pass
