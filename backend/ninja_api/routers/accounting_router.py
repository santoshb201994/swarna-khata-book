from typing import List, Optional
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Router

from apps.accounting.models import GoldRate, Customer, DayBook, ShopRateSetting
from apps.products.models import Purity
from apps.accounting.scrapers import list_available_sources
from apps.accounting.services import sync_rates_from_source
from ninja_api.auth import jwt_auth, require_role
from ninja_api.schemas import (
    GoldRateIn, GoldRateOut, CustomerIn, CustomerOut,
    DayBookOut, CloseDayIn, CashEntryIn,
    RateSourceOut, SyncRatesIn, SyncRatesResponse,
    ShopRateSettingIn, ShopRateSettingOut
)

router = Router(tags=["Accounting, Bullion Rates & Cash DayBook"])


# ==============================================================================
# GOLD RATES & WEB SCRAPER SYNC
# ==============================================================================

@router.get("/gold-rates/sources/", response=List[RateSourceOut], auth=jwt_auth)
def get_rate_sources(request):
    """
    List selectable bullion association scraping sources for user/shop dropdown.
    Highlights shop's configured default source.
    """
    sources = list_available_sources()
    branch = request.auth.branch if request.auth else None
    preferred = "ksjf"
    if branch:
        setting = ShopRateSetting.objects.filter(branch=branch).first()
        if setting:
            preferred = setting.preferred_source

    for s in sources:
        s["is_default"] = (s["id"] == preferred)
    return sources


@router.post("/gold-rates/sync/", response={200: SyncRatesResponse, 400: dict, 502: dict}, auth=jwt_auth)
async def sync_rates_from_web(request, payload: SyncRatesIn):
    """
    Scrapes live bullion rates from the selected website source (KSJF, IBJA, Bullion Desk)
    and atomically updates the current showroom's active GoldRate entries.
    Requires Owner or Manager role.
    """
    user = request.auth
    require_role(user, ['owner', 'manager'])
    tenant_schema = getattr(request.tenant, 'schema_name', None) if hasattr(request, 'tenant') else None

    try:
        result = await sync_rates_from_source(
            source_id=payload.source,
            branch=None,
            user=user,
            tenant_schema=tenant_schema,
        )

        formatted_rates = result["rates"]
        msg = f"Successfully synced {len(formatted_rates)} rates from {result['source_name']} for {result['effective_date']}."
        return 200, {
            "status": "success",
            "source_id": result["source_id"],
            "source_name": result["source_name"],
            "effective_date": result["effective_date"],
            "updated_count": result["updated_count"],
            "message": msg,
            "rates": formatted_rates,
        }
    except ValueError as e:
        return 400, {"error": str(e)}
    except ConnectionError as e:
        return 502, {"error": f"Failed to connect to rate provider: {str(e)}"}
    except Exception as e:
        import logging
        logging.getLogger(__name__).exception("Failed to sync gold rates from web")
        return 400, {"error": f"Scraping failed: {str(e)}"}


@router.get("/gold-rates/settings/", response=ShopRateSettingOut, auth=jwt_auth)
def get_rate_settings(request):
    """Get the shop's saved rate scraping preference and audit timestamp."""
    branch = request.auth.branch if request.auth else None
    setting, _ = ShopRateSetting.objects.get_or_create(branch=branch)
    return {
        "preferred_source": setting.preferred_source,
        "last_synced_at": setting.last_synced_at,
        "last_synced_source": setting.last_synced_source,
    }


@router.put("/gold-rates/settings/", response=ShopRateSettingOut, auth=jwt_auth)
def update_rate_settings(request, payload: ShopRateSettingIn):
    """Save preferred default scraping source for this shop."""
    require_role(request.auth, ['owner', 'manager'])
    branch = request.auth.branch if request.auth else None
    setting, _ = ShopRateSetting.objects.get_or_create(branch=branch)
    setting.preferred_source = payload.preferred_source
    setting.save()
    return {
        "preferred_source": setting.preferred_source,
        "last_synced_at": setting.last_synced_at,
        "last_synced_source": setting.last_synced_source,
    }


