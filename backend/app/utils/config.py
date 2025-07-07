from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
    api_port: int = 8000
    api_host: str = "0.0.0.0"
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: str = ".xlsx"
    
    # Email settings
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    email_use_tls: bool = True
    
    # OpenAI settings
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.1
    openai_max_tokens: int = 1000
    
    # Redis settings
    redis_url: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()