import { test, expect } from '@playwright/test';

test.describe('Dropdown Options Verification', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login
    await page.goto('/login');
    // Login as admin
    await page.fill('input[placeholder="e.g. owner or ramesh_sales"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("Sign In to Store")');
    // Wait for POS screen to appear
    await expect(page.getByRole('link', { name: 'POS Billing & Invoice' })).toBeVisible({ timeout: 15000 });
  });

  test('Product list filter dropdowns work properly', async ({ page }) => {
    await page.getByRole('link', { name: 'Items & QR Tags' }).click();
    await expect(page.locator('h1:has-text("Inventory, Items & QR Tags")')).toBeVisible();

    // Check Category filter dropdown
    const categorySelect = page.locator('select').filter({ hasText: 'All Categories' });
    await expect(categorySelect).toBeVisible();
    await expect(categorySelect.locator('option')).not.toHaveCount(1);
    const catOptions = await categorySelect.locator('option').allInnerTexts();
    console.log('Category options:', catOptions);
    expect(catOptions.length).toBeGreaterThan(1);
    
    // Select an option
    await categorySelect.selectOption({ index: 1 });
    const selectedCatVal = await categorySelect.inputValue();
    expect(selectedCatVal).not.toBe('');

    // Check Purity filter dropdown
    const puritySelect = page.locator('select').filter({ hasText: 'All Purities' });
    await expect(puritySelect).toBeVisible();
    await expect(puritySelect.locator('option')).not.toHaveCount(1);
    const purityOptions = await puritySelect.locator('option').allInnerTexts();
    console.log('Purity options:', purityOptions);
    expect(purityOptions.length).toBeGreaterThan(1);

    // Select an option
    await puritySelect.selectOption({ index: 1 });
    const selectedPurityVal = await puritySelect.inputValue();
    expect(selectedPurityVal).not.toBe('');

    // Check Status filter dropdown
    const statusSelect = page.locator('select').filter({ hasText: 'All Statuses' });
    await expect(statusSelect).toBeVisible();
    await statusSelect.selectOption('AVAILABLE');
    expect(await statusSelect.inputValue()).toBe('AVAILABLE');
  });

  test('Add Product Modal dropdown options work properly', async ({ page }) => {
    await page.getByRole('link', { name: 'Items & QR Tags' }).click();
    await expect(page.locator('h1:has-text("Inventory, Items & QR Tags")')).toBeVisible();
    await page.click('button:has-text("Add Jewelry Item")');

    // Category dropdown
    const modalCategorySelect = page.locator('div:has(> label:has-text("Category *")) select');
    await expect(modalCategorySelect).toBeVisible();
    await expect(modalCategorySelect.locator('option')).not.toHaveCount(0);
    const catOptions = await modalCategorySelect.locator('option').allInnerTexts();
    console.log('Modal category options:', catOptions);
    expect(catOptions.length).toBeGreaterThan(0);

    // Purity dropdown
    const modalPuritySelect = page.locator('div:has(> label:has-text("Purity *")) select');
    await expect(modalPuritySelect).toBeVisible();
    await expect(modalPuritySelect.locator('option')).not.toHaveCount(0);
    const purOptions = await modalPuritySelect.locator('option').allInnerTexts();
    console.log('Modal purity options:', purOptions);
    expect(purOptions.length).toBeGreaterThan(0);

    // Making charge type dropdown
    const makingChargeSelect = page.locator('div:has(> label:has-text("Making Charge Type")) select');
    await expect(makingChargeSelect).toBeVisible();
    await makingChargeSelect.selectOption('percent');
    expect(await makingChargeSelect.inputValue()).toBe('percent');
    await makingChargeSelect.selectOption('fixed');
    expect(await makingChargeSelect.inputValue()).toBe('fixed');
    await makingChargeSelect.selectOption('per_gram');
    expect(await makingChargeSelect.inputValue()).toBe('per_gram');
  });

  test('Accounting Dashboard dropdown options work properly', async ({ page }) => {
    await page.getByRole('link', { name: 'Accounting & Day Book' }).click();
    await expect(page.locator('h1:has-text("Accounting & Day Book")')).toBeVisible();

    // Live metal rate scraper source dropdown
    const sourceSelect = page.locator('select[title*="trade association"]');
    await expect(sourceSelect).toBeVisible();
    await expect(sourceSelect.locator('option')).not.toHaveCount(0);
    const sourceOptions = await sourceSelect.locator('option').allInnerTexts();
    console.log('Rate source options:', sourceOptions);
    expect(sourceOptions.length).toBeGreaterThan(0);

    // Purity rate updater dropdown
    const purityRateSelect = page.locator('form select');
    await expect(purityRateSelect).toBeVisible();
    await expect(purityRateSelect.locator('option')).not.toHaveCount(0);
    const purityRateOptions = await purityRateSelect.locator('option').allInnerTexts();
    console.log('Purity rate options:', purityRateOptions);
    expect(purityRateOptions.length).toBeGreaterThan(0);
  });

  test('Staff Management Modal role dropdown works properly', async ({ page }) => {
    const staffBtn = page.locator('button:has-text("Staff")');
    await expect(staffBtn).toBeVisible();
    await staffBtn.click();

    // Click Add New Salesman / Staff tab
    const addTab = page.locator('button:has-text("Add New Salesman / Staff")');
    await expect(addTab).toBeVisible();
    await addTab.click();

    const roleSelect = page.locator('label:has-text("Role *") + select, div:has(> label:has-text("Role *")) select');
    await expect(roleSelect).toBeVisible();
    const roleOptions = await roleSelect.locator('option').allInnerTexts();
    console.log('Staff role options:', roleOptions);
    expect(roleOptions.length).toBe(3);

    await roleSelect.selectOption('manager');
    expect(await roleSelect.inputValue()).toBe('manager');
    await roleSelect.selectOption('accountant');
    expect(await roleSelect.inputValue()).toBe('accountant');
    await roleSelect.selectOption('staff');
    expect(await roleSelect.inputValue()).toBe('staff');
  });
});
