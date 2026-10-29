# Graph Report - swarna_khata_book  (2026-10-28)

## Corpus Check
- 159 files · ~74,555 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .bat 3, .css 2)

## Summary
- 1246 nodes · 2899 edges · 82 communities (43 shown, 39 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 323 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `96004c74`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- bills_router.py
- django_db
- accounting_router.py
- Product
- products_router.py
- tenants_router.py
- pos_pairing_router.py
- backend
- compilerOptions
- django_apps
- compilerOptions
- schemas.py
- validate_password_policy
- .oxlintrc.json
- billing_router.py
- tsconfig.json
- swarna-khata-book
- Quick Start (Local Development)
- React + TypeScript + Vite
- Master Feature Checklist & Test Mapping
- package.json
- POSSessionHub
- InvoiceSetting
- package.json
- Client
- devDependencies
- App.tsx
- NinjaPOSBillingTestCase
- billing/models.py
- auth_router.py
- DayBookAccountingTestCase
- BackendAuthoritativePollingTestCase
- InvoiceSettingsTestCase
- vite.config.ts
- create_token
- bills_router.py
- middleware.py
- ClientAdmin
- base.py
- POSPairingSession
- SecurityAuditAndAccessControlTestCase
- User
- qr_tags_router.py
- websocket_handler.py
- export_tenant_data_to_zip
- @playwright/test
- pairing.py
- scripts
- ScannedItemAudit
- verify-before-complete.md
- Purity
- qrcode
- billing/services.py
- urls.py
- DataExportTestCase
- DayBook
- JWTAuth
- CustomUserAdmin
- StockSummary

## God Nodes (most connected - your core abstractions)
1. `Client` - 60 edges
2. `create_token()` - 55 edges
3. `User` - 51 edges
4. `Branch` - 51 edges
5. `Product` - 48 edges
6. `require_role()` - 42 edges
7. `Purity` - 41 edges
8. `Domain` - 36 edges
9. `Category` - 30 edges
10. `StockSummary` - 29 edges

## Surprising Connections (you probably didn't know these)
- `DomainInline` --uses--> `Domain`  [INFERRED]
  backend/apps/tenants/admin.py → backend/apps/tenants/models.py
- `sync_live_rates_async()` --uses--> `GoldRate`  [INFERRED]
  backend/apps/accounting/services.py → backend/apps/accounting/models.py
- `sync_rates_from_source()` --uses--> `GoldRate`  [INFERRED]
  backend/apps/accounting/services.py → backend/apps/accounting/models.py
- `export_tenant_data_to_zip()` --uses--> `GoldRate`  [INFERRED]
  backend/apps/tenants/export_service.py → backend/apps/accounting/models.py
- `create_gold_rate()` --uses--> `GoldRate`  [INFERRED]
  backend/ninja_api/routers/accounting_router.py → backend/apps/accounting/models.py

## Import Cycles
- None detected.

## Communities (82 total, 39 thin omitted)

### Community 0 - "bills_router.py"
Cohesion: 0.15
Nodes (11): Bill, Meta, Status, create_bill(), get_bill_cart(), scan_item_into_bill(), BillCreateResponse, BillDetailResponse (+3 more)

### Community 1 - "django_db"
Cohesion: 0.07
Nodes (14): Migration, Migration, Migration, Migration, Migration, Migration, Migration, Migration (+6 more)

### Community 2 - "accounting_router.py"
Cohesion: 0.05
Nodes (28): ShopRateSetting, get_scraper(), list_available_sources(), fetch_live_market_rates_async(), sync_live_rates_async(), sync_rates_from_source(), close_day_book(), close_day_book_alias() (+20 more)

### Community 3 - "Product"
Cohesion: 0.20
Nodes (5): ProductAdmin, ProductFilter, Meta, Product, Meta

### Community 4 - "products_router.py"
Cohesion: 0.09
Nodes (22): require_role(), create_category(), create_product(), create_purity(), delete_product(), _format_product(), get_product(), list_categories() (+14 more)

### Community 5 - "tenants_router.py"
Cohesion: 0.11
Nodes (16): create_tenant(), developer_login(), developer_overview(), developer_reset_user_password(), developer_switch_store_token(), developer_toggle_user_status(), _format_tenant(), list_tenants() (+8 more)

### Community 6 - "pos_pairing_router.py"
Cohesion: 0.19
Nodes (9): revoke_pairing_session(), mobile_scan_fallback(), redeem_pos_pairing_token(), revoke_pos_pairing_token(), start_pos_pairing_session(), MobileScanIn, RedeemPairingIn, RevokePairingIn (+1 more)

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
Cohesion: 0.13
Nodes (25): AddPaymentIn, CashEntryIn, CloseDayIn, CustomerOut, DayBookOut, DayBookPatchIn, DomainOut, GoldRateIn (+17 more)

### Community 12 - "validate_password_policy"
Cohesion: 0.10
Nodes (4): JewelleryPasswordPolicyValidator, validate_password_policy(), generate_schema_name(), PasswordPolicyTestCase

### Community 13 - ".oxlintrc.json"
Cohesion: 0.33
Nodes (5): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema

### Community 14 - "billing_router.py"
Cohesion: 0.11
Nodes (16): Sale, Meta, PaymentStatus, SaleStatus, _next_invoice_number(), record_stock_movement(), add_sale_payment(), cancel_sale() (+8 more)

### Community 33 - "Quick Start (Local Development)"
Cohesion: 0.09
Nodes (20): Jewellery ERP — Coding Workflow Mindmap, 1. Camera Photo Capture & QR Code Barcode Tags, 1-Click Launch (Windows), 1. Install Dependencies & Synchronize Environment, 2. POS Billing & Invoicing, 2. Run Database Migrations, 3. Accounting & Day Book, 3. Seed Initial Demo Data (Showroom, Gold Rates, Categories, Sample Items) (+12 more)

### Community 34 - "React + TypeScript + Vite"
Cohesion: 0.50
Nodes (3): Expanding the Oxlint configuration, React Compiler, React + TypeScript + Vite

### Community 36 - "Master Feature Checklist & Test Mapping"
Cohesion: 0.12
Nodes (15): 1. Store Onboarding & Identity Management, 2. Developer Superadmin Control Plane, 3. Bullion Rates & Live Web Scraper, 4. POS Billing & Invoicing, 5. Mobile QR Scanner Pairing Session, 6. Products, Inventory & QR Barcodes, 7. Daybook & Double-Entry Accounting, Master Feature Checklist & Test Mapping (+7 more)

### Community 37 - "package.json"
Cohesion: 0.15
Nodes (12): axios@^1.20.0, @tanstack/react-query@^5.104.5, zod@^4.6.7, @zxing/browser@^0.2.1, name, private, type, version (+4 more)

### Community 39 - "InvoiceSetting"
Cohesion: 0.25
Nodes (4): InvoiceSetting, PaperSize, TemplateStyle, update_invoice_settings()

### Community 40 - "package.json"
Cohesion: 0.11
Nodes (19): dependencies, @hookform/resolvers@^6.0.0, html5-qrcode@^2.3.8, lucide-react@^1.61.0, react@^19.3.1, react-dom@^19.3.1, react-hook-form@^7.90.0, react-hot-toast@^2.6.1 (+11 more)

### Community 43 - "Client"
Cohesion: 0.09
Nodes (5): Client, Meta, InvoiceSnapshotImmutabilityTestCase, NinjaProductsStockTestCase, TenantIsolationTestCase

### Community 44 - "devDependencies"
Cohesion: 0.17
Nodes (12): devDependencies, oxlint@^1.88.0, @playwright/test@^1.64.1, @types/node@^24.19.2, @types/react@^19.3.0, @types/react-dom@^19.3.0, typescript@~6.0.3, oxlint (+4 more)

### Community 45 - "App.tsx"
Cohesion: 0.05
Nodes (87): api, App(), FeatureRoute(), ProtectedRoute(), Layout(), PasswordPolicyChecklist(), PasswordPolicyChecklistProps, AuthContext (+79 more)

### Community 48 - "billing/models.py"
Cohesion: 0.25
Nodes (6): PaymentInline, SaleAdmin, SaleItemInline, Payment, PaymentMethod, SaleItem

### Community 49 - "auth_router.py"
Cohesion: 0.07
Nodes (22): decode_token(), change_own_password(), create_branch(), create_user(), get_branch(), get_current_user(), list_branches(), list_users() (+14 more)

### Community 51 - "BackendAuthoritativePollingTestCase"
Cohesion: 0.09
Nodes (4): IdempotencyRecord, Meta, generate_bill_token(), BackendAuthoritativePollingTestCase

### Community 53 - "vite.config.ts"
Cohesion: 0.20
Nodes (8): @tailwindcss/vite@^4.3.3, vite@^8.3.4, @vitejs/plugin-basic-ssl@^2.3.0, @vitejs/plugin-react@^6.1.2, @tailwindcss/vite, vite, @vitejs/plugin-basic-ssl, @vitejs/plugin-react

### Community 54 - "create_token"
Cohesion: 0.06
Nodes (4): create_token(), DeveloperPortalTestCase, NinjaAuthTestCase, StoreOnboardingAndRBACTestCase

### Community 55 - "bills_router.py"
Cohesion: 0.16
Nodes (7): not_found_handler(), permission_error_handler(), value_error_handler(), create_stock_movement(), StockMovementIn, StockMovementOut, StockSummaryOut

### Community 58 - "base.py"
Cohesion: 0.07
Nodes (6): BaseRateScraper, RateScrapeResult, BullionDeskScraper, IBJAScraper, KSJFScraper, MultiSourceGoldRateScraperTestCase

### Community 59 - "POSPairingSession"
Cohesion: 0.29
Nodes (3): POSPairingSession, Meta, redeem_pairing_code()

### Community 62 - "User"
Cohesion: 0.18
Nodes (8): Customer, Branch, Meta, User, Role, Category, Meta, Domain

### Community 63 - "qr_tags_router.py"
Cohesion: 0.15
Nodes (13): QRTagAdmin, QRTag, Meta, generate_qr_batch_async(), _threaded_qr(), generate_qr_for_product(), batch_generate_tags(), _format_qrtag() (+5 more)

### Community 64 - "websocket_handler.py"
Cohesion: 0.16
Nodes (7): get_active_session(), mobile_websocket_app(), parse_query_string(), pos_websocket_app(), send_json(), validate_jwt_user(), application()

### Community 65 - "export_tenant_data_to_zip"
Cohesion: 0.07
Nodes (8): CleanupFile, export_tenant_data_to_zip(), generate_all_shops_export_archive(), generate_shop_export_archive(), _write_csv_to_zip(), export_all_shops_data(), export_shop_data(), _parse_date()

### Community 67 - "pairing.py"
Cohesion: 0.21
Nodes (4): generate_pairing_qr_data_url(), get_lan_ip(), start_pairing_session(), verify_mobile_token()

### Community 68 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, lint, preview, test:e2e, tunnel

### Community 69 - "ScannedItemAudit"
Cohesion: 0.29
Nodes (4): ScannedItemAudit, Meta, resolve_and_record_scan(), _execute_scan()

### Community 71 - "Purity"
Cohesion: 0.33
Nodes (3): Purity, Meta, register_store()

### Community 74 - "billing/services.py"
Cohesion: 0.10
Nodes (6): Item, Meta, Status, create_sale(), generate_invoice_pdf(), generate_invoice_pdf_async()

### Community 77 - "DayBook"
Cohesion: 0.10
Nodes (7): DayBookAdmin, DayBook, Meta, GoldRate, Meta, DomainInline, get_current_rates()

### Community 86 - "StockSummary"
Cohesion: 0.13
Nodes (9): StockMovementAdmin, StockSummaryAdmin, StockMovement, Meta, MovementType, StockSummary, Meta, list_stock_movements() (+1 more)

## Knowledge Gaps
- **1 isolated node(s):** `swarna-khata-book`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 533 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **39 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Branch` connect `User` to `accounting_router.py`, `products_router.py`, `tenants_router.py`, `InvoiceSetting`, `Purity`, `Client`, `DataExportTestCase`, `DayBook`, `billing_router.py`, `NinjaPOSBillingTestCase`, `auth_router.py`, `DayBookAccountingTestCase`, `BackendAuthoritativePollingTestCase`, `InvoiceSettingsTestCase`, `create_token`, `base.py`, `SecurityAuditAndAccessControlTestCase`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Are the 26 inferred relationships involving `Client` (e.g. with `export_tenant_data_to_zip()` and `generate_all_shops_export_archive()`) actually correct?**
  _`Client` has 26 INFERRED edges - model-reasoned connections that need verification._
- **What connects `swarna-khata-book` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `bills_router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14619883040935672 - nodes in this community are weakly interconnected._
- **Why does `Client` connect `Client` to `export_tenant_data_to_zip`, `tenants_router.py`, `Purity`, `validate_password_policy`, `DayBook`, `DataExportTestCase`, `NinjaPOSBillingTestCase`, `auth_router.py`, `DayBookAccountingTestCase`, `BackendAuthoritativePollingTestCase`, `InvoiceSettingsTestCase`, `create_token`, `base.py`, `SecurityAuditAndAccessControlTestCase`, `User`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 26 inferred relationships involving `User` (e.g. with `export_tenant_data_to_zip()` and `create_token()`) actually correct?**
  _`User` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Should `django_db` be split into smaller, more focused modules?**
  _Cohesion score 0.07254623044096728 - nodes in this community are weakly interconnected._