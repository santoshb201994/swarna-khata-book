# Graph Report - swarna_khata_book  (2026-11-01)

## Corpus Check
- 183 files · ~90,239 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .bat 3, .css 2)

## Summary
- 1446 nodes · 3361 edges · 104 communities (54 shown, 50 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 383 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `519a3df7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- list_products
- OldGoldValidationTestCase
- MultiSourceGoldRateScraperTestCase
- qr_tags_router.py
- Client
- Client
- TrayQRTagsTestCase
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
- create_sale
- index.ts
- index.ts
- dependencies
- POSSessionHub
- devDependencies
- Layout.tsx
- NinjaPOSBillingTestCase
- bills_router.py
- auth_router.py
- ShopRateSetting
- pos_pairing_router.py
- InvoiceSettingsTestCase
- vite.config.ts
- create_token
- render-build.sh
- DayBookAccountingTestCase
- post
- django_db
- pairing.py
- SecurityAuditAndAccessControlTestCase
- User
- ._post_product
- StockSummary
- export_tenant_data_to_zip
- @playwright/test
- logger.ts
- scripts
- billing/models.py
- verify-before-complete.md
- jewellery_erp_coding_workflow_mindmap.md
- Sale
- UnifiedQRArchitectureTestCase
- DataExportTestCase
- get
- Purity
- DeveloperPortal.tsx
- JWTAuth
- services
- CustomUserAdmin
- billing_router.py
- accounting/services.py
- MobileScannerPage.tsx
- qrPayload.ts
- DayBook
- vercel.json
- Product
- download_invoice_pdf
- start.sh
- require_role
- react
- sync_rates_from_source
- accounts/migrations/0001_initial.py
- tenants/admin.py
- stock_router.py
- tenants/admin.py
- ClientAdmin
- bills_router.py
- middleware.py
- MobileScannerPage.tsx

## God Nodes (most connected - your core abstractions)
1. `Client` - 73 edges
2. `create_token()` - 63 edges
3. `User` - 59 edges
4. `Branch` - 59 edges
5. `Product` - 59 edges
6. `Purity` - 48 edges
7. `Domain` - 44 edges
8. `require_role()` - 42 edges
9. `Category` - 37 edges
10. `StockSummary` - 31 edges

## Surprising Connections (you probably didn't know these)
- `DomainInline` --uses--> `Domain`  [INFERRED]
  backend/apps/tenants/admin.py → backend/apps/tenants/models.py
- `sync_rates_from_source()` --uses--> `GoldRate`  [INFERRED]
  backend/apps/accounting/services.py → backend/apps/accounting/models.py
- `export_tenant_data_to_zip()` --uses--> `GoldRate`  [INFERRED]
  backend/apps/tenants/export_service.py → backend/apps/accounting/models.py
- `create_gold_rate()` --uses--> `GoldRate`  [INFERRED]
  backend/ninja_api/routers/accounting_router.py → backend/apps/accounting/models.py
- `get_current_rates()` --uses--> `GoldRate`  [INFERRED]
  backend/ninja_api/routers/accounting_router.py → backend/apps/accounting/models.py

## Import Cycles
- None detected.

## Communities (104 total, 50 thin omitted)

### Community 0 - "list_products"
Cohesion: 0.33
Nodes (4): get_product(), list_categories(), list_products(), list_purities()

### Community 2 - "MultiSourceGoldRateScraperTestCase"
Cohesion: 0.07
Nodes (8): BaseRateScraper, RateScrapeResult, BullionDeskScraper, IBJAScraper, KSJFScraper, get_scraper(), list_available_sources(), MultiSourceGoldRateScraperTestCase

### Community 3 - "qr_tags_router.py"
Cohesion: 0.05
Nodes (32): QRTag, Meta, Tray, Meta, generate_qr_batch_async(), _threaded_qr(), generate_qr_for_product(), generate_qr_for_tray() (+24 more)

### Community 4 - "Client"
Cohesion: 0.09
Nodes (5): Client, Meta, InvoiceSnapshotImmutabilityTestCase, NinjaProductsStockTestCase, TenantIsolationTestCase

### Community 5 - "Client"
Cohesion: 0.12
Nodes (15): create_tenant(), developer_login(), developer_reset_user_password(), developer_switch_store_token(), developer_toggle_user_status(), _format_tenant(), list_tenants(), toggle_tenant_status() (+7 more)

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
Cohesion: 0.12
Nodes (32): create_category(), create_purity(), CashEntryIn, CategoryIn, CategoryOut, CloseDayIn, CustomerIn, CustomerOut (+24 more)

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

### Community 37 - "create_sale"
Cohesion: 0.10
Nodes (6): InvoiceSetting, PaperSize, TemplateStyle, create_sale(), generate_invoice_pdf(), generate_invoice_pdf_async()

### Community 38 - "index.ts"
Cohesion: 0.28
Nodes (10): CameraCaptureModal(), CameraCaptureModalProps, ClubTrayModal(), ProductFormModal(), ProductFormModalProps, ProductList(), SortField, TrayQRTagModal() (+2 more)

### Community 39 - "index.ts"
Cohesion: 0.14
Nodes (21): AccountingDashboard(), RateSource, InvoiceModal(), InvoiceModalProps, InvoiceSettingsModalProps, clean(), detectProductMetal(), MetalType (+13 more)

### Community 40 - "dependencies"
Cohesion: 0.09
Nodes (29): dependencies, axios@^1.20.0, @hookform/resolvers@^6.0.0, html5-qrcode@^2.3.8, lucide-react@^1.61.0, qrcode@^1.5.4, react@^19.3.1, react-dom@^19.3.1 (+21 more)

### Community 44 - "devDependencies"
Cohesion: 0.17
Nodes (12): devDependencies, oxlint@^1.88.0, @playwright/test@^1.64.1, @types/node@^24.19.2, @types/react@^19.3.0, @types/react-dom@^19.3.0, typescript@~6.0.3, oxlint (+4 more)

### Community 45 - "Layout.tsx"
Cohesion: 0.21
Nodes (14): Layout(), InvoiceSettingsModal(), CustomerDirectoryModal(), ExportDataModal(), StaffManagementModal(), StaffManagementModalProps, UserItem, canAccessFeature() (+6 more)

### Community 48 - "bills_router.py"
Cohesion: 0.09
Nodes (4): IdempotencyRecord, Meta, generate_bill_token(), BackendAuthoritativePollingTestCase

### Community 49 - "auth_router.py"
Cohesion: 0.07
Nodes (21): decode_token(), change_own_password(), create_branch(), create_user(), get_branch(), get_current_user(), list_branches(), list_users() (+13 more)

### Community 50 - "ShopRateSetting"
Cohesion: 0.29
Nodes (3): ShopRateSetting, update_customer(), update_rate_settings()

### Community 51 - "pos_pairing_router.py"
Cohesion: 0.06
Nodes (24): POSPairingSession, Meta, ScannedItemAudit, Meta, redeem_pairing_code(), resolve_and_record_scan(), revoke_pairing_session(), verify_mobile_token() (+16 more)

### Community 53 - "vite.config.ts"
Cohesion: 0.20
Nodes (8): @tailwindcss/vite@^4.3.3, vite@^8.3.4, @vitejs/plugin-basic-ssl@^2.3.0, @vitejs/plugin-react@^6.1.2, @tailwindcss/vite, vite, @vitejs/plugin-basic-ssl, @vitejs/plugin-react

### Community 54 - "create_token"
Cohesion: 0.06
Nodes (4): create_token(), DeveloperPortalTestCase, NinjaAuthTestCase, StoreOnboardingAndRBACTestCase

### Community 57 - "post"
Cohesion: 0.20
Nodes (6): close_day_book(), close_day_book_alias(), create_customer(), _perform_close_day_book(), reopen_day_book(), reopen_day_book_alias()

### Community 58 - "django_db"
Cohesion: 0.07
Nodes (16): Migration, Migration, Migration, Migration, Migration, Migration, Migration, Migration (+8 more)

### Community 59 - "pairing.py"
Cohesion: 0.27
Nodes (3): generate_pairing_qr_data_url(), get_lan_ip(), start_pairing_session()

### Community 62 - "User"
Cohesion: 0.20
Nodes (8): Customer, Branch, Meta, User, Role, Category, Meta, Domain

### Community 64 - "StockSummary"
Cohesion: 0.13
Nodes (9): StockMovementAdmin, StockSummaryAdmin, StockMovement, Meta, MovementType, StockSummary, Meta, list_stock_movements() (+1 more)

### Community 65 - "export_tenant_data_to_zip"
Cohesion: 0.07
Nodes (8): CleanupFile, export_tenant_data_to_zip(), generate_all_shops_export_archive(), generate_shop_export_archive(), _write_csv_to_zip(), export_all_shops_data(), export_shop_data(), _parse_date()

### Community 67 - "logger.ts"
Cohesion: 0.13
Nodes (7): ErrorBoundary, Props, State, logBuffer, LogEntry, logger, LogLevel

### Community 68 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, lint, preview, test:e2e, tunnel

### Community 69 - "billing/models.py"
Cohesion: 0.24
Nodes (6): PaymentInline, SaleAdmin, SaleItemInline, Payment, PaymentMethod, SaleItem

### Community 72 - "Sale"
Cohesion: 0.13
Nodes (12): Sale, Meta, PaymentStatus, SaleStatus, _next_invoice_number(), record_stock_movement(), add_sale_payment(), cancel_sale() (+4 more)

### Community 77 - "get"
Cohesion: 0.17
Nodes (7): get_current_rates(), get_customer(), get_live_market_rates(), get_rate_settings(), get_rate_sources(), list_customers(), list_gold_rates_history()

### Community 78 - "Purity"
Cohesion: 0.33
Nodes (3): Purity, Meta, register_store()

### Community 79 - "DeveloperPortal.tsx"
Cohesion: 0.16
Nodes (20): App(), FeatureRoute(), ProtectedRoute(), PasswordPolicyChecklist(), PasswordPolicyChecklistProps, AuthContext, AuthContextType, AuthProvider() (+12 more)

### Community 81 - "services"
Cohesion: 0.14
Nodes (13): generateValue, key, sync, value, services, autoDeployTrigger, buildCommand, envVars (+5 more)

### Community 83 - "billing_router.py"
Cohesion: 0.11
Nodes (15): get_item_by_qr(), _resolve_item_by_token(), update_invoice_settings(), verify_physical_tag(), AddPaymentIn, InvoiceSettingOut, InvoiceSettingUpdateIn, PaymentOut (+7 more)

### Community 84 - "accounting/services.py"
Cohesion: 0.19
Nodes (4): GoldRate, Meta, fetch_live_market_rates_async(), sync_live_rates_async()

### Community 85 - "MobileScannerPage.tsx"
Cohesion: 0.48
Nodes (5): MobileScannerPage(), ScannedHistoryItem, getApiBaseUrl(), getWsBaseUrl(), react-router-dom

### Community 86 - "qrPayload.ts"
Cohesion: 0.22
Nodes (15): CartItem, BulkQRPrintModal(), BulkQRPrintModalProps, TagItemWithQR, QRTagModal(), QRTagModalProps, Product, generateQRDataUrl() (+7 more)

### Community 87 - "DayBook"
Cohesion: 0.19
Nodes (7): DayBook, Meta, _format_daybook(), get_today_day_book(), list_day_books(), record_petty_cash_entry(), update_day_book_cash()

### Community 89 - "Product"
Cohesion: 0.22
Nodes (5): ProductFilter, Meta, Product, Meta, developer_overview()

### Community 90 - "download_invoice_pdf"
Cohesion: 0.25
Nodes (4): download_invoice_pdf(), download_invoice_pdf_underscore(), get_invoice_settings(), list_sales()

### Community 92 - "require_role"
Cohesion: 0.29
Nodes (3): require_role(), create_gold_rate(), delete_product()

### Community 93 - "react"
Cohesion: 0.23
Nodes (16): api, PosScannerConnectionModal(), PosScannerConnectionModalProps, CustomerDirectoryModalProps, CustomerFormModal(), CustomerFormModalProps, CustomerSelectOrAdd(), CustomerSelectOrAddProps (+8 more)

### Community 97 - "stock_router.py"
Cohesion: 0.16
Nodes (7): not_found_handler(), permission_error_handler(), value_error_handler(), create_stock_movement(), StockMovementIn, StockMovementOut, StockSummaryOut

### Community 98 - "tenants/admin.py"
Cohesion: 0.17
Nodes (3): DayBookAdmin, ProductAdmin, DomainInline

### Community 100 - "bills_router.py"
Cohesion: 0.12
Nodes (14): Bill, Meta, Status, Item, Meta, Status, create_bill(), get_bill_cart() (+6 more)

### Community 102 - "MobileScannerPage.tsx"
Cohesion: 0.19
Nodes (11): @zxing/browser@^0.2.1, @zxing/library@^0.23.0, beep(), isVideoReady(), makeReader(), MobileQRScanner(), startDecodeLoop(), MobileQRScannerProps (+3 more)

## Knowledge Gaps
- **1 isolated node(s):** `swarna-khata-book`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 632 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **50 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Branch` connect `User` to `OldGoldValidationTestCase`, `MultiSourceGoldRateScraperTestCase`, `qr_tags_router.py`, `Client`, `Client`, `TrayQRTagsTestCase`, `schemas.py`, `NinjaPOSBillingTestCase`, `bills_router.py`, `auth_router.py`, `InvoiceSettingsTestCase`, `create_token`, `DayBookAccountingTestCase`, `SecurityAuditAndAccessControlTestCase`, `._post_product`, `Sale`, `UnifiedQRArchitectureTestCase`, `DataExportTestCase`, `get`, `Purity`, `billing_router.py`, `accounting/services.py`, `Product`, `download_invoice_pdf`, `sync_rates_from_source`, `tenants/admin.py`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Are the 31 inferred relationships involving `Client` (e.g. with `export_tenant_data_to_zip()` and `generate_all_shops_export_archive()`) actually correct?**
  _`Client` has 31 INFERRED edges - model-reasoned connections that need verification._
- **What connects `swarna-khata-book` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `OldGoldValidationTestCase` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `Client` connect `Client` to `OldGoldValidationTestCase`, `MultiSourceGoldRateScraperTestCase`, `Client`, `TrayQRTagsTestCase`, `validate_password_policy`, `NinjaPOSBillingTestCase`, `bills_router.py`, `auth_router.py`, `InvoiceSettingsTestCase`, `create_token`, `DayBookAccountingTestCase`, `SecurityAuditAndAccessControlTestCase`, `User`, `._post_product`, `export_tenant_data_to_zip`, `UnifiedQRArchitectureTestCase`, `DataExportTestCase`, `Purity`, `Product`, `tenants/admin.py`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Are the 31 inferred relationships involving `User` (e.g. with `export_tenant_data_to_zip()` and `create_token()`) actually correct?**
  _`User` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Should `MultiSourceGoldRateScraperTestCase` be split into smaller, more focused modules?**
  _Cohesion score 0.06821480406386067 - nodes in this community are weakly interconnected._