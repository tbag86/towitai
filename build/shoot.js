// Screenshot every slide of deck.html at 1920x1080 for QA.
const path = require('path');
function pw(){ try{return require('playwright');}catch(_){return require('/usr/local/lib/node_modules/playwright');} }
(async () => {
  const { chromium } = pw();
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  const deckArg = process.argv[2] || '../site/williams/index.html'; // pass a built client: ../site/<slug>/index.html
  const url = 'file://' + path.resolve(__dirname, deckArg);
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);
  const n = await page.evaluate(() => document.querySelectorAll('.slide').length);
  const out = path.resolve(__dirname, 'assets/shots');
  require('fs').mkdirSync(out, { recursive: true });
  for (let k = 0; k < n; k++) {
    await page.waitForTimeout(1100); // let reveal + counters settle
    await page.screenshot({ path: path.join(out, `slide-${String(k+1).padStart(2,'0')}.png`) });
    await page.keyboard.press('ArrowRight');
  }
  await browser.close();
  console.log(`shot ${n} slides -> ${out}`);
})().catch(e => { console.error(e); process.exit(1); });
