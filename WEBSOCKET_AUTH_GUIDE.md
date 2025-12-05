# 🔒 WebSocket Authentication Guide

## Overview

The VisionAI WebSocket endpoint (`ws://localhost:8000/ws`) now **requires JWT authentication** for making predictions. This ensures that all real-time emotion predictions are tracked by user.

---

## 🔑 Authentication Flow

```
1. Login via REST API → Get Access Token
2. Connect to WebSocket
3. Send prediction with token in message
4. Receive authenticated prediction result
```

---

## 🚀 Quick Start

### Step 1: Login and Get Token

Use the REST API to authenticate:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"youruser","password":"yourpass"}'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Step 2: Connect to WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Connected to WebSocket');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

### Step 3: Send Prediction with Token

```javascript
const accessToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...";

// Capture image from camera
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');
ctx.drawImage(videoElement, 0, 0);
const imageBase64 = canvas.toDataURL('image/jpeg').split(',')[1];

// Send prediction request with token
ws.send(JSON.stringify({
  command: "predict",
  image: imageBase64,
  token: accessToken  // 🔑 REQUIRED
}));
```

### Step 4: Handle Response

```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'prediction' && data.status === 'success') {
    console.log('Emotion:', data.emotion_name);
    console.log('Confidence:', data.confidence);
    console.log('User ID:', data.user_id);
  } else if (data.type === 'error') {
    console.error('Error:', data.message);
    if (data.code === 'AUTH_REQUIRED') {
      // User not authenticated
      redirectToLogin();
    } else if (data.code === 'INVALID_TOKEN') {
      // Token expired, refresh it
      refreshToken();
    }
  }
};
```

---

## 📡 WebSocket Commands

### 🔒 `predict` - Make Prediction (AUTH REQUIRED)

**Request:**
```json
{
  "command": "predict",
  "image": "base64_encoded_image_data",
  "token": "your_jwt_access_token"
}
```

**Success Response:**
```json
{
  "type": "prediction",
  "status": "success",
  "emotion_name": "happy",
  "confidence": 95.67,
  "model_version_tag": "v1.0",
  "processing_time_ms": 45,
  "timestamp": "2025-12-02T10:30:00",
  "user_id": 123
}
```

**Error Responses:**

Missing token:
```json
{
  "type": "error",
  "message": "Autenticación requerida. Incluye 'token' en el mensaje.",
  "code": "AUTH_REQUIRED"
}
```

Invalid/Expired token:
```json
{
  "type": "error",
  "message": "Token inválido o expirado. Por favor, inicia sesión nuevamente.",
  "code": "INVALID_TOKEN"
}
```

---

### ✅ `health` - Health Check (PUBLIC)

**Request:**
```json
{
  "command": "health"
}
```

**Response:**
```json
{
  "type": "health",
  "status": "healthy",
  "service": "VisionAI WebSocket",
  "timestamp": "2025-12-02T10:30:00",
  "clients_connected": 5
}
```

---

### 📊 `model_info` - Get Model Info (PUBLIC)

**Request:**
```json
{
  "command": "model_info"
}
```

**Response:**
```json
{
  "type": "model_info",
  "status": "success",
  "info": {
    "version": "v1.0",
    "emotion_classes": ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"],
    "input_shape": [48, 48, 1],
    "model_type": "CNN"
  }
}
```

---

### 📋 `emotions` - List Emotions (PUBLIC)

**Request:**
```json
{
  "command": "emotions"
}
```

**Response:**
```json
{
  "type": "emotions",
  "status": "success",
  "emotions": [
    {"id": 1, "name": "angry", "description": "Enojo"},
    {"id": 2, "name": "disgust", "description": "Disgusto"},
    ...
  ]
}
```

---

## 💻 Implementation Examples

### Python Client

```python
import asyncio
import websockets
import json
import base64
import requests

# 1. Login
def get_token():
    response = requests.post(
        "http://localhost:8000/api/v1/auth/login",
        json={"username": "myuser", "password": "mypass"}
    )
    return response.json()["access_token"]

# 2. WebSocket with Auth
async def predict_with_auth(image_path):
    token = get_token()
    
    # Read image
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()
    
    # Connect to WebSocket
    async with websockets.connect("ws://localhost:8000/ws") as ws:
        # Skip welcome message
        await ws.recv()
        
        # Send prediction with token
        await ws.send(json.dumps({
            "command": "predict",
            "image": image_b64,
            "token": token
        }))
        
        # Get result
        result = json.loads(await ws.recv())
        return result

# Run
result = asyncio.run(predict_with_auth("face.jpg"))
print(f"Emotion: {result['emotion_name']}")
```

---

### JavaScript/Next.js Client

