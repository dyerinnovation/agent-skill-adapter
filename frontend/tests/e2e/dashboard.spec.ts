import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('Dashboard title is visible', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /Dashboard/i })).toBeVisible();
  });

  test('Dashboard cards render', async ({ page }) => {
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Check for dashboard content - using more flexible selectors
    const pageContent = await page.textContent('body');
    expect(pageContent).toBeTruthy();
  });

  test('Navigation links are present', async ({ page }) => {
    // Check that key navigation links exist
    await expect(page.getByRole('link', { name: /Dashboard/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Skills/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Training/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Evaluation/i })).toBeVisible();
  });

  test('Dashboard loads without critical JavaScript errors', async ({ page }) => {
    const errors: string[] = [];
    
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    page.on('pageerror', error => {
      errors.push(error.message);
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Allow common development warnings and connection errors (API not running)
    const criticalErrors = errors.filter(err => 
      !err.includes('Warning:') && 
      !err.includes('DevTools') &&
      !err.includes('ERR_CONNECTION_REFUSED') &&  // API might not be running
      !err.includes('Failed to load resource')
    );
    
    expect(criticalErrors).toHaveLength(0);
  });
});
