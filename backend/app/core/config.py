from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    # App settings
    app_name: str = "Bug Bounty Platform"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API settings
    api_v1_prefix: str = "/api/v1"
    
    # Database settings
    database_url: str = "postgresql://user:password@localhost/bb_platform"
    
    # Redis settings
    redis_url: str = "redis://localhost:6379"
    
    # Security settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS settings
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://frontend:3000"
    ]
    
    # Module settings
    enabled_modules: List[str] = ["recon", "osint", "vulnscan", "reporting"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings() 