from django.core.management.base import BaseCommand

from apps.companies.models import Company

_COMPANIES = [
    {
        'name': 'apple',
        'careers_url': 'https://jobs.apple.com/en-us/search',
        'logo_url': 'https://logo.clearbit.com/apple.com',
    },
    {
        'name': 'nvidia',
        'careers_url': 'https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite',
        'logo_url': 'https://logo.clearbit.com/nvidia.com',
    },
]


class Command(BaseCommand):
    help = 'Seed scraper-managed companies (apple, nvidia).'

    def handle(self, *args, **options):
        for data in _COMPANIES:
            company, created = Company.objects.update_or_create(
                name=data['name'],
                defaults={
                    'careers_url': data['careers_url'],
                    'logo_url': data['logo_url'],
                    'is_active': True,
                },
            )
            status = 'created' if created else 'updated'
            self.stdout.write(f'  {status}: {company.name}')
