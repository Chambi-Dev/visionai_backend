from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Crear instancia de FastAPI
app = FastAPI(
    title="VisionAI Backend",
    description="API para predicción de emociones con IA",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar routers (comentado hasta que estén implementados)
# from app.api.routes import health, predictions, dashboard
# app.include_router(health.router, tags=["Health"])
# app.include_router(predictions.router, prefix="/api/v1", tags=["Predictions"])
# app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Bienvenido a VisionAI Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
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
    print("🚀 VisionAI Backend iniciado correctamente")

@app.on_event("shutdown")
async def shutdown_event():
    """Evento al cerrar la aplicación"""
    print("👋 VisionAI Backend detenido")
