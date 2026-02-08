import { test, expect } from '@playwright/test';

test.describe('Navigation', () => {
  test('Dashboard page loads', async ({ page }) => {
    await page.goto('/');
    
    await expect(page).toHaveTitle(/Skill Adapter/);
    await expect(page.getByRole('heading', { name: /Dashboard/i })).toBeVisible();
  });

  test('Skills page loads', async ({ page }) => {
    await page.goto('/skills');
    
    await expect(page).toHaveTitle(/Skill Adapter/);
    await expect(page.getByRole('heading', { name: /Skills/i })).toBeVisible();
  });

  test('Training page loads', async ({ page }) => {
    await page.goto('/training');
    
    await expect(page).toHaveTitle(/Skill Adapter/);
    // Use first() to handle multiple heading matches
    await expect(page.getByRole('heading', { name: /Training/i }).first()).toBeVisible();
  });

  test('Evaluation page loads', async ({ page }) => {
    await page.goto('/evaluation');
    
    await expect(page).toHaveTitle(/Skill Adapter/);
    await expect(page.getByRole('heading', { name: /Evaluation/i })).toBeVisible();
  });

  test('Sidebar navigation works', async ({ page }) => {
    await page.goto('/');
    
    // Navigate to Skills
    await page.getByRole('link', { name: /Skills/i }).click();
    await expect(page).toHaveURL(/\/skills/);
    await expect(page.getByRole('heading', { name: /Skills/i })).toBeVisible();
    
    // Navigate to Training - use first() for multiple matches
    await page.getByRole('link', { name: /Training/i }).click();
    await expect(page).toHaveURL(/\/training/);
    await expect(page.getByRole('heading', { name: /Training/i }).first()).toBeVisible();
    
    // Navigate to Evaluation
    await page.getByRole('link', { name: /Evaluation/i }).click();
    await expect(page).toHaveURL(/\/evaluation/);
    await expect(page.getByRole('heading', { name: /Evaluation/i })).toBeVisible();
    
    // Navigate back to Dashboard
    await page.getByRole('link', { name: /Dashboard/i }).click();
    await expect(page).toHaveURL(/\//);
    await expect(page.getByRole('heading', { name: /Dashboard/i })).toBeVisible();
  });

  test('Page titles render correctly', async ({ page }) => {
    const pages = [
      { url: '/', title: /Skill Adapter/ },
      { url: '/skills', title: /Skill Adapter/ },
      { url: '/training', title: /Skill Adapter/ },
      { url: '/evaluation', title: /Skill Adapter/ },
    ];

    for (const { url, title } of pages) {
      await page.goto(url);
      await expect(page).toHaveTitle(title);
    }
  });
});
