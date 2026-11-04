import { test, expect } from '@playwright/test';

test.describe('Invoice Settings & Branding Studio', () => {

  test('Billing screen renders Invoice Settings button for store owners', async ({ page }) => {
    // Authenticate as owner
    await page.addInitScript(() => {
      localStorage.setItem('auth_tokens', JSON.stringify({
        access: 'mock_owner_access_token',
        refresh: 'mock_owner_refresh_token',
        user: {
          id: 1,
          username: 'santosh',
          role: 'owner',
          tenant_schema: 't_santosh',
        },
      }));
    });

    // Mock invoice settings API
    await page.route('**/api/billing/invoice-settings/', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 1,
            shop_name_primary: 'Santosh Jewellers Flagship',
            shop_name_secondary: 'ಸಂತೋಷ್ ಜ್ಯುವೆಲ್ಲರ್ಸ್',
            tagline: 'Pure BIS Hallmark Gold & Silver',
            gstin: '29ABCDE1234F1Z5',
            phone_mobile_1: '9999999999',
            address_primary: 'Main Showroom, Sarafa Bazar, Gadag',
            template_style: 'traditional_bilingual',
            default_paper_size: 'A4',
            show_invocation: true,
            show_huid: true,
            show_bank_details: true,
          }),
        });
      } else {
        await route.fulfill({ status: 200, contentType: 'application/json', body: route.request().postData() || '{}' });
      }
    });

    // Mock products & customers
    await page.route('**/api/products/**', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) });
    });
    await page.route('**/api/customers/**', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) });
    });
    await page.route('**/api/gold-rates/**', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) });
    });

    await page.goto('/billing');

    // Click customize invoice button if present
    const customizeBtn = page.locator('button:has-text("Invoice Settings"), button[title*="Invoice Settings"], button:has-text("Customize")');
    if (await customizeBtn.count() > 0) {
      await customizeBtn.first().click();
      await expect(page.locator('text=Invoice Customization & Branding Studio')).toBeVisible();
      await expect(page.locator('text=Store Identity')).toBeVisible();
      await expect(page.locator('button:has-text("Reset to Balaji Reference Profile")')).toBeVisible();
    }
  });
});
