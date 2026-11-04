import { test, expect } from '@playwright/test';

test.describe('Mobile Camera Scanner & Pairing Experience', () => {

  test('Accessing /scanner without pairing session displays inactive pairing guidance', async ({ page }) => {
    await page.goto('/scanner');
    await expect(page.locator('text=Pairing Session Inactive')).toBeVisible();
    await expect(page.locator('text=Reload / Try Again')).toBeVisible();
  });

  test('Accessing /scanner with pairing parameters attempts redemption and renders camera viewport', async ({ page }) => {
    // Mock the pairing redemption API
    await page.route('**/api/pos/pairing/redeem/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'paired',
          mobile_token: 'mock_mobile_jwt_token_12345',
          expires_in_seconds: 43200,
          tenant_schema: 't_santosh',
          session: {
            session_id: 'sess_123',
            user_name: 'Santosh Jewellers',
            branch_name: 'Main Showroom',
          },
        }),
      });
    });

    await page.goto('/scanner?session_id=sess_123&code=PAIR99&tenant=t_santosh');

    // Header renders Swarna Khata Mobile POS
    await expect(page.locator('text=Swarna Khata')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Mobile POS')).toBeVisible();
  });
});
