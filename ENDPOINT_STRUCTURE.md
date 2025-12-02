# VisionAI Statistics API - Endpoint Structure

```
📁 /api/v1/stats
│
├── 🌍 PUBLIC ENDPOINTS (No Auth Required)
│   │
│   ├── GET /global
│   │   ├─> Total predictions
│   │   ├─> Total users
│   │   ├─> Sessions today
│   │   ├─> Most common emotion
│   │   ├─> Average confidence
│   │   ├─> Predictions last hour
│   │   └─> Predictions today
│   │
│   ├── GET /emotions/distribution
│   │   ├─> Total predictions
│   │   └─> Emotions[]
│   │       ├─> emotion_name
│   │       ├─> count
│   │       └─> percentage
│   │
│   ├── GET /trends?days=7
│   │   ├─> period_days
│   │   └─> daily_stats[]
│   │       ├─> date
│   │       ├─> total_predictions
│   │       ├─> unique_users
│   │       └─> avg_confidence
│   │
│   ├── GET /hourly-activity
│   │   ├─> hourly_distribution[]
│   │   │   ├─> hour (0-23)
│   │   │   └─> count
│   │   ├─> peak_hour
│   │   └─> peak_hour_count
│   │
│   ├── GET /emotions/trends?days=7
│   │   ├─> period_days
│   │   └─> trends[]
│   │       ├─> date
│   │       ├─> emotion_name
│   │       └─> count
│   │
│   └── GET /performance
│       ├─> avg_processing_time_ms
│       ├─> min_processing_time_ms
│       ├─> max_processing_time_ms
│       └─> total_predictions_analyzed
│
│
└── 🔒 PRIVATE ENDPOINTS (Require: Authorization: Bearer <token>)
    │
    ├── GET /me
    │   ├─> user_id
    │   ├─> username
    │   ├─> total_predictions
    │   ├─> predictions_today
    │   ├─> predictions_this_week
    │   ├─> predictions_this_month
    │   ├─> favorite_emotion
    │   ├─> avg_confidence
    │   ├─> first_prediction_date
    │   └─> last_prediction_date
    │
    ├── GET /me/activity?days=30
    │   ├─> period_days
    │   ├─> daily_activity[]
    │   │   ├─> date
    │   │   └─> prediction_count
    │   └─> total_predictions
    │
    ├── GET /me/emotions
    │   ├─> total_predictions
    │   ├─> emotions[]
    │   │   ├─> emotion_name
    │   │   ├─> count
    │   │   ├─> percentage
    │   │   └─> avg_confidence
    │   └─> most_frequent_emotion
    │
    └── GET /me/recent?limit=20
        ├─> count
        └─> predictions[]
            ├─> predic_id
            ├─> emotion_name
            ├─> confidence
            ├─> timestamp
            └─> processing_time_ms
```

---

## Quick Reference Table

| Endpoint | Method | Auth | Purpose | Chart Type |
|----------|--------|------|---------|------------|
| `/stats/global` | GET | ❌ No | System overview | KPI Cards |
| `/stats/emotions/distribution` | GET | ❌ No | Emotion breakdown | Pie/Donut |
| `/stats/trends` | GET | ❌ No | Daily statistics | Line Chart |
| `/stats/hourly-activity` | GET | ❌ No | Hour patterns | Bar Chart |
| `/stats/emotions/trends` | GET | ❌ No | Emotion trends | Multi-line |
| `/stats/performance` | GET | ❌ No | System metrics | Gauge |
| `/stats/me` | GET | ✅ Yes | User overview | KPI Cards |
| `/stats/me/activity` | GET | ✅ Yes | Daily history | Heatmap |
| `/stats/me/emotions` | GET | ✅ Yes | Personal emotions | Pie Chart |
| `/stats/me/recent` | GET | ✅ Yes | Recent history | Table/List |

---

## Response Time Optimization

All endpoints are optimized with:
- ✅ Single database query per endpoint (no N+1)
- ✅ Proper SQL aggregations (COUNT, AVG, SUM at DB level)
- ✅ Indexed columns (timestamp, user_id, emotion_id)
- ✅ Efficient JOINs only when necessary
- ✅ Date filtering at query level

Expected response times (with ~10K predictions):
- Simple stats: < 50ms
- Aggregated queries: < 100ms
- Complex trends: < 200ms

---

## Data Flow

```
Frontend Request
      ↓
FastAPI Router (/stats endpoints)
      ↓
Dependencies (get_db, get_current_user)
      ↓
DashboardService (business logic)
      ↓
SQLAlchemy ORM (database queries)
      ↓
PostgreSQL Database
      ↓
Return formatted Dict
      ↓
Pydantic Schema (validation)
      ↓
JSON Response
      ↓
Frontend Renders Chart
```

---

## Security Model

### Public Endpoints
- ✅ No authentication required
- ✅ Only aggregate/anonymized data
- ✅ No personal information exposed
- ✅ Rate limiting recommended

### Private Endpoints
- ✅ JWT token required in header
- ✅ Token validated on each request
- ✅ User identity extracted from token
- ✅ Data filtered by user_id automatically
- ✅ Inactive users rejected (403)
- ✅ Invalid tokens rejected (401)

---

## Example Curl Commands

### Public Endpoint
```bash
curl http://localhost:8000/api/v1/stats/global
```

### Private Endpoint
```bash
# Step 1: Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'
# Response: {"access_token": "eyJ...", "token_type": "bearer"}

# Step 2: Use token
curl http://localhost:8000/api/v1/stats/me \
  -H "Authorization: Bearer eyJ..."
```

---

## Frontend Integration Pattern

```javascript
// 1. Create API client
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
});

// 2. Add auth interceptor
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 3. Use in components
async function fetchStats() {
  try {
    // Public data
    const global = await api.get('/stats/global');
    const emotions = await api.get('/stats/emotions/distribution');
    
    // Private data (requires login)
    const myStats = await api.get('/stats/me');
    const myActivity = await api.get('/stats/me/activity?days=30');
    
    return { global, emotions, myStats, myActivity };
  } catch (error) {
    if (error.response?.status === 401) {
      // Redirect to login
    }
  }
}
```

---

## Testing Checklist

- [ ] Server running: `uvicorn app.main:app --reload`
- [ ] Visit http://localhost:8000/docs
- [ ] Test public endpoint: `/stats/global`
- [ ] Create test user via `/auth/register`
- [ ] Login via `/auth/login` to get token
- [ ] Test private endpoint: `/stats/me` with token
- [ ] Run test script: `python test_stats_endpoints.py`
- [ ] Check logs for any errors
- [ ] Verify database has prediction data
- [ ] Test with frontend integration

---

## Common Use Cases

### 1. Homepage Dashboard
```javascript
// Fetch key metrics
const stats = await fetch('/api/v1/stats/global').then(r => r.json());
// Display: Total predictions, users, today's activity
```

### 2. Analytics Page
```javascript
// Fetch trends
const trends = await fetch('/api/v1/stats/trends?days=30').then(r => r.json());
// Render line chart showing 30-day prediction trend
```

### 3. User Profile
```javascript
// Fetch personal stats (requires auth)
const myStats = await fetch('/api/v1/stats/me', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());
// Display user's total predictions, favorite emotion, etc.
```

### 4. Activity Calendar
```javascript
// Fetch user activity (requires auth)
const activity = await fetch('/api/v1/stats/me/activity?days=90', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());
// Render calendar heatmap
```

---

**📚 For complete documentation, see `STATS_API_GUIDE.md`**
