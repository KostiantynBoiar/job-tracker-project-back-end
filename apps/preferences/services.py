from django.db import models as db_models
from apps.jobs.models import Job
from .models import UserPreference, UserKeyword, DailyRecap, RecapJob
from .exceptions import PreferenceNotFoundException, PreferenceAlreadyExistsException
from django.db.models import Case, When

class PreferenceService:

    @staticmethod
    def get_or_create(user):
        pref, _ = UserPreference.objects.get_or_create(user=user)
        return pref

    @staticmethod
    def update(user, data: dict):
        pref = PreferenceService.get_or_create(user)
        for field, value in data.items():
            setattr(pref, field, value)
        pref.save()
        return pref

    # --- Companies ---

    @staticmethod
    def add_company(user, company):
        pref = PreferenceService.get_or_create(user)
        if pref.preferred_companies.filter(id=company.id).exists():
            raise PreferenceAlreadyExistsException()
        pref.preferred_companies.add(company)

    @staticmethod
    def remove_company(user, company_id: int):
        pref = PreferenceService.get_or_create(user)
        if not pref.preferred_companies.filter(id=company_id).exists():
            raise PreferenceNotFoundException()
        pref.preferred_companies.remove(pref.preferred_companies.get(id=company_id))

    # --- Categories ---

    @staticmethod
    def add_category(user, category):
        pref = PreferenceService.get_or_create(user)
        if pref.preferred_categories.filter(id=category.id).exists():
            raise PreferenceAlreadyExistsException()
        pref.preferred_categories.add(category)

    @staticmethod
    def remove_category(user, category_id: int):
        pref = PreferenceService.get_or_create(user)
        if not pref.preferred_categories.filter(id=category_id).exists():
            raise PreferenceNotFoundException()
        pref.preferred_categories.remove(pref.preferred_categories.get(id=category_id))

    # --- Locations ---

    @staticmethod
    def add_location(user, location):
        pref = PreferenceService.get_or_create(user)
        if pref.preferred_locations.filter(id=location.id).exists():
            raise PreferenceAlreadyExistsException()
        pref.preferred_locations.add(location)

    @staticmethod
    def remove_location(user, location_id: int):
        pref = PreferenceService.get_or_create(user)
        if not pref.preferred_locations.filter(id=location_id).exists():
            raise PreferenceNotFoundException()
        pref.preferred_locations.remove(pref.preferred_locations.get(id=location_id))

    # --- Keywords ---

    @staticmethod
    def add_keyword(user, keyword: str):
        _, created = UserKeyword.objects.get_or_create(user=user, keyword=keyword)
        if not created:
            raise PreferenceAlreadyExistsException()

    @staticmethod
    def remove_keyword(user, keyword_id: int):
        try:
            UserKeyword.objects.get(id=keyword_id, user=user).delete()
        except UserKeyword.DoesNotExist:
            raise PreferenceNotFoundException()


class RecommendationService:
    """
    Scores and ranks active jobs against a user's preferences.

    Scoring weights:
      +3  job company is in user's preferred companies
      +2  job category is in user's preferred categories
      +2  job location is in user's preferred locations
      +2  each keyword found in job title
      +1  each keyword found in job description (not title)
    """

    @staticmethod
    def get_recommended_jobs(user, limit: int = 20) -> list:
        """Returns a list of recommended jobs (limited)."""
        return list(RecommendationService.get_recommended_jobs_queryset(user)[:limit])

    @staticmethod
    def get_recommended_jobs_queryset(user):
        """
        Returns a queryset of recommended jobs sorted by score.
        Used for pagination in views.
        """
        qs = Job.objects.filter(is_active=True).select_related(
            'company', 'location', 'category'
        )

        try:
            prefs = user.preference
        except UserPreference.DoesNotExist:
            # No preferences set — return latest jobs
            return qs.order_by('-posted_at')

        # Hard filters
        if prefs.remote_only:
            qs = qs.filter(
                db_models.Q(is_remote=True) | db_models.Q(location__is_remote=True)
            )
        if prefs.min_salary:
            qs = qs.filter(
                db_models.Q(salary_max__gte=prefs.min_salary) |
                db_models.Q(salary_max__isnull=True)
            )
        if prefs.experience_level:
            qs = qs.filter(experience_level=prefs.experience_level)

        # Preference sets for scoring
        preferred_company_ids = set(
            prefs.preferred_companies.values_list('id', flat=True)
        )
        preferred_category_ids = set(
            prefs.preferred_categories.values_list('id', flat=True)
        )
        preferred_location_ids = set(
            prefs.preferred_locations.values_list('id', flat=True)
        )
        keywords = list(prefs.keywords.values_list('keyword', flat=True))

        # If no preferences are set, return by date
        if not any([preferred_company_ids, preferred_category_ids, preferred_location_ids, keywords]):
            return qs.order_by('-posted_at')

        scored = []
        for job in qs:
            score = RecommendationService._score(
                job, preferred_company_ids, preferred_category_ids,
                preferred_location_ids, keywords,
            )
            scored.append((score, job))

        scored.sort(key=lambda x: (
            -x[0],
            -(x[1].posted_at.timestamp() if x[1].posted_at else 0),
        ))
        
        # Return a list that can be sliced by pagination
        # We preserve the order by returning job IDs in scored order
        job_ids = [job.id for _, job in scored]
        

        preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(job_ids)])
        return Job.objects.filter(pk__in=job_ids).select_related(
            'company', 'location', 'category'
        ).order_by(preserved_order)

    @staticmethod
    def _score(job, company_ids, category_ids, location_ids, keywords) -> int:
        score = 0

        if company_ids and job.company_id in company_ids:
            score += 3
        if category_ids and job.category_id and job.category_id in category_ids:
            score += 2
        if location_ids and job.location_id and job.location_id in location_ids:
            score += 2

        if keywords:
            title_lower = job.title.lower()
            desc_lower = (job.description or '').lower()
            for kw in keywords:
                if kw in title_lower:
                    score += 2
                elif kw in desc_lower:
                    score += 1

        return score
