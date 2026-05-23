"""Management command to create daily challenge."""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date


class Command(BaseCommand):
    help = 'Create daily challenge for today'

    def handle(self, *args, **options):
        from apps.education.models import Test, DailyChallenge, Subject
        today = date.today()

        if DailyChallenge.objects.filter(date=today).exists():
            self.stdout.write(self.style.WARNING(f'Daily challenge for {today} already exists.'))
            return

        # Pick a random active test
        import random
        tests = list(Test.objects.filter(is_active=True))
        if not tests:
            self.stdout.write(self.style.ERROR('No active tests found.'))
            return

        test = random.choice(tests)
        DailyChallenge.objects.create(date=today, test=test, bonus_xp=100)
        self.stdout.write(self.style.SUCCESS(f'Created daily challenge for {today}: {test.title_uz}'))
