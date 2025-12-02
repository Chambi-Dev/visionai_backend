"""
Endpoints de estadísticas para el sistema de predicción de emociones.
Incluye endpoints públicos y privados (requieren autenticación).
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.services.dashboard_service import dashboard_service
from app.models.schemas import (
    PublicGlobalStats,
    PublicEmotionDistributionResponse,
    PublicTrendsResponse,
    PublicHourlyActivityResponse,
    PublicEmotionTrendsResponse,
    PerformanceMetrics,
    UserPersonalStats,
    UserActivityResponse,
    UserEmotionStatsResponse,
    UserRecentPredictionsResponse
)
from app.utils.logger import logger

router = APIRouter()


# ==================== ENDPOINTS PÚBLICOS ====================

@router.get(
    "/stats/global",
    response_model=PublicGlobalStats,
    summary="📊 Estadísticas globales del sistema",
    description="Obtiene estadísticas generales públicas del sistema de predicción de emociones",
    tags=["Public Stats"]
)
async def get_global_statistics(db: Session = Depends(get_db)):
    """
    **Estadísticas globales del sistema** (público)
    
    Retorna:
    - Total de predicciones realizadas
    - Usuarios únicos que han usado el sistema
    - Sesiones activas hoy
    - Emoción más común detectada
    - Confianza promedio del modelo
    - Predicciones en la última hora
    - Predicciones realizadas hoy
    """
    try:
        stats = dashboard_service.get_global_stats(db)
        return stats
    except Exception as e:
        logger.error(f"Error getting global stats: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving global statistics")


@router.get(
    "/stats/emotions/distribution",
    response_model=PublicEmotionDistributionResponse,
    summary="🎭 Distribución de emociones",
    description="Obtiene la distribución de todas las emociones detectadas en el sistema",
    tags=["Public Stats"]
)
async def get_emotion_distribution(db: Session = Depends(get_db)):
    """
    **Distribución de emociones** (público)
    
    Retorna el conteo y porcentaje de cada emoción detectada en todas las predicciones.
    Útil para gráficos de torta/dona o barras.
    """
    try:
        distribution = dashboard_service.get_emotion_distribution(db)
        return distribution
    except Exception as e:
        logger.error(f"Error getting emotion distribution: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving emotion distribution")


@router.get(
    "/stats/trends",
    response_model=PublicTrendsResponse,
    summary="📈 Tendencias temporales",
    description="Obtiene tendencias de predicciones agrupadas por día",
    tags=["Public Stats"]
)
async def get_prediction_trends(
    days: int = Query(7, ge=1, le=90, description="Días hacia atrás"),
    db: Session = Depends(get_db)
):
    """
    **Tendencias de predicciones** (público)
    
    Retorna estadísticas diarias incluyendo:
    - Total de predicciones por día
    - Usuarios únicos por día
    - Confianza promedio por día
    
    Útil para gráficos de línea temporales.
    """
    try:
        trends = dashboard_service.get_trends(db, days)
        return trends
    except Exception as e:
        logger.error(f"Error getting trends: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving trends")


@router.get(
    "/stats/hourly-activity",
    response_model=PublicHourlyActivityResponse,
    summary="🕐 Actividad por hora",
    description="Obtiene la distribución de predicciones por hora del día",
    tags=["Public Stats"]
)
async def get_hourly_activity(db: Session = Depends(get_db)):
    """
    **Actividad por hora del día** (público)
    
    Retorna cuántas predicciones se realizan en cada hora del día (0-23).
    Incluye la hora pico de actividad.
    
    Útil para gráficos de barras de actividad horaria.
    """
    try:
        activity = dashboard_service.get_hourly_activity(db)
        return activity
    except Exception as e:
        logger.error(f"Error getting hourly activity: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving hourly activity")


@router.get(
    "/stats/emotions/trends",
    response_model=PublicEmotionTrendsResponse,
    summary="🎭📈 Tendencias por emoción",
    description="Obtiene cómo cada emoción ha variado en el tiempo",
    tags=["Public Stats"]
)
async def get_emotion_trends(
    days: int = Query(7, ge=1, le=90, description="Días hacia atrás"),
    db: Session = Depends(get_db)
):
    """
    **Tendencias por emoción específica** (público)
    
    Retorna el conteo diario de cada emoción en el período especificado.
    Útil para gráficos de líneas múltiples o áreas apiladas.
    """
    try:
        trends = dashboard_service.get_emotion_trends(db, days)
        return trends
    except Exception as e:
        logger.error(f"Error getting emotion trends: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving emotion trends")


@router.get(
    "/stats/performance",
    response_model=PerformanceMetrics,
    summary="⚡ Métricas de rendimiento",
    description="Obtiene métricas de rendimiento del modelo ML",
    tags=["Public Stats"]
)
async def get_performance_metrics(db: Session = Depends(get_db)):
    """
    **Métricas de rendimiento del sistema** (público)
    
    Retorna tiempos de procesamiento del modelo:
    - Tiempo promedio de procesamiento
    - Tiempo mínimo
    - Tiempo máximo
    - Total de predicciones analizadas
    """
    try:
        metrics = dashboard_service.get_performance_metrics(db)
        return metrics
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving performance metrics")


# ==================== ENDPOINTS PRIVADOS (REQUIEREN AUTENTICACIÓN) ====================

@router.get(
    "/stats/me",
    response_model=UserPersonalStats,
    summary="👤 Mis estadísticas personales",
    description="Obtiene las estadísticas personales del usuario autenticado",
    tags=["Private Stats (User)"]
)
async def get_my_stats(
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Estadísticas personales** (privado - requiere autenticación)
    
    Retorna estadísticas del usuario actual:
    - Total de predicciones realizadas
    - Predicciones hoy
    - Predicciones esta semana
    - Predicciones este mes
    - Emoción favorita
    - Confianza promedio
    - Fechas de primera y última predicción
    
    **Requiere:** Token de autenticación en header `Authorization: Bearer <token>`
    """
    try:
        stats = dashboard_service.get_user_personal_stats(db, current_user_id)
        return stats
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving user statistics")


