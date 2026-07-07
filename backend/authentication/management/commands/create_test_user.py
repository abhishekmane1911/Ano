"""
Management command to create a test user for development.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a test user for development'

    def handle(self, *args, **options):
        email = 'test@iiti.ac.in'
        password = 'testpass123'
        username = 'testuser'

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'User {email} already exists!')
            )
            user = User.objects.get(email=email)
            # Update password
            user.set_password(password)
            user.is_active = True
            user.is_verified = True
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Updated password for {email}')
            )
        else:
            # Create new user
            user = User.objects.create_user(
                email=email,
                username=username,
                password=password,
                is_active=True,
                is_verified=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created user {email}')
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nTest user credentials:\n'
                f'Email: {email}\n'
                f'Password: {password}\n'
                f'User ID: {user.id}\n'
                f'Active: {user.is_active}\n'
                f'Verified: {user.is_verified}\n'
            )
        )
