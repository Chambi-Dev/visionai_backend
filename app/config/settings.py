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
    
    # Configuración de base de datos
    DATABASE_URL: Optional[str] = None
    
    # Configuración del modelo ML
    MODEL_PATH: str = "ml_models/modelo_emociones.keras"
    
    # Configuración de CORS
    ALLOWED_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia única de configuración
settings = Settings()
