import json
import re
import time
from datetime import datetime
from typing import Iterator

import requests
from bs4 import BeautifulSoup

from scrapers.base import BaseScraper, ScrapedJob
from scrapers.factory import ScraperFactory

_SEARCH_URL = 'https://jobs.apple.com/en-us/search'
_DETAIL_BASE = 'https://jobs.apple.com/en-us/details'
_PAGE_SIZE = 20
_TIMEOUT = 60
_MAX_RETRIES = 3
_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ),
}


@ScraperFactory.register('apple')
class AppleScraper(BaseScraper):
    company_slug = 'apple'

    def stream_jobs(self) -> Iterator[ScrapedJob]:
        page = 1
        total = None

        while True:
            data = self._fetch_page(page)
            results = data.get('searchResults', [])
            if not results:
                break

            if total is None:
                total = data.get('totalRecords', 0)

            for item in results:
                yield self._parse(item)

            fetched_so_far = (page - 1) * _PAGE_SIZE + len(results)
            if len(results) < _PAGE_SIZE or fetched_so_far >= total:
                break
            page += 1

    def _fetch_page(self, page: int) -> dict:
        last_exc = None
        for attempt in range(_MAX_RETRIES):
            try:
                response = requests.get(
                    _SEARCH_URL,
                    params={'page': page},
                    headers=_HEADERS,
                    timeout=_TIMEOUT,
                )
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')
                for script in soup.find_all('script'):
                    text = script.string or ''
                    if '__staticRouterHydrationData' not in text:
                        continue
                    m = re.search(r'JSON\.parse\("(.*?)"\);', text, re.DOTALL)
                    if m:
                        json_str = m.group(1).encode('utf-8').decode('unicode_escape')
                        data = json.loads(json_str)
                        return data.get('loaderData', {}).get('search', {})
                return {}

            except requests.exceptions.Timeout as exc:
                last_exc = exc
                if attempt < _MAX_RETRIES - 1:
                    time.sleep(5 * (attempt + 1))

        raise last_exc

    def _parse(self, item: dict) -> ScrapedJob:
        position_id = str(item.get('positionId', ''))
        locs = item.get('locations', [])
        loc = locs[0] if locs else {}

        city = loc.get('city') or None
        state = loc.get('stateProvince') or None
        country = loc.get('countryName') or 'United States'

        posted_at = None
        raw_date = item.get('postDateInGMT')
        if raw_date:
            try:
                posted_at = datetime.fromisoformat(raw_date.replace('Z', '+00:00'))
            except ValueError:
                pass

        return ScrapedJob(
            external_id=position_id,
            title=item.get('postingTitle', ''),
            external_url=f'{_DETAIL_BASE}/{position_id}',
            description=item.get('jobSummary'),
            is_remote=bool(item.get('homeOffice', False)),
            city=city,
            state=state,
            country=country,
            posted_at=posted_at,
        )
