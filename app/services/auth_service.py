"""
Servicio de autenticación y gestión de usuarios.
"""

from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.models.database_models import User
from app.utils.logger import logger


# Configuración de seguridad
SECRET_KEY = "visionai_secret_key_2025_change_this_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

# Contexto para hashear contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
        """Crea un token JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verifica y decodifica un token JWT"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError as e:
            logger.error(f"Error al verificar token: {e}")
            return None

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
