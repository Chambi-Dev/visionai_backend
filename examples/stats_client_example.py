"""
Example Python client for VisionAI Statistics API
Demonstrates how to consume the endpoints programmatically
"""

import requests
from typing import Optional, Dict, Any
from datetime import datetime


class VisionAIStatsClient:
    """Client for VisionAI Statistics API"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.token: Optional[str] = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with optional authentication"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    # ==================== Authentication ====================
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Login and store token
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Login response with token
        """
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        self.token = data["access_token"]
        return data
    
    def register(self, username: str, password: str) -> Dict[str, Any]:
        """
        Register new user
        
        Args:
            username: Desired username
            password: Desired password
            
        Returns:
            User data
        """
        response = requests.post(
            f"{self.base_url}/auth/register",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        return response.json()
    
    # ==================== Public Stats ====================
    
    def get_global_stats(self) -> Dict[str, Any]:
        """
        Get global system statistics
        
        Returns:
            Global stats including total predictions, users, etc.
        """
        response = requests.get(
            f"{self.base_url}/stats/global",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_emotion_distribution(self) -> Dict[str, Any]:
        """
        Get emotion distribution
        
        Returns:
            Distribution of emotions with counts and percentages
        """
        response = requests.get(
            f"{self.base_url}/stats/emotions/distribution",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_trends(self, days: int = 7) -> Dict[str, Any]:
        """
        Get prediction trends over time
        
        Args:
            days: Number of days to look back (1-90)
            
        Returns:
            Daily statistics for the period
        """
        response = requests.get(
            f"{self.base_url}/stats/trends",
            params={"days": days},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_hourly_activity(self) -> Dict[str, Any]:
        """
        Get hourly activity distribution
        
        Returns:
            Prediction counts by hour of day
        """
        response = requests.get(
            f"{self.base_url}/stats/hourly-activity",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_emotion_trends(self, days: int = 7) -> Dict[str, Any]:
        """
        Get emotion-specific trends
        
        Args:
            days: Number of days to look back (1-90)
            
        Returns:
            Daily counts for each emotion
        """
        response = requests.get(
            f"{self.base_url}/stats/emotions/trends",
            params={"days": days},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get model performance metrics
        
        Returns:
            Processing time statistics
        """
        response = requests.get(
            f"{self.base_url}/stats/performance",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    # ==================== Private Stats (Require Auth) ====================
    
    def get_my_stats(self) -> Dict[str, Any]:
        """
        Get personal statistics (requires authentication)
        
        Returns:
            User's comprehensive statistics
            
        Raises:
            HTTPError: If not authenticated
        """
        if not self.token:
            raise ValueError("Must be authenticated. Call login() first.")
        
        response = requests.get(
            f"{self.base_url}/stats/me",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_my_activity(self, days: int = 30) -> Dict[str, Any]:
        """
        Get personal daily activity (requires authentication)
        
        Args:
            days: Number of days to look back (1-365)
            
        Returns:
            User's daily prediction counts
            
        Raises:
            HTTPError: If not authenticated
        """
        if not self.token:
            raise ValueError("Must be authenticated. Call login() first.")
        
        response = requests.get(
            f"{self.base_url}/stats/me/activity",
            params={"days": days},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_my_emotions(self) -> Dict[str, Any]:
        """
        Get personal emotion breakdown (requires authentication)
        
        Returns:
            User's emotion distribution
            
        Raises:
            HTTPError: If not authenticated
        """
        if not self.token:
            raise ValueError("Must be authenticated. Call login() first.")
        
        response = requests.get(
            f"{self.base_url}/stats/me/emotions",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_my_recent_predictions(self, limit: int = 20) -> Dict[str, Any]:
        """
        Get recent predictions (requires authentication)
        
        Args:
            limit: Number of predictions to return (1-100)
            
        Returns:
            User's recent predictions
            
        Raises:
            HTTPError: If not authenticated
        """
        if not self.token:
            raise ValueError("Must be authenticated. Call login() first.")
        
        response = requests.get(
            f"{self.base_url}/stats/me/recent",
            params={"limit": limit},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()


# ==================== Example Usage ====================

def example_public_stats():
    """Example: Using public statistics"""
    print("📊 FETCHING PUBLIC STATISTICS\n")
    
    client = VisionAIStatsClient()
    
    # Global stats
    print("Global Statistics:")
    stats = client.get_global_stats()
    print(f"  Total predictions: {stats['total_predictions']}")
    print(f"  Active users: {stats['total_unique_users']}")
    print(f"  Predictions today: {stats['predictions_today']}")
    print(f"  Most common emotion: {stats['most_common_emotion']}")
    print()
    
    # Emotion distribution
    print("Emotion Distribution:")
    distribution = client.get_emotion_distribution()
    for emotion in distribution['emotions'][:3]:  # Top 3
        print(f"  {emotion['emotion_name']}: {emotion['percentage']:.1f}% ({emotion['count']} times)")
    print()
    
    # Performance
    print("Performance Metrics:")
    perf = client.get_performance_metrics()
    print(f"  Avg processing time: {perf['avg_processing_time_ms']:.1f}ms")
    print(f"  Total analyzed: {perf['total_predictions_analyzed']}")
    print()


def example_private_stats(username: str, password: str):
    """Example: Using private statistics with authentication"""
    print("🔒 FETCHING PRIVATE STATISTICS\n")
    
    client = VisionAIStatsClient()
    
    # Login
    print(f"Logging in as {username}...")
    client.login(username, password)
    print("✅ Logged in successfully!\n")
    
    # My stats
    print("My Personal Statistics:")
    my_stats = client.get_my_stats()
    print(f"  Username: {my_stats['username']}")
    print(f"  Total predictions: {my_stats['total_predictions']}")
    print(f"  Predictions today: {my_stats['predictions_today']}")
    print(f"  This week: {my_stats['predictions_this_week']}")
    print(f"  Favorite emotion: {my_stats['favorite_emotion']}")
    print(f"  Average confidence: {my_stats['avg_confidence']:.2f}")
    print()
    
    # My emotions
    print("My Emotion Breakdown:")
    my_emotions = client.get_my_emotions()
    for emotion in my_emotions['emotions'][:3]:  # Top 3
        print(f"  {emotion['emotion_name']}: {emotion['percentage']:.1f}% "
              f"(confidence: {emotion['avg_confidence']:.2f})")
    print()
    
    # Recent predictions
    print("My Recent Predictions:")
    recent = client.get_my_recent_predictions(limit=5)
    for pred in recent['predictions']:
        timestamp = datetime.fromisoformat(pred['timestamp'])
        print(f"  {timestamp.strftime('%Y-%m-%d %H:%M')} - "
              f"{pred['emotion_name']} ({pred['confidence']:.2f})")
    print()


def example_analytics_dashboard():
    """Example: Building an analytics dashboard"""
    print("📈 ANALYTICS DASHBOARD\n")
    
    client = VisionAIStatsClient()
    
    # Fetch all relevant data
    global_stats = client.get_global_stats()
    distribution = client.get_emotion_distribution()
    trends = client.get_trends(days=7)
    hourly = client.get_hourly_activity()
    
    print("="*60)
    print("VISIONAI ANALYTICS DASHBOARD")
    print("="*60)
    print()
    
    # KPIs
    print("📊 KEY METRICS")
    print(f"  Total Predictions: {global_stats['total_predictions']:,}")
    print(f"  Total Users: {global_stats['total_unique_users']:,}")
    print(f"  Today: {global_stats['predictions_today']:,}")
    print(f"  Last Hour: {global_stats['predictions_last_hour']:,}")
    print(f"  Avg Confidence: {global_stats['avg_confidence']:.1%}")
    print()
    
    # Top emotions
    print("🎭 TOP EMOTIONS")
    for emotion in distribution['emotions'][:5]:
        bar = "█" * int(emotion['percentage'] / 2)
        print(f"  {emotion['emotion_name']:12} {bar} {emotion['percentage']:.1f}%")
    print()
    
    # Peak hour
    print("⏰ PEAK ACTIVITY")
    print(f"  Peak Hour: {hourly['peak_hour']}:00 ({hourly['peak_hour_count']} predictions)")
    print()
    
    # Recent trend
    if trends['daily_stats']:
        recent = trends['daily_stats'][-1]
        print("📅 TODAY'S STATS")
        print(f"  Predictions: {recent['total_predictions']}")
        print(f"  Unique Users: {recent['unique_users']}")
        print(f"  Avg Confidence: {recent['avg_confidence']:.1%}")
    print()


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║        VisionAI Statistics API - Python Client           ║
    ║                                                          ║
    ║  This script demonstrates how to use the API             ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Example 1: Public stats (no auth required)
        example_public_stats()
        
        # Example 2: Analytics dashboard
        example_analytics_dashboard()
        
        # Example 3: Private stats (requires auth)
        print("\n" + "="*60)
        print("To see private stats, provide your credentials:")
        username = input("Username (or press Enter to skip): ").strip()
        
        if username:
            password = input("Password: ").strip()
            example_private_stats(username, password)
        else:
            print("\n⏭️  Skipping private stats example")
        
        print("\n" + "="*60)
        print("✅ Examples completed successfully!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the API.")
        print("Make sure the server is running on http://localhost:8000")
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
        if e.response.status_code == 401:
            print("Authentication failed. Check your credentials.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
