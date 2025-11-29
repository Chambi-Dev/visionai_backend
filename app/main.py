"""
VisionAI Backend - Sistema Híbrido FastAPI + WebSocket
- FastAPI REST API: Estadísticas, dashboard, predicción de imágenes estáticas
- WebSocket: Stream de cámara en tiempo real
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json
import base64
from datetime import datetime
from typing import Set, Optional

from app.utils.logger import logger
from app.config.database import SessionLocal
from app.config.settings import settings
from app.services.prediction_service import prediction_service
from app.services.ml_service import ml_service
from app.services.auth_service import auth_service
from app.models.database_models import EmotionClass

# Importar rutas REST
from app.api.routes import predictions, health, dashboard, auth


# Crear aplicación FastAPI
app = FastAPI(
    title="VisionAI Backend",
    description="API REST + WebSocket para detección de emociones faciales en tiempo real",
    version="2.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas REST
app.include_router(
    predictions.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Predictions"]
)
app.include_router(
    health.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Health"]
)
app.include_router(
    dashboard.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Dashboard"]
)
app.include_router(
    auth.router,
    prefix=settings.API_V1_PREFIX + "/auth",
    tags=["Authentication"]
)

# Clientes WebSocket conectados
connected_clients: Set[WebSocket] = set()


# Dependencia para base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    """Endpoint raíz con información del servidor"""
    return {
        "service": "VisionAI Backend",
        "version": "2.0.0",
        "status": "running",
        "apis": {
            "rest": f"{settings.API_V1_PREFIX}/docs",
            "websocket": "ws://localhost:8000/ws"
        }
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket para predicción de emociones en tiempo real (cámara).
    
    Comandos disponibles:
    - predict: {"command": "predict", "image": "base64..."}
    - emotions: {"command": "emotions"}
    - model_info: {"command": "model_info"}
    - health: {"command": "health"}
    """
    await websocket.accept()
    connected_clients.add(websocket)
    
    # Crear sesión de BD para este WebSocket
    db = SessionLocal()
    
    try:
        # Enviar mensaje de bienvenida
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "message": "Conectado a VisionAI WebSocket - Stream de cámara",
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Cliente WebSocket conectado. Total: {len(connected_clients)}")
        
        # Loop de mensajes
        while True:
            # Recibir mensaje del cliente
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Obtener comando
            command = message.get("command", "").lower()
            
            # Enrutar según comando
            if command == "predict":
                await handle_predict(websocket, message, db)
            
            elif command == "emotions":
                await handle_get_emotions(websocket, db)
            
            elif command == "model_info":
                await handle_get_model_info(websocket)
            
            elif command == "health":
                await handle_health_check(websocket)
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Comando desconocido: {command}",
                    "available_commands": ["predict", "emotions", "model_info", "health"]
                })
    
    except WebSocketDisconnect:
        logger.info("Cliente WebSocket desconectado")
    except Exception as e:
        logger.error(f"Error en WebSocket: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "message": "Error interno del servidor"
            })
        except Exception:
            pass
    finally:
        connected_clients.discard(websocket)
        db.close()
        logger.info(f"Cliente desconectado. Total: {len(connected_clients)}")


