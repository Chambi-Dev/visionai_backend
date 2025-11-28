# VisionAI Backend - Sistema Híbrido REST + WebSocket

> Sistema de predicción de emociones faciales con API REST para estadísticas y WebSocket para stream de cámara en tiempo real

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![WebSocket](https://img.shields.io/badge/WebSocket-13.1-blue.svg)](https://websockets.readthedocs.io/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15+-orange.svg)](https://www.tensorflow.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Descripción

VisionAI Backend es un sistema híbrido que combina:
- **API REST (FastAPI)** - Para estadísticas, dashboard y predicciones de imágenes estáticas
- **WebSocket** - Para stream de cámara en tiempo real con latencia ultra-baja

El sistema utiliza Deep Learning para detectar emociones faciales y clasifica expresiones en 7 emociones diferentes.

### Características Principales

- **API REST** - Endpoints para estadísticas, dashboard y predicciones
- **WebSocket** - Stream de cámara en tiempo real (< 10ms latencia)
- **Autenticación JWT** - Sistema de usuarios con login/registro
- **Rastreo de Usuario** - Cada predicción asociada a un usuario
- **Deep Learning** - CNN entrenada para 7 emociones
- **7 Emociones** - angry, disgust, fear, happy, neutral, sad, surprise
- **Persistencia** - PostgreSQL con SQLAlchemy
- **Dashboard** - Estadísticas y analytics completos
- **Documentación** - Swagger UI automática en `/docs`
- **Alto Rendimiento** - 100+ predicciones/segundo

## Arquitectura

```
┌─────────────────────────────────────────────┐
│            Frontend/Cliente                  │
└────────┬────────────────────┬────────────────┘
         │                    │
         │ REST API           │ WebSocket
         │ (Estadísticas)     │ (Cámara en vivo)
         ↓                    ↓
┌────────────────────────────────────────────────┐
│       VisionAI Backend (FastAPI + WS)          │
├────────────────────────────────────────────────┤
│  REST API:                  WebSocket:         │
│  • POST /api/v1/predict     • ws://host/ws     │
│  • GET  /api/v1/emotions    • predict          │
│  • GET  /api/v1/model/info  • emotions         │
│  • GET  /api/v1/dashboard/* • model_info       │
│  • GET  /api/v1/health      • health           │
│                                                 │
│  AUTH API:                                      │
│  • POST /api/v1/auth/register                  │
│  • POST /api/v1/auth/login                     │
│  • GET  /api/v1/auth/verify                    │
│  • GET  /api/v1/auth/users/me                  │
└────────┬───────────────────────────────────────┘
         │
         ├──→ prediction_service.py
         │    └──→ ml_service.py → modelo_emociones.h5
         │
         └──→ PostgreSQL
              ├── predictions_log (con user)
              ├── emotion_classes
              ├── model_versions
              └── users
```

## Casos de Uso

### REST API - Para:
- **Dashboard web** - Obtener estadísticas y gráficos
- **Upload de imágenes** - Analizar fotos estáticas
- **Analytics** - Consultar histórico y métricas
- **Reportes** - Generar informes de uso

### WebSocket - Para:
- **Stream de cámara** - Análisis en tiempo real
- **Apps interactivas** - Juegos con detección facial
- **Bots** - Respuesta en tiempo real a emociones
- **Apps móviles** - Detección continua

## Inicio Rápido

### Prerequisitos

- Python 3.11 o superior
- PostgreSQL 12+
- 2GB RAM mínimo (para modelo ML)

### Instalación

1. **Clonar repositorio**
```bash
git clone https://github.com/Chambi-Dev/visionai_backend.git
cd visionai_backend
```

2. **Crear entorno virtual**
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tu contraseña de PostgreSQL
# Por defecto usa la contraseña "123"
# Cambia solo la contraseña en DATABASE_URL si la tuya es diferente
```

5. **Configurar base de datos**
```bash
# Crear base de datos en PostgreSQL
createdb visionai_db

# Ejecutar migraciones
alembic upgrade head
```

6. **Iniciar servidor**
```bash
python -m app.main
```

El servidor estará disponible en:
- **REST API:** http://localhost:8000
- **Documentación:** http://localhost:8000/docs
- **WebSocket:** ws://localhost:8000/ws

## API REST

### Documentación Interactiva

Accede a la documentación Swagger en: **http://localhost:8000/docs**

### Autenticación

El sistema incluye autenticación JWT para identificar usuarios en las predicciones.

#### Registrar Usuario

```bash
POST /api/v1/auth/register
Content-Type: application/json

curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario",
    "password": "contraseña123"
  }'
