import { test, expect } from '@playwright/test';

/**
 * POS Screen UX E2E Tests
 *
 * Covers UX fixes applied to POSScreen:
 * - Checkout button ("Complete Sale & Save") is disabled when cart is empty
 * - Catalog shows empty state when no items match search
 * - Old gold weight input has min="0" (no negative values)
 * - POS catalog panel renders products or inventory state
 */
test.describe('POS Screen UX Validation', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder="e.g. owner or ramesh_sales"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("Sign In to Store")');
    await expect(page.getByRole('link', { name: 'POS Billing & Invoice' })).toBeVisible({ timeout: 15000 });
    await expect(page.locator('h1').filter({ hasText: 'POS Billing & Invoice' })).toBeVisible({ timeout: 10000 });
  });

  test('Checkout button is disabled when cart is empty', async ({ page }) => {
    const checkoutBtn = page.locator('button:has-text("Complete Sale & Save")');
    await expect(checkoutBtn).toBeVisible({ timeout: 10000 });
    await expect(checkoutBtn).toBeDisabled();
  });

  test('Catalog shows empty state message when search finds no items', async ({ page }) => {
    const searchInput = page.locator('input[placeholder="Type SKU or product name to add..."]');
    await expect(searchInput).toBeVisible({ timeout: 10000 });
    await searchInput.fill('XYZNOSUCHJEWELITEM99999');

    await expect(page.locator('text=No items match')).toBeVisible({ timeout: 8000 });
  });

  test('Old gold weight input has min="0" preventing negative values', async ({ page }) => {
    const weightInput = page.locator('div:has(> label:has-text("Old Gold Wt (g)")) input');
    await expect(weightInput).toBeVisible({ timeout: 8000 });
    await expect(weightInput).toHaveAttribute('min', '0');
  });

  test('POS catalog panel renders available product cards on load', async ({ page }) => {
    const addButtons = page.locator('button[title="Add to Bill"]');
    await expect(addButtons.first()).toBeVisible({ timeout: 10000 });
    const count = await addButtons.count();
    expect(count).toBeGreaterThan(0);
  });

});
