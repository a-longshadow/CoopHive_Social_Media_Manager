"""
Custom email backend that loads settings dynamically from database-first approach.

This backend wraps Django's SMTP backend but loads configuration from:
1. Database (via app_settings) - PRIMARY
2. Environment variables - FALLBACK  
3. Django settings - DEFAULT

This avoids circular import issues during Django startup while providing
database-first configuration at runtime.
"""

from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend
from django.conf import settings


class DatabaseFirstEmailBackend(SMTPEmailBackend):
    """Email backend that loads settings from database first, then environment."""
    
    def __init__(self, host=None, port=None, username=None, password=None,
                 use_tls=None, fail_silently=False, use_ssl=None, timeout=None,
                 ssl_keyfile=None, ssl_certfile=None, **kwargs):
        
        # Load database-first settings at runtime (avoiding circular imports)
        try:
            from user_account_manager.utils import get_email_settings
            email_config = get_email_settings()
            
            # Use database-first values, but allow explicit overrides
            host = host or email_config['EMAIL_HOST']
            port = port or email_config['EMAIL_PORT']
            username = username or email_config['EMAIL_HOST_USER']
            password = password or email_config['EMAIL_HOST_PASSWORD']
            use_tls = use_tls if use_tls is not None else email_config.get('EMAIL_USE_TLS', False)
            use_ssl = use_ssl if use_ssl is not None else email_config.get('EMAIL_USE_SSL', True)
            
            # Ensure TLS and SSL are not both enabled
            if use_ssl and use_tls:
                use_tls = False
            
        except (ImportError, Exception):
            # Fallback to Django settings if database loading fails
            host = host or getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com')
            port = port or getattr(settings, 'EMAIL_PORT', 587)
            username = username or getattr(settings, 'EMAIL_HOST_USER', '')
            password = password or getattr(settings, 'EMAIL_HOST_PASSWORD', '')
            use_tls = use_tls if use_tls is not None else getattr(settings, 'EMAIL_USE_TLS', True)
        
        # Initialize parent with our dynamically loaded settings
        super().__init__(
            host=host,
            port=port,
            username=username,
            password=password,
            use_tls=use_tls,
            fail_silently=fail_silently,
            use_ssl=use_ssl,
            timeout=timeout,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            **kwargs
        )
