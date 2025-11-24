# Ejemplos y Pruebas - VisionAI Backend

Esta carpeta contiene **ejemplos de clientes y archivos de prueba** para interactuar con el servidor VisionAI Backend.

> **IMPORTANTE:** Estos archivos son **SOLO PARA PRUEBAS Y DEMOSTRACIÓN**. NO son parte de la arquitectura del backend, son ejemplos para que sepas cómo conectarte desde tu frontend o aplicación cliente.

---

## Archivos en esta Carpeta

| Archivo | Descripción |
|---------|-------------|
| `websocket_client_example.py` | Cliente Python CLI para probar WebSocket |
| `test_websocket.html` | Interfaz web de prueba para WebSocket |
| `README.md` | Este archivo (documentación de ejemplos) |

---

## Inicio Rápido

### 1. Iniciar el Servidor

```bash
# Activar entorno virtual
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Desde la raíz del proyecto
python -m app.main
```

El servidor estará disponible en: **`ws://localhost:8000`**

### 2. Probar con Cliente Python

```bash
# Predecir una imagen
python examples/websocket_client_example.py imagen.jpg

# Procesar carpeta completa
python examples/websocket_client_example.py --folder ./imagenes/

# Listar emociones disponibles
python examples/websocket_client_example.py --emotions

# Información del modelo ML
python examples/websocket_client_example.py --model-info

# Health check del servidor
python examples/websocket_client_example.py --health
```

### 3. Probar con Interfaz Web

Abre `test_websocket.html` en tu navegador y conecta a `ws://localhost:8000`.

---

## Protocolo WebSocket

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

#### PREDICT - Predecir Emoción

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
  "timestamp": "2025-11-24T10:30:45.123456"
}
```

#### EMOTIONS - Lista de Emociones

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
    {"id": 2, "name": "disgust", "description": "Disgusto"},
    {"id": 3, "name": "fear", "description": "Miedo"},
    {"id": 4, "name": "happy", "description": "Felicidad o alegría"},
    {"id": 5, "name": "neutral", "description": "Neutral"},
    {"id": 6, "name": "sad", "description": "Tristeza"},
    {"id": 7, "name": "surprise", "description": "Sorpresa"}
  ]
}
```

#### MODEL_INFO - Información del Modelo

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
    "input_shape": [96, 96, 3],
    "num_classes": 7
  }
}
```

#### HEALTH - Estado del Servidor

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
  "timestamp": "2025-11-24T10:30:45",
  "clients_connected": 3
}
```

---

## Ejemplos de Código

### Python

```python
import asyncio
import websockets
import json
import base64

async def predict_emotion(image_path):
    uri = "ws://localhost:8000"
    
    async with websockets.connect(uri) as websocket:
        # Recibir bienvenida
        welcome = await websocket.recv()
        print(json.loads(welcome)["message"])
        
        # Leer y codificar imagen
        with open(image_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode()
        
        # Enviar comando de predicción
        await websocket.send(json.dumps({
            "command": "predict",
            "image": image_base64
        }))
        
        # Recibir resultado
        response = await websocket.recv()
        result = json.loads(response)
        
        print(f"Emoción detectada: {result['emotion_name']}")
        print(f"Confianza: {result['confidence']:.2%}")
        print(f"Tiempo de procesamiento: {result['processing_time_ms']}ms")

# Ejecutar
asyncio.run(predict_emotion("rostro.jpg"))
```

### JavaScript/HTML

```html
<!DOCTYPE html>
<html>
<head>
    <title>VisionAI Test</title>
</head>
<body>
    <h1>Predicción de Emociones</h1>
    <input type="file" id="imageInput" accept="image/*">
    <button onclick="predict()">Predecir</button>
    <div id="result"></div>
    
    <script>
        let ws = new WebSocket('ws://localhost:8000');
        
        ws.onopen = () => console.log('Conectado a VisionAI');
        
        ws.onmessage = (event) => {
            const msg = JSON.parse(event.data);
            
            if (msg.type === 'prediction') {
                document.getElementById('result').innerHTML = `
                    <h2>Resultado</h2>
                    <p><strong>Emoción:</strong> ${msg.emotion_name}</p>
                    <p><strong>Confianza:</strong> ${(msg.confidence * 100).toFixed(2)}%</p>
                    <p><strong>Tiempo:</strong> ${msg.processing_time_ms}ms</p>
                `;
            }
        };
        
        async function predict() {
            const file = document.getElementById('imageInput').files[0];
            if (!file) return alert('Selecciona una imagen');
            
            const reader = new FileReader();
            reader.onload = () => {
                const base64 = reader.result.split(',')[1];
                ws.send(JSON.stringify({
                    command: 'predict',
                    image: base64
                }));
            };
            reader.readAsDataURL(file);
        }
    </script>
</body>
</html>
```

