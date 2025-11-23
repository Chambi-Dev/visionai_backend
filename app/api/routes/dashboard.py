"""
Endpoints para dashboard y estadísticas.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app.api.dependencies import get_db
from app.models.database_models import PredictionsLog, EmotionClass
from app.utils.logger import logger

router = APIRouter()


@router.get(
    "/dashboard/stats",
    summary="Estadísticas generales",
    description="Obtiene estadísticas generales del sistema"
)
async def get_statistics(db: Session = Depends(get_db)):
    """
    **Estadísticas generales del sistema.**
    
    Returns:
        - Total de predicciones
        - Emoción más común
        - Predicciones por emoción
        - Confianza promedio
    """
    try:
        # Total de predicciones
        total_predictions = db.query(
            func.count(PredictionsLog.predic_id)
        ).scalar()
        
        # Predicciones por emoción
        predictions_by_emotion = db.query(
            EmotionClass.emotion_name,
            func.count(PredictionsLog.predic_id).label('count')
        ).join(
            PredictionsLog,
            EmotionClass.emotion_id == PredictionsLog.emotion_id
        ).group_by(
            EmotionClass.emotion_name
        ).all()
        
        # Confianza promedio
        avg_confidence = db.query(
            func.avg(PredictionsLog.confidence)
        ).scalar() or 0.0
        
        # Emoción más común
        most_common = db.query(
            EmotionClass.emotion_name,
            func.count(PredictionsLog.predic_id).label('count')
        ).join(
            PredictionsLog,
            EmotionClass.emotion_id == PredictionsLog.emotion_id
        ).group_by(
            EmotionClass.emotion_name
        ).order_by(
            desc('count')
        ).first()
        
        return {
            "total_predictions": total_predictions or 0,
            "most_common_emotion": {
                "name": most_common[0] if most_common else None,
                "count": most_common[1] if most_common else 0
            },
            "average_confidence": float(avg_confidence),
            "predictions_by_emotion": {
                emotion: count
                for emotion, count in predictions_by_emotion
            }
        }
    except Exception as e:
        logger.error(f"Error en estadísticas: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener estadísticas"
        )


@router.get(
    "/dashboard/recent",
    summary="Predicciones recientes",
    description="Obtiene las últimas predicciones realizadas"
)
async def get_recent_predictions(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    **Predicciones recientes.**
    
    Args:
        limit: Número de predicciones a retornar (1-100)
    
    Returns:
        Lista de predicciones recientes
    """
    try:
        predictions = db.query(
            PredictionsLog.predic_id,
            PredictionsLog.timestamp,
            EmotionClass.emotion_name,
            PredictionsLog.confidence,
            PredictionsLog.source_ip
        ).join(
            EmotionClass,
            PredictionsLog.emotion_id == EmotionClass.emotion_id
        ).order_by(
            desc(PredictionsLog.timestamp)
        ).limit(limit).all()
        
        return {
            "count": len(predictions),
            "predictions": [
                {
                    "id": pred.predic_id,
                    "timestamp": pred.timestamp.isoformat(),
                    "emotion": pred.emotion_name,
                    "confidence": float(pred.confidence),
                    "source_ip": (
                        str(pred.source_ip) if pred.source_ip else None
                    )
                }
                for pred in predictions
            ]
        }
    except Exception as e:
        logger.error(f"Error al obtener predicciones recientes: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener predicciones recientes"
        )


@router.get(
    "/dashboard/timeline",
    summary="Timeline de predicciones",
    description="Predicciones agrupadas por día"
)
async def get_predictions_timeline(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """
    **Timeline de predicciones.**
    
    Args:
        days: Número de días atrás (1-30)
    
    Returns:
        Predicciones agrupadas por día
    """
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        predictions = db.query(
            func.date(PredictionsLog.timestamp).label('date'),
            func.count(PredictionsLog.predic_id).label('count')
        ).filter(
            PredictionsLog.timestamp >= start_date
        ).group_by(
            func.date(PredictionsLog.timestamp)
        ).order_by(
            'date'
        ).all()
        
        return {
            "period_days": days,
            "timeline": [
                {
                    "date": pred.date.isoformat(),
                    "count": pred.count
                }
                for pred in predictions
            ]
        }
    except Exception as e:
        logger.error(f"Error en timeline: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener timeline"
        )


@router.get(
    "/dashboard/emotion/{emotion_name}",
    summary="Estadísticas por emoción",
    description="Estadísticas detalladas de una emoción específica"
)
async def get_emotion_stats(
    emotion_name: str,
    db: Session = Depends(get_db)
):
    """
    **Estadísticas de una emoción.**
    
    Args:
        emotion_name: Nombre de la emoción
    
    Returns:
        Estadísticas detalladas de la emoción
    """
    try:
        # Verificar que existe la emoción
        emotion = db.query(EmotionClass).filter(
            EmotionClass.emotion_name == emotion_name
        ).first()
        
        if not emotion:
            raise HTTPException(
                status_code=404,
                detail=f"Emoción '{emotion_name}' no encontrada"
            )
        
        # Contar predicciones
        total_count = db.query(
            func.count(PredictionsLog.predic_id)
        ).filter(
            PredictionsLog.emotion_id == emotion.emotion_id
        ).scalar()
        
        # Confianza promedio
        avg_confidence = db.query(
            func.avg(PredictionsLog.confidence)
        ).filter(
            PredictionsLog.emotion_id == emotion.emotion_id
        ).scalar() or 0.0
        
        # Última predicción
        last_prediction = db.query(
            PredictionsLog.timestamp
        ).filter(
            PredictionsLog.emotion_id == emotion.emotion_id
        ).order_by(
            desc(PredictionsLog.timestamp)
        ).first()
        
        return {
            "emotion": {
                "id": emotion.emotion_id,
                "name": emotion.emotion_name,
                "description": emotion.emotion_desc
            },
            "statistics": {
                "total_predictions": total_count or 0,
                "average_confidence": float(avg_confidence),
                "last_prediction": (
                    last_prediction[0].isoformat()
                    if last_prediction else None
                )
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en stats de emoción: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener estadísticas de emoción"
        )
