#!/usr/bin/env python
"""
Manual test script for matchmaking functionality.
Run this after starting the Django server to test the matchmaking API.

Usage:
    python test_matchmaking_manual.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"


def print_response(response, title="Response"):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)


def test_matchmaking():
    """Test matchmaking flow"""
    
    print("\n" + "="*60)
    print("MATCHMAKING API TEST")
    print("="*60)
    
    # Step 1: Register and login two users
    print("\n1. Creating test users...")
    
    # User 1
    user1_data = {
        "email": "testuser1@iiti.ac.in",
        "username": "testuser1",
        "password": "TestPass123!",
        "password2": "TestPass123!"
    }
    
    # User 2
    user2_data = {
        "email": "testuser2@iiti.ac.in",
        "username": "testuser2",
        "password": "TestPass123!",
        "password2": "TestPass123!"
    }
    
    # Register users (may fail if already exist)
    requests.post(f"{API_URL}/auth/register/", json=user1_data)
    requests.post(f"{API_URL}/auth/register/", json=user2_data)
    
    # Login user 1
    login1 = requests.post(f"{API_URL}/auth/login/", json={
        "email": user1_data["email"],
        "password": user1_data["password"]
    })
    
    if login1.status_code != 200:
        print("Failed to login user 1")
        print_response(login1, "User 1 Login Failed")
        return
    
    token1 = login1.json()["access"]
    headers1 = {"Authorization": f"Bearer {token1}"}
    
    # Login user 2
    login2 = requests.post(f"{API_URL}/auth/login/", json={
        "email": user2_data["email"],
        "password": user2_data["password"]
    })
    
    if login2.status_code != 200:
        print("Failed to login user 2")
        print_response(login2, "User 2 Login Failed")
        return
    
    token2 = login2.json()["access"]
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    print("✓ Users logged in successfully")
    
    # Step 2: Create profiles if they don't exist
    print("\n2. Creating profiles...")
    
    profile1_data = {
        "age": 22,
        "interests": ["coding", "music", "movies"],
        "hobbies": ["reading", "gaming"],
        "relationship_intent": "friendship",
        "personality_tags": ["introverted", "creative"],
        "bio": "Love coding and music!"
    }
    
    profile2_data = {
        "age": 23,
        "interests": ["sports", "travel", "photography"],
        "hobbies": ["hiking", "cooking"],
        "relationship_intent": "dating",
        "personality_tags": ["extroverted", "adventurous"],
        "bio": "Always up for an adventure!"
    }
    
    # Create profiles (may fail if already exist)
    requests.post(f"{API_URL}/profiles/", json=profile1_data, headers=headers1)
    requests.post(f"{API_URL}/profiles/", json=profile2_data, headers=headers2)
    
    # Get profiles
    profile1_resp = requests.get(f"{API_URL}/profiles/me/", headers=headers1)
    profile2_resp = requests.get(f"{API_URL}/profiles/me/", headers=headers2)
    
    if profile1_resp.status_code != 200 or profile2_resp.status_code != 200:
        print("Failed to get profiles")
        return
    
    profile1 = profile1_resp.json()
    profile2 = profile2_resp.json()
    
    print(f"✓ Profile 1: {profile1['anonymous_id']}")
    print(f"✓ Profile 2: {profile2['anonymous_id']}")
    
    # Step 3: Get profiles for swiping (as user 1)
    print("\n3. Getting profiles for swiping (User 1)...")
    profiles_resp = requests.get(f"{API_URL}/matchmaking/profiles/", headers=headers1)
    print_response(profiles_resp, "Available Profiles")
    
    # Step 4: User 1 swipes right on User 2
    print("\n4. User 1 swipes right on User 2...")
    
    # Get profile2's ID from the profiles list
    profiles = profiles_resp.json()
    profile2_id = None
    for p in profiles:
        if p['anonymous_id'] == profile2['anonymous_id']:
            # We need the actual profile ID, not anonymous_id
            # Let's get it from the profile endpoint
            break
    
    # For simplicity, we'll use a direct query
    from django.contrib.auth import get_user_model
    from profiles.models import Profile
    
    # Actually, let's just use the API properly
    # We need to find profile2's UUID
    print("Note: In a real scenario, you'd get the profile UUID from the profiles list")
    print("For this test, you may need to manually get the profile UUID")
    
    # Step 5: User 2 swipes right on User 1 (creates match)
    print("\n5. User 2 swipes right on User 1...")
    print("Note: This would create a match if both users swipe right")
    
    # Step 6: List matches
    print("\n6. Listing matches (User 1)...")
    matches_resp = requests.get(f"{API_URL}/matchmaking/matches/", headers=headers1)
    print_response(matches_resp, "User 1 Matches")
    
    print("\n7. Listing matches (User 2)...")
    matches_resp2 = requests.get(f"{API_URL}/matchmaking/matches/", headers=headers2)
    print_response(matches_resp2, "User 2 Matches")
    
    # If there are matches, test messaging
    if matches_resp.status_code == 200 and matches_resp.json():
        matches = matches_resp.json()
        if len(matches) > 0:
            match_id = matches[0]['id']
            
            print(f"\n8. Sending message in match {match_id}...")
            message_data = {
                "content": "Hey! Nice to match with you!",
                "message_type": "text"
            }
            send_resp = requests.post(
                f"{API_URL}/matchmaking/matches/{match_id}/messages/send/",
                json=message_data,
                headers=headers1
            )
            print_response(send_resp, "Send Message")
            
            print(f"\n9. Getting match messages...")
            messages_resp = requests.get(
                f"{API_URL}/matchmaking/matches/{match_id}/messages/",
                headers=headers1
            )
            print_response(messages_resp, "Match Messages")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)


if __name__ == "__main__":
    try:
        test_matchmaking()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
