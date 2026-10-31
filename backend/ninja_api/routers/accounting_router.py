import logging
from typing import List, Optional
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from ninja import Router

logger = logging.getLogger(__name__)
audit_logger = logging.getLogger('swarnakhata.audit')

from apps.accounting.models import GoldRate, Customer, DayBook, ShopRateSetting
from apps.products.models import Purity
from apps.accounting.scrapers import list_available_sources
from apps.accounting.services import sync_rates_from_source
from ninja_api.auth import jwt_auth, require_role
from ninja_api.schemas import (
    GoldRateIn, GoldRateOut, CustomerIn, CustomerOut,
    DayBookOut, CloseDayIn, CashEntryIn, DayBookPatchIn,
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
    """Get active live gold/metal rates per purity for the current showroom branch."""
    from apps.accounts.models import Branch
    branch = request.auth.branch if (request.auth and request.auth.branch) else Branch.objects.first()
    rates_qs = GoldRate.objects.select_related('purity', 'entered_by').filter(is_current=True)
    if branch:
        rates_for_branch = rates_qs.filter(branch=branch)
        if rates_for_branch.exists():
            rates_qs = rates_for_branch

    # Deduplicate: latest effective rate per purity_id
    deduped = {}
    for r in rates_qs.order_by('-effective_date', '-created_at'):
        if r.purity_id not in deduped:
            deduped[r.purity_id] = r

    # Ensure EVERY configured purity has an active rate.
    # Checks specific metal keywords in priority order so silver/platinum are never defaulted to gold rates.
    today = timezone.localdate()
    purities = Purity.objects.all()
    default_benchmarks = [
        ('silver', Decimal('92.00')),
        ('925', Decimal('92.00')),
        ('chandi', Decimal('92.00')),
        ('platinum', Decimal('3200.00')),
        ('950', Decimal('3200.00')),
        ('24', Decimal('7450.00')),
        ('999', Decimal('7450.00')),
        ('22', Decimal('6830.00')),
        ('916', Decimal('6830.00')),
        ('18', Decimal('5590.00')),
        ('750', Decimal('5590.00')),
        ('14', Decimal('4350.00')),
        ('585', Decimal('4350.00')),
    ]
    for p in purities:
        if p.id not in deduped:
            p_name_lower = p.name.lower()
            val = Decimal('6830.00')
            for k, benchmark in default_benchmarks:
                if k in p_name_lower:
                    val = benchmark
                    break
            created_rate = GoldRate.objects.filter(
                purity=p,
                branch=branch,
                effective_date=today,
            ).order_by('-created_at').first()
            if not created_rate:
                created_rate = GoldRate.objects.create(
                    purity=p,
                    branch=branch,
                    effective_date=today,
                    rate_per_gram=val,
                    is_current=True,
                    entered_by=request.auth
                )
            deduped[p.id] = created_rate

    results = []
    for r in deduped.values():
        entered_by = r.entered_by.get_full_name() or r.entered_by.username if r.entered_by else 'Admin'
        results.append({
            "id": r.id,
            "purity_id": r.purity_id,
            "purity": r.purity_id,
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
    pid = payload.purity_id or payload.purity
    if not pid:
        return 400, {"error": "purity_id or purity is required."}

    purity = get_object_or_404(Purity, id=pid)
    eff_date = payload.effective_date or timezone.localdate()
    branch = request.auth.branch if request.auth else None

    with transaction.atomic():
        if payload.is_current:
            GoldRate.objects.filter(purity=purity, branch=branch).update(is_current=False)

        rate = GoldRate.objects.create(
            purity=purity,
            rate_per_gram=payload.rate_per_gram,
            effective_date=eff_date,
            is_current=payload.is_current,
            entered_by=request.auth,
            branch=branch,
        )

    entered_by = request.auth.get_full_name() or request.auth.username if request.auth else 'Admin'
    audit_logger.info(
        "RATE_MANUAL_UPDATE: purity='%s' (id=%s) rate=₹%s effective=%s is_current=%s entered_by='%s' branch='%s'",
        purity.name, rate.purity_id, rate.rate_per_gram, rate.effective_date, rate.is_current, entered_by, branch
    )
    return 201, {
        "id": rate.id,
        "purity_id": rate.purity_id,
        "purity": rate.purity_id,
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
    if search and search.strip():
        term = search.strip()
        qs = qs.filter(
            Q(name__icontains=term) |
            Q(phone__icontains=term) |
            Q(pan_number__icontains=term) |
            Q(address__icontains=term)
        )
    return qs.order_by('-id')[:100]


@router.post("/customers/", response={201: CustomerOut, 400: dict}, auth=jwt_auth)
def create_customer(request, payload: CustomerIn):
    phone = payload.phone.strip()
    name = payload.name.strip()
    if not name:
        return 400, {"error": "Customer name is required."}
    if not phone:
        return 400, {"error": "Customer phone number is required."}

    existing = Customer.objects.filter(phone=phone).first()
    if existing:
        return 400, {
            "error": f"Customer with phone '{phone}' already exists: {existing.name}.",
            "existing_customer_id": existing.id,
            "existing_customer_name": existing.name,
        }

    cust = Customer.objects.create(
        name=name,
        phone=phone,
        email=(payload.email or '').strip(),
        address=(payload.address or '').strip(),
        pan_number=(payload.pan_number or '').strip().upper(),
        aadhar_last4=(payload.aadhar_last4 or '').strip(),
    )
    return 201, cust


@router.get("/customers/{customer_id}/", response=CustomerOut, auth=jwt_auth)
def get_customer(request, customer_id: int):
    return get_object_or_404(Customer, id=customer_id)


@router.put("/customers/{customer_id}/", response={200: CustomerOut, 400: dict}, auth=jwt_auth)
def update_customer(request, customer_id: int, payload: CustomerIn):
    cust = get_object_or_404(Customer, id=customer_id)
    name = payload.name.strip()
    phone = payload.phone.strip()
    if not name:
        return 400, {"error": "Customer name is required."}
    if not phone:
        return 400, {"error": "Customer phone number is required."}

    existing = Customer.objects.filter(phone=phone).exclude(id=customer_id).first()
    if existing:
        return 400, {"error": f"Another customer already has phone '{phone}': {existing.name}."}

    cust.name = name
    cust.phone = phone
    cust.email = (payload.email or '').strip()
    cust.address = (payload.address or '').strip()
    cust.pan_number = (payload.pan_number or '').strip().upper()
    cust.aadhar_last4 = (payload.aadhar_last4 or '').strip()
    cust.save()
    return 200, cust


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


@router.post("/day-book/cash-entry/", response={201: DayBookOut, 400: dict}, auth=jwt_auth)
def record_petty_cash_entry(request, payload: CashEntryIn):
    """
    Record ad-hoc showroom petty cash movement (e.g. tea, office supplies, owner withdrawal).
    """
    today = timezone.localdate()
    branch = request.auth.branch if request.auth else None

    amount = payload.amount.quantize(Decimal('0.01'))
    if amount <= Decimal('0.00'):
        return 400, {"error": "Amount must be greater than zero."}

    if payload.entry_type not in ('in', 'out'):
        return 400, {"error": "entry_type must be 'in' or 'out'"}

    with transaction.atomic():
        day, _ = DayBook.objects.select_for_update().get_or_create(
            date=today, branch=branch,
            defaults={'opening_balance': Decimal('0.00')}
        )
        if day.is_closed:
            return 400, {"error": "Day book is already closed for today. Cannot post further cash entries."}

        if payload.entry_type == 'in':
            day.cash_in += amount
        else:
            day.cash_out += amount

        if payload.note:
            day.notes = f"{day.notes}\n[{timezone.now().strftime('%H:%M')}] {payload.entry_type.upper()}: ₹{amount} - {payload.note}".strip()

        day.save()

    username = request.auth.username if request.auth else 'anonymous'
    audit_logger.info(
        "CASH_DRAWER_ENTRY: type=%s amount=₹%s note='%s' user='%s' branch='%s' running_cash=₹%s",
        payload.entry_type.upper(), amount, payload.note or '', username, branch, day.cash_in - day.cash_out
    )

    return 201, _format_daybook(day)


def _perform_close_day_book(request, day_id: int):
    require_role(request.auth, ['owner', 'manager', 'accountant'])
    notes = ''
    try:
        import json
        if request.body:
            body_data = json.loads(request.body)
            notes = body_data.get('notes', '')
    except Exception:
        pass

    with transaction.atomic():
        day = DayBook.objects.select_for_update().filter(id=day_id).first()
        if not day:
            return 404, {"error": "DayBook not found."}
        if day.is_closed:
            return 400, {"error": "Day book is already closed for this date."}

        day.closing_balance = day.opening_balance + day.cash_in - day.cash_out
        day.is_closed = True
        day.closed_by = request.auth
        if notes:
            day.notes = notes
        day.save()

    username = request.auth.username if request.auth else 'anonymous'
    audit_logger.info(
        "DAYBOOK_CLOSE: day_id=%s date=%s closing_balance=₹%s user='%s' branch='%s'",
        day.id, day.date, day.closing_balance, username, day.branch
    )

    return 200, _format_daybook(day)


@router.post("/day-book/{day_id}/close/", response={200: DayBookOut, 400: dict, 404: dict}, auth=jwt_auth)
def close_day_book(request, day_id: int):
    """
    Close the business daybook cash drawer.
    Computes closing_balance = opening_balance + cash_in - cash_out and locks entries.
    """
    return _perform_close_day_book(request, day_id)


@router.post("/day-book/{day_id}/close_day/", response={200: DayBookOut, 400: dict, 404: dict}, auth=jwt_auth)
def close_day_book_alias(request, day_id: int):
    """Alias for close_day_book endpoint."""
    return _perform_close_day_book(request, day_id)


@router.post("/day-book/{day_id}/reopen/", response={200: DayBookOut, 400: dict, 404: dict}, auth=jwt_auth)
def reopen_day_book(request, day_id: int):
    """
    Reopen the business daybook cash drawer for adjustments (Owner & Manager Level 60+).
    """
    require_role(request.auth, ['owner', 'manager'])
    with transaction.atomic():
        day = DayBook.objects.select_for_update().filter(id=day_id).first()
        if not day:
            return 404, {"error": "DayBook not found."}
        day.is_closed = False
        day.closed_by = None
        reopen_note = f"\n[{timezone.now().strftime('%H:%M')}] DAY REOPENED by {request.auth.username}"
        day.notes = (day.notes + reopen_note).strip()
        day.save()

    audit_logger.info(
        "DAYBOOK_REOPEN: day_id=%s date=%s user='%s' branch='%s'",
        day.id, day.date, request.auth.username, day.branch
    )

    return 200, _format_daybook(day)


@router.post("/day-book/{day_id}/reopen_day/", response={200: DayBookOut, 400: dict, 404: dict}, auth=jwt_auth)
def reopen_day_book_alias(request, day_id: int):
    """Alias for reopen_day_book endpoint."""
    return reopen_day_book(request, day_id)


@router.patch("/day-book/{day_id}/", response={200: DayBookOut, 400: dict, 404: dict}, auth=jwt_auth)
def update_day_book_cash(request, day_id: int, payload: DayBookPatchIn):
    """Patch update daybook cash values directly."""
    require_role(request.auth, ['owner', 'manager', 'accountant'])
    with transaction.atomic():
        day = DayBook.objects.select_for_update().filter(id=day_id).first()
        if not day:
            return 404, {"error": "DayBook not found."}
        if day.is_closed:
            return 400, {"error": "Day book is already closed for this date. Cannot modify."}

        if payload.cash_in is not None:
            day.cash_in = payload.cash_in
        if payload.cash_out is not None:
            day.cash_out = payload.cash_out
        if payload.notes is not None:
            day.notes = payload.notes
        day.save()
    return 200, _format_daybook(day)


@router.post("/day-book/{day_id}/reopen/", response={200: DayBookOut, 400: dict, 404: dict}, auth=jwt_auth)
def reopen_day_book(request, day_id: int):
    """Reopen a previously closed daybook for supervisor adjustments (Owner/Manager only)."""
    require_role(request.auth, ['owner', 'manager'])
    with transaction.atomic():
        day = DayBook.objects.select_for_update().filter(id=day_id).first()
        if not day:
            return 404, {"error": "DayBook not found."}
        if not day.is_closed:
            return 400, {"error": "DayBook is already open."}
        day.is_closed = False
        day.save(update_fields=['is_closed'])
    return 200, _format_daybook(day)
