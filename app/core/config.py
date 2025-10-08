from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database - Using SQLite for simplicity
    database_url: str = "sqlite:///./project_mgmt.db"
    
    # JWT - Change secret key in production using environment variable
    secret_key: str = "1234567890abcdef"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Google Gemini AI
    gemini_api_key: Optional[str] = None
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Heroku deployment
    port: int = 8000
    
    # Production settings
    allowed_hosts: list = ["*"]  # Configure properly for production
    
    class Config:
        env_file = ".env"
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    def get_database_url(self):
        """Get database URL - using SQLite for this deployment"""
        return self.database_url

settings = Settings()