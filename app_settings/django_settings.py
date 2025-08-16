"""
Database-first settings helper for Django settings.py

This module provides the get_credential_setting function that implements:
1. Database first (AppSetting model)
2. Environment variable fallback  
3. Fail securely (no hardcoded defaults except super admin emails)
"""

import os
from typing import Any, Optional
from django.core.exceptions import ImproperlyConfigured


def get_credential_setting(key: str, required: bool = False, value_type: type = str, default: Any = None) -> Any:
    """
    Get a credential setting using database-first, environment fallback approach.
    
    This function is designed to be used in Django settings.py during app startup.
    It handles the case where the database might not be available yet.
    
    Args:
        key: Setting key to retrieve
        required: If True, will raise ImproperlyConfigured if not found
        value_type: Type to cast the value to (str, bool, int, list, dict)
        default: Default value (only used for non-security-critical settings)
        
    Returns:
        The setting value cast to the specified type
        
    Raises:
        ImproperlyConfigured: If required setting is not found
    """
    
    # Only these settings are allowed to have hardcoded values
    HARDCODED_ALLOWED = {
        'SUPER_ADMIN_EMAILS': ['joe@coophive.network', 'levi@coophive.network']
    }
    
    # Step 1: Try database first (if available)
    try:
        from app_settings.models import AppSetting
        try:
            setting = AppSetting.objects.get(key=key)
            return _cast_value(setting.value, value_type)
        except AppSetting.DoesNotExist:
            pass
    except Exception:
        # Database not available yet (during migrations, etc.)
        pass
    
    # Step 2: Try environment variable
    env_value = os.getenv(key)
    if env_value is not None:
        return _cast_value(env_value, value_type)
    
    # Step 3: Check if hardcoded value is allowed
    if key in HARDCODED_ALLOWED:
        return HARDCODED_ALLOWED[key]
    
    # Step 4: Use default if provided (for non-critical settings)
    if default is not None:
        return default
    
    # Step 5: Fail securely if required
    if required:
        raise ImproperlyConfigured(
            f"Required setting '{key}' not found in database or environment variables. "
            f"Add it to the database via Django admin or set as environment variable."
        )
    
    return None


def _cast_value(value: str, value_type: type) -> Any:
    """Cast a string value to the specified type."""
    if value_type == bool:
        return value.lower() in ('true', '1', 'yes', 'on')
    elif value_type == int:
        return int(value)
    elif value_type == list:
        try:
            import json
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else value.split(',')
        except:
            return value.split(',')
    elif value_type == dict:
        try:
            import json
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except:
            return {}
    else:
        return str(value)


# Convenience functions for common setting types
def get_secret_setting(key: str) -> str:
    """Get a required secret setting."""
    return get_credential_setting(key, required=True, value_type=str)


def get_bool_setting(key: str, default: bool = None) -> bool:
    """Get a boolean setting.""" 
    required = default is None
    return get_credential_setting(key, required=required, value_type=bool, default=default)


def get_int_setting(key: str, default: int = None) -> int:
    """Get an integer setting."""
    required = default is None
    return get_credential_setting(key, required=required, value_type=int, default=default)


def get_list_setting(key: str, default: list = None) -> list:
    """Get a list setting."""
    required = default is None
    return get_credential_setting(key, required=required, value_type=list, default=default)


def get_dict_setting(key: str, default: dict = None) -> dict:
    """Get a dict setting."""
    required = default is None
    return get_credential_setting(key, required=required, value_type=dict, default=default)