@router.get("/gold-rates/current/", response=List[GoldRateOut], auth=jwt_auth)
def get_current_rates(request):
    """Get active live gold rates per purity for the current showroom branch."""
    branch = request.auth.branch if request.auth else None
    rates = GoldRate.objects.select_related('purity', 'entered_by').filter(is_current=True)
    if branch:
        rates = rates.filter(branch=branch)

    results = []
    for r in rates:
        entered_by = r.entered_by.get_full_name() or r.entered_by.username if r.entered_by else 'Admin'
        results.append({
            "id": r.id,
            "purity_id": r.purity_id,
            "purity_name": r.purity.name,
            "rate_per_gram": r.rate_per_gram,
            "effective_date": r.effective_date,
            "is_current": r.is_current,
            "entered_by_name": entered_by,
            "created_at": r.created_at,
        })
    return results


@router.get("/gold-rates/live-market/", auth=jwt_auth)
def get_live_market_rates(request):
    """Asynchronous bullion market benchmark rate feed."""
    from asgiref.sync import async_to_sync
    from apps.accounting.services import fetch_live_market_rates_async
    rates = async_to_sync(fetch_live_market_rates_async)()
    return {
        "source": "Bullion Market Benchmark Feed (Async)",
        "currency": "INR",
        "rates": {k: str(v) for k, v in rates.items()}
    }


@router.get("/gold-rates/history/", response=List[GoldRateOut], auth=jwt_auth)
def list_gold_rates_history(request, purity_id: Optional[int] = None):
    """Retrieve historical gold price audit trail."""
    qs = GoldRate.objects.select_related('purity', 'entered_by').all()
    if purity_id:
        qs = qs.filter(purity_id=purity_id)

    results = []
    for r in qs[:100]:
        entered_by = r.entered_by.get_full_name() or r.entered_by.username if r.entered_by else 'Admin'
        results.append({
            "id": r.id,
            "purity_id": r.purity_id,
            "purity_name": r.purity.name,
            "rate_per_gram": r.rate_per_gram,
            "effective_date": r.effective_date,
            "is_current": r.is_current,
            "entered_by_name": entered_by,
            "created_at": r.created_at,
        })
    return results


@router.post("/gold-rates/", response={201: GoldRateOut, 400: dict}, auth=jwt_auth)
def create_gold_rate(request, payload: GoldRateIn):
    """
    Set new active gold rate for a purity.
    Restricted to Owner or Manager role.
    """
    require_role(request.auth, ['owner', 'manager'])
    purity = get_object_or_404(Purity, id=payload.purity_id)
    eff_date = payload.effective_date or timezone.localdate()

    rate = GoldRate.objects.create(
        purity=purity,
        rate_per_gram=payload.rate_per_gram,
        effective_date=eff_date,
        is_current=payload.is_current,
        entered_by=request.auth,
        branch=request.auth.branch if request.auth else None,
    )

    entered_by = request.auth.get_full_name() or request.auth.username if request.auth else 'Admin'
    return 201, {
        "id": rate.id,
        "purity_id": rate.purity_id,
        "purity_name": purity.name,
        "rate_per_gram": rate.rate_per_gram,
        "effective_date": rate.effective_date,
        "is_current": rate.is_current,
        "entered_by_name": entered_by,
        "created_at": rate.created_at,
    }


# ==============================================================================
# CUSTOMERS / CRM
# ==============================================================================

@router.get("/customers/", response=List[CustomerOut], auth=jwt_auth)
def list_customers(request, search: Optional[str] = None):
    """Search and list customer khata directory."""
    qs = Customer.objects.all()
    if search:
        qs = qs.filter(name__icontains=search) | qs.filter(phone__icontains=search) | qs.filter(pan_number__icontains=search)
    return qs[:100]


@router.post("/customers/", response={201: CustomerOut, 400: dict}, auth=jwt_auth)
def create_customer(request, payload: CustomerIn):
    if Customer.objects.filter(phone=payload.phone).exists():
        return 400, {"error": f"Customer with phone '{payload.phone}' already exists."}

    cust = Customer.objects.create(
        name=payload.name,
        phone=payload.phone,
        email=payload.email or '',
        address=payload.address or '',
        pan_number=payload.pan_number or '',
        aadhar_last4=payload.aadhar_last4 or '',
    )
    return 201, cust


@router.get("/customers/{customer_id}/", response=CustomerOut, auth=jwt_auth)
def get_customer(request, customer_id: int):
    return get_object_or_404(Customer, id=customer_id)


