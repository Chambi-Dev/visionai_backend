"""
Endpoints para predicción de emociones.
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional
from app.api.dependencies import get_db, get_current_user_optional
from app.services.prediction_service import prediction_service
from app.models.schemas import PredictionResponse, PredictionError
from app.utils.logger import logger

router = APIRouter()


@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Predecir emoción facial",
    description="Sube una imagen y obtén la emoción detectada con su nivel de confianza",
    responses={
        200: {
            "description": "Predicción exitosa",
            "content": {
                "application/json": {
                    "example": {
                        "emotion_name": "happy",
                        "confidence": 0.9234,
                        "model_version_tag": "v1.0.0",
                        "processing_time_ms": 145
                    }
                }
            }
        },
        400: {
            "description": "Imagen inválida",
            "model": PredictionError
        },
        500: {
            "description": "Error del servidor",
            "model": PredictionError
        }
    }
)
async def predict_emotion(
    request: Request,
    file: UploadFile = File(..., description="Imagen con expresión facial (JPEG, PNG, WEBP)"),
    db: Session = Depends(get_db),
    current_user: Optional[int] = Depends(get_current_user_optional)
):
    """
    **Predice la emoción en una imagen facial.**
    
    ## Parámetros:
    - **file**: Imagen con expresión facial
      - Formatos: JPEG, PNG, WEBP
      - Tamaño máximo: 5MB
      - Debe contener un rostro claramente visible
    
    ## Autenticación (Opcional):
    - Incluye header: `Authorization: Bearer <token>`
    - Si se incluye, la predicción se asociará al usuario
    
    ## Retorna:
    - **emotion_name**: Nombre de la emoción detectada
      - Posibles valores: angry, disgust, fear, happy, neutral, sad, surprise
    - **confidence**: Nivel de confianza [0-1]
    - **model_version_tag**: Versión del modelo utilizado
    - **processing_time_ms**: Tiempo de procesamiento en milisegundos
    
    ## Ejemplo de uso con curl:
    ```bash
    # Sin autenticación
    curl -X POST "http://localhost:8000/api/v1/predict" \\
         -H "Content-Type: multipart/form-data" \\
         -F "file=@rostro.jpg"
    
    # Con autenticación
    curl -X POST "http://localhost:8000/api/v1/predict" \\
         -H "Authorization: Bearer <token>" \\
         -H "Content-Type: multipart/form-data" \\
         -F "file=@rostro.jpg"
    ```
    """
    
    # Validar que se subió un archivo
    if not file:
        logger.warning("Request sin archivo")
        raise HTTPException(
            status_code=400,
            detail="No se proporcionó ningún archivo"
        )
    
    # Validar tipo de archivo
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
    if file.content_type not in allowed_types:
        logger.warning(f"Tipo de archivo no permitido: {file.content_type}")
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido: {file.content_type}. "
                   f"Usa JPEG, PNG o WEBP"
        )
    
    # Obtener IP del cliente
    client_ip = request.client.host if request.client else None
    
    try:
        # Leer bytes del archivo
        logger.info(f"Procesando archivo: {file.filename} ({file.content_type})")
        image_bytes = await file.read()
        
        # Validar que no esté vacío
        if len(image_bytes) == 0:
            raise HTTPException(
                status_code=400,
                detail="El archivo está vacío"
            )
        
        # Realizar predicción
        result = await prediction_service.predict_emotion(
            image_bytes=image_bytes,
            db=db,
            source_ip=client_ip,
            user_id=current_user
        )
        
        logger.info(
            f"Predicción REST exitosa: {result.emotion_name} "
            f"por usuario: {current_user or 'anónimo'}"
        )
        
        return result
        
    except ValueError as e:
        # Error de validación (imagen inválida, formato, etc.)
        logger.warning(f"Error de validación: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        # Error inesperado del servidor
        logger.error(f"Error en predicción: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor al procesar la imagen"
        )
    finally:
        # Cerrar el archivo
        await file.close()


@router.get(
    "/emotions",
    summary="Listar emociones disponibles",
    description="Obtiene la lista de todas las emociones que el modelo puede detectar"
)
async def list_emotions(db: Session = Depends(get_db)):
    """
    **Lista todas las emociones detectables.**
    
    Retorna la lista de emociones que el modelo puede identificar,
    junto con sus descripciones.
    """
    try:
        from app.models.database_models import EmotionClass
        
        emotions = db.query(EmotionClass).all()
        
        if not emotions:
            # Si no hay emociones en BD, devolver la lista hardcodeada
            return {
                "emotions": [
                    {"id": 1, "name": "angry", "description": "Enojo o ira"},
                    {"id": 2, "name": "disgust", "description": "Disgusto o asco"},
                    {"id": 3, "name": "fear", "description": "Miedo o temor"},
                    {"id": 4, "name": "happy", "description": "Felicidad o alegría"},
                    {"id": 5, "name": "neutral", "description": "Neutral o sin emoción aparente"},
                    {"id": 6, "name": "sad", "description": "Tristeza"},
                    {"id": 7, "name": "surprise", "description": "Sorpresa"}
                ]
            }
        
        return {
            "emotions": [
                {
                    "id": emotion.emotion_id,
                    "name": emotion.emotion_name,
                    "description": emotion.emotion_desc
                }
                for emotion in emotions
            ]
        }
        
    except Exception as e:
        logger.error(f"Error al listar emociones: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener lista de emociones"
        )


@router.get(
    "/model/info",
    summary="Información del modelo",
    description="Obtiene información sobre el modelo de ML actualmente cargado"
)
async def get_model_info():
    """
    **Información del modelo de ML.**
    
    Retorna detalles técnicos sobre el modelo cargado en memoria.
    """
    try:
        from app.services.ml_service import ml_service
        
        info = ml_service.get_model_info()
        return info
        
    except Exception as e:
        logger.error(f"Error al obtener info del modelo: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener información del modelo"
        )
