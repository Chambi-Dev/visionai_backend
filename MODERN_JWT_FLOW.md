# 🔐 Modern JWT Authentication Flow - Implementation Guide

## ✅ The Modern Way (Now Implemented!)

Your backend now implements the **industry-standard secure JWT flow** for Next.js:

```
┌─────────────────────────────────────────────────────────────┐
│  MODERN JWT FLOW                                            │
│  ✅ Access Token → Response Body (client uses it)          │
│  ✅ Refresh Token → httpOnly Cookie (browser manages it)   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Why This Approach?

| Token Type | Storage | Purpose | Exposure |
|------------|---------|---------|----------|
| **Access Token** | Memory/State | API requests | Safe (short-lived: 30min) |
| **Refresh Token** | httpOnly Cookie | Get new tokens | Protected (can't access via JS) |

### Benefits:
- ✅ **Access token in body** - Client can use it in Authorization headers
- ✅ **Refresh token in cookie** - Protected from XSS attacks
- ✅ **Token rotation** - New refresh token on each refresh (extra security)
- ✅ **Automatic refresh** - Cookie sent automatically to `/refresh` endpoint
- ✅ **Best of both worlds** - Security + Flexibility

---

## 🚀 API Flow

### 1. Login (`POST /api/v1/auth/login`)

**Request:**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "mypassword"
}
```

**Response:**
```http
HTTP/1.1 200 OK
Set-Cookie: refresh_token=eyJhbGciOiJIUz...; HttpOnly; Secure; SameSite=Lax; Max-Age=604800; Path=/api/v1/auth/refresh

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**What happens:**
- ✅ Access token returned in **JSON body** (30 min lifetime)
- ✅ Refresh token set in **httpOnly cookie** (7 days lifetime)
- ✅ Cookie only sent to `/api/v1/auth/refresh` (path restriction)

---

### 2. Use Access Token for API Requests

**Request:**
```http
GET /api/v1/stats/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
{
  "user_id": 1,
  "username": "john_doe",
  "total_predictions": 150,
  ...
}
```

---

### 3. Refresh Tokens (`POST /api/v1/auth/refresh`)

**When access token expires (after 30 min), refresh it:**

**Request:**
```http
POST /api/v1/auth/refresh
Cookie: refresh_token=eyJhbGciOiJIUz...
```

**Response:**
```http
HTTP/1.1 200 OK
Set-Cookie: refresh_token=NEW_REFRESH_TOKEN; HttpOnly; Secure; SameSite=Lax; Max-Age=604800; Path=/api/v1/auth/refresh

