"""
Servidor WebSocket para VisionAI Backend.
Sistema de predicción de emociones faciales en tiempo real.
"""

import asyncio
import websockets
import json
import base64
from datetime import datetime
from typing import Set
from app.utils.logger import logger
from app.config.database import SessionLocal
from app.services.prediction_service import prediction_service
from app.services.ml_service import ml_service
from app.models.database_models import EmotionClass


# Configuración del servidor
HOST = "0.0.0.0"
PORT = 8000

# Clientes conectados
connected_clients: Set[websockets.WebSocketServerProtocol] = set()


async def handle_predict(websocket, message: dict, db):
    """
    Maneja solicitudes de predicción de emociones.
    
    Args:
        websocket: Conexión WebSocket del cliente
        message: Mensaje con imagen en base64
        db: Sesión de base de datos
    """
    try:
        # Validar estructura
        if "image" not in message:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "Campo 'image' requerido"
            }))
            return
        
        # Decodificar imagen base64
        try:
            image_base64 = message["image"]
            image_bytes = base64.b64decode(image_base64)
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Error al decodificar imagen: {str(e)}"
            }))
            return
        
        # Validar que no esté vacía
        if len(image_bytes) == 0:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "La imagen está vacía"
            }))
            return
        
        # Obtener IP del cliente
        client_ip = websocket.remote_address[0] if websocket.remote_address else None
        
        # Realizar predicción
        logger.info("Procesando predicción por WebSocket")
        result = await prediction_service.predict_emotion(
            image_bytes=image_bytes,
            db=db,
            source_ip=client_ip
        )
        
        # Enviar respuesta exitosa
        await websocket.send(json.dumps({
            "type": "prediction",
            "status": "success",
            "emotion_name": result.emotion_name,
            "confidence": result.confidence,
            "model_version_tag": result.model_version_tag,
            "processing_time_ms": result.processing_time_ms,
            "timestamp": datetime.now().isoformat()
        }))
        
    except ValueError as e:
        await websocket.send(json.dumps({
            "type": "error",
            "message": str(e)
        }))
    except Exception as e:
        logger.error(f"Error en predicción WebSocket: {e}", exc_info=True)
        await websocket.send(json.dumps({
            "type": "error",
            "message": "Error interno del servidor"
        }))


async def handle_get_emotions(websocket, db):
    """
    Maneja solicitudes para obtener lista de emociones.
    
    Args:
        websocket: Conexión WebSocket del cliente
        db: Sesión de base de datos
    """
    try:
        emotions = db.query(EmotionClass).all()
        
        if not emotions:
            # Lista por defecto si no hay en BD
            emotions_data = [
                {"id": 1, "name": "angry", "description": "Enojo o ira"},
                {"id": 2, "name": "disgust", "description": "Disgusto o asco"},
                {"id": 3, "name": "fear", "description": "Miedo o temor"},
                {"id": 4, "name": "happy", "description": "Felicidad o alegría"},
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
        
        await websocket.send(json.dumps({
            "type": "emotions",
            "status": "success",
            "emotions": emotions_data
        }))
        
    except Exception as e:
        logger.error(f"Error al listar emociones: {e}")
        await websocket.send(json.dumps({
            "type": "error",
            "message": "Error al obtener lista de emociones"
        }))


async def handle_get_model_info(websocket):
    """
    Maneja solicitudes de información del modelo.
    
    Args:
        websocket: Conexión WebSocket del cliente
    """
    try:
        info = ml_service.get_model_info()
        await websocket.send(json.dumps({
            "type": "model_info",
            "status": "success",
            "info": info
        }))
    except Exception as e:
        logger.error(f"Error al obtener info del modelo: {e}")
        await websocket.send(json.dumps({
            "type": "error",
            "message": "Error al obtener información del modelo"
        }))


async def handle_health_check(websocket):
    """
    Maneja solicitudes de health check.
    
    Args:
        websocket: Conexión WebSocket del cliente
    """
    await websocket.send(json.dumps({
        "type": "health",
        "status": "healthy",
        "service": "VisionAI Backend",
        "timestamp": datetime.now().isoformat(),
        "clients_connected": len(connected_clients)
    }))


async def handle_client(websocket, path):
    """
    Maneja la conexión de un cliente WebSocket.
    
    Args:
        websocket: Conexión WebSocket
        path: Ruta de la conexión
    """
    # Registrar cliente
    connected_clients.add(websocket)
    client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
    logger.info(f"✅ Cliente conectado: {client_info} (Total: {len(connected_clients)})")
    
    # Obtener sesión de base de datos
    db = SessionLocal()
    
    try:
        # Enviar mensaje de bienvenida
        await websocket.send(json.dumps({
            "type": "welcome",
            "message": "Bienvenido a VisionAI WebSocket Server",
            "version": "2.0.0",
            "commands": {
                "predict": "Predecir emoción (requiere campo 'image' base64)",
                "emotions": "Obtener lista de emociones",
                "model_info": "Información del modelo ML",
                "health": "Estado del servidor"
            }
        }))
        
        # Bucle principal de mensajes
        async for message in websocket:
            try:
                # Parsear JSON
                data = json.loads(message)
                command = data.get("command", "predict")
                
                # Enrutar comandos
                if command == "predict":
                    await handle_predict(websocket, data, db)
                elif command == "emotions":
                    await handle_get_emotions(websocket, db)
                elif command == "model_info":
                    await handle_get_model_info(websocket)
                elif command == "health":
                    await handle_health_check(websocket)
                else:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": f"Comando desconocido: {command}"
                    }))
                    
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "JSON inválido"
                }))
            except Exception as e:
                logger.error(f"Error procesando mensaje: {e}", exc_info=True)
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Error al procesar mensaje"
                }))
    
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"🔌 Cliente desconectado: {client_info}")
    except Exception as e:
        logger.error(f"❌ Error en conexión: {e}", exc_info=True)
    finally:
        # Limpiar recursos
        connected_clients.discard(websocket)
        db.close()
        logger.info(f"Cliente removido: {client_info} (Total: {len(connected_clients)})")


async def main():
    """Función principal del servidor."""
    logger.info("=" * 60)
    logger.info("🚀 VisionAI WebSocket Server")
    logger.info("=" * 60)
    
    # Cargar modelo ML
    try:
        logger.info("📦 Cargando modelo de Machine Learning...")
        model_info = ml_service.get_model_info()
        logger.info(f"✅ Modelo cargado: {model_info.get('status')}")
    except Exception as e:
        logger.error(f"❌ Error al cargar modelo: {e}")
        return
    
    # Iniciar servidor WebSocket
    logger.info(f"🌐 Iniciando servidor WebSocket en ws://{HOST}:{PORT}")
    
    async with websockets.serve(handle_client, HOST, PORT):
        logger.info("=" * 60)
        logger.info(f"✅ Servidor activo en ws://{HOST}:{PORT}")
        logger.info("📡 Esperando conexiones de clientes...")
        logger.info("=" * 60)
        logger.info("")
        logger.info("Comandos disponibles:")
        logger.info("  • predict      - Predecir emoción")
        logger.info("  • emotions     - Listar emociones")
        logger.info("  • model_info   - Info del modelo")
        logger.info("  • health       - Health check")
        logger.info("")
        logger.info("Presiona Ctrl+C para detener el servidor")
        logger.info("=" * 60)
        
        # Mantener servidor corriendo
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 60)
        logger.info("🛑 Servidor detenido por el usuario")
        logger.info("=" * 60)



