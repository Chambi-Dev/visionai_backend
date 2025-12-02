# 🚀 Quick Start Guide - VisionAI Statistics Endpoints

## ⚡ TL;DR

I've created **10 new REST API endpoints** for your emotion prediction system:
- **6 public endpoints** - System statistics anyone can view
- **4 private endpoints** - Personal user statistics (require auth)

---

## 📁 What Was Added

### New Files
1. **`app/api/routes/stats.py`** - All 10 endpoint definitions
2. **`app/services/dashboard_service.py`** - Business logic for stats calculations
3. **`STATS_API_GUIDE.md`** - Complete API documentation
4. **`ENDPOINT_STRUCTURE.md`** - Visual endpoint map
5. **`IMPLEMENTATION_SUMMARY.md`** - Technical details
6. **`test_stats_endpoints.py`** - Test script

### Modified Files
1. **`app/api/dependencies.py`** - Added `get_current_user()` for auth
2. **`app/models/schemas.py`** - Added 15 response schemas
3. **`app/main.py`** - Registered stats router

---

## 🎯 Endpoints At A Glance

### Public (No Auth) - `/api/v1/stats/`
| Endpoint | What It Returns | Perfect For |
|----------|----------------|-------------|
| `GET /global` | System overview stats | Homepage KPIs |
| `GET /emotions/distribution` | Emotion breakdown % | Pie chart |
| `GET /trends?days=7` | Daily prediction trends | Line chart |
| `GET /hourly-activity` | Activity by hour | Bar chart |
| `GET /emotions/trends?days=7` | Emotion trends over time | Multi-line chart |
| `GET /performance` | Model performance metrics | System health |

### Private (Require Auth) - `/api/v1/stats/me/`
| Endpoint | What It Returns | Perfect For |
|----------|----------------|-------------|
| `GET /me` | User's total stats | Profile dashboard |
| `GET /me/activity?days=30` | Daily activity history | Calendar heatmap |
| `GET /me/emotions` | Personal emotion breakdown | Personal pie chart |
| `GET /me/recent?limit=20` | Recent predictions | Activity feed |

---

## 🏃 Quick Test (3 Steps)

### Step 1: Start Server
```bash
cd visionai_backend
uvicorn app.main:app --reload
```

### Step 2: Test Public Endpoint
```bash
curl http://localhost:8000/api/v1/stats/global
```

Expected response:
```json
{
  "total_predictions": 1234,
  "total_unique_users": 42,
  "total_sessions_today": 5,
  "most_common_emotion": "happy",
  "avg_confidence": 0.87,
  "predictions_last_hour": 3,
  "predictions_today": 45
}
```

### Step 3: Test Private Endpoint
```bash
# Login (replace with your credentials)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"youruser","password":"yourpass"}'

# Copy the access_token from response, then:
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:8000/api/v1/stats/me
```

---

## 🎨 Frontend Integration Example

### React Component
```javascript
import { useEffect, useState } from 'react';

function Dashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    // Fetch public stats
    fetch('http://localhost:8000/api/v1/stats/global')
      .then(res => res.json())
      .then(data => setStats(data));
  }, []);

  if (!stats) return <div>Loading...</div>;

  return (
    <div className="dashboard">
      <div className="stat-card">
        <h3>Total Predictions</h3>
        <p>{stats.total_predictions}</p>
      </div>
      <div className="stat-card">
        <h3>Active Users</h3>
        <p>{stats.total_unique_users}</p>
      </div>
      <div className="stat-card">
        <h3>Today</h3>
        <p>{stats.predictions_today}</p>
      </div>
      <div className="stat-card">
        <h3>Most Common</h3>
        <p>{stats.most_common_emotion}</p>
      </div>
    </div>
  );
}
```

### With Authentication
```javascript
function UserStats() {
  const [myStats, setMyStats] = useState(null);
  const token = localStorage.getItem('token'); // Get saved token

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/stats/me', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
      .then(res => res.json())
      .then(data => setMyStats(data));
  }, [token]);

  if (!myStats) return <div>Loading...</div>;

  return (
    <div className="user-stats">
      <h2>Welcome, {myStats.username}!</h2>
      <p>You've made {myStats.predictions_today} predictions today</p>
      <p>Your favorite emotion: {myStats.favorite_emotion}</p>
      <p>Total predictions: {myStats.total_predictions}</p>
    </div>
  );
}
```

