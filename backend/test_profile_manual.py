"""
Manual test script to verify profile system implementation
Run with: python manage.py shell < test_profile_manual.py
"""

from django.contrib.auth import get_user_model
from profiles.models import Profile
import json

User = get_user_model()

print("\n=== Profile System Manual Test ===\n")

# Clean up any existing test data
User.objects.filter(email='profiletest@iiti.ac.in').delete()

# Create a test user
print("1. Creating test user...")
user = User.objects.create_user(
    username='profiletest',
    email='profiletest@iiti.ac.in',
    password='testpass123'
)
user.is_verified = True
user.save()
print(f"   ✓ User created: {user.email}")

# Create a profile
print("\n2. Creating profile...")
profile = Profile.objects.create(
    user=user,
    age=22,
    interests=['coding', 'music', 'reading'],
    hobbies=['guitar', 'hiking', 'photography'],
    relationship_intent='friendship',
    personality_tags=['introverted', 'creative', 'analytical'],
    bio='Test bio for profile system'
)
print(f"   ✓ Profile created with anonymous_id: {profile.anonymous_id}")
print(f"   ✓ Profile ID (UUID): {profile.id}")

# Verify UUID format
print("\n3. Verifying UUID format...")
import uuid
assert isinstance(profile.id, uuid.UUID), "Profile ID should be UUID"
assert isinstance(profile.anonymous_id, uuid.UUID), "Anonymous ID should be UUID"
print("   ✓ Both IDs are valid UUIDs")

# Verify no personal information in profile representation
print("\n4. Verifying anonymity...")
profile_str = str(profile)
assert user.email not in profile_str, "Email should not be in profile string representation"
assert str(profile.anonymous_id) in profile_str, "Anonymous ID should be in profile string"
print(f"   ✓ Profile representation: {profile_str}")
print("   ✓ No personal information exposed")

# Verify profile fields
print("\n5. Verifying profile fields...")
assert profile.age == 22, "Age should be 22"
assert profile.interests == ['coding', 'music', 'reading'], "Interests should match"
assert profile.hobbies == ['guitar', 'hiking', 'photography'], "Hobbies should match"
assert profile.relationship_intent == 'friendship', "Relationship intent should be friendship"
assert profile.personality_tags == ['introverted', 'creative', 'analytical'], "Personality tags should match"
print("   ✓ All profile fields stored correctly")

# Verify profile can be retrieved by anonymous_id
print("\n6. Verifying retrieval by anonymous_id...")
retrieved_profile = Profile.objects.get(anonymous_id=profile.anonymous_id)
assert retrieved_profile.id == profile.id, "Retrieved profile should match"
print(f"   ✓ Profile retrieved successfully by anonymous_id")

# Verify one-to-one relationship
print("\n7. Verifying one-to-one relationship...")
assert user.profile == profile, "User should have profile relationship"
assert profile.user == user, "Profile should have user relationship"
print("   ✓ One-to-one relationship working correctly")

# Test validation
print("\n8. Testing validation...")
try:
    invalid_profile = Profile(
        user=user,
        age=15,  # Invalid age
        interests=['test'],
        hobbies=['test'],
        relationship_intent='friendship',
        personality_tags=['test']
    )
    invalid_profile.full_clean()
    print("   ✗ Validation should have failed for age < 18")
except Exception as e:
    print(f"   ✓ Validation correctly rejected invalid age: {type(e).__name__}")

print("\n=== All Manual Tests Passed! ===\n")

# Cleanup
user.delete()
print("Test data cleaned up.")
