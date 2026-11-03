# Graph Report - swarna_khata_book  (2026-11-03)

## Corpus Check
- 201 files · ~99,986 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .bat 3, .css 2)

## Summary
- 1645 nodes · 3873 edges · 116 communities (59 shown, 57 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 447 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `926de6e7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- products_router.py
- export_tenant_data_to_zip
- DecimalJsonEncoder
- qr_tags_router.py
- NinjaPOSBillingTestCase
- Client
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
- UUID
- react
- dependencies
- MultiSourceGoldRateScraperTestCase
- billing/services.py
- @playwright/test
- MultiSourceGoldRateScraperTestCase
- POSSessionHub
- bills_router.py
- auth_router.py
- websocket_handler.py
- Tray
- StockSummary
- create_token
- render-build.sh
- DayBookAccountingTestCase
- lucide-react
- TrayQRTagsTestCase
- UnifiedQRArchitectureTestCase
- SecurityAuditAndAccessControlTestCase
- User
- BrevoEmailProvider
- Purity
- Payment
- package.json
- logger.ts
- scripts
- accounting_router.py
- verify-before-complete.md
- jewellery_erp_coding_workflow_mindmap.md
- tenants_router.py
- resolver.py
- metalRateHelper.ts
- DataExportTestCase
- django_db_models_deletion
- pairing.py
- BrevoPasswordResetIntegrationTestCase
- CanaryBatchMigrator
- services
- pairing.py
- InvoiceSetting
- list_users
- Layout.tsx
- vercel.json
- QRTagModal.tsx
- Sale
- start.sh
- download_invoice_pdf
- ProductionHardeningArchitectureTestCase
- index.ts
- billing/services.py
- GoldRate
- Product
- export_router.py
- get
- _get_encryption_key
- urls.py
- MobileScannerPage.tsx
- @playwright/test
- JWTAuth
- Item
- django_contrib
- provider.py
- NinjaProductsStockTestCase
- POSScreen.tsx
- CustomUserAdmin
- stock/admin.py
- _write_csv_to_zip
- vite.config.ts

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
- `create_gold_rate()` --uses--> `GoldRate`  [INFERRED]
  backend/ninja_api/routers/accounting_router.py → backend/apps/accounting/models.py
- `get_current_rates()` --uses--> `GoldRate`  [INFERRED]
  backend/ninja_api/routers/accounting_router.py → backend/apps/accounting/models.py

## Import Cycles
- None detected.

## Communities (116 total, 57 thin omitted)

### Community 0 - "products_router.py"
Cohesion: 0.08
Nodes (23): _threaded_qr(), generate_qr_for_product(), create_category(), create_product(), create_purity(), delete_product(), _format_product(), get_product() (+15 more)

### Community 3 - "qr_tags_router.py"
Cohesion: 0.11
Nodes (17): QRTag, Meta, generate_qr_batch_async(), batch_generate_tags(), create_tray(), _format_qrtag(), _format_tray(), _generate_tray_code() (+9 more)

### Community 5 - "Client"
Cohesion: 0.05
Nodes (8): Client, Meta, ProvisioningStatus, InvoiceSnapshotImmutabilityTestCase, CustomerEmailValidationTestCase, OldGoldValidationTestCase, ProductValidationTestCase, TenantIsolationTestCase

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
Cohesion: 0.09
Nodes (40): AddPaymentIn, BatchQRIn, BillCreateResponse, BillDetailResponse, CashEntryIn, CloseDayIn, CreateTrayIn, CustomerOut (+32 more)

### Community 12 - "validate_password_policy"
Cohesion: 0.06
Nodes (6): JewelleryPasswordPolicyValidator, validate_password_policy(), generate_schema_name(), _execute_pipeline(), get_store_provisioning_status(), PasswordPolicyTestCase

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

### Community 37 - "UUID"
Cohesion: 0.13
Nodes (5): Migration, Migration, Migration, RequestLoggingMiddleware, scan_item_into_bill()

### Community 38 - "react"
Cohesion: 0.19
Nodes (20): App(), FeatureRoute(), ProtectedRoute(), PasswordPolicyChecklist(), PasswordPolicyChecklistProps, AuthProvider(), useAuth(), AccountingDashboard() (+12 more)

### Community 39 - "dependencies"
Cohesion: 0.10
Nodes (20): dependencies, axios@^1.20.0, @hookform/resolvers@^6.0.0, html5-qrcode@^2.3.8, lucide-react@^1.61.0, qrcode@^1.5.4, react@^19.3.1, react-hook-form@^7.90.0 (+12 more)

### Community 43 - "billing/services.py"
Cohesion: 0.15
Nodes (3): create_sale(), generate_invoice_pdf(), generate_invoice_pdf_async()

### Community 44 - "@playwright/test"
Cohesion: 0.17
Nodes (12): devDependencies, oxlint@^1.88.0, @playwright/test@^1.64.1, @types/node@^24.19.2, @types/react@^19.3.0, @types/react-dom@^19.3.0, typescript@~6.0.3, oxlint (+4 more)

### Community 45 - "MultiSourceGoldRateScraperTestCase"
Cohesion: 0.18
Nodes (4): BaseRateScraper, RateScrapeResult, BullionDeskScraper, IBJAScraper

### Community 48 - "bills_router.py"
Cohesion: 0.06
Nodes (9): Bill, Meta, Status, IdempotencyRecord, Meta, generate_bill_token(), create_bill(), get_bill_cart() (+1 more)

### Community 49 - "auth_router.py"
Cohesion: 0.07
Nodes (26): EmailService, PasswordResetToken, Meta, decode_token(), change_own_password(), complete_password_reset(), create_branch(), create_user() (+18 more)

### Community 51 - "websocket_handler.py"
Cohesion: 0.17
Nodes (7): get_active_session(), mobile_websocket_app(), parse_query_string(), pos_websocket_app(), send_json(), validate_jwt_user(), application()

### Community 52 - "Tray"
Cohesion: 0.14
Nodes (4): Tray, Meta, delete_tray(), update_tray()

### Community 53 - "StockSummary"
Cohesion: 0.13
Nodes (9): not_found_handler(), permission_error_handler(), value_error_handler(), create_stock_movement(), list_stock_movements(), list_stock_summary(), StockMovementIn, StockMovementOut (+1 more)

### Community 54 - "create_token"
Cohesion: 0.06
Nodes (4): create_token(), DeveloperPortalTestCase, NinjaAuthTestCase, StoreOnboardingAndRBACTestCase

### Community 57 - "lucide-react"
Cohesion: 0.42
Nodes (7): CustomerDirectoryModal(), CustomerDirectoryModalProps, CustomerFormModal(), CustomerFormModalProps, CustomerSelectOrAddProps, Customer, lucide-react

### Community 62 - "User"
Cohesion: 0.17
Nodes (7): Branch, Meta, User, Role, resolve_and_record_scan(), Domain, TenantProvisioningService

### Community 64 - "Purity"
Cohesion: 0.13
Nodes (9): Customer, ProductAdmin, Category, Meta, Purity, Meta, TenantBackupService, TenantRestoreService (+1 more)

### Community 65 - "Payment"
Cohesion: 0.24
Nodes (6): PaymentInline, SaleAdmin, SaleItemInline, Payment, PaymentMethod, SaleItem

### Community 66 - "package.json"
Cohesion: 0.15
Nodes (12): react-dom@^19.3.1, zod@^4.6.7, @zxing/browser@^0.2.1, @zxing/library@^0.23.0, name, private, type, version (+4 more)

### Community 67 - "logger.ts"
Cohesion: 0.12
Nodes (7): ErrorBoundary, Props, State, logBuffer, LogEntry, logger, LogLevel

### Community 68 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, lint, preview, test:e2e, tunnel

### Community 69 - "accounting_router.py"
Cohesion: 0.10
Nodes (18): DayBook, Meta, close_day_book(), close_day_book_alias(), create_customer(), create_gold_rate(), _format_daybook(), get_today_day_book() (+10 more)

### Community 72 - "tenants_router.py"
Cohesion: 0.12
Nodes (17): require_role(), reset_staff_password(), create_tenant(), developer_login(), developer_reset_user_password(), developer_switch_store_token(), developer_toggle_user_status(), _format_tenant() (+9 more)

### Community 74 - "resolver.py"
Cohesion: 0.09
Nodes (5): ProductionTenantMiddleware, TenantContextMismatchError, TenantResolutionError, TenantResolver, TenantSuspendedOrInactiveError

### Community 75 - "metalRateHelper.ts"
Cohesion: 0.53
Nodes (5): clean(), detectProductMetal(), MetalType, ResolvedMetalRate, resolveProductRate()

### Community 77 - "django_db_models_deletion"
Cohesion: 0.06
Nodes (17): Migration, Migration, Migration, Migration, Migration, Migration, Migration, Migration (+9 more)

### Community 78 - "pairing.py"
Cohesion: 0.12
Nodes (14): POSPairingSession, Meta, redeem_pairing_code(), revoke_pairing_session(), verify_mobile_token(), mobile_scan_fallback(), _execute_scan(), redeem_pos_pairing_token() (+6 more)

### Community 81 - "services"
Cohesion: 0.14
Nodes (13): generateValue, key, sync, value, services, autoDeployTrigger, buildCommand, envVars (+5 more)

### Community 83 - "pairing.py"
Cohesion: 0.15
Nodes (6): ScannedItemAudit, Meta, generate_pairing_qr_data_url(), get_lan_ip(), start_pairing_session(), generate_qr_for_tray()

### Community 84 - "InvoiceSetting"
Cohesion: 0.25
Nodes (4): InvoiceSetting, PaperSize, TemplateStyle, update_invoice_settings()

### Community 86 - "list_users"
Cohesion: 0.22
Nodes (4): get_branch(), get_current_user(), list_branches(), list_users()

### Community 87 - "Layout.tsx"
Cohesion: 0.19
Nodes (14): Layout(), InvoiceSettingsModal(), ExportDataModal(), ExportDataModalProps, StaffManagementModal(), StaffManagementModalProps, UserItem, canAccessFeature() (+6 more)

### Community 89 - "QRTagModal.tsx"
Cohesion: 0.22
Nodes (15): CartItem, BulkQRPrintModal(), BulkQRPrintModalProps, TagItemWithQR, QRTagModal(), QRTagModalProps, Product, generateQRDataUrl() (+7 more)

### Community 90 - "Sale"
Cohesion: 0.17
Nodes (11): Sale, Meta, PaymentStatus, SaleStatus, _next_invoice_number(), add_sale_payment(), cancel_sale(), create_sale_invoice() (+3 more)

### Community 92 - "download_invoice_pdf"
Cohesion: 0.20
Nodes (5): download_invoice_pdf(), download_invoice_pdf_underscore(), get_invoice_settings(), get_item_by_qr(), list_sales()

### Community 94 - "index.ts"
Cohesion: 0.22
Nodes (15): CameraCaptureModal(), CameraCaptureModalProps, ClubTrayModal(), ClubTrayModalProps, ProductFormModal(), ProductFormModalProps, ProductList(), SortField (+7 more)

### Community 95 - "billing/services.py"
Cohesion: 0.19
Nodes (4): StockMovement, Meta, MovementType, record_stock_movement()

### Community 96 - "GoldRate"
Cohesion: 0.09
Nodes (10): DayBookAdmin, GoldRate, Meta, ShopRateSetting, get_scraper(), list_available_sources(), fetch_live_market_rates_async(), sync_live_rates_async() (+2 more)

### Community 97 - "Product"
Cohesion: 0.22
Nodes (5): ProductFilter, Meta, Product, Meta, developer_overview()

### Community 98 - "export_router.py"
Cohesion: 0.22
Nodes (4): CleanupFile, export_all_shops_data(), export_shop_data(), _parse_date()

### Community 99 - "get"
Cohesion: 0.17
Nodes (6): get_current_rates(), get_customer(), get_live_market_rates(), get_rate_settings(), list_customers(), list_gold_rates_history()

### Community 102 - "MobileScannerPage.tsx"
Cohesion: 0.22
Nodes (11): beep(), isVideoReady(), makeReader(), MobileQRScanner(), startDecodeLoop(), MobileQRScannerProps, ScannerState, MobileScannerPage() (+3 more)

### Community 105 - "Item"
Cohesion: 0.25
Nodes (5): Item, Meta, Status, _resolve_item_by_token(), verify_physical_tag()

### Community 106 - "django_contrib"
Cohesion: 0.29
Nodes (3): ClientAdmin, DomainAdmin, DomainInline

### Community 109 - "provider.py"
Cohesion: 0.11
Nodes (4): BaseEmailProvider, EmailDeliveryError, get_email_provider(), get_password_reset_email()

### Community 110 - "NinjaProductsStockTestCase"
Cohesion: 0.18
Nodes (3): StockSummary, Meta, NinjaProductsStockTestCase

### Community 111 - "POSScreen.tsx"
Cohesion: 0.15
Nodes (23): api, AuthContext, AuthContextType, RateSource, InvoiceModal(), InvoiceModalProps, InvoiceSettingsModalProps, PosScannerConnectionModal() (+15 more)

### Community 118 - "vite.config.ts"
Cohesion: 0.20
Nodes (8): @tailwindcss/vite@^4.3.3, vite@^8.3.4, @vitejs/plugin-basic-ssl@^2.3.0, @vitejs/plugin-react@^6.1.2, @tailwindcss/vite, vite, @vitejs/plugin-basic-ssl, @vitejs/plugin-react

## Knowledge Gaps
- **1 isolated node(s):** `swarna-khata-book`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 723 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **57 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Branch` connect `User` to `products_router.py`, `NinjaPOSBillingTestCase`, `Client`, `InvoiceSettingsTestCase`, `MultiSourceGoldRateScraperTestCase`, `bills_router.py`, `auth_router.py`, `create_token`, `DayBookAccountingTestCase`, `TrayQRTagsTestCase`, `UnifiedQRArchitectureTestCase`, `SecurityAuditAndAccessControlTestCase`, `Purity`, `accounting_router.py`, `tenants_router.py`, `DataExportTestCase`, `BrevoPasswordResetIntegrationTestCase`, `InvoiceSetting`, `list_users`, `Sale`, `download_invoice_pdf`, `ProductionHardeningArchitectureTestCase`, `GoldRate`, `Product`, `get`, `NinjaProductsStockTestCase`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Are the 34 inferred relationships involving `Client` (e.g. with `export_tenant_data_to_zip()` and `generate_all_shops_export_archive()`) actually correct?**
  _`Client` has 34 INFERRED edges - model-reasoned connections that need verification._
- **What connects `swarna-khata-book` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `products_router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07557354925775979 - nodes in this community are weakly interconnected._
- **Why does `User` connect `User` to `export_tenant_data_to_zip`, `NinjaPOSBillingTestCase`, `Client`, `InvoiceSettingsTestCase`, `validate_password_policy`, `MultiSourceGoldRateScraperTestCase`, `bills_router.py`, `auth_router.py`, `create_token`, `DayBookAccountingTestCase`, `TrayQRTagsTestCase`, `UnifiedQRArchitectureTestCase`, `SecurityAuditAndAccessControlTestCase`, `Purity`, `tenants_router.py`, `resolver.py`, `DataExportTestCase`, `BrevoPasswordResetIntegrationTestCase`, `list_users`, `ProductionHardeningArchitectureTestCase`, `Product`, `JWTAuth`, `NinjaProductsStockTestCase`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Are the 38 inferred relationships involving `User` (e.g. with `TenantBackupService` and `export_tenant_data_to_zip()`) actually correct?**
  _`User` has 38 INFERRED edges - model-reasoned connections that need verification._
- **Should `qr_tags_router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11491935483870967 - nodes in this community are weakly interconnected._