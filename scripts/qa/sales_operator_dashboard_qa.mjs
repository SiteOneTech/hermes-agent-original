#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import { chromium } from 'playwright';

const baseUrl = process.env.BASE_URL || 'http://100.115.198.70:9323';
const cookieName = process.env.QA_COOKIE_NAME;
const cookieValue = process.env.QA_COOKIE_VALUE;
const outDir = process.env.OUTPUT_DIR || 'factory/projects/empleado-uno-sales-operator-core/evidence/sales-operator-dashboard';

if (!cookieName || !cookieValue) {
  console.error('QA_COOKIE_NAME and QA_COOKIE_VALUE are required');
  process.exit(2);
}

await fs.mkdir(outDir, { recursive: true });
const browser = await chromium.launch({ headless: true });
const report = {
  ok: false,
  baseUrl,
  unauthRedirect: null,
  authChecks: {},
  consoleErrors: [],
  networkFailures: [],
  screenshots: {},
};

try {
  const unauth = await browser.newContext();
  const unauthPage = await unauth.newPage();
  await unauthPage.goto(`${baseUrl}/user/sales-operator/`, { waitUntil: 'domcontentloaded' });
  report.unauthRedirect = unauthPage.url();
  if (!report.unauthRedirect.includes('/user/login')) {
    throw new Error(`Unauthenticated route did not redirect to login: ${report.unauthRedirect}`);
  }
  await unauth.close();

  const context = await browser.newContext({ viewport: { width: 1440, height: 1100 } });
  await context.addCookies([{ name: cookieName, value: cookieValue, url: baseUrl, httpOnly: true, sameSite: 'Lax' }]);
  const page = await context.newPage();
  page.on('console', (msg) => {
    if (msg.type() === 'error') report.consoleErrors.push(msg.text());
  });
  page.on('requestfailed', (request) => {
    const url = request.url();
    if (url.startsWith(baseUrl)) report.networkFailures.push(`${request.method()} ${url} ${request.failure()?.errorText || ''}`);
  });

  await page.goto(`${baseUrl}/user/sales-operator/`, { waitUntil: 'networkidle' });
  const requiredTexts = ['Empleado.uno activo', 'Jornadas de trabajo', 'CRM rápido', 'Política comercial', 'Medell'];
  for (const text of requiredTexts) {
    report.authChecks[text] = await page.getByText(text, { exact: false }).first().isVisible().catch(() => false);
    if (!report.authChecks[text]) throw new Error(`Missing required dashboard text: ${text}`);
  }
  const desktopPath = path.join(outDir, 'desktop.png');
  await page.screenshot({ path: desktopPath, fullPage: true });
  report.screenshots.desktop = desktopPath;

  await page.setViewportSize({ width: 390, height: 1200 });
  await page.goto(`${baseUrl}/user/sales-operator/`, { waitUntil: 'networkidle' });
  const mobilePath = path.join(outDir, 'mobile.png');
  await page.screenshot({ path: mobilePath, fullPage: true });
  report.screenshots.mobile = mobilePath;
  await context.close();

  if (report.consoleErrors.length || report.networkFailures.length) {
    throw new Error(`Console/network errors: ${JSON.stringify({ consoleErrors: report.consoleErrors, networkFailures: report.networkFailures })}`);
  }
  report.ok = true;
} finally {
  await browser.close();
  await fs.writeFile(path.join(outDir, 'playwright-report.json'), `${JSON.stringify(report, null, 2)}\n`, 'utf8');
}

console.log(JSON.stringify(report, null, 2));
if (!report.ok) process.exit(1);
