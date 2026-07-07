"""
Management command to migrate existing user emails to hashed format.
Part of the Advanced Gamification Modules - Security hardening.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from security.models import HashedIdentity
from security.services import IdentityHasher

User = get_user_model()


class Command(BaseCommand):
    help = 'Migrate existing user emails to hashed format for enhanced privacy'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force migration even if some users already have hashed identities',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS('Starting email hash migration...')
        )
        
        # Get users without hashed identities
        users_to_migrate = User.objects.filter(hashed_identity__isnull=True)
        total_users = users_to_migrate.count()
        
        if total_users == 0:
            self.stdout.write(
                self.style.WARNING('No users found that need email hash migration.')
            )
            return
        
        self.stdout.write(
            f'Found {total_users} users that need email hash migration.'
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made.')
            )
            for user in users_to_migrate[:10]:  # Show first 10
                self.stdout.write(f'Would migrate: {user.email}')
            if total_users > 10:
                self.stdout.write(f'... and {total_users - 10} more users')
            return
        
        # Confirm migration
        if not force:
            confirm = input(
                f'This will create hashed identities for {total_users} users. '
                'Continue? (y/N): '
            )
            if confirm.lower() != 'y':
                self.stdout.write('Migration cancelled.')
                return
        
        # Perform migration
        migrated_count = 0
        failed_count = 0
        
        with transaction.atomic():
            for user in users_to_migrate:
                try:
                    # Generate hash for user's email
                    email_hash, salt = IdentityHasher.hash_email(user.email)
                    
                    # Create hashed identity record
                    HashedIdentity.objects.create(
                        user=user,
                        email_hash=email_hash,
                        salt=salt
                    )
                    
                    migrated_count += 1
                    
                    if migrated_count % 100 == 0:
                        self.stdout.write(f'Migrated {migrated_count} users...')
                
                except Exception as e:
                    self.stderr.write(
                        f'Failed to migrate user {user.email}: {e}'
                    )
                    failed_count += 1
        
        # Report results
        self.stdout.write(
            self.style.SUCCESS(
                f'Migration completed! '
                f'Migrated: {migrated_count}, Failed: {failed_count}'
            )
        )
        
        if failed_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'{failed_count} users failed to migrate. '
                    'Check error messages above.'
                )
            )
        
        # Verify migration
        remaining_users = User.objects.filter(hashed_identity__isnull=True).count()
        if remaining_users == 0:
            self.stdout.write(
                self.style.SUCCESS('All users now have hashed identities!')
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'{remaining_users} users still need migration.'
                )
            )