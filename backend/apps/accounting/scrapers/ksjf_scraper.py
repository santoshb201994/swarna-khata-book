import re
import logging
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date
import httpx
from bs4 import BeautifulSoup
from django.utils import timezone

from .base import BaseRateScraper, RateScrapeResult

logger = logging.getLogger(__name__)


class KSJFScraper(BaseRateScraper):
    """
    Scraper for Karnataka State Jewellers Federation (KSJF)
    Target URL: https://ksjf.in/market.php
    Ingests official benchmark rates for Karnataka jewellery trade.
    """
    source_id = "ksjf"
    name = "Karnataka State Jewellers Federation (KSJF)"
    url = "https://ksjf.in/market.php"
    description = "Official daily bullion fixing by Karnataka State Jewellers Federation (Bangalore market desk)."

    async def fetch_and_parse(self) -> RateScrapeResult:
        headers = {
            "User-Agent": self.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        try:
            async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
                response = await client.get(self.url, headers=headers)
                response.raise_for_status()
                html = response.text
        except httpx.HTTPError as exc:
            logger.error(f"Failed to fetch KSJF market page: {exc}")
            raise ConnectionError(f"Unable to reach KSJF market desk ({self.url}): {exc}")

        return self.parse_html(html)

    def parse_html(self, html: str) -> RateScrapeResult:
        soup = BeautifulSoup(html, "lxml" if "lxml" in BeautifulSoup.__dict__.get("builder_registry", {}) else "html.parser")

        rate_date = timezone.localdate()
        raw_rates = {}

        # 1. Parse date from page (e.g. "Rate update dated 24/10/2026." or archive "24 Oct 2026")
        date_muted = soup.find(string=re.compile(r"Rate update dated", re.I))
        if date_muted:
            date_match = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", str(date_muted))
            if date_match:
                d, m, y = map(int, date_match.groups())
                try:
                    rate_date = date(y, m, d)
                except ValueError:
                    pass

        # 2. Strategy A: CSS Selector on `.rate-board.big`
        board = soup.select_one(".rate-board.big") or soup.select_one(".rate-board")
        if board:
            items = board.find_all("div")
            for div in items:
                label_el = div.find("span")
                val_el = div.find("strong")
                if label_el and val_el:
                    lbl = label_el.get_text(strip=True).lower()
                    val_str = re.sub(r"[^\d.]", "", val_el.get_text(strip=True))
                    if val_str:
                        if "24ct" in lbl or "24kt" in lbl:
                            raw_rates["gold_24ct"] = Decimal(val_str)
                        elif "22ct" in lbl or "22kt" in lbl:
                            raw_rates["gold_22ct"] = Decimal(val_str)
                        elif "silver" in lbl:
                            raw_rates["silver_kg"] = Decimal(val_str)

        # 3. Strategy B: CSS Selector on `.market-archive-card.is-current` or first `.market-archive-card`
        if not ("gold_24ct" in raw_rates and "gold_22ct" in raw_rates):
            card = soup.select_one(".market-archive-card.is-current") or soup.select_one(".market-archive-card")
            if card:
                # Check date
                strong = card.find("strong")
                if strong:
                    try:
                        dt = datetime.strptime(strong.get_text(strip=True), "%d %b %Y").date()
                        rate_date = dt
                    except Exception:
                        pass
                for span in card.find_all("span"):
                    text = span.get_text(strip=True)
                    val_match = re.search(r"Rs\s*([\d,]+)", text, re.I)
                    if val_match:
                        clean_num = Decimal(val_match.group(1).replace(",", ""))
                        if "24ct" in text.lower():
                            raw_rates["gold_24ct"] = clean_num
                        elif "22ct" in text.lower():
                            raw_rates["gold_22ct"] = clean_num
                        elif "silver" in text.lower():
                            raw_rates["silver_kg"] = clean_num

        # 4. Strategy C: Full-text Regex Fallback
        if not ("gold_24ct" in raw_rates and "gold_22ct" in raw_rates):
            g24_match = re.search(r"Gold\s*24CT[^:\d]*[:\s]*Rs\s*([\d,]+)", html, re.I)
            if g24_match:
                raw_rates["gold_24ct"] = Decimal(g24_match.group(1).replace(",", ""))

            g22_match = re.search(r"Gold\s*22CT[^:\d]*[:\s]*Rs\s*([\d,]+)", html, re.I)
            if g22_match:
                raw_rates["gold_22ct"] = Decimal(g22_match.group(1).replace(",", ""))

            silver_match = re.search(r"Silver[^:\d]*[:\s]*Rs\s*([\d,]+)", html, re.I)
            if silver_match:
                raw_rates["silver_kg"] = Decimal(silver_match.group(1).replace(",", ""))

        # 5. Sanity check extracted numbers
        if "gold_24ct" not in raw_rates or "gold_22ct" not in raw_rates:
            raise ValueError(f"Could not parse valid Gold 24CT/22CT rates from KSJF HTML (Extracted: {raw_rates})")

        g24 = raw_rates["gold_24ct"]
        g22 = raw_rates["gold_22ct"]

        # Bullion market threshold verification (Gold: 4000 to 30000/g)
        if not (Decimal("4000") <= g24 <= Decimal("30000")):
            raise ValueError(f"Gold 24CT rate {g24} is outside safety verification thresholds.")
        if not (Decimal("3500") <= g22 <= Decimal("28000")):
            raise ValueError(f"Gold 22CT rate {g22} is outside safety verification thresholds.")

        # Silver calculation (KSJF quotes per kg, convert to per gram)
        silver_kg = raw_rates.get("silver_kg", Decimal("0"))
        silver_per_gram = (silver_kg / Decimal("1000")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Derived Purities
        # 18KT = 24KT * 0.750
        g18 = (g24 * Decimal("0.750")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        # 14KT = 24KT * 0.585
        g14 = (g24 * Decimal("0.585")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        rates_per_gram = {
            "24KT (999)": g24.quantize(Decimal("0.01")),
            "22KT (916)": g22.quantize(Decimal("0.01")),
            "18KT (750)": g18,
            "14KT (585)": g14,
            "Silver (925)": silver_per_gram,
        }

        return RateScrapeResult(
            source_id=self.source_id,
            source_name=self.name,
            source_url=self.url,
            effective_date=rate_date,
            rates_per_gram=rates_per_gram,
            raw_data={
                "gold_24ct_per_gram": str(g24),
                "gold_22ct_per_gram": str(g22),
                "silver_per_kg": str(silver_kg),
                "silver_per_gram": str(silver_per_gram),
            },
            metadata={
                "parsed_at": timezone.now().isoformat(),
                "unit": "INR per gram (Silver converted from kg)",
            }
        )
