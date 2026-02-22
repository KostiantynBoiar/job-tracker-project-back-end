"""
Integration tests for NvidiaScraper.
Tests a single page fetch to verify API reachability and parse correctness.
Run with: pytest scrapers/tests/test_nvidia.py -v
"""
import pytest

from scrapers.base import ScrapedJob
from scrapers.providers.nvidia import NvidiaScraper


@pytest.fixture(scope="module")
def scraper():
    return NvidiaScraper()


@pytest.fixture(scope="module")
def postings(scraper):
    return scraper._fetch_page(0)


@pytest.fixture(scope="module")
def jobs(scraper, postings):
    return [scraper._parse(item) for item in postings]


def test_api_returns_postings(postings):
    assert len(postings) > 0


def test_all_items_are_scraped_jobs(jobs):
    assert all(isinstance(j, ScrapedJob) for j in jobs)


def test_external_id_non_empty(jobs):
    assert all(j.external_id for j in jobs)


def test_title_non_empty(jobs):
    assert all(j.title for j in jobs)


def test_external_url_format(jobs):
    for job in jobs:
        assert job.external_url.startswith(
            "https://nvidia.wd5.myworkdayjobs.com/en-us/NVIDIAExternalCareerSite"
        )


def test_no_duplicate_external_ids(jobs):
    ids = [j.external_id for j in jobs]
    assert len(ids) == len(set(ids))


def test_is_remote_is_bool(jobs):
    assert all(isinstance(j.is_remote, bool) for j in jobs)


def test_city_is_string_or_none(jobs):
    assert all(j.city is None or isinstance(j.city, str) for j in jobs)


def test_country_is_string_or_none(jobs):
    assert all(j.country is None or isinstance(j.country, str) for j in jobs)
