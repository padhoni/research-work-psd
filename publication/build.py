"""Generate synchronized proof of concept, suggested paper text, and figures.
Run from project root: python publication/build.py
The journal manuscript is never opened or modified by this script.
"""
import csv
import hashlib
import html
import json
import platform
import shutil
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
import scipy
from analysis import analyze, simulate, DEMO
from simulation_study import run_study

OUT = ROOT/'publication'
FIG = OUT/'figures'
REFERENCES = [
    ('SciPy paired t-test and confidence intervals', 'https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_rel.html'),
    ('NumPy random-stream compatibility', 'https://numpy.org/doc/stable/reference/random/compatibility.html'),
    ('NASA Task Load Index manual', 'https://humansystems.arc.nasa.gov/groups/TLX/downloads/TLX_pappen_manual.pdf'),
    ('ASA Statement on p-Values: Context, Process, and Purpose', 'https://doi.org/10.1080/00031305.2016.1154108'),
    ('Morris, White, Crowther (2019). Using simulation studies to evaluate statistical methods', 'https://doi.org/10.1002/sim.8086'),
]

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def compact(result): return {k:v for k,v in result.items() if k != 'rows'}

def collect():
    original_path=ROOT/'examples/documentation_original.csv'
    original_path.write_text(DEMO)
    data_path=ROOT/'examples/documentation.csv'
    a=compact(analyze(DEMO))
    b=compact(analyze(data_path.read_text()))
    if b['n'] != 5000:
        raise ValueError('Publication configuration requires the preserved 5,000-row dataset.')
    return dict(schema_version='2.0',study_type='Simulation-based proof of concept; no clinical deployment',
        software={'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
        data_sha256={'examples/documentation_original.csv':digest(original_path),'examples/documentation.csv':digest(data_path)},
        generator_metadata=json.loads((ROOT/'examples/documentation.metadata.json').read_text()),
        original_example=a,large_example=b,cds=simulate(),monte_carlo=run_study(),
        exclusions=['No measured burnout, NASA-TLX, diagnostic accuracy, medication safety, or patient engagement outcomes.',
        'No live Epic connection, ambient scribe, or CDS Hooks service is implemented.',
        'The screenshot-derived 72%, six-month trends, burnout percentages, F1, and error-rate claims are not outputs of this experiment.'])

def suggested_sections(r):
    a,b,c,m=r['original_example'],r['large_example'],r['cds'],r['monte_carlo']
    g,h=c['groups'];sc=m['scenarios'];null=[s for s in sc if s['true_difference']==0]
    return [
      ('IV. Results: simulation-based prototype evaluation',
       'The prototype was evaluated using synthetic data and reproducible numerical experiments. No real clinicians were enrolled, no Epic deployment was evaluated, and no clinical effectiveness or documentation-quality outcomes were measured. Numerical estimates below describe the supplied examples or the specified generating models.'),
      ('A. Worked paired documentation-time example',
       f"For the original five synthetic clinician pairs, mean pre- and post-intervention times were {a['pre']:.2f} and {a['post']:.2f} minutes. The mean paired reduction was {a['difference']:.2f} minutes (95% Student t confidence interval [CI], {a['ci'][0]:.3f}–{a['ci'][1]:.3f}), equivalent to an {a['reduction']:.2f}% relative reduction. The two-sided paired test yielded t({a['df']}) = {a['t']:.3f}, p = {a['p']:.6g}; Cohen’s dz was {a['dz']:.3f}. The fixed example was selected for illustration; its narrow variation and large effect size do not establish a plausible clinical effect or provide evidence about a clinician population."),
      ('B. Expanded synthetic dataset',
       f"The 5,000-row demonstration dataset retained the five original pairs and added 4,995 generated pairs. Its mean pre- and post-intervention times were {b['pre']:.3f} and {b['post']:.3f} minutes, respectively. The mean paired reduction was {b['difference']:.3f} minutes (95% CI, {b['ci'][0]:.3f}–{b['ci'][1]:.3f}), corresponding to an {b['reduction']:.2f}% relative reduction. The paired statistic was t({b['df']}) = {b['t']:.3f}, with Cohen’s dz = {b['dz']:.3f}. The numerical p-value underflowed to zero in double-precision computation and is reported as below numerical precision, rather than as an exact zero. These calculations demonstrate processing of a larger synthetic input; the nominal CI and p-value are conditional model summaries, not empirical evidence of clinical benefit."),
      ('C. Synthetic CDS override counts',
       f"Independent binomial counts were generated for two groups of {c['n']:,} hypothetical alerts using assumed override probabilities of {c['legacy_probability']:.2f} and {c['ai_probability']:.2f}. With NumPy default_rng and seed {c['seed']}, the generated counts were {g['overrides']:,} and {h['overrides']:,}, giving rates of {g['rate']:.2f}% (Wilson 95% CI, {g['ci'][0]:.2f}–{g['ci'][1]:.2f}%) and {h['rate']:.2f}% (Wilson 95% CI, {h['ci'][0]:.2f}–{h['ci'][1]:.2f}%). The difference was {c['difference_pp']:.2f} percentage points. This difference reflects the input assumptions. The simulation does not contain monthly observations, proactive interaction events, diagnostic labels, or measured medication safety outcomes."),
      ('D. Repeated numerical simulation',
       f"A separate Monte Carlo experiment evaluated the paired-difference t procedure in {m['scenario_count']} scenarios with {m['repetitions']:,} repetitions per scenario. Independent normal differences were generated for sample sizes 5, 50, and 332, true means −0.50, 0, 0.50, and 0.95 minutes, and standard deviations 0.65 and 1.30 minutes. Empirical 95% CI coverage ranged from {100*min(s['coverage'] for s in sc):.1f}% to {100*max(s['coverage'] for s in sc):.1f}%. Across null scenarios, rejection at the two-sided 0.05 level ranged from {100*min(s['rejection_rate'] for s in null):.1f}% to {100*max(s['rejection_rate'] for s in null):.1f}%. The largest estimated Monte Carlo standard error for coverage was {100*max(s['coverage_mcse'] for s in sc):.2f} percentage points. Scenario-level bias, coverage, rejection rates, and Monte Carlo standard errors are supplied in monte_carlo.csv. This evaluates numerical behavior under the test’s normality assumptions, not robustness to clinical confounding or evidence that AI is effective."),
      ('E. Interpretation and scope',
       'The results demonstrate reproducible descriptive and inferential calculations for specified synthetic inputs. The application does not train or evaluate an AI model. Burnout, workload, documentation quality, patient engagement, diagnostic accuracy, and drug-interaction errors were not measured. Clinical utility and generalizability require a separate study using appropriately collected data and a design capable of addressing confounding and repeated observations.'),
    ]

def methods(r):
    return [
      ('Purpose and scope', 'This proof of concept implements a local statistical evaluation dashboard and a reproducible simulation pipeline. Its purpose is to verify calculations and illustrate conditional results. It is not a deployed Epic intervention or a new clinical efficacy study.'),
      ('Data and units', 'The analysis unit is a synthetic clinician-level paired value, expressed as mean active documentation minutes per encounter. The original five fixed pairs are retained in examples/documentation_original.csv. The expanded file examples/documentation.csv contains those five pairs plus 4,995 generated pairs; it is not a sample of recruited clinicians. No patient-level data are used.'),
      ('Expanded dataset generator', 'Python random.Random(42) generates pre = max(0.50, Normal(5.11, 0.50²)) and change = Normal(0.95, 0.65²); post = max(0.10, pre − change). Pre and change are independent draws, while pre and post are paired through the shared baseline. Both times are rounded to two decimal places after generating the pair. Negative changes are possible. This model was chosen for demonstration, not fitted to observed data; its outcome should not be interpreted as an estimated intervention effect. The original five rows are fixed, so the 5,000-row file is a mixed demonstration dataset rather than 5,000 identically generated replicates.'),
      ('Paired analysis', 'For d_i = pre_i − post_i, calculate mean(d), sample SD s_d, t = mean(d)/(s_d/√n), df = n − 1, and a two-sided p-value. The 95% CI is mean(d) ± t_(0.975,df) × s_d/√n. Relative reduction is 100 × (mean(pre) − mean(post))/mean(pre). Cohen’s dz is mean(d)/s_d. Independent units and approximately normal differences are the inferential assumptions. Zero variance produces undefined inference; a zero pre mean produces undefined relative reduction. Invalid, incomplete, duplicate, negative, and nonfinite inputs are rejected. Missing data are not imputed.'),
      ('CDS count model', 'The current application uses two sequential NumPy default_rng(42).binomial(n=10000, p) draws with p=0.89 and p=0.34 and Wilson 95% intervals. These are group totals for synthetic independent alerts, not CDS Hooks messages or real audit logs. No deployment timeline or prediction accuracy is modeled. Counts are not interchangeable with clustered clinical alerts.'),
      ('Repeated simulation specification', 'Aim: assess numerical estimation and inference when paired differences are normal. Data generation: independent N(delta, sigma²) differences, with n in {5,50,332}, delta in {−0.50,0,0.50,0.95}, sigma in {0.65,1.30}, and 1,000 repetitions per scenario. Seed: 20260927 with a separate NumPy default_rng; traversal order is n, delta, sigma. Estimand: mean difference. Method: two-sided one-sample t-test of differences, algebraically equivalent to the paired test. Performance: bias, 95% CI coverage, and rejection probability at alpha=0.05, interpreted as Type I error only at delta=0 and as power otherwise. Monte Carlo SE is SD(estimates)/√R for bias and √[q(1−q)/R] for proportions. No seeds or scenarios were selected to obtain desired results. Sample size 332 is an illustrative simulation setting, not a measured survey cohort. This experiment is separate from the 5,000-row demonstration.'),
      ('Removed unsupported outcomes', 'The original 461.3→25.0 workload simulation was removed from the publication results: its scale was undocumented, an unbounded normal model could produce invalid scores, and workload was mislabeled as burnout. The app may analyze user-supplied 0–100 NASA-TLX values, but this package reports no workload or burnout experiment. The screenshot-derived 16→4.5-minute and six-month CDS series are archived, not presented as project findings. The original 72% total-workflow claim was also inconsistent with its listed task sums (25→9 minutes would be 64%).'),
      ('Interpretation of p-values', 'A p-value is conditional on the statistical model and null hypothesis; it does not establish causation, clinical importance, or the truth of an intervention claim. The large differences selected in a simulation can produce small p-values by construction. Extremely small values are shown in scientific notation or labeled below numerical precision. The previous claim that p < 0.0001 mathematically proves an AI benefit is withdrawn.'),
      ('Reproducibility and original-script differences', 'The original script used the legacy np.random.seed(42) stream, generated two workload arrays first, and then generated individual Bernoulli alert events. The current CDS model uses a new generator and direct binomial totals, so identical numeric seeds need not give identical realized rates. The scientific assumptions and algorithm changes are explicit; the revised documents use only the current pipeline’s results. Dataset hashes and package versions are recorded in publication/results.json. Archived files document the earlier state.'),
      ('Implementation and reproduction', f"The statistical engine is analysis.py; simulation_study.py defines the repeated experiment; publication/build.py generates this document, suggested Results text, figures, and the application results page. Run: python -m pip install -r requirements-publication.txt; then python publication/build.py. Start the dashboard with python server.py. Verify with python -m unittest discover -s tests -v. This build used Python {r['software']['python']}, NumPy {r['software']['numpy']}, and SciPy {r['software']['scipy']}; the complete environment is recorded in publication/environment.lock.txt. The journal manuscript itself is not modified by the pipeline."),
      ('Limitations', 'This is a software proof of concept with a limited numerical simulation. It does not establish a new statistical method or clinical benefit. The normal-difference experiment does not test nonnormality, selection bias, clinician clustering, longitudinal confounding, measurement error, or clinical safety. The application has no live EHR integration, ambient transcription model, authentication, or deployment-grade controls. A journal submission requires author review of novelty, scope, citations, declarations, and journal-specific requirements.'),
    ]

def figures(r):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
    a,b,c=r['original_example'],r['large_example'],r['cds']
    fig,axes=plt.subplots(1,2,figsize=(11,4.6))
    for ax,item,label in zip(axes,[a,b],['Fixed worked example (5 pairs)','Expanded demonstration (5,000 pairs)']):
        bars=ax.bar(['Pre','Post'],[item['pre'],item['post']],color=['#8c9e98','#17775d'],width=.55)
        ax.bar_label(bars,labels=[f"{item['pre']:.3f}",f"{item['post']:.3f}"],padding=5)
        ax.set(ylim=(0,6.3),ylabel='Mean minutes per encounter',title=label)
        ax.text(.5,.94,f"{item['reduction']:.2f}% relative reduction",ha='center',transform=ax.transAxes)
    fig.text(.5,.025,'Synthetic data; descriptive means. The two datasets are distinct and overlap in their first five rows.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.065,1,1));save(fig,'documentation_means',plt)
    fig,ax=plt.subplots(figsize=(7.5,4.8));groups=c['groups'];vals=[g['rate'] for g in groups]
    errors=[[g['rate']-g['ci'][0] for g in groups],[g['ci'][1]-g['rate'] for g in groups]]
    bars=ax.bar(['Legacy CDS scenario','AI-assisted CDS scenario'],vals,yerr=errors,capsize=5,color=['#8c9e98','#17775d'],width=.55)
    ax.bar_label(bars,labels=[f'{v:.2f}%' for v in vals],padding=8)
    ax.set(ylim=(0,105),ylabel='Simulated override rate (%)',title='Synthetic CDS counts; 10,000 alerts per group')
    fig.text(.5,.025,'Assumed probabilities: 0.89 and 0.34; seed 42. Error bars: Wilson 95% CIs.\nNot live telemetry or evidence of alert quality.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.09,1,1));save(fig,'cds_counts',plt)
    sc=r['monte_carlo']['scenarios'];fig,axes=plt.subplots(1,2,figsize=(11,4.8))
    for sd,marker in [(0.65,'o'),(1.3,'s')]:
        null=[s for s in sc if s['sd']==sd and s['true_difference']==0]
        for ax,key,error,title,target in [(axes[0],'coverage','coverage_mcse','95% CI coverage under the null',95),(axes[1],'rejection_rate','rejection_mcse','Type I error under the null',5)]:
            ax.errorbar([s['n'] for s in null],[100*s[key] for s in null],yerr=[1.96*100*s[error] for s in null],fmt=marker+'-',capsize=4,label=f'SD = {sd:g} min')
            ax.set(xscale='log',xticks=[5,50,332],xticklabels=['5','50','332'],xlabel='Pairs per simulated dataset',ylabel='Percent',title=title)
    for ax,target in zip(axes,[95,5]):ax.axhline(target,color='gray',ls='--',label='Nominal target');ax.legend(fontsize=8)
    fig.text(.5,.02,'Normal-difference model; 1,000 repetitions per scenario. Error bars: ±1.96 estimated Monte Carlo SE.\nAll 24 scenarios, including nonzero effects, are reported in monte_carlo.csv.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.09,1,1));save(fig,'monte_carlo_null',plt)

def save(fig,name,plt):
    for ext in ['png','pdf','svg']:fig.savefig(FIG/f'{name}.{ext}',dpi=300,facecolor='white')
    plt.close(fig)

def write_doc(path,title,sections,table=None,include_figures=True):
    from docx import Document
    from docx.shared import Inches,Pt
    doc=Document();doc.core_properties.title=title
    doc.styles['Normal'].font.name='Calibri';doc.styles['Normal'].font.size=Pt(11)
    doc.add_heading(title,0)
    doc.add_paragraph('Simulation-based proof of concept • No clinical effectiveness claims')
    for heading,text in sections:doc.add_heading(heading,level=1);doc.add_paragraph(text)
    if table:
        doc.add_heading('Original five synthetic pairs',level=1)
        t=doc.add_table(rows=1,cols=3);t.style='Light Shading Accent 1'
        for cell,value in zip(t.rows[0].cells,['Clinician ID','Pre (min)','Post (min)']):cell.text=value
        for row in csv.DictReader(DEMO.splitlines()):
            for cell,value in zip(t.add_row().cells,row.values()):cell.text=str(value)
    if include_figures:
        doc.add_heading('Figures generated from the same analysis',level=1)
        for name,caption in [('documentation_means','Figure 1. Synthetic documentation-time means; 5 and 5,000 pairs are distinct examples, not independent clinical cohorts.'),('cds_counts','Figure 2. Synthetic binomial override rates with Wilson 95% intervals; no clinical telemetry.'),('monte_carlo_null','Figure 3. Normal-model numerical validation. Error bars represent Monte Carlo uncertainty, not clinical uncertainty.')]:
            doc.add_picture(str(FIG/f'{name}.png'),width=Inches(6))
            doc.add_paragraph(caption)
    doc.add_heading('References and software sources',level=1)
    for name,url in REFERENCES:doc.add_paragraph(f'{name}. {url}')
    doc.save(path)

def main():
    OUT.mkdir(exist_ok=True)
    backup=ROOT/'archive/pre_sync/Proof of Concept.docx'
    if not backup.exists():
        backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/'Proof of Concept.docx',backup)
    r=collect();(OUT/'results.json').write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    with (OUT/'monte_carlo.csv').open('w',newline='') as f:
        rows=r['monte_carlo']['scenarios'];w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    figures(r)
    results=suggested_sections(r);method=methods(r)
    refs='\n'.join(f'- [{name}]({url})' for name,url in REFERENCES)
    (OUT/'Suggested_Results.md').write_text('# Suggested replacement Results section\n\nAuthor review required. This file does not modify the journal manuscript.\n\n'+'\n\n'.join(f'## {h}\n\n{p}' for h,p in results)+'\n\n## References for Methods and interpretation\n\n'+refs+'\n')
    (OUT/'Methods_and_Limitations.md').write_text('# Suggested Methods and limitations\n\n'+'\n\n'.join(f'## {h}\n\n{p}' for h,p in method)+'\n\n'+refs+'\n')
    write_doc(ROOT/'Proof of Concept.docx','Simulation-Based Evaluation Framework for EHR Documentation and CDS Scenarios',method+results,table=True)
    write_doc(OUT/'Suggested_Results.docx','Suggested replacement Results section — for author review',results)
    # One generated page replaces the earlier screenshot-transcription page.
    body=''.join(f'<section><h2>{html.escape(h)}</h2><p>{html.escape(p)}</p></section>' for h,p in results)
    for name in ['documentation_means','cds_counts','monte_carlo_null']:
        svg=(FIG/f'{name}.svg').read_text();body+='<section>'+svg[svg.index('<svg'):]+'</section>'
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Synchronized simulation results</title><style>body{font:16px/1.7 system-ui;background:#f5f7f3;color:#173c35;max-width:1000px;margin:32px auto;padding:0 20px}section{background:white;padding:22px;margin:20px 0;border:1px solid #dce4dc;border-radius:8px}svg{max-width:100%;height:auto}a{color:#166655}.notice{padding:16px;background:#fff1d8}</style><a href="/">← Research dashboard</a><h1>Synchronized simulation results</h1><p class="notice">Generated from the same pipeline as Proof of Concept.docx and the suggested paper Results section. All datasets are synthetic. The journal manuscript has not been edited.</p>'''+body+'<p>Rebuild with <code>python publication/build.py</code>. Source values: <code>publication/results.json</code>.</p></html>'
    (ROOT/'static/paper.html').write_text(page)
    tracked=['analysis.py','simulation_study.py','publication/build.py','requirements.txt','requirements-publication.txt','examples/generate_documentation.py','examples/documentation.metadata.json','Proof of Concept.docx','publication/results.json','publication/Suggested_Results.docx','publication/Suggested_Results.md','publication/Methods_and_Limitations.md','publication/monte_carlo.csv','static/paper.html','server.py','static/index.html','static/app.js','static/style.css','README.md','publication/Manuscript_Change_Guide.md','publication/environment.lock.txt']
    tracked += [str(p.relative_to(ROOT)) for p in sorted(FIG.glob('*'))]
    (OUT/'manifest.json').write_text(json.dumps({'sha256':{name:digest(ROOT/name) for name in tracked},'data_sha256':r['data_sha256']},indent=2)+'\n')
    print(json.dumps({'status':'generated','original_reduction':r['original_example']['reduction'],'large_reduction':r['large_example']['reduction'],'cds_rates':[g['rate'] for g in r['cds']['groups']],'monte_carlo_scenarios':r['monte_carlo']['scenario_count']},indent=2))

if __name__=='__main__':main()
