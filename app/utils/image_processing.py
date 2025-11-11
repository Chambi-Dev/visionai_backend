from PIL import Image
import numpy as np
import io
from app.utils.logger import logger

async def preprocess_image(image_bytes: bytes ) -> np.ndarray:

    #tomas los bytes de la imagen y la abre con pil , la converte a RGB
    #luego lo redimenciona a 96x96  y normaliza para el modelo

    try:
        image = Image.open(io.BytesIO(image_bytes))

        image = image.convert("RGB")

        processed_image = image.resize((96, 96))

        img_array = np.array(processed_image) / 255.0

        return np.expand_dims(img_array, axis=0)  # Shape: (1, 96, 96, 3)
    except Exception as e:
        logger.error(f"Error al procesar la imagen: {e}")
        raise ValueError("No se pudo procesar la imagen proporcionada.")
        
    
