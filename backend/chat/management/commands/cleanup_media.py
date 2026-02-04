"""
Management command to clean up orphaned media files.
Usage: python manage.py cleanup_media
"""
from django.core.management.base import BaseCommand
from ano_backend.file_utils import cleanup_orphaned_files


class Command(BaseCommand):
    help = 'Clean up orphaned media files that are not referenced in the database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting files',
        )
    
    def handle(self, *args, **options):
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No files will be deleted')
            )
            # TODO: Implement dry run functionality
            return
        
        self.stdout.write('Starting media cleanup...')
        
        try:
            cleaned_count = cleanup_orphaned_files()
            
            if cleaned_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully cleaned up {cleaned_count} orphaned files'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('No orphaned files found')
                )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during cleanup: {str(e)}')
            )
            raise