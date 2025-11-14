from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Configuración general
    APP_NAME: str = "VisionAI Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Configuración de la API
    API_V1_PREFIX: str = "/api/v1"
    
    # Configuración de base de datos (lee de .env, por defecto usa 123)
    DATABASE_URL: str = (
        "postgresql+psycopg2://postgres:123@localhost:5432/visionai_db"
    )
    
    # Configuración del modelo ML
    MODEL_PATH: str = "ml_models/modelo_emociones.h5"
    
    # Configuración de CORS
    ALLOWED_ORIGINS: list = ["*"]
    
    # Configuración del servidor WebSocket
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = 'utf-8'


# Instancia única de configuración
settings = Settings()
