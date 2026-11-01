# Graph Report - swarna_khata_book  (2026-11-02)

## Corpus Check
- 193 files · ~94,795 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .bat 3, .css 2)

## Summary
- 1548 nodes · 3652 edges · 112 communities (54 shown, 58 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 422 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5f67f906`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- products_router.py
- api.py
- MultiSourceGoldRateScraperTestCase
- qr_tags_router.py
- NinjaPOSBillingTestCase
- tenants_router.py
- InvoiceSettingsTestCase
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
- django_db
- tenants/admin.py
- package.json
- StockSummary
- POSSessionHub
- package.json
- pos_pairing_router.py
- backup_service.py
- bills_router.py
- auth_router.py
- Product
- websocket_handler.py
- create_sale
- UUID
- create_token
- render-build.sh
- DayBookAccountingTestCase
- MultiSourceGoldRateScraperTestCase
- logging
- UnifiedQRArchitectureTestCase
- SecurityAuditAndAccessControlTestCase
- User
- billing_router.py
- export_tenant_data_to_zip
- NinjaAuthTestCase
- logger.ts
- scripts
- verify-before-complete.md
- jewellery_erp_coding_workflow_mindmap.md
- Sale
- django_contrib
- DeveloperPortal.tsx
- DataExportTestCase
- @playwright/test
- TrayQRTagsTestCase
- DeveloperPortalTestCase
- CanaryBatchMigrator
- services
- download_invoice_pdf
- pairing.py
- Payment
- billing/services.py
- qrPayload.ts
- accounting_router.py
- vercel.json
- ShopRateSetting
- InvoiceSetting
- start.sh
- JWTAuth
- lucide-react
- App.tsx
- GoldRate
- vite.config.ts
- resolve_and_record_scan
- metalRateHelper.ts
- CustomUserAdmin
- _get_encryption_key
- MobileScannerPage.tsx
- verify_mobile_token
- POSPairingSession
- react-dom
- Purity
- POSScreen.tsx
- Client

## God Nodes (most connected - your core abstractions)
1. `Client` - 78 edges
2. `User` - 69 edges
3. `create_token()` - 67 edges
4. `Branch` - 65 edges
5. `Product` - 65 edges
6. `Purity` - 54 edges
7. `Domain` - 47 edges
8. `Category` - 43 edges
9. `require_role()` - 42 edges
10. `StockSummary` - 31 edges

## Surprising Connections (you probably didn't know these)
- `DomainInline` --uses--> `Domain`  [INFERRED]
  backend/apps/tenants/admin.py → backend/apps/tenants/models.py
- `TenantBackupService` --uses--> `GoldRate`  [INFERRED]
  backend/apps/tenants/backup_service.py → backend/apps/accounting/models.py
- `export_tenant_data_to_zip()` --uses--> `GoldRate`  [INFERRED]
  backend/apps/tenants/export_service.py → backend/apps/accounting/models.py
- `create_gold_rate()` --uses--> `GoldRate`  [INFERRED]
  backend/ninja_api/routers/accounting_router.py → backend/apps/accounting/models.py
- `get_current_rates()` --uses--> `GoldRate`  [INFERRED]
  backend/ninja_api/routers/accounting_router.py → backend/apps/accounting/models.py

## Import Cycles
- None detected.

## Communities (112 total, 58 thin omitted)

### Community 0 - "products_router.py"
Cohesion: 0.10
Nodes (19): _threaded_qr(), generate_qr_for_product(), require_role(), create_category(), create_product(), create_purity(), delete_product(), _format_product() (+11 more)

### Community 1 - "api.py"
Cohesion: 0.38
Nodes (3): not_found_handler(), permission_error_handler(), value_error_handler()

### Community 2 - "MultiSourceGoldRateScraperTestCase"
Cohesion: 0.15
Nodes (6): BaseRateScraper, RateScrapeResult, BullionDeskScraper, IBJAScraper, get_scraper(), list_available_sources()

### Community 3 - "qr_tags_router.py"
Cohesion: 0.08
Nodes (22): QRTag, Meta, Tray, Meta, generate_qr_batch_async(), generate_qr_for_tray(), batch_generate_tags(), create_tray() (+14 more)

### Community 5 - "tenants_router.py"
Cohesion: 0.12
Nodes (11): generate_schema_name(), create_tenant(), developer_login(), developer_reset_user_password(), developer_switch_store_token(), developer_toggle_user_status(), _format_tenant(), list_tenants() (+3 more)

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
Nodes (44): BatchQRIn, BillCreateResponse, BillDetailResponse, CashEntryIn, CategoryOut, CloseDayIn, CreateTrayIn, CustomerOut (+36 more)

### Community 12 - "validate_password_policy"
Cohesion: 0.11
Nodes (3): JewelleryPasswordPolicyValidator, validate_password_policy(), PasswordPolicyTestCase

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

### Community 37 - "django_db"
Cohesion: 0.07
Nodes (16): Migration, Migration, Migration, Migration, Migration, Migration, Migration, Migration (+8 more)

### Community 38 - "tenants/admin.py"
Cohesion: 0.33
Nodes (3): ClientAdmin, DomainAdmin, DomainInline

### Community 39 - "package.json"
Cohesion: 0.09
Nodes (22): dependencies, axios@^1.20.0, @hookform/resolvers@^6.0.0, html5-qrcode@^2.3.8, lucide-react@^1.61.0, qrcode@^1.5.4, react@^19.3.1, react-hook-form@^7.90.0 (+14 more)

### Community 40 - "StockSummary"
Cohesion: 0.14
Nodes (10): StockMovement, Meta, MovementType, StockSummary, Meta, record_stock_movement(), cancel_sale(), create_stock_movement() (+2 more)

### Community 44 - "package.json"
Cohesion: 0.14
Nodes (18): devDependencies, oxlint@^1.88.0, @playwright/test@^1.64.1, @types/node@^24.19.2, @types/react@^19.3.0, @types/react-dom@^19.3.0, typescript@~6.0.3, @vitejs/plugin-basic-ssl@^2.3.0 (+10 more)

### Community 45 - "pos_pairing_router.py"
Cohesion: 0.19
Nodes (5): redeem_pairing_code(), revoke_pairing_session(), redeem_pos_pairing_token(), revoke_pos_pairing_token(), start_pos_pairing_session()

### Community 48 - "bills_router.py"
Cohesion: 0.06
Nodes (13): Bill, Meta, Status, IdempotencyRecord, Meta, Item, Meta, Status (+5 more)

### Community 49 - "auth_router.py"
Cohesion: 0.07
Nodes (23): decode_token(), change_own_password(), create_branch(), create_user(), get_branch(), get_current_user(), list_branches(), list_users() (+15 more)

### Community 50 - "Product"
Cohesion: 0.22
Nodes (5): ProductFilter, Meta, Product, Meta, developer_overview()

### Community 51 - "websocket_handler.py"
Cohesion: 0.18
Nodes (7): get_active_session(), mobile_websocket_app(), parse_query_string(), pos_websocket_app(), send_json(), validate_jwt_user(), application()

### Community 53 - "UUID"
Cohesion: 0.15
Nodes (4): Migration, Migration, Migration, RequestLoggingMiddleware

### Community 58 - "logging"
Cohesion: 0.10
Nodes (5): ProductionTenantMiddleware, TenantContextMismatchError, TenantResolutionError, TenantResolver, TenantSuspendedOrInactiveError

### Community 62 - "User"
Cohesion: 0.23
Nodes (5): Branch, Meta, User, Role, Domain

### Community 64 - "billing_router.py"
Cohesion: 0.11
Nodes (16): add_sale_payment(), get_item_by_qr(), _resolve_item_by_token(), update_invoice_settings(), verify_physical_tag(), AddPaymentIn, InvoiceSettingOut, InvoiceSettingUpdateIn (+8 more)

### Community 65 - "export_tenant_data_to_zip"
Cohesion: 0.06
Nodes (9): CleanupFile, export_tenant_data_to_zip(), generate_all_shops_export_archive(), generate_shop_export_archive(), _write_csv_to_zip(), health_check(), export_all_shops_data(), export_shop_data() (+1 more)

### Community 67 - "logger.ts"
Cohesion: 0.13
Nodes (7): ErrorBoundary, Props, State, logBuffer, LogEntry, logger, LogLevel

### Community 68 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, lint, preview, test:e2e, tunnel

### Community 72 - "Sale"
Cohesion: 0.21
Nodes (8): Sale, Meta, PaymentStatus, SaleStatus, _next_invoice_number(), create_sale_invoice(), _format_sale(), get_sale()

### Community 74 - "django_contrib"
Cohesion: 0.29
Nodes (3): DayBookAdmin, StockMovementAdmin, StockSummaryAdmin

### Community 75 - "DeveloperPortal.tsx"
Cohesion: 0.13
Nodes (21): PasswordPolicyChecklist(), PasswordPolicyChecklistProps, Login(), DeveloperPortal(), OverviewData, StoreUser, TenantItem, StaffManagementModal() (+13 more)

### Community 81 - "services"
Cohesion: 0.14
Nodes (13): generateValue, key, sync, value, services, autoDeployTrigger, buildCommand, envVars (+5 more)

### Community 82 - "download_invoice_pdf"
Cohesion: 0.25
Nodes (4): download_invoice_pdf(), download_invoice_pdf_underscore(), get_invoice_settings(), list_sales()

### Community 83 - "pairing.py"
Cohesion: 0.31
Nodes (3): generate_pairing_qr_data_url(), get_lan_ip(), start_pairing_session()

### Community 84 - "Payment"
Cohesion: 0.24
Nodes (6): PaymentInline, SaleAdmin, SaleItemInline, Payment, PaymentMethod, SaleItem

### Community 86 - "qrPayload.ts"
Cohesion: 0.16
Nodes (21): CartItem, BulkQRPrintModal(), BulkQRPrintModalProps, TagItemWithQR, ClubTrayModal(), ClubTrayModalProps, SortField, QRTagModal() (+13 more)

### Community 87 - "accounting_router.py"
Cohesion: 0.10
Nodes (18): DayBook, Meta, close_day_book(), close_day_book_alias(), create_customer(), create_gold_rate(), _format_daybook(), get_today_day_book() (+10 more)

### Community 89 - "ShopRateSetting"
Cohesion: 0.12
Nodes (8): ShopRateSetting, get_current_rates(), get_customer(), get_live_market_rates(), get_rate_settings(), get_rate_sources(), list_customers(), list_gold_rates_history()

### Community 90 - "InvoiceSetting"
Cohesion: 0.25
Nodes (4): InvoiceSetting, PaperSize, TemplateStyle, reset_demo_invoice_settings()

### Community 94 - "lucide-react"
Cohesion: 0.36
Nodes (7): CameraCaptureModal(), CameraCaptureModalProps, ProductFormModal(), ProductFormModalProps, Category, Purity, lucide-react

### Community 95 - "App.tsx"
Cohesion: 0.17
Nodes (20): App(), FeatureRoute(), ProtectedRoute(), Layout(), AuthContext, AuthContextType, AuthProvider(), useAuth() (+12 more)

### Community 96 - "GoldRate"
Cohesion: 0.16
Nodes (5): GoldRate, Meta, fetch_live_market_rates_async(), sync_live_rates_async(), sync_rates_from_source()

### Community 97 - "vite.config.ts"
Cohesion: 0.25
Nodes (6): @tailwindcss/vite@^4.3.3, vite@^8.3.4, @vitejs/plugin-react@^6.1.2, @tailwindcss/vite, vite, @vitejs/plugin-react

### Community 98 - "resolve_and_record_scan"
Cohesion: 0.33
Nodes (3): ScannedItemAudit, Meta, resolve_and_record_scan()

### Community 99 - "metalRateHelper.ts"
Cohesion: 0.53
Nodes (5): clean(), detectProductMetal(), MetalType, ResolvedMetalRate, resolveProductRate()

### Community 102 - "MobileScannerPage.tsx"
Cohesion: 0.19
Nodes (11): @zxing/browser@^0.2.1, @zxing/library@^0.23.0, beep(), isVideoReady(), makeReader(), MobileQRScanner(), startDecodeLoop(), MobileQRScannerProps (+3 more)

### Community 103 - "verify_mobile_token"
Cohesion: 0.33
Nodes (3): verify_mobile_token(), mobile_scan_fallback(), _execute_scan()

### Community 110 - "Purity"
Cohesion: 0.08
Nodes (11): Customer, ProductAdmin, Category, Meta, Purity, Meta, TenantBackupService, TenantRestoreService (+3 more)

### Community 111 - "POSScreen.tsx"
Cohesion: 0.14
Nodes (28): api, RateSource, InvoiceModal(), InvoiceModalProps, InvoiceSettingsModalProps, PosScannerConnectionModal(), PosScannerConnectionModalProps, POSScreen() (+20 more)

### Community 113 - "Client"
Cohesion: 0.05
Nodes (8): Client, Meta, ProvisioningStatus, NinjaProductsStockTestCase, CustomerEmailValidationTestCase, OldGoldValidationTestCase, ProductValidationTestCase, TenantIsolationTestCase

## Knowledge Gaps
- **1 isolated node(s):** `swarna-khata-book`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 682 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **58 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Branch` connect `User` to `products_router.py`, `NinjaPOSBillingTestCase`, `tenants_router.py`, `InvoiceSettingsTestCase`, `backup_service.py`, `bills_router.py`, `auth_router.py`, `Product`, `create_sale`, `create_token`, `DayBookAccountingTestCase`, `MultiSourceGoldRateScraperTestCase`, `UnifiedQRArchitectureTestCase`, `SecurityAuditAndAccessControlTestCase`, `billing_router.py`, `NinjaAuthTestCase`, `Sale`, `DataExportTestCase`, `TrayQRTagsTestCase`, `DeveloperPortalTestCase`, `download_invoice_pdf`, `accounting_router.py`, `ShopRateSetting`, `InvoiceSetting`, `GoldRate`, `test_mobile_scanner.py`, `Purity`, `Client`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `Client` (e.g. with `export_tenant_data_to_zip()` and `generate_all_shops_export_archive()`) actually correct?**
  _`Client` has 32 INFERRED edges - model-reasoned connections that need verification._
- **What connects `swarna-khata-book` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `products_router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `User` connect `User` to `products_router.py`, `NinjaPOSBillingTestCase`, `tenants_router.py`, `InvoiceSettingsTestCase`, `backup_service.py`, `bills_router.py`, `auth_router.py`, `Product`, `create_sale`, `create_token`, `DayBookAccountingTestCase`, `MultiSourceGoldRateScraperTestCase`, `logging`, `UnifiedQRArchitectureTestCase`, `SecurityAuditAndAccessControlTestCase`, `export_tenant_data_to_zip`, `NinjaAuthTestCase`, `DataExportTestCase`, `TrayQRTagsTestCase`, `DeveloperPortalTestCase`, `.provision_store`, `JWTAuth`, `test_mobile_scanner.py`, `Purity`, `Client`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `User` (e.g. with `TenantBackupService` and `export_tenant_data_to_zip()`) actually correct?**
  _`User` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Should `qr_tags_router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07692307692307693 - nodes in this community are weakly interconnected._