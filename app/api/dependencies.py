"""
Dependencias inyectables para FastAPI.
"""

from typing import Generator, Optional
from sqlalchemy.orm import Session
from fastapi import Header
from app.config.database import SessionLocal
from app.services.auth_service import auth_service
from app.utils.logger import logger


def get_db() -> Generator[Session, None, None]:
    """
    Dependencia para obtener una sesión de base de datos.
    
    Yields:
        Session: Sesión de SQLAlchemy
    
    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_optional(
    authorization: Optional[str] = Header(None)
) -> Optional[str]:
    """
    Dependencia opcional para obtener el usuario autenticado.
    Si hay token, lo valida y retorna el username.
    Si no hay token o es inválido, retorna None.
    
    Args:
        authorization: Header Authorization con Bearer token
    
    Returns:
        Username del usuario autenticado o None
    """
    if not authorization:
        return None
    
    # Extraer token del header "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning("Formato de Authorization header inválido")
        return None
    
    token = parts[1]
    payload = auth_service.verify_token(token)
    
    if not payload:
        logger.warning("Token JWT inválido")
        return None
    
    username = payload.get("sub")
    logger.info(f"Usuario autenticado: {username}")
    return username
