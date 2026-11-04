# Graph Report - swarna_khata_book  (2026-11-04)

## Corpus Check
- 213 files · ~106,691 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .bat 3, .css 2)

## Summary
- 1728 nodes · 4126 edges · 111 communities (54 shown, 57 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 497 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5446f5f9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- products_router.py
- create_token
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
- package.json
- django_db
- tenants_router.py
- NinjaAuthTestCase
- App.tsx
- Purity
- bills_router.py
- auth_router.py
- tenants_router.py
- POSPairingSession
- Sale
- NinjaPOSBillingTestCase
- DataExportTestCase
- render-build.sh
- DayBookAccountingTestCase
- POSSessionHub
- index.ts
- UnifiedQRArchitectureTestCase
- SecurityAuditAndAccessControlTestCase
- Branch
- typing
- @playwright/test
- TrayQRTagsTestCase
- react
- logger.ts
- scripts
- django_conf
- verify-before-complete.md
- jewellery_erp_coding_workflow_mindmap.md
- resolver.py
- typing
- accounting_router.py
- websocket_handler.py
- Client
- EndpointsAuthAndBranchesTestCase
- Product
- devDependencies
- services
- vite.config.ts
- DayBook
- pos_pairing_router.py
- EndpointsProductsQrAndStockTestCase
- MobileScannerPage.tsx
- vercel.json
- export_tenant_data_to_zip
- JWTAuth
- start.sh
- qr_tags_router.py
- pairing.py
- tenants/admin.py
- QRTag
- Tray
- ProductFormModal.tsx
- StockMovement
- Command
- list_stock_movements
- create_stock_movement
- EndpointsAccountingAndDaybookTestCase
- backup_service.py
- CustomUserAdmin
- EndpointsBillingPosAndExportTestCase
- _get_encryption_key
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
- `export_tenant_data_to_zip()` --uses--> `GoldRate`  [INFERRED]
  backend/apps/tenants/export_service.py → backend/apps/accounting/models.py
- `create_gold_rate()` --uses--> `GoldRate`  [INFERRED]
  backend/ninja_api/routers/accounting_router.py → backend/apps/accounting/models.py

## Import Cycles
- None detected.

## Communities (111 total, 57 thin omitted)

### Community 0 - "products_router.py"
Cohesion: 0.10
Nodes (18): generate_qr_for_product(), require_role(), create_category(), create_product(), create_purity(), delete_product(), _format_product(), get_product() (+10 more)

### Community 1 - "create_token"
Cohesion: 0.09
Nodes (3): create_token(), DeveloperPortalTestCase, StoreOnboardingAndRBACTestCase

### Community 2 - "MultiSourceGoldRateScraperTestCase"
Cohesion: 0.07
Nodes (8): BaseRateScraper, RateScrapeResult, BullionDeskScraper, IBJAScraper, KSJFScraper, get_scraper(), list_available_sources(), MultiSourceGoldRateScraperTestCase

### Community 3 - "index.ts"
Cohesion: 0.14
Nodes (17): vitest@^5.1.0, AuthContext, AuthContextType, clean(), detectProductMetal(), MetalType, ResolvedMetalRate, resolveProductRate() (+9 more)

### Community 4 - "lucide-react"
Cohesion: 0.19
Nodes (16): PasswordPolicyChecklist(), PasswordPolicyChecklistProps, ResetPasswordPage(), OverviewData, StoreUser, TenantItem, StaffManagementModal(), StaffManagementModalProps (+8 more)

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
Nodes (47): scan_item_into_bill(), BatchQRIn, BillCreateResponse, BillDetailResponse, BranchOut, CashEntryIn, CategoryOut, CloseDayIn (+39 more)

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

### Community 38 - "BrevoPasswordResetIntegrationTestCase"
Cohesion: 0.07
Nodes (3): BrevoEmailProvider, ConsoleEmailProvider, BrevoPasswordResetIntegrationTestCase

### Community 39 - "package.json"
Cohesion: 0.08
Nodes (33): dependencies, axios@^1.20.0, @hookform/resolvers@^6.0.0, html5-qrcode@^2.3.8, lucide-react@^1.61.0, qrcode@^1.5.4, react@^19.3.1, react-dom@^19.3.1 (+25 more)

### Community 40 - "django_db"
Cohesion: 0.08
Nodes (15): Migration, Customer, Migration, Migration, Migration, Migration, Migration, Category (+7 more)

### Community 43 - "tenants_router.py"
Cohesion: 0.11
Nodes (10): create_tenant(), developer_login(), developer_reset_user_password(), developer_switch_store_token(), developer_toggle_user_status(), _format_tenant(), list_tenants(), toggle_tenant_status() (+2 more)

### Community 45 - "App.tsx"
Cohesion: 0.17
Nodes (20): App(), FeatureRoute(), ProtectedRoute(), Layout(), AuthProvider(), useAuth(), AccountingDashboard(), Login() (+12 more)

### Community 46 - "Purity"
Cohesion: 0.13
Nodes (4): sync_rates_from_source(), Purity, Meta, TenantIsolationTestCase

### Community 48 - "bills_router.py"
Cohesion: 0.07
Nodes (9): Bill, Meta, Status, IdempotencyRecord, Meta, generate_bill_token(), create_bill(), get_bill_cart() (+1 more)

### Community 49 - "auth_router.py"
Cohesion: 0.06
Nodes (30): EmailService, PasswordResetToken, Meta, decode_token(), change_own_password(), complete_password_reset(), create_branch(), create_user() (+22 more)

### Community 50 - "tenants_router.py"
Cohesion: 0.10
Nodes (9): ShopRateSetting, check_global_username_uniqueness(), generate_schema_name(), TenantProvisioningService, _execute_pipeline(), developer_delete_tenant(), developer_overview(), get_store_provisioning_status() (+1 more)

### Community 51 - "POSPairingSession"
Cohesion: 0.15
Nodes (7): POSPairingSession, Meta, _inner_resolve_and_record_scan(), resolve_and_record_scan(), _sync_resolve(), mobile_scan_fallback(), _execute_scan()

### Community 52 - "Sale"
Cohesion: 0.08
Nodes (11): InvoiceSetting, PaperSize, TemplateStyle, Sale, Meta, PaymentStatus, SaleStatus, create_sale() (+3 more)

### Community 58 - "index.ts"
Cohesion: 0.14
Nodes (24): CartItem, BulkQRPrintModal(), BulkQRPrintModalProps, TagItemWithQR, ClubTrayModal(), ClubTrayModalProps, FALLBACK_CATEGORIES, FALLBACK_PURITIES (+16 more)

### Community 62 - "Branch"
Cohesion: 0.19
Nodes (6): Branch, Meta, User, Role, Migration, Domain

### Community 63 - "typing"
Cohesion: 0.13
Nodes (4): BaseEmailProvider, EmailDeliveryError, get_email_provider(), get_password_reset_email()

### Community 66 - "react"
Cohesion: 0.19
Nodes (20): api, DEFAULT_PURITY_OPTIONS, DEFAULT_RATE_SOURCES, RateSource, InvoiceModal(), InvoiceModalProps, InvoiceSettingsModalProps, PosScannerConnectionModal() (+12 more)

### Community 67 - "logger.ts"
Cohesion: 0.13
Nodes (7): ErrorBoundary, Props, State, logBuffer, LogEntry, logger, LogLevel

### Community 68 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, preview, test:e2e, test:unit, tunnel

### Community 69 - "django_conf"
Cohesion: 0.05
Nodes (15): Migration, Migration, Migration, Migration, Migration, Migration, Migration, Migration (+7 more)

### Community 72 - "resolver.py"
Cohesion: 0.10
Nodes (5): ProductionTenantMiddleware, TenantContextMismatchError, TenantResolutionError, TenantResolver, TenantSuspendedOrInactiveError

### Community 74 - "typing"
Cohesion: 0.14
Nodes (7): CleanupFile, not_found_handler(), permission_error_handler(), value_error_handler(), export_all_shops_data(), export_shop_data(), _parse_date()

### Community 75 - "accounting_router.py"
Cohesion: 0.06
Nodes (25): fetch_live_market_rates_async(), sync_live_rates_async(), close_day_book(), close_day_book_alias(), create_customer(), create_gold_rate(), _format_daybook(), get_current_rates() (+17 more)

### Community 76 - "websocket_handler.py"
Cohesion: 0.15
Nodes (8): verify_mobile_token(), get_active_session(), mobile_websocket_app(), parse_query_string(), pos_websocket_app(), send_json(), validate_jwt_user(), application()

### Community 77 - "Client"
Cohesion: 0.07
Nodes (7): DomainInline, Client, Meta, ProvisioningStatus, InvoiceSnapshotImmutabilityTestCase, NinjaProductsStockTestCase, OldGoldValidationTestCase

### Community 79 - "Product"
Cohesion: 0.20
Nodes (5): ProductAdmin, ProductFilter, Meta, Product, Meta

### Community 80 - "devDependencies"
Cohesion: 0.17
Nodes (12): devDependencies, oxlint@^1.88.0, @playwright/test@^1.64.1, @types/node@^24.19.2, @types/react@^19.3.0, @types/react-dom@^19.3.0, typescript@~6.0.3, oxlint (+4 more)

### Community 81 - "services"
Cohesion: 0.14
Nodes (13): generateValue, key, sync, value, services, autoDeployTrigger, buildCommand, envVars (+5 more)

### Community 82 - "vite.config.ts"
Cohesion: 0.18
Nodes (8): @tailwindcss/vite@^4.3.3, vite@^8.3.4, @vitejs/plugin-basic-ssl@^2.3.0, @vitejs/plugin-react@^6.1.2, @tailwindcss/vite, vite, @vitejs/plugin-basic-ssl, @vitejs/plugin-react

### Community 83 - "DayBook"
Cohesion: 0.15
Nodes (6): DayBookAdmin, DayBook, Meta, GoldRate, Meta, TenantBackupService

### Community 84 - "pos_pairing_router.py"
Cohesion: 0.17
Nodes (5): redeem_pairing_code(), revoke_pairing_session(), redeem_pos_pairing_token(), revoke_pos_pairing_token(), start_pos_pairing_session()

### Community 87 - "MobileScannerPage.tsx"
Cohesion: 0.20
Nodes (12): beep(), isVideoReady(), makeReader(), MobileQRScanner(), startDecodeLoop(), MobileQRScannerProps, ScannerState, MobileScannerPage() (+4 more)

### Community 89 - "export_tenant_data_to_zip"
Cohesion: 0.13
Nodes (4): export_tenant_data_to_zip(), generate_all_shops_export_archive(), generate_shop_export_archive(), _write_csv_to_zip()

### Community 92 - "qr_tags_router.py"
Cohesion: 0.11
Nodes (16): generate_qr_for_tray(), batch_generate_tags(), create_tray(), _format_qrtag(), _format_tray(), _generate_tray_code(), get_qr_tag(), get_tray() (+8 more)

### Community 93 - "pairing.py"
Cohesion: 0.18
Nodes (5): ScannedItemAudit, Meta, generate_pairing_qr_data_url(), get_lan_ip(), start_pairing_session()

### Community 95 - "QRTag"
Cohesion: 0.27
Nodes (4): QRTag, Meta, generate_qr_batch(), generate_qr_batch_async()

### Community 96 - "Tray"
Cohesion: 0.20
Nodes (3): Tray, Meta, delete_tray()

### Community 97 - "ProductFormModal.tsx"
Cohesion: 0.29
Nodes (8): CameraCaptureModal(), CameraCaptureModalProps, FALLBACK_CATEGORIES, FALLBACK_PURITIES, ProductFormModal(), ProductFormModalProps, Category, Purity

### Community 98 - "StockMovement"
Cohesion: 0.50
Nodes (3): StockMovement, Meta, MovementType

### Community 115 - "EndpointsBillingPosAndExportTestCase"
Cohesion: 0.12
Nodes (7): PaymentInline, SaleAdmin, SaleItemInline, Payment, PaymentMethod, SaleItem, EndpointsBillingPosAndExportTestCase

### Community 120 - "billing_router.py"
Cohesion: 0.06
Nodes (29): Item, Meta, Status, record_stock_movement(), add_sale_payment(), cancel_sale(), create_sale_invoice(), download_invoice_pdf() (+21 more)

## Knowledge Gaps
- **1 isolated node(s):** `swarna-khata-book`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 776 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **57 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `Branch` to `products_router.py`, `create_token`, `MultiSourceGoldRateScraperTestCase`, `ProductValidationTestCase`, `InvoiceSettingsTestCase`, `validate_password_policy`, `ProductionHardeningArchitectureTestCase`, `BrevoPasswordResetIntegrationTestCase`, `django_db`, `tenants_router.py`, `NinjaAuthTestCase`, `Purity`, `bills_router.py`, `auth_router.py`, `tenants_router.py`, `NinjaPOSBillingTestCase`, `DataExportTestCase`, `DayBookAccountingTestCase`, `UnifiedQRArchitectureTestCase`, `SecurityAuditAndAccessControlTestCase`, `TrayQRTagsTestCase`, `resolver.py`, `Client`, `EndpointsAuthAndBranchesTestCase`, `DayBook`, `EndpointsProductsQrAndStockTestCase`, `export_tenant_data_to_zip`, `JWTAuth`, `EndpointsAccountingAndDaybookTestCase`, `backup_service.py`, `EndpointsBillingPosAndExportTestCase`, `billing_router.py`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Are the 40 inferred relationships involving `Client` (e.g. with `check_global_username_uniqueness()` and `export_tenant_data_to_zip()`) actually correct?**
  _`Client` has 40 INFERRED edges - model-reasoned connections that need verification._
- **What connects `swarna-khata-book` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `products_router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09915966386554621 - nodes in this community are weakly interconnected._
- **Why does `Client` connect `Client` to `create_token`, `MultiSourceGoldRateScraperTestCase`, `ProductValidationTestCase`, `InvoiceSettingsTestCase`, `validate_password_policy`, `ProductionHardeningArchitectureTestCase`, `BrevoPasswordResetIntegrationTestCase`, `django_db`, `tenants_router.py`, `NinjaAuthTestCase`, `Purity`, `bills_router.py`, `auth_router.py`, `tenants_router.py`, `NinjaPOSBillingTestCase`, `DataExportTestCase`, `DayBookAccountingTestCase`, `UnifiedQRArchitectureTestCase`, `SecurityAuditAndAccessControlTestCase`, `Branch`, `TrayQRTagsTestCase`, `EndpointsAuthAndBranchesTestCase`, `EndpointsProductsQrAndStockTestCase`, `export_tenant_data_to_zip`, `EndpointsAccountingAndDaybookTestCase`, `EndpointsBillingPosAndExportTestCase`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Are the 47 inferred relationships involving `User` (e.g. with `sync_rates_from_source()` and `check_global_username_uniqueness()`) actually correct?**
  _`User` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Should `create_token` be split into smaller, more focused modules?**
  _Cohesion score 0.08712121212121213 - nodes in this community are weakly interconnected._