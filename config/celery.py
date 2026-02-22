import os

from celery import Celery
from celery.signals import worker_ready

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('job_tracker')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@worker_ready.connect
def on_worker_ready(**kwargs):
    from apps.jobs.tasks import scrape_all
    scrape_all.delay()
