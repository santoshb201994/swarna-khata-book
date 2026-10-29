from decimal import Decimal
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
from django.core.exceptions import ValidationError as DjangoValidationError
from apps.accounts.validators import validate_password_policy


# ==============================================================================
# AUTH & ACCOUNTS SCHEMAS
# ==============================================================================

class TokenRequest(BaseModel):
    username: str
    password: str


class TokenRefreshRequest(BaseModel):
    refresh: str


class UserInfo(BaseModel):
    id: int
    username: str
    email: Optional[str] = ''
    role: str
    branch_id: Optional[int] = None
    tenant_schema: Optional[str] = None


class TokenResponse(BaseModel):
    access: str
    refresh: Optional[str] = None
    user: Optional[UserInfo] = None
    tenant_schema: Optional[str] = None


class UserCreateIn(BaseModel):
    username: str
    password: str
    email: Optional[str] = ''
    first_name: Optional[str] = ''
    last_name: Optional[str] = ''
    role: str = 'staff'
    phone: Optional[str] = ''
    branch_id: Optional[int] = None

    @field_validator('password')
    @classmethod
    def validate_user_password(cls, v: str) -> str:
        try:
            validate_password_policy(v)
        except DjangoValidationError as exc:
            raise ValueError(exc.messages[0])
        return v


class StoreRegistrationIn(BaseModel):
    shop_name: str
    owner_username: str
    owner_password: str
    owner_email: Optional[str] = ''
    owner_phone: Optional[str] = ''
    address: Optional[str] = ''
    gstin: Optional[str] = ''

    @field_validator('owner_password')
    @classmethod
    def validate_owner_pwd(cls, v: str) -> str:
        try:
            validate_password_policy(v)
        except DjangoValidationError as exc:
            raise ValueError(exc.messages[0])
        return v


class StoreRegistrationOut(BaseModel):
    schema_name: str
    shop_name: str
    domain: str
    owner_username: str
    access: str
    refresh: str
    message: str


class PasswordResetIn(BaseModel):
    new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_new_pwd(cls, v: str) -> str:
        try:
            validate_password_policy(v)
        except DjangoValidationError as exc:
            raise ValueError(exc.messages[0])
        return v


class PasswordChangeIn(BaseModel):
    current_password: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_new_pwd(cls, v: str) -> str:
        try:
            validate_password_policy(v)
        except DjangoValidationError as exc:
            raise ValueError(exc.messages[0])
        return v


class StaffStatusUpdateIn(BaseModel):
    is_active: bool


class SwitchStoreIn(BaseModel):
    schema_name: str


class UserDetailOut(BaseModel):
    id: int
    username: str
    email: Optional[str] = ''
    first_name: Optional[str] = ''
    last_name: Optional[str] = ''
    role: str
    phone: Optional[str] = ''
    branch_id: Optional[int] = None
    branch_name: Optional[str] = None
    tenant_schema: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class BranchIn(BaseModel):
    name: str
    address: Optional[str] = ''
    phone: Optional[str] = ''
    gstin: Optional[str] = ''
    is_active: bool = True


class BranchOut(BaseModel):
    id: int
    name: str
    address: Optional[str] = ''
    phone: Optional[str] = ''
    gstin: Optional[str] = ''
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# PRODUCT SCHEMAS
# ==============================================================================

class CategoryIn(BaseModel):
    name: str
    description: Optional[str] = ''


class CategoryOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = ''

    model_config = ConfigDict(from_attributes=True)


class PurityIn(BaseModel):
    name: str
    fineness: Decimal = Field(..., max_digits=5, decimal_places=3)


class PurityOut(BaseModel):
    id: int
    name: str
    fineness: Decimal

    model_config = ConfigDict(from_attributes=True)


class ProductIn(BaseModel):
    name: str
    sku: str
    category_id: int
    purity_id: int
    gross_weight: Decimal = Field(..., gt=0, max_digits=10, decimal_places=3)
    stone_weight: Decimal = Field(default=Decimal('0.000'), ge=0, max_digits=10, decimal_places=3)
    other_weight: Decimal = Field(default=Decimal('0.000'), ge=0, max_digits=10, decimal_places=3)
    making_charge_type: str = 'per_gram'
    making_charge_value: Decimal = Field(default=Decimal('0.00'), ge=0, max_digits=10, decimal_places=2)
    description: Optional[str] = ''
    hsn_code: Optional[str] = '7113'
    huid: Optional[str] = ''
    branch_id: Optional[int] = None
    initial_stock: int = Field(default=1, ge=0)


