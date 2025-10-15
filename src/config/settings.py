# src/config/settings.py
"""Configuration loader for separation of concerns. Loads .env for easy overrides in prod."""
import os
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]

load_dotenv()

class Settings:
    """App settings with type hints for IDE support."""
    gemini_api_key: str = os.getenv("GEMINI_API_KEY")
    max_chunk_size: int = int(os.getenv("MAX_CHUNK_SIZE", "1000"))
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    jwt_secret: str = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")


# Create settings instance outside the class
settings = Settings()
if not settings.gemini_api_key:
    raise ValueError("GEMINI_API_KEY is required")