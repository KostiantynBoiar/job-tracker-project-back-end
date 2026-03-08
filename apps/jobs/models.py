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
        return [(choice.value, choice.label) for choice in cls]

    @property
    def label(self):
        labels = {
            'entry': 'Entry Level',
            'mid': 'Mid Level',
            'senior': 'Senior Level',
            'executive': 'Executive Level',
        }
        return labels.get(self.value, self.value)


class EmploymentType(str, Enum):
    """Employment type choices for jobs."""
    FULL_TIME = 'full_time'
    PART_TIME = 'part_time'
    CONTRACT = 'contract'
    FREELANCE = 'freelance'
    INTERNSHIP = 'internship'

    @classmethod
    def choices(cls):
        return [(c.value, c.value.replace('_', ' ').title()) for c in cls]


class ScrapeLogStatus(str, Enum):
    """Status choices for scrape logs."""
    RUNNING = 'running'
    SUCCESS = 'success'
    FAILED = 'failed'

    @classmethod
    def choices(cls):
        return [(c.value, c.value.capitalize()) for c in cls]


class Location(models.Model):
    """
    Location model representing geographic job locations.
    """
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100)
    is_remote = models.BooleanField(default=False)

    class Meta:
        db_table = 'locations'
        unique_together = [['city', 'state', 'country', 'is_remote']]

    def __str__(self):
        parts = [p for p in [self.city, self.state, self.country] if p]
        label = ', '.join(parts)
        if self.is_remote:
            label += ' (Remote)'
        return label


class JobCategory(models.Model):
    """
    JobCategory model for categorising job postings.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        db_table = 'job_categories'
        verbose_name = 'Job Category'
        verbose_name_plural = 'Job Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Job(models.Model):
    """
    Job model representing job postings.
    """
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='jobs',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        related_name='jobs',
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        JobCategory,
        on_delete=models.SET_NULL,
        related_name='jobs',
        blank=True,
        null=True,
    )
    external_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices(),
        blank=True,
        null=True,
    )
    experience_level = models.CharField(
        max_length=20,
        choices=ExperienceLevel.choices(),
        blank=True,
        null=True,
    )
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_currency = models.CharField(max_length=10, default='USD', blank=True, null=True)
    external_url = models.URLField()
    is_remote = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
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
            models.Index(fields=['is_active']),
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
        return [(choice.value, choice.label) for choice in cls]

    @property
    def label(self):
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
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='saved_by_users',
    )
    status = models.CharField(
        max_length=20,
        choices=SavedJobStatus.choices(),
        default=SavedJobStatus.ACTIVE.value,
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


class ScrapeLog(models.Model):
    """
    ScrapeLog model for tracking scraping runs per company.
    """
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='scrape_logs',
    )
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(blank=True, null=True)
    jobs_found = models.IntegerField(default=0)
    jobs_new = models.IntegerField(default=0)
    status = models.CharField(
        max_length=10,
        choices=ScrapeLogStatus.choices(),
        default=ScrapeLogStatus.RUNNING.value,
    )
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'scrape_logs'
        ordering = ['-started_at']

    def __str__(self):
        return f"Scrape {self.company.name} [{self.status}] @ {self.started_at}"
