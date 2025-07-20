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
    
    # Database URL for LangChain (constructed from Supabase settings)
    @property
    def database_url(self) -> str:
        """Construct PostgreSQL URL from Supabase URL - LEGACY, kept for compatibility"""
        return self.supabase_url.replace('https://', 'postgresql://postgres:').replace('.supabase.co', '.supabase.co:5432') + '/postgres'
    
    @property
    def langchain_database_url(self) -> str:
        """Dedicated PostgreSQL URL for LangChain chat functionality"""
        # First try the explicit DATABASE_URL from environment
        import os
        explicit_url = os.getenv("DATABASE_URL")
        if explicit_url:
            return explicit_url
        
        # Fallback: construct from Supabase settings with proper format
        # Extract project reference from Supabase URL
        supabase_host = self.supabase_url.replace("https://", "").replace("http://", "")
        project_ref = supabase_host.split('.')[0]
        
        # Security: No fallback with hardcoded credentials - require DATABASE_URL
        raise ValueError("DATABASE_URL environment variable is required for LangChain database connection")
    
    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()