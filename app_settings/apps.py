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
            from django.db.models.signals import post_migrate
            import logging
            
            logger = logging.getLogger(__name__)
            
            # Use post_migrate signal to avoid database access warnings
            def init_settings_signal(sender, **kwargs):
                try:
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
            
            # Connect to post_migrate signal
            post_migrate.connect(init_settings_signal, sender=self)
            
            # Also try immediate initialization for production (with delay)
            def init_settings_delayed():
                try:
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
            
            # Schedule the initialization for after app is fully ready
            import threading
            timer = threading.Timer(5.0, init_settings_delayed)  # Longer delay to avoid warnings
            timer.daemon = True
            timer.start()
                
        except ImportError:
            # Management command not available yet
            pass
