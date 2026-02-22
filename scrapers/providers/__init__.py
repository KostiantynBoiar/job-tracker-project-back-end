# Import all providers so their @ScraperFactory.register decorators run
# and they appear in ScraperFactory.available().
from . import apple, nvidia  # noqa: F401