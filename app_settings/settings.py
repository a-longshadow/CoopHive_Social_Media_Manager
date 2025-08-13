from django.core.exceptions import ObjectDoesNotExist
from .models import AppSetting

class SettingsManager:
    """Manager class for accessing application settings from the database."""
    
    @staticmethod
    def get(key: str) -> str:
        """Get a setting value from the database.
        
        Args:
            key: The setting key to retrieve
            
        Returns:
            The setting value as a string
            
        Raises:
            KeyError: If the setting does not exist in the database
        """
        try:
            setting = AppSetting.objects.get(key=key)
            return setting.value
        except ObjectDoesNotExist:
            raise KeyError(f"Setting '{key}' does not exist in database")