```

**Respuesta:**
```json
{
  "user_id": 1,
  "username": "usuario",
  "is_active": true,
  "created_at": "2025-11-28T10:30:00"
}
```

#### Iniciar Sesión

```bash
POST /api/v1/auth/login
Content-Type: application/json

curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario",
    "password": "contraseña123"
  }'
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Verificar Token

```bash
GET /api/v1/auth/verify
Authorization: Bearer <token>

curl "http://localhost:8000/api/v1/auth/verify" \
  -H "Authorization: Bearer <token>"
```

#### Obtener Usuario Actual

```bash
GET /api/v1/auth/users/me
Authorization: Bearer <token>

curl "http://localhost:8000/api/v1/auth/users/me" \
  -H "Authorization: Bearer <token>"
```

### Endpoints Principales

#### 1. Predicción (Upload de Imagen)

**Sin autenticación (anónima):**
```bash
POST /api/v1/predict
Content-Type: multipart/form-data

curl -X POST "http://localhost:8000/api/v1/predict" \
  -F "file=@imagen.jpg"
```

**Con autenticación (asociada a usuario):**
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Authorization: Bearer <token>" \
  -F "file=@imagen.jpg"
```

**Respuesta:**
```json
{
  "emotion_name": "happy",
  "confidence": 0.9234,
  "model_version_tag": "v1.0.0",
  "processing_time_ms": 145
}
```

> **Nota:** Si envías el token de autenticación, la predicción se guardará asociada a tu usuario en la base de datos (campo `user` en `predictions_log`).

#### 2. Listar Emociones

```bash
GET /api/v1/emotions

curl "http://localhost:8000/api/v1/emotions"
```

#### 3. Información del Modelo

```bash
GET /api/v1/model/info

curl "http://localhost:8000/api/v1/model/info"
```

#### 4. Health Check

```bash
GET /api/v1/health

curl "http://localhost:8000/api/v1/health"
```

### Endpoints de Dashboard

#### Estadísticas Generales

```bash
GET /api/v1/dashboard/stats
```

**Respuesta:**
```json
{
  "total_predictions": 1523,
  "most_common_emotion": {
    "name": "happy",
    "count": 542
  },
  "average_confidence": 0.8756,
  "predictions_by_emotion": {
    "happy": 542,
    "neutral": 389,
    "sad": 234
  }
}
```

#### Predicciones Recientes

```bash
GET /api/v1/dashboard/recent?limit=10
```

#### Timeline de Predicciones

```bash
GET /api/v1/dashboard/timeline?days=7
```

#### Estadísticas por Emoción

```bash
GET /api/v1/dashboard/emotion/{emotion_name}
```

## WebSocket (Stream de Cámara)

### Conectar al WebSocket

**Ruta:** `ws://localhost:8000/ws`

**JavaScript:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
    console.log('Conectado al stream de cámara');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'prediction') {
        console.log('Emoción:', data.emotion_name);
        console.log('Confianza:', data.confidence);
    }
};

// Enviar frame de cámara
function sendFrame(imageBase64) {
    ws.send(JSON.stringify({
        command: 'predict',
        image: imageBase64  // Sin prefijo data:image
    }));
}
```

**JavaScript:**
```javascript
const ws = new WebSocket('ws://localhost:8000');

