"""
One-time production setup command.
Loads compendium fixtures and creates the initial superuser.
Skips safely if data already exists.
"""
import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User


FIXTURES = [
    'compendium/fixtures/initialdata_base.json',
    'compendium/fixtures/initialdata_dependent_fixed.json',
    'compendium/fixtures/weapondice.json',
    'compendium/fixtures/weaponscaling.json',
    'compendium/fixtures/weaponrequirements.json',
    'compendium/fixtures/spelldice.json',
    'compendium/fixtures/spellrequirements.json',
    'compendium/fixtures/spellcharged.json',
    'compendium/fixtures/spellchargeddice.json',
    'compendium/fixtures/backgrounds.json',
    'compendium/fixtures/lineages.json',
    'compendium/fixtures/weaponproffeats_fixture.json',
    'compendium/fixtures/spirits_fixture.json',
    'compendium/fixtures/items_full.json',
    'compendium/fixtures/rings_full.json',
]


class Command(BaseCommand):
    help = 'Load compendium fixtures and create initial superuser'

    def handle(self, *args, **options):
        # Load fixtures
        from compendium.models import Weapon
        if Weapon.objects.count() == 0:
            self.stdout.write('Loading compendium fixtures...')
            for fixture in FIXTURES:
                try:
                    call_command('loaddata', fixture, verbosity=0)
                    self.stdout.write(f'  Loaded {fixture}')
                except Exception as e:
                    self.stdout.write(f'  FAILED {fixture}: {e}')
            self.stdout.write(self.style.SUCCESS('Compendium data loaded.'))
        else:
            self.stdout.write('Compendium data already exists, skipping fixtures.')

        # Create superuser
        if not User.objects.filter(username='bell').exists():
            user = User.objects.create_superuser(
                username='bell',
                email='belminsestic55@gmail.com',
                password='Kjhhjkkk1!'
            )
            self.stdout.write(self.style.SUCCESS(f'Superuser "bell" created.'))

            # Create UserProfile for the superuser
            from accounts.models import UserProfile
            if not hasattr(user, 'profile'):
                UserProfile.objects.create(
                    user=user,
                    user_type='permanent',
                    subscription_status='active_patron',
                    is_admin=True,
                    max_characters=50,
                    max_campaigns_as_gm=20,
                )
                self.stdout.write(self.style.SUCCESS('UserProfile created for "bell".'))
        else:
            self.stdout.write('Superuser "bell" already exists, skipping.')
