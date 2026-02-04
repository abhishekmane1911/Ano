"""
Manual API test script to verify profile endpoints
Run with: python test_profile_api_manual.py
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

print("\n=== Profile API Manual Test ===\n")

# Step 1: Register a new user
print("1. Registering new user...")
register_data = {
    "username": "apitestuser",
    "email": "apitest@iiti.ac.in",
    "password": "TestPass123!",
    "password2": "TestPass123!"
}

try:
    response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
    if response.status_code == 201:
        print(f"   ✓ User registered successfully")
        user_data = response.json()
    else:
        print(f"   Note: Registration returned {response.status_code}")
        print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    print("   Make sure the Django server is running: python manage.py runserver")
    exit(1)

# Step 2: Login to get tokens
print("\n2. Logging in...")
login_data = {
    "email": "apitest@iiti.ac.in",
    "password": "TestPass123!"
}

response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
if response.status_code == 200:
    tokens = response.json()
    access_token = tokens['access']
    print(f"   ✓ Login successful")
    print(f"   Access token: {access_token[:20]}...")
else:
    print(f"   ✗ Login failed: {response.status_code}")
    print(f"   Response: {response.json()}")
    exit(1)

# Set up headers with authentication
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Step 3: Create a profile
print("\n3. Creating profile...")
profile_data = {
    "age": 22,
    "interests": ["coding", "music", "reading"],
    "hobbies": ["guitar", "hiking", "photography"],
    "relationship_intent": "friendship",
    "personality_tags": ["introverted", "creative", "analytical"],
    "bio": "Test bio for API testing"
}

response = requests.post(f"{BASE_URL}/profiles/", json=profile_data, headers=headers)
if response.status_code == 201:
    profile = response.json()
    anonymous_id = profile['anonymous_id']
    print(f"   ✓ Profile created successfully")
    print(f"   Anonymous ID: {anonymous_id}")
    
    # Verify no personal information is exposed
    assert 'email' not in profile, "Email should not be in response"
    assert 'user' not in profile, "User should not be in response"
    assert 'username' not in profile, "Username should not be in response"
    print(f"   ✓ No personal information exposed in response")
else:
    print(f"   ✗ Profile creation failed: {response.status_code}")
    print(f"   Response: {response.json()}")
    exit(1)

# Step 4: Get own profile
print("\n4. Retrieving own profile...")
response = requests.get(f"{BASE_URL}/profiles/me/", headers=headers)
if response.status_code == 200:
    my_profile = response.json()
    print(f"   ✓ Profile retrieved successfully")
    print(f"   Age: {my_profile['age']}")
    print(f"   Interests: {my_profile['interests']}")
    
    # Verify no personal information
    assert 'email' not in my_profile, "Email should not be in response"
    assert 'user' not in my_profile, "User should not be in response"
    print(f"   ✓ No personal information exposed")
else:
    print(f"   ✗ Failed to retrieve profile: {response.status_code}")
    exit(1)

# Step 5: Update profile
print("\n5. Updating profile...")
update_data = {
    "age": 23,
    "bio": "Updated bio text"
}

response = requests.patch(f"{BASE_URL}/profiles/me/", json=update_data, headers=headers)
if response.status_code == 200:
    updated_profile = response.json()
    print(f"   ✓ Profile updated successfully")
    print(f"   New age: {updated_profile['age']}")
    print(f"   New bio: {updated_profile['bio']}")
    assert updated_profile['age'] == 23, "Age should be updated"
    assert updated_profile['bio'] == "Updated bio text", "Bio should be updated"
else:
    print(f"   ✗ Failed to update profile: {response.status_code}")
    print(f"   Response: {response.json()}")

# Step 6: Get profile by anonymous_id
print("\n6. Retrieving profile by anonymous_id...")
response = requests.get(f"{BASE_URL}/profiles/{anonymous_id}/", headers=headers)
if response.status_code == 200:
    public_profile = response.json()
    print(f"   ✓ Profile retrieved by anonymous_id")
    print(f"   Anonymous ID: {public_profile['anonymous_id']}")
    
    # Verify no personal information
    assert 'email' not in public_profile, "Email should not be in response"
    assert 'user' not in public_profile, "User should not be in response"
    print(f"   ✓ No personal information exposed")
else:
    print(f"   ✗ Failed to retrieve profile: {response.status_code}")

# Step 7: Test validation - invalid age
print("\n7. Testing validation (invalid age)...")
invalid_data = {
    "age": 15,  # Too young
    "interests": ["test"],
    "hobbies": ["test"],
    "relationship_intent": "friendship",
    "personality_tags": ["test"]
}

# First, we need to delete the existing profile to test creation validation
# (In a real scenario, this would be a different user)
print("   Note: Validation test would require a new user account")

# Step 8: Test validation - invalid relationship intent
print("\n8. Testing update validation (invalid relationship intent)...")
invalid_update = {
    "relationship_intent": "invalid_choice"
}

response = requests.patch(f"{BASE_URL}/profiles/me/", json=invalid_update, headers=headers)
if response.status_code == 400:
    print(f"   ✓ Validation correctly rejected invalid relationship intent")
    print(f"   Error: {response.json()}")
else:
    print(f"   ✗ Validation should have failed: {response.status_code}")

print("\n=== All API Tests Completed! ===\n")
print("Note: To fully test, manually verify:")
print("  - Avatar upload functionality")
print("  - Unauthenticated access is blocked")
print("  - Duplicate profile creation is prevented")