---

## 📊 Chart Examples

### Emotion Distribution (Pie Chart with Chart.js)
```javascript
import { Pie } from 'react-chartjs-2';

function EmotionChart() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/stats/emotions/distribution')
      .then(res => res.json())
      .then(result => {
        setData({
          labels: result.emotions.map(e => e.emotion_name),
          datasets: [{
            data: result.emotions.map(e => e.count),
            backgroundColor: [
              '#FF6384', '#36A2EB', '#FFCE56',
              '#4BC0C0', '#9966FF', '#FF9F40'
            ]
          }]
        });
      });
  }, []);

  return data ? <Pie data={data} /> : <div>Loading...</div>;
}
```

### Daily Trends (Line Chart)
```javascript
import { Line } from 'react-chartjs-2';

function TrendsChart() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/stats/trends?days=7')
      .then(res => res.json())
      .then(result => {
        setData({
          labels: result.daily_stats.map(s => s.date),
          datasets: [{
            label: 'Predictions',
            data: result.daily_stats.map(s => s.total_predictions),
            borderColor: '#36A2EB',
            fill: false
          }]
        });
      });
  }, []);

  return data ? <Line data={data} /> : <div>Loading...</div>;
}
```

---

## 🔑 Authentication Flow

### 1. Register New User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"newuser","password":"securepass123"}'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"newuser","password":"securepass123"}'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Use Token
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/stats/me
```

---

## 📚 Documentation

- **Complete API Guide**: `STATS_API_GUIDE.md`
- **Endpoint Structure**: `ENDPOINT_STRUCTURE.md`
- **Implementation Details**: `IMPLEMENTATION_SUMMARY.md`
- **Interactive Docs**: http://localhost:8000/docs

---

## 🧪 Testing

### Run Automated Tests
```bash
python test_stats_endpoints.py
```

### Manual Testing via Swagger UI
1. Go to http://localhost:8000/docs
2. Find "Statistics" section
3. Try "GET /stats/global" (no auth needed)
4. For private endpoints:
   - Click "Authorize" button at top
   - Enter token: `Bearer YOUR_TOKEN`
   - Try "GET /stats/me"

---

## 🎁 Example Dashboard Layouts

### Public Dashboard
```
┌─────────────────────────────────────────────┐
│  📊 15,234 Predictions  👥 342 Users        │
│  🔥 456 Today          ⚡ 23 Last Hour     │
├─────────────────────────────────────────────┤
│  Most Common: 😊 Happy                      │
│  Average Confidence: 87%                    │
├─────────────────────────────────────────────┤
│  [Emotion Distribution Pie Chart]           │
├─────────────────────────────────────────────┤
│  [7-Day Trend Line Chart]                   │
└─────────────────────────────────────────────┘
```

### User Profile
```
┌─────────────────────────────────────────────┐
│  Welcome back, john_doe! 👋                 │
├─────────────────────────────────────────────┤
│  📅 Today: 12   📊 This Week: 67           │
│  📈 This Month: 189   💯 Total: 1,234      │
├─────────────────────────────────────────────┤
│  Your Favorite: 😊 Happy                    │
│  Average Confidence: 89%                    │
├─────────────────────────────────────────────┤
│  [Personal Emotion Pie Chart]               │
├─────────────────────────────────────────────┤
│  [30-Day Activity Calendar Heatmap]         │
└─────────────────────────────────────────────┘
```

---

## ✅ Checklist

- [x] 10 endpoints created (6 public + 4 private)
- [x] Authentication system integrated
- [x] Response schemas with validation
- [x] Service layer with business logic
- [x] Comprehensive documentation
- [x] Test script included
- [x] No errors or warnings
- [x] Ready for production

---

## 🆘 Troubleshooting

### Can't connect to server?
```bash
# Make sure server is running
uvicorn app.main:app --reload
```

### Getting 401 Unauthorized?
```bash
# Make sure you're using a valid token
# Token expires after 24 hours - login again
```

### No data in responses?
```bash
# Make sure you have predictions in the database
# Use the WebSocket endpoint to create some predictions first
```

### Import errors?
```bash
# Make sure all dependencies are installed
pip install -r requirements.txt
```

---

## 🎉 You're All Set!

Your emotion prediction system now has a complete statistics API. Start building your frontend charts and dashboards!

**Questions? Check the full docs in `STATS_API_GUIDE.md`**
