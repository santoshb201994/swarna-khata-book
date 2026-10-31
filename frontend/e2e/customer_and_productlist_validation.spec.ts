import { test, expect } from '@playwright/test';

/**
 * Customer & ProductList Validation E2E Tests
 *
 * Covers fixes applied to:
 * - CustomerFormModal: email format validation (client-side)
 * - CustomerDirectoryModal: empty state when search finds nothing
 * - ProductList: weight filter error when min > max
 * - ProductList: distinct empty states for "no items matched your filters"
 * - ProductList: loading indicator rendering
 */
test.describe('Customer Form Email Validation', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder="e.g. owner or ramesh_sales"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("Sign In to Store")');
    await expect(page.getByRole('link', { name: 'POS Billing & Invoice' })).toBeVisible({ timeout: 15000 });
  });

  test('Customer form shows error toast for invalid email format', async ({ page }) => {
    // Open customer directory modal via Customers button in header
    await page.locator('button:has-text("Customers")').click();
    await expect(page.locator('h2:has-text("Customer Khata Directory")')).toBeVisible({ timeout: 8000 });

    // Click Add New Customer inside the directory modal
    await page.locator('button:has-text("Add New Customer")').click();
    await expect(page.locator('input[placeholder="e.g. Ramesh Patil"]')).toBeVisible({ timeout: 8000 });

    // Fill name and phone (required)
    await page.locator('input[placeholder="e.g. Ramesh Patil"]').fill('Test Customer');
    await page.locator('input[placeholder*="10-digit mobile"]').fill('9000000001');

    // Fill invalid email
    await page.locator('input[type="email"]').fill('notanemail');

    // Submit form
    await page.locator('button[type="submit"]:has-text("Save & Select Customer")').click();

    // Should show email validation error toast
    await expect(page.locator('text=Please enter a valid email address')).toBeVisible({ timeout: 5000 });
  });

  test('Customer directory shows empty state for no-match search', async ({ page }) => {
    await page.locator('button:has-text("Customers")').click();
    await expect(page.locator('h2:has-text("Customer Khata Directory")')).toBeVisible({ timeout: 8000 });

    // Use search input inside the Customer Directory modal
    const searchInput = page.locator('input[placeholder="Search by customer name, phone number, PAN, address..."]');
    await expect(searchInput).toBeVisible({ timeout: 8000 });
    await searchInput.fill('XYZNOSUCHCUSTOMER99999');

    // Should show empty state inside directory modal
    await expect(page.locator('text=No customers found')).toBeVisible({ timeout: 8000 });
  });

});

test.describe('Product List Weight Filter Validation', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder="e.g. owner or ramesh_sales"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("Sign In to Store")');
    await expect(page.getByRole('link', { name: 'POS Billing & Invoice' })).toBeVisible({ timeout: 15000 });

    await page.getByRole('link', { name: 'Items & QR Tags' }).click();
    await expect(page.locator('h1:has-text("Inventory, Items & QR Tags")')).toBeVisible({ timeout: 10000 });
  });

  test('Weight filter shows error when min weight exceeds max weight', async ({ page }) => {
    const minInput = page.locator('input[placeholder="Min g"]');
    const maxInput = page.locator('input[placeholder="Max g"]');

    await expect(minInput).toBeVisible({ timeout: 5000 });
    await expect(maxInput).toBeVisible({ timeout: 5000 });

    await minInput.fill('20');
    await maxInput.fill('5'); // min > max — invalid

    await expect(page.locator('text=Min weight must be ≤ Max weight')).toBeVisible({ timeout: 5000 });
  });

  test('Product list shows empty state with message when filtered out', async ({ page }) => {
    const minInput = page.locator('input[placeholder="Min g"]');
    await expect(minInput).toBeVisible({ timeout: 5000 });
    await minInput.fill('99999');

    await expect(page.locator('text=No items matched your filters')).toBeVisible({ timeout: 8000 });
  });

  test('Product list displays inventory items table', async ({ page }) => {
    await expect(page.locator('h1:has-text("Inventory, Items & QR Tags")')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('table')).toBeVisible({ timeout: 10000 });
  });

});