{
  "access_token": "NEW_ACCESS_TOKEN",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**What happens:**
- ✅ Reads refresh token from **cookie automatically**
- ✅ Generates **NEW access token** (returned in body)
- ✅ Generates **NEW refresh token** (token rotation - more secure!)
- ✅ Updates cookie with new refresh token

---

### 4. Logout (`POST /api/v1/auth/logout`)

**Request:**
```http
POST /api/v1/auth/logout
```

**Response:**
```http
HTTP/1.1 200 OK
Set-Cookie: refresh_token=; Max-Age=0; Path=/api/v1/auth/refresh

{
  "message": "Logged out successfully"
}
```

**What happens:**
- ✅ Clears refresh token cookie
- ✅ Client should delete access token from memory

---

## 💻 Next.js Implementation

### API Client with Automatic Token Refresh

```typescript
// lib/api-client.ts
import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class APIClient {
  private client: AxiosInstance;
  private refreshing: boolean = false;
  private refreshSubscribers: Array<(token: string) => void> = [];

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      withCredentials: true, // ⭐ IMPORTANT: Send cookies with requests
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add access token to requests
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = this.getAccessToken();
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      }
    );

    // Handle 401 and refresh token automatically
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

        // If 401 and not already retrying
        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.refreshing) {
            // Wait for ongoing refresh
            return new Promise((resolve) => {
              this.refreshSubscribers.push((token: string) => {
                if (originalRequest.headers) {
                  originalRequest.headers.Authorization = `Bearer ${token}`;
                }
                resolve(this.client(originalRequest));
              });
            });
          }

          originalRequest._retry = true;
          this.refreshing = true;

          try {
            // Refresh token (cookie sent automatically!)
            const { data } = await axios.post(
              `${API_URL}/auth/refresh`,
              {},
              { withCredentials: true } // Send refresh token cookie
            );

            const newToken = data.access_token;
            this.saveAccessToken(newToken);

            // Notify subscribers
            this.refreshSubscribers.forEach((callback) => callback(newToken));
            this.refreshSubscribers = [];

            // Retry original request with new token
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
            }
            return this.client(originalRequest);
          } catch (refreshError) {
            // Refresh failed, logout
            this.clearAccessToken();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          } finally {
            this.refreshing = false;
          }
        }

        return Promise.reject(error);
      }
    );
  }

  private getAccessToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('access_token');
    }
    return null;
  }

  private saveAccessToken(token: string) {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
    }
  }

  private clearAccessToken() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
    }
  }

  // ==================== AUTH ====================

  async login(username: string, password: string) {
    const { data } = await this.client.post('/auth/login', {
      username,
      password,
    });
    // Save access token (refresh token is in cookie automatically)
    this.saveAccessToken(data.access_token);
    return data;
  }

  async logout() {
    await this.client.post('/auth/logout');
    this.clearAccessToken();
  }

  // ==================== STATS ====================

  async getGlobalStats() {
    const { data } = await this.client.get('/stats/global');
    return data;
  }

  async getMyStats() {
    const { data } = await this.client.get('/stats/me');
    return data;
  }

  // Add more methods...
}

export const apiClient = new APIClient();
```

---

### Usage in Components

```typescript
// app/login/page.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api-client';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.login(username, password);
      // Access token saved in localStorage
      // Refresh token saved in httpOnly cookie
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Username"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      {error && <p>{error}</p>}
      <button type="submit">Login</button>
    </form>
  );
}
```

```typescript
// app/profile/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api-client';

export default function ProfilePage() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      // Access token sent automatically
      // If expired, automatically refreshed with cookie
      const data = await apiClient.getMyStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleLogout = async () => {
    await apiClient.logout();
    window.location.href = '/login';
  };

  if (!stats) return <div>Loading...</div>;

  return (
    <div>
      <h1>Welcome, {stats.username}!</h1>
      <p>Total predictions: {stats.total_predictions}</p>
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}
```

---

## 🔒 Security Features

### ✅ What Makes This Secure:

1. **Refresh Token in httpOnly Cookie**
   - JavaScript cannot access it (XSS protection)
   - Browser manages it automatically
   - Only sent to `/auth/refresh` endpoint

2. **Short-lived Access Token**
   - 30 minutes lifetime
   - If stolen, attacker has limited time
   - Stored in memory/localStorage (acceptable because short-lived)

3. **Token Rotation**
   - New refresh token generated on each refresh
   - Old refresh token becomes invalid
   - Prevents token replay attacks

4. **SameSite Cookie Protection**
   - `SameSite=Lax` prevents CSRF attacks
   - Cookie only sent to your domain

5. **Path Restriction**
   - Cookie only sent to `/api/v1/auth/refresh`
   - Not leaked to other endpoints

---

## 🧪 Testing

### Test Login
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}' \
  -c cookies.txt -v

# Output shows:
# - access_token in JSON body
# - Set-Cookie header with refresh_token
```

### Test API with Access Token
```bash
# Extract access token from response
ACCESS_TOKEN="your_access_token_here"

curl -H "Authorization: Bearer $ACCESS_TOKEN" \
  http://localhost:8000/api/v1/stats/me
```

### Test Token Refresh
```bash
# Refresh (sends cookie automatically)
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -b cookies.txt \
  -c cookies.txt \
  -v

# Output shows:
# - New access_token in JSON body
# - New Set-Cookie header with new refresh_token
```

### Test Logout
```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -b cookies.txt \
  -v
```

---

## 🎯 Key Points

### For Frontend Developers:

1. **Always use `withCredentials: true`** or `credentials: 'include'` in fetch/axios
2. **Store access token in localStorage or React state**
3. **Don't try to access refresh token** - it's httpOnly
4. **Implement automatic refresh** on 401 errors
5. **Call `/auth/logout`** on logout to clear cookie

### Security Checklist:

- ✅ Access token in body (30 min)
- ✅ Refresh token in httpOnly cookie (7 days)
- ✅ Token rotation on refresh
- ✅ SameSite=Lax for CSRF protection
- ✅ Secure flag for HTTPS
- ✅ Path restriction for refresh token
- ✅ Short token lifetimes
- ✅ Automatic token refresh

---

## 🚀 This is Production-Ready!

Your JWT implementation now follows **modern best practices** used by companies like:
- Auth0
- Firebase
- Supabase
- NextAuth.js

Perfect for your Next.js frontend! 🎉