ws.onopen = () => {
    console.log('Conectado a VisionAI');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Respuesta:', data);
};
```

**Python:**
```python
import asyncio
import websockets
import json

async def connect():
    uri = "ws://localhost:8000"
    async with websockets.connect(uri) as websocket:
        # Recibir bienvenida
        welcome = await websocket.recv()
        print(json.loads(welcome))
        
        # Enviar comando
        await websocket.send(json.dumps({"command": "health"}))
        
        # Recibir respuesta
        response = await websocket.recv()
        print(json.loads(response))

asyncio.run(connect())
```

### Comandos Disponibles

#### 1. PREDICT - Predicción de Emoción

**Sin autenticación:**
```json
{
  "command": "predict",
  "image": "iVBORw0KGgoAAAANSUhEUgAA..."  // Base64
}
```

**Con autenticación (recomendado):**
```json
{
  "command": "predict",
  "image": "iVBORw0KGgoAAAANSUhEUgAA...",  // Base64
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  // JWT token
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
  "timestamp": "2025-11-28T10:30:45.123456",
  "user": "username"  // Si se envió token
}
```

> **Nota:** Si incluyes el campo `token` con un JWT válido, la predicción se asociará a tu usuario en la base de datos.

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
    "input_shape": "(None, 96, 96, 3)",
    "num_classes": 7,
    "total_params": 3227687
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
  "clients_connected": 3
}
```

## Pruebas

### Cliente Python de Ejemplo

```bash
# Health check
python examples/websocket_client_example.py --health

# Listar emociones
python examples/websocket_client_example.py --emotions

# Info del modelo
python examples/websocket_client_example.py --model-info

# Predecir una imagen
python examples/websocket_client_example.py imagen.jpg

# Procesar carpeta
python examples/websocket_client_example.py --folder ./imagenes/
```

### Interfaz Web de Prueba

Abre `examples/test_websocket.html` en tu navegador para probar la API visualmente.

## Estructura del Proyecto

```
visionai_backend/
├── app/
│   ├── main.py                    # Servidor WebSocket principal
│   ├── __init__.py
│   ├── api/
│   │   ├── dependencies.py        # Dependencias (DB session)
│   │   └── routes/                # (Legacy - no usadas)
│   ├── config/
│   │   ├── database.py            # Configuración SQLAlchemy
│   │   └── settings.py            # Variables de configuración
│   ├── models/
│   │   ├── database_models.py     # Modelos ORM
│   │   └── schemas.py             # Schemas Pydantic
│   ├── services/
│   │   ├── ml_service.py          # Servicio Machine Learning
│   │   └── prediction_service.py  # Lógica de predicciones
│   └── utils/
│       ├── image_processing.py    # Preprocesamiento imágenes
│       └── logger.py              # Sistema de logging
├── ml_models/
│   └── modelo_emociones.h5        # Modelo ML entrenado
├── alembic/                        # Migraciones de BD
├── examples/                       # Ejemplos de clientes
├── requirements.txt                # Dependencias Python
└── README.md
```

## Configuración

### Variables de Entorno

El proyecto usa variables de entorno para configuración sensible como contraseñas de base de datos.

#### Configuración Inicial

1. **Copiar archivo de ejemplo:**
   ```bash
   cp .env.example .env
   ```

2. **Editar `.env` con tu configuración local:**
   ```env
   # Base de datos - CAMBIA LA CONTRASEÑA según tu PostgreSQL
   DATABASE_URL=postgresql+psycopg2://postgres:TU_CONTRASEÑA@localhost:5432/visionai_db
   
   # Servidor WebSocket
   HOST=0.0.0.0
   PORT=8000
   
   # Modelo ML
   MODEL_PATH=ml_models/modelo_emociones.h5
   
   # Debug
   DEBUG=True
   ```

