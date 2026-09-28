// Run with NODE_PATH pointing to an installed Playwright package.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs/promises');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 try {
 const page=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto(process.env.APP_URL||'http://127.0.0.1:8766');
 const ready=()=>page.waitForFunction(()=>document.querySelector('#metrics').textContent.includes('18.59%'));
 await ready();
 async function download(selector) {const pending=page.waitForEvent('download');await page.click(selector);return fs.readFile(await (await pending).path(),'utf8');}
 const bundle=JSON.parse(await download('#export'));
 assert.equal(bundle.analysis.n,5);assert.equal(bundle.analysis.source,'simulated');assert.ok(bundle.input_csv.includes('C01'));assert.ok(bundle.figure_svg.includes('<svg'));assert.ok(bundle.analysis.report.includes('Simulated'));
 const svg=await download('#figure');assert.ok(svg.includes('simulated'));assert.equal(await page.evaluate(s=>new DOMParser().parseFromString(s,'image/svg+xml').querySelector('parsererror')===null,svg),true);
 console.log('PASS demo statistics, JSON contents, SVG export');
 await page.selectOption('#source','observed');assert.ok(await page.isDisabled('#export'));await page.click('#analyze');await page.waitForFunction(()=>document.querySelector('#report').textContent.includes('User-supplied observational'));
 await page.setInputFiles('#file',{name:'workload.csv',mimeType:'text/csv',buffer:Buffer.from('clinician_id,pre,post\nA,65,48\nB,72,60\nC,54,45')});
 await page.selectOption('#metric','workload');await page.click('#analyze');await page.waitForFunction(()=>document.querySelector('#report').textContent.includes('NASA-TLX points'));
 assert.equal(JSON.parse(await download('#export')).analysis.n,3);
 console.log('PASS file import, observed provenance, workload analysis, stale export disabled');
 await page.fill('#csv','clinician_id,pre,post\na,461,25\nb,50,24');await page.click('#analyze');await page.waitForFunction(()=>document.querySelector('#error').textContent.includes('0 and 100'));assert.ok(await page.isDisabled('#export'));
 await page.selectOption('#metric','time');await page.fill('#csv','clinician_id,pre,post\na,0,1\nb,0,1');await page.click('#analyze');await page.waitForFunction(()=>document.querySelector('#metrics').textContent.includes('Undefined'));assert.ok((await page.locator('#stats').innerText()).includes('Undefined'));
 await page.fill('#csv','clinician_id,pre,post\n<img src=x onerror=alert(1)>,3,2\nb,4,2');await page.click('#analyze');await page.waitForSelector('#chart svg');assert.equal(await page.locator('#chart img').count(),0);
 console.log('PASS validation, zero variance, escaped clinician identifiers');
 await page.click('#demo');await ready();
 // Edits made while analysis is in flight must not be replaced by the old response.
 await page.route('**/api/analyze',async route=>{await new Promise(r=>setTimeout(r,400));await route.continue();});
 await page.click('#analyze');await page.fill('#csv','clinician_id,pre,post\nNew,8,3\nOther,6,4');await page.waitForFunction(()=>!document.querySelector('#analyze').disabled);assert.ok(await page.isDisabled('#export'));assert.equal(await page.locator('#metrics').innerText(),'');await page.unroute('**/api/analyze');
 console.log('PASS in-flight edit protection');
 await page.click('[data-tab="cds"]');await page.click('#simulate');await page.waitForSelector('#cds-results:not([hidden])');const first=JSON.parse(await download('#export-cds'));await page.click('#simulate');await page.waitForSelector('#cds-results:not([hidden])');assert.deepEqual(JSON.parse(await download('#export-cds')),first);
 await page.fill('#n','10.5');await page.click('#simulate');await page.waitForFunction(()=>document.querySelector('#cds-error').textContent.includes('whole numbers'));assert.ok(await page.isDisabled('#export-cds'));
 await page.fill('#n','10');await page.fill('#legacy','0');await page.fill('#ai','100');await page.click('#simulate');await page.waitForSelector('#cds-results:not([hidden])');const edge=JSON.parse(await download('#export-cds'));assert.equal(edge.groups[0].overrides,0);assert.equal(edge.groups[1].overrides,10);
 console.log('PASS simulation reproducibility, invalid counts, probability boundaries, JSON export');
 await page.click('[data-tab="methods"]');assert.ok(await page.locator('#methods').isVisible());
 await page.click('[data-tab="analysis"]');await page.click('#demo');await ready();
 for(const width of [1440,768,390]) {await page.setViewportSize({width,height:900});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);}
 assert.deepEqual(errors,[]);console.log('PASS navigation, responsive widths 1440/768/390, no JavaScript errors');
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
