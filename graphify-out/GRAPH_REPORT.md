# Graph Report - swarna_khata_book  (2026-11-04)

## Corpus Check
- 201 files · ~101,378 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .bat 3, .css 2)

## Summary
- 1663 nodes · 3930 edges · 107 communities (50 shown, 57 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 465 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fb152c45`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- products_router.py
- Product
- OldGoldValidationTestCase
- qr_tags_router.py
- Client
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
- Layout.tsx
- package.json
- billing/models.py
- billing_router.py
- list_users
- react
- base.py
- bills_router.py
- auth_router.py
- create_token
- websocket_handler.py
- typing
- tenants/admin.py
- NinjaAuthTestCase
- render-build.sh
- DayBookAccountingTestCase
- POSSessionHub
- DataExportTestCase
- UnifiedQRArchitectureTestCase
- SecurityAuditAndAccessControlTestCase
- Branch
- BrevoEmailProvider
- StockSummary
- .provision_store
- resolve_and_record_scan
- logger.ts
- scripts
- base.py
- verify-before-complete.md
- jewellery_erp_coding_workflow_mindmap.md
- tenants_router.py
- TrayQRTagsTestCase
- accounting_router.py
- pairing.py
- _format_tray
- pos_pairing_router.py
- metalRateHelper.ts
- CanaryBatchMigrator
- services
- resolve_and_record_scan
- DeveloperPortalTestCase
- bills_router.py
- MobileScannerPage.tsx
- vercel.json
- ConsoleEmailProvider
- start.sh
- QRTagModal.tsx
- resolver.py
- backup_service.py
- stock_router.py
- generate_qr_for_product
- django_db_models_deletion
- export_tenant_data_to_zip
- urls.py
- NinjaPOSBillingTestCase
- Tray
- index.ts
- CustomUserAdmin
- InvoiceSetting
- delete_tray

## God Nodes (most connected - your core abstractions)
1. `Client` - 86 edges
2. `User` - 77 edges
3. `create_token()` - 71 edges
4. `Branch` - 68 edges
5. `Product` - 66 edges
6. `Purity` - 55 edges
7. `Domain` - 51 edges
8. `Category` - 44 edges
9. `require_role()` - 43 edges
10. `StockSummary` - 31 edges

## Surprising Connections (you probably didn't know these)
- `DomainInline` --uses--> `Domain`  [INFERRED]
  backend/apps/tenants/admin.py → backend/apps/tenants/models.py
- `sync_live_rates_async()` --uses--> `GoldRate`  [INFERRED]
  backend/apps/accounting/services.py → backend/apps/accounting/models.py
- `sync_rates_from_source()` --uses--> `GoldRate`  [INFERRED]
  backend/apps/accounting/services.py → backend/apps/accounting/models.py
- `TenantBackupService` --uses--> `GoldRate`  [INFERRED]
  backend/apps/tenants/backup_service.py → backend/apps/accounting/models.py
- `create_gold_rate()` --uses--> `GoldRate`  [INFERRED]
  backend/ninja_api/routers/accounting_router.py → backend/apps/accounting/models.py

## Import Cycles
- None detected.

## Communities (107 total, 57 thin omitted)

### Community 0 - "products_router.py"
Cohesion: 0.11
Nodes (15): Item, Meta, Status, create_category(), create_product(), create_purity(), delete_product(), _format_product() (+7 more)

### Community 1 - "Product"
Cohesion: 0.22
Nodes (5): ProductFilter, Meta, Product, Meta, developer_overview()

### Community 3 - "qr_tags_router.py"
Cohesion: 0.17
Nodes (11): QRTag, Meta, batch_generate_tags(), create_tray(), _format_qrtag(), _generate_tray_code(), get_qr_tag(), list_qr_tags() (+3 more)

### Community 4 - "Client"
Cohesion: 0.09
Nodes (6): Client, Meta, ProvisioningStatus, InvoiceSnapshotImmutabilityTestCase, NinjaProductsStockTestCase, TenantIsolationTestCase

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
Cohesion: 0.08
Nodes (47): AddPaymentIn, BatchQRIn, CashEntryIn, CategoryIn, CategoryOut, CloseDayIn, CreateTrayIn, CustomerOut (+39 more)

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
Cohesion: 0.09
Nodes (6): Purity, Meta, TenantRestoreService, TenantProvisioningService, require_branch_access(), ProductionHardeningArchitectureTestCase

### Community 38 - "Layout.tsx"
Cohesion: 0.13
Nodes (27): App(), FeatureRoute(), ProtectedRoute(), Layout(), AuthContext, AuthContextType, AuthProvider(), useAuth() (+19 more)

### Community 39 - "package.json"
Cohesion: 0.04
Nodes (55): dependencies, axios@^1.20.0, @hookform/resolvers@^6.0.0, html5-qrcode@^2.3.8, lucide-react@^1.61.0, qrcode@^1.5.4, react@^19.3.1, react-dom@^19.3.1 (+47 more)

### Community 40 - "billing/models.py"
Cohesion: 0.21
Nodes (7): PaymentInline, SaleAdmin, SaleItemInline, Payment, PaymentMethod, SaleItem, TenantBackupService

### Community 43 - "billing_router.py"
Cohesion: 0.06
Nodes (25): Sale, Meta, PaymentStatus, SaleStatus, create_sale(), generate_invoice_pdf(), generate_invoice_pdf_async(), _next_invoice_number() (+17 more)

### Community 44 - "list_users"
Cohesion: 0.22
Nodes (4): get_branch(), get_current_user(), list_branches(), list_users()

### Community 45 - "react"
Cohesion: 0.23
Nodes (13): PasswordPolicyChecklist(), PasswordPolicyChecklistProps, Login(), ResetPasswordPage(), DeveloperPortal(), OverviewData, StoreUser, TenantItem (+5 more)

### Community 48 - "bills_router.py"
Cohesion: 0.07
Nodes (5): BillJWTAuth, decode_token(), generate_bill_token(), JWTAuth, BackendAuthoritativePollingTestCase

### Community 49 - "auth_router.py"
Cohesion: 0.06
Nodes (25): EmailService, PasswordResetToken, Meta, change_own_password(), complete_password_reset(), create_branch(), create_user(), _find_user_by_email() (+17 more)

### Community 51 - "websocket_handler.py"
Cohesion: 0.16
Nodes (8): get_active_session(), mobile_websocket_app(), _sync_resolve(), parse_query_string(), pos_websocket_app(), send_json(), validate_jwt_user(), application()

### Community 53 - "tenants/admin.py"
Cohesion: 0.13
Nodes (5): DayBookAdmin, ProductAdmin, ClientAdmin, DomainAdmin, DomainInline

### Community 62 - "Branch"
Cohesion: 0.19
Nodes (9): Customer, Branch, Meta, User, Role, Category, Meta, Domain (+1 more)

### Community 64 - "StockSummary"
Cohesion: 0.29
Nodes (4): StockMovementAdmin, StockSummaryAdmin, StockSummary, Meta

### Community 67 - "logger.ts"
Cohesion: 0.13
Nodes (7): ErrorBoundary, Props, State, logBuffer, LogEntry, logger, LogLevel

### Community 68 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, lint, preview, test:e2e, tunnel

### Community 69 - "base.py"
Cohesion: 0.15
Nodes (6): BaseRateScraper, RateScrapeResult, BullionDeskScraper, IBJAScraper, get_scraper(), list_available_sources()

### Community 72 - "tenants_router.py"
Cohesion: 0.08
Nodes (21): check_global_username_uniqueness(), generate_schema_name(), require_role(), reset_staff_password(), create_tenant(), developer_delete_tenant(), developer_login(), developer_reset_user_password() (+13 more)

### Community 75 - "accounting_router.py"
Cohesion: 0.05
Nodes (29): DayBook, Meta, ShopRateSetting, fetch_live_market_rates_async(), sync_live_rates_async(), sync_rates_from_source(), close_day_book(), close_day_book_alias() (+21 more)

### Community 76 - "pairing.py"
Cohesion: 0.23
Nodes (4): generate_pairing_qr_data_url(), get_lan_ip(), start_pairing_session(), verify_mobile_token()

### Community 77 - "_format_tray"
Cohesion: 0.29
Nodes (4): _format_tray(), get_tray(), get_tray_by_code(), list_trays()

### Community 78 - "pos_pairing_router.py"
Cohesion: 0.19
Nodes (6): revoke_pairing_session(), mobile_scan_fallback(), _execute_scan(), redeem_pos_pairing_token(), revoke_pos_pairing_token(), start_pos_pairing_session()

### Community 79 - "metalRateHelper.ts"
Cohesion: 0.43
Nodes (6): clean(), detectProductMetal(), MetalType, ResolvedMetalRate, resolveProductRate(), GoldRate

### Community 81 - "services"
Cohesion: 0.14
Nodes (13): generateValue, key, sync, value, services, autoDeployTrigger, buildCommand, envVars (+5 more)

### Community 82 - "resolve_and_record_scan"
Cohesion: 0.18
Nodes (5): POSPairingSession, Meta, ScannedItemAudit, Meta, redeem_pairing_code()

### Community 86 - "bills_router.py"
Cohesion: 0.12
Nodes (13): Bill, Meta, Status, IdempotencyRecord, Meta, create_bill(), get_bill_cart(), scan_item_into_bill() (+5 more)

### Community 87 - "MobileScannerPage.tsx"
Cohesion: 0.22
Nodes (11): beep(), isVideoReady(), makeReader(), MobileQRScanner(), startDecodeLoop(), MobileQRScannerProps, ScannerState, MobileScannerPage() (+3 more)

### Community 89 - "ConsoleEmailProvider"
Cohesion: 0.18
Nodes (3): BaseEmailProvider, ConsoleEmailProvider, get_email_provider()

### Community 94 - "QRTagModal.tsx"
Cohesion: 0.14
Nodes (25): CartItem, CameraCaptureModal(), CameraCaptureModalProps, BulkQRPrintModal(), BulkQRPrintModalProps, TagItemWithQR, ClubTrayModal(), ProductFormModal() (+17 more)

### Community 96 - "resolver.py"
Cohesion: 0.09
Nodes (5): ProductionTenantMiddleware, TenantContextMismatchError, TenantResolutionError, TenantResolver, TenantSuspendedOrInactiveError

### Community 101 - "stock_router.py"
Cohesion: 0.13
Nodes (9): not_found_handler(), permission_error_handler(), value_error_handler(), create_stock_movement(), list_stock_movements(), list_stock_summary(), StockMovementIn, StockMovementOut (+1 more)

### Community 102 - "generate_qr_for_product"
Cohesion: 0.22
Nodes (4): generate_qr_batch_async(), _threaded_qr(), generate_qr_for_product(), regenerate_product_qr()

### Community 104 - "django_db_models_deletion"
Cohesion: 0.05
Nodes (21): Migration, Migration, Migration, Migration, Migration, Migration, Migration, Migration (+13 more)

### Community 105 - "export_tenant_data_to_zip"
Cohesion: 0.07
Nodes (10): GoldRate, Meta, CleanupFile, export_tenant_data_to_zip(), generate_all_shops_export_archive(), generate_shop_export_archive(), _write_csv_to_zip(), export_all_shops_data() (+2 more)

### Community 110 - "Tray"
Cohesion: 0.14
Nodes (5): Tray, Meta, generate_qr_for_tray(), regenerate_tray_tag(), update_tray()

### Community 111 - "index.ts"
Cohesion: 0.15
Nodes (26): api, InvoiceModalProps, InvoiceSettingsModalProps, PosScannerConnectionModal(), PosScannerConnectionModalProps, CustomerDirectoryModalProps, CustomerFormModal(), CustomerFormModalProps (+18 more)

### Community 117 - "InvoiceSetting"
Cohesion: 0.25
Nodes (4): InvoiceSetting, PaperSize, TemplateStyle, update_invoice_settings()

## Knowledge Gaps
- **1 isolated node(s):** `swarna-khata-book`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 732 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **57 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `Branch` to `Product`, `OldGoldValidationTestCase`, `Client`, `ProductValidationTestCase`, `InvoiceSettingsTestCase`, `validate_password_policy`, `ProductionHardeningArchitectureTestCase`, `billing/models.py`, `list_users`, `base.py`, `bills_router.py`, `auth_router.py`, `create_token`, `tenants/admin.py`, `NinjaAuthTestCase`, `DayBookAccountingTestCase`, `DataExportTestCase`, `UnifiedQRArchitectureTestCase`, `SecurityAuditAndAccessControlTestCase`, `BrevoEmailProvider`, `.provision_store`, `tenants_router.py`, `TrayQRTagsTestCase`, `resolve_and_record_scan`, `DeveloperPortalTestCase`, `resolver.py`, `backup_service.py`, `export_tenant_data_to_zip`, `NinjaPOSBillingTestCase`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Are the 36 inferred relationships involving `Client` (e.g. with `check_global_username_uniqueness()` and `export_tenant_data_to_zip()`) actually correct?**
  _`Client` has 36 INFERRED edges - model-reasoned connections that need verification._
- **What connects `swarna-khata-book` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `products_router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10846560846560846 - nodes in this community are weakly interconnected._
- **Why does `Branch` connect `Branch` to `products_router.py`, `Product`, `OldGoldValidationTestCase`, `Client`, `ProductValidationTestCase`, `InvoiceSettingsTestCase`, `ProductionHardeningArchitectureTestCase`, `billing/models.py`, `billing_router.py`, `list_users`, `base.py`, `bills_router.py`, `auth_router.py`, `create_token`, `tenants/admin.py`, `NinjaAuthTestCase`, `DayBookAccountingTestCase`, `DataExportTestCase`, `UnifiedQRArchitectureTestCase`, `SecurityAuditAndAccessControlTestCase`, `BrevoEmailProvider`, `tenants_router.py`, `TrayQRTagsTestCase`, `accounting_router.py`, `resolve_and_record_scan`, `DeveloperPortalTestCase`, `backup_service.py`, `export_tenant_data_to_zip`, `NinjaPOSBillingTestCase`, `InvoiceSetting`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Are the 41 inferred relationships involving `User` (e.g. with `check_global_username_uniqueness()` and `TenantBackupService`) actually correct?**
  _`User` has 41 INFERRED edges - model-reasoned connections that need verification._
- **Should `OldGoldValidationTestCase` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._