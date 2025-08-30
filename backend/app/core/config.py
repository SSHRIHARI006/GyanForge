import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Small settings container that reads from environment variables.

    This avoids the need for `pydantic-settings` during local development.
    """
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./gyanforge.db")
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # API Keys
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    tavily_api_key: Optional[str] = os.getenv("TAVILY_API_KEY")
    youtube_api_key: Optional[str] = os.getenv("YOUTUBE_API_KEY")
    pinecone_api_key: Optional[str] = os.getenv("PINECONE_API_KEY")
    pinecone_environment: Optional[str] = os.getenv("PINECONE_ENVIRONMENT")
    pinecone_index_name: Optional[str] = os.getenv("PINECONE_INDEX_NAME")
    
    # CORS Configuration
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Convert CORS_ORIGINS string to list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
