import { test, expect } from '@playwright/test';

test.describe('Store Registration & Password Reset Flow', () => {

  test('Store registration form renders all required business inputs and validations', async ({ page }) => {
    await page.goto('/login');
    await page.click('button:has-text("Register Store")');

    // Business identity fields
    await expect(page.locator('input[placeholder="e.g. Sri Lakshmi Jewellers"]')).toBeVisible();
    await expect(page.locator('input[placeholder="29AAAAA0000A1Z5"]')).toBeVisible();
    await expect(page.locator('input[placeholder="e.g. 9876543210"]')).toBeVisible();
    await expect(page.locator('input[placeholder="e.g. owner@jewellers.com"]')).toBeVisible();
    await expect(page.locator('input[placeholder="e.g. lakshmi_owner"]')).toBeVisible();

    // Password and policy check
    const pwdInput = page.locator('input[placeholder="e.g. Gold*Vault8"]');
    await expect(pwdInput).toBeVisible();
    await expect(page.locator('text=Jewellery Shield Password Policy')).toBeVisible();

    // Password policy indicators update reactively
    await pwdInput.fill('weak');
    await expect(page.locator('text=8 to 64 characters')).toBeVisible();
  });

  test('Forgot Password toggle displays email input and handles submission feedback', async ({ page }) => {
    await page.goto('/login');
    await page.click('button:has-text("Forgot Password?")');

    // Verify forgot password header & inputs
    await expect(page.locator('text=Reset Your Store Password')).toBeVisible();
    const emailInput = page.locator('input[placeholder="owner@jewellers.com"]');
    await expect(emailInput).toBeVisible();

    // Submit invalid email
    await emailInput.fill('invalid-email-no-at');
    await page.click('button:has-text("Send Reset Link")');

    // Submit valid email with mocked response
    await page.route('**/api/auth/forgot-password/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ message: 'If an account exists, instructions have been sent.' }),
      });
    });

    await emailInput.fill('owner@laxmijewellers.com');
    await page.click('button:has-text("Send Reset Link")');

    // Verify confirmation view renders
    await expect(page.locator('text=Email Dispatched')).toBeVisible();
    await expect(page.locator('button:has-text("Return to Sign In")')).toBeVisible();
  });

  test('Reset password page displays token validation state', async ({ page }) => {
    // Visit reset password route with mock expired token
    await page.route('**/api/auth/verify-reset-token/', async (route) => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({ valid: false, error: 'This reset link has expired or is invalid.' }),
      });
    });

    await page.goto('/reset-password?token=invalid_token_123');
    await expect(page.locator('text=Link Expired or Invalid')).toBeVisible();
    await expect(page.locator('text=Return to Sign In')).toBeVisible();
  });
});
