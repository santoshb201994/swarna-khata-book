# Master Feature Checklist & Test Mapping

This document details all business features of Swarna Khata Book and their corresponding automated verification tests.

## 1. Store Onboarding & Identity Management
- **Description**: Shop owners can register a new tenant, configure store domain, and manage owner and staff credentials.
- **Constraints**:
  - Store codes must be alphanumeric and generate a tenant schema.
  - Password policy requires uppercase, lowercase, numbers, allowed special characters (`!@#$%^&*()_+-=`), and forbids consecutive characters.
  - Staff (Salesman) cannot alter rates or delete invoices.
- **Automated Tests**:
  - `backend/tests/test_store_onboarding_and_rbac.py`
  - `backend/tests/test_password_policy.py`

## 2. Developer Superadmin Control Plane
- **Description**: Platform operators access `/developer` via dedicated obsidian terminal with cross-tenant visibility.
- **Constraints**:
  - `/login` must never display developer options.
  - Superadmin token issued on `public` schema.
  - Can suspend stores, reset passwords, and switch store context.
- **Automated Tests**:
  - `backend/tests/test_developer_portal.py`
  - `frontend/e2e/golden_paths.spec.ts`

## 3. Bullion Rates & Live Web Scraper
- **Description**: Fetches live gold/silver bullion rates from selected websites (e.g. KSJF) and persists them per branch/tenant.
- **Constraints**:
  - Async router handlers must not directly access ORM foreign keys without `sync_to_async`.
  - Scraped purities: 24KT (999), 22KT (916), 18KT (750), 14KT (585), Silver (925).
- **Automated Tests**:
  - `backend/tests/test_multi_source_scraper.py`
  - `backend/tests/test_daybook_accounting.py`

## 4. POS Billing & Invoicing
- **Description**: Fast point-of-sale terminal calculating gross weight, stone weight, net weight, wastage, making charges, and GST.
- **Constraints**:
  - Supports Split Payment (Cash, UPI, Card, Old Gold exchange).
  - Generates immutable financial invoices with tax compliance.
- **Automated Tests**:
  - `backend/tests/test_ninja_pos_billing.py`

## 5. Mobile QR Scanner Pairing Session
- **Description**: Desktop displays QR code; salesman scans via phone camera to pair phone as a wireless barcode reader.
- **Constraints**:
  - Pairing session remains active for 12 hours or until explicit logout.
  - Desktop pairing modal provides explicit "Close" button.
  - Backend authoritative polling architecture.
- **Automated Tests**:
  - `backend/tests/test_backend_authoritative_polling.py`

## 6. Products, Inventory & QR Barcodes
- **Description**: Manages jewellery inventory with item categories, purity tags, weight, and barcode/QR printing.
- **Constraints**:
  - Multi-tenant stock isolation.
  - Stock count decrements automatically on invoice settlement.
- **Automated Tests**:
  - `backend/tests/test_ninja_products_stock.py`
  - `backend/tests/test_tenant_isolation.py`

## 7. Daybook & Double-Entry Accounting
- **Description**: Real-time cash drawer tracking and daily journal ledgers.
- **Constraints**:
  - Every settled bill creates corresponding debit/credit accounting entries.
- **Automated Tests**:
  - `backend/tests/test_daybook_accounting.py`
