"""
Configuración del sistema de logging para la aplicación.
"""

import logging
import sys
from pathlib import Path

# Crear directorio de logs si no existe
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configurar el formato de logs
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Configurar el logger principal
logger = logging.getLogger("visionai")
logger.setLevel(logging.DEBUG)

# Handler para consola (stdout)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
console_handler.setFormatter(console_formatter)

# Handler para archivo
file_handler = logging.FileHandler(log_dir / "visionai.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
file_handler.setFormatter(file_formatter)

# Agregar handlers al logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Evitar duplicación de logs
logger.propagate = False
