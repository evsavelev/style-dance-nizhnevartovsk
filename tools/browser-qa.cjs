const {chromium} = require('playwright');
const AxeBuilder = require('@axe-core/playwright').default;
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const base = process.argv[2] || 'http://127.0.0.1:4173/';
const label = process.argv[3] || 'local';
const executablePath = process.env.CHROME_PATH || path.join(process.env.LOCALAPPDATA, 'ms-playwright/chromium-1228/chrome-win64/chrome.exe');
(async () => {
 const browser = await chromium.launch({headless:true, executablePath});
 const results = [];
 for (const [width,height] of [[1280,900],[1440,900],[768,1024],[375,812],[390,844],[430,932]]) {
  const context = await browser.newContext({viewport:{width,height},deviceScaleFactor:1,reducedMotion:'reduce'});
  const page = await context.newPage();
  const errors=[], badResponses=[], requests=[];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', m => {if(m.type()==='error') errors.push(m.text());});
  page.on('response', r => {if(r.status()>=400) badResponses.push({url:r.url(),status:r.status()});});
  page.on('request',r=>requests.push(r.url()));
  await page.goto(base,{waitUntil:'networkidle'});
  await page.evaluate(()=>document.fonts.ready);
  await page.screenshot({path:'qa/'+label+'-'+width+'-hero.png'});
  // Force all lazy images into view, then verify decoded resources.
  await page.evaluate(async()=>{
    for(let y=0;y<document.documentElement.scrollHeight;y+=600) {window.scrollTo(0,y);await new Promise(r=>setTimeout(r,35));}
  });
  await page.waitForLoadState('networkidle');
  await page.evaluate(async()=>{await Promise.all([...document.images].filter(i=>i.id!=='dialog-image').map(i=>i.decode()));window.scrollTo(0,0);});
  const layout=await page.evaluate(()=>({
   overflow:document.documentElement.scrollWidth>innerWidth,
   wide:[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect();return r.width&& (r.right>innerWidth+1||r.left< -1)&& getComputedStyle(e).position!=='fixed';}).map(e=>({tag:e.tagName,class:e.className})).slice(0,10),
   broken:[...document.images].filter(i=>i.id!=='dialog-image'&&(!i.complete||!i.naturalWidth)).map(i=>i.src),
   anchors:[...document.querySelectorAll('a[href^="#"]')].filter(a=>!document.getElementById(a.hash.slice(1))).map(a=>a.outerHTML),
   phones:[...document.querySelectorAll('a[href^="tel:"]')].map(a=>a.getAttribute('href')),
   externalResources:performance.getEntriesByType('resource').filter(r=>!r.name.startsWith(location.origin)).map(r=>r.name)
  }));
  if(layout.overflow) console.log(JSON.stringify(layout,null,2));
  assert.equal(layout.overflow,false,'horizontal overflow '+width);
  assert.equal(layout.broken.length,0,'broken images');
  assert.equal(layout.anchors.length,0,'missing anchors');
  assert(layout.phones.every(p=>p==='tel:+73466570383'));
  assert.equal(layout.externalResources.length,0,'external resources');
  await page.screenshot({path:'qa/'+label+'-'+width+'-full.png',fullPage:true});
  if(width<1200) {
   const toggle=page.locator('#mobile-menu-btn');
   await toggle.click();assert.equal(await toggle.getAttribute('aria-expanded'),'true');
   await page.screenshot({path:'qa/'+label+'-'+width+'-menu.png'});
   await page.keyboard.press('Escape');assert.equal(await toggle.getAttribute('aria-expanded'),'false');
   await toggle.click();await page.locator('#mobile-menu a[href="#styles"]').click();
   assert.equal(await toggle.getAttribute('aria-expanded'),'false');
  }
  // All navigation destinations and booking anchors are independently checked.
  for (const href of ['#styles','#about','#teachers','#schedule','#gallery','#contacts','#booking']) {
   await page.locator('a[href="'+href+'"]:visible').first().click();
   await page.waitForTimeout(30);
   assert.equal(await page.evaluate(()=>location.hash),href);
  }
  for(const category of ['events','kids','training','all']) {
   const button=page.locator('[data-filter="'+category+'"]');await button.click();
   const actual=await page.locator('.gallery-item:visible').count();
   const expected=await page.locator(category==='all'?'.gallery-item':'.gallery-item[data-category="'+category+'"]').count();
   assert.equal(actual,expected);assert.equal(await button.getAttribute('aria-pressed'),'true');
  }
  await page.locator('.gallery-item').first().click();assert(await page.locator('#photo-dialog').isVisible());
  await page.screenshot({path:'qa/'+label+'-'+width+'-lightbox.png'});
  await page.keyboard.press('Escape');assert.equal(await page.locator('#photo-dialog').isVisible(),false);
  await page.locator('.gallery-item').first().click();await page.locator('.dialog-close').click();
  assert.equal(await page.locator('#photo-dialog').isVisible(),false);
  const axe = await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']).analyze();
  results.push({width,height,layout,errors,badResponses,requestCount:requests.length,axe:axe.violations.map(v=>({id:v.id,impact:v.impact,description:v.description,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))}))});
  console.log(label,width,'OK, axe findings:',axe.violations.length);
  await context.close();
 }
 fs.writeFileSync('qa/'+label+'-results.json',JSON.stringify(results,null,2));
 await browser.close();
 assert(results.every(r=>r.errors.length===0&&r.badResponses.length===0),'console/network failures');
 assert(results.every(r=>r.axe.length===0),'accessibility findings');
})().catch(e=>{console.error(e);process.exit(1);});
