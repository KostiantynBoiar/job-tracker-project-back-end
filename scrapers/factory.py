from scrapers.base import BaseScraper


class ScraperFactory:
    """
    Factory + registry for job scrapers.

    Scrapers self-register via the @ScraperFactory.register(slug) decorator:

        @ScraperFactory.register('apple')
        class AppleScraper(BaseScraper):
            ...

    Usage:
        scraper = ScraperFactory.get('apple')
        jobs = scraper.scrape()
    """

    _registry: dict[str, type[BaseScraper]] = {}

    @classmethod
    def register(cls, slug: str):
        """Class decorator that registers a scraper under the given slug."""
        def decorator(scraper_cls: type[BaseScraper]):
            cls._registry[slug.lower()] = scraper_cls
            return scraper_cls
        return decorator

    @classmethod
    def get(cls, slug: str) -> BaseScraper:
        klass = cls._registry.get(slug.lower())
        if klass is None:
            raise ValueError(
                f"No scraper registered for '{slug}'. "
                f"Available: {list(cls._registry)}"
            )
        return klass()

    @classmethod
    def available(cls) -> list[str]:
        return list(cls._registry)
