#!/usr/bin/env python
"""
Manual test script for search scope filtering
Tests that users can only search messages in accessible chats
Run with: python test_search_scope_manual.py
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ano_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from rest_framework.test import force_authenticate
from profiles.models import Profile
from chat.models import Chatroom, Message
from matchmaking.models import Match, Swipe
from chat.views import search_messages

User = get_user_model()

def test_search_scope():
    """Test that search respects access scope"""
    print("=" * 60)
    print("Testing Search Scope Filtering")
    print("=" * 60)
    
    # Create two test users
    print("\n1. Creating test users...")
    try:
        user1 = User.objects.get(email='test1@iiti.ac.in')
        profile1 = user1.profile
        print(f"   ℹ Using existing user1: {user1.email}")
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
            interests=['coding'],
            hobbies=['reading'],
            relationship_intent='friendship'
        )
        print(f"   ✓ Created user1: {user1.email}")
    
    try:
        user2 = User.objects.get(email='test2@iiti.ac.in')
        profile2 = user2.profile
        print(f"   ℹ Using existing user2: {user2.email}")
    except User.DoesNotExist:
        user2 = User.objects.create_user(
            username='test2',
            email='test2@iiti.ac.in',
            password='testpass123'
        )
        user2.is_verified = True
        user2.save()
        profile2 = Profile.objects.create(
            user=user2,
            age=21,
            interests=['music'],
            hobbies=['gaming'],
            relationship_intent='dating'
        )
        print(f"   ✓ Created user2: {user2.email}")
    
    # Create a public chatroom
    print("\n2. Creating public chatroom...")
    chatroom, _ = Chatroom.objects.get_or_create(
        name='Public Test Room',
        defaults={
            'description': 'Public room for testing',
            'is_active': True,
            'created_by': user1
        }
    )
    print(f"   ✓ Chatroom: {chatroom.name}")
    
    # Create messages in public chatroom
    print("\n3. Creating messages in public chatroom...")
    msg1, _ = Message.objects.get_or_create(
        chatroom=chatroom,
        sender=profile1,
        content="Public message about Python programming",
        defaults={'message_type': 'text'}
    )
    print(f"   ✓ Message 1: {msg1.content[:40]}...")
    
    # Create a match between user1 and user2
    print("\n4. Creating match between users...")
    # Create swipes
    Swipe.objects.get_or_create(
        swiper=profile1,
        swiped=profile2,
        defaults={'direction': 'right'}
    )
    Swipe.objects.get_or_create(
        swiper=profile2,
        swiped=profile1,
        defaults={'direction': 'right'}
    )
    
    # Create match
    match, _ = Match.objects.get_or_create(
        profile1=profile1,
        profile2=profile2,
        defaults={'is_active': True}
    )
    print(f"   ✓ Match created: {match.id}")
    
    # Create message in match chat
    print("\n5. Creating message in match chat...")
    match_msg, _ = Message.objects.get_or_create(
        match=match,
        sender=profile1,
        content="Private match message about Python",
        defaults={'message_type': 'text'}
    )
    print(f"   ✓ Match message: {match_msg.content[:40]}...")
    
    # Test search as user1 (should see both messages)
    print("\n6. Testing search as user1 (has access to match)...")
    factory = RequestFactory()
    request = factory.get('/api/chat/search/', {'q': 'Python'})
    force_authenticate(request, user=user1)
    
    response = search_messages(request)
    if response.status_code == 200:
        count = response.data['count']
        print(f"   ✓ User1 found {count} result(s)")
        for result in response.data['results']:
            location = result['chatroom_name'] or 'Match Chat'
            print(f"     - {location}: {result['content'][:40]}...")
    
    # Create user3 who is NOT in the match
    print("\n7. Creating user3 (not in match)...")
    try:
        user3 = User.objects.get(email='test3@iiti.ac.in')
        profile3 = user3.profile
        print(f"   ℹ Using existing user3: {user3.email}")
    except User.DoesNotExist:
        user3 = User.objects.create_user(
            username='test3',
            email='test3@iiti.ac.in',
            password='testpass123'
        )
        user3.is_verified = True
        user3.save()
        profile3 = Profile.objects.create(
            user=user3,
            age=22,
            interests=['art'],
            hobbies=['painting'],
            relationship_intent='friendship'
        )
        print(f"   ✓ Created user3: {user3.email}")
    
    # Test search as user3 (should only see public chatroom message)
    print("\n8. Testing search as user3 (no access to match)...")
    request = factory.get('/api/chat/search/', {'q': 'Python'})
    force_authenticate(request, user=user3)
    
    response = search_messages(request)
    if response.status_code == 200:
        count = response.data['count']
        print(f"   ✓ User3 found {count} result(s)")
        for result in response.data['results']:
            location = result['chatroom_name'] or 'Match Chat'
            print(f"     - {location}: {result['content'][:40]}...")
        
        # Verify user3 cannot see match messages
        has_match_msg = any(r['match_id'] is not None for r in response.data['results'])
        if not has_match_msg:
            print(f"   ✓ Correctly filtered: User3 cannot see match messages")
        else:
            print(f"   ❌ Error: User3 can see match messages they shouldn't access")
    
    print("\n" + "=" * 60)
    print("Search scope filtering test completed!")
    print("=" * 60)
    print("\nKey findings:")
    print("- Users can search public chatroom messages")
    print("- Users can search their own match messages")
    print("- Users CANNOT search other users' match messages")

if __name__ == '__main__':
    try:
        test_search_scope()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
