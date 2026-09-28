const $ = id => document.getElementById(id);
let result = null, simulation = null, svg = '', analyzedCSV = '';
const fmt = (n, digits=2) => n == null ? 'Undefined' : Number(n).toFixed(digits);
const escapeHTML = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function api(path, data) { const r = await fetch(path, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}); const body = await r.json(); if (!r.ok) throw Error(body.error); return body; }
function download(name, text, type) { const url=URL.createObjectURL(new Blob([text],{type})); const a=document.createElement('a'); a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000); }
function invalidate() { result=null; $('export').disabled=$('figure').disabled=true; $('metrics').innerHTML='';$('stats').innerHTML='';$('chart').innerHTML='';$('report').textContent='Inputs changed. Run the analysis to refresh results.';$('warnings').innerHTML='';$('source-banner').textContent='UNANALYZED INPUT · Run paired analysis to calculate results and confirm provenance.'; }
function chart(r) {
 const W=640,H=290,left=55,right=590,top=35,bottom=238;
 const max=Math.max(...r.rows.flatMap(x=>[x.pre,x.post]),1)*1.15;
 const y=v=>bottom-(v/max)*(bottom-top);
 let parts=[];
 for(let i=0;i<=4;i++){let v=max*i/4;parts.push(`<line x1="${left}" y1="${y(v)}" x2="${right}" y2="${y(v)}" stroke="#e5ebe4"/><text x="45" y="${y(v)+4}" text-anchor="end" fill="#71817c" font-size="11">${v.toFixed(1)}</text>`);}
 // Deterministic horizontal offsets keep pairs legible while retaining all observations.
 r.rows.forEach((row,i)=>{let offset=((i%17)-8)*2;parts.push(`<line x1="${210+offset}" y1="${y(row.pre)}" x2="${440+offset}" y2="${y(row.post)}" stroke="#9fb8a8" opacity=".5"/><circle cx="${210+offset}" cy="${y(row.pre)}" r="4" fill="#8b9e97"><title>${escapeHTML(row.clinician_id)} pre: ${row.pre}</title></circle><circle cx="${440+offset}" cy="${y(row.post)}" r="4" fill="#1a765c"><title>${escapeHTML(row.clinician_id)} post: ${row.post}</title></circle>`);});
 return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="Paired pre and post outcomes" style="font-family:Arial,sans-serif;background:white"><title>${r.source==='simulated'?'Simulated':'Observed'} clinician-level paired outcomes</title><text x="55" y="18" fill="#71817c" font-size="10">${r.metric==='time'?'Documentation minutes':'NASA-TLX points'} · ${r.source} · n=${r.n}</text>${parts.join('')}<text x="210" y="265" text-anchor="middle" fill="#163635" font-size="12">Pre-intervention</text><text x="440" y="265" text-anchor="middle" fill="#163635" font-size="12">Post-intervention</text></svg>`;
}
async function run() {
 $('error').textContent='';$('analyze').disabled=true;
 const csv=$('csv').value, metric=$('metric').value, source=$('source').value;
 try {
  const r=await api('/api/analyze',{csv,metric,source});
  if(csv!==$('csv').value || metric!==$('metric').value || source!==$('source').value) return;
  result=r;analyzedCSV=csv;
  const unit=r.metric==='time'?'minutes per encounter':'workload points';
  $('metrics').innerHTML=[['Clinician pairs',r.n,'Complete paired observations'],['Mean pre-intervention',fmt(r.pre),unit],['Mean post-intervention',fmt(r.post),unit],['Relative reduction',r.reduction==null?'Undefined':fmt(r.reduction)+'%','Calculated from group means']].map(x=>`<div class="metric"><label>${x[0]}</label><strong>${x[1]}</strong><small>${x[2]}</small></div>`).join('');
  $('stats').innerHTML=[['Mean paired difference',fmt(r.difference,3)],['95% CI of difference',r.ci?r.ci.map(x=>fmt(x,3)).join(' to '):'Undefined'],['t statistic / df',`${fmt(r.t,3)} / ${r.df}`],['Two-sided p-value',r.p==null?'Undefined':r.p===0?'Below numerical precision':r.p.toExponential(4)],['Cohen’s dz',fmt(r.dz,3)]].map(x=>`<div><dt>${x[0]}</dt><dd>${x[1]}</dd></div>`).join('');
  svg=chart(r);$('chart').innerHTML=svg;$('report').textContent=r.report;$('warnings').innerHTML=r.warnings.map(x=>`<p>${escapeHTML(x)}</p>`).join('');
  $('source-banner').textContent=r.source==='simulated'?'SIMULATED DATA · Method demonstration only. These results are not clinical evidence.':'USER-SUPPLIED OBSERVED DATA · Verify collection methods and study design before manuscript use.';
  $('export').disabled=$('figure').disabled=false;
 } catch(e) {invalidate();$('error').textContent=e.message;} finally {$('analyze').disabled=false;}
}
async function demo() {try{const r=await fetch('/api/demo');if(!r.ok)throw Error('Unable to load demo.');$('csv').value=(await r.json()).csv;$('metric').value='time';$('source').value='simulated';await run();}catch(e){$('error').textContent=e.message;}}
$('analyze').onclick=run;$('demo').onclick=demo;
$('load-large').onclick=async()=>{ $('load-large').disabled=true;try{const response=await fetch('/api/synthetic-5000');if(!response.ok)throw Error('Unable to load synthetic dataset. Restart the updated server.');const data=await response.json();$('csv').value=data.csv;$('metric').value='time';$('source').value='simulated';invalidate();await run();}catch(e){$('error').textContent=e.message;}finally{$('load-large').disabled=false;}};
['csv','metric','source'].forEach(id=>$(id).addEventListener('input',invalidate));
$('file').onchange=async e=>{const f=e.target.files[0];if(!f)return;if(f.size>1900000){$('error').textContent='CSV file must be under 1.9 MB.';return;}try{$('csv').value=await f.text();invalidate();$('error').textContent='CSV loaded. Select its outcome and provenance, then run the analysis.';}catch(err){$('error').textContent=err.message;}};
$('figure').onclick=()=>download('epic-paired-outcomes.svg',svg,'image/svg+xml');
$('export').onclick=()=>{if(!result)return;download('epic-research-bundle.json',JSON.stringify({application:'EPIC Research Lab',version:'2.0.0',exported_at:new Date().toISOString(),analysis:result,input_csv:analyzedCSV,figure_svg:svg,method:{test:'Two-sided paired t-test',confidence_level:0.95,unit:'clinician',difference:'pre minus post',missing_data:'Rejected; complete pairs required',dependencies:'requirements.txt'},sources:['Proof of Concept.docx','https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_rel.html','https://humansystems.arc.nasa.gov/groups/TLX/downloads/TLX_pappen_manual.pdf']},null,2),'application/json');};
document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>{document.querySelectorAll('.page').forEach(p=>p.hidden=p.id!==b.dataset.tab);document.querySelectorAll('nav button').forEach(x=>x.classList.toggle('active',x===b));});
['seed','n','legacy','ai'].forEach(id=>$(id).oninput=()=>{simulation=null;$('export-cds').disabled=true;$('cds-results').hidden=true;});
$('simulate').onclick=async()=>{simulation=null;$('export-cds').disabled=true;$('cds-results').hidden=true;$('cds-error').textContent=''; const data=Object.fromEntries(['seed','n','legacy','ai'].map(id=>[id,$(id).value])); if(Object.values(data).some(x=>x.trim()==='')){$('cds-error').textContent='Complete all simulation inputs.';return;}$('simulate').disabled=true;try{let r=await api('/api/simulate',data);if(Object.keys(data).some(id=>data[id]!==$(id).value))return;simulation=r;$('cds-results').hidden=false;$('cds-results').innerHTML=`<h2>Synthetic override rates</h2><p>Seed ${r.seed} · ${r.n.toLocaleString()} alerts per group</p>`+r.groups.map(g=>`<strong>${g.name}: ${fmt(g.rate)}%</strong><div>${g.overrides.toLocaleString()} overrides · Wilson 95% CI ${g.ci.map(x=>fmt(x)).join('–')}%</div><div class="bar-track"><div class="bar" style="width:${g.rate}%"></div></div>`).join('')+`<p>Legacy minus AI: <strong>${fmt(r.difference_pp)} percentage points</strong></p><p class="small-note">${r.note}</p>`;$('export-cds').disabled=false;}catch(e){$('cds-error').textContent=e.message;}finally{$('simulate').disabled=false;}};
$('export-cds').onclick=()=>download('epic-cds-simulation.json',JSON.stringify(simulation,null,2),'application/json');
demo();
