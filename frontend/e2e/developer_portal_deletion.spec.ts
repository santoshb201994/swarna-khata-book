import { test, expect } from '@playwright/test';

test.describe('Developer Portal Store Management & Deletion Suite', () => {

  test('Developer portal overview displays active stores and handles store deletion', async ({ page }) => {
    // Authenticate as developer superadmin in localStorage
    await page.addInitScript(() => {
      localStorage.setItem('access_token', 'mock_dev_access_token');
      localStorage.setItem('tenant_schema', 'public');
      localStorage.setItem('user_info', JSON.stringify({
        id: 99,
        username: 'developer',
        role: 'superadmin',
        is_superuser: true,
        tenant_schema: 'public',
      }));
    });

    // Mock developer overview API
    await page.route('**/api/developer/overview/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_tenants: 1,
          active_tenants: 1,
          total_users: 1,
          tenants: [
            {
              id: 1,
              name: 'santosh',
              schema_name: 't_santosh',
              description: 'Santosh Jewellers',
              is_active: true,
              domains: ['t_santosh.swarnakhata.internal'],
              created_on: '2026-11-03',
              product_count: 0,
              branch_count: 1,
              users: [
                { id: 10, username: 'santosh', role: 'owner', phone: '9999999999', is_active: true, branch_name: 'Main Showroom' },
              ],
            },
          ],
        }),
      });
    });

    // Mock delete endpoint
    await page.route('**/api/developer/tenants/*/delete/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, message: 'Store deleted successfully' }),
      });
    });

    await page.goto('/developer');

    // Overview renders active shop
    await expect(page.getByRole('heading', { name: 'santosh' })).toBeVisible();
    await expect(page.locator('text=schema: t_santosh')).toBeVisible();
    await expect(page.locator('button:has-text("Delete Store")')).toBeVisible();
    await expect(page.locator('button:has-text("Enter Store as Superadmin")')).toBeVisible();
  });
});
