import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';
const port = 18774,
  base = `http://127.0.0.1:${port}`,
  server = spawn(process.env.PYTHON || 'python3', ['-m', 'semantic_plan', 'serve', String(port)], {
    stdio: ['ignore', 'pipe', 'inherit'],
  });
let browser;
try {
  for (let i = 0; i < 100; i++) {
    try {
      if ((await fetch(base)).ok) break;
    } catch {}
    if (server.exitCode !== null) throw Error('server exited');
    if (i === 99) throw Error('server timeout');
    await new Promise((r) => setTimeout(r, 100));
  }
  browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1400, height: 1200 } }),
    errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  for (const lang of ['fr', 'en', 'es']) {
    await page.goto(`${base}/?lang=${lang}`);
    await page.waitForFunction(() => document.getElementById('calls').textContent === '4');
    assert.equal(await page.locator('html').getAttribute('lang'), lang);
    assert.equal(await page.locator('#naive').textContent(), '15');
    assert.equal(await page.locator('#questions').textContent(), '6');
    assert.equal(await page.locator('.node').count(), 5);
    for (const [mode, calls, questions] of [
      ['warm', '0', '0'],
      ['changed', '2', '3'],
      ['policy', '4', '6'],
      ['review', '2', '4'],
    ]) {
      await page.locator('#mode').selectOption(mode);
      await page.locator('#run').click();
      await page.waitForFunction(
        (expected) => document.getElementById('calls').textContent === expected,
        calls,
      );
      assert.equal(await page.locator('#questions').textContent(), questions);
    }
    assert.equal(await page.locator('.cell.blocked_review').count(), 4);
    assert.equal(await page.locator('#sql-rows').textContent(), '[]');
    const event = page.waitForEvent('download');
    await page.locator('#download').click();
    assert.equal((await event).suggestedFilename(), 'semantic-plan-evidence.json');
  }
  await page.goto(`${base}/?lang=fr`);
  await page.waitForFunction(() => document.getElementById('calls').textContent === '4');
  await mkdir('.local', { recursive: true });
  await page.screenshot({ path: '.local/preview-fr.png', fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
  assert.deepEqual(errors, []);
  assert.equal((await fetch(`${base}/.env`)).status, 404);
  console.log(
    'FR/EN/ES: actual naive/optimized calls, warm cache, row/policy invalidation, review gate, SQLite query, export and mobile verified.',
  );
} finally {
  if (browser) await browser.close();
  server.kill('SIGTERM');
}
