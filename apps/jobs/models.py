from django.db import models
from django.contrib.auth import get_user_model
from enum import Enum

User = get_user_model()


class ExperienceLevel(str, Enum):
    """Experience level choices for jobs."""
    ENTRY = 'entry'
    MID = 'mid'
    SENIOR = 'senior'
    EXECUTIVE = 'executive'

    @classmethod
    def choices(cls):
        """Return choices in Django format."""
        return [(choice.value, choice.label) for choice in cls]

    @property
    def label(self):
        """Return human-readable label."""
        labels = {
            'entry': 'Entry Level',
            'mid': 'Mid Level',
            'senior': 'Senior Level',
            'executive': 'Executive Level',
        }
        return labels.get(self.value, self.value)


class Company(models.Model):
    """
    Company model representing job posting companies.
    """
    name = models.CharField(max_length=255, blank=False, null=False)
    logo_url = models.URLField(blank=True, null=True)
    careers_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'companies'
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Job(models.Model):
    """
    Job model representing job postings.
    """
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='jobs',
        blank=False,
        null=False
    )
    external_id = models.CharField(max_length=255, unique=True, blank=False, null=False)
    title = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    external_url = models.URLField(blank=False, null=False)
    experience_level = models.CharField(
        max_length=20,
        choices=ExperienceLevel.choices(),
        blank=True,
        null=True
    )
    is_remote = models.BooleanField(default=False)
    posted_at = models.DateTimeField(blank=True, null=True)
    scraped_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'jobs'
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['external_id']),
            models.Index(fields=['company']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.title} at {self.company.name}"


class SavedJobStatus(str, Enum):
    """Status choices for saved jobs."""
    ACTIVE = 'active'
    EXPIRED = 'expired'
    FRESH = 'fresh'

    @classmethod
    def choices(cls):
        """Return choices in Django format."""
        return [(choice.value, choice.label) for choice in cls]

    @property
    def label(self):
        """Return human-readable label."""
        labels = {
            'active': 'Active',
            'expired': 'Expired',
            'fresh': 'Fresh',
        }
        return labels.get(self.value, self.value)


class SavedJob(models.Model):
    """
    SavedJob model representing jobs saved by users.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_jobs',
        blank=False,
        null=False
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='saved_by_users',
        blank=False,
        null=False
    )
    status = models.CharField(
        max_length=20,
        choices=SavedJobStatus.choices(),
        default=SavedJobStatus.ACTIVE.value,
        blank=False,
        null=False
    )
    notes = models.TextField(blank=True, null=True)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'saved_jobs'
        verbose_name = 'Saved Job'
        verbose_name_plural = 'Saved Jobs'
        ordering = ['-saved_at']
        unique_together = [['user', 'job']]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['job']),
            models.Index(fields=['status']),
            models.Index(fields=['-saved_at']),
        ]

    def __str__(self):
        return f"{self.user.email} saved {self.job.title}"
