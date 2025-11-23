# Ejemplos de Uso - VisionAI WebSocket

Esta carpeta contiene **ejemplos de clientes** para conectarse al servidor WebSocket.

## 📁 Archivos

- **`websocket_client_example.py`** - Cliente Python de ejemplo
- **`WEBSOCKET_GUIDE.md`** - Guía completa de uso
- **`README_WEBSOCKET.md`** - Documentación resumida

## ⚠️ Importante

Estos archivos son **SOLO PARA PRUEBAS Y DEMOSTRACIÓN**.

**NO son parte de la arquitectura del backend**, son ejemplos para que sepas cómo conectarte desde tu frontend o aplicación cliente.

## 🚀 Uso

```bash
# Desde la raíz del proyecto
python examples/websocket_client_example.py imagen.jpg
```

## 🏗️ Arquitectura Real del Backend

```
visionai_backend/
├── app/                    ← BACKEND (servidor)
│   ├── main.py            ← Servidor WebSocket
│   ├── config/
│   ├── models/
│   ├── services/
│   └── utils/
├── examples/              ← EJEMPLOS (clientes de prueba)
│   ├── websocket_client_example.py
│   └── README.md
└── requirements.txt
```

## 💡 Para Producción

En tu aplicación real (frontend, móvil, etc.), deberás implementar tu propio cliente WebSocket basado en estos ejemplos.