```typescript
// lib/websocket-client.ts
import { useEffect, useState, useRef } from 'react';

export function useAuthenticatedWebSocket(accessToken: string | null) {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const reconnectTimeout = useRef<NodeJS.Timeout>();

  useEffect(() => {
    if (!accessToken) return;

    const websocket = new WebSocket('ws://localhost:8000/ws');

    websocket.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'connection') {
        console.log('Connected:', data.message);
      }
    };

    websocket.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
      
      // Auto-reconnect after 3 seconds
      reconnectTimeout.current = setTimeout(() => {
        console.log('Reconnecting...');
      }, 3000);
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    setWs(websocket);

    return () => {
      websocket.close();
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
    };
  }, [accessToken]);

  const predict = async (imageBase64: string) => {
    if (!ws || !connected || !accessToken) {
      throw new Error('WebSocket not connected or no token');
    }

    return new Promise((resolve, reject) => {
      const messageHandler = (event: MessageEvent) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'prediction') {
          ws.removeEventListener('message', messageHandler);
          resolve(data);
        } else if (data.type === 'error') {
          ws.removeEventListener('message', messageHandler);
          reject(new Error(data.message));
        }
      };

      ws.addEventListener('message', messageHandler);

      ws.send(JSON.stringify({
        command: 'predict',
        image: imageBase64,
        token: accessToken
      }));
    });
  };

  return { ws, connected, predict };
}
```

**Usage in Component:**

```typescript
// components/CameraPredictor.tsx
'use client';

import { useAuthenticatedWebSocket } from '@/lib/websocket-client';
import { useEffect, useRef, useState } from 'react';

export default function CameraPredictor({ accessToken }: { accessToken: string }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [emotion, setEmotion] = useState<string>('');
  
  const { connected, predict } = useAuthenticatedWebSocket(accessToken);

  useEffect(() => {
    // Start camera
    navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    });
  }, []);

  const captureAndPredict = async () => {
    if (!videoRef.current || !canvasRef.current || !connected) return;

    const canvas = canvasRef.current;
    const video = videoRef.current;
    const ctx = canvas.getContext('2d');
    
    if (!ctx) return;

    // Capture frame
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0);

    // Convert to base64
    const imageBase64 = canvas.toDataURL('image/jpeg').split(',')[1];

    try {
      const result = await predict(imageBase64);
      setEmotion(`${result.emotion_name} (${result.confidence.toFixed(1)}%)`);
    } catch (error) {
      console.error('Prediction error:', error);
    }
  };

  return (
    <div>
      <video ref={videoRef} autoPlay />
      <canvas ref={canvasRef} style={{ display: 'none' }} />
      <button onClick={captureAndPredict} disabled={!connected}>
        {connected ? 'Predict Emotion' : 'Connecting...'}
      </button>
      {emotion && <p>Emotion: {emotion}</p>}
    </div>
  );
}
```

---

## 🔄 Token Refresh Strategy

Since access tokens expire after 30 minutes:

### Option 1: Refresh Before Expiration

```javascript
let accessToken = null;
let tokenExpiresAt = null;

async function ensureValidToken() {
  const now = Date.now();
  
  // Refresh if token expires in less than 5 minutes
  if (!tokenExpiresAt || tokenExpiresAt - now < 5 * 60 * 1000) {
    const response = await fetch('/api/v1/auth/refresh', {
      method: 'POST',
      credentials: 'include' // Send refresh token cookie
    });
    
    const data = await response.json();
    accessToken = data.access_token;
    tokenExpiresAt = now + (data.expires_in * 1000);
  }
  
  return accessToken;
}

// Before each prediction
const token = await ensureValidToken();
ws.send(JSON.stringify({
  command: 'predict',
  image: imageBase64,
  token: token
}));
```

### Option 2: Refresh on INVALID_TOKEN Error

```javascript
ws.onmessage = async (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'error' && data.code === 'INVALID_TOKEN') {
    // Token expired, refresh it
    const newToken = await refreshAccessToken();
    
    // Retry prediction with new token
    ws.send(JSON.stringify({
      command: 'predict',
      image: lastImage,
      token: newToken
    }));
  }
};
```

---

## 🛡️ Security Best Practices

1. **Never expose tokens in URL** - Always send in message body
2. **Use HTTPS/WSS in production** - Encrypt WebSocket connection
3. **Implement token refresh** - Don't let users get disconnected
4. **Handle AUTH_REQUIRED errors** - Redirect to login
5. **Clear tokens on logout** - Both access and refresh
6. **Validate token on backend** - Already implemented ✅

---

## 🧪 Testing

Run the test client:

```bash
python examples/websocket_authenticated_client.py
```

This will test:
- ✅ Login and token retrieval
- ✅ WebSocket connection
- ✅ Prediction without token (should fail)
- ✅ Prediction with invalid token (should fail)
- ✅ Prediction with valid token (should succeed)
- ✅ Public commands (health, model_info)

---

## 📊 Error Codes Reference

| Code | Description | Action |
|------|-------------|--------|
| `AUTH_REQUIRED` | No token provided | Prompt user to login |
| `INVALID_TOKEN` | Token invalid/expired | Refresh token or re-login |
| `USER_NOT_FOUND` | User doesn't exist | Re-login |

---

## ✅ Summary

- **Predictions**: Require JWT token in each message
- **Public commands**: `health`, `model_info`, `emotions` - no auth needed
- **Token lifetime**: 30 minutes (refresh before expiration)
- **User tracking**: All predictions logged with user_id
- **Security**: Industry-standard JWT authentication

Your WebSocket is now secure and production-ready! 🎉
