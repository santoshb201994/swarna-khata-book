import { test, expect } from '@playwright/test';

test.describe('RBAC Hierarchy Verification for Internal Webapp Features', () => {

  test.beforeEach(async ({ page }) => {
    // Login as admin (Owner / Superadmin: Rank 100)
    await page.goto('/login');
    await page.fill('input[placeholder="e.g. owner or ramesh_sales"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("Sign In to Store")');
    await expect(page.getByRole('link', { name: 'POS Billing & Invoice' })).toBeVisible({ timeout: 15000 });
  });

  test('Store Owner / Superadmin has access to full feature hierarchy', async ({ page }) => {
    // 1. Header controls check
    await expect(page.locator('button:has-text("Customers")')).toBeVisible();
    await expect(page.locator('button:has-text("Staff")')).toBeVisible();
    await expect(page.locator('button:has-text("Bill & Invoice Studio")')).toBeVisible();

    // 2. Navigation tabs check
    await expect(page.getByRole('link', { name: 'POS Billing & Invoice' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Items & QR Tags' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Accounting & Day Book' })).toBeVisible();

    // 3. Products page check (Add Jewelry Item button visible for rank >= 60)
    await page.getByRole('link', { name: 'Items & QR Tags' }).click();
    await expect(page.locator('h1:has-text("Inventory, Items & QR Tags")')).toBeVisible();
    await expect(page.locator('button:has-text("Add Jewelry Item")')).toBeVisible();

    // 4. Accounting page check (Close Day, Auto-Sync, and Rate Update visible for rank >= 60)
    await page.getByRole('link', { name: 'Accounting & Day Book' }).click();
    await expect(page.locator('h1:has-text("Accounting & Day Book")')).toBeVisible();
    await expect(page.locator('button:has-text("Auto-Sync")')).toBeVisible();
    await expect(page.locator('button:has-text("Update Rate")')).toBeVisible();
    await expect(page.locator('button:has-text("Record in Day Book")')).toBeVisible();
  });

  test('Staff modal role options strictly enforce downward hierarchy', async ({ page }) => {
    // Open staff modal
    const staffBtn = page.locator('button:has-text("Staff")');
    await expect(staffBtn).toBeVisible();
    await staffBtn.click();

    const addTab = page.locator('button:has-text("Add New Salesman / Staff")');
    await expect(addTab).toBeVisible();
    await addTab.click();

    // Role select options should include all subordinate roles for superadmin
    const roleSelect = page.locator('label:has-text("Role *") + select, div:has(> label:has-text("Role *")) select');
    await expect(roleSelect).toBeVisible({ timeout: 10000 });
    const options = await roleSelect.locator('option').allInnerTexts();
    expect(options.some(o => o.includes('Salesman'))).toBe(true);
    expect(options.some(o => o.includes('Manager'))).toBe(true);
    expect(options.some(o => o.includes('Accountant'))).toBe(true);
  });

  test('Invoice Studio modal opens for Owner / Superadmin', async ({ page }) => {
    await page.locator('button:has-text("Bill & Invoice Studio")').click();
    await expect(page.locator('text=Invoice Customization & Branding Studio')).toBeVisible();
    await expect(page.locator('text=Owner Control')).toBeVisible();
    await page.click('button:has(svg.lucide-x), button[aria-label="Close"]');
  });
});
