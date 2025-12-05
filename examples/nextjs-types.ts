/**
 * TypeScript Types for VisionAI Stats API
 * 
 * Use these types in your Next.js application for type-safe API responses.
 * All timestamps are in ISO 8601 format (YYYY-MM-DDTHH:mm:ss)
 */

// ============= EMOTION TYPES =============

export interface EmotionDistribution {
  emotion_name: string;
  count: number;
  percentage: number; // 0-100
}

export interface EmotionInfo {
  emotion_id: number;
  emotion_name: string;
  emotion_desc: string | null;
}

// ============= GLOBAL STATS (PUBLIC) =============

export interface PublicGlobalStats {
  total_predictions: number;
  total_unique_users: number;
  total_sessions_today: number;
  most_common_emotion: string;
  avg_confidence: number;
  predictions_last_hour: number;
  predictions_today: number;
}

export interface PublicEmotionDistributionResponse {
  total_predictions: number;
  emotions: EmotionDistribution[];
}

// ============= TRENDS (PUBLIC) =============

export interface DailyStats {
  date: string;              // ISO date: "2025-12-04"
  timestamp: string;         // ISO datetime: "2025-12-04T00:00:00"
  total_predictions: number;
  unique_users: number;
  avg_confidence: number;
}

export interface PublicTrendsResponse {
  period_days: number;
  daily_stats: DailyStats[];
}

// ============= HOURLY ACTIVITY (PUBLIC) =============

export interface HourlyDistribution {
  hour: number;           // 0-23
  hour_label: string;     // "00:00", "13:00", etc.
  count: number;
}

export interface PublicHourlyActivityResponse {
  hourly_distribution: HourlyDistribution[];
  peak_hour: number;
  peak_hour_count: number;
}

// ============= EMOTION TRENDS (PUBLIC) =============

export interface EmotionTrend {
  date: string;          // ISO date: "2025-12-04"
  timestamp: string;     // ISO datetime: "2025-12-04T00:00:00"
  emotion_name: string;
  count: number;
}

export interface PublicEmotionTrendsResponse {
  period_days: number;
  trends: EmotionTrend[];
}

// ============= PERFORMANCE (PUBLIC) =============

export interface PerformanceMetrics {
  avg_processing_time_ms: number;
  min_processing_time_ms: number;
  max_processing_time_ms: number;
  total_predictions_analyzed: number;
}

// ============= USER STATS (PRIVATE) =============

export interface UserPersonalStats {
  user_id: number;
  username: string;
  total_predictions: number;
  predictions_today: number;
  predictions_this_week: number;
  predictions_this_month: number;
  favorite_emotion: string | null;
  avg_confidence: number;
  first_prediction_date: string | null;  // ISO datetime
  last_prediction_date: string | null;   // ISO datetime
}

// ============= USER ACTIVITY (PRIVATE) =============

export interface UserDailyActivity {
  date: string;              // ISO date: "2025-12-04"
  timestamp: string;         // ISO datetime: "2025-12-04T00:00:00"
  prediction_count: number;
}

export interface UserActivityResponse {
  period_days: number;
  daily_activity: UserDailyActivity[];
  total_predictions: number;
}

// ============= USER EMOTIONS (PRIVATE) =============

export interface UserEmotionBreakdown {
  emotion_name: string;
  count: number;
  percentage: number;
  avg_confidence: number;
}

export interface UserEmotionStatsResponse {
  total_predictions: number;
  emotions: UserEmotionBreakdown[];
  most_frequent_emotion: string | null;
}

// ============= USER RECENT PREDICTIONS (PRIVATE) =============

export interface UserRecentPrediction {
  predic_id: number;
  emotion_name: string;
  confidence: number;
  timestamp: string;         // ISO datetime with full precision
  processing_time_ms: number | null;
}

export interface UserRecentPredictionsResponse {
  count: number;
  predictions: UserRecentPrediction[];
}

// ============= AUTHENTICATION =============

export interface Token {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserResponse {
  user_id: number;
  username: string;
  is_active: boolean;
  created_at: string;  // ISO datetime
}

// ============= HELPER TYPES =============

/**
 * Emotion names used in the system
 */
export type EmotionName = 
  | 'happy'
  | 'sad'
  | 'angry'
  | 'surprise'
  | 'fear'
  | 'disgust'
  | 'neutral';

/**
 * Chart data point for time series
 */
export interface TimeSeriesDataPoint {
  date: string;
  timestamp: string;
  value: number;
  label?: string;
}

/**
 * Transform trends data for multi-line charts
 */
export interface EmotionTrendByDate {
  date: string;
  timestamp: string;
  [emotionName: string]: string | number; // emotion names as keys with count values
}

// ============= API ERROR =============

export interface ApiError {
  detail: string;
  code?: string;
}
