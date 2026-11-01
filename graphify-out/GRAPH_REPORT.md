# Graph Report - swarna_khata_book  (2026-11-01)

## Corpus Check
- 178 files · ~86,053 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .bat 3, .css 2)

## Summary
- 1399 nodes · 3235 edges · 100 communities (49 shown, 51 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 368 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8d47616c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- products_router.py
- urls.py
- RateScrapeResult
- qr_tags_router.py
- billing_router.py
- tenants_router.py
- NinjaAuthTestCase
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
- stock/admin.py
- POSSessionHub
- POSScreen.tsx
- dependencies
- OldGoldValidationTestCase
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
- Product
- bills_router.py
- StockSummary
- SecurityAuditAndAccessControlTestCase
- User
- ProductValidationTestCase
- billing/models.py
- export_tenant_data_to_zip
- @playwright/test
- logger.ts
- scripts
- ShopRateSetting
- verify-before-complete.md
- jewellery_erp_coding_workflow_mindmap.md
- MultiSourceGoldRateScraperTestCase
- billing/services.py
- TrayQRTagsTestCase
- DataExportTestCase
- django_db
- django_db_models_deletion
- App.tsx
- KSJFScraper
- services
- CustomUserAdmin
- sync_live_rates_async
- django_conf
- registry.py
- MobileScannerPage.tsx
- metalRateHelper.ts
- vercel.json
- pos_pairing_router.py
- accounts/migrations/0001_initial.py
- start.sh
- DayBook
- ProductList.tsx
- react
- ClientAdmin
- RequestLoggingMiddleware
- middleware.py
- products/migrations/0001_initial.py
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

## Communities (100 total, 51 thin omitted)

### Community 0 - "products_router.py"
Cohesion: 0.10
Nodes (18): Item, Meta, Status, require_role(), create_category(), create_product(), create_purity(), delete_product() (+10 more)

### Community 2 - "RateScrapeResult"
Cohesion: 0.17
Nodes (4): BaseRateScraper, RateScrapeResult, BullionDeskScraper, IBJAScraper

### Community 3 - "qr_tags_router.py"
Cohesion: 0.07
Nodes (28): generate_pairing_qr_data_url(), QRTag, Meta, Tray, Meta, generate_qr_batch_async(), _threaded_qr(), generate_qr_for_product() (+20 more)

### Community 4 - "billing_router.py"
Cohesion: 0.13
Nodes (14): _next_invoice_number(), StockMovement, Meta, MovementType, record_stock_movement(), add_sale_payment(), cancel_sale(), create_sale_invoice() (+6 more)

### Community 5 - "tenants_router.py"
Cohesion: 0.14
Nodes (13): create_tenant(), developer_login(), developer_reset_user_password(), developer_switch_store_token(), developer_toggle_user_status(), _format_tenant(), list_tenants(), toggle_tenant_status() (+5 more)

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
Cohesion: 0.08
Nodes (44): BillCreateResponse, BillDetailResponse, BranchOut, CategoryIn, CategoryOut, CloseDayIn, CustomerOut, DayBookOut (+36 more)

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
Cohesion: 0.27
Nodes (12): api, RateSource, InvoiceModal(), InvoiceModalProps, InvoiceSettingsModalProps, PosScannerConnectionModal(), PosScannerConnectionModalProps, POSScreen() (+4 more)

### Community 40 - "dependencies"
Cohesion: 0.10
Nodes (26): dependencies, @hookform/resolvers@^6.0.0, html5-qrcode@^2.3.8, lucide-react@^1.61.0, qrcode@^1.5.4, react@^19.3.1, react-dom@^19.3.1, react-hook-form@^7.90.0 (+18 more)

### Community 44 - "devDependencies"
Cohesion: 0.17
Nodes (12): devDependencies, oxlint@^1.88.0, @playwright/test@^1.64.1, @types/node@^24.19.2, @types/react@^19.3.0, @types/react-dom@^19.3.0, typescript@~6.0.3, oxlint (+4 more)

### Community 45 - "App.tsx"
Cohesion: 0.14
Nodes (20): PasswordPolicyChecklist(), PasswordPolicyChecklistProps, Login(), OverviewData, StoreUser, TenantItem, StaffManagementModal(), StaffManagementModalProps (+12 more)

### Community 48 - "bills_router.py"
Cohesion: 0.05
Nodes (11): Bill, Meta, Status, IdempotencyRecord, Meta, BillJWTAuth, decode_token(), generate_bill_token() (+3 more)

### Community 49 - "auth_router.py"
Cohesion: 0.09
Nodes (16): change_own_password(), create_branch(), create_user(), get_branch(), get_current_user(), list_branches(), list_users(), obtain_token() (+8 more)

### Community 50 - "accounting_router.py"
Cohesion: 0.09
Nodes (20): close_day_book(), close_day_book_alias(), create_customer(), create_gold_rate(), _format_daybook(), get_today_day_book(), list_day_books(), _perform_close_day_book() (+12 more)

### Community 51 - "websocket_handler.py"
Cohesion: 0.06
Nodes (15): POSPairingSession, Meta, get_lan_ip(), redeem_pairing_code(), start_pairing_session(), verify_mobile_token(), get_active_session(), mobile_websocket_app() (+7 more)

### Community 53 - "vite.config.ts"
Cohesion: 0.20
Nodes (8): @tailwindcss/vite@^4.3.3, vite@^8.3.4, @vitejs/plugin-basic-ssl@^2.3.0, @vitejs/plugin-react@^6.1.2, @tailwindcss/vite, vite, @vitejs/plugin-basic-ssl, @vitejs/plugin-react

### Community 54 - "create_token"
Cohesion: 0.11
Nodes (3): create_token(), DeveloperPortalTestCase, StoreOnboardingAndRBACTestCase

### Community 57 - "Product"
Cohesion: 0.09
Nodes (10): ScannedItemAudit, Meta, resolve_and_record_scan(), ProductFilter, Meta, Product, Meta, StockSummary (+2 more)

### Community 58 - "bills_router.py"
Cohesion: 0.11
Nodes (8): not_found_handler(), permission_error_handler(), value_error_handler(), get_bill_cart(), scan_item_into_bill(), create_stock_movement(), list_stock_movements(), list_stock_summary()

### Community 59 - "StockSummary"
Cohesion: 0.08
Nodes (8): Category, Meta, Client, Meta, register_store(), InvoiceSnapshotImmutabilityTestCase, NinjaProductsStockTestCase, TenantIsolationTestCase

### Community 62 - "User"
Cohesion: 0.16
Nodes (11): Customer, GoldRate, Meta, Branch, Meta, User, Role, Purity (+3 more)

### Community 64 - "billing/models.py"
Cohesion: 0.24
Nodes (6): PaymentInline, SaleAdmin, SaleItemInline, Payment, PaymentMethod, SaleItem

### Community 65 - "export_tenant_data_to_zip"
Cohesion: 0.07
Nodes (8): CleanupFile, export_tenant_data_to_zip(), generate_all_shops_export_archive(), generate_shop_export_archive(), _write_csv_to_zip(), export_all_shops_data(), export_shop_data(), _parse_date()

### Community 67 - "logger.ts"
Cohesion: 0.13
Nodes (7): ErrorBoundary, Props, State, logBuffer, LogEntry, logger, LogLevel

### Community 68 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, lint, preview, test:e2e, tunnel

### Community 69 - "ShopRateSetting"
Cohesion: 0.17
Nodes (6): ShopRateSetting, get_customer(), get_rate_settings(), get_rate_sources(), list_customers(), list_gold_rates_history()

### Community 74 - "billing/services.py"
Cohesion: 0.06
Nodes (14): InvoiceSetting, PaperSize, TemplateStyle, Sale, Meta, PaymentStatus, SaleStatus, create_sale() (+6 more)

### Community 77 - "django_db"
Cohesion: 0.18
Nodes (5): Migration, Migration, Migration, Migration, Migration

### Community 78 - "django_db_models_deletion"
Cohesion: 0.20
Nodes (4): Migration, Migration, Migration, Migration

### Community 79 - "App.tsx"
Cohesion: 0.18
Nodes (19): react-router-dom@^7.18.4, App(), FeatureRoute(), ProtectedRoute(), Layout(), AuthContext, AuthContextType, AuthProvider() (+11 more)

### Community 81 - "services"
Cohesion: 0.14
Nodes (13): generateValue, key, sync, value, services, autoDeployTrigger, buildCommand, envVars (+5 more)

### Community 83 - "sync_live_rates_async"
Cohesion: 0.22
Nodes (3): fetch_live_market_rates_async(), sync_live_rates_async(), get_live_market_rates()

### Community 84 - "django_conf"
Cohesion: 0.22
Nodes (4): Migration, Migration, Migration, Migration

### Community 85 - "registry.py"
Cohesion: 0.28
Nodes (3): get_scraper(), list_available_sources(), sync_rates_from_source()

### Community 86 - "MobileScannerPage.tsx"
Cohesion: 0.39
Nodes (6): axios@^1.20.0, MobileScannerPage(), ScannedHistoryItem, getApiBaseUrl(), getWsBaseUrl(), axios

### Community 87 - "metalRateHelper.ts"
Cohesion: 0.53
Nodes (5): clean(), detectProductMetal(), MetalType, ResolvedMetalRate, resolveProductRate()

### Community 89 - "pos_pairing_router.py"
Cohesion: 0.19
Nodes (7): revoke_pairing_session(), redeem_pos_pairing_token(), revoke_pos_pairing_token(), start_pos_pairing_session(), RedeemPairingIn, RevokePairingIn, StartPairingIn

### Community 92 - "DayBook"
Cohesion: 0.12
Nodes (5): DayBookAdmin, DayBook, Meta, ProductAdmin, DomainInline

### Community 93 - "ProductList.tsx"
Cohesion: 0.15
Nodes (22): CartItem, CameraCaptureModal(), CameraCaptureModalProps, ClubTrayModal(), ClubTrayModalProps, ProductFormModal(), ProductFormModalProps, SortField (+14 more)

### Community 94 - "react"
Cohesion: 0.42
Nodes (7): CustomerDirectoryModalProps, CustomerFormModal(), CustomerFormModalProps, CustomerSelectOrAdd(), CustomerSelectOrAddProps, Customer, react

### Community 102 - "MobileScannerPage.tsx"
Cohesion: 0.19
Nodes (11): @zxing/browser@^0.2.1, @zxing/library@^0.23.0, beep(), isVideoReady(), makeReader(), MobileQRScanner(), startDecodeLoop(), MobileQRScannerProps (+3 more)

## Knowledge Gaps
- **1 isolated node(s):** `swarna-khata-book`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 613 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **51 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Branch` connect `User` to `products_router.py`, `billing_router.py`, `tenants_router.py`, `NinjaAuthTestCase`, `OldGoldValidationTestCase`, `NinjaPOSBillingTestCase`, `bills_router.py`, `auth_router.py`, `accounting_router.py`, `InvoiceSettingsTestCase`, `create_token`, `DayBookAccountingTestCase`, `Product`, `StockSummary`, `SecurityAuditAndAccessControlTestCase`, `ProductValidationTestCase`, `MultiSourceGoldRateScraperTestCase`, `billing/services.py`, `TrayQRTagsTestCase`, `DataExportTestCase`, `registry.py`, `DayBook`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `Client` (e.g. with `export_tenant_data_to_zip()` and `generate_all_shops_export_archive()`) actually correct?**
  _`Client` has 30 INFERRED edges - model-reasoned connections that need verification._
- **What connects `swarna-khata-book` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `products_router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10416666666666667 - nodes in this community are weakly interconnected._
- **Why does `Client` connect `StockSummary` to `tenants_router.py`, `NinjaAuthTestCase`, `validate_password_policy`, `OldGoldValidationTestCase`, `NinjaPOSBillingTestCase`, `bills_router.py`, `auth_router.py`, `InvoiceSettingsTestCase`, `create_token`, `DayBookAccountingTestCase`, `Product`, `SecurityAuditAndAccessControlTestCase`, `User`, `ProductValidationTestCase`, `export_tenant_data_to_zip`, `MultiSourceGoldRateScraperTestCase`, `TrayQRTagsTestCase`, `DataExportTestCase`, `DayBook`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `User` (e.g. with `export_tenant_data_to_zip()` and `create_token()`) actually correct?**
  _`User` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Should `qr_tags_router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06504494976203067 - nodes in this community are weakly interconnected._