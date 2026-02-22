from celery import shared_task
from django.contrib.auth import get_user_model


@shared_task
def send_daily_recaps():
    """
    Generates a DailyRecap for every active user with daily notification frequency
    and records which jobs were recommended.
    Runs on the Celery Beat schedule defined in settings.CELERY_BEAT_SCHEDULE.
    """
    from .models import UserPreference, DailyRecap, RecapJob
    from .services import RecommendationService

    User = get_user_model()

    users = User.objects.filter(
        is_active=True,
        preference__notification_frequency='daily',
    )

    for user in users:
        try:
            jobs = RecommendationService.get_recommended_jobs(user, limit=10)
            recap = DailyRecap.objects.create(
                user=user,
                jobs_count=len(jobs),
                status='sent',
            )
            if jobs:
                RecapJob.objects.bulk_create([
                    RecapJob(recap=recap, job=job) for job in jobs
                ])
        except Exception:
            DailyRecap.objects.create(user=user, jobs_count=0, status='failed')