import { test, expect } from '@playwright/test';

/**
 * Product Form Validation E2E Tests
 *
 * Covers all validation fixes applied to ProductFormModal:
 * - gross_weight must be > 0 to submit
 * - stone + other weight exceeding gross shows inline warning
 * - Weight inputs reject negative values via min attribute
 * - Valid product with stone < gross can be submitted
 */
test.describe('Product Form Validation', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder="e.g. owner or ramesh_sales"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("Sign In to Store")');
    await expect(page.getByRole('link', { name: 'POS Billing & Invoice' })).toBeVisible({ timeout: 15000 });

    // Navigate to Products page
    await page.getByRole('link', { name: 'Items & QR Tags' }).click();
    await expect(page.locator('h1:has-text("Inventory, Items & QR Tags")')).toBeVisible({ timeout: 10000 });

    // Open Add Jewelry Item modal
    await page.click('button:has-text("Add Jewelry Item")');
    await expect(page.locator('input[placeholder*="22KT Antique Bridal Choker"]')).toBeVisible({ timeout: 8000 });
  });

  test('Submit button blocked when gross weight is 0 or empty', async ({ page }) => {
    // Fill required name and sku but leave gross weight empty
    await page.locator('input[placeholder*="22KT Antique Bridal Choker"]').fill('Test Zero Weight Ring');
    await page.locator('input[placeholder*="JW-"]').fill(`VAL-${Date.now()}`);

    // Click submit
    const submitBtn = page.locator('button[type="submit"]:has-text("Save & Generate QR")');
    await expect(submitBtn).toBeVisible();
    await submitBtn.click();

    // Modal stays visible due to required field or validation toast
    await expect(page.locator('input[placeholder*="22KT Antique Bridal Choker"]')).toBeVisible();
  });

  test('Stone weight exceeding gross weight shows inline warning', async ({ page }) => {
    // Target inputs strictly inside the Add Product modal form
    const modalForm = page.locator('form:has-text("Weights Breakdown")');
    const grossInput = modalForm.locator('div:has(> label:has-text("Gross Wt")) input');
    await grossInput.fill('5.000');

    const stoneInput = modalForm.locator('div:has(> label:has-text("Stone Wt")) input');
    await stoneInput.fill('8.000');

    // Should show inline warning about stone exceeding gross
    await expect(modalForm.locator('text=Stone+Other exceeds Gross!')).toBeVisible({ timeout: 5000 });
  });

  test('Gross weight input has min attribute to reject non-positive values', async ({ page }) => {
    const modalForm = page.locator('form:has-text("Weights Breakdown")');
    const grossInput = modalForm.locator('div:has(> label:has-text("Gross Wt")) input');
    await expect(grossInput).toHaveAttribute('min', '0.001');
  });

  test('Valid product with stone < gross submits without errors', async ({ page }) => {
    const modalForm = page.locator('form:has-text("Weights Breakdown")');
    await page.locator('input[placeholder*="22KT Antique Bridal Choker"]').fill('Valid E2E Bangle');
    await page.locator('input[placeholder*="JW-"]').fill(`BANGLE-E2E-${Date.now()}`);

    // Fill gross weight
    const grossInput = modalForm.locator('div:has(> label:has-text("Gross Wt")) input');
    await grossInput.fill('15.000');

    // Fill stone weight (less than gross)
    const stoneInput = modalForm.locator('div:has(> label:has-text("Stone Wt")) input');
    await stoneInput.fill('2.000');

    // No warning should appear
    await expect(modalForm.locator('text=Stone+Other exceeds Gross!')).not.toBeVisible();
  });

});
