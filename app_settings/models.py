from django.db import models
from typing import Optional, Any
import json

class AppSetting(models.Model):
    """Model to store application settings in the database."""
    key = models.CharField(max_length=100, unique=True, db_index=True)
    value = models.TextField(blank=True)
    description = models.TextField(blank=True, help_text="What this setting does")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Application Setting"
        verbose_name_plural = "Application Settings"
        ordering = ["key"]

    def __str__(self):
        return self.key


class SettingsManager:
    """Class to manage application settings stored in the database."""
    
    def __init__(self, fallback_to_env: bool = False):
        """
        Initialize settings manager.
        
        Args:
            fallback_to_env: Whether to try getting values from environment variables
                          if not found in database
        """
        self.fallback_to_env = fallback_to_env

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        try:
            setting = AppSetting.objects.get(key=key)
            return self._deserialize_value(setting.value)
        except AppSetting.DoesNotExist:
            return default

    def set(self, key: str, value: Any, description: str = "") -> None:
        """Set a setting value."""
        serialized_value = self._serialize_value(value)
        AppSetting.objects.update_or_create(
            key=key,
            defaults={"value": serialized_value, "description": description}
        )

    def delete(self, key: str) -> None:
        """Delete a setting."""
        AppSetting.objects.filter(key=key).delete()

    def exists(self, key: str) -> bool:
        """Check if a setting exists."""
        return AppSetting.objects.filter(key=key).exists()

    def _serialize_value(self, value: Any) -> str:
        """Serialize a value for storage."""
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        return str(value)

    def _deserialize_value(self, value: str) -> Any:
        """Deserialize a stored value."""
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
