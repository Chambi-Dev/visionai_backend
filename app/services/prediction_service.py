"""
Servicio de predicción de emociones.
Orquesta el procesamiento de imágenes, predicción y almacenamiento en BD.
"""

import time
from typing import Optional
from sqlalchemy.orm import Session
from app.services.ml_service import ml_service
from app.utils.image_processing import preprocess_image
from app.models.database_models import PredictionsLog, EmotionClass, ModelVersion
from app.models.schemas import PredictionResponse
from app.utils.logger import logger


class PredictionService:
    """
    Servicio para manejar predicciones de emociones.
    """
    
    # Mapeo de nombres de emociones a IDs igual a la DB
    EMOTION_NAME_TO_ID = {
        'angry': 1,
        'disgust': 2,
        'fear': 3,
        'happy': 4,
        'neutral': 5,
        'sad': 6,
        'surprise': 7
    }
    
    async def predict_emotion(
        self,
        image_bytes: bytes,
        db: Session,
        source_ip: Optional[str] = None
    ) -> PredictionResponse:
        """
        Realiza una predicción completa de emoción.
        
        Flujo:
        1. Preprocesa la imagen
        2. Realiza la predicción con el modelo
        3. Guarda el resultado en la BD
        4. Retorna la respuesta formateada
        
        Args:
            image_bytes: Bytes de la imagen a predecir
            db: Sesión de base de datos
            source_ip: IP del cliente (opcional)
        
        Returns:
            PredictionResponse: Respuesta con emoción, confianza, etc.
        
        Raises:
            ValueError: Si hay error en procesamiento de imagen
            Exception: Si hay error en predicción o BD
        """
        start_time = time.time()
        
        try:
            # 1. Preprocesar imagen
            logger.info("Iniciando preprocesamiento de imagen")
            image_array = await preprocess_image(image_bytes)
            preprocess_time = time.time() - start_time
            logger.info(f"Preprocesamiento completado en {preprocess_time*1000:.2f}ms")
            
            # 2. Realizar predicción
            logger.info("Iniciando predicción")
            prediction_start = time.time()
            emotion_name, confidence, all_probs = ml_service.predict(image_array)
            prediction_time = time.time() - prediction_start
            logger.info(f"Predicción completada en {prediction_time*1000:.2f}ms")
            
            # 3. Calcular tiempo total
            total_time_ms = int((time.time() - start_time) * 1000)
            
            # 4. Obtener modelo activo
            model_version = self._get_active_model(db)
            if not model_version:
                logger.warning("No hay modelo activo en BD, usando configuración")
                model_version_tag = "v1.0.0"
                model_id = 1
            else:
                model_version_tag = model_version.model_version_tag
                model_id = model_version.model_id
            
            # 5. Obtener ID de emoción
            emotion_id = self.EMOTION_NAME_TO_ID.get(emotion_name)
            if not emotion_id:
                logger.error(f"Emoción desconocida: {emotion_name}")
                raise ValueError(f"Emoción no reconocida: {emotion_name}")
            
            # 6. Guardar en base de datos
            try:
                self._save_prediction(
                    db=db,
                    emotion_id=emotion_id,
                    confidence=confidence,
                    model_id=model_id,
                    processing_time_ms=total_time_ms,
                    source_ip=source_ip
                )
                logger.info("Predicción guardada en BD")
            except Exception as e:
                # No fallar la predicción si falla el guardado
                logger.error(f"Error al guardar predicción en BD: {e}")
            
            # 7. Construir respuesta
            response = PredictionResponse(
                emotion_name=emotion_name,
                confidence=round(confidence, 4),
                model_version_tag=model_version_tag,
                processing_time_ms=total_time_ms
            )
            
            logger.info(
                f"Predicción exitosa: {emotion_name} "
                f"({confidence:.2%}) en {total_time_ms}ms"
            )
            
            return response
            
        except ValueError as e:
            # Error de validación (imagen inválida, etc.)
            logger.error(f"Error de validación: {e}")
            raise
        except Exception as e:
            # Error inesperado
            logger.error(f"Error en predicción: {e}", exc_info=True)
            raise Exception(f"Error al procesar la predicción: {str(e)}")
    
    def _get_active_model(self, db: Session) -> Optional[ModelVersion]:
        """
        Obtiene el modelo activo de la base de datos.
        
        Args:
            db: Sesión de base de datos
        
        Returns:
            ModelVersion o None si no hay modelo activo
        """
        try:
            # Buscar modelo con estado '01' (activo)
            model = db.query(ModelVersion).filter(
                ModelVersion.model_status == '01'
            ).first()
            
            if not model:
                logger.warning("No se encontró modelo activo en BD")
            
            return model
        except Exception as e:
            logger.error(f"Error al consultar modelo activo: {e}")
            return None
    
    def _save_prediction(
        self,
        db: Session,
        emotion_id: int,
        confidence: float,
        model_id: int,
        processing_time_ms: int,
        source_ip: Optional[str] = None
    ) -> None:
        """
        Guarda una predicción en la base de datos.
        
        Args:
            db: Sesión de base de datos
            emotion_id: ID de la emoción predicha
            confidence: Confianza de la predicción
            model_id: ID del modelo usado
            processing_time_ms: Tiempo de procesamiento en ms
            source_ip: IP del cliente
        """
        try:
            prediction_log = PredictionsLog(
                emotion_id=emotion_id,
                confidence=confidence,
                model_id=model_id,
                processing_time_ms=processing_time_ms,
                source_ip=source_ip
            )
            
            db.add(prediction_log)
            db.commit()
            db.refresh(prediction_log)
            
            logger.debug(f"Predicción guardada con ID: {prediction_log.predic_id}")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error al guardar predicción: {e}")
            raise
    
    def get_emotion_by_name(self, db: Session, emotion_name: str) -> Optional[EmotionClass]:
        """
        Obtiene información de una emoción por nombre.
        
        Args:
            db: Sesión de base de datos
            emotion_name: Nombre de la emoción
        
        Returns:
            EmotionClass o None
        """
        try:
            emotion = db.query(EmotionClass).filter(
                EmotionClass.emotion_name == emotion_name
            ).first()
            return emotion
        except Exception as e:
            logger.error(f"Error al consultar emoción: {e}")
            return None


# Instancia global del servicio
prediction_service = PredictionService()
