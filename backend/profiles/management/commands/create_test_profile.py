"""
Management command to create a test profile for a user
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from profiles.models import Profile

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a test profile for a user'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='User email address')

    def handle(self, *args, **options):
        email = options['email']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with email {email} does not exist'))
            return
        
        # Check if profile already exists
        if hasattr(user, 'profile'):
            self.stdout.write(self.style.WARNING(f'Profile already exists for {email}'))
            self.stdout.write(f'Anonymous ID: {user.profile.anonymous_id}')
            return
        
        # Create profile
        profile = Profile.objects.create(
            user=user,
            age=22,
            interests=['coding', 'music', 'movies'],
            hobbies=['reading', 'gaming'],
            relationship_intent='friendship',
            personality_tags=['introverted', 'creative', 'tech-savvy'],
            bio='Test profile for development'
        )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Profile created for {email}'))
        self.stdout.write(f'  Anonymous ID: {profile.anonymous_id}')
        self.stdout.write(f'  Profile ID: {profile.id}')
