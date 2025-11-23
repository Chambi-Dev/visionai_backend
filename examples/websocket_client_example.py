"""
Cliente WebSocket para VisionAI Backend.
Conecta y envía imágenes para predicción en tiempo real.
"""

import asyncio
import websockets
import json
import base64
from pathlib import Path


async def predict_emotion(
    image_path: str,
    server_url: str = "ws://localhost:8000"
):
    """
    Conecta al WebSocket y envía una imagen para predicción.
    
    Args:
        image_path: Ruta a la imagen a procesar
        server_url: URL del servidor WebSocket
    """
    try:
        # Leer imagen y convertir a base64
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Conectar al WebSocket
        async with websockets.connect(server_url) as websocket:
            print(f"✓ Conectado a {server_url}")
            
            # Recibir mensaje de bienvenida
            welcome = await websocket.recv()
            welcome_data = json.loads(welcome)
            print(f"← {welcome_data.get('message', 'Conectado')}")
            print()
            
            # Preparar mensaje de predicción
            message = {
                "command": "predict",
                "image": image_base64
            }
            
            # Enviar imagen
            print(f"→ Enviando imagen: {image_path}")
            await websocket.send(json.dumps(message))
            
            # Recibir respuesta
            response = await websocket.recv()
            result = json.loads(response)
            
            # Mostrar resultado
            print(f"← Respuesta recibida:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get("status") == "success":
                print(f"\n🎭 Emoción: {result['emotion_name']}")
                print(f"📊 Confianza: {result['confidence']:.2%}")
                print(f"⏱️  Tiempo: {result['processing_time_ms']}ms")
            else:
                print(f"\n❌ Error: {result.get('message')}")
    
    except FileNotFoundError:
        print(f"❌ Error: Imagen no encontrada '{image_path}'")
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ Error de WebSocket: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


async def get_emotions(server_url: str = "ws://localhost:8000"):
    """Obtiene la lista de emociones disponibles."""
    try:
        async with websockets.connect(server_url) as websocket:
            # Recibir bienvenida
            await websocket.recv()
            
            # Solicitar emociones
            await websocket.send(json.dumps({"command": "emotions"}))
            
            # Recibir respuesta
            response = await websocket.recv()
            result = json.loads(response)
            
            print("📋 Emociones disponibles:")
            for emotion in result.get("emotions", []):
                print(f"  • {emotion['name']}: {emotion['description']}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


async def get_model_info(server_url: str = "ws://localhost:8000"):
    """Obtiene información del modelo ML."""
    try:
        async with websockets.connect(server_url) as websocket:
            # Recibir bienvenida
            await websocket.recv()
            
            # Solicitar info
            await websocket.send(json.dumps({"command": "model_info"}))
            
            # Recibir respuesta
            response = await websocket.recv()
            result = json.loads(response)
            
            print("🤖 Información del modelo:")
            print(json.dumps(result.get("info", {}), indent=2))
    
    except Exception as e:
        print(f"❌ Error: {e}")


async def health_check(server_url: str = "ws://localhost:8000"):
    """Verifica el estado del servidor."""
    try:
        async with websockets.connect(server_url) as websocket:
            # Recibir bienvenida
            await websocket.recv()
            
            # Solicitar health
            await websocket.send(json.dumps({"command": "health"}))
            
            # Recibir respuesta
            response = await websocket.recv()
            result = json.loads(response)
            
            print(f"💚 Estado: {result.get('status')}")
            print(f"🔌 Clientes: {result.get('clients_connected')}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


async def continuous_prediction(
    image_folder: str,
    server_url: str = "ws://localhost:8000"
):
    """
    Procesa múltiples imágenes manteniendo conexión abierta.
    
    Args:
        image_folder: Carpeta con imágenes a procesar
        server_url: URL del servidor WebSocket
    """
    try:
        # Buscar imágenes
        folder = Path(image_folder)
        images = (
            list(folder.glob("*.jpg")) +
            list(folder.glob("*.png")) +
            list(folder.glob("*.jpeg"))
        )
        
        if not images:
            print(f"❌ No hay imágenes en '{image_folder}'")
            return
        
        # Conectar al WebSocket
        async with websockets.connect(server_url) as websocket:
            print(f"✓ Conectado a {server_url}")
            
            # Recibir bienvenida
            await websocket.recv()
            
            print(f"📁 Procesando {len(images)} imágenes...\n")
            
            for i, image_path in enumerate(images, 1):
                # Leer y codificar imagen
                with open(image_path, "rb") as image_file:
                    image_bytes = image_file.read()
                    image_b64 = base64.b64encode(image_bytes).decode()
                
                # Enviar mensaje
                message = {
                    "command": "predict",
                    "image": image_b64
                }
                
                print(f"[{i}/{len(images)}] {image_path.name}")
                await websocket.send(json.dumps(message))
                
                # Recibir respuesta
                response = await websocket.recv()
                result = json.loads(response)
                
                if result.get("status") == "success":
                    emotion = result['emotion_name']
                    conf = result['confidence']
                    print(f"  → {emotion} ({conf:.2%})")
                else:
                    print(f"  → Error: {result.get('message')}")
                
                print()
                
                # Pausa entre imágenes
                await asyncio.sleep(0.3)
            
            print("✓ Todas las imágenes procesadas")
    
    except FileNotFoundError:
        print(f"❌ Carpeta no encontrada '{image_folder}'")
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ Error de WebSocket: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Función principal con ejemplos de uso."""
    import sys
    
    print("=" * 60)
    print("🚀 Cliente WebSocket VisionAI")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python websocket_client_example.py <imagen.jpg>")
        print("  python websocket_client_example.py --folder <carpeta>")
        print("  python websocket_client_example.py --emotions")
        print("  python websocket_client_example.py --model-info")
        print("  python websocket_client_example.py --health")
        print()
        print("Ejemplos:")
        print("  python websocket_client_example.py rostro.jpg")
        print("  python websocket_client_example.py --folder ./imagenes/")
        print("  python websocket_client_example.py --emotions")
        return
    
    # Procesar argumentos
    if sys.argv[1] == "--folder":
        if len(sys.argv) < 3:
            print("❌ Error: Especifica la carpeta")
            return
        asyncio.run(continuous_prediction(sys.argv[2]))
    elif sys.argv[1] == "--emotions":
        asyncio.run(get_emotions())
    elif sys.argv[1] == "--model-info":
        asyncio.run(get_model_info())
    elif sys.argv[1] == "--health":
        asyncio.run(health_check())
    else:
        asyncio.run(predict_emotion(sys.argv[1]))


if __name__ == "__main__":
    main()

