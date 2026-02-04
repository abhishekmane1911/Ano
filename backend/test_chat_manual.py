#!/usr/bin/env python
"""
Manual test script for Chat API endpoints
Run this after starting the Django server
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def print_response(response, title):
    """Print formatted response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def main():
    print("Chat API Manual Test")
    print("="*60)
    
    # Step 1: Register a user
    print("\n1. Registering user...")
    register_data = {
        "username": "chattest",
        "email": "chattest@iiti.ac.in",
        "password": "TestPass123!",
        "password2": "TestPass123!"
    }
    response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
    print_response(response, "Register User")
    
    if response.status_code != 201:
        print("\n⚠️  Registration failed. User might already exist.")
        print("Trying to login instead...")
    
    # Step 2: Login
    print("\n2. Logging in...")
    login_data = {
        "email": "chattest@iiti.ac.in",
        "password": "TestPass123!"
    }
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    print_response(response, "Login")
    
    if response.status_code != 200:
        print("\n❌ Login failed. Cannot continue tests.")
        return
    
    tokens = response.json()
    access_token = tokens.get('access')
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Step 3: Create profile if not exists
    print("\n3. Creating profile...")
    profile_data = {
        "age": 21,
        "interests": ["coding", "music"],
        "hobbies": ["reading", "gaming"],
        "relationship_intent": "friendship",
        "personality_tags": ["introverted", "creative"],
        "bio": "Test user for chat"
    }
    response = requests.post(f"{BASE_URL}/profiles/", json=profile_data, headers=headers)
    if response.status_code == 201:
        print_response(response, "Create Profile")
    else:
        print(f"Profile creation status: {response.status_code} (might already exist)")
    
    # Step 4: List chatrooms
    print("\n4. Listing chatrooms...")
    response = requests.get(f"{BASE_URL}/chat/chatrooms/", headers=headers)
    print_response(response, "List Chatrooms")
    
    chatrooms = response.json()
    
    # If no chatrooms exist, we can't test further
    if not chatrooms:
        print("\n⚠️  No chatrooms available. Please create a chatroom in Django admin first.")
        print("   python manage.py shell")
        print("   >>> from chat.models import Chatroom")
        print("   >>> Chatroom.objects.create(name='General', description='General chat')")
        return
    
    chatroom_id = chatrooms[0]['id']
    print(f"\nUsing chatroom: {chatrooms[0]['name']} (ID: {chatroom_id})")
    
    # Step 5: Get chatroom details
    print("\n5. Getting chatroom details...")
    response = requests.get(f"{BASE_URL}/chat/chatrooms/{chatroom_id}/", headers=headers)
    print_response(response, "Chatroom Details")
    
    # Step 6: Send a message
    print("\n6. Sending a message...")
    message_data = {
        "content": "Hello from the test script!",
        "message_type": "text"
    }
    response = requests.post(
        f"{BASE_URL}/chat/chatrooms/{chatroom_id}/send_message/",
        json=message_data,
        headers=headers
    )
    print_response(response, "Send Message")
    
    if response.status_code != 201:
        print("\n❌ Failed to send message. Cannot continue tests.")
        return
    
    message_id = response.json()['id']
    
    # Step 7: Get chatroom messages
    print("\n7. Getting chatroom messages...")
    response = requests.get(
        f"{BASE_URL}/chat/chatrooms/{chatroom_id}/messages/",
        headers=headers
    )
    print_response(response, "Chatroom Messages")
    
    # Step 8: Edit the message
    print("\n8. Editing the message...")
    edit_data = {
        "content": "Hello from the test script! (edited)"
    }
    response = requests.put(
        f"{BASE_URL}/chat/messages/{message_id}/",
        json=edit_data,
        headers=headers
    )
    print_response(response, "Edit Message")
    
    # Step 9: React to the message
    print("\n9. Reacting to the message...")
    reaction_data = {
        "emoji": "👍"
    }
    response = requests.post(
        f"{BASE_URL}/chat/messages/{message_id}/react/",
        json=reaction_data,
        headers=headers
    )
    print_response(response, "React to Message")
    
    # Step 10: Pin the message
    print("\n10. Pinning the message...")
    response = requests.post(
        f"{BASE_URL}/chat/messages/{message_id}/pin/",
        headers=headers
    )
    print_response(response, "Pin Message")
    
    # Step 11: Unpin the message
    print("\n11. Unpinning the message...")
    response = requests.post(
        f"{BASE_URL}/chat/messages/{message_id}/pin/",
        headers=headers
    )
    print_response(response, "Unpin Message")
    
    # Step 12: Delete the message
    print("\n12. Deleting the message...")
    response = requests.delete(
        f"{BASE_URL}/chat/messages/{message_id}/",
        headers=headers
    )
    print(f"\n{'='*60}")
    print("Delete Message")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 204:
        print("✅ Message deleted successfully")
    
    print("\n" + "="*60)
    print("✅ All chat API tests completed!")
    print("="*60)

if __name__ == "__main__":
    main()
