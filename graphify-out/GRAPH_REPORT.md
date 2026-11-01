# Graph Report - swarna_khata_book  (2026-11-01)

## Corpus Check
- 176 files · ~85,703 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .bat 3, .css 2)

## Summary
- 1393 nodes · 3233 edges · 100 communities (54 shown, 46 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 368 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `15b00c0b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- products_router.py
- django_db
- MultiSourceGoldRateScraperTestCase
- qr_tags_router.py
- billing_router.py
- tenants_router.py
- billing/services.py
- backend
- compilerOptions
- django_apps
- compilerOptions
- schemas.py
- validate_password_policy
- .oxlintrc.json
- vercel.json
- tsconfig.json
- swarna-khata-book
- Key Modules & Capabilities
- React + TypeScript + Vite
- Master Feature Checklist & Test Mapping
- urls.py
- POSSessionHub
- POSScreen.tsx
- dependencies
- Client
- devDependencies
- App.tsx
- NinjaPOSBillingTestCase
- bills_router.py
- auth_router.py
- accounting_router.py
- websocket_handler.py
- InvoiceSettingsTestCase
- vite.config.ts
- create_token
- render-build.sh
- DayBookAccountingTestCase
- bills_router.py
- Product
- SecurityAuditAndAccessControlTestCase
- User
- resolve_and_record_scan
- billing/models.py
- export_tenant_data_to_zip
- @playwright/test
- logger.ts
- scripts
- pairing.py
- verify-before-complete.md
- jewellery_erp_coding_workflow_mindmap.md
- pos_pairing_router.py
- Item
- TrayQRTagsTestCase
- DataExportTestCase
- ShopRateSetting
- GoldRate
- App.tsx
- DayBook
- services
- CustomUserAdmin
- get
- StockSummary
- Purity
- post
- POSPairingSession
- OldGoldValidationTestCase
- JWTAuth
- @types/qrcode@^1.5.6
- GoldRate
- ProductList.tsx
- react
- logging
- tenants/admin.py
- middleware.py
- package.json
- MobileScannerPage.tsx

## God Nodes (most connected - your core abstractions)
1. `Client` - 70 edges
2. `create_token()` - 61 edges
3. `User` - 57 edges
4. `Branch` - 57 edges
5. `Product` - 55 edges
6. `Purity` - 46 edges
7. `Domain` - 42 edges
8. `require_role()` - 42 edges
9. `Category` - 35 edges
10. `StockSummary` - 31 edges

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

## Communities (100 total, 46 thin omitted)

### Community 0 - "products_router.py"
Cohesion: 0.09
Nodes (23): generate_qr_for_product(), require_role(), create_category(), create_product(), create_purity(), delete_product(), _format_product(), get_product() (+15 more)

### Community 1 - "django_db"
Cohesion: 0.07
Nodes (15): Migration, Migration, Migration, Migration, Migration, Migration, Migration, Migration (+7 more)

### Community 2 - "MultiSourceGoldRateScraperTestCase"
Cohesion: 0.08
Nodes (6): BaseRateScraper, RateScrapeResult, BullionDeskScraper, IBJAScraper, KSJFScraper, MultiSourceGoldRateScraperTestCase

### Community 3 - "qr_tags_router.py"
Cohesion: 0.07
Nodes (25): QRTag, Meta, Tray, Meta, generate_qr_batch_async(), _threaded_qr(), generate_qr_for_tray(), batch_generate_tags() (+17 more)

### Community 4 - "billing_router.py"
Cohesion: 0.10
Nodes (18): Item, Meta, Status, Sale, Meta, PaymentStatus, SaleStatus, _next_invoice_number() (+10 more)

### Community 5 - "tenants_router.py"
Cohesion: 0.11
Nodes (15): create_tenant(), developer_login(), developer_reset_user_password(), developer_switch_store_token(), developer_toggle_user_status(), _format_tenant(), list_tenants(), toggle_tenant_status() (+7 more)

### Community 6 - "billing/services.py"
Cohesion: 0.12
Nodes (6): InvoiceSetting, PaperSize, TemplateStyle, generate_invoice_pdf(), generate_invoice_pdf_async(), update_invoice_settings()

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
Cohesion: 0.11
Nodes (31): AddPaymentIn, CashEntryIn, CloseDayIn, CustomerOut, DayBookOut, DayBookPatchIn, DomainOut, GoldRateIn (+23 more)

### Community 12 - "validate_password_policy"
Cohesion: 0.10
Nodes (4): JewelleryPasswordPolicyValidator, validate_password_policy(), generate_schema_name(), PasswordPolicyTestCase

### Community 13 - ".oxlintrc.json"
Cohesion: 0.33
Nodes (5): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema

### Community 33 - "Key Modules & Capabilities"
Cohesion: 0.12
Nodes (16): 1. 1-Click Launch (Windows), 1. POS Billing & Wireless Mobile QR Scanner, 2. Bullion Rates & Live Web Scrapers, 2. Manual Commands, 3. Accounting & Cash Drawer Day Book, 4. Enterprise Multi-Tenancy & Hierarchical RBAC, 5. Large Data Export Engine, Architecture Overview (+8 more)

### Community 34 - "React + TypeScript + Vite"
Cohesion: 0.50
Nodes (3): Expanding the Oxlint configuration, React Compiler, React + TypeScript + Vite

### Community 36 - "Master Feature Checklist & Test Mapping"
Cohesion: 0.12
Nodes (15): 1. Store Onboarding & Identity Management, 2. Developer Superadmin Control Plane, 3. Bullion Rates & Live Web Scraper, 4. POS Billing & Invoicing, 5. Mobile QR Scanner Pairing Session, 6. Products, Inventory & QR Barcodes, 7. Daybook & Double-Entry Accounting, Master Feature Checklist & Test Mapping (+7 more)

### Community 39 - "POSScreen.tsx"
Cohesion: 0.15
Nodes (24): api, AuthContext, AuthContextType, RateSource, InvoiceModal(), InvoiceModalProps, clean(), detectProductMetal() (+16 more)

### Community 40 - "dependencies"
Cohesion: 0.11
Nodes (19): dependencies, axios@^1.20.0, @hookform/resolvers@^6.0.0, lucide-react@^1.61.0, qrcode@^1.5.4, react@^19.3.1, react-hot-toast@^2.6.1, react-router-dom@^7.18.4 (+11 more)

### Community 43 - "Client"
Cohesion: 0.06
Nodes (6): Client, Meta, NinjaProductsStockTestCase, CustomerEmailValidationTestCase, ProductValidationTestCase, TenantIsolationTestCase

### Community 44 - "devDependencies"
Cohesion: 0.17
Nodes (12): devDependencies, oxlint@^1.88.0, @playwright/test@^1.64.1, @types/node@^24.19.2, @types/react@^19.3.0, @types/react-dom@^19.3.0, typescript@~6.0.3, oxlint (+4 more)

### Community 45 - "App.tsx"
Cohesion: 0.14
Nodes (20): PasswordPolicyChecklist(), PasswordPolicyChecklistProps, Login(), OverviewData, StoreUser, TenantItem, StaffManagementModal(), StaffManagementModalProps (+12 more)

### Community 48 - "bills_router.py"
Cohesion: 0.09
Nodes (4): IdempotencyRecord, Meta, generate_bill_token(), BackendAuthoritativePollingTestCase

### Community 49 - "auth_router.py"
Cohesion: 0.07
Nodes (22): decode_token(), change_own_password(), create_branch(), create_user(), get_branch(), get_current_user(), list_branches(), list_users() (+14 more)

### Community 50 - "accounting_router.py"
Cohesion: 0.43
Nodes (4): create_customer(), update_customer(), update_rate_settings(), CustomerIn

### Community 51 - "websocket_handler.py"
Cohesion: 0.20
Nodes (7): get_active_session(), mobile_websocket_app(), parse_query_string(), pos_websocket_app(), send_json(), validate_jwt_user(), application()

### Community 53 - "vite.config.ts"
Cohesion: 0.20
Nodes (8): @tailwindcss/vite@^4.3.3, vite@^8.3.4, @vitejs/plugin-basic-ssl@^2.3.0, @vitejs/plugin-react@^6.1.2, @tailwindcss/vite, vite, @vitejs/plugin-basic-ssl, @vitejs/plugin-react

### Community 54 - "create_token"
Cohesion: 0.06
Nodes (4): create_token(), DeveloperPortalTestCase, NinjaAuthTestCase, StoreOnboardingAndRBACTestCase

### Community 58 - "bills_router.py"
Cohesion: 0.10
Nodes (14): Bill, Meta, Status, not_found_handler(), permission_error_handler(), value_error_handler(), create_bill(), get_bill_cart() (+6 more)

### Community 59 - "Product"
Cohesion: 0.17
Nodes (6): ProductAdmin, ProductFilter, Meta, Product, Meta, developer_overview()

### Community 62 - "User"
Cohesion: 0.21
Nodes (7): Branch, Meta, User, Role, Category, Meta, Domain

### Community 63 - "resolve_and_record_scan"
Cohesion: 0.29
Nodes (4): ScannedItemAudit, Meta, resolve_and_record_scan(), _execute_scan()

### Community 64 - "billing/models.py"
Cohesion: 0.25
Nodes (6): PaymentInline, SaleAdmin, SaleItemInline, Payment, PaymentMethod, SaleItem

### Community 65 - "export_tenant_data_to_zip"
Cohesion: 0.09
Nodes (7): CleanupFile, export_tenant_data_to_zip(), generate_all_shops_export_archive(), generate_shop_export_archive(), export_all_shops_data(), export_shop_data(), _parse_date()

### Community 67 - "logger.ts"
Cohesion: 0.13
Nodes (7): ErrorBoundary, Props, State, logBuffer, LogEntry, logger, LogLevel

### Community 68 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, lint, preview, test:e2e, tunnel

### Community 69 - "pairing.py"
Cohesion: 0.18
Nodes (4): generate_pairing_qr_data_url(), get_lan_ip(), start_pairing_session(), _write_csv_to_zip()

### Community 72 - "pos_pairing_router.py"
Cohesion: 0.17
Nodes (10): revoke_pairing_session(), verify_mobile_token(), mobile_scan_fallback(), redeem_pos_pairing_token(), revoke_pos_pairing_token(), start_pos_pairing_session(), MobileScanIn, RedeemPairingIn (+2 more)

### Community 77 - "ShopRateSetting"
Cohesion: 0.17
Nodes (5): get_scraper(), list_available_sources(), sync_rates_from_source(), get_rate_sources(), sync_rates_from_web()

### Community 78 - "GoldRate"
Cohesion: 0.22
Nodes (3): fetch_live_market_rates_async(), sync_live_rates_async(), get_live_market_rates()

### Community 79 - "App.tsx"
Cohesion: 0.38
Nodes (10): App(), FeatureRoute(), ProtectedRoute(), Layout(), AuthProvider(), useAuth(), AccountingDashboard(), DeveloperPortal() (+2 more)

### Community 80 - "DayBook"
Cohesion: 0.19
Nodes (7): DayBook, Meta, _format_daybook(), get_today_day_book(), list_day_books(), record_petty_cash_entry(), update_day_book_cash()

### Community 81 - "services"
Cohesion: 0.14
Nodes (13): generateValue, key, sync, value, services, buildCommand, envVars, healthCheckPath (+5 more)

### Community 83 - "get"
Cohesion: 0.20
Nodes (5): get_current_rates(), get_customer(), get_rate_settings(), list_customers(), list_gold_rates_history()

### Community 84 - "StockSummary"
Cohesion: 0.12
Nodes (11): StockMovementAdmin, StockSummaryAdmin, StockMovement, Meta, MovementType, StockSummary, Meta, record_stock_movement() (+3 more)

### Community 85 - "Purity"
Cohesion: 0.13
Nodes (5): Customer, ShopRateSetting, Purity, Meta, register_store()

### Community 87 - "post"
Cohesion: 0.18
Nodes (6): close_day_book(), close_day_book_alias(), create_gold_rate(), _perform_close_day_book(), reopen_day_book(), reopen_day_book_alias()

### Community 88 - "POSPairingSession"
Cohesion: 0.29
Nodes (3): POSPairingSession, Meta, redeem_pairing_code()

### Community 92 - "GoldRate"
Cohesion: 0.25
Nodes (3): DayBookAdmin, GoldRate, Meta

### Community 93 - "ProductList.tsx"
Cohesion: 0.17
Nodes (17): CartItem, CameraCaptureModal(), CameraCaptureModalProps, ClubTrayModal(), ClubTrayModalProps, ProductFormModal(), ProductFormModalProps, SortField (+9 more)

### Community 94 - "react"
Cohesion: 0.25
Nodes (12): InvoiceSettingsModal(), InvoiceSettingsModalProps, CustomerDirectoryModal(), CustomerDirectoryModalProps, CustomerFormModal(), CustomerFormModalProps, CustomerSelectOrAddProps, ExportDataModal() (+4 more)

### Community 96 - "tenants/admin.py"
Cohesion: 0.33
Nodes (3): ClientAdmin, DomainAdmin, DomainInline

### Community 99 - "package.json"
Cohesion: 0.15
Nodes (12): html5-qrcode@^2.3.8, react-dom@^19.3.1, react-hook-form@^7.90.0, @zxing/browser@^0.2.1, name, private, type, version (+4 more)

### Community 102 - "MobileScannerPage.tsx"
Cohesion: 0.20
Nodes (12): beep(), isVideoReady(), makeReader(), MobileQRScanner(), startDecodeLoop(), MobileQRScannerProps, ScannerState, MobileScannerPage() (+4 more)

## Knowledge Gaps
- **1 isolated node(s):** `swarna-khata-book`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 608 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **46 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Branch` connect `User` to `products_router.py`, `MultiSourceGoldRateScraperTestCase`, `billing_router.py`, `tenants_router.py`, `billing/services.py`, `Client`, `NinjaPOSBillingTestCase`, `bills_router.py`, `auth_router.py`, `accounting_router.py`, `InvoiceSettingsTestCase`, `create_token`, `DayBookAccountingTestCase`, `Product`, `SecurityAuditAndAccessControlTestCase`, `Item`, `TrayQRTagsTestCase`, `DataExportTestCase`, `ShopRateSetting`, `get`, `Purity`, `OldGoldValidationTestCase`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `Client` (e.g. with `export_tenant_data_to_zip()` and `generate_all_shops_export_archive()`) actually correct?**
  _`Client` has 30 INFERRED edges - model-reasoned connections that need verification._
- **What connects `swarna-khata-book` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `products_router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08961593172119488 - nodes in this community are weakly interconnected._
- **Why does `Product` connect `Product` to `products_router.py`, `qr_tags_router.py`, `billing_router.py`, `tenants_router.py`, `Client`, `NinjaPOSBillingTestCase`, `InvoiceSettingsTestCase`, `create_token`, `SecurityAuditAndAccessControlTestCase`, `User`, `resolve_and_record_scan`, `export_tenant_data_to_zip`, `pairing.py`, `Item`, `TrayQRTagsTestCase`, `DataExportTestCase`, `StockSummary`, `Purity`, `OldGoldValidationTestCase`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `User` (e.g. with `export_tenant_data_to_zip()` and `create_token()`) actually correct?**
  _`User` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Should `django_db` be split into smaller, more focused modules?**
  _Cohesion score 0.07254623044096728 - nodes in this community are weakly interconnected._