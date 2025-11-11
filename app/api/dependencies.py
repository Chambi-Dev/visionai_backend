"""
Dependencias inyectables para FastAPI.
"""

from typing import Generator
from sqlalchemy.orm import Session
from app.config.database import SessionLocal


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
