# Graph Report - swarna_khata_book  (2026-10-25)

## Corpus Check
- 139 files · ~49,223 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 4, .css 2, .bat 1)

## Summary
- 1031 nodes · 2260 edges · 74 communities (35 shown, 39 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 244 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d461aaaf`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Sale
- django_db
- BackendAuthoritativePollingTestCase
- pairing.py
- Client
- bills_router.py
- App.tsx
- backend
- compilerOptions
- django_apps
- compilerOptions
- schemas.py
- validate_password_policy
- .oxlintrc.json
- tenants/admin.py
- tsconfig.json
- swarna-khata-book
- Quick Start (Local Development)
- React + TypeScript + Vite
- Master Feature Checklist & Test Mapping
- GoldRate
- POSSessionHub
- accounting_router.py
- DayBook
- base.py
- NinjaProductsStockTestCase
- dependencies
- NinjaPOSBillingTestCase
- products_router.py
- tenants_router.py
- package.json
- MobileQRScanner.tsx
- billing/models.py
- billing/services.py
- create_token
- billing_router.py
- list_users
- middleware.py
- vite.config.ts
- StockMovement
- accounting/services.py
- User
- scripts
- JWTAuth
- ProductAdmin
- @playwright/test
- CustomUserAdmin
- verify-before-complete.md

## God Nodes (most connected - your core abstractions)
1. `Client` - 44 edges
2. `User` - 38 edges
3. `Product` - 38 edges
4. `create_token()` - 38 edges
5. `Branch` - 33 edges
6. `Purity` - 29 edges
7. `Domain` - 28 edges
8. `require_role()` - 26 edges
9. `StoreOnboardingAndRBACTestCase` - 22 edges
10. `DayBook` - 21 edges

## Surprising Connections (you probably didn't know these)
- `DomainInline` --uses--> `Domain`  [INFERRED]
  backend/apps/tenants/admin.py → backend/apps/tenants/models.py
- `sync_live_rates_async()` --uses--> `GoldRate`  [INFERRED]
  backend/apps/accounting/services.py → backend/apps/accounting/models.py
- `sync_rates_from_source()` --uses--> `GoldRate`  [INFERRED]
  backend/apps/accounting/services.py → backend/apps/accounting/models.py
- `create_gold_rate()` --uses--> `GoldRate`  [INFERRED]
  backend/ninja_api/routers/accounting_router.py → backend/apps/accounting/models.py
- `MultiSourceGoldRateScraperTestCase` --uses--> `GoldRate`  [INFERRED]
  backend/tests/test_multi_source_scraper.py → backend/apps/accounting/models.py

## Import Cycles
- None detected.

## Communities (74 total, 39 thin omitted)

### Community 0 - "Sale"
Cohesion: 0.13
Nodes (13): Sale, Meta, PaymentStatus, SaleStatus, create_sale(), _next_invoice_number(), add_sale_payment(), cancel_sale() (+5 more)

### Community 1 - "django_db"
Cohesion: 0.09
Nodes (12): Migration, Migration, Migration, Migration, Migration, Migration, Migration, Migration (+4 more)

### Community 2 - "BackendAuthoritativePollingTestCase"
Cohesion: 0.09
Nodes (4): IdempotencyRecord, Meta, generate_bill_token(), BackendAuthoritativePollingTestCase

### Community 3 - "pairing.py"
Cohesion: 0.06
Nodes (26): POSPairingSession, Meta, ScannedItemAudit, Meta, generate_pairing_qr_data_url(), get_lan_ip(), redeem_pairing_code(), resolve_and_record_scan() (+18 more)

### Community 4 - "Client"
Cohesion: 0.11
Nodes (15): Client, Meta, create_tenant(), developer_overview(), developer_reset_user_password(), developer_switch_store_token(), _format_tenant(), generate_schema_name() (+7 more)

### Community 5 - "bills_router.py"
Cohesion: 0.14
Nodes (11): Bill, Meta, Status, create_bill(), get_bill_cart(), scan_item_into_bill(), BillCreateResponse, BillDetailResponse (+3 more)

### Community 6 - "App.tsx"
Cohesion: 0.07
Nodes (56): axios@^1.20.0, api, App(), ProtectedRoute(), Layout(), PasswordPolicyChecklist(), PasswordPolicyChecklistProps, AuthContext (+48 more)

### Community 7 - "backend"
Cohesion: 0.06
Nodes (34): build, command, depends_on, env_file, ports, volumes, context, dockerfile (+26 more)

### Community 8 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+11 more)

### Community 9 - "django_apps"
Cohesion: 0.09
Nodes (7): AccountingConfig, AccountsConfig, BillingConfig, ProductsConfig, QrTagsConfig, StockConfig, TenantsConfig

### Community 10 - "compilerOptions"
Cohesion: 0.12
Nodes (16): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+8 more)

### Community 11 - "schemas.py"
Cohesion: 0.12
Nodes (30): AddPaymentIn, BranchOut, CategoryOut, DomainOut, PasswordChangeIn, PaymentIn, PaymentOut, ProductListOut (+22 more)

### Community 12 - "validate_password_policy"
Cohesion: 0.11
Nodes (3): JewelleryPasswordPolicyValidator, validate_password_policy(), PasswordPolicyTestCase

### Community 13 - ".oxlintrc.json"
Cohesion: 0.33
Nodes (5): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema

### Community 14 - "tenants/admin.py"
Cohesion: 0.12
Nodes (5): DayBookAdmin, ClientAdmin, DomainAdmin, DomainInline, health_check()

### Community 33 - "Quick Start (Local Development)"
Cohesion: 0.09
Nodes (20): Jewellery ERP — Coding Workflow Mindmap, 1. Camera Photo Capture & QR Code Barcode Tags, 1-Click Launch (Windows), 1. Install Dependencies & Synchronize Environment, 2. POS Billing & Invoicing, 2. Run Database Migrations, 3. Accounting & Day Book, 3. Seed Initial Demo Data (Showroom, Gold Rates, Categories, Sample Items) (+12 more)

### Community 34 - "React + TypeScript + Vite"
Cohesion: 0.50
Nodes (3): Expanding the Oxlint configuration, React Compiler, React + TypeScript + Vite

### Community 36 - "Master Feature Checklist & Test Mapping"
Cohesion: 0.12
Nodes (15): 1. Store Onboarding & Identity Management, 2. Developer Superadmin Control Plane, 3. Bullion Rates & Live Web Scraper, 4. POS Billing & Invoicing, 5. Mobile QR Scanner Pairing Session, 6. Products, Inventory & QR Barcodes, 7. Daybook & Double-Entry Accounting, Master Feature Checklist & Test Mapping (+7 more)

### Community 37 - "GoldRate"
Cohesion: 0.11
Nodes (9): GoldRate, Meta, ShopRateSetting, get_current_rates(), get_customer(), get_live_market_rates(), get_rate_settings(), get_rate_sources() (+1 more)

### Community 39 - "accounting_router.py"
Cohesion: 0.10
Nodes (18): Customer, sync_rates_from_source(), create_customer(), create_gold_rate(), list_customers(), sync_rates_from_web(), update_customer(), update_rate_settings() (+10 more)

### Community 40 - "DayBook"
Cohesion: 0.17
Nodes (9): DayBook, Meta, close_day_book(), _format_daybook(), get_today_day_book(), list_day_books(), record_petty_cash_entry(), CashEntryIn (+1 more)

### Community 43 - "base.py"
Cohesion: 0.07
Nodes (8): BaseRateScraper, RateScrapeResult, BullionDeskScraper, IBJAScraper, KSJFScraper, get_scraper(), list_available_sources(), MultiSourceGoldRateScraperTestCase

### Community 45 - "dependencies"
Cohesion: 0.11
Nodes (19): dependencies, @hookform/resolvers@^6.0.0, html5-qrcode@^2.3.8, lucide-react@^1.61.0, react@^19.3.1, react-dom@^19.3.1, react-hook-form@^7.90.0, react-hot-toast@^2.6.1 (+11 more)

### Community 48 - "products_router.py"
Cohesion: 0.06
Nodes (34): Item, Meta, Status, ProductFilter, Meta, Product, Meta, QRTagAdmin (+26 more)

### Community 49 - "tenants_router.py"
Cohesion: 0.11
Nodes (16): User, Role, decode_token(), require_role(), change_own_password(), create_branch(), create_user(), list_users() (+8 more)

### Community 50 - "package.json"
Cohesion: 0.17
Nodes (15): devDependencies, oxlint@^1.88.0, @types/node@^24.19.2, @types/react@^19.3.0, @types/react-dom@^19.3.0, typescript@~6.0.3, name, private (+7 more)

### Community 51 - "MobileQRScanner.tsx"
Cohesion: 0.20
Nodes (10): @zxing/browser@^0.2.1, @zxing/library@^0.23.0, beep(), isVideoReady(), makeReader(), startDecodeLoop(), MobileQRScannerProps, ScannerState (+2 more)

### Community 52 - "billing/models.py"
Cohesion: 0.25
Nodes (6): PaymentInline, SaleAdmin, SaleItemInline, Payment, PaymentMethod, SaleItem

### Community 54 - "create_token"
Cohesion: 0.06
Nodes (5): create_token(), DayBookAccountingTestCase, DeveloperPortalTestCase, NinjaAuthTestCase, StoreOnboardingAndRBACTestCase

### Community 55 - "billing_router.py"
Cohesion: 0.31
Nodes (3): not_found_handler(), permission_error_handler(), value_error_handler()

### Community 56 - "list_users"
Cohesion: 0.18
Nodes (5): Branch, Meta, get_branch(), get_current_user(), list_branches()

### Community 58 - "vite.config.ts"
Cohesion: 0.20
Nodes (8): @tailwindcss/vite@^4.3.3, vite@^8.3.4, @vitejs/plugin-basic-ssl@^2.3.0, @vitejs/plugin-react@^6.1.2, @tailwindcss/vite, vite, @vitejs/plugin-basic-ssl, @vitejs/plugin-react

### Community 59 - "StockMovement"
Cohesion: 0.13
Nodes (11): StockMovementAdmin, StockSummaryAdmin, StockMovement, Meta, MovementType, StockSummary, Meta, record_stock_movement() (+3 more)

### Community 62 - "User"
Cohesion: 0.18
Nodes (6): Category, Meta, Purity, Meta, Domain, TenantIsolationTestCase

### Community 63 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, lint, preview, test:e2e

## Knowledge Gaps
- **1 isolated node(s):** `swarna-khata-book`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 433 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **39 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Product` connect `products_router.py` to `Sale`, `pairing.py`, `Client`, `NinjaProductsStockTestCase`, `NinjaPOSBillingTestCase`, `create_token`, `billing_router.py`, `StockMovement`, `User`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `Client` (e.g. with `create_tenant()` and `developer_overview()`) actually correct?**
  _`Client` has 19 INFERRED edges - model-reasoned connections that need verification._
- **What connects `swarna-khata-book` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Sale` be split into smaller, more focused modules?**
  _Cohesion score 0.12648221343873517 - nodes in this community are weakly interconnected._
- **Why does `validate_password_policy()` connect `validate_password_policy` to `schemas.py`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `User` (e.g. with `create_token()` and `JWTAuth`) actually correct?**
  _`User` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Should `django_db` be split into smaller, more focused modules?**
  _Cohesion score 0.08669354838709678 - nodes in this community are weakly interconnected._