from typing import Iterator

import requests

from scrapers.base import BaseScraper, ScrapedJob
from scrapers.factory import ScraperFactory

_API_URL = (
    'https://nvidia.wd5.myworkdayjobs.com'
    '/wday/cxs/nvidia/NVIDIAExternalCareerSite/jobs'
)
_DETAIL_BASE = (
    'https://nvidia.wd5.myworkdayjobs.com'
    '/en-us/NVIDIAExternalCareerSite'
)
_PAGE_SIZE = 20


@ScraperFactory.register('nvidia')
class NvidiaScraper(BaseScraper):
    company_slug = 'nvidia'

    def stream_jobs(self) -> Iterator[ScrapedJob]:
        offset = 0

        while True:
            postings = self._fetch_page(offset)
            if not postings:
                break

            for item in postings:
                yield self._parse(item)

            if len(postings) < _PAGE_SIZE:
                break
            offset += _PAGE_SIZE

    def _fetch_page(self, offset: int) -> list[dict]:
        response = requests.post(
            _API_URL,
            json={
                'appliedFacets': {},
                'limit': _PAGE_SIZE,
                'offset': offset,
                'searchText': '',
            },
            headers={'Accept': 'application/json'},
            timeout=30,
        )
        response.raise_for_status()
        return response.json().get('jobPostings', [])

    def _parse(self, item: dict) -> ScrapedJob:
        path = item.get('externalPath', '')
        last_segment = path.rstrip('/').rsplit('/', 1)[-1]
        external_id = last_segment.rsplit('_', 1)[-1] if '_' in last_segment else last_segment

        loc = item.get('locationsText', '')
        parts = [p.strip() for p in loc.split(',')]
        city = parts[0] if len(parts) >= 1 else None
        state = parts[1] if len(parts) >= 2 else None
        country = parts[-1] if len(parts) >= 3 else 'United States'

        return ScrapedJob(
            external_id=external_id,
            title=item.get('title', ''),
            external_url=f'{_DETAIL_BASE}{path}',
            is_remote='remote' in loc.lower(),
            city=city,
            state=state,
            country=country,
        )
