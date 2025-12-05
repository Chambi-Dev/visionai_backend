# 📊 Chart Integration Guide - Next.js + shadcn/ui

## Overview

All stats endpoints now return **proper timestamps** for seamless integration with shadcn's chart components (built on Recharts).

---

## 🎯 What Changed

### Before (String dates only)
```json
{
  "date": "2025-12-04",
  "total_predictions": 150
}
```
❌ Had to parse dates manually  
❌ Inconsistent formats  
❌ No precise time data  

### After (Date + Timestamp)
```json
{
  "date": "2025-12-04",
  "timestamp": "2025-12-04T00:00:00",
  "total_predictions": 150
}
```
✅ Both human-readable date and precise timestamp  
✅ ISO 8601 format (JavaScript-friendly)  
✅ Ready for charts without conversion  

---

## 📋 Updated Endpoints

### 1. Daily Trends (`GET /stats/trends?days=7`)

**Response:**
```typescript
{
  period_days: 7,
  daily_stats: [
    {
      date: "2025-12-04",           // String for display
      timestamp: "2025-12-04T00:00:00",  // DateTime for sorting/charting
      total_predictions: 150,
      unique_users: 45,
      avg_confidence: 0.87
    }
  ]
}
```

### 2. Emotion Trends (`GET /stats/emotion-trends?days=7`)

**Response:**
```typescript
{
  period_days: 7,
  trends: [
    {
      date: "2025-12-04",
      timestamp: "2025-12-04T00:00:00",
      emotion_name: "happy",
      count: 50
    }
  ]
}
```

### 3. Hourly Activity (`GET /stats/hourly`)

**Response:**
```typescript
{
  hourly_distribution: [
    {
      hour: 0,
      hour_label: "00:00",    // NEW: Formatted label for x-axis
      count: 15
    },
    {
      hour: 13,
      hour_label: "13:00",
      count: 87
    }
  ],
  peak_hour: 13,
  peak_hour_count: 87
}
```

### 4. User Activity (`GET /stats/me/activity?days=30`)

**Response:**
```typescript
{
  period_days: 30,
  daily_activity: [
    {
      date: "2025-12-04",
      timestamp: "2025-12-04T00:00:00",
      prediction_count: 25
    }
  ],
  total_predictions: 500
}
```

### 5. Recent Predictions (`GET /stats/me/recent?limit=20`)

**Response:**
```typescript
{
  count: 20,
  predictions: [
    {
      predic_id: 1234,
      emotion_name: "happy",
      confidence: 0.95,
      timestamp: "2025-12-04T14:35:22.123456",  // Full precision
      processing_time_ms: 45
    }
  ]
}
```

### 6. User Personal Stats (`GET /stats/me`)

**Response:**
```typescript
{
  user_id: 1,
  username: "john_doe",
  total_predictions: 500,
  predictions_today: 25,
  predictions_this_week: 120,
  predictions_this_month: 450,
  favorite_emotion: "happy",
  avg_confidence: 0.87,
  first_prediction_date: "2025-01-15T10:30:00",  // DateTime
  last_prediction_date: "2025-12-04T14:35:22"    // DateTime
}
```

---

## 💻 Next.js Integration Examples

### Setup API Client

```typescript
// lib/api-client.ts
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const statsApi = {
  async getTrends(days: number = 7) {
    const { data } = await axios.get(`${API_URL}/stats/trends?days=${days}`, {
      headers: { Authorization: `Bearer ${getAccessToken()}` }
    });
    return data;
  },
  
  async getHourlyActivity() {
    const { data } = await axios.get(`${API_URL}/stats/hourly`);
    return data;
  },
  
  async getEmotionTrends(days: number = 7) {
    const { data } = await axios.get(`${API_URL}/stats/emotion-trends?days=${days}`);
    return data;
  },
  
  async getUserActivity(days: number = 30) {
    const { data } = await axios.get(`${API_URL}/stats/me/activity?days=${days}`, {
      headers: { Authorization: `Bearer ${getAccessToken()}` }
    });
    return data;
  }
};
```

---

## 📊 Chart Examples with shadcn/ui

### 1. Line Chart - Daily Predictions

```tsx
// components/charts/daily-predictions-chart.tsx
'use client';

import { useEffect, useState } from 'react';
import { Line, LineChart, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { statsApi } from '@/lib/api-client';

interface DailyStat {
  date: string;
  timestamp: string;
  total_predictions: number;
  unique_users: number;
  avg_confidence: number;
}

export function DailyPredictionsChart() {
  const [data, setData] = useState<DailyStat[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const response = await statsApi.getTrends(7);
        setData(response.daily_stats);
      } catch (error) {
        console.error('Error loading chart data:', error);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) return <div>Loading chart...</div>;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Daily Predictions</CardTitle>
        <CardDescription>Last 7 days</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="date" 
              tickFormatter={(value) => {
                // Format: Dec 4
                const date = new Date(value);
                return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
              }}
            />
            <YAxis />
            <Tooltip 
              labelFormatter={(value) => {
                const date = new Date(value);
                return date.toLocaleDateString('en-US', { 
                  weekday: 'long', 
                  month: 'long', 
                  day: 'numeric' 
                });
              }}
            />
            <Line 
              type="monotone" 
              dataKey="total_predictions" 
              stroke="#8884d8" 
              name="Predictions"
              strokeWidth={2}
            />
            <Line 
              type="monotone" 
              dataKey="unique_users" 
              stroke="#82ca9d" 
              name="Users"
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
```

---

### 2. Bar Chart - Hourly Activity

