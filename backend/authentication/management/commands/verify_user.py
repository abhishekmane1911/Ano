"""
Management command to manually verify a user's email.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Manually verify a user email'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email address of the user to verify')

    def handle(self, *args, **options):
        email = options['email'].lower()

        try:
            user = User.objects.get(email=email)
            
            if user.is_verified:
                self.stdout.write(
                    self.style.WARNING(f'User {email} is already verified!')
                )
            else:
                user.is_verified = True
                user.is_active = True
                user.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully verified user {email}')
                )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nUser details:\n'
                    f'Email: {user.email}\n'
                    f'Username: {user.username}\n'
                    f'User ID: {user.id}\n'
                    f'Active: {user.is_active}\n'
                    f'Verified: {user.is_verified}\n'
                    f'\nYou can now login with this account!'
                )
            )
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User with email {email} not found!')
            )
