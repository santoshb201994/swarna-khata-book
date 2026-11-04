# Graph Report - swarna_khata_book  (2026-11-04)

## Corpus Check
- 213 files · ~106,377 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .bat 3, .css 2)

## Summary
- 1722 nodes · 4120 edges · 104 communities (51 shown, 53 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 497 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7fb5e9b6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- products_router.py
- DeveloperPortalTestCase
- MultiSourceGoldRateScraperTestCase
- index.ts
- lucide-react
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
- BrevoPasswordResetIntegrationTestCase
- dependencies
- django_db
- tenants_router.py
- NinjaAuthTestCase
- App.tsx
- Category
- bills_router.py
- auth_router.py
- EndpointsAuthAndBranchesTestCase
- TrayQRTagsTestCase
- create_token
- StockSummary
- Client
- render-build.sh
- DayBookAccountingTestCase
- POSSessionHub
- DataExportTestCase
- UnifiedQRArchitectureTestCase
- SecurityAuditAndAccessControlTestCase
- Branch
- Product
- devDependencies
- TrayQRTagsTestCase
- react
- logger.ts
- scripts
- JWTAuth
- verify-before-complete.md
- jewellery_erp_coding_workflow_mindmap.md
- create_tenant
- export_tenant_data_to_zip
- accounting_router.py
- MobileScannerPage.tsx
- tenants/admin.py
- pos_pairing_router.py
- QRTagModal.tsx
- services
- typing
- EndpointsProductsQrAndStockTestCase
- MobileScannerPage.tsx
- vercel.json
- export_service.py
- start.sh
- qr_tags_router.py
- InvoiceSetting
- logging
- Command
- stock_router.py
- @playwright/test
- vite.config.ts
- EndpointsAccountingAndDaybookTestCase
- DecimalJsonEncoder
- CustomUserAdmin
- backup_service.py
- POSPairingSession
- billing_router.py

## God Nodes (most connected - your core abstractions)
1. `Client` - 95 edges
2. `User` - 89 edges
3. `create_token()` - 79 edges
4. `Branch` - 76 edges
5. `Product` - 70 edges
6. `Purity` - 61 edges
7. `Domain` - 59 edges
8. `Category` - 48 edges
9. `require_role()` - 43 edges
10. `StockSummary` - 32 edges

## Surprising Connections (you probably didn't know these)
- `DomainInline` --uses--> `Domain`  [INFERRED]
  backend/apps/tenants/admin.py → backend/apps/tenants/models.py
- `sync_live_rates_async()` --uses--> `GoldRate`  [INFERRED]
  backend/apps/accounting/services.py → backend/apps/accounting/models.py
- `sync_rates_from_source()` --uses--> `GoldRate`  [INFERRED]
  backend/apps/accounting/services.py → backend/apps/accounting/models.py
- `TenantBackupService` --uses--> `GoldRate`  [INFERRED]
  backend/apps/tenants/backup_service.py → backend/apps/accounting/models.py
- `export_tenant_data_to_zip()` --uses--> `GoldRate`  [INFERRED]
  backend/apps/tenants/export_service.py → backend/apps/accounting/models.py

## Import Cycles
- None detected.

## Communities (104 total, 53 thin omitted)

### Community 0 - "products_router.py"
Cohesion: 0.10
Nodes (18): generate_qr_for_product(), require_role(), create_category(), create_product(), create_purity(), delete_product(), _format_product(), get_product() (+10 more)

### Community 2 - "MultiSourceGoldRateScraperTestCase"
Cohesion: 0.07
Nodes (8): BaseRateScraper, RateScrapeResult, BullionDeskScraper, IBJAScraper, KSJFScraper, get_scraper(), list_available_sources(), MultiSourceGoldRateScraperTestCase

### Community 3 - "index.ts"
Cohesion: 0.15
Nodes (17): clean(), detectProductMetal(), MetalType, ResolvedMetalRate, resolveProductRate(), CameraCaptureModal(), CameraCaptureModalProps, ProductFormModalProps (+9 more)

### Community 4 - "lucide-react"
Cohesion: 0.18
Nodes (17): PasswordPolicyChecklist(), PasswordPolicyChecklistProps, ResetPasswordPage(), OverviewData, StoreUser, TenantItem, StaffManagementModal(), StaffManagementModalProps (+9 more)

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
Cohesion: 0.07
Nodes (51): BatchQRIn, BillCreateResponse, BillDetailResponse, BranchOut, CashEntryIn, CategoryOut, CloseDayIn, CreateTrayIn (+43 more)

### Community 12 - "validate_password_policy"
Cohesion: 0.10
Nodes (4): is_username_globally_available(), JewelleryPasswordPolicyValidator, validate_password_policy(), PasswordPolicyTestCase

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

### Community 37 - "ProductionHardeningArchitectureTestCase"
Cohesion: 0.10
Nodes (4): TenantRestoreService, CanaryBatchMigrator, require_branch_access(), ProductionHardeningArchitectureTestCase

### Community 38 - "BrevoPasswordResetIntegrationTestCase"
Cohesion: 0.07
Nodes (4): BrevoEmailProvider, ConsoleEmailProvider, EmailDeliveryError, BrevoPasswordResetIntegrationTestCase

### Community 39 - "dependencies"
Cohesion: 0.09
Nodes (23): dependencies, axios@^1.20.0, @hookform/resolvers@^6.0.0, html5-qrcode@^2.3.8, lucide-react@^1.61.0, qrcode@^1.5.4, react@^19.3.1, react-dom@^19.3.1 (+15 more)

### Community 40 - "django_db"
Cohesion: 0.05
Nodes (20): Migration, Migration, Migration, Migration, Migration, Migration, Migration, Migration (+12 more)

### Community 43 - "tenants_router.py"
Cohesion: 0.10
Nodes (9): check_global_username_uniqueness(), generate_schema_name(), TenantProvisioningService, _execute_pipeline(), developer_delete_tenant(), _format_tenant(), get_store_provisioning_status(), list_tenants() (+1 more)

### Community 45 - "App.tsx"
Cohesion: 0.15
Nodes (22): App(), FeatureRoute(), ProtectedRoute(), Layout(), AuthContext, AuthContextType, AuthProvider(), useAuth() (+14 more)

### Community 46 - "Category"
Cohesion: 0.13
Nodes (4): ProductAdmin, Category, Meta, TenantIsolationTestCase

### Community 48 - "bills_router.py"
Cohesion: 0.06
Nodes (9): Bill, Meta, Status, IdempotencyRecord, Meta, generate_bill_token(), create_bill(), get_bill_cart() (+1 more)

### Community 49 - "auth_router.py"
Cohesion: 0.06
Nodes (29): EmailService, PasswordResetToken, Meta, decode_token(), change_own_password(), complete_password_reset(), create_branch(), create_user() (+21 more)

### Community 51 - "TrayQRTagsTestCase"
Cohesion: 0.12
Nodes (10): resolve_and_record_scan(), get_active_session(), mobile_websocket_app(), _sync_resolve(), parse_query_string(), pos_websocket_app(), send_json(), validate_jwt_user() (+2 more)

### Community 53 - "StockSummary"
Cohesion: 0.19
Nodes (8): StockMovementAdmin, StockSummaryAdmin, StockMovement, Meta, MovementType, StockSummary, Meta, seed_demo_tenant()

### Community 54 - "Client"
Cohesion: 0.05
Nodes (6): Client, Meta, ProvisioningStatus, NinjaPOSBillingTestCase, NinjaProductsStockTestCase, OldGoldValidationTestCase

### Community 62 - "Branch"
Cohesion: 0.21
Nodes (7): Branch, Meta, User, Role, Purity, Meta, Domain

### Community 63 - "Product"
Cohesion: 0.09
Nodes (10): ScannedItemAudit, Meta, generate_pairing_qr_data_url(), _inner_resolve_and_record_scan(), ProductFilter, Meta, Product, Meta (+2 more)

### Community 64 - "devDependencies"
Cohesion: 0.13
Nodes (19): devDependencies, oxlint@^1.88.0, @playwright/test@^1.64.1, @types/node@^24.19.2, @types/react@^19.3.0, @types/react-dom@^19.3.0, typescript@~6.0.3, @vitejs/plugin-react@^6.1.2 (+11 more)

### Community 66 - "react"
Cohesion: 0.20
Nodes (19): api, RateSource, InvoiceModal(), InvoiceModalProps, InvoiceSettingsModalProps, PosScannerConnectionModal(), PosScannerConnectionModalProps, POSScreen() (+11 more)

### Community 67 - "logger.ts"
Cohesion: 0.13
Nodes (7): ErrorBoundary, Props, State, logBuffer, LogEntry, logger, LogLevel

### Community 68 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, preview, test:e2e, test:unit, tunnel

### Community 72 - "create_tenant"
Cohesion: 0.15
Nodes (6): create_tenant(), developer_login(), developer_reset_user_password(), developer_switch_store_token(), developer_toggle_user_status(), toggle_tenant_status()

### Community 74 - "export_tenant_data_to_zip"
Cohesion: 0.06
Nodes (8): CleanupFile, export_tenant_data_to_zip(), generate_all_shops_export_archive(), generate_shop_export_archive(), health_check(), export_all_shops_data(), export_shop_data(), _parse_date()

### Community 75 - "accounting_router.py"
Cohesion: 0.05
Nodes (27): ShopRateSetting, fetch_live_market_rates_async(), sync_live_rates_async(), sync_rates_from_source(), close_day_book(), close_day_book_alias(), create_customer(), create_gold_rate() (+19 more)

### Community 76 - "MobileScannerPage.tsx"
Cohesion: 0.39
Nodes (6): MobileScannerPage(), ScannedHistoryItem, getApiBaseUrl(), getWsBaseUrl(), axios, react-router-dom

### Community 77 - "tenants/admin.py"
Cohesion: 0.33
Nodes (3): ClientAdmin, DomainAdmin, DomainInline

### Community 78 - "pos_pairing_router.py"
Cohesion: 0.11
Nodes (14): revoke_pairing_session(), not_found_handler(), permission_error_handler(), value_error_handler(), scan_item_into_bill(), mobile_scan_fallback(), redeem_pos_pairing_token(), revoke_pos_pairing_token() (+6 more)

### Community 80 - "QRTagModal.tsx"
Cohesion: 0.14
Nodes (24): CartItem, BulkQRPrintModal(), BulkQRPrintModalProps, TagItemWithQR, ClubTrayModal(), ClubTrayModalProps, ProductFormModal(), ProductList() (+16 more)

### Community 81 - "services"
Cohesion: 0.14
Nodes (13): generateValue, key, sync, value, services, autoDeployTrigger, buildCommand, envVars (+5 more)

### Community 84 - "typing"
Cohesion: 0.10
Nodes (4): BaseEmailProvider, get_email_provider(), get_password_reset_email(), RequestLoggingMiddleware

### Community 87 - "MobileScannerPage.tsx"
Cohesion: 0.19
Nodes (11): @zxing/browser@^0.2.1, @zxing/library@^0.23.0, beep(), isVideoReady(), makeReader(), MobileQRScanner(), startDecodeLoop(), MobileQRScannerProps (+3 more)

### Community 89 - "export_service.py"
Cohesion: 0.14
Nodes (7): DayBookAdmin, Customer, DayBook, Meta, GoldRate, Meta, _write_csv_to_zip()

### Community 92 - "qr_tags_router.py"
Cohesion: 0.08
Nodes (23): QRTag, Meta, Tray, Meta, generate_qr_batch(), generate_qr_batch_async(), generate_qr_for_tray(), batch_generate_tags() (+15 more)

### Community 93 - "InvoiceSetting"
Cohesion: 0.12
Nodes (4): create_sale(), generate_invoice_pdf(), generate_invoice_pdf_async(), InvoiceSnapshotImmutabilityTestCase

### Community 96 - "logging"
Cohesion: 0.09
Nodes (6): verify_mobile_token(), ProductionTenantMiddleware, TenantContextMismatchError, TenantResolutionError, TenantResolver, TenantSuspendedOrInactiveError

### Community 100 - "stock_router.py"
Cohesion: 0.21
Nodes (5): record_stock_movement(), create_stock_movement(), list_stock_movements(), list_stock_summary(), StockMovementIn

### Community 106 - "vite.config.ts"
Cohesion: 0.22
Nodes (6): @tailwindcss/vite@^4.3.3, vite@^8.3.4, @vitejs/plugin-basic-ssl@^2.3.0, @tailwindcss/vite, vite, @vitejs/plugin-basic-ssl

### Community 115 - "backup_service.py"
Cohesion: 0.07
Nodes (18): PaymentInline, SaleAdmin, SaleItemInline, InvoiceSetting, PaperSize, TemplateStyle, Item, Meta (+10 more)

### Community 117 - "POSPairingSession"
Cohesion: 0.09
Nodes (5): POSPairingSession, Meta, get_lan_ip(), redeem_pairing_code(), start_pairing_session()

### Community 120 - "billing_router.py"
Cohesion: 0.09
Nodes (18): _next_invoice_number(), add_sale_payment(), cancel_sale(), create_sale_invoice(), download_invoice_pdf(), download_invoice_pdf_underscore(), _format_sale(), get_invoice_settings() (+10 more)

## Knowledge Gaps
- **1 isolated node(s):** `swarna-khata-book`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 770 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **53 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `Branch` to `products_router.py`, `DeveloperPortalTestCase`, `MultiSourceGoldRateScraperTestCase`, `ProductValidationTestCase`, `InvoiceSettingsTestCase`, `validate_password_policy`, `ProductionHardeningArchitectureTestCase`, `BrevoPasswordResetIntegrationTestCase`, `tenants_router.py`, `NinjaAuthTestCase`, `Category`, `bills_router.py`, `auth_router.py`, `EndpointsAuthAndBranchesTestCase`, `create_token`, `StockSummary`, `Client`, `DayBookAccountingTestCase`, `DataExportTestCase`, `UnifiedQRArchitectureTestCase`, `SecurityAuditAndAccessControlTestCase`, `Product`, `TrayQRTagsTestCase`, `JWTAuth`, `create_tenant`, `export_tenant_data_to_zip`, `accounting_router.py`, `EndpointsProductsQrAndStockTestCase`, `export_service.py`, `InvoiceSetting`, `logging`, `stock_router.py`, `EndpointsAccountingAndDaybookTestCase`, `backup_service.py`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Are the 40 inferred relationships involving `Client` (e.g. with `check_global_username_uniqueness()` and `export_tenant_data_to_zip()`) actually correct?**
  _`Client` has 40 INFERRED edges - model-reasoned connections that need verification._
- **What connects `swarna-khata-book` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `products_router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09915966386554621 - nodes in this community are weakly interconnected._
- **Why does `Client` connect `Client` to `DeveloperPortalTestCase`, `MultiSourceGoldRateScraperTestCase`, `ProductValidationTestCase`, `InvoiceSettingsTestCase`, `validate_password_policy`, `ProductionHardeningArchitectureTestCase`, `BrevoPasswordResetIntegrationTestCase`, `tenants_router.py`, `NinjaAuthTestCase`, `Category`, `bills_router.py`, `auth_router.py`, `EndpointsAuthAndBranchesTestCase`, `create_token`, `StockSummary`, `DayBookAccountingTestCase`, `DataExportTestCase`, `UnifiedQRArchitectureTestCase`, `SecurityAuditAndAccessControlTestCase`, `Branch`, `Product`, `TrayQRTagsTestCase`, `create_tenant`, `export_tenant_data_to_zip`, `tenants/admin.py`, `EndpointsProductsQrAndStockTestCase`, `export_service.py`, `InvoiceSetting`, `EndpointsAccountingAndDaybookTestCase`, `backup_service.py`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Are the 47 inferred relationships involving `User` (e.g. with `sync_rates_from_source()` and `check_global_username_uniqueness()`) actually correct?**
  _`User` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Should `DeveloperPortalTestCase` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._