from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import date
from typing import Dict, Any, Optional
import httpx
from asgiref.sync import async_to_sync


@dataclass
class RateScrapeResult:
    source_id: str
    source_name: str
    source_url: str
    effective_date: date
    rates_per_gram: Dict[str, Decimal]  # Normalized name -> Decimal rate per gram
    raw_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseRateScraper(ABC):
    """
    Abstract base class for all bullion association web scrapers.
    """
    source_id: str = ""
    name: str = ""
    url: str = ""
    description: str = ""

    USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )

    @abstractmethod
    async def fetch_and_parse(self) -> RateScrapeResult:
        """Fetch external webpage and extract normalized bullion rates."""
        pass

    def fetch_and_parse_sync(self) -> RateScrapeResult:
        """Synchronous wrapper for Celery/CLI execution."""
        return async_to_sync(self.fetch_and_parse)()
