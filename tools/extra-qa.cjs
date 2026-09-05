const {chromium}=require('playwright');
const path=require('node:path');
const fs=require('node:fs');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:path.join(process.env.LOCALAPPDATA,'ms-playwright/chromium-1228/chrome-win64/chrome.exe')});
 const page=await browser.newPage({viewport:{width:390,height:844},reducedMotion:'reduce'});
 await page.goto('http://127.0.0.1:4173/',{waitUntil:'networkidle'});
 for(const id of ['styles','about','teachers','schedule','gallery','contacts']){
  const section=page.locator('#'+id);await section.scrollIntoViewIfNeeded();
  await page.evaluate(async()=>Promise.all([...document.images].filter(i=>i.id!=='dialog-image').map(i=>{i.loading='eager';return i.decode()})));
  await section.screenshot({path:'qa/mobile-'+id+'.png',style:'.site-header,.skip-link{visibility:hidden!important}'});
 }
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('file:///'+path.resolve('index.html').replaceAll('\\','/'),{waitUntil:'load'});
 await page.evaluate(async()=>Promise.all([...document.images].filter(i=>i.id!=='dialog-image').map(i=>{i.loading='eager';return i.decode()})));
 await page.locator('#mobile-menu-btn').click();
 assert.equal(await page.locator('#mobile-menu-btn').getAttribute('aria-expanded'),'true');
 assert.equal(errors.length,0);
 const result=await page.evaluate(()=>({fileProtocol:location.protocol,css:document.styleSheets.length,images:[...document.images].filter(i=>i.id!=='dialog-image').every(i=>i.naturalWidth>0),background:getComputedStyle(document.body).backgroundColor}));
 assert(result.images);assert.equal(result.background,'rgb(18, 19, 22)');
 fs.writeFileSync('qa/file-protocol.json',JSON.stringify(result,null,2));
 console.log(result);await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
