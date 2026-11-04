# Graph Report - swarna_khata_book  (2026-11-04)

## Corpus Check
- 201 files · ~100,368 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .bat 3, .css 2)

## Summary
- 1650 nodes · 3884 edges · 108 communities (51 shown, 57 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 450 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fccf6428`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- products_router.py
- backup_service.py
- DecimalJsonEncoder
- qr_tags_router.py
- NinjaPOSBillingTestCase
- ProductValidationTestCase
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
- ProductionHardeningArchitectureTestCase
- react
- dependencies
- bills_router.py
- StockSummary
- devDependencies
- GoldRate
- base.py
- bills_router.py
- auth_router.py
- JWTAuth
- websocket_handler.py
- CanaryBatchMigrator
- django_db_models_deletion
- NinjaAuthTestCase
- render-build.sh
- DayBookAccountingTestCase
- NinjaProductsStockTestCase
- index.ts
- UnifiedQRArchitectureTestCase
- SecurityAuditAndAccessControlTestCase
- Branch
- BrevoPasswordResetIntegrationTestCase
- create_token
- RequestLoggingMiddleware
- TenantResolver
- logger.ts
- scripts
- GoldRate
- verify-before-complete.md
- jewellery_erp_coding_workflow_mindmap.md
- tenants_router.py
- logging
- metalRateHelper.ts
- DataExportTestCase
- django_db
- pos_pairing_router.py
- ConsoleEmailProvider
- services
- start_pairing_session
- update_invoice_settings
- vercel.json
- TenantProvisioningService
- billing_router.py
- start.sh
- package.json
- index.ts
- stock_router.py
- Product
- @playwright/test
- api.py
- MobileScannerPage.tsx
- vite.config.ts
- tenants/admin.py
- typing
- AuthContext.tsx
- POSScreen.tsx
- CustomUserAdmin
- ProductionTenantMiddleware
- PasswordResetToken
- @types/qrcode@^1.5.6

## God Nodes (most connected - your core abstractions)
1. `Client` - 81 edges
2. `User` - 73 edges
3. `create_token()` - 69 edges
4. `Branch` - 67 edges
5. `Product` - 65 edges
6. `Purity` - 54 edges
7. `Domain` - 49 edges
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
- `DayBookAccountingTestCase` --uses--> `GoldRate`  [INFERRED]
  backend/tests/test_daybook_accounting.py → backend/apps/accounting/models.py
- `MultiSourceGoldRateScraperTestCase` --uses--> `GoldRate`  [INFERRED]
  backend/tests/test_multi_source_scraper.py → backend/apps/accounting/models.py

## Import Cycles
- None detected.

## Communities (108 total, 57 thin omitted)

### Community 0 - "products_router.py"
Cohesion: 0.08
Nodes (24): _threaded_qr(), generate_qr_for_product(), require_role(), create_category(), create_product(), create_purity(), delete_product(), _format_product() (+16 more)

### Community 1 - "backup_service.py"
Cohesion: 0.07
Nodes (11): PaymentInline, SaleAdmin, SaleItemInline, Payment, PaymentMethod, SaleItem, TenantBackupService, export_tenant_data_to_zip() (+3 more)

### Community 3 - "qr_tags_router.py"
Cohesion: 0.08
Nodes (22): QRTag, Meta, Tray, Meta, generate_qr_batch_async(), generate_qr_for_tray(), batch_generate_tags(), create_tray() (+14 more)

### Community 5 - "ProductValidationTestCase"
Cohesion: 0.06
Nodes (3): CustomerEmailValidationTestCase, OldGoldValidationTestCase, ProductValidationTestCase

### Community 7 - "backend"
Cohesion: 0.06
Nodes (34): build, command, depends_on, env_file, ports, volumes, context, dockerfile (+26 more)

### Community 8 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+11 more)

### Community 9 - "django_apps"
Cohesion: 0.08
Nodes (8): AccountingConfig, AccountsConfig, BillingConfig, EmailsConfig, ProductsConfig, QrTagsConfig, StockConfig, TenantsConfig

### Community 10 - "compilerOptions"
Cohesion: 0.12
Nodes (16): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+8 more)

### Community 11 - "schemas.py"
Cohesion: 0.10
Nodes (36): AddPaymentIn, BatchQRIn, CashEntryIn, CloseDayIn, CreateTrayIn, CustomerIn, CustomerOut, DayBookOut (+28 more)

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

### Community 38 - "react"
Cohesion: 0.11
Nodes (35): App(), FeatureRoute(), ProtectedRoute(), Layout(), PasswordPolicyChecklist(), PasswordPolicyChecklistProps, AuthProvider(), useAuth() (+27 more)

### Community 39 - "dependencies"
Cohesion: 0.11
Nodes (19): dependencies, axios@^1.20.0, @hookform/resolvers@^6.0.0, lucide-react@^1.61.0, qrcode@^1.5.4, react@^19.3.1, react-hot-toast@^2.6.1, react-router-dom@^7.18.4 (+11 more)

### Community 40 - "bills_router.py"
Cohesion: 0.14
Nodes (11): Bill, Meta, Status, create_bill(), get_bill_cart(), scan_item_into_bill(), BillCreateResponse, BillDetailResponse (+3 more)

### Community 43 - "StockSummary"
Cohesion: 0.06
Nodes (15): InvoiceSetting, PaperSize, TemplateStyle, create_sale(), generate_invoice_pdf(), generate_invoice_pdf_async(), StockMovementAdmin, StockSummaryAdmin (+7 more)

### Community 44 - "devDependencies"
Cohesion: 0.17
Nodes (12): devDependencies, oxlint@^1.88.0, @playwright/test@^1.64.1, @types/node@^24.19.2, @types/react@^19.3.0, @types/react-dom@^19.3.0, typescript@~6.0.3, oxlint (+4 more)

### Community 46 - "base.py"
Cohesion: 0.15
Nodes (6): BaseRateScraper, RateScrapeResult, BullionDeskScraper, IBJAScraper, get_scraper(), list_available_sources()

### Community 48 - "bills_router.py"
Cohesion: 0.09
Nodes (4): IdempotencyRecord, Meta, generate_bill_token(), BackendAuthoritativePollingTestCase

### Community 49 - "auth_router.py"
Cohesion: 0.06
Nodes (27): decode_token(), change_own_password(), complete_password_reset(), create_branch(), create_user(), get_branch(), get_current_user(), list_branches() (+19 more)

### Community 51 - "websocket_handler.py"
Cohesion: 0.05
Nodes (14): POSPairingSession, Meta, resolve_and_record_scan(), get_active_session(), mobile_websocket_app(), _sync_resolve(), parse_query_string(), pos_websocket_app() (+6 more)

### Community 53 - "django_db_models_deletion"
Cohesion: 0.08
Nodes (10): Migration, Migration, Migration, Migration, Migration, Migration, Migration, Migration (+2 more)

### Community 58 - "index.ts"
Cohesion: 0.18
Nodes (15): InvoiceSettingsModalProps, CustomerDirectoryModalProps, CustomerFormModal(), CustomerFormModalProps, CustomerSelectOrAdd(), CustomerSelectOrAddProps, Branch, Customer (+7 more)

### Community 62 - "Branch"
Cohesion: 0.17
Nodes (12): Customer, Branch, Meta, User, Role, Category, Meta, Purity (+4 more)

### Community 64 - "create_token"
Cohesion: 0.11
Nodes (3): create_token(), DeveloperPortalTestCase, StoreOnboardingAndRBACTestCase

### Community 67 - "logger.ts"
Cohesion: 0.12
Nodes (7): ErrorBoundary, Props, State, logBuffer, LogEntry, logger, LogLevel

### Community 68 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, lint, preview, test:e2e, tunnel

### Community 69 - "GoldRate"
Cohesion: 0.05
Nodes (28): GoldRate, Meta, ShopRateSetting, fetch_live_market_rates_async(), sync_live_rates_async(), sync_rates_from_source(), close_day_book(), close_day_book_alias() (+20 more)

### Community 72 - "tenants_router.py"
Cohesion: 0.10
Nodes (15): Client, Meta, ProvisioningStatus, generate_schema_name(), create_tenant(), developer_login(), developer_overview(), developer_reset_user_password() (+7 more)

### Community 74 - "logging"
Cohesion: 0.24
Nodes (3): TenantContextMismatchError, TenantResolutionError, TenantSuspendedOrInactiveError

### Community 75 - "metalRateHelper.ts"
Cohesion: 0.53
Nodes (5): clean(), detectProductMetal(), MetalType, ResolvedMetalRate, resolveProductRate()

### Community 77 - "django_db"
Cohesion: 0.07
Nodes (13): Migration, Migration, Migration, Migration, Migration, Migration, Migration, Migration (+5 more)

### Community 78 - "pos_pairing_router.py"
Cohesion: 0.13
Nodes (13): redeem_pairing_code(), revoke_pairing_session(), verify_mobile_token(), mobile_scan_fallback(), redeem_pos_pairing_token(), revoke_pos_pairing_token(), start_pos_pairing_session(), MobileScanIn (+5 more)

### Community 79 - "ConsoleEmailProvider"
Cohesion: 0.18
Nodes (3): BaseEmailProvider, ConsoleEmailProvider, get_email_provider()

### Community 81 - "services"
Cohesion: 0.14
Nodes (13): generateValue, key, sync, value, services, autoDeployTrigger, buildCommand, envVars (+5 more)

### Community 82 - "start_pairing_session"
Cohesion: 0.12
Nodes (4): generate_pairing_qr_data_url(), get_lan_ip(), start_pairing_session(), _get_encryption_key()

### Community 89 - "TenantProvisioningService"
Cohesion: 0.21
Nodes (3): TenantProvisioningService, _execute_pipeline(), get_store_provisioning_status()

### Community 90 - "billing_router.py"
Cohesion: 0.08
Nodes (23): DayBook, Meta, Item, Meta, Status, Sale, Meta, PaymentStatus (+15 more)

### Community 92 - "package.json"
Cohesion: 0.15
Nodes (12): html5-qrcode@^2.3.8, react-dom@^19.3.1, react-hook-form@^7.90.0, @zxing/browser@^0.2.1, name, private, type, version (+4 more)

### Community 94 - "index.ts"
Cohesion: 0.13
Nodes (28): CartItem, CameraCaptureModal(), CameraCaptureModalProps, BulkQRPrintModal(), BulkQRPrintModalProps, TagItemWithQR, ClubTrayModal(), ClubTrayModalProps (+20 more)

### Community 95 - "stock_router.py"
Cohesion: 0.16
Nodes (6): create_stock_movement(), list_stock_movements(), list_stock_summary(), StockMovementIn, StockMovementOut, StockSummaryOut

### Community 97 - "Product"
Cohesion: 0.09
Nodes (7): DayBookAdmin, ProductAdmin, ProductFilter, Meta, Product, Meta, TenantIsolationTestCase

### Community 101 - "api.py"
Cohesion: 0.10
Nodes (8): CleanupFile, health_check(), not_found_handler(), permission_error_handler(), value_error_handler(), export_all_shops_data(), export_shop_data(), _parse_date()

### Community 102 - "MobileScannerPage.tsx"
Cohesion: 0.23
Nodes (10): beep(), isVideoReady(), makeReader(), MobileQRScanner(), startDecodeLoop(), MobileQRScannerProps, ScannerState, MobileScannerPage() (+2 more)

### Community 105 - "vite.config.ts"
Cohesion: 0.20
Nodes (8): @tailwindcss/vite@^4.3.3, vite@^8.3.4, @vitejs/plugin-basic-ssl@^2.3.0, @vitejs/plugin-react@^6.1.2, @tailwindcss/vite, vite, @vitejs/plugin-basic-ssl, @vitejs/plugin-react

### Community 106 - "tenants/admin.py"
Cohesion: 0.33
Nodes (3): ClientAdmin, DomainAdmin, DomainInline

### Community 110 - "AuthContext.tsx"
Cohesion: 0.67
Nodes (3): AuthContext, AuthContextType, User

### Community 111 - "POSScreen.tsx"
Cohesion: 0.26
Nodes (13): api, AccountingDashboard(), RateSource, InvoiceModal(), InvoiceModalProps, PosScannerConnectionModal(), PosScannerConnectionModalProps, POSScreen() (+5 more)

### Community 118 - "PasswordResetToken"
Cohesion: 0.14
Nodes (6): EmailService, PasswordResetToken, Meta, _find_user_by_email(), request_password_reset(), ForgotPasswordIn

## Knowledge Gaps
- **1 isolated node(s):** `swarna-khata-book`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 725 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **57 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `Branch` to `products_router.py`, `backup_service.py`, `NinjaPOSBillingTestCase`, `ProductValidationTestCase`, `InvoiceSettingsTestCase`, `ProductionHardeningArchitectureTestCase`, `StockSummary`, `GoldRate`, `bills_router.py`, `auth_router.py`, `JWTAuth`, `websocket_handler.py`, `NinjaAuthTestCase`, `DayBookAccountingTestCase`, `NinjaProductsStockTestCase`, `UnifiedQRArchitectureTestCase`, `SecurityAuditAndAccessControlTestCase`, `BrevoPasswordResetIntegrationTestCase`, `create_token`, `TenantResolver`, `tenants_router.py`, `DataExportTestCase`, `django_db`, `TenantProvisioningService`, `Product`, `PasswordResetToken`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Are the 34 inferred relationships involving `Client` (e.g. with `export_tenant_data_to_zip()` and `generate_all_shops_export_archive()`) actually correct?**
  _`Client` has 34 INFERRED edges - model-reasoned connections that need verification._
- **What connects `swarna-khata-book` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `products_router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07926829268292683 - nodes in this community are weakly interconnected._
- **Why does `Branch` connect `Branch` to `products_router.py`, `backup_service.py`, `NinjaPOSBillingTestCase`, `ProductValidationTestCase`, `InvoiceSettingsTestCase`, `ProductionHardeningArchitectureTestCase`, `StockSummary`, `GoldRate`, `bills_router.py`, `auth_router.py`, `websocket_handler.py`, `NinjaAuthTestCase`, `DayBookAccountingTestCase`, `NinjaProductsStockTestCase`, `UnifiedQRArchitectureTestCase`, `SecurityAuditAndAccessControlTestCase`, `BrevoPasswordResetIntegrationTestCase`, `create_token`, `GoldRate`, `tenants_router.py`, `DataExportTestCase`, `django_db`, `update_invoice_settings`, `TenantProvisioningService`, `billing_router.py`, `Product`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Are the 38 inferred relationships involving `User` (e.g. with `TenantBackupService` and `export_tenant_data_to_zip()`) actually correct?**
  _`User` has 38 INFERRED edges - model-reasoned connections that need verification._
- **Should `backup_service.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07198228128460686 - nodes in this community are weakly interconnected._