3. **Importante:** El archivo `.env` está en `.gitignore` y **NUNCA** se sube a Git por seguridad.

#### Gestión de Contraseñas

- **`.env.example`** - Archivo de plantilla con contraseña por defecto `123` (se sube a Git)
- **`.env`** - Tu configuración local con tu contraseña real (NO se sube a Git)

**Para trabajo en equipo:**
- Cada desarrollador copia `.env.example` a `.env`
- Cada uno modifica la contraseña según su PostgreSQL local
- Nadie sube su `.env` al repositorio
- Si no existe `.env`, el sistema usa automáticamente la contraseña `123` por defecto

**Ejemplo para diferentes máquinas:**
```bash
# Máquina 1 (.env)
DATABASE_URL=postgresql+psycopg2://postgres:miPassword123@localhost:5432/visionai_db

# Máquina 2 (.env)
DATABASE_URL=postgresql+psycopg2://postgres:otraPassword@localhost:5432/visionai_db

# Git (.env.example) - Contraseña por defecto
DATABASE_URL=postgresql+psycopg2://postgres:123@localhost:5432/visionai_db
```

### Configuración de la Base de Datos

El proyecto usa PostgreSQL con las siguientes tablas:

- **emotion_classes** - Catálogo de emociones
- **model_versions** - Versiones del modelo ML
- **predictions_log** - Historial de predicciones con usuario
- **users** - Usuarios del sistema (autenticación)

#### Esquema de predictions_log

```sql
CREATE TABLE predictions_log (
    predic_id BIGSERIAL PRIMARY KEY,
    emotion_id BIGINT NOT NULL,
    confidence FLOAT NOT NULL,
    model_id BIGINT NOT NULL,
    processing_time_ms INTEGER,
    source_ip INET,
    user VARCHAR(50),  -- ← Usuario que hizo la predicción
    timestamp TIMESTAMPTZ DEFAULT NOW()
);
```

## Autenticación y Rastreo de Usuarios

### Sistema de Usuarios

El backend incluye un sistema completo de autenticación JWT que permite:

- Registro de nuevos usuarios
- Login con generación de token JWT
- Asociación de predicciones a usuarios
- Consulta de historial por usuario
- Análisis de uso por usuario

### Flujo de Autenticación

```mermaid
sequenceDiagram
    Cliente->>Backend: POST /auth/register
    Backend-->>Cliente: Usuario creado
    Cliente->>Backend: POST /auth/login
    Backend-->>Cliente: JWT token
    Cliente->>Backend: POST /predict + Bearer token
    Backend->>BD: Guarda predicción con username
    Backend-->>Cliente: Resultado + user
```

### Ejemplo Completo de Uso

**1. Registrar usuario:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "usuario", "password": "pass123"}'
```

**2. Login:**
```bash
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "usuario", "password": "pass123"}' \
  | jq -r '.access_token')
```

**3. Predicción autenticada:**
```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@imagen.jpg"
```

**4. Ver predicciones del usuario:**
```sql
SELECT * FROM predictions_log 
WHERE user = 'usuario' 
ORDER BY timestamp DESC;
```

### Interfaz de Prueba

Incluimos una interfaz web completa para probar la autenticación:

**Abre:** `examples/test_websocket_auth.html`

Características:
- Login con usuario y contraseña
- Conexión WebSocket persistente
- Upload de imágenes con predicción
- Predicciones asociadas al usuario
- Visualización de resultados en tiempo real

### Consultas SQL Útiles

**Predicciones por usuario:**
```sql
SELECT 
    user,
    COUNT(*) as total,
    AVG(confidence) as confianza_promedio
FROM predictions_log
WHERE user IS NOT NULL
GROUP BY user
ORDER BY total DESC;
```

**Top emociones por usuario:**
```sql
SELECT 
    pl.user,
    ec.emotion_name,
    COUNT(*) as veces,
    AVG(pl.confidence) as confianza
