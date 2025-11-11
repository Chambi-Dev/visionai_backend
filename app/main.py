from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import predictions
from app.utils.logger import logger

# Crear instancia de FastAPI
app = FastAPI(
    title="VisionAI Backend",
    description="API para predicción de emociones faciales con IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(predictions.router, prefix="/api/v1", tags=["Predictions"])


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Bienvenido a VisionAI Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
        "endpoints": {
            "predict": "/api/v1/predict",
            "emotions": "/api/v1/emotions",
            "model_info": "/api/v1/model/info",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "VisionAI Backend"
    }

@app.on_event("startup")
async def startup_event():
    """Evento al iniciar la aplicación"""
    logger.info(" VisionAI Backend iniciando...")
    
    # Precarga del modelo ML
    try:
        from app.services.ml_service import ml_service
        model_info = ml_service.get_model_info()
        logger.info(f" Modelo cargado: {model_info.get('status')}")
    except Exception as e:
        logger.error(f" Error al cargar modelo: {e}")
    
    logger.info(" VisionAI Backend iniciado correctamente")

@app.on_event("shutdown")
async def shutdown_event():
    """Evento al cerrar la aplicación"""
    logger.info(" VisionAI Backend detenido")

