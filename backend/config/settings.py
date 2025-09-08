from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"  # Will use gpt-5 when available
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    
    # Data Processing
    MAX_CSV_SIZE_MB: int = 1000
    SAMPLE_SIZE: int = 10000
    CHUNK_SIZE: int = 50000
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: list = ["http://localhost:3000"]
    
    # File Storage
    UPLOAD_DIR: str = "./data/uploads"
    CACHE_DIR: str = "./data/cache"
    
    # Agent Configuration
    MAX_ITERATIONS: int = 10
    STREAM_DELAY: float = 0.1
    
    class Config:
        env_file = ".env"

settings = Settings()