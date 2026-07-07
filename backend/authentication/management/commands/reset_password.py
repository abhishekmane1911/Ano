"""
Management command to generate password reset URLs for users.
Useful for development and troubleshooting.

Usage:
    python manage.py reset_password user@iiti.ac.in
    python manage.py reset_password --list-users
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate password reset URL for a user'

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            nargs='?',
            type=str,
            help='Email address of the user'
        )
        parser.add_argument(
            '--list-users',
            action='store_true',
            help='List all active users'
        )

    def handle(self, *args, **options):
        if options['list_users']:
            self.list_users()
            return

        email = options.get('email')
        if not email:
            raise CommandError('Please provide an email address or use --list-users')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise CommandError(f'User with email "{email}" does not exist')

        if not user.is_active:
            self.stdout.write(
                self.style.WARNING(f'Warning: User {email} is not active')
            )

        # Generate reset token
        reset_token = user.generate_password_reset_token()

        # Generate reset URL
        reset_url = f"{settings.FRONTEND_URL}/password-reset-confirm?token={reset_token}"

        # Display results
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS('PASSWORD RESET URL GENERATED'))
        self.stdout.write("="*60)
        self.stdout.write(f"Email: {email}")
        self.stdout.write(f"User ID: {user.id}")
        self.stdout.write(f"Active: {user.is_active}")
        self.stdout.write(f"Verified: {user.is_verified}")
        self.stdout.write("\n" + self.style.HTTP_INFO("Reset URL:"))
        self.stdout.write(reset_url)
        self.stdout.write("\n" + self.style.HTTP_INFO("Token:"))
        self.stdout.write(str(reset_token))
        self.stdout.write("\n" + "="*60)
        self.stdout.write(
            self.style.SUCCESS(
                '\nCopy the URL above and paste it in your browser to reset the password'
            )
        )
        self.stdout.write("="*60 + "\n")

    def list_users(self):
        """List all active users"""
        users = User.objects.filter(is_active=True).order_by('-date_joined')
        
        if not users.exists():
            self.stdout.write(self.style.WARNING('No active users found'))
            return

        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS('ACTIVE USERS'))
        self.stdout.write("="*60)
        
        for user in users:
            self.stdout.write(
                f"\n{user.email}"
                f"\n  ID: {user.id}"
                f"\n  Username: {user.username}"
                f"\n  Verified: {user.is_verified}"
                f"\n  Joined: {user.date_joined.strftime('%Y-%m-%d %H:%M')}"
            )
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal: {users.count()} active users')
        )
        self.stdout.write("="*60 + "\n")
