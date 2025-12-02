# 📊 VisionAI Statistics API Guide

This guide documents all statistics endpoints available in the VisionAI emotion prediction system.

## Overview

The API provides two types of endpoints:
- **Public Stats**: Accessible by anyone, provides global system statistics
- **Private Stats**: Require authentication, provides personal user statistics

Base URL: `/api/v1/stats`

---

## 🌍 Public Endpoints (No Authentication Required)

### 1. Global Statistics
**GET** `/stats/global`

Returns overall system statistics.

**Response:**
```json
{
  "total_predictions": 15234,
  "total_unique_users": 342,
  "total_sessions_today": 45,
  "most_common_emotion": "happy",
  "avg_confidence": 0.87,
  "predictions_last_hour": 23,
  "predictions_today": 456
}
```

**Use case:** Display key metrics on homepage/dashboard

---

### 2. Emotion Distribution
**GET** `/stats/emotions/distribution`

Returns the distribution of all emotions detected.

**Response:**
```json
{
  "total_predictions": 15234,
  "emotions": [
    {
      "emotion_name": "happy",
      "count": 4521,
      "percentage": 29.67
    },
    {
      "emotion_name": "neutral",
      "count": 3842,
      "percentage": 25.21
    },
    {
      "emotion_name": "sad",
      "count": 2910,
      "percentage": 19.10
    }
  ]
}
```

**Use case:** Pie chart or donut chart showing emotion distribution

---

### 3. Prediction Trends
**GET** `/stats/trends?days=7`

Returns daily prediction statistics over time.

**Query Parameters:**
- `days` (optional): Number of days to look back (1-90, default: 7)

**Response:**
```json
{
  "period_days": 7,
  "daily_stats": [
    {
      "date": "2025-11-24",
      "total_predictions": 234,
      "unique_users": 45,
      "avg_confidence": 0.85
    },
    {
      "date": "2025-11-25",
      "total_predictions": 189,
      "unique_users": 38,
      "avg_confidence": 0.88
    }
  ]
}
```

**Use case:** Line chart showing prediction trends over time

---

### 4. Hourly Activity
**GET** `/stats/hourly-activity`

Returns prediction distribution by hour of day.

**Response:**
```json
{
  "hourly_distribution": [
    {"hour": 0, "count": 12},
    {"hour": 1, "count": 8},
    {"hour": 2, "count": 5},
    ...
    {"hour": 14, "count": 234},
    {"hour": 15, "count": 198}
  ],
  "peak_hour": 14,
  "peak_hour_count": 234
}
```

**Use case:** Bar chart showing when the system is most active

---

### 5. Emotion Trends
**GET** `/stats/emotions/trends?days=7`

Returns how each emotion has varied over time.

**Query Parameters:**
- `days` (optional): Number of days to look back (1-90, default: 7)

**Response:**
```json
{
  "period_days": 7,
  "trends": [
    {
      "date": "2025-11-24",
      "emotion_name": "happy",
      "count": 67
    },
    {
      "date": "2025-11-24",
      "emotion_name": "sad",
      "count": 45
    },
    {
      "date": "2025-11-25",
      "emotion_name": "happy",
      "count": 72
    }
  ]
}
```

**Use case:** Multi-line chart or stacked area chart showing emotion trends

---

### 6. Performance Metrics
**GET** `/stats/performance`

Returns ML model performance metrics.

**Response:**
```json
{
  "avg_processing_time_ms": 45.32,
  "min_processing_time_ms": 12,
  "max_processing_time_ms": 234,
  "total_predictions_analyzed": 15234
}
```

**Use case:** System performance dashboard

---

## 🔒 Private Endpoints (Authentication Required)

All private endpoints require an `Authorization` header with a valid JWT token:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 1. My Personal Statistics
**GET** `/stats/me`

Returns comprehensive statistics for the authenticated user.

**Headers:**
```
Authorization: Bearer <your_token>
```

**Response:**
```json
{
  "user_id": 42,
  "username": "john_doe",
  "total_predictions": 234,
  "predictions_today": 12,
  "predictions_this_week": 67,
  "predictions_this_month": 189,
  "favorite_emotion": "happy",
  "avg_confidence": 0.89,
  "first_prediction_date": "2025-10-15T14:23:11Z",
  "last_prediction_date": "2025-11-30T09:45:23Z"
}
```

**Use case:** User profile dashboard showing personal statistics

---

### 2. My Daily Activity
**GET** `/stats/me/activity?days=30`

Returns the user's daily prediction activity.

**Query Parameters:**
- `days` (optional): Number of days to look back (1-365, default: 30)

**Headers:**
```
Authorization: Bearer <your_token>
```

**Response:**
```json
{
  "period_days": 30,
  "daily_activity": [
    {
      "date": "2025-11-01",
      "prediction_count": 5
    },
    {
      "date": "2025-11-02",
      "prediction_count": 8
    },
    {
      "date": "2025-11-03",
      "prediction_count": 12
    }
  ],
  "total_predictions": 234
}
```

**Use case:** Calendar heatmap or line chart showing user's activity pattern

---

### 3. My Emotion Breakdown
**GET** `/stats/me/emotions`

Returns the breakdown of emotions detected for the user.

**Headers:**
```
Authorization: Bearer <your_token>
```

