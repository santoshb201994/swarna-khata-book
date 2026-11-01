# Graph Report - swarna_khata_book  (2026-11-01)

## Corpus Check
- 177 files · ~85,765 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .bat 3, .css 2)

## Summary
- 1395 nodes · 3234 edges · 97 communities (49 shown, 48 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 368 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `053191ab`
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
- ProductValidationTestCase
- devDependencies
- App.tsx
- NinjaPOSBillingTestCase
- bills_router.py
- auth_router.py
- NinjaAuthTestCase
- websocket_handler.py
- InvoiceSettingsTestCase
- vite.config.ts
- create_token
- render-build.sh
- DayBookAccountingTestCase
- Category
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
- POSPairingSession
- Item
- TrayQRTagsTestCase
- DataExportTestCase
- MobileScannerPage.tsx
- InvoiceSetting
- App.tsx
- DayBook
- services
- CustomUserAdmin
- metalRateHelper.ts
- StockSummary
- Purity
- accounting_router.py
- verify_mobile_token
- OldGoldValidationTestCase
- JWTAuth
- start.sh
- ProductList.tsx
- react
- tenants/admin.py
- middleware.py
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
- `export_tenant_data_to_zip()` --uses--> `GoldRate`  [INFERRED]
  backend/apps/tenants/export_service.py → backend/apps/accounting/models.py
- `create_gold_rate()` --uses--> `GoldRate`  [INFERRED]
  backend/ninja_api/routers/accounting_router.py → backend/apps/accounting/models.py
- `list_gold_rates_history()` --uses--> `GoldRate`  [INFERRED]
  backend/ninja_api/routers/accounting_router.py → backend/apps/accounting/models.py
- `DayBookAccountingTestCase` --uses--> `GoldRate`  [INFERRED]
  backend/tests/test_daybook_accounting.py → backend/apps/accounting/models.py
- `MultiSourceGoldRateScraperTestCase` --uses--> `GoldRate`  [INFERRED]
  backend/tests/test_multi_source_scraper.py → backend/apps/accounting/models.py

## Import Cycles
- None detected.

## Communities (97 total, 48 thin omitted)

### Community 0 - "products_router.py"
Cohesion: 0.11
Nodes (19): _threaded_qr(), generate_qr_for_product(), require_role(), create_category(), create_product(), create_purity(), delete_product(), _format_product() (+11 more)

### Community 1 - "django_db"
Cohesion: 0.07
Nodes (15): Migration, Migration, Migration, Migration, Migration, Migration, Migration, Migration (+7 more)

### Community 2 - "MultiSourceGoldRateScraperTestCase"
Cohesion: 0.07
Nodes (8): BaseRateScraper, RateScrapeResult, BullionDeskScraper, IBJAScraper, KSJFScraper, get_scraper(), list_available_sources(), MultiSourceGoldRateScraperTestCase

### Community 3 - "qr_tags_router.py"
Cohesion: 0.08
Nodes (22): QRTag, Meta, Tray, Meta, generate_qr_batch_async(), generate_qr_for_tray(), batch_generate_tags(), create_tray() (+14 more)

### Community 4 - "billing_router.py"
Cohesion: 0.13
Nodes (14): Sale, Meta, PaymentStatus, SaleStatus, _next_invoice_number(), add_sale_payment(), create_sale_invoice(), download_invoice_pdf() (+6 more)

### Community 5 - "tenants_router.py"
Cohesion: 0.13
Nodes (12): Client, Meta, create_tenant(), developer_login(), developer_overview(), developer_reset_user_password(), developer_switch_store_token(), developer_toggle_user_status() (+4 more)

### Community 6 - "billing/services.py"
Cohesion: 0.15
Nodes (5): Item, Meta, Status, generate_invoice_pdf(), generate_invoice_pdf_async()

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
Nodes (50): AddPaymentIn, BatchQRIn, BillCreateResponse, BillDetailResponse, BranchOut, CategoryOut, CloseDayIn, CreateTrayIn (+42 more)

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
Cohesion: 0.20
Nodes (19): api, RateSource, InvoiceModal(), InvoiceModalProps, PosScannerConnectionModal(), PosScannerConnectionModalProps, CartItem, POSScreen() (+11 more)

### Community 40 - "dependencies"
Cohesion: 0.10
Nodes (27): dependencies, @hookform/resolvers@^6.0.0, html5-qrcode@^2.3.8, lucide-react@^1.61.0, qrcode@^1.5.4, react@^19.3.1, react-dom@^19.3.1, react-hook-form@^7.90.0 (+19 more)

### Community 44 - "devDependencies"
Cohesion: 0.17
Nodes (12): devDependencies, oxlint@^1.88.0, @playwright/test@^1.64.1, @types/node@^24.19.2, @types/react@^19.3.0, @types/react-dom@^19.3.0, typescript@~6.0.3, oxlint (+4 more)

### Community 45 - "App.tsx"
Cohesion: 0.14
Nodes (20): PasswordPolicyChecklist(), PasswordPolicyChecklistProps, Login(), OverviewData, StoreUser, TenantItem, StaffManagementModal(), StaffManagementModalProps (+12 more)

### Community 48 - "bills_router.py"
Cohesion: 0.07
Nodes (8): Bill, Meta, Status, IdempotencyRecord, Meta, generate_bill_token(), create_bill(), BackendAuthoritativePollingTestCase

### Community 49 - "auth_router.py"
Cohesion: 0.08
Nodes (20): decode_token(), change_own_password(), create_branch(), create_user(), get_branch(), get_current_user(), list_branches(), list_users() (+12 more)

### Community 51 - "websocket_handler.py"
Cohesion: 0.18
Nodes (7): get_active_session(), mobile_websocket_app(), parse_query_string(), pos_websocket_app(), send_json(), validate_jwt_user(), application()

### Community 53 - "vite.config.ts"
Cohesion: 0.20
Nodes (8): @tailwindcss/vite@^4.3.3, vite@^8.3.4, @vitejs/plugin-basic-ssl@^2.3.0, @vitejs/plugin-react@^6.1.2, @tailwindcss/vite, vite, @vitejs/plugin-basic-ssl, @vitejs/plugin-react

### Community 54 - "create_token"
Cohesion: 0.11
Nodes (3): create_token(), DeveloperPortalTestCase, StoreOnboardingAndRBACTestCase

### Community 57 - "Category"
Cohesion: 0.11
Nodes (4): Category, Meta, NinjaProductsStockTestCase, TenantIsolationTestCase

### Community 58 - "bills_router.py"
Cohesion: 0.18
Nodes (6): not_found_handler(), permission_error_handler(), value_error_handler(), get_bill_cart(), scan_item_into_bill(), ScanItemIn

### Community 59 - "Product"
Cohesion: 0.14
Nodes (5): resolve_and_record_scan(), ProductFilter, Meta, Product, Meta

### Community 62 - "User"
Cohesion: 0.20
Nodes (7): Customer, Branch, Meta, User, Role, DomainInline, Domain

### Community 64 - "billing/models.py"
Cohesion: 0.24
Nodes (6): PaymentInline, SaleAdmin, SaleItemInline, Payment, PaymentMethod, SaleItem

### Community 65 - "export_tenant_data_to_zip"
Cohesion: 0.08
Nodes (8): CleanupFile, export_tenant_data_to_zip(), generate_all_shops_export_archive(), generate_shop_export_archive(), _write_csv_to_zip(), export_all_shops_data(), export_shop_data(), _parse_date()

### Community 67 - "logger.ts"
Cohesion: 0.13
Nodes (7): ErrorBoundary, Props, State, logBuffer, LogEntry, logger, LogLevel

### Community 68 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, lint, preview, test:e2e, tunnel

### Community 69 - "pairing.py"
Cohesion: 0.27
Nodes (3): generate_pairing_qr_data_url(), get_lan_ip(), start_pairing_session()

### Community 72 - "POSPairingSession"
Cohesion: 0.13
Nodes (7): POSPairingSession, Meta, redeem_pairing_code(), revoke_pairing_session(), redeem_pos_pairing_token(), revoke_pos_pairing_token(), start_pos_pairing_session()

### Community 77 - "MobileScannerPage.tsx"
Cohesion: 0.33
Nodes (7): axios@^1.20.0, MobileScannerPage(), ScannedHistoryItem, getApiBaseUrl(), getWsBaseUrl(), axios, react-router-dom

### Community 78 - "InvoiceSetting"
Cohesion: 0.25
Nodes (4): InvoiceSetting, PaperSize, TemplateStyle, update_invoice_settings()

### Community 79 - "App.tsx"
Cohesion: 0.28
Nodes (12): App(), FeatureRoute(), ProtectedRoute(), Layout(), AuthContext, AuthContextType, AuthProvider(), useAuth() (+4 more)

### Community 80 - "DayBook"
Cohesion: 0.15
Nodes (4): DayBookAdmin, DayBook, Meta, ProductAdmin

### Community 81 - "services"
Cohesion: 0.14
Nodes (13): generateValue, key, sync, value, services, buildCommand, envVars, healthCheckPath (+5 more)

### Community 83 - "metalRateHelper.ts"
Cohesion: 0.43
Nodes (6): clean(), detectProductMetal(), MetalType, ResolvedMetalRate, resolveProductRate(), GoldRate

### Community 84 - "StockSummary"
Cohesion: 0.12
Nodes (12): StockMovementAdmin, StockSummaryAdmin, StockMovement, Meta, MovementType, StockSummary, Meta, record_stock_movement() (+4 more)

### Community 85 - "Purity"
Cohesion: 0.11
Nodes (9): GoldRate, Meta, ShopRateSetting, fetch_live_market_rates_async(), sync_live_rates_async(), sync_rates_from_source(), Purity, Meta (+1 more)

### Community 87 - "accounting_router.py"
Cohesion: 0.07
Nodes (27): close_day_book(), close_day_book_alias(), create_customer(), create_gold_rate(), _format_daybook(), get_customer(), get_live_market_rates(), get_rate_settings() (+19 more)

### Community 88 - "verify_mobile_token"
Cohesion: 0.33
Nodes (3): verify_mobile_token(), mobile_scan_fallback(), _execute_scan()

### Community 93 - "ProductList.tsx"
Cohesion: 0.17
Nodes (20): CameraCaptureModal(), CameraCaptureModalProps, ClubTrayModal(), ClubTrayModalProps, ProductFormModal(), ProductFormModalProps, ProductList(), SortField (+12 more)

### Community 94 - "react"
Cohesion: 0.36
Nodes (6): InvoiceSettingsModal(), InvoiceSettingsModalProps, ExportDataModal(), ExportDataModalProps, InvoiceSetting, react

### Community 102 - "MobileScannerPage.tsx"
Cohesion: 0.19
Nodes (11): @zxing/browser@^0.2.1, @zxing/library@^0.23.0, beep(), isVideoReady(), makeReader(), MobileQRScanner(), startDecodeLoop(), MobileQRScannerProps (+3 more)

## Knowledge Gaps
- **1 isolated node(s):** `swarna-khata-book`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 610 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **48 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Branch` connect `User` to `products_router.py`, `MultiSourceGoldRateScraperTestCase`, `billing_router.py`, `tenants_router.py`, `ProductValidationTestCase`, `NinjaPOSBillingTestCase`, `bills_router.py`, `auth_router.py`, `NinjaAuthTestCase`, `InvoiceSettingsTestCase`, `create_token`, `DayBookAccountingTestCase`, `Category`, `Product`, `SecurityAuditAndAccessControlTestCase`, `Item`, `TrayQRTagsTestCase`, `DataExportTestCase`, `InvoiceSetting`, `DayBook`, `Purity`, `accounting_router.py`, `OldGoldValidationTestCase`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `Client` (e.g. with `export_tenant_data_to_zip()` and `generate_all_shops_export_archive()`) actually correct?**
  _`Client` has 30 INFERRED edges - model-reasoned connections that need verification._
- **What connects `swarna-khata-book` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `products_router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1051693404634581 - nodes in this community are weakly interconnected._
- **Why does `Product` connect `Product` to `products_router.py`, `qr_tags_router.py`, `billing_router.py`, `tenants_router.py`, `ProductValidationTestCase`, `NinjaPOSBillingTestCase`, `InvoiceSettingsTestCase`, `create_token`, `Category`, `SecurityAuditAndAccessControlTestCase`, `User`, `export_tenant_data_to_zip`, `pairing.py`, `Item`, `TrayQRTagsTestCase`, `DataExportTestCase`, `DayBook`, `StockSummary`, `OldGoldValidationTestCase`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `User` (e.g. with `export_tenant_data_to_zip()` and `create_token()`) actually correct?**
  _`User` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Should `django_db` be split into smaller, more focused modules?**
  _Cohesion score 0.07254623044096728 - nodes in this community are weakly interconnected._