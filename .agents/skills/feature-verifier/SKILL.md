---
name: feature-verifier
description: Comprehensive feature verification and regression testing runbook for Swarna Khata Book. Use this skill whenever code is updated, before finishing any user request, or when asked to verify feature statuses or health.
---

# Feature Verifier Skill

This skill executes full-stack regression verification across backend APIs, frontend TypeScript builds, and Playwright browser E2E workflows. It verifies that new changes have not broken existing working features.

## When to Run
1. After adding or modifying any backend route, model, middleware, or service.
2. After updating any frontend page, component, or store.
3. Before declaring any user task or feature complete.
4. When the user asks for a system health check or feature status check.

## Verification Pipeline

Execute the automated verification script:

```powershell
.\scripts\verify_all_features.ps1
```

Or run individual tiers:

### Tier 1: Frontend Type & Build Verification
```powershell
npm --prefix frontend run build
npm --prefix frontend run lint
```
Checks for TypeScript compilation errors, broken imports, missing types, and syntax errors.

### Tier 2: Backend Regression Test Suite
```powershell
uv run --directory backend python manage.py test tests --keepdb -v 1
```
Runs 60+ unit & integration tests covering multi-tenant schema isolation, POS billing, daybook accounting, developer portal, scraper, and authentication.

### Tier 3: Browser E2E Smoke Tests (Playwright)
```powershell
npm --prefix frontend run test:e2e
```
Runs headless browser tests validating the golden paths:
- Store login & domain resolution
- Developer portal route isolation (`/developer`)
- Gold rate board display
- POS billing & mobile pairing modal

## Feature Health Matrix Reporting

After running tests, report the feature status using the checklist in [feature_checklist.md](./references/feature_checklist.md):

| Feature Area | Status | Test Component | Notes |
| :--- | :---: | :--- | :--- |
| **Store Authentication & RBAC** | ✅ / ❌ | `test_store_onboarding_and_rbac.py` | Owner, staff, password policy |
| **Developer Portal** | ✅ / ❌ | `test_developer_portal.py` | `/developer` cross-tenant tools |
| **Live Gold Rate Scraper** | ✅ / ❌ | `test_multi_source_scraper.py` | Sync without async ORM errors |
| **POS Billing & Invoice** | ✅ / ❌ | `test_ninja_pos_billing.py` | Multi-mode settlement |
| **Products & QR Stock** | ✅ / ❌ | `test_ninja_products_stock.py` | Weight, purity, barcode lookup |
| **Mobile Pairing Session** | ✅ / ❌ | `test_backend_authoritative_polling.py` | Polling, 12h expiry |
| **Daybook Accounting** | ✅ / ❌ | `test_daybook_accounting.py` | Financial balance integrity |
| **Frontend TypeScript Build** | ✅ / ❌ | `npm run build` | Zero compile errors |
| **Browser E2E Smoke Tests** | ✅ / ❌ | `npm run test:e2e` | Headless Chrome navigation |

If any tier fails, immediately diagnose the failure, fix the regression, and re-run the verification pipeline before reporting back to the user.
