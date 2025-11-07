# app/config/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base # <-- IMPORTA ESTO
from .settings import settings # Importa tus configuraciones (donde está la DB_URL)

# Asegúrate de que tu settings.py tenga la variable DATABASE_URL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL 

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- ESTA ES LA LÍNEA QUE FALTA ---
# Aquí creas la clase Base de la que heredarán todos tus modelos
Base = declarative_base()
# --- ---

# Función de dependencia para usar en las rutas de FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()