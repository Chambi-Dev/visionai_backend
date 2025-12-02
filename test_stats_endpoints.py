"""
Script de prueba para los nuevos endpoints de estadísticas.
Ejecutar después de tener algunos datos en la base de datos.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def print_response(title, response):
    """Imprime una respuesta formateada"""
    print(f"\n{'='*60}")
    print(f"📊 {title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")

def test_public_endpoints():
    """Prueba todos los endpoints públicos"""
    print("\n🌍 TESTING PUBLIC ENDPOINTS (No Authentication Required)")
    
    # 1. Global stats
    response = requests.get(f"{BASE_URL}/stats/global")
    print_response("Global Statistics", response)
    
    # 2. Emotion distribution
    response = requests.get(f"{BASE_URL}/stats/emotions/distribution")
    print_response("Emotion Distribution", response)
    
    # 3. Trends (7 days)
    response = requests.get(f"{BASE_URL}/stats/trends?days=7")
    print_response("Prediction Trends (7 days)", response)
    
    # 4. Hourly activity
    response = requests.get(f"{BASE_URL}/stats/hourly-activity")
    print_response("Hourly Activity", response)
    
    # 5. Emotion trends
    response = requests.get(f"{BASE_URL}/stats/emotions/trends?days=7")
    print_response("Emotion Trends (7 days)", response)
    
    # 6. Performance metrics
    response = requests.get(f"{BASE_URL}/stats/performance")
    print_response("Performance Metrics", response)

def test_private_endpoints(username, password):
    """Prueba todos los endpoints privados"""
    print("\n🔒 TESTING PRIVATE ENDPOINTS (Authentication Required)")
    
    # Login to get token
    print("\n🔐 Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    print(f"✅ Login successful! Token: {token[:20]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Personal stats
    response = requests.get(f"{BASE_URL}/stats/me", headers=headers)
    print_response("My Personal Statistics", response)
    
    # 2. User activity
    response = requests.get(f"{BASE_URL}/stats/me/activity?days=30", headers=headers)
    print_response("My Daily Activity (30 days)", response)
    
    # 3. User emotions
    response = requests.get(f"{BASE_URL}/stats/me/emotions", headers=headers)
    print_response("My Emotion Breakdown", response)
    
    # 4. Recent predictions
    response = requests.get(f"{BASE_URL}/stats/me/recent?limit=10", headers=headers)
    print_response("My Recent Predictions (10)", response)

def test_authentication_required():
    """Prueba que los endpoints privados requieren autenticación"""
    print("\n🔐 TESTING AUTHENTICATION REQUIREMENTS")
    
    # Try to access private endpoint without token
    response = requests.get(f"{BASE_URL}/stats/me")
    print_response("Access /stats/me without token (should fail)", response)
    
    # Try with invalid token
    headers = {"Authorization": "Bearer invalid_token_xyz"}
    response = requests.get(f"{BASE_URL}/stats/me", headers=headers)
    print_response("Access /stats/me with invalid token (should fail)", response)

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║        VisionAI Statistics API Test Suite               ║
    ║                                                          ║
    ║  Make sure the server is running on localhost:8000      ║
    ║  Run: uvicorn app.main:app --reload                     ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Test public endpoints
        test_public_endpoints()
        
        # Test authentication requirement
        test_authentication_required()
        
        # Test private endpoints (you need to provide valid credentials)
        print("\n" + "="*60)
        print("To test private endpoints, provide your credentials:")
        username = input("Username (or press Enter to skip): ").strip()
        
        if username:
            password = input("Password: ").strip()
            test_private_endpoints(username, password)
        else:
            print("\n⏭️  Skipping private endpoint tests")
        
        print("\n" + "="*60)
        print("✅ Test suite completed!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print("Make sure the server is running on http://localhost:8000")
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
