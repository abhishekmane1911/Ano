#!/usr/bin/env python
"""
Manual test script for search API endpoint
Run with: python test_search_api_manual.py
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ano_backend.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import force_authenticate
from chat.views import search_messages
from profiles.models import Profile

User = get_user_model()

def test_search_api():
    """Test the search API endpoint"""
    print("=" * 60)
    print("Testing Search API Endpoint")
    print("=" * 60)
    
    # Get test user
    print("\n1. Getting test user...")
    try:
        user = User.objects.get(email='test1@iiti.ac.in')
        print(f"   ✓ Found user: {user.email}")
    except User.DoesNotExist:
        print("   ❌ Test user not found. Run test_search_manual.py first.")
        return
    
    # Create request factory
    factory = RequestFactory()
    
    # Test search with query
    print("\n2. Testing search with query 'python'...")
    request = factory.get('/api/chat/search/', {'q': 'python'})
    force_authenticate(request, user=user)
    
    response = search_messages(request)
    print(f"   Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.data
        print(f"   ✓ Query: {data['query']}")
        print(f"   ✓ Count: {data['count']}")
        print(f"   ✓ Results: {len(data['results'])}")
        
        if data['results']:
            result = data['results'][0]
            print(f"\n   First result:")
            print(f"     - ID: {result['id']}")
            print(f"     - Content: {result['content'][:50]}...")
            print(f"     - Highlighted: {result['highlighted_content'][:60]}...")
            print(f"     - Chatroom: {result['chatroom_name']}")
    else:
        print(f"   ❌ Error: {response.data}")
    
    # Test search without query
    print("\n3. Testing search without query...")
    request = factory.get('/api/chat/search/')
    force_authenticate(request, user=user)
    
    response = search_messages(request)
    print(f"   Status code: {response.status_code}")
    if response.status_code == 400:
        print(f"   ✓ Correctly rejected: {response.data}")
    
    # Test search with different queries
    print("\n4. Testing multiple search queries...")
    queries = ['coding', 'anonymous', 'machine learning']
    
    for query in queries:
        request = factory.get('/api/chat/search/', {'q': query})
        force_authenticate(request, user=user)
        response = search_messages(request)
        
        if response.status_code == 200:
            count = response.data['count']
            print(f"   ✓ '{query}': {count} result(s)")
        else:
            print(f"   ❌ '{query}': Error")
    
    print("\n" + "=" * 60)
    print("Search API test completed!")
    print("=" * 60)

if __name__ == '__main__':
    try:
        test_search_api()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
