"""
Cliente WebSocket AUTENTICADO para VisionAI Backend.
Muestra cómo conectarse y hacer predicciones en tiempo real CON JWT.

⚠️ IMPORTANTE: Las predicciones ahora REQUIEREN autenticación JWT.
"""

import asyncio
import websockets
import json
import base64
import requests
from pathlib import Path


def login_and_get_token(username: str = "testuser", password: str = "testpass123"):
    """
    Inicia sesión en el backend y obtiene el access token.
    
    Returns:
        str: Access token JWT
    """
    print("🔐 Autenticando usuario...")
    base_url = "http://localhost:8000/api/v1"
    
    # Intentar registrar usuario (si no existe)
    try:
        register_response = requests.post(
            f"{base_url}/auth/register",
            json={"username": username, "password": password}
        )
        if register_response.status_code == 201:
            print(f"✅ Usuario '{username}' registrado exitosamente")
        elif register_response.status_code == 400:
            print(f"ℹ️  Usuario '{username}' ya existe, continuando...")
    except Exception as e:
        print(f"⚠️  Advertencia en registro: {e}")
    
    # Login para obtener token
    login_response = requests.post(
        f"{base_url}/auth/login",
        json={"username": username, "password": password}
    )
    
    if login_response.status_code == 200:
        data = login_response.json()
        access_token = data["access_token"]
        print(f"✅ Login exitoso! Access token obtenido (válido por {data.get('expires_in', 1800)}s)")
        return access_token
    else:
        raise Exception(f"❌ Login falló: {login_response.status_code} - {login_response.text}")


async def test_authenticated_websocket():
    """
    Ejemplo completo de uso de WebSocket con autenticación JWT.
    """
    print("=" * 70)
    print("🚀 VisionAI WebSocket Cliente - Con Autenticación JWT")
    print("=" * 70)
    print()
    
    # PASO 1: Obtener token JWT
    try:
        access_token = login_and_get_token()
    except Exception as e:
        print(f"\n❌ Error al autenticar: {e}")
        print("⚠️  Asegúrate de que el servidor esté corriendo en http://localhost:8000")
        return
    
    print()
    
    # PASO 2: Conectar a WebSocket
    uri = "ws://localhost:8000/ws"
    print(f"🔌 Conectando a WebSocket: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Conectado al WebSocket!")
            
            # Recibir mensaje de bienvenida
            welcome = await websocket.recv()
            welcome_data = json.loads(welcome)
            print(f"\n📩 Mensaje del servidor:")
            print(f"   {welcome_data.get('message', 'Conectado')}")
            if "auth_required" in welcome_data:
                print(f"   ⚠️  {welcome_data['auth_required']}")
            print()
            
            # PASO 3: Test 1 - Predicción SIN token (debe fallar)
            print("🧪 Test 1: Intentando predicción SIN token (debe fallar)...")
            message_no_auth = {
                "command": "predict",
                "image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="  # 1x1 pixel
            }
            await websocket.send(json.dumps(message_no_auth))
            response = await websocket.recv()
            response_data = json.loads(response)
            
            if response_data.get("type") == "error" and response_data.get("code") == "AUTH_REQUIRED":
                print("✅ Correctamente rechazado: autenticación requerida")
            else:
                print(f"⚠️  Respuesta inesperada: {response_data}")
            print()
            
            # PASO 4: Test 2 - Predicción CON token inválido (debe fallar)
            print("🧪 Test 2: Intentando predicción con token INVÁLIDO (debe fallar)...")
            message_bad_token = {
                "command": "predict",
                "image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                "token": "invalid_token_123"
            }
            await websocket.send(json.dumps(message_bad_token))
            response = await websocket.recv()
            response_data = json.loads(response)
            
            if response_data.get("type") == "error" and response_data.get("code") == "INVALID_TOKEN":
                print("✅ Correctamente rechazado: token inválido")
            else:
                print(f"⚠️  Respuesta inesperada: {response_data}")
            print()
            
            # PASO 5: Test 3 - Predicción CON token válido (debe funcionar)
            print("🧪 Test 3: Predicción con token VÁLIDO (debe funcionar)...")
            
            # Usar una imagen de prueba si existe
            test_image_path = Path("test_image.jpg")
            if test_image_path.exists():
                with open(test_image_path, "rb") as f:
                    image_bytes = f.read()
                    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                print(f"   📸 Usando imagen: {test_image_path}")
            else:
                # Imagen 1x1 pixel como fallback
                image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
                print("   📸 Usando imagen de prueba 1x1 pixel")
            
            message_with_auth = {
                "command": "predict",
                "image": image_base64,
                "token": access_token  # 🔑 TOKEN INCLUIDO
            }
            
            await websocket.send(json.dumps(message_with_auth))
            response = await websocket.recv()
            response_data = json.loads(response)
            
            if response_data.get("type") == "prediction" and response_data.get("status") == "success":
                print("✅ Predicción exitosa!")
                print(f"   🎭 Emoción detectada: {response_data.get('emotion_name')}")
                print(f"   📊 Confianza: {response_data.get('confidence'):.2f}%")
                print(f"   ⏱️  Tiempo de procesamiento: {response_data.get('processing_time_ms')}ms")
                print(f"   👤 User ID: {response_data.get('user_id')}")
            else:
                print(f"⚠️  Error en predicción: {response_data.get('message', 'Unknown error')}")
            print()
            
            # PASO 6: Test 4 - Otros comandos (no requieren auth)
            print("🧪 Test 4: Comandos públicos (health, model_info)...")
            
            # Health check
            await websocket.send(json.dumps({"command": "health"}))
            response = await websocket.recv()
            health_data = json.loads(response)
            if health_data.get("status") == "healthy":
                print(f"✅ Health: {health_data.get('status')} - {health_data.get('clients_connected')} clientes")
            
            # Model info
            await websocket.send(json.dumps({"command": "model_info"}))
            response = await websocket.recv()
            model_data = json.loads(response)
            if model_data.get("status") == "success":
                info = model_data.get("info", {})
                print(f"✅ Model: {info.get('version', 'N/A')} - {info.get('emotion_classes', []).__len__()} clases")
            
            print()
            print("=" * 70)
            print("✅ Todos los tests completados!")
            print("=" * 70)
            
    except websockets.exceptions.WebSocketException as e:
        print(f"\n❌ Error de WebSocket: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")


async def predict_single_image(image_path: str, username: str = "testuser", password: str = "testpass123"):
    """
    Función helper para hacer una sola predicción autenticada.
    
    Args:
        image_path: Ruta a la imagen a analizar
        username: Usuario para autenticación
        password: Contraseña para autenticación
    """
    # Autenticar
    access_token = login_and_get_token(username, password)
    
    # Leer imagen
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    # Conectar y predecir
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # Recibir welcome
        await websocket.recv()
        
        # Enviar predicción con token
        message = {
            "command": "predict",
            "image": image_base64,
            "token": access_token
        }
        await websocket.send(json.dumps(message))
        
        # Recibir respuesta
        response = await websocket.recv()
        return json.loads(response)


if __name__ == "__main__":
    print("\n")
    print("⚠️  Asegúrate de que el servidor esté corriendo:")
    print("   python -m uvicorn app.main:app --reload")
    print("\n")
    
    # Ejecutar tests
    asyncio.run(test_authenticated_websocket())
    
    print("\n")
    print("💡 TIP: Para predecir una imagen específica:")
    print("   result = asyncio.run(predict_single_image('path/to/image.jpg'))")
    print("   print(result)")
