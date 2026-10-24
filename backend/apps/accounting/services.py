import asyncio
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from asgiref.sync import sync_to_async
from .models import GoldRate
from apps.products.models import Purity


# Base reference bullion pricing factors relative to pure 24KT (999) gold
PURITY_FACTORS = {
    '24KT': Decimal('1.000'),     # 99.9%
    '22KT': Decimal('0.9167'),    # 91.6%
    '18KT': Decimal('0.750'),     # 75.0%
    '14KT': Decimal('0.585'),     # 58.5%
}


async def fetch_live_market_rates_async(base_24k_rate: Decimal = Decimal('7450.00')) -> dict:
    """
    Asynchronously fetch or calculate market bullion benchmark rates.
    Simulates / prepares integration with external bullion market feeds (e.g. IBJA / MCX)
    without blocking Django request threads.
    """
    # Non-blocking async simulation of external API feed latency
    await asyncio.sleep(0.01)

    rates = {}
    for code, factor in PURITY_FACTORS.items():
        rate = (base_24k_rate * factor).quantize(Decimal('1.00'), rounding=ROUND_HALF_UP)
        rates[code] = rate

    # Silver standard benchmark per gram
    rates['Silver'] = Decimal('92.00')
    return rates


async def sync_live_rates_async(user=None, branch=None, base_24k_rate: Decimal = Decimal('7450.00')):
    """
    Asynchronously syncs current gold rates into the database using async-compatible ORM operations.
    Updates or creates active GoldRate records for each configured purity.
    """
    market_rates = await fetch_live_market_rates_async(base_24k_rate=base_24k_rate)
    today = timezone.localdate()
    updated_records = []

    # Query purities asynchronously using sync_to_async or list evaluation
    def get_purities():
        return list(Purity.objects.all())

    purities = await sync_to_async(get_purities)()

    def persist_rate(purity, rate_value):
        rate_record, _ = GoldRate.objects.get_or_create(
            purity=purity,
            effective_date=today,
            branch=branch,
            defaults={
                'rate_per_gram': rate_value,
                'is_current': True,
                'entered_by': user,
            }
        )
        if rate_record.rate_per_gram != rate_value or not rate_record.is_current:
            rate_record.rate_per_gram = rate_value
            rate_record.is_current = True
            rate_record.entered_by = user
            rate_record.save()
        return rate_record

    for purity in purities:
        # Match rate by key in name or code
        matched_rate = None
        for key, val in market_rates.items():
            if key in purity.name or key in purity.code:
                matched_rate = val
                break

        if matched_rate:
            record = await sync_to_async(persist_rate)(purity, matched_rate)
            updated_records.append(record)

    return updated_records


async def sync_rates_from_source(source_id: str, branch=None, user=None, tenant_schema: str = None) -> dict:
    """
    Asynchronously scrape rates from the selected provider website (e.g. KSJF, IBJA)
    and atomically update the active GoldRate records in the current tenant schema.
    """
    from django.db import transaction
    from .models import ShopRateSetting
    from .scrapers import get_scraper

    scraper = get_scraper(source_id)
    if not scraper:
        raise ValueError(f"Unknown or unsupported rate source '{source_id}'")

    # 1. Scrape rates from website
    scrape_result = await scraper.fetch_and_parse()
    effective_date = scrape_result.effective_date

    # 2. Database transaction inside tenant schema
    from django.db import connection
    from django_tenants.utils import schema_context
    current_schema = tenant_schema or getattr(connection, 'schema_name', None)
    if not current_schema or current_schema == 'public':
        current_schema = 'demo'

    def _persist_all():
        with schema_context(current_schema):
            with transaction.atomic():
                from apps.accounts.models import Branch
                resolved_branch = branch
                if not resolved_branch and user and getattr(user, 'branch_id', None):
                    resolved_branch = getattr(user, 'branch', None)
                if not resolved_branch:
                    resolved_branch = Branch.objects.first()

                updated_rates = []
                purities = list(Purity.objects.all())

                for purity in purities:
                    purity_name_upper = purity.name.upper()
                    matched_val = None

                    for key, val in scrape_result.rates_per_gram.items():
                        key_tag = key.split()[0].upper()  # '24KT', '22KT', '18KT', '14KT', 'SILVER'
                        if key_tag in purity_name_upper:
                            matched_val = val
                            break

                    if matched_val is not None:
                        # Deactivate prior current rates
                        GoldRate.objects.filter(
                            purity=purity,
                            branch=resolved_branch,
                            is_current=True
                        ).exclude(effective_date=effective_date).update(is_current=False)

                        rate_obj, _ = GoldRate.objects.update_or_create(
                            purity=purity,
                            branch=resolved_branch,
                            effective_date=effective_date,
                            defaults={
                                'rate_per_gram': matched_val,
                                'is_current': True,
                                'entered_by': user,
                            }
                        )
                        entered_name = "Admin"
                        if user:
                            entered_name = getattr(user, 'username', 'Admin')
                            if hasattr(user, 'get_full_name'):
                                fn = user.get_full_name()
                                if fn:
                                    entered_name = fn

                        updated_rates.append({
                            "id": rate_obj.id,
                            "purity_id": purity.id,
                            "purity_name": purity.name,
                            "rate_per_gram": rate_obj.rate_per_gram,
                            "effective_date": rate_obj.effective_date,
                            "is_current": rate_obj.is_current,
                            "entered_by_name": entered_name,
                            "created_at": rate_obj.created_at,
                        })

                # Update shop preference & audit timestamp
                setting, _ = ShopRateSetting.objects.get_or_create(branch=resolved_branch)
                setting.preferred_source = source_id
                setting.last_synced_at = timezone.now()
                setting.last_synced_source = scraper.name
                setting.save()

                return updated_rates

    updated = await sync_to_async(_persist_all)()

    return {
        "source_id": scraper.source_id,
        "source_name": scraper.name,
        "source_url": scraper.url,
        "effective_date": effective_date,
        "updated_count": len(updated),
        "rates": updated,
        "raw_data": scrape_result.raw_data,
    }

