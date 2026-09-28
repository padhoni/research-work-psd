"""Descriptive manuscript figures, kept separate from simulated paired analyses.
Run: MPLCONFIGDIR=/tmp/epic-matplotlib python3 paper_results.py
Optional: --workflow-mapping chart (default paragraph; both are provisional).
"""
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT/'results/paper/source_data.json'

def summarize(data, mapping='paragraph'):
    if mapping not in ('paragraph','chart'):
        raise ValueError('Workflow mapping must be paragraph or chart.')
    rows = data['workflow'][mapping]
    for row in rows:
        if not all(isinstance(row[k],(int,float)) and not isinstance(row[k],bool) and math.isfinite(row[k]) and row[k] >= 0 for k in ('pre','post')):
            raise ValueError('Workflow times must be finite and nonnegative.')
    pre, post = sum(r['pre'] for r in rows), sum(r['post'] for r in rows)
    cds = data['cds']
    if len(cds['months']) < 2 or not len(cds['months']) == len(cds['override_percent']) == len(cds['interaction_percent']):
        raise ValueError('Monthly CDS series must have matching lengths.')
    if any(not isinstance(x,(int,float)) or isinstance(x,bool) or not math.isfinite(x) or not 0 <= x <= 100 for field in ('override_percent','interaction_percent') for x in cds[field]):
        raise ValueError('CDS percentages must be finite and between 0 and 100.')
    def reduction(a,b): return 100*(a-b)/a if a else None
    return dict(provenance=data['provenance'],workflow_mapping=mapping,mapping_status='Provisional: screenshot paragraph and chart disagree.',workflow=[dict(r,reduction_percent=reduction(r['pre'],r['post'])) for r in rows],total_pre_minutes=pre,total_post_minutes=post,total_reduction_percent=reduction(pre,post),total_assumption='Sum assumes mutually exclusive tasks measured in comparable encounters.',override_drop_pp=cds['override_percent'][0]-cds['override_percent'][-1],override_relative_reduction_percent=reduction(cds['override_percent'][0],cds['override_percent'][-1]),interaction_increase_pp=cds['interaction_percent'][-1]-cds['interaction_percent'][0],burnout_drop_pp=data['burnout']['pre_percent']-data['burnout']['post_percent'],inference='Descriptive only. No inferential tests or confidence intervals calculated from aggregate values.')

