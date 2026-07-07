#!/usr/bin/env python
"""
Database Cleanup Script
Removes test data and dummy entries from the production database
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ano_backend.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
django.setup()

from django.contrib.auth import get_user_model
from chat.models import Chatroom, Message
from profiles.models import Profile
from reputation.models import UserReputation, MessageRanking, Vote
from moderation.models import ModerationResult, ViolationHistory, Shadowban
from security.models import RateLimitRecord, SecurityEvent

User = get_user_model()


def cleanup_test_chatrooms():
    """Remove test chatrooms"""
    print("\n🧹 Cleaning up test chatrooms...")
    
    test_chatrooms = Chatroom.objects.filter(name__icontains='test')
    count = test_chatrooms.count()
    
    if count > 0:
        print(f"   Found {count} test chatrooms:")
        for room in test_chatrooms:
            print(f"   - {room.name}: {room.description}")
        
        confirm = input(f"\n   Delete these {count} chatrooms? (yes/no): ")
        if confirm.lower() == 'yes':
            test_chatrooms.delete()
            print(f"   ✓ Deleted {count} test chatrooms")
        else:
            print("   ✗ Skipped chatroom cleanup")
    else:
        print("   ✓ No test chatrooms found")


def cleanup_test_users():
    """Remove test users (non-IITI emails)"""
    print("\n🧹 Cleaning up test users...")
    
    # Find users with test-related emails that aren't IITI emails
    test_users = User.objects.filter(
        email__icontains='test'
    ).exclude(
        email__endswith='@iiti.ac.in'
    )
    
    # Also find load test and performance test users
    load_test_users = User.objects.filter(email__icontains='loadtest')
    perf_test_users = User.objects.filter(email__icontains='perf')
    
    all_test_users = (test_users | load_test_users | perf_test_users).distinct()
    count = all_test_users.count()
    
    if count > 0:
        print(f"   Found {count} test users:")
        for user in all_test_users[:10]:  # Show first 10
            print(f"   - {user.email}")
        if count > 10:
            print(f"   ... and {count - 10} more")
        
        confirm = input(f"\n   Delete these {count} users? (yes/no): ")
        if confirm.lower() == 'yes':
            all_test_users.delete()
            print(f"   ✓ Deleted {count} test users")
        else:
            print("   ✗ Skipped user cleanup")
    else:
        print("   ✓ No test users found")


def cleanup_old_rate_limit_records():
    """Remove old rate limit records (older than 24 hours)"""
    print("\n🧹 Cleaning up old rate limit records...")
    
    from django.utils import timezone
    from datetime import timedelta
    
    cutoff_time = timezone.now() - timedelta(hours=24)
    old_records = RateLimitRecord.objects.filter(timestamp__lt=cutoff_time)
    count = old_records.count()
    
    if count > 0:
        old_records.delete()
        print(f"   ✓ Deleted {count} old rate limit records")
    else:
        print("   ✓ No old rate limit records found")


def cleanup_expired_shadowbans():
    """Remove expired shadowbans"""
    print("\n🧹 Cleaning up expired shadowbans...")
    
    from django.utils import timezone
    
    expired_bans = Shadowban.objects.filter(
        expires_at__lt=timezone.now(),
        is_active=True
    )
    count = expired_bans.count()
    
    if count > 0:
        expired_bans.update(is_active=False)
        print(f"   ✓ Deactivated {count} expired shadowbans")
    else:
        print("   ✓ No expired shadowbans found")


def cleanup_expired_violations():
    """Remove expired violations"""
    print("\n🧹 Cleaning up expired violations...")
    
    from django.utils import timezone
    
    expired_violations = ViolationHistory.objects.filter(
        expires_at__lt=timezone.now(),
        is_active=True
    )
    count = expired_violations.count()
    
    if count > 0:
        expired_violations.update(is_active=False)
        print(f"   ✓ Deactivated {count} expired violations")
    else:
        print("   ✓ No expired violations found")


def show_database_stats():
    """Show current database statistics"""
    print("\n📊 Database Statistics:")
    print(f"   Total users: {User.objects.count()}")
    print(f"   Total profiles: {Profile.objects.count()}")
    print(f"   Total chatrooms: {Chatroom.objects.count()}")
    print(f"   Total messages: {Message.objects.count()}")
    print(f"   Total votes: {Vote.objects.count()}")
    print(f"   Active shadowbans: {Shadowban.objects.filter(is_active=True).count()}")
    print(f"   Active violations: {ViolationHistory.objects.filter(is_active=True).count()}")
    print(f"   Security events: {SecurityEvent.objects.count()}")


def main():
    """Main cleanup function"""
    print("=" * 60)
    print("🗑️  Database Cleanup Script")
    print("=" * 60)
    
    # Show current stats
    show_database_stats()
    
    # Run cleanup operations
    cleanup_test_chatrooms()
    cleanup_test_users()
    cleanup_old_rate_limit_records()
    cleanup_expired_shadowbans()
    cleanup_expired_violations()
    
    # Show final stats
    print("\n" + "=" * 60)
    print("✅ Cleanup Complete!")
    print("=" * 60)
    show_database_stats()
    
    print("\n🎯 Recommendations:")
    print("   1. Review remaining data for any anomalies")
    print("   2. Run database vacuum/optimize if needed")
    print("   3. Update database statistics")
    print("   4. Test application functionality")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Cleanup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
