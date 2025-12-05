"""
Servicio de dashboard y estadísticas.
"""

from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, extract, and_
from app.models.database_models import PredictionsLog, EmotionClass, User
from app.utils.logger import logger


class DashboardService:
    """Servicio para estadísticas y dashboard"""
    
    # ==================== ESTADÍSTICAS PÚBLICAS ====================
    
    @staticmethod
    def get_global_stats(db: Session) -> Dict[str, Any]:
        """
        Obtiene estadísticas globales del sistema.
        
        Returns:
            Diccionario con estadísticas globales
        """
        try:
            now = datetime.now()
            today_start = datetime(now.year, now.month, now.day)
            hour_ago = now - timedelta(hours=1)
            
            # Total de predicciones
            total_predictions = db.query(
                func.count(PredictionsLog.predic_id)
            ).scalar() or 0
            
            # Usuarios únicos totales
            total_users = db.query(
                func.count(func.distinct(PredictionsLog.user_id))
            ).filter(
                PredictionsLog.user_id.isnot(None)
            ).scalar() or 0
            
            # Sesiones hoy (IPs únicas + usuarios únicos)
            sessions_today = db.query(
                func.count(func.distinct(PredictionsLog.source_ip))
            ).filter(
                PredictionsLog.timestamp >= today_start
            ).scalar() or 0
            
            # Emoción más común
            most_common = db.query(
                EmotionClass.emotion_name
            ).join(
                PredictionsLog
            ).group_by(
                EmotionClass.emotion_name
            ).order_by(
                desc(func.count(PredictionsLog.predic_id))
            ).first()
            
            # Confianza promedio
            avg_confidence = db.query(
                func.avg(PredictionsLog.confidence)
            ).scalar() or 0.0
            
            # Predicciones última hora
            predictions_last_hour = db.query(
                func.count(PredictionsLog.predic_id)
            ).filter(
                PredictionsLog.timestamp >= hour_ago
            ).scalar() or 0
            
            # Predicciones hoy
            predictions_today = db.query(
                func.count(PredictionsLog.predic_id)
            ).filter(
                PredictionsLog.timestamp >= today_start
            ).scalar() or 0
            
            return {
                "total_predictions": total_predictions,
                "total_unique_users": total_users,
                "total_sessions_today": sessions_today,
                "most_common_emotion": most_common[0] if most_common else "N/A",
                "avg_confidence": float(avg_confidence),
                "predictions_last_hour": predictions_last_hour,
                "predictions_today": predictions_today
            }
        except Exception as e:
            logger.error(f"Error getting global stats: {e}")
            raise
    
    @staticmethod
    def get_emotion_distribution(db: Session) -> Dict[str, Any]:
        """
        Obtiene la distribución de emociones detectadas.
        
        Returns:
            Diccionario con distribución de emociones
        """
        try:
            # Total de predicciones
            total = db.query(
                func.count(PredictionsLog.predic_id)
            ).scalar() or 0
            
            if total == 0:
                return {"total_predictions": 0, "emotions": []}
            
            # Conteo por emoción
            emotion_counts = db.query(
                EmotionClass.emotion_name,
                func.count(PredictionsLog.predic_id).label('count')
            ).join(
                PredictionsLog
            ).group_by(
                EmotionClass.emotion_name
            ).order_by(
                desc('count')
            ).all()
            
            emotions = [
                {
                    "emotion_name": emotion,
                    "count": count,
                    "percentage": round((count / total) * 100, 2)
                }
                for emotion, count in emotion_counts
            ]
            
            return {
                "total_predictions": total,
                "emotions": emotions
            }
        except Exception as e:
            logger.error(f"Error getting emotion distribution: {e}")
            raise
    
    @staticmethod
    def get_trends(db: Session, days: int = 7) -> Dict[str, Any]:
        """
        Obtiene tendencias diarias de predicciones.
        
        Args:
            days: Número de días hacia atrás
            
        Returns:
            Diccionario con tendencias diarias
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            daily_stats = db.query(
                func.date(PredictionsLog.timestamp).label('date'),
                func.count(PredictionsLog.predic_id).label('total_predictions'),
                func.count(func.distinct(PredictionsLog.user_id)).label('unique_users'),
                func.avg(PredictionsLog.confidence).label('avg_confidence')
            ).filter(
                PredictionsLog.timestamp >= start_date
            ).group_by(
                func.date(PredictionsLog.timestamp)
            ).order_by(
                'date'
            ).all()
            
            return {
                "period_days": days,
                "daily_stats": [
                    {
                        "date": stat.date.isoformat(),
                        "timestamp": datetime.combine(stat.date, datetime.min.time()),
                        "total_predictions": stat.total_predictions,
                        "unique_users": stat.unique_users or 0,
                        "avg_confidence": float(stat.avg_confidence or 0.0)
                    }
                    for stat in daily_stats
                ]
            }
        except Exception as e:
            logger.error(f"Error getting trends: {e}")
            raise
    
    @staticmethod
    def get_hourly_activity(db: Session) -> Dict[str, Any]:
        """
        Obtiene la distribución de actividad por hora del día.
        
        Returns:
            Diccionario con distribución horaria
        """
        try:
            hourly_data = db.query(
                extract('hour', PredictionsLog.timestamp).label('hour'),
                func.count(PredictionsLog.predic_id).label('count')
            ).group_by(
                'hour'
            ).order_by(
                'hour'
            ).all()
            
            hourly_distribution = [
                {
                    "hour": int(hour),
                    "hour_label": f"{int(hour):02d}:00",
                    "count": count
                }
                for hour, count in hourly_data
            ]
            
            # Encontrar hora pico
            peak = max(hourly_data, key=lambda x: x[1]) if hourly_data else None
            
            return {
                "hourly_distribution": hourly_distribution,
                "peak_hour": int(peak[0]) if peak else 0,
                "peak_hour_count": peak[1] if peak else 0
            }
        except Exception as e:
            logger.error(f"Error getting hourly activity: {e}")
            raise
    
    @staticmethod
    def get_emotion_trends(db: Session, days: int = 7) -> Dict[str, Any]:
        """
        Obtiene tendencias de emociones específicas en el tiempo.
        
        Args:
            days: Número de días hacia atrás
            
        Returns:
            Diccionario con tendencias por emoción
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            trends = db.query(
                func.date(PredictionsLog.timestamp).label('date'),
                EmotionClass.emotion_name,
                func.count(PredictionsLog.predic_id).label('count')
            ).join(
                EmotionClass
            ).filter(
                PredictionsLog.timestamp >= start_date
            ).group_by(
                func.date(PredictionsLog.timestamp),
                EmotionClass.emotion_name
            ).order_by(
                'date',
                EmotionClass.emotion_name
            ).all()
            
            return {
                "period_days": days,
                "trends": [
                    {
                        "date": trend.date.isoformat(),
                        "timestamp": datetime.combine(trend.date, datetime.min.time()),
                        "emotion_name": trend.emotion_name,
                        "count": trend.count
                    }
                    for trend in trends
                ]
            }
        except Exception as e:
            logger.error(f"Error getting emotion trends: {e}")
            raise
    
    @staticmethod
    def get_performance_metrics(db: Session) -> Dict[str, Any]:
        """
        Obtiene métricas de rendimiento del sistema.
        
        Returns:
            Diccionario con métricas de rendimiento
        """
        try:
            metrics = db.query(
                func.avg(PredictionsLog.processing_time_ms).label('avg_time'),
                func.min(PredictionsLog.processing_time_ms).label('min_time'),
                func.max(PredictionsLog.processing_time_ms).label('max_time'),
                func.count(PredictionsLog.predic_id).label('total')
            ).filter(
                PredictionsLog.processing_time_ms.isnot(None)
            ).first()
            
            if not metrics or metrics.total == 0:
                return {
                    "avg_processing_time_ms": 0.0,
                    "min_processing_time_ms": 0,
                    "max_processing_time_ms": 0,
                    "total_predictions_analyzed": 0
                }
            
            return {
                "avg_processing_time_ms": float(metrics.avg_time or 0.0),
                "min_processing_time_ms": metrics.min_time or 0,
                "max_processing_time_ms": metrics.max_time or 0,
                "total_predictions_analyzed": metrics.total
            }
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            raise
    
    # ==================== ESTADÍSTICAS PRIVADAS (USUARIO) ====================
    
    @staticmethod
    def get_user_personal_stats(db: Session, user_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas personales de un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Diccionario con estadísticas personales
        """
        try:
            # Obtener información del usuario
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            now = datetime.now()
            today_start = datetime(now.year, now.month, now.day)
            week_start = today_start - timedelta(days=now.weekday())
            month_start = datetime(now.year, now.month, 1)
            
            # Total de predicciones del usuario
            total_predictions = db.query(
                func.count(PredictionsLog.predic_id)
            ).filter(
                PredictionsLog.user_id == user_id
            ).scalar() or 0
            
            # Predicciones hoy
            predictions_today = db.query(
                func.count(PredictionsLog.predic_id)
            ).filter(
                and_(
                    PredictionsLog.user_id == user_id,
                    PredictionsLog.timestamp >= today_start
                )
            ).scalar() or 0
            
            # Predicciones esta semana
            predictions_week = db.query(
                func.count(PredictionsLog.predic_id)
            ).filter(
                and_(
                    PredictionsLog.user_id == user_id,
                    PredictionsLog.timestamp >= week_start
                )
            ).scalar() or 0
            
            # Predicciones este mes
            predictions_month = db.query(
                func.count(PredictionsLog.predic_id)
            ).filter(
                and_(
                    PredictionsLog.user_id == user_id,
                    PredictionsLog.timestamp >= month_start
                )
            ).scalar() or 0
            
            # Emoción favorita
            favorite = db.query(
                EmotionClass.emotion_name
            ).join(
                PredictionsLog
            ).filter(
                PredictionsLog.user_id == user_id
            ).group_by(
                EmotionClass.emotion_name
            ).order_by(
                desc(func.count(PredictionsLog.predic_id))
            ).first()
            
            # Confianza promedio
            avg_confidence = db.query(
                func.avg(PredictionsLog.confidence)
            ).filter(
                PredictionsLog.user_id == user_id
            ).scalar() or 0.0
            
            # Primera y última predicción
            first_prediction = db.query(
                func.min(PredictionsLog.timestamp)
            ).filter(
                PredictionsLog.user_id == user_id
            ).scalar()
            
            last_prediction = db.query(
                func.max(PredictionsLog.timestamp)
            ).filter(
                PredictionsLog.user_id == user_id
            ).scalar()
            
            return {
                "user_id": user_id,
                "username": user.username,
                "total_predictions": total_predictions,
                "predictions_today": predictions_today,
                "predictions_this_week": predictions_week,
                "predictions_this_month": predictions_month,
                "favorite_emotion": favorite[0] if favorite else None,
                "avg_confidence": float(avg_confidence),
                "first_prediction_date": first_prediction if first_prediction else None,
                "last_prediction_date": last_prediction if last_prediction else None
            }
        except Exception as e:
            logger.error(f"Error getting user personal stats: {e}")
            raise
    
    @staticmethod
    def get_user_activity(db: Session, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Obtiene la actividad diaria del usuario.
        
        Args:
            user_id: ID del usuario
            days: Número de días hacia atrás
            
        Returns:
            Diccionario con actividad diaria
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            daily_activity = db.query(
                func.date(PredictionsLog.timestamp).label('date'),
                func.count(PredictionsLog.predic_id).label('count')
            ).filter(
                and_(
                    PredictionsLog.user_id == user_id,
                    PredictionsLog.timestamp >= start_date
                )
            ).group_by(
                func.date(PredictionsLog.timestamp)
            ).order_by(
                'date'
            ).all()
            
            total = sum(activity[1] for activity in daily_activity)
            
            return {
                "period_days": days,
                "daily_activity": [
                    {
                        "date": activity[0].isoformat(),
                        "timestamp": datetime.combine(activity[0], datetime.min.time()),
                        "prediction_count": activity[1]
                    }
                    for activity in daily_activity
                ],
                "total_predictions": total
            }
        except Exception as e:
            logger.error(f"Error getting user activity: {e}")
            raise
    
    @staticmethod
    def get_user_emotion_stats(db: Session, user_id: int) -> Dict[str, Any]:
        """
        Obtiene el desglose de emociones del usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Diccionario con estadísticas de emociones
        """
        try:
            # Total de predicciones del usuario
            total = db.query(
                func.count(PredictionsLog.predic_id)
            ).filter(
                PredictionsLog.user_id == user_id
            ).scalar() or 0
            
            if total == 0:
                return {
                    "total_predictions": 0,
                    "emotions": [],
                    "most_frequent_emotion": None
                }
            
            # Desglose por emoción
            emotion_breakdown = db.query(
                EmotionClass.emotion_name,
                func.count(PredictionsLog.predic_id).label('count'),
                func.avg(PredictionsLog.confidence).label('avg_confidence')
            ).join(
                PredictionsLog
            ).filter(
                PredictionsLog.user_id == user_id
            ).group_by(
                EmotionClass.emotion_name
            ).order_by(
                desc('count')
            ).all()
            
            emotions = [
                {
                    "emotion_name": emotion,
                    "count": count,
                    "percentage": round((count / total) * 100, 2),
                    "avg_confidence": float(avg_conf or 0.0)
                }
                for emotion, count, avg_conf in emotion_breakdown
            ]
            
            most_frequent = emotions[0]["emotion_name"] if emotions else None
            
            return {
                "total_predictions": total,
                "emotions": emotions,
                "most_frequent_emotion": most_frequent
            }
        except Exception as e:
            logger.error(f"Error getting user emotion stats: {e}")
            raise
    
    @staticmethod
    def get_user_recent_predictions(
        db: Session,
        user_id: int,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Obtiene las predicciones recientes del usuario.
        
        Args:
            user_id: ID del usuario
            limit: Número máximo de predicciones a retornar
            
        Returns:
            Diccionario con predicciones recientes
        """
        try:
            recent = db.query(
                PredictionsLog.predic_id,
                EmotionClass.emotion_name,
                PredictionsLog.confidence,
                PredictionsLog.timestamp,
                PredictionsLog.processing_time_ms
            ).join(
                EmotionClass
            ).filter(
                PredictionsLog.user_id == user_id
            ).order_by(
                desc(PredictionsLog.timestamp)
            ).limit(limit).all()
            
            return {
                "count": len(recent),
                "predictions": [
                    {
                        "predic_id": pred.predic_id,
                        "emotion_name": pred.emotion_name,
                        "confidence": float(pred.confidence),
                        "timestamp": pred.timestamp,
                        "processing_time_ms": pred.processing_time_ms
                    }
                    for pred in recent
                ]
            }
        except Exception as e:
            logger.error(f"Error getting user recent predictions: {e}")
            raise


dashboard_service = DashboardService()