"""
Servicio de autenticación y gestión de usuarios.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.models.database_models import User
from app.config.settings import settings
from app.utils.logger import logger


# Contexto para hashear contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Exportar constantes para retrocompatibilidad
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


class AuthService:
    """Servicio para autenticación y gestión de usuarios"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica que la contraseña coincida con el hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Genera hash de contraseña"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Crea un token JWT de acceso
        
        Args:
            data: Datos a incluir en el token (ej: {"sub": username})
            expires_delta: Tiempo de expiración personalizado
            
        Returns:
            Token JWT codificado
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({
            "exp": expire,
            "type": "access"
        })
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def create_refresh_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Crea un token JWT de refresh (mayor duración)
        
        Args:
            data: Datos a incluir en el token (ej: {"sub": username})
            expires_delta: Tiempo de expiración personalizado
            
        Returns:
            Refresh token JWT codificado
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        to_encode.update({
            "exp": expire,
            "type": "refresh"
        })
        encoded_jwt = jwt.encode(
            to_encode,
            settings.REFRESH_SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """
        Verifica y decodifica un token JWT de acceso
        
        Args:
            token: Token JWT a verificar
            
        Returns:
            Payload del token si es válido, None si es inválido
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            # Verificar que sea un access token
            if payload.get("type") != "access":
                logger.warning("Token no es de tipo access")
                return None
            return payload
        except JWTError as e:
            logger.error(f"Error al verificar token: {e}")
            return None

    @staticmethod
    def verify_refresh_token(token: str) -> Optional[dict]:
        """
        Verifica y decodifica un token JWT de refresh
        
        Args:
            token: Refresh token JWT a verificar
            
        Returns:
            Payload del token si es válido, None si es inválido
        """
        try:
            payload = jwt.decode(
                token,
                settings.REFRESH_SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            # Verificar que sea un refresh token
            if payload.get("type") != "refresh":
                logger.warning("Token no es de tipo refresh")
                return None
            return payload
        except JWTError as e:
            logger.error(f"Error al verificar refresh token: {e}")
            return None

    @staticmethod
    def create_tokens(username: str) -> Dict[str, str]:
        """
        Crea ambos tokens (access y refresh) para un usuario
        
        Args:
            username: Nombre de usuario
            
        Returns:
            Diccionario con access_token y refresh_token
        """
        access_token = AuthService.create_access_token(
            data={"sub": username}
        )
        refresh_token = AuthService.create_refresh_token(
            data={"sub": username}
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Obtiene un usuario por username"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def create_user(
        db: Session,
        username: str,
        password: str
    ) -> User:
        """Crea un nuevo usuario"""
        hashed_password = AuthService.get_password_hash(password)
        db_user = User(
            username=username,
            hashed_password=hashed_password,
            is_active=True
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"Usuario creado: {username}")
        return db_user

    @staticmethod
    def authenticate_user(
        db: Session,
        username: str,
        password: str
    ) -> Optional[User]:
        """Autentica un usuario"""
        user = AuthService.get_user_by_username(db, username)
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user


# Instancia única del servicio
auth_service = AuthService()
