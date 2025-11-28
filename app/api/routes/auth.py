"""
Endpoints de autenticación y gestión de usuarios.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.api.dependencies import get_db
from app.services.auth_service import auth_service, ACCESS_TOKEN_EXPIRE_MINUTES
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
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description="Crea una nueva cuenta de usuario con username y contraseña"
)
async def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    **Registra un nuevo usuario en el sistema.**
    
    - **username**: Nombre de usuario único (3-50 caracteres)
    - **password**: Contraseña (mínimo 6 caracteres)
    
    Returns:
        Información del usuario creado (sin contraseña)
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
        return db_user
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
    db: Session = Depends(get_db)
):
    """
    **Autentica un usuario y genera un token de acceso.**
    
    - **username**: Nombre de usuario
    - **password**: Contraseña
    
    Returns:
        Token JWT para autenticación en endpoints protegidos
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
    
    # Crear token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    logger.info(f"Login exitoso: {credentials.username}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get(
    "/verify",
    response_model=UserResponse,
    summary="Verificar token",
    description="Verifica que el token sea válido y retorna info del usuario"
)
async def verify_token(
    token: str,
    db: Session = Depends(get_db)
):
    """
    **Verifica un token JWT y retorna información del usuario.**
    
    - **token**: Token JWT a verificar
    
    Returns:
        Información del usuario si el token es válido
    """
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


@router.get(
    "/users/me",
    response_model=UserResponse,
    summary="Obtener perfil del usuario actual",
    description="Retorna información del usuario autenticado (requiere token)"
)
async def get_current_user(
    token: str,
    db: Session = Depends(get_db)
):
    """
    **Obtiene el perfil del usuario autenticado.**
    
    Requiere token JWT en el header Authorization: Bearer <token>
    """
    return await verify_token(token, db)
