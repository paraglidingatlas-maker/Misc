// usage: node shot.js <jobs.json>   job: {url (path under repo), w, h, out, full?, actions?: js string run in page, wait?, clip?:{x,y,width,height}, scrollTo?: selector}
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const ROOT = '/home/user/Misc';
const MIME = {'.html':'text/html','.js':'application/javascript','.css':'text/css','.jpg':'image/jpeg','.png':'image/png','.svg':'image/svg+xml','.json':'application/json','.webp':'image/webp'};
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2]));
  const browser = await chromium.launch({proxy:{server:'http://127.0.0.1:44937'}});
  const report = [];
  for (const j of jobs) {
    const ctx = await browser.newContext({viewport:{width:j.w,height:j.h||900}, deviceScaleFactor:j.dpr||1, hasTouch: j.w<500, isMobile: j.w<500});
    await ctx.route('http://local/**', async r => { let p = decodeURIComponent(new URL(r.request().url()).pathname); if (p.endsWith('/')) p += 'index.html';
      const f = path.join(ROOT, p); if (!fs.existsSync(f)) return r.fulfill({status:404, body:''}); r.fulfill({status:200, body:fs.readFileSync(f), contentType: MIME[path.extname(f)]||'application/octet-stream'}); });
    const page = await ctx.newPage(); const errs = [];
    page.on('pageerror', e => errs.push('pageerror: '+e.message)); page.on('console', m => { if (m.type()==='error') errs.push('console: '+m.text()); });
    await page.goto('http://local/' + j.url, {waitUntil:'networkidle'}).catch(e=>errs.push('goto '+e.message));
    await page.waitForTimeout(j.wait ?? 1200);
    if (j.actions) { try { await page.evaluate(j.actions); } catch(e){ errs.push('action: '+e.message); } await page.waitForTimeout(j.wait2 ?? 900); }
    if (j.scrollTo) { await page.evaluate(s => { const el = document.querySelector(s); if (el) el.scrollIntoView({block:'start'}); }, j.scrollTo); await page.waitForTimeout(700); }
    const ov = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    if (j.out) await page.screenshot({path:j.out, fullPage:!!j.full, clip:j.clip});
    if (j.evalOut) report.push({out:j.out, val: await page.evaluate(j.evalOut).catch(e=>'ERR '+e.message)});
    report.push({out:j.out, url:j.url, w:j.w, overflowX:ov, errs});
    await ctx.close();
  }
  await browser.close();
  console.log(JSON.stringify(report, null, 1));
})();
