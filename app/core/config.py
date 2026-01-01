from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Inventory Management API"
    environment: str = "development"

    database_url: str = "sqlite:///./inventory.db"
    redis_url: str = "redis://localhost:6379/0"
    
    model_config = SettingsConfigDict(env_file=".env")    
    
    log_level: str = "INFO"

    # Rate limiting
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60

    # Cache
    cache_ttl_seconds: int = 20

   

settings = Settings()