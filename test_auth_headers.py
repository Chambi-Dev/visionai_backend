"""
Test script para verificar que los endpoints de autenticación usan Authorization headers correctamente.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_auth_endpoints():
    print("=" * 60)
    print("🧪 Testing Authentication with Authorization Headers")
    print("=" * 60)
    
    # 1. Register user
    print("\n1️⃣  Registering test user...")
    register_data = {
        "username": "testuser_headers",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 201:
            print("✅ User registered successfully")
        elif response.status_code == 400:
            print("ℹ️  User already exists, continuing...")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(response.json())
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 2. Login
    print("\n2️⃣  Logging in...")
    login_data = {
        "username": "testuser_headers",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            print("✅ Login successful!")
            print(f"   Access token: {access_token[:50]}...")
            
            # Check for refresh token in cookie
            refresh_cookie = response.cookies.get("refresh_token")
            if refresh_cookie:
                print(f"   Refresh token cookie: {refresh_cookie[:50]}...")
            else:
                print("   ⚠️  No refresh token cookie found")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.json())
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # 3. Test /auth/verify with Authorization header
    print("\n3️⃣  Testing /auth/verify with Authorization header...")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/auth/verify", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Token verification successful!")
            print(f"   Username: {data.get('username')}")
            print(f"   User ID: {data.get('user_id')}")
        else:
            print(f"❌ Verification failed: {response.status_code}")
            print(response.json())
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 4. Test /auth/users/me with Authorization header
    print("\n4️⃣  Testing /auth/users/me with Authorization header...")
    
    try:
        response = requests.get(f"{BASE_URL}/auth/users/me", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Get user profile successful!")
            print(f"   Username: {data.get('username')}")
            print(f"   User ID: {data.get('user_id')}")
            print(f"   Active: {data.get('is_active')}")
        else:
            print(f"❌ Get profile failed: {response.status_code}")
            print(response.json())
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 5. Test /stats/me with Authorization header
    print("\n5️⃣  Testing /stats/me with Authorization header...")
    
    try:
        response = requests.get(f"{BASE_URL}/stats/me", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Get personal stats successful!")
            print(f"   Username: {data.get('username')}")
            print(f"   Total predictions: {data.get('total_predictions')}")
        else:
            print(f"❌ Get stats failed: {response.status_code}")
            print(response.json())
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 6. Test without Authorization header (should fail)
    print("\n6️⃣  Testing /auth/users/me WITHOUT Authorization header (should fail)...")
    
    try:
        response = requests.get(f"{BASE_URL}/auth/users/me")
        if response.status_code == 401:
            print("✅ Correctly rejected request without auth!")
            print(f"   Error: {response.json().get('detail')}")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 7. Test with invalid token (should fail)
    print("\n7️⃣  Testing with invalid token (should fail)...")
    invalid_headers = {
        "Authorization": "Bearer invalid_token_123"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/auth/verify", headers=invalid_headers)
        if response.status_code == 401:
            print("✅ Correctly rejected invalid token!")
            print(f"   Error: {response.json().get('detail')}")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    print("\n⚠️  Make sure your FastAPI server is running on http://localhost:8000\n")
    test_auth_endpoints()
