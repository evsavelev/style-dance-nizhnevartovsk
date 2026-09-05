import lighthouse from 'lighthouse';
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
const executablePath=process.env.CHROME_PATH||path.join(process.env.LOCALAPPDATA,'ms-playwright/chromium-1228/chrome-win64/chrome.exe');
const browser=await chromium.launch({executablePath,headless:true,args:['--remote-debugging-port=9224']});
try {
 for(const mode of ['mobile','desktop']){
  const flags={port:9224,output:['json','html'],onlyCategories:['performance','accessibility','best-practices','seo'],logLevel:'error'};
  const config=mode==='desktop'?{extends:'lighthouse:default',settings:{formFactor:'desktop',screenEmulation:{mobile:false,width:1440,height:900,deviceScaleFactor:1,disabled:false},throttling:{rttMs:40,throughputKbps:10240,cpuSlowdownMultiplier:1,requestLatencyMs:0,downloadThroughputKbps:0,uploadThroughputKbps:0}}}:undefined;
  const result=await lighthouse(process.argv[2]||'http://127.0.0.1:4173/',flags,config);
  fs.writeFileSync('qa/lighthouse-'+mode+'.report.json',result.report[0]);
  fs.writeFileSync('qa/lighthouse-'+mode+'.report.html',result.report[1]);
  console.log(mode,JSON.stringify(Object.fromEntries(Object.entries(result.lhr.categories).map(([k,v])=>[k,v.score]))));
 }
}finally{await browser.close();}
