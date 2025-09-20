"""
Configuration management for Strands Agent
Handles API key management and other configuration settings
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for managing API keys and settings"""
    
    def __init__(self):
        self.google_api_key = self._get_env_var("GOOGLE_API_KEY")
        self.search_engine_id = self._get_env_var("GOOGLE_SEARCH_ENGINE_ID")
        
    def _get_env_var(self, var_name: str) -> Optional[str]:
        """Get environment variable with error handling"""
        value = os.getenv(var_name)
        if not value:
            print(f"Warning: {var_name} not found in environment variables")
        return value
    
    def is_configured(self) -> bool:
        """Check if all required configuration is present"""
        return bool(self.google_api_key and self.search_engine_id)
    
    def get_missing_config(self) -> list:
        """Return list of missing configuration items"""
        missing = []
        if not self.google_api_key:
            missing.append("GOOGLE_API_KEY")
        if not self.search_engine_id:
            missing.append("GOOGLE_SEARCH_ENGINE_ID")
        return missing

# Global config instance
config = Config()