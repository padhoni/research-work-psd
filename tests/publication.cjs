const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs/promises');
const path=require('node:path');
(async()=>{
const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 const base=process.env.APP_URL||'http://127.0.0.1:8769';
 await page.goto(base);await page.waitForFunction(()=>document.querySelector('#metrics').textContent.includes('18.59%'));
 await page.click('#load-large');await page.waitForFunction(()=>document.querySelector('#metrics').textContent.includes('5000'));
 const exported=page.waitForEvent('download');await page.click('#export');
 const bundle=JSON.parse(await fs.readFile(await (await exported).path(),'utf8'));
 assert.equal(bundle.analysis.n,5000);assert.ok(bundle.analysis.reproducibility.input_sha256);
 const api=await page.request.get(base+'/api/publication');assert.equal(api.status(),200);
 const actual=await api.json();assert.equal(bundle.analysis.reduction,actual.large_example.reduction);
 await page.click('a[href="/paper"]');await page.waitForSelector('svg');assert.equal(await page.locator('svg').count(),3);
 const text=await page.locator('body').innerText();
 assert.ok(text.includes('18.59%'));assert.ok(text.includes('18.58%'));assert.ok(text.includes('89.37%'));assert.ok(text.includes('33.15%'));assert.ok(text.includes('24 scenarios'));
 assert.ok(!text.includes('85.0%'));assert.ok(!text.includes('54.9%'));
 await page.screenshot({path:path.resolve(__dirname,'../publication/app_results.png'),fullPage:true});
 for(const width of [768,390]){await page.setViewportSize({width,height:1000});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);}
 assert.deepEqual(errors,[]);console.log('PASS publication navigation, 5,000-row preset, reproducibility export, shared result equality, three figures, and responsive page');
}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
