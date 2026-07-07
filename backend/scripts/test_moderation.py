#!/usr/bin/env python
"""
Test script to verify AI moderation is working
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ano_backend.settings')
django.setup()

from moderation.services import ModerationService, LocalModerator

def test_local_moderation():
    """Test local moderation with various messages"""
    print("=" * 60)
    print("TESTING LOCAL AI MODERATION")
    print("=" * 60)
    
    moderator = LocalModerator()
    
    test_cases = [
        ("Hello, how are you?", False),
        ("This is stupid", True),
        ("You are an idiot", True),
        ("I hate everything", True),
        ("Nice weather today!", False),
        ("kill yourself", True),
    ]
    
    print("\nTest Results:")
    print("-" * 60)
    
    for content, should_flag in test_cases:
        result = moderator.check_content(content)
        flagged = result['flagged']
        toxicity = result['toxicity_score']
        categories = result['categories']
        
        status = "✓ PASS" if flagged == should_flag else "✗ FAIL"
        
        print(f"\n{status}")
        print(f"Message: '{content}'")
        print(f"Expected: {'FLAGGED' if should_flag else 'CLEAN'}")
        print(f"Got: {'FLAGGED' if flagged else 'CLEAN'}")
        print(f"Toxicity: {toxicity:.2f}")
        print(f"Categories: {categories}")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)

if __name__ == '__main__':
    test_local_moderation()
