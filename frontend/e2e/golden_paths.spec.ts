import { test, expect } from '@playwright/test';

test.describe('Golden Paths Feature Verification', () => {

  test('Public Login Screen (/login) shows Store Sign In without Developer exposure', async ({ page }) => {
    await page.goto('/login');

    // Verify Title and Store Sign In tab
    await expect(page.locator('text=Swarna Khata')).toBeVisible();
    await expect(page.locator('button:has-text("Store Sign In")')).toBeVisible();
    await expect(page.locator('button:has-text("Register Store")')).toBeVisible();

    // Verify Developer tab is NOT visible in public login
    await expect(page.locator('button:has-text("Developer")')).not.toBeVisible();
    await expect(page.locator('text=Developer Control Plane')).not.toBeVisible();
    await expect(page.locator('text=Master Password')).not.toBeVisible();
  });

  test('Register Store persona displays Jewellery Shield password policy', async ({ page }) => {
    await page.goto('/login');
    
    // Click on Register Store
    await page.click('button:has-text("Register Store")');

    // Assert shop name and password input are visible
    await expect(page.locator('input[placeholder="e.g. Sri Lakshmi Jewellers"]')).toBeVisible();
    await expect(page.locator('input[placeholder="e.g. Gold*Vault8"]')).toBeVisible();

    // Assert policy checklist rules render
    await expect(page.locator('text=Jewellery Shield Password Policy')).toBeVisible();
    await expect(page.locator('text=8 to 64 characters')).toBeVisible();
    await expect(page.locator('text=At least 1 uppercase letter (A-Z)')).toBeVisible();
    await expect(page.locator('text=No consecutive duplicate characters')).toBeVisible();
  });

  test('Dedicated Developer Portal (/developer) renders Obsidian Control Plane', async ({ page }) => {
    await page.goto('/developer');

    // Assert Developer Control Plane login terminal renders
    await expect(page.locator('text=Developer Control Plane')).toBeVisible();
    await expect(page.locator('text=[ROOT ACCESS]')).toBeVisible();
    await expect(page.locator('label:has-text("Developer Username")')).toBeVisible();
    await expect(page.locator('label:has-text("Master Password")')).toBeVisible();
    await expect(page.locator('button:has-text("Authenticate Terminal")')).toBeVisible();
  });

  test('Unauthenticated access to protected routes redirects to /login', async ({ page }) => {
    await page.goto('/products');
    // Should redirect to /login
    await expect(page).toHaveURL(/.*\/login/);
  });

  test('Password eye toggle allows viewing and hiding entered password', async ({ page }) => {
    await page.goto('/login');
    const pwdInput = page.locator('input[placeholder="••••••••"]');
    await pwdInput.fill('admin123');
    await expect(pwdInput).toHaveAttribute('type', 'password');

    // Click the eye toggle to show password
    const toggleBtn = page.locator('button[aria-label="Show password"]');
    await expect(toggleBtn).toBeVisible();
    await toggleBtn.click();

    // Now type should be text
    await expect(pwdInput).toHaveAttribute('type', 'text');

    // Click again to hide password
    const hideBtn = page.locator('button[aria-label="Hide password"]');
    await expect(hideBtn).toBeVisible();
    await hideBtn.click();

    // Type should return to password
    await expect(pwdInput).toHaveAttribute('type', 'password');
  });

});
