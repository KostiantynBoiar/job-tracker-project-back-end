from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator, Optional


@dataclass
class ScrapedJob:
    external_id: str
    title: str
    external_url: str
    description: Optional[str] = None
    requirements: Optional[str] = None
    is_remote: bool = False
    experience_level: Optional[str] = None
    employment_type: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    posted_at: Optional[datetime] = None


class BaseScraper(ABC):
    company_slug: str

    @abstractmethod
    def stream_jobs(self) -> Iterator[ScrapedJob]:
        """Yield scraped jobs one by one."""
        ...

    def fetch_jobs(self) -> list[ScrapedJob]:
        return list(self.stream_jobs())