**Response:**
```json
{
  "total_predictions": 234,
  "emotions": [
    {
      "emotion_name": "happy",
      "count": 89,
      "percentage": 38.03,
      "avg_confidence": 0.91
    },
    {
      "emotion_name": "neutral",
      "count": 67,
      "percentage": 28.63,
      "avg_confidence": 0.88
    },
    {
      "emotion_name": "surprised",
      "count": 45,
      "percentage": 19.23,
      "avg_confidence": 0.85
    }
  ],
  "most_frequent_emotion": "happy"
}
```

**Use case:** Personal emotion distribution pie chart

---

### 4. My Recent Predictions
**GET** `/stats/me/recent?limit=20`

Returns the user's most recent predictions.

**Query Parameters:**
- `limit` (optional): Number of predictions to return (1-100, default: 20)

**Headers:**
```
Authorization: Bearer <your_token>
```

**Response:**
```json
{
  "count": 20,
  "predictions": [
    {
      "predic_id": 15234,
      "emotion_name": "happy",
      "confidence": 0.92,
      "timestamp": "2025-11-30T10:23:45Z",
      "processing_time_ms": 42
    },
    {
      "predic_id": 15233,
      "emotion_name": "neutral",
      "confidence": 0.87,
      "timestamp": "2025-11-30T10:20:12Z",
      "processing_time_ms": 38
    }
  ]
}
```

**Use case:** Recent activity feed or history table

---

## 🔐 Authentication

To access private endpoints, you need to:

1. **Register a user:**
   ```bash
   POST /api/v1/auth/register
   {
     "username": "your_username",
     "password": "your_password"
   }
   ```

2. **Login to get a token:**
   ```bash
   POST /api/v1/auth/login
   {
     "username": "your_username",
     "password": "your_password"
   }
   ```

3. **Use the token in requests:**
   ```bash
   curl -H "Authorization: Bearer <your_token>" \
        http://localhost:8000/api/v1/stats/me
   ```

---

## 📊 Frontend Integration Examples

### React Example (Public Stats)

```javascript
// Fetch global statistics
async function fetchGlobalStats() {
  const response = await fetch('http://localhost:8000/api/v1/stats/global');
  const data = await response.json();
  return data;
}

// Fetch emotion distribution for pie chart
async function fetchEmotionDistribution() {
  const response = await fetch('http://localhost:8000/api/v1/stats/emotions/distribution');
  const data = await response.json();
  return data;
}
```

### React Example (Private Stats with Auth)

```javascript
// Fetch user's personal stats
async function fetchMyStats(token) {
  const response = await fetch('http://localhost:8000/api/v1/stats/me', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  const data = await response.json();
  return data;
}

// Fetch user's activity for last 30 days
async function fetchMyActivity(token, days = 30) {
  const response = await fetch(
    `http://localhost:8000/api/v1/stats/me/activity?days=${days}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  const data = await response.json();
  return data;
}
```

### Chart.js Integration Example

```javascript
// Display emotion distribution as pie chart
async function displayEmotionChart() {
  const data = await fetchEmotionDistribution();
  
  new Chart(ctx, {
    type: 'pie',
    data: {
      labels: data.emotions.map(e => e.emotion_name),
      datasets: [{
        data: data.emotions.map(e => e.count),
        backgroundColor: [
          '#FF6384', '#36A2EB', '#FFCE56', 
          '#4BC0C0', '#9966FF', '#FF9F40'
        ]
      }]
    }
  });
}
```

---

## 🚀 Quick Start

1. Start the server:
   ```bash
   cd visionai_backend
   uvicorn app.main:app --reload
   ```

2. Visit the interactive API docs:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

3. Test a public endpoint:
   ```bash
   curl http://localhost:8000/api/v1/stats/global
   ```

4. Test a private endpoint:
   ```bash
   # First login
   TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"your_user","password":"your_pass"}' \
     | jq -r '.access_token')
   
   # Then use the token
   curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/stats/me
   ```

---

## 📈 Recommended Chart Types

| Endpoint | Best Chart Type |
|----------|----------------|
| Global Stats | KPI Cards/Metrics |
| Emotion Distribution | Pie/Donut Chart |
| Prediction Trends | Line Chart |
| Hourly Activity | Bar Chart |
| Emotion Trends | Multi-line/Stacked Area Chart |
| Performance Metrics | Gauge/Metric Cards |
| User Activity | Calendar Heatmap/Line Chart |
| User Emotions | Pie/Bar Chart |
| Recent Predictions | Table/List |

---

## 🎯 Use Cases

### Dashboard for Admins (Public Stats)
- Show total predictions and users
- Display real-time activity (last hour)
- Show emotion distribution
- Performance metrics

### User Profile Page (Private Stats)
- User's total predictions
- Predictions today/week/month
- Personal emotion distribution
- Activity calendar

### Analytics Page (Public Stats)
- Trends over time
- Peak activity hours
- Emotion trends by day
- System performance

---

## 🔧 Error Handling

All endpoints return standard HTTP status codes:

- **200 OK**: Success
- **401 Unauthorized**: Missing or invalid token (private endpoints)
- **403 Forbidden**: User account is inactive
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## 📝 Notes

- All timestamps are in ISO 8601 format (UTC)
- Confidence values are floats between 0.0 and 1.0
- Date fields are strings in YYYY-MM-DD format
- The system tracks both authenticated users and anonymous sessions
- Performance metrics only include predictions where processing time was recorded