```tsx
// components/charts/hourly-activity-chart.tsx
'use client';

import { useEffect, useState } from 'react';
import { Bar, BarChart, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { statsApi } from '@/lib/api-client';

interface HourlyData {
  hour: number;
  hour_label: string;
  count: number;
}

export function HourlyActivityChart() {
  const [data, setData] = useState<HourlyData[]>([]);

  useEffect(() => {
    async function loadData() {
      const response = await statsApi.getHourlyActivity();
      setData(response.hourly_distribution);
    }
    loadData();
  }, []);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Hourly Activity</CardTitle>
        <CardDescription>Predictions by hour of day</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="hour_label"  // Use the formatted label!
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis />
            <Tooltip 
              labelFormatter={(label) => `Time: ${label}`}
              formatter={(value) => [`${value} predictions`, 'Count']}
            />
            <Bar dataKey="count" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
```

---

### 3. Area Chart - Emotion Trends

```tsx
// components/charts/emotion-trends-chart.tsx
'use client';

import { useEffect, useState } from 'react';
import { Area, AreaChart, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { statsApi } from '@/lib/api-client';

const EMOTION_COLORS: Record<string, string> = {
  happy: '#22c55e',
  sad: '#3b82f6',
  angry: '#ef4444',
  surprise: '#f59e0b',
  fear: '#8b5cf6',
  disgust: '#06b6d4',
  neutral: '#64748b'
};

export function EmotionTrendsChart() {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    async function loadData() {
      const response = await statsApi.getEmotionTrends(7);
      
      // Transform data: group by date
      const groupedByDate = response.trends.reduce((acc: any, item: any) => {
        const date = item.date;
        if (!acc[date]) {
          acc[date] = { date, timestamp: item.timestamp };
        }
        acc[date][item.emotion_name] = item.count;
        return acc;
      }, {});
      
      setData(Object.values(groupedByDate));
    }
    loadData();
  }, []);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Emotion Trends</CardTitle>
        <CardDescription>Distribution over time</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="date"
              tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            />
            <YAxis />
            <Tooltip 
              labelFormatter={(value) => new Date(value).toLocaleDateString('en-US', { 
                weekday: 'long', 
                month: 'long', 
                day: 'numeric' 
              })}
            />
            <Legend />
            {Object.keys(EMOTION_COLORS).map((emotion) => (
              <Area
                key={emotion}
                type="monotone"
                dataKey={emotion}
                stackId="1"
                stroke={EMOTION_COLORS[emotion]}
                fill={EMOTION_COLORS[emotion]}
                fillOpacity={0.6}
              />
            ))}
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
```

---

### 4. Table - Recent Predictions

```tsx
// components/tables/recent-predictions-table.tsx
'use client';

import { useEffect, useState } from 'react';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { statsApi } from '@/lib/api-client';

interface Prediction {
  predic_id: number;
  emotion_name: string;
  confidence: number;
  timestamp: string;
  processing_time_ms: number;
}

const EMOTION_VARIANTS: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
  happy: 'default',
  sad: 'secondary',
  angry: 'destructive',
  neutral: 'outline',
};

export function RecentPredictionsTable() {
  const [predictions, setPredictions] = useState<Prediction[]>([]);

  useEffect(() => {
    async function loadData() {
      const response = await statsApi.getUserRecentPredictions(10);
      setPredictions(response.predictions);
    }
    loadData();
  }, []);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Predictions</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Timestamp</TableHead>
              <TableHead>Emotion</TableHead>
              <TableHead>Confidence</TableHead>
              <TableHead>Processing Time</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {predictions.map((pred) => (
              <TableRow key={pred.predic_id}>
                <TableCell>
                  {new Date(pred.timestamp).toLocaleString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </TableCell>
                <TableCell>
                  <Badge variant={EMOTION_VARIANTS[pred.emotion_name] || 'default'}>
                    {pred.emotion_name}
                  </Badge>
                </TableCell>
                <TableCell>{(pred.confidence * 100).toFixed(1)}%</TableCell>
                <TableCell>{pred.processing_time_ms}ms</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
```

---

## 🎨 Complete Dashboard Example

```tsx
// app/dashboard/page.tsx
'use client';

import { DailyPredictionsChart } from '@/components/charts/daily-predictions-chart';
import { HourlyActivityChart } from '@/components/charts/hourly-activity-chart';
import { EmotionTrendsChart } from '@/components/charts/emotion-trends-chart';
import { RecentPredictionsTable } from '@/components/tables/recent-predictions-table';

export default function DashboardPage() {
  return (
    <div className="container mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <DailyPredictionsChart />
        <HourlyActivityChart />
      </div>
      
      <EmotionTrendsChart />
      
      <RecentPredictionsTable />
    </div>
  );
}
```

---

## ✅ Benefits

1. **No Date Parsing Needed**: Timestamps are in ISO 8601 format
2. **JavaScript-Friendly**: `new Date(timestamp)` works instantly
3. **Chart-Ready**: Direct use in Recharts/shadcn components
4. **Consistent Format**: All endpoints use same timestamp format
5. **Both Formats**: Date string for display, timestamp for calculations
6. **Sortable**: Proper datetime comparison in JavaScript
7. **Timezone-Aware**: ISO format includes timezone info

---

## 🚀 Quick Test

```bash
# Get trends with timestamps
curl http://localhost:8000/api/v1/stats/trends?days=7

# Get hourly with labels
curl http://localhost:8000/api/v1/stats/hourly

# Get user activity
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/stats/me/activity?days=30
```

All stats endpoints now return chart-ready data! 📊✨
