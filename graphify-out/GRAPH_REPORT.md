# Graph Report - swarna_khata_book  (2026-10-31)

## Corpus Check
- 172 files · ~85,427 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .bat 3, .css 2)

## Summary
- 1371 nodes · 3205 edges · 89 communities (46 shown, 43 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 368 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c34f3bd2`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- products_router.py
- django_db
- create_token
- qr_tags_router.py
- billing_router.py
- tenants_router.py
- DeveloperPortalTestCase
- backend
- compilerOptions
- django_apps
- compilerOptions
- schemas.py
- validate_password_policy
- .oxlintrc.json
- list_stock_movements
- tsconfig.json
- swarna-khata-book
- Key Modules & Capabilities
- React + TypeScript + Vite
- Master Feature Checklist & Test Mapping
- logging
- POSSessionHub
- dependencies
- Purity
- devDependencies
- DeveloperPortal.tsx
- NinjaPOSBillingTestCase
- bills_router.py
- auth_router.py
- pairing.py
- InvoiceSettingsTestCase
- vite.config.ts
- NinjaAuthTestCase
- DayBookAccountingTestCase
- ._post_product
- MultiSourceGoldRateScraperTestCase
- test_mobile_scanner.py
- SecurityAuditAndAccessControlTestCase
- User
- TrayQRTagsTestCase
- billing/models.py
- export_tenant_data_to_zip
- @playwright/test
- logger.ts
- scripts
- Decimal
- verify-before-complete.md
- jewellery_erp_coding_workflow_mindmap.md
- pos_pairing_router.py
- Sale
- bills_router.py
- DataExportTestCase
- AuthContext.tsx
- App.tsx
- tenants/admin.py
- CustomUserAdmin
- billing/services.py
- MobileQRScanner.tsx
- stock_router.py
- accounting_router.py
- JWTAuth
- Product
- react
- ProductList.tsx
- react
- download_invoice_pdf
- DayBook

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

## Communities (89 total, 43 thin omitted)

### Community 0 - "products_router.py"
Cohesion: 0.08
Nodes (25): ProductFilter, Meta, Product, Meta, create_category(), create_product(), create_purity(), delete_product() (+17 more)

### Community 1 - "django_db"
Cohesion: 0.07
Nodes (15): Migration, Migration, Migration, Migration, Migration, Migration, Migration, Migration (+7 more)

### Community 3 - "qr_tags_router.py"
Cohesion: 0.07
Nodes (24): QRTag, Meta, Tray, Meta, generate_qr_batch_async(), _threaded_qr(), generate_qr_for_product(), generate_qr_for_tray() (+16 more)

### Community 4 - "billing_router.py"
Cohesion: 0.14
Nodes (13): Item, Meta, Status, StockMovement, Meta, MovementType, record_stock_movement(), add_sale_payment() (+5 more)

### Community 5 - "tenants_router.py"
Cohesion: 0.14
Nodes (13): require_role(), create_tenant(), developer_login(), developer_overview(), developer_reset_user_password(), developer_switch_store_token(), developer_toggle_user_status(), _format_tenant() (+5 more)

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
Nodes (31): AddPaymentIn, BatchQRIn, CashEntryIn, CloseDayIn, CreateTrayIn, CustomerOut, DayBookOut, DayBookPatchIn (+23 more)

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

### Community 37 - "logging"
Cohesion: 0.11
Nodes (3): ProductionTenantMiddleware, RequestLoggingMiddleware, health_check()

### Community 40 - "dependencies"
Cohesion: 0.10
Nodes (27): dependencies, @hookform/resolvers@^6.0.0, html5-qrcode@^2.3.8, lucide-react@^1.61.0, qrcode@^1.5.4, react@^19.3.1, react-dom@^19.3.1, react-hook-form@^7.90.0 (+19 more)

### Community 43 - "Purity"
Cohesion: 0.10
Nodes (9): GoldRate, Meta, ShopRateSetting, sync_live_rates_async(), sync_rates_from_source(), Purity, Meta, get_current_rates() (+1 more)

### Community 44 - "devDependencies"
Cohesion: 0.17
Nodes (12): devDependencies, oxlint@^1.88.0, @playwright/test@^1.64.1, @types/node@^24.19.2, @types/react@^19.3.0, @types/react-dom@^19.3.0, typescript@~6.0.3, oxlint (+4 more)

### Community 45 - "DeveloperPortal.tsx"
Cohesion: 0.14
Nodes (20): PasswordPolicyChecklist(), PasswordPolicyChecklistProps, Login(), OverviewData, StoreUser, TenantItem, StaffManagementModal(), StaffManagementModalProps (+12 more)

### Community 48 - "bills_router.py"
Cohesion: 0.09
Nodes (4): IdempotencyRecord, Meta, generate_bill_token(), BackendAuthoritativePollingTestCase

### Community 49 - "auth_router.py"
Cohesion: 0.07
Nodes (23): decode_token(), change_own_password(), create_branch(), create_user(), get_branch(), get_current_user(), list_branches(), list_users() (+15 more)

### Community 51 - "pairing.py"
Cohesion: 0.06
Nodes (16): POSPairingSession, Meta, ScannedItemAudit, Meta, generate_pairing_qr_data_url(), get_lan_ip(), redeem_pairing_code(), start_pairing_session() (+8 more)

### Community 53 - "vite.config.ts"
Cohesion: 0.20
Nodes (8): @tailwindcss/vite@^4.3.3, vite@^8.3.4, @vitejs/plugin-basic-ssl@^2.3.0, @vitejs/plugin-react@^6.1.2, @tailwindcss/vite, vite, @vitejs/plugin-basic-ssl, @vitejs/plugin-react

### Community 58 - "MultiSourceGoldRateScraperTestCase"
Cohesion: 0.07
Nodes (8): BaseRateScraper, RateScrapeResult, BullionDeskScraper, IBJAScraper, KSJFScraper, get_scraper(), list_available_sources(), MultiSourceGoldRateScraperTestCase

### Community 62 - "User"
Cohesion: 0.22
Nodes (6): Branch, Meta, User, Role, DomainInline, Domain

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

### Community 69 - "Decimal"
Cohesion: 0.20
Nodes (6): Customer, Category, Meta, StockSummary, Meta, _write_csv_to_zip()

### Community 72 - "pos_pairing_router.py"
Cohesion: 0.15
Nodes (12): revoke_pairing_session(), mobile_scan_fallback(), _execute_scan(), redeem_pos_pairing_token(), revoke_pos_pairing_token(), start_pos_pairing_session(), MobileScanIn, RedeemPairingIn (+4 more)

### Community 74 - "Sale"
Cohesion: 0.11
Nodes (7): Sale, Meta, PaymentStatus, SaleStatus, create_sale(), _next_invoice_number(), InvoiceSnapshotImmutabilityTestCase

### Community 75 - "bills_router.py"
Cohesion: 0.11
Nodes (14): Bill, Meta, Status, not_found_handler(), permission_error_handler(), value_error_handler(), create_bill(), get_bill_cart() (+6 more)

### Community 77 - "AuthContext.tsx"
Cohesion: 0.67
Nodes (3): AuthContext, AuthContextType, User

### Community 79 - "App.tsx"
Cohesion: 0.20
Nodes (18): axios@^1.20.0, App(), FeatureRoute(), ProtectedRoute(), Layout(), AuthProvider(), useAuth(), AccountingDashboard() (+10 more)

### Community 84 - "billing/services.py"
Cohesion: 0.12
Nodes (6): InvoiceSetting, PaperSize, TemplateStyle, generate_invoice_pdf(), generate_invoice_pdf_async(), update_invoice_settings()

### Community 85 - "MobileQRScanner.tsx"
Cohesion: 0.19
Nodes (11): @zxing/browser@^0.2.1, @zxing/library@^0.23.0, beep(), isVideoReady(), makeReader(), MobileQRScanner(), startDecodeLoop(), MobileQRScannerProps (+3 more)

### Community 86 - "stock_router.py"
Cohesion: 0.22
Nodes (4): create_stock_movement(), StockMovementIn, StockMovementOut, StockSummaryOut

### Community 87 - "accounting_router.py"
Cohesion: 0.07
Nodes (23): fetch_live_market_rates_async(), close_day_book(), close_day_book_alias(), create_customer(), create_gold_rate(), _format_daybook(), get_customer(), get_live_market_rates() (+15 more)

### Community 89 - "Product"
Cohesion: 0.08
Nodes (5): Client, Meta, NinjaProductsStockTestCase, OldGoldValidationTestCase, TenantIsolationTestCase

### Community 90 - "react"
Cohesion: 0.30
Nodes (11): api, PosScannerConnectionModalProps, CustomerDirectoryModalProps, CustomerFormModal(), CustomerFormModalProps, CustomerSelectOrAddProps, ExportDataModalProps, Customer (+3 more)

### Community 93 - "ProductList.tsx"
Cohesion: 0.14
Nodes (20): CartItem, CameraCaptureModal(), CameraCaptureModalProps, ClubTrayModal(), ClubTrayModalProps, ProductFormModal(), ProductFormModalProps, SortField (+12 more)

### Community 94 - "react"
Cohesion: 0.20
Nodes (16): RateSource, InvoiceModal(), InvoiceModalProps, InvoiceSettingsModalProps, clean(), detectProductMetal(), MetalType, ResolvedMetalRate (+8 more)

### Community 96 - "download_invoice_pdf"
Cohesion: 0.25
Nodes (4): download_invoice_pdf(), download_invoice_pdf_underscore(), get_invoice_settings(), list_sales()

### Community 100 - "DayBook"
Cohesion: 0.12
Nodes (6): DayBookAdmin, DayBook, Meta, ProductAdmin, StockMovementAdmin, StockSummaryAdmin

## Knowledge Gaps
- **1 isolated node(s):** `swarna-khata-book`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 592 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **43 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Branch` connect `User` to `products_router.py`, `create_token`, `billing_router.py`, `tenants_router.py`, `DeveloperPortalTestCase`, `Purity`, `NinjaPOSBillingTestCase`, `bills_router.py`, `auth_router.py`, `InvoiceSettingsTestCase`, `NinjaAuthTestCase`, `DayBookAccountingTestCase`, `._post_product`, `MultiSourceGoldRateScraperTestCase`, `test_mobile_scanner.py`, `SecurityAuditAndAccessControlTestCase`, `TrayQRTagsTestCase`, `Decimal`, `Sale`, `DataExportTestCase`, `billing/services.py`, `accounting_router.py`, `Product`, `download_invoice_pdf`, `DayBook`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `Client` (e.g. with `export_tenant_data_to_zip()` and `generate_all_shops_export_archive()`) actually correct?**
  _`Client` has 30 INFERRED edges - model-reasoned connections that need verification._
- **What connects `swarna-khata-book` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `products_router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07926829268292683 - nodes in this community are weakly interconnected._
- **Why does `Product` connect `products_router.py` to `create_token`, `qr_tags_router.py`, `billing_router.py`, `tenants_router.py`, `NinjaPOSBillingTestCase`, `pairing.py`, `InvoiceSettingsTestCase`, `._post_product`, `test_mobile_scanner.py`, `SecurityAuditAndAccessControlTestCase`, `User`, `TrayQRTagsTestCase`, `export_tenant_data_to_zip`, `Decimal`, `Sale`, `DataExportTestCase`, `stock_router.py`, `Product`, `DayBook`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `User` (e.g. with `export_tenant_data_to_zip()` and `create_token()`) actually correct?**
  _`User` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Should `django_db` be split into smaller, more focused modules?**
  _Cohesion score 0.07254623044096728 - nodes in this community are weakly interconnected._