import { test, expect } from '@playwright/test';

const baseUrl = process.env.BASE_URL || 'http://100.115.198.70:9323';
const cookieName = process.env.QA_COOKIE_NAME;
const cookieValue = process.env.QA_COOKIE_VALUE;

test.describe('Sales Operator private dashboard', () => {
  test('redirects unauthenticated users and renders protected dashboard', async ({ browser }, testInfo) => {
    expect(cookieName, 'QA_COOKIE_NAME').toBeTruthy();
    expect(cookieValue, 'QA_COOKIE_VALUE').toBeTruthy();

    const unauth = await browser.newContext();
    const unauthPage = await unauth.newPage();
    await unauthPage.goto(`${baseUrl}/user/sales-operator/`, { waitUntil: 'domcontentloaded' });
    expect(unauthPage.url()).toContain('/user/login');
    await unauth.close();

    const consoleErrors = [];
    const networkFailures = [];
    const context = await browser.newContext({ viewport: { width: 1440, height: 1100 } });
    await context.addCookies([{ name: cookieName, value: cookieValue, url: baseUrl, httpOnly: true, sameSite: 'Lax' }]);
    const page = await context.newPage();
    page.on('console', (msg) => {
      if (msg.type() === 'error') consoleErrors.push(msg.text());
    });
    page.on('requestfailed', (request) => {
      if (request.url().startsWith(baseUrl)) networkFailures.push(`${request.method()} ${request.url()} ${request.failure()?.errorText || ''}`);
    });

    await page.goto(`${baseUrl}/user/sales-operator/`, { waitUntil: 'networkidle' });
    await expect(page.getByText('Empleado.uno activo', { exact: false }).first()).toBeVisible();
    await expect(page.getByText('Jornadas de trabajo', { exact: false }).first()).toBeVisible();
    await expect(page.getByText('CRM rápido', { exact: false }).first()).toBeVisible();
    await expect(page.getByText('Política comercial', { exact: false }).first()).toBeVisible();
    await expect(page.getByText('Medell', { exact: false }).first()).toBeVisible();
    await page.screenshot({ path: testInfo.outputPath('desktop.png'), fullPage: true });

    await page.setViewportSize({ width: 390, height: 1200 });
    await page.goto(`${baseUrl}/user/sales-operator/`, { waitUntil: 'networkidle' });
    await page.screenshot({ path: testInfo.outputPath('mobile.png'), fullPage: true });
    await context.close();

    expect(consoleErrors).toEqual([]);
    expect(networkFailures).toEqual([]);
  });
});
