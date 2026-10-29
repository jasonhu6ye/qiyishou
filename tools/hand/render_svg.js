// 把一批 SVG 帧渲染成 PNG 横排：node render_svg.js jobs.json
// jobs.json: [{"out": "x.png", "size": 96, "frames": ["<svg ...>", ...]}]
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: 1 });
  for (const job of jobs) {
    const n = job.frames.length, s = job.size;
    await page.setViewportSize({ width: s * n, height: s });
    await page.setContent(`<html><body style="margin:0;background:transparent"><div id="strip" style="display:flex;width:${s * n}px;height:${s}px">${job.frames.join('')}</div></body></html>`);
    await page.locator('#strip').screenshot({ path: job.out, omitBackground: true });
  }
  await browser.close();
})();
