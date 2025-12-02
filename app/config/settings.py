from pydantic_settings import BaseSettings


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
    
    # Configuración de JWT/Autenticación
    SECRET_KEY: str = "visionai_secret_key_2025_change_this_in_production"
    REFRESH_SECRET_KEY: str = "visionai_refresh_secret_key_2025_change_this_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 30 minutos
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 días
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = 'utf-8'


# Instancia única de configuración
settings = Settings()
