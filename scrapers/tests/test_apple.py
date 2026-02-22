"""
Integration tests for AppleScraper.
Tests a single page fetch to verify API reachability and parse correctness.
Run with: pytest scrapers/tests/test_apple.py -v
"""
import pytest

from scrapers.base import ScrapedJob
from scrapers.providers.apple import AppleScraper


@pytest.fixture(scope="module")
def scraper():
    return AppleScraper()


@pytest.fixture(scope="module")
def page_data(scraper):
    return scraper._fetch_page(1)


@pytest.fixture(scope="module")
def jobs(scraper, page_data):
    return [scraper._parse(item) for item in page_data.get("searchResults", [])]


def test_api_returns_search_results(page_data):
    assert "searchResults" in page_data


def test_total_records_positive(page_data):
    assert page_data.get("totalRecords", 0) > 0


def test_page_has_jobs(jobs):
    assert len(jobs) > 0


def test_all_items_are_scraped_jobs(jobs):
    assert all(isinstance(j, ScrapedJob) for j in jobs)


def test_external_id_non_empty(jobs):
    assert all(j.external_id for j in jobs)


def test_title_non_empty(jobs):
    assert all(j.title for j in jobs)


def test_external_url_format(jobs):
    for job in jobs:
        assert job.external_url.startswith("https://jobs.apple.com/en-us/details/")


def test_external_url_contains_id(jobs):
    for job in jobs:
        assert job.external_id in job.external_url


def test_no_duplicate_external_ids(jobs):
    ids = [j.external_id for j in jobs]
    assert len(ids) == len(set(ids))


def test_is_remote_is_bool(jobs):
    assert all(isinstance(j.is_remote, bool) for j in jobs)


def test_city_is_string_or_none(jobs):
    assert all(j.city is None or isinstance(j.city, str) for j in jobs)


def test_country_is_string_or_none(jobs):
    assert all(j.country is None or isinstance(j.country, str) for j in jobs)


def test_posted_at_is_datetime_or_none(jobs):
    from datetime import datetime
    assert all(j.posted_at is None or isinstance(j.posted_at, datetime) for j in jobs)


def test_description_is_string_or_none(jobs):
    assert all(j.description is None or isinstance(j.description, str) for j in jobs)
