#!/usr/bin/env python
"""
Manual test script to verify authentication endpoints.
Run this after starting the Django server.
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/auth"

def test_registration():
    """Test user registration"""
    print("\n=== Testing Registration ===")
    data = {
        "email": "testuser@iiti.ac.in",
        "username": "testuser",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!"
    }
    response = requests.post(f"{BASE_URL}/register/", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 201

def test_invalid_email():
    """Test registration with invalid email domain"""
    print("\n=== Testing Invalid Email Domain ===")
    data = {
        "email": "testuser@gmail.com",
        "username": "testuser2",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!"
    }
    response = requests.post(f"{BASE_URL}/register/", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 400

def test_login_unverified():
    """Test login with unverified account"""
    print("\n=== Testing Login (Unverified Account) ===")
    data = {
        "email": "testuser@iiti.ac.in",
        "password": "SecurePass123!"
    }
    response = requests.post(f"{BASE_URL}/login/", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 401

if __name__ == "__main__":
    print("Starting manual authentication tests...")
    print("Make sure Django server is running on http://localhost:8000")
    
    try:
        # Test registration
        if test_registration():
            print("✓ Registration test passed")
        else:
            print("✗ Registration test failed")
        
        # Test invalid email
        if test_invalid_email():
            print("✓ Invalid email test passed")
        else:
            print("✗ Invalid email test failed")
        
        # Test login with unverified account
        if test_login_unverified():
            print("✓ Unverified login test passed")
        else:
            print("✗ Unverified login test failed")
        
        print("\n=== Manual Tests Complete ===")
        print("Note: To test full flow, you need to:")
        print("1. Get verification token from database")
        print("2. Call /api/auth/verify-email/ with the token")
        print("3. Then test login with verified account")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to server")
        print("Please start the Django server with: python manage.py runserver")
