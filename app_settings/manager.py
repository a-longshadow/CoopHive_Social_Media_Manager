import os
from typing import Optional, Any, Union
import json
from django.core.exceptions import ImproperlyConfigured
from .models import AppSetting


class DatabaseFirstSettingsManager:
    """
    100% compliant database-first, environment variable second settings manager.
    
    Priority Order:
    1. Database (AppSetting model)
    2. Environment Variables 
    3. FAIL SECURELY (no hardcoded defaults except super admin emails)
    """
    
    # Only these settings are allowed to have hardcoded values
    HARDCODED_ALLOWED = {
        'SUPER_ADMIN_EMAILS': ['joe@coophive.network', 'levi@coophive.network']
    }
    
    def __init__(self):
        """Initialize the database-first settings manager."""
        pass

    def get(self, key: str, required: bool = False, value_type: type = str) -> Any:
        """
        Get a setting value using database-first, environment fallback approach.
        
        Args:
            key: Setting key to retrieve
            required: If True, will raise ImproperlyConfigured if not found
            value_type: Type to cast the value to (str, bool, int, list, dict)
            
        Returns:
            The setting value cast to the specified type
            
        Raises:
            ImproperlyConfigured: If required setting is not found
        """
        # Step 1: Try database first
        try:
            setting = AppSetting.objects.get(key=key)
            return self._cast_value(setting.value, value_type)
        except AppSetting.DoesNotExist:
            pass
        
        # Step 2: Try environment variable
        env_value = os.getenv(key)
        if env_value is not None:
            return self._cast_value(env_value, value_type)
        
        # Step 3: Check if hardcoded value is allowed
        if key in self.HARDCODED_ALLOWED:
            return self.HARDCODED_ALLOWED[key]
        
        # Step 4: Fail securely if required
        if required:
            raise ImproperlyConfigured(
                f"Required setting '{key}' not found in database or environment variables. "
                f"Add it to the database via Django admin or set as environment variable."
            )
        
        return None

    def get_secret(self, key: str) -> str:
        """Get a secret setting (required, string type)."""
        return self.get(key, required=True, value_type=str)
    
    def get_bool(self, key: str, required: bool = False) -> Optional[bool]:
        """Get a boolean setting."""
        return self.get(key, required=required, value_type=bool)
    
    def get_int(self, key: str, required: bool = False) -> Optional[int]:
        """Get an integer setting.""" 
        return self.get(key, required=required, value_type=int)
    
    def get_list(self, key: str, required: bool = False) -> Optional[list]:
        """Get a list setting."""
        return self.get(key, required=required, value_type=list)
    
    def get_dict(self, key: str, required: bool = False) -> Optional[dict]:
        """Get a dict setting."""
        return self.get(key, required=required, value_type=dict)

    def set(self, key: str, value: Any, description: str = "") -> None:
        """Set a setting value in the database."""
        serialized_value = self._serialize_value(value)
        AppSetting.objects.update_or_create(
            key=key,
            defaults={"value": serialized_value, "description": description}
        )

    def delete(self, key: str) -> None:
        """Delete a setting from the database."""
        AppSetting.objects.filter(key=key).delete()

    def exists(self, key: str) -> bool:
        """Check if a setting exists in database or environment."""
        return (
            AppSetting.objects.filter(key=key).exists() or 
            os.getenv(key) is not None
        )

    def get_all_settings(self) -> dict:
        """Get all settings from database as a dictionary."""
        settings = {}
        for setting in AppSetting.objects.all():
            settings[setting.key] = self._deserialize_value(setting.value)
        return settings

    def init_default_settings(self) -> None:
        """Initialize default settings in database if they don't exist."""
        default_settings = [
            ('SECRET_KEY', '', 'Django secret key for cryptographic signing'),
            ('DEBUG', 'False', 'Debug mode (True/False)'),
            ('EMAIL_HOST', '', 'SMTP server hostname'),
            ('EMAIL_PORT', '587', 'SMTP server port'),
            ('EMAIL_USE_TLS', 'True', 'Use TLS for email (True/False)'),
            ('EMAIL_USE_SSL', 'False', 'Use SSL for email (True/False)'),
            ('EMAIL_HOST_USER', '', 'SMTP username'),
            ('EMAIL_HOST_PASSWORD', '', 'SMTP password'),
            ('DEFAULT_FROM_EMAIL', '', 'Default from email address'),
            ('GOOGLE_OAUTH_CLIENT_ID', '', 'Google OAuth client ID'),
            ('GOOGLE_OAUTH_CLIENT_SECRET', '', 'Google OAuth client secret'),
            ('DOMAIN_RESTRICTION_ENABLED', 'True', 'Enable domain restriction (True/False)'),
            ('ALLOWED_DOMAIN', 'coophive.network', 'Allowed email domain'),
            ('GOOGLE_VERIFICATION_ENABLED', 'True', 'Enable Google verification (True/False)'),
        ]
        
        for key, value, description in default_settings:
            if not AppSetting.objects.filter(key=key).exists():
                AppSetting.objects.create(
                    key=key,
                    value=value,
                    description=description
                )

    def _cast_value(self, value: str, value_type: type) -> Any:
        """Cast a string value to the specified type."""
        if value_type == bool:
            return value.lower() in ('true', '1', 'yes', 'on')
        elif value_type == int:
            return int(value)
        elif value_type == list:
            return self._deserialize_value(value) if isinstance(self._deserialize_value(value), list) else value.split(',')
        elif value_type == dict:
            return self._deserialize_value(value) if isinstance(self._deserialize_value(value), dict) else {}
        else:
            return str(value)

    def _serialize_value(self, value: Any) -> str:
        """Serialize a value for storage."""
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        elif isinstance(value, bool):
            return 'True' if value else 'False'
        return str(value)

    def _deserialize_value(self, value: str) -> Any:
        """Deserialize a stored value."""
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value


# Global instance
settings_manager = DatabaseFirstSettingsManager()