class ProductUpdateIn(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    purity_id: Optional[int] = None
    gross_weight: Optional[Decimal] = Field(default=None, gt=0, max_digits=10, decimal_places=3)
    stone_weight: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=3)
    other_weight: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=3)
    making_charge_type: Optional[str] = None
    making_charge_value: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    description: Optional[str] = None
    hsn_code: Optional[str] = None
    huid: Optional[str] = None
    is_active: Optional[bool] = None


class ProductOut(BaseModel):
    id: int
    name: str
    sku: str
    category_id: int
    category_name: Optional[str] = None
    purity_id: int
    purity_name: Optional[str] = None
    gross_weight: Decimal
    stone_weight: Decimal
    other_weight: Decimal
    net_weight: Decimal
    making_charge_type: str
    making_charge_value: Decimal
    description: Optional[str] = ''
    hsn_code: Optional[str] = '7113'
    huid: Optional[str] = ''
    photo_url: Optional[str] = None
    qr_code_url: Optional[str] = None
    is_active: bool
    branch_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductListOut(BaseModel):
    id: int
    name: str
    sku: str
    category_id: int
    category_name: Optional[str] = None
    purity_id: int
    purity_name: Optional[str] = None
    gross_weight: Decimal
    stone_weight: Optional[Decimal] = Decimal('0.000')
    other_weight: Optional[Decimal] = Decimal('0.000')
    net_weight: Decimal
    making_charge_type: Optional[str] = 'per_gram'
    making_charge_value: Optional[Decimal] = Decimal('0.00')
    huid: Optional[str] = ''
    photo_url: Optional[str] = None
    qr_code_url: Optional[str] = None
    item_status: Optional[str] = 'AVAILABLE'
    is_active: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# STOCK SCHEMAS
# ==============================================================================

class StockMovementIn(BaseModel):
    product_id: int
    movement_type: str  # 'IN', 'OUT', 'RETURN', 'EXCHANGE', 'ADJUSTMENT'
    quantity: int = Field(default=1, gt=0, le=100000)
    reference_type: Optional[str] = ''
    reference_id: Optional[int] = None
    note: Optional[str] = ''


