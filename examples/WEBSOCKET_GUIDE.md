# Guía de Uso - VisionAI WebSocket Server

## 🚀 Servidor WebSocket Puro

El proyecto ahora usa **WebSocket nativo** (sin FastAPI) para comunicación en tiempo real optimizada.

---

## 🌐 Iniciar el Servidor

```bash
# Activar entorno virtual
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor WebSocket
python -m app.main
```

El servidor estará disponible en: **`ws://localhost:8000`**

---

## 📡 Protocolo de Comunicación

### Conexión
```javascript
const ws = new WebSocket('ws://localhost:8000');
```

Al conectar, recibes un mensaje de bienvenida:
```json
{
  "type": "welcome",
  "message": "Bienvenido a VisionAI WebSocket Server",
  "version": "2.0.0",
  "commands": {
    "predict": "Predecir emoción",
    "emotions": "Obtener lista de emociones",
    "model_info": "Información del modelo ML",
    "health": "Estado del servidor"
  }
}
```

### Comandos Disponibles

#### 1. PREDICT - Predecir Emoción
**Enviar:**
```json
{
  "command": "predict",
  "image": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

**Recibir:**
```json
{
  "type": "prediction",
  "status": "success",
  "emotion_name": "happy",
  "confidence": 0.9234,
  "model_version_tag": "v1.0.0",
  "processing_time_ms": 145,
  "timestamp": "2025-11-14T10:30:45.123456"
}
```

#### 2. EMOTIONS - Lista de Emociones
**Enviar:**
```json
{
  "command": "emotions"
}
```

**Recibir:**
```json
{
  "type": "emotions",
  "status": "success",
  "emotions": [
    {"id": 1, "name": "angry", "description": "Enojo o ira"},
    {"id": 4, "name": "happy", "description": "Felicidad o alegría"}
  ]
}
```

#### 3. MODEL_INFO - Información del Modelo
**Enviar:**
```json
{
  "command": "model_info"
}
```

**Recibir:**
```json
{
  "type": "model_info",
  "status": "success",
  "info": {
    "status": "loaded",
    "input_shape": [48, 48, 1],
    "num_classes": 7
  }
}
```

#### 4. HEALTH - Estado del Servidor
**Enviar:**
```json
{
  "command": "health"
}
```

**Recibir:**
```json
{
  "type": "health",
  "status": "healthy",
  "service": "VisionAI Backend",
  "timestamp": "2025-11-14T10:30:45",
  "clients_connected": 3
}
```

---

## Cliente Python

Archivo incluido: **`websocket_client_example.py`**

### Comandos

```bash
# Predecir una imagen
python websocket_client_example.py rostro.jpg

# Procesar carpeta de imágenes
python websocket_client_example.py --folder ./imagenes/

# Listar emociones disponibles
python websocket_client_example.py --emotions

# Info del modelo
python websocket_client_example.py --model-info

# Health check
python websocket_client_example.py --health
```

### Código de Ejemplo

```python
import asyncio
import websockets
import json
import base64

