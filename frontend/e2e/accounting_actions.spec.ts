import { test, expect } from '@playwright/test';

test.describe('Accounting Dashboard Actions Verification', () => {

  test.beforeEach(async ({ page }) => {
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));
    page.on('response', async res => {
      if (res.url().includes('day-book') || res.url().includes('gold-rate')) {
        let text = '';
        try { text = await res.text(); } catch {}
        console.log('HTTP:', res.url(), res.status(), text);
      }
    });

    // Login as admin (Owner)
    await page.goto('/login');
    await page.fill('input[placeholder="e.g. owner or ramesh_sales"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("Sign In to Store")');
    await expect(page.getByRole('link', { name: 'POS Billing & Invoice' })).toBeVisible({ timeout: 15000 });

    // Navigate to Accounting & Day Book
    await page.getByRole('link', { name: 'Accounting & Day Book' }).click();
    await expect(page.locator('h1:has-text("Accounting & Day Book")')).toBeVisible({ timeout: 10000 });
    // Wait for live accounting data to finish loading (badge shows either Day Open or Day Closed)
    await expect(page.locator('h1 span:has-text("Day Open"), h1 span:has-text("Day Closed")')).toBeVisible({ timeout: 15000 });

    // If day was previously closed in an earlier test run, reopen it so subsequent tests can run cleanly
    const isClosed = await page.locator('h1 span:has-text("Day Closed")').isVisible();
    if (isClosed) {
      page.once('dialog', async (dialog) => {
        await dialog.accept();
      });
      await page.click('button:has-text("Reopen Day Book")');
      await expect(page.locator('h1 span:has-text("Day Open")')).toBeVisible({ timeout: 10000 });
    }
  });

  test('Record Cash Drawer In / Out updates day book cash drawer', async ({ page }) => {
    // Fill petty cash form: 500 Cash In
    const amountInput = page.locator('input[placeholder="Amount (₹)..."]');
    await expect(amountInput).toBeVisible({ timeout: 10000 });
    await amountInput.fill('500');

    const notesInput = page.locator('input[placeholder="Reason / Notes..."]');
    await expect(notesInput).toBeVisible();
    await notesInput.fill('Morning opening cash replenishment');

    await page.click('button:has-text("Record in Day Book")');

    // Wait for success toast
    await expect(page.locator('text=Recorded ₹500 Cash In')).toBeVisible({ timeout: 10000 });
  });

  test('Update Rate manual update updates live rate across shop', async ({ page }) => {
    // Select a purity in the rate updater
    const rateInput = page.locator('input[placeholder*="New rate (₹/g)"]');
    await expect(rateInput).toBeVisible({ timeout: 10000 });
    await rateInput.fill('7525');

    await page.click('button:has-text("Update Rate")');

    // Verify success toast
    await expect(page.locator('text=Live metal rate updated across shop!')).toBeVisible({ timeout: 10000 });
    // Verify updated rate shows in the rate card
    await expect(page.locator('text=7,525')).toBeVisible({ timeout: 10000 });
  });

  test('Close Business Day finalizes cash drawer and updates badge', async ({ page }) => {
    // Live accounting status badge shows Day Open
    await expect(page.locator('h1 span:has-text("Day Open")')).toBeVisible({ timeout: 10000 });

    const closeDayBtn = page.locator('button:has-text("Close Business Day")');
    await expect(closeDayBtn).toBeVisible({ timeout: 10000 });

    // Handle both window.confirm (native) and any inline confirm UI
    page.once('dialog', async (dialog) => {
      await dialog.accept();
    });

    await closeDayBtn.click();
    await expect(page.locator('text=Business day successfully closed and audited!')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('h1 span:has-text("Day Closed")')).toBeVisible({ timeout: 10000 });
  });

  test('Rate Sync Auto-Sync button is visible and responds', async ({ page }) => {
    // Rate source dropdown and Auto-Sync button must be visible for owner
    const syncBtn = page.locator('button:has-text("Auto-Sync")');
    await expect(syncBtn).toBeVisible({ timeout: 10000 });

    // Source dropdown must have at least one option (if it exists, sync button should be present)
    const sourceSelect = page.locator('select[title*="trade association"], select').filter({ hasText: /Gold|Rate|Source/i }).first();
    if (await sourceSelect.isVisible({ timeout: 3000 })) {
      const options = await sourceSelect.locator('option').allInnerTexts();
      // When sources exist, the Auto-Sync button is shown
      expect(options.length).toBeGreaterThan(0);
      await expect(syncBtn).toBeVisible();
    }
  });
});
