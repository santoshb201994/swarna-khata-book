import { test, expect } from '@playwright/test';

test.describe('Tray Group QR Code Clubbing & Details Feature', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder="e.g. owner or ramesh_sales"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("Sign In to Store")');
    await expect(page.getByRole('link', { name: 'POS Billing & Invoice' })).toBeVisible({ timeout: 15000 });

    await page.getByRole('link', { name: 'Items & QR Tags' }).click();
    await expect(page.locator('h1:has-text("Inventory, Items & QR Tags")')).toBeVisible({ timeout: 10000 });
  });

  test('displays Trays & Group QR Tags tab and switches cleanly', async ({ page }) => {
    const traysTab = page.locator('button:has-text("Trays & Group QR Tags")');
    await expect(traysTab).toBeVisible({ timeout: 5000 });
    await traysTab.click();

    // Verify Trays section header or search is visible
    await expect(page.locator('input[placeholder*="Search trays"]')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('button:has-text("Club Items into New Tray")')).toBeVisible({ timeout: 5000 });

    // Switch back to All Jewelry Items
    const itemsTab = page.locator('button:has-text("All Jewelry Items")');
    await itemsTab.click();
    await expect(page.locator('table')).toBeVisible({ timeout: 5000 });
  });

  test('allows selecting multiple items, clubbing into tray QR, and viewing all item details', async ({ page }) => {
    // 1. Check table rows are visible
    const table = page.locator('table');
    await expect(table).toBeVisible({ timeout: 10000 });

    // 2. Select first 2 items via row checkboxes
    const checkboxes = table.locator('tbody input[type="checkbox"]');
    const count = await checkboxes.count();
    if (count < 2) {
      test.skip(true, 'Need at least 2 items to run clubbing test');
      return;
    }

    await checkboxes.nth(0).check();
    await checkboxes.nth(1).check();

    // 3. Selection banner should appear
    const banner = page.locator('text=SELECTED TO CLUB');
    await expect(banner).toBeVisible({ timeout: 5000 });
    await expect(page.locator('text=Combined Gross Weight:')).toBeVisible();

    // 4. Click Club into Group QR Tag
    const clubBtn = page.getByRole('button', { name: 'Club into Group QR Tag' });
    await expect(clubBtn).toBeVisible();
    await clubBtn.click();

    // 5. ClubTrayModal should be open
    await expect(page.locator('h3:has-text("Club QR Codes into Tray Group")')).toBeVisible({ timeout: 5000 });

    const trayNameInput = page.locator('input[placeholder*="Tray 1 - 22KT"]');
    await expect(trayNameInput).toBeVisible();
    const testTrayName = `E2E Bridal Tray ${Date.now().toString().slice(-4)}`;
    await trayNameInput.fill(testTrayName);

    // Verify items table inside modal has 2 items
    await expect(page.locator('text=Items Clubbed in this Tray (2)')).toBeVisible();

    // 6. Submit to generate group QR code
    const generateBtn = page.getByRole('button', { name: 'Generate Group QR Code' });
    await generateBtn.click();

    // 7. TrayQRTagModal should open with group QR and itemized details
    await expect(page.locator('h3:has-text("Jewellery Tray Group QR Tag")')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText(testTrayName, { exact: true })).toBeVisible();
    await expect(page.locator('text=SWARNA KHATA JEWELLERS')).toBeVisible();
    await expect(page.locator('text=Total Clubbed Pieces')).toBeVisible();
    await expect(page.locator('text=Itemized Tray Breakdown (2 Products)')).toBeVisible();

    // Close the QR Tag modal
    const closeBtn = page.getByRole('button', { name: 'Close' });
    await closeBtn.click();
    await expect(page.locator('h3:has-text("Jewellery Tray Group QR Tag")')).not.toBeVisible();

    // 8. Navigate to Trays tab and verify the created tray is present in the grid
    const traysTab = page.locator('button:has-text("Trays & Group QR Tags")');
    await traysTab.click();
    await expect(page.getByText(testTrayName, { exact: true })).toBeVisible({ timeout: 5000 });

    // Click View Group QR on the card
    const trayCard = page.locator('div.rounded-2xl').filter({ hasText: testTrayName });
    const viewQrBtn = trayCard.getByRole('button', { name: 'View Group QR' }).first();
    await viewQrBtn.click();
    await expect(page.locator('h3:has-text("Jewellery Tray Group QR Tag")')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('text=Print Tray Group Tag')).toBeVisible();
  });

});
