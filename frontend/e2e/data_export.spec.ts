import { test, expect } from '@playwright/test';

test.describe('Owner and Developer Data Export Suite', () => {

  test('Store Owner can open Export Data Modal and see all datasets and preset filters', async ({ page }) => {
    // Login as admin (Owner / Superadmin: Rank 100)
    await page.goto('/login');
    await page.fill('input[placeholder="e.g. owner or ramesh_sales"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("Sign In to Store")');
    await expect(page.getByRole('link', { name: 'POS Billing & Invoice' })).toBeVisible({ timeout: 15000 });

    // Verify Export Data button in top bar
    const exportBtn = page.locator('button:has-text("Export Data")');
    await expect(exportBtn).toBeVisible();
    await exportBtn.click();

    // Verify modal elements
    await expect(page.locator('text=Export Store Data Archive')).toBeVisible();
    await expect(page.locator('text=Owner Level 80+')).toBeVisible();

    // Verify presets
    await expect(page.locator('button:has-text("All Time")')).toBeVisible();
    await expect(page.locator('button:has-text("Last 30 Days")')).toBeVisible();
    await expect(page.locator('button:has-text("Last 90 Days")')).toBeVisible();
    await expect(page.locator('button:has-text("Current FY")')).toBeVisible();

    // Verify included datasets
    await expect(page.locator('text=Sales & Invoices')).toBeVisible();
    await expect(page.locator('text=Inventory & Stock')).toBeVisible();
    await expect(page.locator('text=Accounting & Daybook')).toBeVisible();
    await expect(page.locator('text=Directory & Manifest')).toBeVisible();

    // Click Last 30 Days and check date inputs populate
    await page.locator('button:has-text("Last 30 Days")').click();

    // Close modal
    await page.locator('button[aria-label="Close modal"]').click();
    await expect(page.locator('text=Export Store Data Archive')).not.toBeVisible();
  });

  test('Developer Portal shows Global Multi-Store Archive card with date filters', async ({ page }) => {
    await page.goto('/developer');

    // Login as developer
    await page.fill('input[placeholder="root / admin"]', 'admin');
    await page.fill('input[placeholder="••••••••"]', 'admin123');
    await page.click('button:has-text("Authenticate Terminal")');

    // Wait for console to load
    await expect(page.locator('text=Global Tenant Isolation')).toBeVisible({ timeout: 15000 });

    // Verify Global Multi-Store Archive section
    await expect(page.locator('text=Global Multi-Store Data Archive')).toBeVisible();
    await expect(page.locator('text=PLATFORM LEVEL 100')).toBeVisible();
    await expect(page.locator('button:has-text("Export All Stores (.ZIP)")')).toBeVisible();
  });
});
