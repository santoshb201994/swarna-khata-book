from typing import Dict, List, Optional
from .base import BaseRateScraper
from .ksjf_scraper import KSJFScraper
from .ibja_scraper import IBJAScraper
from .bullion_desk_scraper import BullionDeskScraper

# Central registry of rate scraper providers
RATE_SCRAPER_REGISTRY: Dict[str, BaseRateScraper] = {
    "ksjf": KSJFScraper(),
    "ibja": IBJAScraper(),
    "bullion_desk": BullionDeskScraper(),
}


def get_scraper(source_id: str) -> Optional[BaseRateScraper]:
    """Retrieve scraper by identifier, defaulting to KSJF if invalid."""
    if not source_id:
        source_id = "ksjf"
    return RATE_SCRAPER_REGISTRY.get(source_id.lower().strip())


def list_available_sources() -> List[dict]:
    """Returns list of selectable bullion rate sources for frontend dropdown."""
    results = []
    for sid, scraper in RATE_SCRAPER_REGISTRY.items():
        results.append({
            "id": scraper.source_id,
            "name": scraper.name,
            "url": scraper.url,
            "description": scraper.description,
            "is_default": sid == "ksjf",
        })
    return results
