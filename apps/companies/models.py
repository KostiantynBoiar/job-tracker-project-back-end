from django.db import models


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
