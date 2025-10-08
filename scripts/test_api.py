#!/usr/bin/env python3
"""
Test script for Smart Car Trip Tracker API
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_health():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print("✅ Health check passed")
        print(f"   Response: {response.json()}")
        return True
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return False

def test_root():
    """Test root endpoint"""
    print("\n🏠 Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    if response.status_code == 200:
        print("✅ Root endpoint working")
        print(f"   Response: {response.json()}")
        return True
    else:
        print(f"❌ Root endpoint failed: {response.status_code}")
        return False

def test_user_registration():
    """Test user registration"""
    print("\n👤 Testing user registration...")
    user_data = {
        "username": f"test_user_{int(time.time())}",
        "email": f"test_{int(time.time())}@example.com",
        "password": "test123456"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=user_data)
    if response.status_code == 200:
        print("✅ User registration successful")
        user = response.json()
        print(f"   User ID: {user['id']}, Username: {user['username']}")
        return user_data
    else:
        print(f"❌ User registration failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def test_login(user_data):
    """Test user login"""
    if not user_data:
        return None
        
    print("\n🔑 Testing user login...")
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        print("✅ Login successful")
        token_data = response.json()
        print(f"   Token type: {token_data['token_type']}")
        return token_data["access_token"]
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def test_protected_endpoint(token):
    """Test protected endpoint"""
    if not token:
        return False
        
    print("\n🔒 Testing protected endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
    
    if response.status_code == 200:
        print("✅ Protected endpoint access successful")
        user = response.json()
        print(f"   User: {user['username']}, Email: {user['email']}")
        return True
    else:
        print(f"❌ Protected endpoint failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def main():
    """Run all tests"""
    print("🚗 Smart Car Trip Tracker - API Test Suite")
    print("=" * 50)
    
    # Test basic endpoints
    if not test_health():
        print("\n❌ Basic connectivity failed. Is the server running?")
        return
    
    test_root()
    
    # Test authentication flow
    user_data = test_user_registration()
    token = test_login(user_data)
    test_protected_endpoint(token)
    
    print("\n" + "=" * 50)
    print("🎉 Test suite completed!")
    print("\n📖 Try the interactive API documentation at:")
    print(f"   {BASE_URL}/docs")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the API server.")
        print("   Make sure the server is running on http://localhost:8001")
        print("   Start it with: cd src && python3 main.py")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")