# Sistema de Gestión de Usuarios - VisionAI

Sistema completo de autenticación con JWT para VisionAI Backend.

## Implementación Completada

### 1. **Modelo de Base de Datos**
- Tabla `users` creada en PostgreSQL
- Campos: `user_id`, `username`, `hashed_password`, `is_active`, `created_at`, `updated_at`
- Migración de Alembic aplicada

### 2. **Servicios de Autenticación**
- Hash de contraseñas con bcrypt
- Generación de tokens JWT
- Verificación de tokens
- Autenticación de usuarios

### 3. **Endpoints REST**
```
POST /api/v1/auth/register  - Registrar nuevo usuario
POST /api/v1/auth/login     - Iniciar sesión (obtener token)
GET  /api/v1/auth/verify    - Verificar token
GET  /api/v1/auth/users/me  - Obtener perfil del usuario actual
```

### 4. **Interfaz de Prueba**
- `examples/test_auth.html` - Interfaz web para testing

## Cómo Probar

### Paso 1: Iniciar el Servidor

```bash
# Activar entorno virtual
venv\Scripts\activate

# Iniciar servidor
python -m app.main
```

El servidor estará disponible en:
- **API Docs:** http://localhost:8000/docs
- **Autenticación:** http://localhost:8000/api/v1/auth/*

### Paso 2: Abrir Interfaz de Prueba

Abre el archivo en tu navegador:
```
examples/test_auth.html
```

### Paso 3: Probar Funcionalidades

#### A) Registrar Usuario
1. Ir a la pestaña "Registro"
2. Ingresar username (min 3 caracteres)
3. Ingresar contraseña (min 6 caracteres)
4. Click en "Registrar Usuario"
5. Debe mostrar el usuario creado con su ID

#### B) Iniciar Sesión
1. Ir a la pestaña "Login"
2. Ingresar username y contraseña del usuario creado
3. Click en "Iniciar Sesión"
4. Debe mostrar el token JWT generado
5. Aparecerá sección de "Verificar Token"

#### C) Verificar Token
1. Después de hacer login, click en "Verificar Token"
2. Debe mostrar información del usuario decodificada del token

#### D) Ver Perfil
1. Click en "Ver Perfil"
2. Debe mostrar información completa del usuario actual

## Probar con Swagger

1. Ir a http://localhost:8000/docs
2. Buscar la sección "Authentication"
3. Probar endpoints:

### Registrar usuario:
```json
POST /api/v1/auth/register
{
  "username": "testuser",
  "password": "password123"
}
```

### Login:
```json
POST /api/v1/auth/login
{
  "username": "testuser",
  "password": "password123"
}
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Verificar token:
```
GET /api/v1/auth/verify?token=<TOKEN_AQUI>
```

## Estructura de la BD

```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX ix_users_username ON users(username);
```

## Seguridad

- Contraseñas hasheadas con bcrypt
- Tokens JWT con expiración (24 horas)
- Username único en base de datos
- Validación de longitud mínima (username: 3, password: 6)
- **SECRET_KEY en producción:** Cambiar en `auth_service.py`

## Ejemplos de Uso con cURL

### Registrar:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"usuario1", "password":"mipassword"}'
```

### Login:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"usuario1", "password":"mipassword"}'
```

### Verificar token:
```bash
curl "http://localhost:8000/api/v1/auth/verify?token=TU_TOKEN_AQUI"
```

## Casos de Prueba

### Casos Exitosos:
1. Registrar usuario nuevo → 201 Created
2. Login con credenciales correctas → 200 OK + Token
3. Verificar token válido → 200 OK + User info

### Casos de Error:
1. Registrar username duplicado → 400 Bad Request
2. Login con password incorrecta → 401 Unauthorized
3. Verificar token inválido/expirado → 401 Unauthorized
4. Username < 3 caracteres → 422 Validation Error
5. Password < 6 caracteres → 422 Validation Error

## Configuración

### Cambiar duración del token:
En `app/services/auth_service.py`:
```python
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas
```

### Cambiar SECRET_KEY (IMPORTANTE en producción):
En `app/services/auth_service.py`:
```python
SECRET_KEY = "tu_clave_secreta_super_segura"
```

## Archivos Creados

```
app/
├── models/
│   ├── database_models.py      # + Modelo User
│   └── schemas.py               # + Schemas de auth
├── services/
│   └── auth_service.py          # NUEVO - Servicio de autenticación
├── api/
│   └── routes/
│       └── auth.py              # NUEVO - Endpoints de auth
└── main.py                      # Modificado - Incluye rutas de auth

alembic/
└── versions/
    └── 79fc21215224_add_users_table.py  # Nueva migración

examples/
└── test_auth.html               # NUEVO - Interfaz de prueba

requirements.txt                 # + passlib[bcrypt], python-jose
```

## Flujo de Autenticación

```
1. Usuario → POST /auth/register → BD (hash password)
   ↓
2. Usuario → POST /auth/login → Verifica credenciales
   ↓
3. Backend → Genera JWT token → Usuario
   ↓
4. Usuario → Requests con token en header → Endpoints protegidos
   ↓
5. Backend → Verifica token → Permite/Deniega acceso
```

## Próximos Pasos (Opcionales)

- Middleware para proteger endpoints automáticamente
- Refresh tokens
- Roles y permisos
- Reset de contraseña
- Límite de intentos de login
- Logs de actividad de usuarios

## Testing Rápido

```bash
# Terminal 1: Iniciar servidor
venv\Scripts\activate
python -m app.main

# Terminal 2: Probar endpoints
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin", "password":"admin123"}'
```

O simplemente abre `examples/test_auth.html` en tu navegador! 🎉