def render(data, summary):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    out=ROOT/'results/paper'
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','pdf.fonttype':42})
    red,green,blue='#C75350','#39916B','#2674BA'
    figures=[]
    fig,ax=plt.subplots(figsize=(8,5))
    rows=summary['workflow']; x=list(range(len(rows)))
    documentation = next(r['reduction_percent'] for r in rows if r['category'] == 'Documentation')
    for offset,key,color,label in [(-.19,'pre',red,'Pre-intervention'),(.19,'post',green,'Post-intervention')]:
        bars=ax.bar([i+offset for i in x],[r[key] for r in rows],width=.36,color=color,label=label)
        ax.bar_label(bars,labels=[f"{r[key]:.1f} min" for r in rows],padding=4)
    ax.set(xticks=x,xticklabels=[r['category'] for r in rows],ylim=(0,20),ylabel='Minutes per encounter',title='Workflow time allocation: reported manuscript values')
    ax.legend(frameon=False)
    ax.set_axisbelow(True); ax.grid(axis='y',alpha=.2)
    fig.text(.5,.03,f"Total: {summary['total_pre_minutes']:g} → {summary['total_post_minutes']:g} min ({summary['total_reduction_percent']:.3g}% reduction); documentation: {documentation:.3f}%.\nSource unverified; provisional labels follow the screenshot {summary['workflow_mapping']}.",ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.10,1,1));figures.append(('workflow_time',fig))
    fig,axes=plt.subplots(2,1,figsize=(8,6.5),sharex=True)
    cds=data['cds']
    for ax,key,color,title in [(axes[0],'override_percent',red,'Alert override rate'),(axes[1],'interaction_percent',blue,'Proactive tool interaction rate')]:
        values=cds[key]
        ax.plot(cds['months'],values,'o-',color=color,lw=2)
        for month,value in zip(cds['months'],values):ax.annotate(f'{value:g}%',(month,value),xytext=(0,9),textcoords='offset points',ha='center',fontsize=9)
        ax.set(ylabel='Rate (%)',title=title,ylim=(0,105 if key=='override_percent' else 8))
        ax.grid(alpha=.2);ax.set_xticks(cds['months'])
    axes[1].set_xlabel('Deployment month')
    fig.suptitle('Six-month CDS trends: reported manuscript values',fontsize=13)
    fig.text(.5,.025,'Source and monthly denominators unverified. Lines connect supplied values; they are not model predictions.\nPanels use different, explicitly labeled scales. No uncertainty or clinical benefit is inferred.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.085,1,.97));figures.append(('cds_monthly_trends',fig))
    fig,ax=plt.subplots(figsize=(7,5))
    burnout=data['burnout'];bars=ax.bar(['Before digital scribe','After digital scribe'],[burnout['pre_percent'],burnout['post_percent']],color=[red,green],width=.55)
    ax.bar_label(bars,labels=['54.9%','33.3%'],padding=5)
    ax.set(ylim=(0,100),ylabel='Respondents reporting burnout (%)',title='Burnout: separate published study')
    ax.set_axisbelow(True);ax.grid(axis='y',alpha=.2)
    fig.text(.5,.025,'28/51 vs. 17/51 paired respondents; 21.6 percentage-point decrease (rounded percentages).\nSource: PMC12225174. Observational association; not the workflow or CDS cohort.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.09,1,1));figures.append(('burnout_published_study',fig))
    for name,fig in figures:
        for extension in ('png','pdf','svg'):fig.savefig(out/f'{name}.{extension}',dpi=300,facecolor='white')
        plt.close(fig)
    return [name for name,_ in figures]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--workflow-mapping',choices=['paragraph','chart'],default='paragraph')
    args=parser.parse_args()
    data=json.loads(SOURCE.read_text());summary=summarize(data,args.workflow_mapping)
    out=SOURCE.parent
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    names=render(data,summary)
    import html
    def embed(name):
        svg=(out/f'{name}.svg').read_text()
        return svg[svg.index('<svg'):]
    sections=''.join('<article>'+embed(name)+'</article>' for name in names)
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>EPIC manuscript results</title><style>body{font:16px/1.6 system-ui;background:#f5f7f3;color:#173c35;max-width:1000px;margin:30px auto;padding:0 18px}article{background:white;padding:20px;margin:24px 0;border:1px solid #dce4dc;border-radius:10px}svg{width:100%;height:auto}a{color:#166655}.notice{padding:16px;background:#fff1d8}button{padding:10px;cursor:pointer}</style><a href="/">← Research dashboard</a><h1>Manuscript results</h1><p class="notice">Transcribed summary values, not output from the five-clinician simulation. Workflow and CDS sources await verification. Workflow labels provisionally follow the '''+html.escape(args.workflow_mapping)+''' in the screenshot.</p><p><strong>Total workflow: 25 → 9 minutes, a 64% reduction.</strong> Documentation alone: 16 → 4.5 minutes, a 71.875% reduction. No p-values or confidence intervals are inferred from the supplied aggregate data.</p>'''+sections+'''<p>Burnout source: <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC12225174/">Effect of a generative artificial intelligence digital scribe on pediatric provider documentation time, cognitive burden, and burnout</a>.</p><p>The F1 = 0.71 and error rate &lt;4.8% claims still need model, dataset, denominator, and source details. Lower overrides and higher interaction rates alone do not establish diagnostic accuracy or safety.</p><button onclick="window.print()">Print / Save as PDF</button></html>'''
    (ROOT/'static/paper.html').write_text(page)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