@router.put("/customers/{customer_id}/", response=CustomerOut, auth=jwt_auth)
def update_customer(request, customer_id: int, payload: CustomerIn):
    cust = get_object_or_404(Customer, id=customer_id)
    cust.name = payload.name
    cust.phone = payload.phone
    cust.email = payload.email or ''
    cust.address = payload.address or ''
    cust.pan_number = payload.pan_number or ''
    cust.aadhar_last4 = payload.aadhar_last4 or ''
    cust.save()
    return cust


# ==============================================================================
# DAYBOOK / CASH DRAWER AUDIT
# ==============================================================================

def _format_daybook(day: DayBook) -> dict:
    return {
        "id": day.id,
        "date": day.date,
        "branch_id": day.branch_id,
        "branch_name": day.branch.name if day.branch else None,
        "opening_balance": day.opening_balance,
        "cash_in": day.cash_in,
        "cash_out": day.cash_out,
        "closing_balance": day.closing_balance,
        "net_cash": day.cash_in - day.cash_out,
        "is_closed": day.is_closed,
        "notes": day.notes,
        "created_at": day.created_at,
    }


@router.get("/day-book/today/", response=DayBookOut, auth=jwt_auth)
def get_today_day_book(request):
    """Retrieve or initialize today's business cash summary for this branch."""
    today = timezone.localdate()
    branch = request.auth.branch if request.auth else None

    # If opening balance not set, inherit closing balance from previous closed day
    day, created = DayBook.objects.get_or_create(
        date=today, branch=branch,
        defaults={'opening_balance': Decimal('0.00')}
    )
    if created:
        prev_day = DayBook.objects.filter(branch=branch, date__lt=today, is_closed=True).order_by('-date').first()
        if prev_day:
            day.opening_balance = prev_day.closing_balance
            day.save(update_fields=['opening_balance'])

    return _format_daybook(day)


@router.get("/day-book/", response=List[DayBookOut], auth=jwt_auth)
def list_day_books(request):
    """List historical day book journals."""
    branch = request.auth.branch if request.auth else None
    qs = DayBook.objects.select_related('branch', 'closed_by').all()
    if branch:
        qs = qs.filter(branch=branch)
    return [_format_daybook(d) for d in qs[:60]]


@router.post("/day-book/{day_id}/close/", response={200: DayBookOut, 400: dict}, auth=jwt_auth)
def close_day_book(request, day_id: int, payload: CloseDayIn):
    """
    Close the business daybook cash drawer.
    Computes closing_balance = opening_balance + cash_in - cash_out and locks entries.
    """
    require_role(request.auth, ['owner', 'manager', 'accountant'])
    day = get_object_or_404(DayBook, id=day_id)
    if day.is_closed:
        return 400, {"error": "Day book is already closed for this date."}

    day.closing_balance = day.opening_balance + day.cash_in - day.cash_out
    day.is_closed = True
    day.closed_by = request.auth
    if payload.notes:
        day.notes = payload.notes
    day.save()

    return 200, _format_daybook(day)


@router.post("/day-book/cash-entry/", response={201: DayBookOut, 400: dict}, auth=jwt_auth)
def record_petty_cash_entry(request, payload: CashEntryIn):
    """
    Record ad-hoc showroom petty cash movement (e.g. tea, office supplies, owner withdrawal).
    """
    today = timezone.localdate()
    branch = request.auth.branch if request.auth else None
    day, _ = DayBook.objects.get_or_create(
        date=today, branch=branch,
        defaults={'opening_balance': Decimal('0.00')}
    )
    if day.is_closed:
        return 400, {"error": "Day book is already closed for today. Cannot post further cash entries."}

    amount = payload.amount.quantize(Decimal('0.01'))
    if payload.entry_type == 'in':
        day.cash_in += amount
    elif payload.entry_type == 'out':
        day.cash_out += amount
    else:
        return 400, {"error": "entry_type must be 'in' or 'out'"}

    if payload.note:
        day.notes = f"{day.notes}\n[{timezone.now().strftime('%H:%M')}] {payload.entry_type.upper()}: ₹{amount} - {payload.note}".strip()

    day.save()
    return 201, _format_daybook(day)
