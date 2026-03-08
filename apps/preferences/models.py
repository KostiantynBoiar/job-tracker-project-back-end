from django.db import models
from django.contrib.auth import get_user_model
from enum import Enum

User = get_user_model()


class NotificationFrequency(str, Enum):
    DAILY = 'daily'
    WEEKLY = 'weekly'
    NEVER = 'never'

    @classmethod
    def choices(cls):
        return [(c.value, c.value.capitalize()) for c in cls]


class RecapStatus(str, Enum):
    PENDING = 'pending'
    SENT = 'sent'
    FAILED = 'failed'

    @classmethod
    def choices(cls):
        return [(c.value, c.value.capitalize()) for c in cls]


class UserPreference(models.Model):
    """
    Stores per-user job preference settings used for recommendations.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='preference',
    )
    experience_level = models.CharField(max_length=20, blank=True, null=True)
    min_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    remote_only = models.BooleanField(default=False)
    notification_frequency = models.CharField(
        max_length=10,
        choices=NotificationFrequency.choices(),
        default=NotificationFrequency.DAILY.value,
    )
    preferred_send_time = models.TimeField(default='09:00:00')
    preferred_companies = models.ManyToManyField(
        'companies.Company',
        blank=True,
        related_name='preferred_by_users',
    )
    preferred_categories = models.ManyToManyField(
        'jobs.JobCategory',
        blank=True,
        related_name='preferred_by_users',
    )
    preferred_locations = models.ManyToManyField(
        'jobs.Location',
        blank=True,
        related_name='preferred_by_users',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_preferences'

    def __str__(self):
        return f"Preferences for {self.user.email}"


class UserKeyword(models.Model):
    """
    Keywords a user wants matched against job titles/descriptions.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='keywords',
    )
    keyword = models.CharField(max_length=100)

    class Meta:
        db_table = 'user_keywords'
        unique_together = [['user', 'keyword']]

    def __str__(self):
        return f"{self.user.email}: {self.keyword}"


class DailyRecap(models.Model):
    """
    Record of a daily recommendation email sent to a user.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='daily_recaps',
    )
    jobs_count = models.IntegerField(default=0)
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=RecapStatus.choices(),
        default=RecapStatus.PENDING.value,
    )

    class Meta:
        db_table = 'daily_recaps'
        ordering = ['-sent_at']

    def __str__(self):
        return f"Recap for {self.user.email} [{self.status}] @ {self.sent_at}"


class RecapJob(models.Model):
    """
    Tracks which jobs were included in a daily recap and if they were clicked.
    """
    recap = models.ForeignKey(
        DailyRecap,
        on_delete=models.CASCADE,
        related_name='recap_jobs',
    )
    job = models.ForeignKey(
        'jobs.Job',
        on_delete=models.CASCADE,
    )
    was_clicked = models.BooleanField(default=False)

    class Meta:
        db_table = 'recap_jobs'
        unique_together = [['recap', 'job']]
