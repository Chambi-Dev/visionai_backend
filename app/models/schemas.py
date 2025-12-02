from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
import datetime

# ============= SCHEMAS DE PREDICCIONES =============

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
    user_id: Optional[int] = None
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


# ============= SCHEMAS DE AUTENTICACIÓN =============

class UserCreate(BaseModel):
    """Schema para crear un nuevo usuario"""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Nombre de usuario único"
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=72,
        description="Contraseña (6-72 caracteres)"
    )


class UserLogin(BaseModel):
    """Schema para login de usuario"""
    username: str = Field(..., description="Nombre de usuario")
    password: str = Field(..., description="Contraseña")


class UserResponse(BaseModel):
    """Schema de respuesta de usuario (sin contraseña)"""
    user_id: int
    username: str
    is_active: bool
    created_at: datetime.datetime
    
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Schema para token de autenticación (access token en body, refresh en cookie)"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(
        default=1800,
        description="Tiempo de expiración del access token en segundos"
    )


class RefreshTokenRequest(BaseModel):
    """Schema para solicitud de refresh token"""
    refresh_token: str = Field(..., description="Refresh token para obtener nuevo access token")


class TokenData(BaseModel):
    """Datos decodificados del token"""
    username: Optional[str] = None


# ============= SCHEMAS DE ESTADÍSTICAS AVANZADAS =============

class EmotionDistribution(BaseModel):
    """Distribución de emociones"""
    emotion_name: str
    count: int
    percentage: float = Field(..., ge=0.0, le=100.0)


class HourlyDistribution(BaseModel):
    """Distribución por hora del día"""
    hour: int = Field(..., ge=0, le=23)
    count: int


class DailyStats(BaseModel):
    """Estadísticas diarias"""
    date: str
    total_predictions: int
    unique_users: int
    avg_confidence: float


class EmotionTrend(BaseModel):
    """Tendencia de emoción en el tiempo"""
    date: str
    emotion_name: str
    count: int


class PublicGlobalStats(BaseModel):
    """Estadísticas globales públicas del sistema"""
    total_predictions: int
    total_unique_users: int
    total_sessions_today: int
    most_common_emotion: str
    avg_confidence: float
    predictions_last_hour: int
    predictions_today: int


class PublicEmotionDistributionResponse(BaseModel):
    """Respuesta de distribución de emociones"""
    total_predictions: int
    emotions: List[EmotionDistribution]


class PublicTrendsResponse(BaseModel):
    """Respuesta de tendencias públicas"""
    period_days: int
    daily_stats: List[DailyStats]


class PublicHourlyActivityResponse(BaseModel):
    """Respuesta de actividad por hora"""
    hourly_distribution: List[HourlyDistribution]
    peak_hour: int
    peak_hour_count: int


class PublicEmotionTrendsResponse(BaseModel):
    """Respuesta de tendencias por emoción"""
    period_days: int
    trends: List[EmotionTrend]


class UserPersonalStats(BaseModel):
    """Estadísticas personales del usuario"""
    user_id: int
    username: str
    total_predictions: int
    predictions_today: int
    predictions_this_week: int
    predictions_this_month: int
    favorite_emotion: Optional[str] = None
    avg_confidence: float
    first_prediction_date: Optional[str] = None
    last_prediction_date: Optional[str] = None


class UserDailyActivity(BaseModel):
    """Actividad diaria del usuario"""
    date: str
    prediction_count: int


class UserEmotionBreakdown(BaseModel):
    """Desglose de emociones del usuario"""
    emotion_name: str
    count: int
    percentage: float
    avg_confidence: float


class UserActivityResponse(BaseModel):
    """Respuesta de actividad del usuario"""
    period_days: int
    daily_activity: List[UserDailyActivity]
    total_predictions: int


class UserEmotionStatsResponse(BaseModel):
    """Respuesta de estadísticas de emociones del usuario"""
    total_predictions: int
    emotions: List[UserEmotionBreakdown]
    most_frequent_emotion: Optional[str] = None


class UserRecentPrediction(BaseModel):
    """Predicción reciente del usuario"""
    predic_id: int
    emotion_name: str
    confidence: float
    timestamp: str
    processing_time_ms: Optional[int] = None


class UserRecentPredictionsResponse(BaseModel):
    """Respuesta de predicciones recientes del usuario"""
    count: int
    predictions: List[UserRecentPrediction]


class PerformanceMetrics(BaseModel):
    """Métricas de rendimiento del sistema"""
    avg_processing_time_ms: float
    min_processing_time_ms: int
    max_processing_time_ms: int
    total_predictions_analyzed: int