class StockMovementOut(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    movement_type: str
    quantity: int
    reference_type: Optional[str] = ''
    reference_id: Optional[int] = None
    note: Optional[str] = ''
    created_by_name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StockSummaryOut(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    category: Optional[str] = None
    quantity_on_hand: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# BILLING / POS SCHEMAS
# ==============================================================================

class SaleItemIn(BaseModel):
    product_id: int
    quantity: int = Field(default=1, gt=0, le=10000)
    gold_rate_per_gram: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    making_charge: Decimal = Field(default=Decimal('0.00'), ge=0, max_digits=10, decimal_places=2)
    stone_charge: Decimal = Field(default=Decimal('0.00'), ge=0, max_digits=10, decimal_places=2)


class PaymentIn(BaseModel):
    method: str  # 'cash', 'upi', 'card', 'cheque', 'old_gold'
    amount: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2)
    reference: Optional[str] = ''
    note: Optional[str] = ''


class SaleCreateIn(BaseModel):
    customer_id: Optional[int] = None
    items: List[SaleItemIn]
    # Primary payment or split payments
    payment: Optional[PaymentIn] = None
    payments: Optional[List[PaymentIn]] = None
    discount: Decimal = Field(default=Decimal('0.00'), ge=0, max_digits=12, decimal_places=2)
    old_gold_weight: Decimal = Field(default=Decimal('0.000'), ge=0, max_digits=10, decimal_places=3)
    old_gold_rate: Decimal = Field(default=Decimal('0.00'), ge=0, max_digits=10, decimal_places=2)
    notes: Optional[str] = ''


class SaleItemOut(BaseModel):
    id: int
    product_id: int
    product_name: str
    sku: str
    purity: str
    quantity: int = 1
    gross_weight: Decimal
    net_weight: Decimal
    gold_rate_per_gram: Decimal
    making_charge: Decimal
    stone_charge: Decimal
    unit_price: Decimal
    total_price: Decimal
    hsn_code: str
    gst_rate: Decimal
    huid: Optional[str] = ''
    wastage_percent: Optional[Decimal] = Decimal('0.00')

    model_config = ConfigDict(from_attributes=True)


class PaymentOut(BaseModel):
    id: int
    method: str
    amount: Decimal
    reference: Optional[str] = ''
    paid_at: datetime
    note: Optional[str] = ''

    model_config = ConfigDict(from_attributes=True)


class InvoiceSettingOut(BaseModel):
    id: int
    branch_id: int
    header_invocation: str = ''
    shop_name_primary: str
    shop_name_secondary: str = ''
    tagline: str = ''
    address_primary: str
    address_secondary: str = ''
    phone_landline: str = ''
    phone_mobile_1: str = ''
    phone_mobile_2: str = ''
    email: str = ''
    website: str = ''
    gstin: str
    pan_number: str = ''
    state_name: str
    state_code: str
    bis_hallmark_licence: str = ''
    logo_url: str = ''
    template_style: str
    default_paper_size: str
    show_invocation: bool = True
    show_bilingual_header: bool = True
    show_huid: bool = True
    show_purity: bool = True
    show_gross_net_weight: bool = True
    show_wastage: bool = True
    show_making_charge: bool = True
    show_stone_details: bool = True
    show_rate_per_gram: bool = True
    show_old_gold_section: bool = True
    show_upi_qr: bool = True
    show_bank_details: bool = True
    show_customer_address: bool = True
    show_hallmark_badge: bool = True
    bank_name: str = ''
    account_name: str = ''
    account_number: str = ''
    ifsc_code: str = ''
    upi_id: str = ''
    terms_and_conditions: str
    declaration: str
    signatory_title: str

    model_config = ConfigDict(from_attributes=True)


class InvoiceSettingUpdateIn(BaseModel):
    header_invocation: Optional[str] = None
    shop_name_primary: Optional[str] = None
    shop_name_secondary: Optional[str] = None
    tagline: Optional[str] = None
    address_primary: Optional[str] = None
    address_secondary: Optional[str] = None
    phone_landline: Optional[str] = None
    phone_mobile_1: Optional[str] = None
    phone_mobile_2: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    gstin: Optional[str] = None
    pan_number: Optional[str] = None
    state_name: Optional[str] = None
    state_code: Optional[str] = None
    bis_hallmark_licence: Optional[str] = None
    logo_url: Optional[str] = None
    template_style: Optional[str] = None
    default_paper_size: Optional[str] = None
    show_invocation: Optional[bool] = None
    show_bilingual_header: Optional[bool] = None
    show_huid: Optional[bool] = None
    show_purity: Optional[bool] = None
    show_gross_net_weight: Optional[bool] = None
    show_wastage: Optional[bool] = None
    show_making_charge: Optional[bool] = None
    show_stone_details: Optional[bool] = None
    show_rate_per_gram: Optional[bool] = None
    show_old_gold_section: Optional[bool] = None
    show_upi_qr: Optional[bool] = None
    show_bank_details: Optional[bool] = None
    show_customer_address: Optional[bool] = None
    show_hallmark_badge: Optional[bool] = None
    bank_name: Optional[str] = None
    account_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    upi_id: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    declaration: Optional[str] = None
    signatory_title: Optional[str] = None


class SaleOut(BaseModel):
    id: int
    invoice_number: str
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    customer_pan: Optional[str] = None
    branch_id: Optional[int] = None
    sale_date: datetime
    gold_rate_per_gram: Decimal
    subtotal: Decimal
    discount: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    total_amount: Decimal
    amount_paid: Decimal
    old_gold_value: Decimal
    balance_due: Decimal
    payment_status: str
    sale_status: str
    notes: Optional[str] = ''
    items: List[SaleItemOut] = []
    payments: List[PaymentOut] = []
    invoice_setting: Optional[InvoiceSettingOut] = None
    shop_snapshot: Optional[dict] = {}
    customer_snapshot: Optional[dict] = {}
    pdf_sha256: Optional[str] = ''

    model_config = ConfigDict(from_attributes=True)


class SaleListOut(BaseModel):
    id: int
    invoice_number: str
    customer_name: Optional[str] = None
    total_amount: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    payment_status: str
    sale_status: str
    sale_date: datetime
    items_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class AddPaymentIn(BaseModel):
    method: str
    amount: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2)
    reference: Optional[str] = ''
    note: Optional[str] = ''


# ==============================================================================
# ACCOUNTING SCHEMAS
# ==============================================================================

class GoldRateIn(BaseModel):
    purity_id: Optional[int] = None
    purity: Optional[int] = None
    rate_per_gram: Decimal = Field(..., max_digits=10, decimal_places=2)
    effective_date: Optional[date] = None
    is_current: bool = True


class GoldRateOut(BaseModel):
    id: int
    purity_id: int
    purity: Optional[int] = None
    purity_name: Optional[str] = None
    rate_per_gram: Decimal
    effective_date: date
    is_current: bool
    entered_by_name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RateSourceOut(BaseModel):
    id: str
    name: str
    url: str
    description: str
    is_default: bool = False


class SyncRatesIn(BaseModel):
    source: str = 'ksjf'
    branch_id: Optional[int] = None


