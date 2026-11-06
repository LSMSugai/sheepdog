// Render the built HTML figures to PNG (2x). Needs Playwright with Chromium.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.join(__dirname, 'abstracts');
  const b = await chromium.launch();
  for (const f of ['0_sheepdog_pipeline', '1_stage1_validation', '1x_stage1_retraining', '1y_stage1_diagnostic', '2_stage2_calibration', '3_stage3_community', 'routes_article']) {
    const p = await b.newPage({ viewport: { width: f.startsWith('routes') ? 900 : f.startsWith('0') ? 1480 : (f.startsWith('1y') || f.startsWith('2_')) ? 1540 : 1200, height: 300 }, deviceScaleFactor: 2 });
    await p.emulateMedia({ colorScheme: 'light' });
    await p.goto('file://' + path.join(dir, f + '.html'));
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
    await p.screenshot({ path: path.join(dir, f + '.png'), fullPage: true });
    await p.close();
  }
  await b.close();
})();
