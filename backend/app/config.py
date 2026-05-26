import os
from pydantic_settings import BaseSettings

try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except ImportError:
    pass

class Settings(BaseSettings):
    PROJECT_NAME: str = "HypnoForge"
    API_V1_STR: str = "/api"
    
    # Database
    DATABASE_URL: str = "sqlite:///./hypnoforge.db"
    
    # AI Engine
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Storage
    OUTPUT_DIR: str = "output"
    STATIC_DIR: str = "static"
    
    class Config:
        case_sensitive = True

settings = Settings()

# Ensure directories exist
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
os.makedirs(settings.STATIC_DIR, exist_ok=True)