class SyncRatesResponse(BaseModel):
    status: str
    source_id: str
    source_name: str
    effective_date: date
    updated_count: int
    message: str
    rates: List[GoldRateOut] = []


class ShopRateSettingIn(BaseModel):
    preferred_source: str


class ShopRateSettingOut(BaseModel):
    preferred_source: str
    last_synced_at: Optional[datetime] = None
    last_synced_source: Optional[str] = ''



class CustomerIn(BaseModel):
    name: str
    phone: str
    email: Optional[str] = ''
    address: Optional[str] = ''
    pan_number: Optional[str] = ''
    aadhar_last4: Optional[str] = ''


class CustomerOut(BaseModel):
    id: int
    name: str
    phone: str
    email: Optional[str] = ''
    address: Optional[str] = ''
    pan_number: Optional[str] = ''
    aadhar_last4: Optional[str] = ''
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DayBookOut(BaseModel):
    id: int
    date: date
    branch_id: Optional[int] = None
    branch_name: Optional[str] = None
    opening_balance: Decimal
    cash_in: Decimal
    cash_out: Decimal
    closing_balance: Decimal
    net_cash: Decimal
    is_closed: bool
    notes: Optional[str] = ''
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CloseDayIn(BaseModel):
    notes: Optional[str] = ''


class CashEntryIn(BaseModel):
    entry_type: str  # 'in' or 'out'
    amount: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2)
    note: Optional[str] = ''


class DayBookPatchIn(BaseModel):
    cash_in: Optional[Decimal] = None
    cash_out: Optional[Decimal] = None
    notes: Optional[str] = None


# ==============================================================================
# QR TAGS SCHEMAS
# ==============================================================================

class QRTagOut(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    purity: Optional[str] = None
    gross_weight: Optional[Decimal] = None
    net_weight: Optional[Decimal] = None
    qr_data: str
    qr_image_url: Optional[str] = None
    printed_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BatchQRIn(BaseModel):
    product_ids: List[int]


# ==============================================================================
# POS PAIRING SCHEMAS
# ==============================================================================

class StartPairingIn(BaseModel):
    base_url: Optional[str] = None


class StartPairingOut(BaseModel):
    session_id: str
    pairing_code: str
    scanner_url: str
    qr_data_url: str
    detected_lan_ip: Optional[str] = None
    expires_at: str
    expires_in_seconds: Optional[int] = 300
    branch_name: Optional[str] = None
    pairing_url: Optional[str] = None
    qr_code_base64: Optional[str] = None


class RedeemPairingIn(BaseModel):
    session_id: str
    pairing_code: str
    device_info: Optional[str] = ''
    tenant_schema: Optional[str] = None


class RedeemPairingOut(BaseModel):
    status: str
    mobile_token: str
    session_id: str
    branch_id: Optional[int] = None
    user_name: Optional[str] = None
    branch_name: Optional[str] = None
    expires_at: str


class RevokePairingIn(BaseModel):
    session_id: str


class MobileScanIn(BaseModel):
    event_id: str
    qr_payload: str
    timestamp: Optional[str] = None


# ==============================================================================
# TENANT MANAGEMENT SCHEMAS
# ==============================================================================

class DomainOut(BaseModel):
    id: int
    domain: str
    is_primary: bool

    model_config = ConfigDict(from_attributes=True)


class TenantOut(BaseModel):
    id: int
    name: str
    schema_name: str
    description: Optional[str] = ''
    is_active: bool
    created_on: date
    domains: List[DomainOut] = []

    model_config = ConfigDict(from_attributes=True)


class TenantCreateIn(BaseModel):
    name: str
    schema_name: str
    domain: str
    description: Optional[str] = ''


# ==============================================================================
# AUTHORITATIVE HTTP POLLING BILL & ITEM SCHEMAS
# ==============================================================================

import uuid

class BillCreateResponse(BaseModel):
    bill_id: uuid.UUID
    status: str
    token: str
    https_url: Optional[str] = None
    created_at: datetime


class ItemOut(BaseModel):
    id: int
    qr_code: str
    name: Optional[str] = ''
    weight: Decimal
    status: str

    model_config = ConfigDict(from_attributes=True)


class BillDetailResponse(BaseModel):
    bill_id: uuid.UUID
    status: str
    created_at: datetime
    total_weight: Decimal
    item_count: int
    items: List[ItemOut]


class ScanItemIn(BaseModel):
    qr_code: str = Field(..., min_length=1, max_length=128)


class ScanItemResponse(BaseModel):
    status: str
    message: str
    bill_id: uuid.UUID
    item: ItemOut
    is_duplicate: bool = False