@router.get(
    "/stats/me/activity",
    response_model=UserActivityResponse,
    summary="📅 Mi actividad diaria",
    description="Obtiene la actividad diaria del usuario autenticado",
    tags=["Private Stats (User)"]
)
async def get_my_activity(
    days: int = Query(30, ge=1, le=365, description="Días hacia atrás"),
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Actividad diaria del usuario** (privado - requiere autenticación)
    
    Retorna el historial de predicciones diarias del usuario.
    Útil para gráficos de calendario o líneas de actividad personal.
    
    **Requiere:** Token de autenticación en header `Authorization: Bearer <token>`
    """
    try:
        activity = dashboard_service.get_user_activity(db, current_user_id, days)
        return activity
    except Exception as e:
        logger.error(f"Error getting user activity: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving user activity")


@router.get(
    "/stats/me/emotions",
    response_model=UserEmotionStatsResponse,
    summary="🎭 Mis emociones detectadas",
    description="Obtiene el desglose de emociones del usuario autenticado",
    tags=["Private Stats (User)"]
)
async def get_my_emotions(
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Desglose de emociones del usuario** (privado - requiere autenticación)
    
    Retorna:
    - Conteo de cada emoción detectada para el usuario
    - Porcentaje de cada emoción
    - Confianza promedio por emoción
    - Emoción más frecuente
    
    Útil para gráficos personalizados de distribución de emociones del usuario.
    
    **Requiere:** Token de autenticación en header `Authorization: Bearer <token>`
    """
    try:
        emotions = dashboard_service.get_user_emotion_stats(db, current_user_id)
        return emotions
    except Exception as e:
        logger.error(f"Error getting user emotions: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving user emotions")


@router.get(
    "/stats/me/recent",
    response_model=UserRecentPredictionsResponse,
    summary="🕒 Mis predicciones recientes",
    description="Obtiene las predicciones más recientes del usuario autenticado",
    tags=["Private Stats (User)"]
)
async def get_my_recent_predictions(
    limit: int = Query(20, ge=1, le=100, description="Número de predicciones"),
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Predicciones recientes del usuario** (privado - requiere autenticación)
    
    Retorna las últimas predicciones realizadas por el usuario con:
    - ID de predicción
    - Emoción detectada
    - Confianza
    - Timestamp
    - Tiempo de procesamiento
    
    **Requiere:** Token de autenticación en header `Authorization: Bearer <token>`
    """
    try:
        recent = dashboard_service.get_user_recent_predictions(db, current_user_id, limit)
        return recent
    except Exception as e:
        logger.error(f"Error getting recent predictions: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving recent predictions")
