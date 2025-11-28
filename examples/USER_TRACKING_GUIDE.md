# Guía de Autenticación en Predicciones

## Resumen de Cambios

Se agregó la funcionalidad de **rastreo de usuario** en las predicciones de emociones. Ahora cada predicción puede ser asociada a un usuario autenticado, permitiendo mejor clasificación y análisis de datos.

---

## Cambios Implementados

### 1. Base de Datos

**Nueva columna en `predictions_log`:**
```sql
ALTER TABLE predictions_log ADD COLUMN user VARCHAR(50);
```

- **Tipo:** VARCHAR(50)
- **Nullable:** Sí (para mantener compatibilidad con datos existentes)
- **Propósito:** Almacenar el username del usuario que realizó la predicción

### 2. Modelos de Datos

**SQLAlchemy Model (`database_models.py`):**
```python
class PredictionsLog(Base):
    # ... campos existentes ...
    user = Column(String(50), nullable=True)
```

**Pydantic Schema (`schemas.py`):**
```python
class PredictionLogBase(BaseModel):
    # ... campos existentes ...
    user: Optional[str] = None
```

### 3. Servicios

**PredictionService (`prediction_service.py`):**
- Método `predict_emotion()` ahora acepta parámetro `user: Optional[str]`
- Método `_save_prediction()` guarda el usuario en la base de datos

### 4. API REST

**Endpoint `/api/v1/predict`:**
- Acepta header opcional: `Authorization: Bearer <token>`
- Si el token es válido, extrae el username y lo asocia a la predicción
- Si no hay token, la predicción se guarda sin usuario (anónima)

**Ejemplo con curl:**
```bash
# Con autenticación
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Authorization: Bearer eyJhbGc..." \
  -F "file=@rostro.jpg"

# Sin autenticación (anónima)
curl -X POST "http://localhost:8000/api/v1/predict" \
  -F "file=@rostro.jpg"
```

### 5. WebSocket

**Protocolo actualizado:**

El comando `predict` ahora acepta un campo opcional `token`:

```json
{
  "command": "predict",
  "image": "base64_encoded_image",
  "token": "jwt_token_here"
}
```

**Respuesta incluye usuario:**
```json
{
  "type": "prediction",
  "status": "success",
  "emotion_name": "happy",
  "confidence": 0.95,
  "user": "username",
  "timestamp": "2025-11-28T17:30:00"
}
```

---

## Uso

### Opción 1: API REST con Autenticación

```python
import requests

# 1. Login
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={
        "username": "usuario",
        "password": "contraseña"
    }
)
token = login_response.json()["access_token"]

# 2. Predicción autenticada
with open("rostro.jpg", "rb") as f:
    predict_response = requests.post(
        "http://localhost:8000/api/v1/predict",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": f}
    )

print(predict_response.json())
```

### Opción 2: WebSocket con Autenticación

```javascript
// 1. Login
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        username: 'usuario',
        password: 'contraseña'
    })
});
const { access_token } = await loginResponse.json();

// 2. Conectar WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');

// 3. Enviar predicción con token
ws.send(JSON.stringify({
    command: 'predict',
    image: base64Image,
    token: access_token
}));
```

### Opción 3: Interfaz Web de Prueba

Abre `examples/test_websocket_auth.html` en tu navegador:

1. **Login:** Ingresa usuario y contraseña
2. **Conectar:** Click en "Conectar al servidor"
3. **Predecir:** Selecciona imagen y click en "Predecir"

La predicción se guardará con tu usuario automáticamente.

---

## Consultas SQL Útiles

### Ver predicciones por usuario
```sql
SELECT 
    user,
    COUNT(*) as total_predicciones,
    AVG(confidence) as confianza_promedio
FROM predictions_log
WHERE user IS NOT NULL
GROUP BY user
ORDER BY total_predicciones DESC;
```

### Ver historial de un usuario específico
```sql
SELECT 
    pl.timestamp,
    ec.emotion_name,
    pl.confidence,
    pl.processing_time_ms
FROM predictions_log pl
JOIN emotion_class ec ON pl.emotion_id = ec.emotion_id
WHERE pl.user = 'username'
ORDER BY pl.timestamp DESC
LIMIT 50;
```

### Comparar predicciones autenticadas vs anónimas
```sql
SELECT 
    CASE WHEN user IS NULL THEN 'Anónimo' ELSE 'Autenticado' END as tipo,
    COUNT(*) as total,
    AVG(confidence) as confianza_promedio
FROM predictions_log
GROUP BY CASE WHEN user IS NULL THEN 'Anónimo' ELSE 'Autenticado' END;
```

---

## Migración

La migración de Alembic ya fue aplicada. Si necesitas revertir:

```bash
# Revertir un paso
alembic downgrade -1

# Volver a aplicar
alembic upgrade head
```

---

## Notas Importantes

### Compatibilidad con Datos Existentes

- La columna `user` es **nullable**, por lo que las predicciones antiguas seguirán funcionando
- Las predicciones sin autenticación tendrán `user = NULL`
- No se requiere migración manual de datos

### Comportamiento por Defecto

- **REST API:** Si no se envía token, la predicción es anónima
- **WebSocket:** Si no se envía token en el mensaje, la predicción es anónima
- **Sin breaking changes:** El sistema sigue funcionando igual sin autenticación

### Seguridad

El token JWT se valida pero **no es obligatorio**. Si quieres hacer la autenticación obligatoria:

1. Modifica `get_current_user_optional` a `get_current_user` (required)
2. Agrega validación en el WebSocket para rechazar predicciones sin token

---

## Testing

### Test Manual

1. **Crear usuario:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "test123"}'
```

2. **Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "test123"}'
```

3. **Predicción autenticada:**
```bash
TOKEN="<token_from_step_2>"
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@imagen.jpg"
```

4. **Verificar en BD:**
```sql
SELECT * FROM predictions_log ORDER BY timestamp DESC LIMIT 1;
```

---

## Archivos Modificados

- `app/models/database_models.py` - Añadida columna `user`
- `app/models/schemas.py` - Añadido campo `user` en schemas
- `app/services/prediction_service.py` - Parámetro `user` en métodos
- `app/api/dependencies.py` - Nueva dependencia `get_current_user_optional`
- `app/api/routes/predictions.py` - Soporte para token en REST
- `app/main.py` - Soporte para token en WebSocket
- `alembic/versions/a8ae8804d8b9_*.py` - Migración de BD
- `visionai_db.sql` - Schema actualizado
- `examples/test_websocket_auth.html` - Nueva interfaz de prueba