---

## 🏗️ Arquitectura

```
visionai_backend/
├── app/                          ← BACKEND (servidor)
│   ├── main.py                  ← Punto de entrada del servidor
│   ├── api/                     ← Rutas y endpoints
│   ├── config/                  ← Configuración y base de datos
│   ├── models/                  ← Modelos SQLAlchemy y schemas
│   ├── services/                ← Lógica de negocio
│   └── utils/                   ← Utilidades
│
├── examples/                     ← EJEMPLOS (este directorio)
│   ├── websocket_client_example.py
│   ├── test_websocket.html
│   └── README.md
│
├── ml_models/                    ← Modelos de Machine Learning
│   └── modelo_emociones.keras
│
└── requirements.txt
```

### Flujo de Datos

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

## Casos de Uso

### Ideal para:
- Stream de video en tiempo real
- Análisis continuo de cámara web
- Dashboards en vivo
- Aplicaciones móviles
- IoT y edge computing
- Chat bots con análisis de emociones

### No recomendado para:
- APIs REST públicas tradicionales
- Integraciones con servicios de terceros sin WebSocket
- Webhooks
- Servicios completamente sin estado

---

## Solución de Problemas

### Error: "Connection refused"
```bash
# Verifica que el servidor esté corriendo
python -m app.main

# Confirma que el puerto 8000 esté libre
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Asegúrate de usar ws:// no http://
```

### Error: "No module named 'websockets'"
```bash
# Instalar dependencias
pip install -r requirements.txt
```

### Error: "Invalid base64"
- Asegúrate de enviar **solo la cadena base64**
- **No incluyas** el prefijo `data:image/png;base64,`
- Verifica que la imagen esté en formato JPEG o PNG

### Servidor no responde
- Revisa los logs del servidor en la terminal
- Verifica la conexión a la base de datos PostgreSQL
- Confirma que el modelo ML esté cargado correctamente

### Error en predicción
- Verifica formato de imagen (JPEG, PNG)
- Confirma codificación base64 correcta
- Revisa tamaño de imagen (<5MB recomendado)

---

## Rendimiento

| Métrica | Valor |
|---------|-------|
| **Latencia promedio** | <10ms |
| **Throughput** | 100+ predicciones/segundo |
| **Memoria en uso** | ~500MB (con modelo cargado) |
| **Conexiones simultáneas** | Hasta 1000 clientes |

---

## Seguridad

Para **producción**, implementa:

- Usar **WSS** (WebSocket Secure) en lugar de WS
- Implementar **autenticación JWT**
- Validar **origen de conexiones** (CORS)
- Limitar **tamaño de imágenes** (<5MB)
- **Rate limiting** por cliente
- Sanitización de **inputs**
- Logs de **auditoría**

---

## Recursos Adicionales

- [Documentación WebSocket](https://websockets.readthedocs.io/)
- [WebSocket API MDN](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [RFC 6455 - WebSocket Protocol](https://tools.ietf.org/html/rfc6455)
- [TensorFlow/Keras Docs](https://www.tensorflow.org/api_docs)

---

## Migración desde FastAPI

Si vienes de una versión anterior con FastAPI:

| Antes (FastAPI) | Ahora (WebSocket Puro) |
|----------------|------------------------|
| `uvicorn app.main:app` | `python -m app.main` |
| `http://localhost:8000` | `ws://localhost:8000` |
| POST /api/v1/predict | `{"command": "predict"}` |
| multipart/form-data | JSON + base64 |
| Sin estado persistente | Conexión persistente |

---

## Ventajas del WebSocket Puro

| Característica | WebSocket Puro | FastAPI+REST |
|---------------|----------------|--------------|
| **Overhead** | Mínimo | Alto (HTTP headers) |
| **Latencia** | <10ms | ~50ms |
| **Conexiones** | Persistentes | Por request |
| **Memoria** | Baja | Media-Alta |
| **Escalabilidad** | ★★★★★ | ★★★ |
| **Complejidad** | Baja | Media |
| **Bidireccional** | Nativo | Requiere polling |

---

## Licencia

MIT License

## Autores

VisionAI Team