async def predict():
    uri = "ws://localhost:8000"
    
    async with websockets.connect(uri) as websocket:
        # Recibir bienvenida
        welcome = await websocket.recv()
        print(json.loads(welcome)["message"])
        
        # Leer imagen
        with open("rostro.jpg", "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode()
        
        # Enviar comando
        await websocket.send(json.dumps({
            "command": "predict",
            "image": image_base64
        }))
        
        # Recibir resultado
        response = await websocket.recv()
        result = json.loads(response)
        
        print(f"Emoción: {result['emotion_name']}")
        print(f"Confianza: {result['confidence']:.2%}")

asyncio.run(predict())
```

---

## Cliente JavaScript/HTML

```html
<!DOCTYPE html>
<html>
<head>
    <title>VisionAI WebSocket</title>
</head>
<body>
    <h1>Predicción de Emociones</h1>
    
    <input type="file" id="imageInput" accept="image/*">
    <button onclick="predict()">Predecir</button>
    
    <div id="result"></div>
    
    <script>
        let ws = null;
        
        // Conectar
        function connect() {
            ws = new WebSocket('ws://localhost:8000');
            
            ws.onopen = () => {
                console.log('Conectado');
            };
            
            ws.onmessage = (event) => {
                const msg = JSON.parse(event.data);
                
                if (msg.type === 'welcome') {
                    console.log(msg.message);
                } else if (msg.type === 'prediction') {
                    showResult(msg);
                } else if (msg.type === 'error') {
                    showError(msg.message);
                }
            };
            
            ws.onerror = (error) => {
                console.error('Error:', error);
            };
        }
        
        // Predecir
        async function predict() {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                connect();
                await new Promise(r => setTimeout(r, 1000));
            }
            
            const file = document.getElementById('imageInput').files[0];
            if (!file) {
                alert('Selecciona una imagen');
                return;
            }
            
            // Convertir a base64
            const reader = new FileReader();
            reader.onload = () => {
                const base64 = reader.result.split(',')[1];
                
                // Enviar
                ws.send(JSON.stringify({
                    command: 'predict',
                    image: base64
                }));
            };
            reader.readAsDataURL(file);
        }
        
        // Mostrar resultado
        function showResult(result) {
            document.getElementById('result').innerHTML = `
                <h2>Resultado</h2>
                <p><strong>Emoción:</strong> ${result.emotion_name}</p>
                <p><strong>Confianza:</strong> ${(result.confidence * 100).toFixed(2)}%</p>
                <p><strong>Tiempo:</strong> ${result.processing_time_ms}ms</p>
            `;
        }
        
        function showError(message) {
            document.getElementById('result').innerHTML = `
                <p style="color: red;">Error: ${message}</p>
            `;
        }
        
        // Auto-conectar
        connect();
    </script>
</body>
</html>
```

---

## Ventajas del WebSocket Puro

| Característica | WebSocket Puro | FastAPI+REST |
|---------------|----------------|--------------|
| **Overhead** | Mínimo | Alto (HTTP) |
| **Latencia** | <10ms | ~50ms |
| **Conexiones** | Persistentes | Por request |
| **Memoria** | Baja | Media-Alta |
| **Escalabilidad** | +++++ | +++ |
| **Complejidad** | Baja | Media |

---

## Arquitectura

```
Cliente → WebSocket → handle_client()
                          ↓
                    [Router de Comandos]
                          ↓
         ┌────────────────┼────────────────┐
         ↓                ↓                ↓
    predict()      get_emotions()   model_info()
         ↓                ↓                ↓
  prediction_service   Database      ml_service
         ↓
    [ML Model]
         ↓
    Response → Cliente
```

---

## Solución de Problemas

### Error: "No module named 'websockets'"
```bash
pip install websockets
```

### Error: "Connection refused"
- Verifica que el servidor esté corriendo: `python -m app.main`
- Confirma el puerto 8000 está libre
- Usa `ws://` no `http://`

### Error: "Invalid base64"
- Asegúrate de enviar solo la cadena base64
- No incluyas el prefijo `data:image/png;base64,`

### Servidor no responde
- Revisa los logs del servidor
- Verifica la conexión a la base de datos
- Confirma que el modelo ML está cargado

---

## Cambios vs FastAPI

| Antes (FastAPI) | Ahora (WebSocket) |
|----------------|-------------------|
| `uvicorn app.main:app` | `python -m app.main` |
| `http://localhost:8000` | `ws://localhost:8000` |
| POST /api/v1/predict | command: "predict" |
| multipart/form-data | JSON + base64 |
| Sin estado persistente | Conexión persistente |

---

## Casos de Uso

**Ideal para:**
- Stream de video en tiempo real
- Análisis continuo de cámara web
- Dashboards en vivo
- Aplicaciones móviles
- IoT y edge computing

**No recomendado para:**
- APIs REST públicas
- Integraciones de terceros
- Webhooks
- Servicios sin estado

---

## Recursos

- [Documentación websockets](https://websockets.readthedocs.io/)
- [WebSocket API MDN](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [RFC 6455 - WebSocket Protocol](https://tools.ietf.org/html/rfc6455)

---
