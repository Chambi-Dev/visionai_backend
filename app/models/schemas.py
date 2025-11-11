from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
import datetime

# Schema para predicciones 
class PredictionResponse(BaseModel):
    """Respuesta de predicción de emoción"""
    emotion_name: str = Field(..., description="Nombre de la emoción detectada")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confianza (0-1)")
    model_version_tag: str = Field(..., description="Versión del modelo")
    processing_time_ms: int = Field(..., gt=0, description="Tiempo de procesamiento en ms")


# Schema para errores
class PredictionError(BaseModel):
    """Respuesta de error en predicción"""
    error: str
    detail: str


# Schema para el dashboard
class PredictionLogBase(BaseModel):
    emotion_id: int
    confidence: float
    model_id: int
    processing_time_ms: Optional[int] = None
    source_ip: Optional[str] = None
    timestamp: datetime.datetime


class PredictionEntry(PredictionLogBase):
    predic_id: int
    
    model_config = ConfigDict(from_attributes=True)


# Estadística simple para el conteo por emoción
class EmotionStat(BaseModel):
    emotion_name: str
    count: int


# JSON que devolverá el endpoint del dashboard
class DashboardStats(BaseModel):
    total_predictions: int
    active_model_tag: str
    predictions_per_emotion: List[EmotionStat]


# Schema para información de emoción
class EmotionInfo(BaseModel):
    """Información de una emoción"""
    emotion_id: int
    emotion_name: str
    emotion_desc: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)