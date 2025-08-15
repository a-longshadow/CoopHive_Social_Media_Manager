"""
Management command to create hardcoded super admin users.

This command creates two super admin users:
- joe@coophive.network
- levi@coophive.network

These users are created without passwords and must use Google OAuth or password reset.
The command is idempotent and safe to run multiple times.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Create hardcoded super admin users for CoopHive'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update existing users to super admin status',
        )

    def handle(self, *args, **options):
        """Create or update super admin users."""
        super_admin_emails = [
            'joe@coophive.network',
            'levi@coophive.network'
        ]
        
        created_count = 0
        updated_count = 0
        
        with transaction.atomic():
            for email in super_admin_emails:
                try:
                    # Extract username from email (joe, levi)
                    username = email.split('@')[0]
                    
                    # Try to get existing user first
                    try:
                        user = User.objects.get(email=email)
                        user_existed = True
                    except User.DoesNotExist:
                        user_existed = False
                        
                        # Create new user
                        user = User.objects.create_user(
                            email=email,
                            username=username,
                        )
                        # Set unusable password (they'll use OAuth or reset)
                        user.set_unusable_password()
                    
                    # Ensure user has super admin privileges
                    needs_update = False
                    if not user.is_superuser:
                        user.is_superuser = True
                        needs_update = True
                    
                    if not user.is_staff:
                        user.is_staff = True
                        needs_update = True
                    
                    if not user.is_active:
                        user.is_active = True
                        needs_update = True
                    
                    # Save if changes were made
                    if needs_update or not user_existed:
                        user.save()
                    
                    if user_existed:
                        if needs_update:
                            updated_count += 1
                            self.stdout.write(
                                self.style.WARNING(
                                    f'Updated existing user {email} to super admin'
                                )
                            )
                        else:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'User {email} already exists as super admin'
                                )
                            )
                    else:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Created super admin user: {email}'
                            )
                        )
                
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error processing {email}: {str(e)}'
                        )
                    )
                    raise
        
        # Summary
        if created_count > 0 or updated_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSummary: {created_count} users created, {updated_count} users updated'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    '\nAll super admin users already exist and are properly configured'
                )
            )
        
        # Check email configuration and provide instructions
        self._check_email_and_provide_instructions()

    def _check_email_and_provide_instructions(self):
        """Check email configuration and provide appropriate instructions."""
        try:
            from user_account_manager.utils import is_email_configured
            
            self.stdout.write(
                self.style.WARNING(
                    '\nNote: Super admin users have no password set.'
                )
            )
            
            if is_email_configured():
                self.stdout.write(
                    self.style.SUCCESS(
                        '✅ Email is configured. Super admins can:'
                    )
                )
                self.stdout.write('  1. Use Google OAuth to log in at /accounts/login/')
                self.stdout.write('  2. Reset password via email at /accounts/reset/')
                self.stdout.write(
                    self.style.SUCCESS(
                        '\nSuper admins can now access the system! 🎉'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        '⚠️  Email is not configured. Super admins can only:'
                    )
                )
                self.stdout.write('  1. Use Google OAuth to log in at /accounts/login/')
                self.stdout.write('')
                self.stdout.write(
                    self.style.ERROR(
                        'To enable password reset, configure email:'
                    )
                )
                self.stdout.write('  python manage.py init_email --check')
                self.stdout.write('  python manage.py init_email --help')
                
        except ImportError:
            # Fallback if utils not available
            self.stdout.write(
                self.style.WARNING(
                    'They must use Google OAuth or configure email for password reset.'
                )
            )