FROM predictions_log pl
JOIN emotion_class ec ON pl.emotion_id = ec.emotion_id
WHERE pl.user = 'usuario'
GROUP BY pl.user, ec.emotion_name
ORDER BY veces DESC;
```

**Historial de actividad:**
```sql
SELECT 
    timestamp,
    user,
    emotion_name,
    confidence
FROM predictions_log pl
JOIN emotion_class ec ON pl.emotion_id = ec.emotion_id
WHERE user IS NOT NULL
ORDER BY timestamp DESC
LIMIT 50;
```

### Notas de Seguridad

- Contraseñas hasheadas con bcrypt
- Tokens JWT con expiración de 24 horas
- Secret key configurable en producción
- Autenticación opcional (compatible con predicciones anónimas)

Para más detalles, consulta: [`examples/USER_TRACKING_GUIDE.md`](examples/USER_TRACKING_GUIDE.md)

## Modelo de Machine Learning

- **Arquitectura:** CNN (Convolutional Neural Network)
- **Input:** Imágenes 96x96x3 (RGB)
- **Output:** 7 clases (emociones)
- **Parámetros:** ~3.2M
- **Formato:** HDF5 (.h5)
- **Framework:** TensorFlow/Keras

### Preprocesamiento de Imágenes

1. Conversión a RGB
2. Redimensionamiento a 96x96
3. Detección facial (opcional)
4. Normalización [0, 1]
5. Expansión de dimensiones (batch)

## Despliegue en Producción

### Docker (Recomendado)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "-m", "app.main"]
```

```bash
docker build -t visionai-backend .
docker run -p 8000:8000 visionai-backend
```

### Servidor Linux

```bash
# Con supervisor o systemd
sudo nano /etc/systemd/system/visionai.service

[Unit]
Description=VisionAI WebSocket Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/visionai_backend
ExecStart=/var/www/visionai_backend/venv/bin/python -m app.main
Restart=always

[Install]
WantedBy=multi-user.target
```

## Rendimiento

| Métrica | Valor |
|---------|-------|
| **Latencia promedio** | < 10ms |
| **Throughput** | 100+ pred/s |
| **Memoria (con modelo)** | ~500MB |
| **Clientes simultáneos** | 1000+ |
| **Tamaño de modelo** | 37MB |

## Solución de Problemas

### Servidor no inicia

```bash
# Verificar puerto ocupado
netstat -ano | findstr :8000

# Matar proceso
taskkill /PID <PID> /F  # Windows
kill -9 <PID>           # Linux
```

### Error de conexión a BD

```bash
# Verificar PostgreSQL activo
pg_isready

# Probar conexión
psql -U postgres -d visionai_db

# Si falla por contraseña incorrecta:
# 1. Verifica tu contraseña de PostgreSQL
# 2. Edita el archivo .env con la contraseña correcta
# 3. Reinicia el servidor: python -m app.main
```

### Configuración en nueva máquina

```bash
# 1. Clonar repositorio
git clone <url>

# 2. Copiar configuración de ejemplo
cp .env.example .env

# 3. Editar .env con TU contraseña de PostgreSQL
nano .env  # o notepad .env en Windows

# 4. Instalar dependencias y ejecutar
pip install -r requirements.txt
alembic upgrade head
python -m app.main
```

### Modelo no carga

```bash
# Verificar archivo existe
ls -lh ml_models/modelo_emociones.h5

# Si tienes .keras, convertir a .h5
# Ya está incluido en el código
```

## Contribución

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## Autores

- **VisionAI Team** - Desarrollo inicial

## Recursos Adicionales

- [Documentación WebSocket](https://websockets.readthedocs.io/)
- [TensorFlow Guide](https://www.tensorflow.org/guide)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Guía completa de uso](examples/WEBSOCKET_GUIDE.md)