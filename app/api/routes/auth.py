"""
Endpoints de autenticación y gestión de usuarios.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie, Header
from sqlalchemy.orm import Session
from datetime import timedelta

from app.api.dependencies import get_db
from app.services.auth_service import auth_service
from app.config.settings import settings
from app.models.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token
)
from app.utils.logger import logger


router = APIRouter()


@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description="Crea una nueva cuenta de usuario con username y contraseña, y retorna tokens de acceso"
)
async def register_user(
    user: UserCreate,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    **Registra un nuevo usuario en el sistema y retorna tokens de acceso.**
    
    - **username**: Nombre de usuario único (3-50 caracteres)
    - **password**: Contraseña (mínimo 6 caracteres)
    
    Returns:
        Access token en response body + Refresh token en httpOnly cookie
        
    **Mejor UX:** Usuario queda automáticamente autenticado después del registro
    """
    # Verificar si el usuario ya existe
    existing_user = auth_service.get_user_by_username(db, user.username)
    if existing_user:
        logger.warning(f"Intento de registro con username existente: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El username ya está registrado"
        )
    
    # Crear nuevo usuario
    try:
        db_user = auth_service.create_user(
            db=db,
            username=user.username,
            password=user.password
        )
        logger.info(f"Usuario registrado: {user.username}")
        
        # Crear tokens para el nuevo usuario (auto-login después del registro)
        tokens = auth_service.create_tokens(user.username)
        
        # Configurar refresh token en httpOnly cookie
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh_token"],
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            path="/api/v1/auth/refresh"
        )
        
        logger.info(f"Usuario autenticado automáticamente: {user.username}")
        
        # Retornar access token en body
        return {
            "access_token": tokens["access_token"],
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except Exception as e:
        logger.error(f"Error al registrar usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el usuario"
        )


@router.post(
    "/login",
    response_model=Token,
    summary="Iniciar sesión",
    description="Autenticar usuario y obtener token JWT"
)
async def login(
    credentials: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    **Autentica un usuario y genera tokens de acceso.**
    
    - **username**: Nombre de usuario
    - **password**: Contraseña
    
    Returns:
        Access token en response body + Refresh token en httpOnly cookie
        
    **Modern JWT Flow:**
    - Access token: En response body (úsalo en Authorization: Bearer <token>)
    - Refresh token: En httpOnly cookie (automático, protegido de XSS)
    """
    # Autenticar usuario
    user = auth_service.authenticate_user(
        db=db,
        username=credentials.username,
        password=credentials.password
    )
    
    if not user:
        logger.warning(f"Intento de login fallido: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear tokens (access y refresh)
    tokens = auth_service.create_tokens(user.username)
    
    logger.info(f"Login exitoso: {credentials.username}")
    
    # MODERN JWT FLOW:
    # 1. Refresh token en httpOnly cookie (seguro, no accesible por JS)
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,   # JavaScript no puede leerlo (protección XSS)
        secure=True,     # Solo HTTPS en producción
        samesite="lax",  # Protección CSRF
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/api/v1/auth/refresh"  # Solo se envía a endpoint de refresh
    )
    
    # 2. Access token en response body (cliente lo usa en Authorization header)
    return {
        "access_token": tokens["access_token"],
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.get(
    "/verify",
    response_model=UserResponse,
    summary="Verificar token",
    description="Verifica que el token sea válido y retorna info del usuario"
)
async def verify_token(
    authorization: str = Header(..., description="Bearer token"),
    db: Session = Depends(get_db)
):
    """
    **Verifica un token JWT y retorna información del usuario.**
    
    Requiere header: `Authorization: Bearer <token>`
    
    Returns:
        Información del usuario si el token es válido
    """
    # Extraer token del header "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de Authorization header inválido. Use: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = parts[1]
    
    # Verificar token
    payload = auth_service.verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Obtener username del token
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    # Obtener usuario de la BD
    user = auth_service.get_user_by_username(db, username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    return user


@router.post(
    "/refresh",
    response_model=Token,
    summary="Renovar tokens",
    description="Obtiene nuevos access y refresh tokens usando el refresh token en cookie"
)
async def refresh_access_token(
    response: Response,
    refresh_token: str = Cookie(None),
    db: Session = Depends(get_db)
):
    """
    **Renueva ambos tokens usando el refresh token de la cookie.**
    
    MODERN JWT FLOW:
    - Lee refresh token de httpOnly cookie (automático)
    - Genera NUEVO access token
    - Genera NUEVO refresh token (token rotation)
    - Retorna access token en body
    - Retorna refresh token en httpOnly cookie
    
    Esto implementa "refresh token rotation" para mayor seguridad.
    
    Returns:
        Nuevo access token en body y nuevo refresh token en cookie
    """
    # Verificar que existe refresh token en cookie
    if not refresh_token:
        logger.warning("Intento de refresh sin cookie")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token no encontrado. Por favor, inicia sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar refresh token
    payload = auth_service.verify_refresh_token(refresh_token)
    if payload is None:
        logger.warning("Intento de refresh con token inválido")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado. Por favor, inicia sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Obtener username del token
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido"
        )
    
    # Verificar que el usuario existe y está activo
    user = auth_service.get_user_by_username(db, username)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo"
        )
    
    # Crear NUEVOS tokens (token rotation para mayor seguridad)
    new_tokens = auth_service.create_tokens(username)
    
    # Actualizar refresh token en cookie
    response.set_cookie(
        key="refresh_token",
        value=new_tokens["refresh_token"],
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/api/v1/auth/refresh"
    )
    
    logger.info(f"Tokens renovados para: {username}")
    
    # Retornar nuevo access token en body
    return {
        "access_token": new_tokens["access_token"],
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post(
    "/logout",
    summary="Cerrar sesión",
    description="Limpia el refresh token de la cookie y el access token del cliente"
)
async def logout(response: Response):
    """
    **Cierra la sesión del usuario.**
    
    - Elimina refresh token de la cookie httpOnly
    - El cliente debe eliminar el access token de memoria/localStorage
    """
    response.delete_cookie(key="refresh_token", path="/api/v1/auth/refresh")
    logger.info("Usuario cerró sesión (refresh token eliminado)")
    return {"message": "Logged out successfully"}


@router.get(
    "/users/me",
    response_model=UserResponse,
    summary="Obtener perfil del usuario actual",
    description="Retorna información del usuario autenticado (requiere token)"
)
async def get_user_profile(
    authorization: str = Header(..., description="Bearer token"),
    db: Session = Depends(get_db)
):
    """
    **Obtiene el perfil del usuario autenticado.**
    
    Requiere header: `Authorization: Bearer <token>`
    """
    return await verify_token(authorization, db)
