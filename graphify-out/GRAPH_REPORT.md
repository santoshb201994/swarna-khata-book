# Graph Report - swarna_khata_book  (2026-11-04)

## Corpus Check
- 213 files · ~105,864 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .bat 3, .css 2)

## Summary
- 1722 nodes · 4116 edges · 119 communities (63 shown, 56 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 495 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `28185229`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- products_router.py
- bills_router.py
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
- BrevoEmailProvider
- dependencies
- tenants_router.py
- DayBook
- NinjaAuthTestCase
- App.tsx
- tenants/admin.py
- bills_router.py
- auth_router.py
- EndpointsAuthAndBranchesTestCase
- websocket_handler.py
- create_token
- GoldRate
- accounting/services.py
- render-build.sh
- DayBookAccountingTestCase
- POSSessionHub
- DataExportTestCase
- UnifiedQRArchitectureTestCase
- SecurityAuditAndAccessControlTestCase
- Branch
- Product
- devDependencies
- typing
- billing/services.py
- logger.ts
- scripts
- OldGoldValidationTestCase
- verify-before-complete.md
- jewellery_erp_coding_workflow_mindmap.md
- create_tenant
- export_tenant_data_to_zip
- post
- TrayQRTagsTestCase
- StockSummary
- pos_pairing_router.py
- Payment
- QRTagModal.tsx
- services
- POSPairingSession
- download_invoice_pdf
- Sale
- EndpointsProductsQrAndStockTestCase
- MobileScannerPage.tsx
- vercel.json
- QRTag
- JWTAuth
- start.sh
- Tray
- billing/services.py
- Tray
- ShopRateSetting
- logging
- update_invoice_settings
- list_users
- Command
- EndpointsBillingPosAndExportTestCase
- stock_router.py
- index.ts
- @playwright/test
- django_db_models_deletion
- GoldRate
- vite.config.ts
- NinjaPOSBillingTestCase
- MobileScannerPage.tsx
- EndpointsAccountingAndDaybookTestCase
- stock/admin.py
- DecimalJsonEncoder
- CustomUserAdmin
- Purity
- pairing.py
- _get_encryption_key
- billing_router.py

## God Nodes (most connected - your core abstractions)
1. `Client` - 95 edges
2. `User` - 85 edges
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

## Communities (119 total, 56 thin omitted)

### Community 0 - "products_router.py"
Cohesion: 0.10
Nodes (18): generate_qr_for_product(), require_role(), create_category(), create_product(), create_purity(), delete_product(), _format_product(), get_product() (+10 more)

### Community 1 - "bills_router.py"
Cohesion: 0.14
Nodes (11): Bill, Meta, Status, create_bill(), get_bill_cart(), scan_item_into_bill(), BillCreateResponse, BillDetailResponse (+3 more)

### Community 2 - "MultiSourceGoldRateScraperTestCase"
Cohesion: 0.06
Nodes (6): BaseRateScraper, RateScrapeResult, BullionDeskScraper, IBJAScraper, KSJFScraper, MultiSourceGoldRateScraperTestCase

### Community 3 - "index.ts"
Cohesion: 0.20
Nodes (19): api, RateSource, InvoiceModal(), InvoiceModalProps, InvoiceSettingsModalProps, PosScannerConnectionModal(), PosScannerConnectionModalProps, POSScreen() (+11 more)

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
Cohesion: 0.09
Nodes (44): AddPaymentIn, BatchQRIn, CashEntryIn, CategoryOut, CloseDayIn, CreateTrayIn, CustomerOut, DayBookOut (+36 more)

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

### Community 39 - "dependencies"
Cohesion: 0.09
Nodes (23): dependencies, axios@^1.20.0, @hookform/resolvers@^6.0.0, html5-qrcode@^2.3.8, lucide-react@^1.61.0, qrcode@^1.5.4, react@^19.3.1, react-dom@^19.3.1 (+15 more)

### Community 40 - "tenants_router.py"
Cohesion: 0.10
Nodes (9): check_global_username_uniqueness(), generate_schema_name(), TenantProvisioningService, _execute_pipeline(), developer_delete_tenant(), _format_tenant(), get_store_provisioning_status(), list_tenants() (+1 more)

### Community 43 - "DayBook"
Cohesion: 0.18
Nodes (8): DayBook, Meta, _format_daybook(), get_today_day_book(), list_day_books(), _perform_close_day_book(), record_petty_cash_entry(), update_day_book_cash()

### Community 45 - "App.tsx"
Cohesion: 0.15
Nodes (22): App(), FeatureRoute(), ProtectedRoute(), Layout(), AuthContext, AuthContextType, AuthProvider(), useAuth() (+14 more)

### Community 46 - "tenants/admin.py"
Cohesion: 0.33
Nodes (3): ClientAdmin, DomainAdmin, DomainInline

### Community 48 - "bills_router.py"
Cohesion: 0.09
Nodes (4): IdempotencyRecord, Meta, generate_bill_token(), BackendAuthoritativePollingTestCase

### Community 49 - "auth_router.py"
Cohesion: 0.06
Nodes (30): EmailService, PasswordResetToken, Meta, decode_token(), change_own_password(), complete_password_reset(), create_branch(), create_user() (+22 more)

### Community 51 - "websocket_handler.py"
Cohesion: 0.16
Nodes (8): get_active_session(), mobile_websocket_app(), _sync_resolve(), parse_query_string(), pos_websocket_app(), send_json(), validate_jwt_user(), application()

### Community 52 - "create_token"
Cohesion: 0.08
Nodes (4): create_token(), developer_login(), DeveloperPortalTestCase, StoreOnboardingAndRBACTestCase

### Community 53 - "GoldRate"
Cohesion: 0.20
Nodes (5): get_current_rates(), get_customer(), get_live_market_rates(), list_customers(), list_gold_rates_history()

### Community 54 - "accounting/services.py"
Cohesion: 0.16
Nodes (4): get_scraper(), fetch_live_market_rates_async(), sync_live_rates_async(), sync_rates_from_source()

### Community 62 - "Branch"
Cohesion: 0.25
Nodes (5): Branch, Meta, User, Role, Domain

### Community 63 - "Product"
Cohesion: 0.22
Nodes (5): ProductFilter, Meta, Product, Meta, developer_overview()

### Community 64 - "devDependencies"
Cohesion: 0.13
Nodes (19): devDependencies, oxlint@^1.88.0, @playwright/test@^1.64.1, @types/node@^24.19.2, @types/react@^19.3.0, @types/react-dom@^19.3.0, typescript@~6.0.3, @vitejs/plugin-react@^6.1.2 (+11 more)

### Community 65 - "typing"
Cohesion: 0.09
Nodes (5): BaseEmailProvider, ConsoleEmailProvider, EmailDeliveryError, get_email_provider(), get_password_reset_email()

### Community 66 - "billing/services.py"
Cohesion: 0.19
Nodes (4): StockMovement, Meta, MovementType, record_stock_movement()

### Community 67 - "logger.ts"
Cohesion: 0.13
Nodes (7): ErrorBoundary, Props, State, logBuffer, LogEntry, logger, LogLevel

### Community 68 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, preview, test:e2e, test:unit, tunnel

### Community 69 - "OldGoldValidationTestCase"
Cohesion: 0.07
Nodes (6): Client, Meta, ProvisioningStatus, NinjaProductsStockTestCase, CustomerEmailValidationTestCase, TenantIsolationTestCase

### Community 72 - "create_tenant"
Cohesion: 0.15
Nodes (7): create_tenant(), developer_reset_user_password(), developer_switch_store_token(), developer_toggle_user_status(), toggle_tenant_status(), SwitchStoreIn, TenantCreateIn

### Community 74 - "export_tenant_data_to_zip"
Cohesion: 0.07
Nodes (7): CleanupFile, export_tenant_data_to_zip(), generate_shop_export_archive(), health_check(), export_all_shops_data(), export_shop_data(), _parse_date()

### Community 75 - "post"
Cohesion: 0.17
Nodes (9): close_day_book(), close_day_book_alias(), create_customer(), create_gold_rate(), reopen_day_book(), reopen_day_book_alias(), sync_rates_from_web(), update_customer() (+1 more)

### Community 77 - "StockSummary"
Cohesion: 0.13
Nodes (3): StockSummary, Meta, OldGoldValidationTestCase

### Community 78 - "pos_pairing_router.py"
Cohesion: 0.17
Nodes (5): redeem_pairing_code(), revoke_pairing_session(), redeem_pos_pairing_token(), revoke_pos_pairing_token(), start_pos_pairing_session()

### Community 79 - "Payment"
Cohesion: 0.24
Nodes (6): PaymentInline, SaleAdmin, SaleItemInline, Payment, PaymentMethod, SaleItem

### Community 80 - "QRTagModal.tsx"
Cohesion: 0.14
Nodes (24): CartItem, BulkQRPrintModal(), BulkQRPrintModalProps, TagItemWithQR, ClubTrayModal(), ClubTrayModalProps, ProductFormModal(), ProductList() (+16 more)

### Community 81 - "services"
Cohesion: 0.14
Nodes (13): generateValue, key, sync, value, services, autoDeployTrigger, buildCommand, envVars (+5 more)

### Community 82 - "POSPairingSession"
Cohesion: 0.12
Nodes (8): POSPairingSession, Meta, ScannedItemAudit, Meta, _inner_resolve_and_record_scan(), resolve_and_record_scan(), mobile_scan_fallback(), _execute_scan()

### Community 83 - "download_invoice_pdf"
Cohesion: 0.25
Nodes (4): download_invoice_pdf(), download_invoice_pdf_underscore(), get_invoice_settings(), list_sales()

### Community 84 - "Sale"
Cohesion: 0.25
Nodes (6): Sale, Meta, PaymentStatus, SaleStatus, _next_invoice_number(), create_sale_invoice()

### Community 87 - "MobileScannerPage.tsx"
Cohesion: 0.19
Nodes (11): @zxing/browser@^0.2.1, @zxing/library@^0.23.0, beep(), isVideoReady(), makeReader(), MobileQRScanner(), startDecodeLoop(), MobileQRScannerProps (+3 more)

### Community 89 - "QRTag"
Cohesion: 0.27
Nodes (4): QRTag, Meta, generate_qr_batch(), generate_qr_batch_async()

### Community 92 - "Tray"
Cohesion: 0.11
Nodes (16): generate_qr_for_tray(), batch_generate_tags(), create_tray(), _format_qrtag(), _format_tray(), _generate_tray_code(), get_qr_tag(), get_tray() (+8 more)

### Community 93 - "billing/services.py"
Cohesion: 0.15
Nodes (3): create_sale(), generate_invoice_pdf(), generate_invoice_pdf_async()

### Community 94 - "Tray"
Cohesion: 0.20
Nodes (3): Tray, Meta, delete_tray()

### Community 95 - "ShopRateSetting"
Cohesion: 0.17
Nodes (5): ShopRateSetting, list_available_sources(), get_rate_settings(), get_rate_sources(), update_rate_settings()

### Community 96 - "logging"
Cohesion: 0.10
Nodes (5): ProductionTenantMiddleware, TenantContextMismatchError, TenantResolutionError, TenantResolver, TenantSuspendedOrInactiveError

### Community 98 - "list_users"
Cohesion: 0.22
Nodes (4): get_branch(), get_current_user(), list_branches(), list_users()

### Community 100 - "EndpointsBillingPosAndExportTestCase"
Cohesion: 0.15
Nodes (4): Item, Meta, Status, EndpointsBillingPosAndExportTestCase

### Community 101 - "stock_router.py"
Cohesion: 0.13
Nodes (9): not_found_handler(), permission_error_handler(), value_error_handler(), create_stock_movement(), list_stock_movements(), list_stock_summary(), StockMovementIn, StockMovementOut (+1 more)

### Community 102 - "index.ts"
Cohesion: 0.15
Nodes (17): clean(), detectProductMetal(), MetalType, ResolvedMetalRate, resolveProductRate(), CameraCaptureModal(), CameraCaptureModalProps, ProductFormModalProps (+9 more)

### Community 104 - "django_db_models_deletion"
Cohesion: 0.05
Nodes (21): Migration, Migration, Migration, Migration, Migration, Migration, Migration, Migration (+13 more)

### Community 105 - "GoldRate"
Cohesion: 0.22
Nodes (3): DayBookAdmin, GoldRate, Meta

### Community 106 - "vite.config.ts"
Cohesion: 0.22
Nodes (6): @tailwindcss/vite@^4.3.3, vite@^8.3.4, @vitejs/plugin-basic-ssl@^2.3.0, @tailwindcss/vite, vite, @vitejs/plugin-basic-ssl

### Community 110 - "MobileScannerPage.tsx"
Cohesion: 0.39
Nodes (6): MobileScannerPage(), ScannedHistoryItem, getApiBaseUrl(), getWsBaseUrl(), axios, react-router-dom

### Community 115 - "Purity"
Cohesion: 0.07
Nodes (15): Customer, InvoiceSetting, PaperSize, TemplateStyle, ProductAdmin, Category, Meta, Purity (+7 more)

### Community 117 - "pairing.py"
Cohesion: 0.22
Nodes (4): generate_pairing_qr_data_url(), get_lan_ip(), start_pairing_session(), verify_mobile_token()

### Community 120 - "billing_router.py"
Cohesion: 0.18
Nodes (8): add_sale_payment(), cancel_sale(), _format_sale(), get_item_by_qr(), get_sale(), reset_demo_invoice_settings(), _resolve_item_by_token(), verify_physical_tag()

## Knowledge Gaps
- **1 isolated node(s):** `swarna-khata-book`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 770 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **56 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `Branch` to `products_router.py`, `MultiSourceGoldRateScraperTestCase`, `ProductValidationTestCase`, `InvoiceSettingsTestCase`, `validate_password_policy`, `ProductionHardeningArchitectureTestCase`, `BrevoEmailProvider`, `tenants_router.py`, `NinjaAuthTestCase`, `bills_router.py`, `auth_router.py`, `EndpointsAuthAndBranchesTestCase`, `create_token`, `DayBookAccountingTestCase`, `DataExportTestCase`, `UnifiedQRArchitectureTestCase`, `SecurityAuditAndAccessControlTestCase`, `Product`, `typing`, `OldGoldValidationTestCase`, `create_tenant`, `export_tenant_data_to_zip`, `TrayQRTagsTestCase`, `StockSummary`, `EndpointsProductsQrAndStockTestCase`, `JWTAuth`, `logging`, `list_users`, `EndpointsBillingPosAndExportTestCase`, `NinjaPOSBillingTestCase`, `EndpointsAccountingAndDaybookTestCase`, `Purity`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Are the 40 inferred relationships involving `Client` (e.g. with `check_global_username_uniqueness()` and `export_tenant_data_to_zip()`) actually correct?**
  _`Client` has 40 INFERRED edges - model-reasoned connections that need verification._
- **What connects `swarna-khata-book` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `products_router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09915966386554621 - nodes in this community are weakly interconnected._
- **Why does `Branch` connect `Branch` to `products_router.py`, `MultiSourceGoldRateScraperTestCase`, `ProductValidationTestCase`, `InvoiceSettingsTestCase`, `ProductionHardeningArchitectureTestCase`, `BrevoEmailProvider`, `tenants_router.py`, `NinjaAuthTestCase`, `bills_router.py`, `auth_router.py`, `EndpointsAuthAndBranchesTestCase`, `create_token`, `GoldRate`, `accounting/services.py`, `DayBookAccountingTestCase`, `DataExportTestCase`, `UnifiedQRArchitectureTestCase`, `SecurityAuditAndAccessControlTestCase`, `Product`, `typing`, `OldGoldValidationTestCase`, `post`, `TrayQRTagsTestCase`, `StockSummary`, `download_invoice_pdf`, `EndpointsProductsQrAndStockTestCase`, `update_invoice_settings`, `list_users`, `EndpointsBillingPosAndExportTestCase`, `NinjaPOSBillingTestCase`, `EndpointsAccountingAndDaybookTestCase`, `Purity`, `billing_router.py`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Are the 45 inferred relationships involving `User` (e.g. with `check_global_username_uniqueness()` and `TenantBackupService`) actually correct?**
  _`User` has 45 INFERRED edges - model-reasoned connections that need verification._
- **Should `bills_router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1437908496732026 - nodes in this community are weakly interconnected._