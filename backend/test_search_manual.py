#!/usr/bin/env python
"""
Manual test script for message search functionality
Run with: python test_search_manual.py
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ano_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from profiles.models import Profile
from chat.models import Chatroom, Message
from matchmaking.models import Match
from django.contrib.postgres.search import SearchQuery

User = get_user_model()

def test_search_functionality():
    """Test the search functionality"""
    print("=" * 60)
    print("Testing Message Search Functionality")
    print("=" * 60)
    
    # Create test users and profiles
    print("\n1. Creating test users and profiles...")
    try:
        user1 = User.objects.get(email='test1@iiti.ac.in')
        profile1 = user1.profile
        print(f"   ℹ Using existing user1: {user1.email}")
        print(f"   ℹ Using existing profile1: {profile1.anonymous_id}")
    except User.DoesNotExist:
        user1 = User.objects.create_user(
            username='test1',
            email='test1@iiti.ac.in',
            password='testpass123'
        )
        user1.is_verified = True
        user1.save()
        profile1 = Profile.objects.create(
            user=user1,
            age=20,
            interests=['coding', 'music'],
            hobbies=['reading'],
            relationship_intent='friendship'
        )
        print(f"   ✓ Created user1: {user1.email}")
        print(f"   ✓ Created profile1: {profile1.anonymous_id}")
    
    # Create test chatroom
    print("\n2. Creating test chatroom...")
    chatroom, created = Chatroom.objects.get_or_create(
        name='Test Search Room',
        defaults={
            'description': 'Room for testing search',
            'is_active': True,
            'created_by': user1
        }
    )
    if created:
        print(f"   ✓ Created chatroom: {chatroom.name}")
    else:
        print(f"   ℹ Using existing chatroom: {chatroom.name}")
    
    # Create test messages with different content
    print("\n3. Creating test messages...")
    test_messages = [
        "Hello everyone, this is a test message",
        "Python is an amazing programming language",
        "I love coding in Django and React",
        "Anonymous chatting is really cool",
        "Let's discuss machine learning algorithms"
    ]
    
    for content in test_messages:
        msg, created = Message.objects.get_or_create(
            chatroom=chatroom,
            sender=profile1,
            content=content,
            defaults={'message_type': 'text'}
        )
        if created:
            print(f"   ✓ Created message: {content[:40]}...")
    
    # Test search functionality
    print("\n4. Testing search queries...")
    
    test_queries = [
        'python',
        'coding',
        'anonymous',
        'test',
        'machine learning'
    ]
    
    for query in test_queries:
        print(f"\n   Searching for: '{query}'")
        search_query = SearchQuery(query)
        results = Message.objects.filter(
            chatroom=chatroom,
            is_deleted=False,
            search_vector=search_query
        )
        print(f"   Found {results.count()} result(s)")
        for msg in results:
            print(f"     - {msg.content[:60]}...")
    
    # Test search vector field
    print("\n5. Checking search_vector field...")
    sample_msg = Message.objects.filter(chatroom=chatroom).first()
    if sample_msg:
        print(f"   Message content: {sample_msg.content}")
        print(f"   Search vector exists: {sample_msg.search_vector is not None}")
    
    print("\n" + "=" * 60)
    print("Search functionality test completed!")
    print("=" * 60)
    
    # Cleanup
    print("\n6. Cleanup (optional - comment out to keep test data)")
    # Message.objects.filter(chatroom=chatroom).delete()
    # chatroom.delete()
    # profile1.delete()
    # user1.delete()
    print("   ℹ Test data preserved for manual testing")

if __name__ == '__main__':
    try:
        test_search_functionality()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
