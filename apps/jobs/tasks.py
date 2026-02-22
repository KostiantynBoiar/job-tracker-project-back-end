import logging

import scrapers.providers  # noqa: F401
from celery import shared_task
from django.utils.timezone import now

from scrapers.factory import ScraperFactory
from apps.jobs.models import Company, Job, Location, ScrapeLog, ScrapeLogStatus

logger = logging.getLogger(__name__)

_LOG_INTERVAL = 50


@shared_task
def scrape_all():
    for slug in ScraperFactory.available():
        scrape_company.delay(slug)


@shared_task
def scrape_company(company_slug: str):
    try:
        company = Company.objects.get(name__iexact=company_slug, is_active=True)
    except Company.DoesNotExist:
        logger.warning('scrape_company: company "%s" not found or inactive', company_slug)
        return

    log = ScrapeLog.objects.create(
        company=company,
        started_at=now(),
        status=ScrapeLogStatus.RUNNING.value,
    )
    logger.info('[%s] scrape started', company_slug)

    jobs_found = 0
    jobs_new = 0

    try:
        for sj in ScraperFactory.get(company_slug).stream_jobs():
            location = None
            if sj.city or sj.country:
                location, _ = Location.objects.get_or_create(
                    city=sj.city or '',
                    state=sj.state or '',
                    country=sj.country or '',
                    is_remote=sj.is_remote,
                )

            optional = ['description', 'requirements', 'experience_level',
                        'employment_type', 'salary_min', 'salary_max', 'posted_at']
            defaults = {
                'company': company,
                'title': sj.title,
                'external_url': sj.external_url,
                'is_remote': sj.is_remote,
                'is_active': True,
                **{f: getattr(sj, f) for f in optional if getattr(sj, f) is not None},
            }
            if location:
                defaults['location'] = location

            _, created = Job.objects.update_or_create(
                external_id=sj.external_id,
                defaults=defaults,
            )

            jobs_found += 1
            if created:
                jobs_new += 1

            if jobs_found % _LOG_INTERVAL == 0:
                logger.info('[%s] progress: %d scraped, %d new', company_slug, jobs_found, jobs_new)
                log.jobs_found = jobs_found
                log.jobs_new = jobs_new
                log.save(update_fields=['jobs_found', 'jobs_new'])

        log.status = ScrapeLogStatus.SUCCESS.value
        log.jobs_found = jobs_found
        log.jobs_new = jobs_new
        log.finished_at = now()
        log.save()
        logger.info('[%s] scrape finished: %d scraped, %d new', company_slug, jobs_found, jobs_new)

    except Exception as exc:
        log.status = ScrapeLogStatus.FAILED.value
        log.error_message = str(exc)
        log.jobs_found = jobs_found
        log.jobs_new = jobs_new
        log.finished_at = now()
        log.save()
        logger.error('[%s] scrape failed after %d jobs: %s', company_slug, jobs_found, exc)
        raise
