"""
Endpoints de health check y estado del servidor.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.services.ml_service import ml_service
from app.utils.logger import logger

router = APIRouter()


@router.get(
    "/health",
    summary="Health check del servidor",
    description="Verifica el estado del servidor, modelo ML y base de datos"
)
async def health_check(db: Session = Depends(get_db)):
    """
    **Health check completo del sistema.**
    
    Verifica:
    - Estado del servidor
    - Modelo ML cargado
    - Conexión a base de datos
    
    Returns:
        Estado general del sistema
    """
    try:
        # Verificar modelo ML
        model_info = ml_service.get_model_info()
        model_status = model_info.get("status", "unknown")
        
        # Verificar BD con query simple
        from app.models.database_models import EmotionClass
        db.query(EmotionClass).first()
        
        return {
            "status": "healthy",
            "service": "VisionAI Backend",
            "components": {
                "api": "running",
                "model": model_status,
                "database": "connected"
            }
        }
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return {
            "status": "unhealthy",
            "service": "VisionAI Backend",
            "error": str(e)
        }


@router.get(
    "/status",
    summary="Estado detallado del sistema",
    description="Información detallada sobre el estado y recursos del sistema"
)
async def system_status():
    """
    **Estado detallado del sistema.**
    
    Información sobre recursos y componentes.
    """
    try:
        model_info = ml_service.get_model_info()
        
        return {
            "status": "running",
            "version": "2.0.0",
            "apis": {
                "rest": "active",
                "websocket": "active"
            },
            "model": model_info
        }
    except Exception as e:
        logger.error(f"Error en status: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