async def handle_predict(websocket: WebSocket, message: dict, db: Session):
    """
    Maneja solicitudes de predicción de emociones.
    
    Args:
        websocket: Conexión WebSocket del cliente
        message: Mensaje con imagen en base64 y opcionalmente token
        db: Sesión de base de datos
    """
    try:
        # Validar estructura
        if "image" not in message:
            await websocket.send_json({
                "type": "error",
                "message": "Campo 'image' requerido"
            })
            return
        
        # Extraer usuario del token si está presente
        user_id = None
        if "token" in message:
            token = message["token"]
            payload = auth_service.verify_token(token)
            if payload:
                username = payload.get("sub")
                # Obtener user_id del username
                user = auth_service.get_user_by_username(db, username)
                if user:
                    user_id = user.user_id
                    logger.info(f"Predicción autenticada para usuario: {username} (ID: {user_id})")
                else:
                    logger.warning(f"Usuario no encontrado: {username}")
            else:
                logger.warning("Token inválido en predicción WebSocket")
        
        # Decodificar imagen base64
        try:
            image_base64 = message["image"]
            image_bytes = base64.b64decode(image_base64)
        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "message": f"Error al decodificar imagen: {str(e)}"
            })
            return
        
        # Validar que no esté vacía
        if len(image_bytes) == 0:
            await websocket.send_json({
                "type": "error",
                "message": "La imagen está vacía"
            })
            return
        
        # Obtener IP del cliente (FastAPI WebSocket)
        client_ip = websocket.client.host if websocket.client else None
        
        # Realizar predicción
        logger.info("Procesando predicción por WebSocket")
        result = await prediction_service.predict_emotion(
            image_bytes=image_bytes,
            db=db,
            source_ip=client_ip,
            user_id=user_id
        )
        
        # Enviar respuesta exitosa
        await websocket.send_json({
            "type": "prediction",
            "status": "success",
            "emotion_name": result.emotion_name,
            "confidence": result.confidence,
            "model_version_tag": result.model_version_tag,
            "processing_time_ms": result.processing_time_ms,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id
        })
        
    except ValueError as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    except Exception as e:
        logger.error(f"Error en predicción WebSocket: {e}", exc_info=True)
        await websocket.send_json({
            "type": "error",
            "message": "Error interno del servidor"
        })


async def handle_get_emotions(websocket: WebSocket, db: Session):
    """Obtener lista de emociones por WebSocket"""
    try:
        emotions = db.query(EmotionClass).all()
        
        if not emotions:
            emotions_data = [
                {"id": 1, "name": "angry", "description": "Enojo"},
                {"id": 2, "name": "disgust", "description": "Disgusto"},
                {"id": 3, "name": "fear", "description": "Miedo"},
                {"id": 4, "name": "happy", "description": "Felicidad"},
                {"id": 5, "name": "neutral", "description": "Neutral"},
                {"id": 6, "name": "sad", "description": "Tristeza"},
                {"id": 7, "name": "surprise", "description": "Sorpresa"}
            ]
        else:
            emotions_data = [
                {
                    "id": emotion.emotion_id,
                    "name": emotion.emotion_name,
                    "description": emotion.emotion_desc
                }
                for emotion in emotions
            ]
        
        await websocket.send_json({
            "type": "emotions",
            "status": "success",
            "emotions": emotions_data
        })
        
    except Exception as e:
        logger.error(f"Error al listar emociones: {e}")
        await websocket.send_json({
            "type": "error",
            "message": "Error al obtener lista de emociones"
        })


async def handle_get_model_info(websocket: WebSocket):
    """Obtener información del modelo por WebSocket"""
    try:
        info = ml_service.get_model_info()
        await websocket.send_json({
            "type": "model_info",
            "status": "success",
            "info": info
        })
    except Exception as e:
        logger.error(f"Error al obtener info del modelo: {e}")
        await websocket.send_json({
            "type": "error",
            "message": "Error al obtener información del modelo"
        })


async def handle_health_check(websocket: WebSocket):
    """Health check por WebSocket"""
    await websocket.send_json({
        "type": "health",
        "status": "healthy",
        "service": "VisionAI WebSocket",
        "timestamp": datetime.now().isoformat(),
        "clients_connected": len(connected_clients)
    })


if __name__ == "__main__":
    import uvicorn
    logger.info("=" * 60)
    logger.info("VisionAI Backend - Sistema Híbrido")
    logger.info("=" * 60)
    logger.info("REST API: http://localhost:8000/docs")
    logger.info("WebSocket: ws://localhost:8000/ws")
    logger.info("=" * 60)
    
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level="info"
    )
