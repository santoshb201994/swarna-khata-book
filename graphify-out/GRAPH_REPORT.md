# Graph Report - swarna_khata_book  (2026-10-31)

## Corpus Check
- 174 files · ~85,563 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .bat 3, .css 2)

## Summary
- 1386 nodes · 3218 edges · 98 communities (51 shown, 47 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 368 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `360e9365`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- products_router.py
- django_db
- MultiSourceGoldRateScraperTestCase
- qr_tags_router.py
- billing_router.py
- tenants_router.py
- middleware.py
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
- metalRateHelper.ts
- dependencies
- Domain
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
- ._post_product
- RateScrapeResult
- Product
- SecurityAuditAndAccessControlTestCase
- User
- TrayQRTagsTestCase
- billing/models.py
- export_tenant_data_to_zip
- @playwright/test
- logger.ts
- scripts
- pairing.py
- verify-before-complete.md
- jewellery_erp_coding_workflow_mindmap.md
- pos_pairing_router.py
- Item
- stock_router.py
- DataExportTestCase
- ShopRateSetting
- GoldRate
- Layout.tsx
- DayBook
- services
- CustomUserAdmin
- POSPairingSession
- billing/services.py
- MobileQRScanner.tsx
- accounting_router.py
- InvoiceSetting
- Product
- JWTAuth
- Purity
- ScannedItemAudit
- ProductList.tsx
- react
- stock/admin.py
- ClientAdmin
- AuthContext.tsx

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
- `sync_rates_from_source()` --uses--> `GoldRate`  [INFERRED]
  backend/apps/accounting/services.py → backend/apps/accounting/models.py
- `export_tenant_data_to_zip()` --uses--> `GoldRate`  [INFERRED]
  backend/apps/tenants/export_service.py → backend/apps/accounting/models.py
- `create_gold_rate()` --uses--> `GoldRate`  [INFERRED]
  backend/ninja_api/routers/accounting_router.py → backend/apps/accounting/models.py
- `get_current_rates()` --uses--> `GoldRate`  [INFERRED]
  backend/ninja_api/routers/accounting_router.py → backend/apps/accounting/models.py
- `list_gold_rates_history()` --uses--> `GoldRate`  [INFERRED]
  backend/ninja_api/routers/accounting_router.py → backend/apps/accounting/models.py

## Import Cycles
- None detected.

## Communities (98 total, 47 thin omitted)

### Community 0 - "products_router.py"
Cohesion: 0.10
Nodes (18): _threaded_qr(), generate_qr_for_product(), create_category(), create_product(), create_purity(), delete_product(), _format_product(), get_product() (+10 more)

### Community 1 - "django_db"
Cohesion: 0.07
Nodes (15): Migration, Migration, Migration, Migration, Migration, Migration, Migration, Migration (+7 more)

### Community 3 - "qr_tags_router.py"
Cohesion: 0.08
Nodes (24): QRTag, Meta, Tray, Meta, generate_qr_batch_async(), generate_qr_for_tray(), batch_generate_tags(), create_tray() (+16 more)

### Community 4 - "billing_router.py"
Cohesion: 0.12
Nodes (15): Sale, Meta, PaymentStatus, SaleStatus, _next_invoice_number(), add_sale_payment(), cancel_sale(), create_sale_invoice() (+7 more)

### Community 5 - "tenants_router.py"
Cohesion: 0.13
Nodes (15): require_role(), reset_staff_password(), create_tenant(), developer_login(), developer_overview(), developer_reset_user_password(), developer_switch_store_token(), developer_toggle_user_status() (+7 more)

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
Cohesion: 0.09
Nodes (37): scan_item_into_bill(), AddPaymentIn, BillCreateResponse, BillDetailResponse, CategoryOut, CloseDayIn, CustomerOut, DayBookOut (+29 more)

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

### Community 39 - "metalRateHelper.ts"
Cohesion: 0.43
Nodes (6): clean(), detectProductMetal(), MetalType, ResolvedMetalRate, resolveProductRate(), GoldRate

### Community 40 - "dependencies"
Cohesion: 0.09
Nodes (28): dependencies, @hookform/resolvers@^6.0.0, html5-qrcode@^2.3.8, lucide-react@^1.61.0, qrcode@^1.5.4, react@^19.3.1, react-dom@^19.3.1, react-hook-form@^7.90.0 (+20 more)

### Community 43 - "Domain"
Cohesion: 0.15
Nodes (3): DomainInline, Domain, TenantIsolationTestCase

### Community 44 - "devDependencies"
Cohesion: 0.17
Nodes (12): devDependencies, oxlint@^1.88.0, @playwright/test@^1.64.1, @types/node@^24.19.2, @types/react@^19.3.0, @types/react-dom@^19.3.0, typescript@~6.0.3, oxlint (+4 more)

### Community 45 - "App.tsx"
Cohesion: 0.20
Nodes (15): PasswordPolicyChecklist(), PasswordPolicyChecklistProps, useAuth(), Login(), DeveloperPortal(), OverviewData, StoreUser, TenantItem (+7 more)

### Community 48 - "bills_router.py"
Cohesion: 0.07
Nodes (9): Bill, Meta, Status, IdempotencyRecord, Meta, generate_bill_token(), create_bill(), get_bill_cart() (+1 more)

### Community 49 - "auth_router.py"
Cohesion: 0.08
Nodes (21): decode_token(), change_own_password(), create_branch(), create_user(), get_branch(), get_current_user(), list_branches(), list_users() (+13 more)

### Community 51 - "websocket_handler.py"
Cohesion: 0.20
Nodes (7): get_active_session(), mobile_websocket_app(), parse_query_string(), pos_websocket_app(), send_json(), validate_jwt_user(), application()

### Community 53 - "vite.config.ts"
Cohesion: 0.20
Nodes (8): @tailwindcss/vite@^4.3.3, vite@^8.3.4, @vitejs/plugin-basic-ssl@^2.3.0, @vitejs/plugin-react@^6.1.2, @tailwindcss/vite, vite, @vitejs/plugin-basic-ssl, @vitejs/plugin-react

### Community 54 - "create_token"
Cohesion: 0.11
Nodes (3): create_token(), DeveloperPortalTestCase, StoreOnboardingAndRBACTestCase

### Community 58 - "RateScrapeResult"
Cohesion: 0.17
Nodes (4): BaseRateScraper, RateScrapeResult, BullionDeskScraper, IBJAScraper

### Community 59 - "Product"
Cohesion: 0.29
Nodes (4): ProductFilter, Meta, Product, Meta

### Community 62 - "User"
Cohesion: 0.17
Nodes (9): Customer, Branch, Meta, User, Role, Category, Meta, StockSummary (+1 more)

### Community 64 - "billing/models.py"
Cohesion: 0.25
Nodes (6): PaymentInline, SaleAdmin, SaleItemInline, Payment, PaymentMethod, SaleItem

### Community 65 - "export_tenant_data_to_zip"
Cohesion: 0.11
Nodes (4): export_tenant_data_to_zip(), generate_all_shops_export_archive(), generate_shop_export_archive(), _write_csv_to_zip()

### Community 67 - "logger.ts"
Cohesion: 0.13
Nodes (7): ErrorBoundary, Props, State, logBuffer, LogEntry, logger, LogLevel

### Community 68 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, lint, preview, test:e2e, tunnel

### Community 69 - "pairing.py"
Cohesion: 0.21
Nodes (4): generate_pairing_qr_data_url(), get_lan_ip(), start_pairing_session(), verify_mobile_token()

### Community 72 - "pos_pairing_router.py"
Cohesion: 0.18
Nodes (8): redeem_pairing_code(), revoke_pairing_session(), redeem_pos_pairing_token(), revoke_pos_pairing_token(), start_pos_pairing_session(), RedeemPairingIn, RevokePairingIn, StartPairingIn

### Community 74 - "Item"
Cohesion: 0.12
Nodes (6): Item, Meta, Status, create_sale(), generate_invoice_pdf(), generate_invoice_pdf_async()

### Community 75 - "stock_router.py"
Cohesion: 0.10
Nodes (11): CleanupFile, not_found_handler(), permission_error_handler(), value_error_handler(), export_all_shops_data(), export_shop_data(), _parse_date(), create_stock_movement() (+3 more)

### Community 77 - "ShopRateSetting"
Cohesion: 0.18
Nodes (5): ShopRateSetting, get_scraper(), list_available_sources(), sync_rates_from_source(), get_rate_sources()

### Community 78 - "GoldRate"
Cohesion: 0.19
Nodes (4): GoldRate, Meta, fetch_live_market_rates_async(), sync_live_rates_async()

### Community 79 - "Layout.tsx"
Cohesion: 0.18
Nodes (16): App(), FeatureRoute(), ProtectedRoute(), Layout(), AuthProvider(), InvoiceSettingsModal(), CustomerDirectoryModal(), ExportDataModal() (+8 more)

### Community 80 - "DayBook"
Cohesion: 0.15
Nodes (4): DayBookAdmin, DayBook, Meta, ProductAdmin

### Community 81 - "services"
Cohesion: 0.15
Nodes (12): generateValue, key, sync, value, services, buildCommand, envVars, healthCheckPath (+4 more)

### Community 83 - "POSPairingSession"
Cohesion: 0.18
Nodes (6): POSPairingSession, Meta, resolve_and_record_scan(), mobile_scan_fallback(), _execute_scan(), MobileScanIn

### Community 84 - "billing/services.py"
Cohesion: 0.19
Nodes (4): StockMovement, Meta, MovementType, record_stock_movement()

### Community 85 - "MobileQRScanner.tsx"
Cohesion: 0.14
Nodes (15): axios@^1.20.0, react-router-dom@^7.18.4, @zxing/browser@^0.2.1, beep(), isVideoReady(), makeReader(), MobileQRScanner(), startDecodeLoop() (+7 more)

### Community 87 - "accounting_router.py"
Cohesion: 0.07
Nodes (27): close_day_book(), close_day_book_alias(), create_customer(), create_gold_rate(), _format_daybook(), get_current_rates(), get_customer(), get_live_market_rates() (+19 more)

### Community 88 - "InvoiceSetting"
Cohesion: 0.25
Nodes (4): InvoiceSetting, PaperSize, TemplateStyle, update_invoice_settings()

### Community 89 - "Product"
Cohesion: 0.06
Nodes (6): Client, Meta, InvoiceSnapshotImmutabilityTestCase, NinjaProductsStockTestCase, CustomerEmailValidationTestCase, OldGoldValidationTestCase

### Community 91 - "Purity"
Cohesion: 0.33
Nodes (3): Purity, Meta, register_store()

### Community 93 - "ProductList.tsx"
Cohesion: 0.15
Nodes (21): CartItem, CameraCaptureModal(), CameraCaptureModalProps, ClubTrayModal(), ClubTrayModalProps, ProductFormModal(), ProductFormModalProps, ProductList() (+13 more)

### Community 94 - "react"
Cohesion: 0.20
Nodes (22): api, AccountingDashboard(), RateSource, InvoiceModal(), InvoiceModalProps, InvoiceSettingsModalProps, PosScannerConnectionModal(), PosScannerConnectionModalProps (+14 more)

### Community 97 - "AuthContext.tsx"
Cohesion: 0.67
Nodes (3): AuthContext, AuthContextType, User

## Knowledge Gaps
- **1 isolated node(s):** `swarna-khata-book`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 605 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **47 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Branch` connect `User` to `products_router.py`, `MultiSourceGoldRateScraperTestCase`, `billing_router.py`, `tenants_router.py`, `NinjaPOSBillingTestCase`, `bills_router.py`, `auth_router.py`, `NinjaAuthTestCase`, `InvoiceSettingsTestCase`, `create_token`, `DayBookAccountingTestCase`, `._post_product`, `SecurityAuditAndAccessControlTestCase`, `TrayQRTagsTestCase`, `DataExportTestCase`, `ShopRateSetting`, `GoldRate`, `DayBook`, `accounting_router.py`, `InvoiceSetting`, `Product`, `Purity`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `Client` (e.g. with `export_tenant_data_to_zip()` and `generate_all_shops_export_archive()`) actually correct?**
  _`Client` has 30 INFERRED edges - model-reasoned connections that need verification._
- **What connects `swarna-khata-book` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `products_router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10080645161290322 - nodes in this community are weakly interconnected._
- **Why does `Product` connect `Product` to `products_router.py`, `qr_tags_router.py`, `billing_router.py`, `tenants_router.py`, `Domain`, `NinjaPOSBillingTestCase`, `InvoiceSettingsTestCase`, `create_token`, `._post_product`, `SecurityAuditAndAccessControlTestCase`, `User`, `TrayQRTagsTestCase`, `export_tenant_data_to_zip`, `pairing.py`, `stock_router.py`, `DataExportTestCase`, `DayBook`, `POSPairingSession`, `Product`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `User` (e.g. with `export_tenant_data_to_zip()` and `create_token()`) actually correct?**
  _`User` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Should `django_db` be split into smaller, more focused modules?**
  _Cohesion score 0.07254623044096728 - nodes in this community are weakly interconnected._