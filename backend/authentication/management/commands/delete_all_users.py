"""
Management command to delete all users and related data.
Use with caution - this will delete ALL users from the database!
"""
# from security.models import HashedIdentity
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from profiles.models import Profile
# from security.models import HashedIdentity
from chat.models import Message
from matchmaking.models import Match
from reports.models import Report

User = get_user_model()


class Command(BaseCommand):
    help = 'Delete all users and related data from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of all users',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This command will delete ALL users and related data!\n'
                    'Run with --confirm flag to proceed:\n'
                    'python manage.py delete_all_users --confirm'
                )
            )
            return

        self.stdout.write(self.style.WARNING('Starting deletion process...'))

        # Count before deletion
        user_count = User.objects.count()
        profile_count = Profile.objects.count()
        # hashed_identity_count = HashedIdentity.objects.count()
        message_count = Message.objects.count()
        match_count = Match.objects.count()
        report_count = Report.objects.count()

        self.stdout.write(f'Found {user_count} users')
        self.stdout.write(f'Found {profile_count} profiles')
        # self.stdout.write(f'Found {hashed_identity_count} hashed identities')
        self.stdout.write(f'Found {message_count} messages')
        self.stdout.write(f'Found {match_count} matches')
        self.stdout.write(f'Found {report_count} reports')

        # Delete in order (related data first due to foreign keys)
        self.stdout.write('\nDeleting reports...')
        Report.objects.all().delete()
        
        self.stdout.write('Deleting messages...')
        Message.objects.all().delete()
        
        self.stdout.write('Deleting matches...')
        Match.objects.all().delete()
        
        self.stdout.write('Deleting profiles...')
        Profile.objects.all().delete()
        
        # self.stdout.write('Deleting hashed identities...')
        # HashedIdentity.objects.all().delete()
        
        self.stdout.write('Deleting users...')
        User.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully deleted:\n'
                f'  - {user_count} users\n'
                f'  - {profile_count} profiles\n'
                f'  - {message_count} messages\n'
                f'  - {match_count} matches\n'
                f'  - {report_count} reports\n'
                f'\nDatabase is now clean. You can create new users.'
            )
        )
