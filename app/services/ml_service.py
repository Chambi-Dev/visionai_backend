"""
Servicio de Machine Learning para predicción de emociones.
Maneja la carga del modelo y las predicciones.
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from typing import Tuple, Optional
import os
from pathlib import Path
from app.config.settings import settings
from app.utils.logger import logger


class MLService:
    """
    Servicio Singleton para gestionar el modelo de ML.
    Carga el modelo una sola vez y lo mantiene en memoria.
    """
    
    _instance = None
    _model = None
    
    # Mapeo de índices a nombres de emociones (debe coincidir con tu entrenamiento)
    EMOTION_CLASSES = [
        'angry',      # 0
        'disgust',    # 1
        'fear',       # 2
        'happy',      # 3
        'neutral',    # 4
        'sad',        # 5
        'surprise'    # 6
    ]
    
    def __new__(cls):
        """Implementación del patrón Singleton"""
        if cls._instance is None:
            cls._instance = super(MLService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Constructor - carga el modelo si no está cargado"""
        if self._model is None:
            self._load_model()
    
    def _load_model(self) -> None:
        """
        Carga el modelo Keras desde el archivo.
        
        Raises:
            FileNotFoundError: Si el modelo no existe
            Exception: Si hay error al cargar el modelo
        """
        # Construir ruta absoluta al modelo
        base_dir = Path(__file__).resolve().parent.parent.parent
        model_path = base_dir / settings.MODEL_PATH
        
        if not model_path.exists():
            logger.error(f"Modelo no encontrado en: {model_path}")
            raise FileNotFoundError(f"Modelo no encontrado: {model_path}")
        
        try:
            logger.info(f"Cargando modelo desde: {model_path}")
            
            # Keras 3.x requiere formato ZIP para .keras
            # Si es HDF5, usar load_model con safe_mode=False
            try:
                self._model = tf.keras.models.load_model(
                    str(model_path),
                    compile=False,
                    safe_mode=False
                )
            except Exception as e_keras3:
                # Fallback: intentar con h5py para modelos antiguos
                logger.warning(f"Intento Keras 3 falló, usando h5: {e_keras3}")
                import h5py
                self._model = tf.keras.models.load_model(
                    str(model_path),
                    compile=False
                )
            
            logger.info("Modelo cargado exitosamente")
            
            # Verificar arquitectura del modelo
            input_shape = self._model.input_shape
            output_shape = self._model.output_shape
            
            logger.info(f"Input shape: {input_shape}")
            logger.info(f"Output shape: {output_shape}")
            
            # Validar que coincida con lo esperado
            if input_shape != (None, 96, 96, 3):
                logger.warning(f"Input shape inesperado: {input_shape}")
            
            if output_shape != (None, 7):
                logger.warning(f"Output shape inesperado: {output_shape}")
                
        except Exception as e:
            logger.error(f"Error al cargar el modelo: {e}")
            raise Exception(f"Error al cargar el modelo: {e}")
    
    def predict(self, image_array: np.ndarray) -> Tuple[str, float, np.ndarray]:
        """
        Realiza una predicción de emoción sobre una imagen procesada.
        
        Args:
            image_array: Array numpy con shape (1, 96, 96, 3) normalizado [0-1]
        
        Returns:
            Tuple con:
                - emotion_name (str): Nombre de la emoción predicha
                - confidence (float): Confianza de la predicción [0-1]
                - all_probabilities (np.ndarray): Todas las probabilidades por clase
        
        Raises:
            ValueError: Si el array tiene formato incorrecto
            Exception: Si hay error durante la predicción
        """
        if self._model is None:
            logger.error("Modelo no está cargado")
            raise Exception("Modelo no inicializado")
        
        # Validar shape del input
        if image_array.shape != (1, 96, 96, 3):
            logger.error(f"Shape incorrecto: {image_array.shape}, esperado: (1, 96, 96, 3)")
            raise ValueError(
                f"Shape de imagen incorrecto: {image_array.shape}. "
                f"Esperado: (1, 96, 96, 3)"
            )
        
        # Validar rango de valores
        if image_array.min() < 0 or image_array.max() > 1:
            logger.warning(
                f"Valores fuera de rango [0-1]: min={image_array.min()}, "
                f"max={image_array.max()}"
            )
        
        try:
            # Hacer predicción
            predictions = self._model.predict(image_array, verbose=0)
            
            # Obtener clase con mayor probabilidad
            predicted_class_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class_idx])
            emotion_name = self.EMOTION_CLASSES[predicted_class_idx]
            
            logger.info(
                f"Predicción: {emotion_name} con confianza {confidence:.4f}"
            )
            
            # Log de todas las probabilidades (útil para debugging)
            for idx, prob in enumerate(predictions[0]):
                logger.debug(f"  {self.EMOTION_CLASSES[idx]}: {prob:.4f}")
            
            return emotion_name, confidence, predictions[0]
            
        except Exception as e:
            logger.error(f"Error durante la predicción: {e}")
            raise Exception(f"Error en predicción: {e}")
    
    def get_model_info(self) -> dict:
        """
        Obtiene información sobre el modelo cargado.
        
        Returns:
            dict: Información del modelo (arquitectura, params, etc.)
        """
        if self._model is None:
            return {"status": "not_loaded"}
        
        try:
            return {
                "status": "loaded",
                "model_path": settings.MODEL_PATH,
                "input_shape": str(self._model.input_shape),
                "output_shape": str(self._model.output_shape),
                "num_layers": len(self._model.layers),
                "total_params": self._model.count_params(),
                "emotion_classes": self.EMOTION_CLASSES
            }
        except Exception as e:
            logger.error(f"Error al obtener info del modelo: {e}")
            return {"status": "error", "error": str(e)}
    
    def reload_model(self) -> None:
        """
        Recarga el modelo desde el disco.
        Útil si se actualiza el modelo sin reiniciar el servidor.
        """
        logger.info("Recargando modelo...")
        self._model = None
        self._load_model()
        logger.info(" Modelo recargado exitosamente")


# Instancia global del servicio (Singleton)
ml_service = MLService()
