"""Export graphs of the running program's default simulated results.
Run: MPLCONFIGDIR=/tmp/epic-matplotlib python3 results/create_graphs.py
Requires matplotlib and a running app at http://127.0.0.1:8766.
"""
from pathlib import Path
import json
import urllib.request
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

OUT = Path(__file__).resolve().parent
BASE = 'http://127.0.0.1:8766'
def request(path, payload=None):
    body = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(BASE+path, data=body, headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.load(response)

def main():
    demo=request('/api/demo')
    paired=request('/api/analyze',dict(csv=demo['csv'],metric='time',source='simulated'))
    cds=request('/api/simulate',dict(seed=42,n=10000,legacy=89,ai=34))
    (OUT/'graph_data.json').write_text(json.dumps(dict(paired=paired,cds=cds),indent=2))
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':12,'axes.titleweight':'bold','axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','pdf.fonttype':42})
    green,gray,ink='#16745D','#899D97','#173C35'
    def style(ax):
        ax.set_axisbelow(True)
        ax.grid(axis='y',color='#E5EBE7',linewidth=.7)
        ax.spines['left'].set_color('#B8C8BF');ax.spines['bottom'].set_color('#B8C8BF')
        ax.tick_params(colors=ink)
    def trajectories(ax):
        for i,row in enumerate(paired['rows']):
            ax.plot([0,1],[row['pre'],row['post']],color=gray,alpha=.75,lw=1.6)
            ax.scatter([0,1],[row['pre'],row['post']],c=[gray,green],s=42,zorder=3)
            ax.annotate(row['clinician_id'],(0,row['pre']),xytext=(-12,0),textcoords='offset points',ha='right',va='center',fontsize=9)
        ax.set(xticks=[0,1],xticklabels=['Pre-intervention','Post-intervention'],xlim=(-.4,1.25),ylim=(3.5,5.85),ylabel='Active documentation time (minutes)',title='A  |  Individual clinician pairs')
        style(ax)
    def means(ax):
        values=[paired['pre'],paired['post']]
        bars=ax.bar(['Pre-intervention','Post-intervention'],values,color=[gray,green],width=.52)
        ax.bar_label(bars,labels=[f'{v:.2f}' for v in values],padding=6,fontweight='bold')
        ax.set(ylim=(0,6.5),ylabel='Mean documentation time (minutes)',title='B  |  Mean documentation time')
        ax.text(.5,.94,f"{paired['reduction']:.2f}% relative reduction",transform=ax.transAxes,ha='center',va='top',color=green,fontweight='bold')
        style(ax)
    def differences(ax):
        diffs=[r['difference'] for r in paired['rows']]
        ax.scatter([-.10,-.05,0,.05,.10],diffs,color=gray,s=42,label='Individual paired differences',zorder=3)
        low,high=paired['ci']; mean=paired['difference']
        ax.errorbar([.55],[mean],yerr=[[mean-low],[high-mean]],fmt='D',color=green,capsize=7,elinewidth=2,markersize=7,label='Mean difference ± 95% CI')
        ax.axhline(0,color=gray,lw=1,ls='--')
        ax.set(xlim=(-.35,.95),ylim=(-.05,1.3),xticks=[0,.55],xticklabels=['Clinician differences','Mean and 95% CI'],ylabel='Minutes saved (pre − post)',title='C  |  Paired difference and uncertainty')
        ax.text(.5,.95,f"Mean {mean:.2f} min; 95% CI [{low:.3f}, {high:.3f}]\nt({paired['df']}) = {paired['t']:.3f}; two-sided p = {paired['p']:.3g}",transform=ax.transAxes,ha='center',va='top',fontsize=9)
        style(ax)
    def overrides(ax):
        groups=cds['groups']; vals=[g['rate'] for g in groups]
        errors=[[g['rate']-g['ci'][0] for g in groups],[g['ci'][1]-g['rate'] for g in groups]]
        bars=ax.bar(['Legacy CDS','AI-assisted CDS'],vals,color=[gray,green],width=.52,yerr=errors,capsize=6,error_kw={'elinewidth':1.5})
        ax.bar_label(bars,labels=[f'{v:.2f}%' for v in vals],padding=8,fontweight='bold')
        ax.set(ylim=(0,108),yticks=[0,20,40,60,80,100],ylabel='Alerts overridden (%)',title='D  |  Simulated CDS override rates')
        ax.text(.5,.96,f"{cds['difference_pp']:.2f} percentage-point difference",transform=ax.transAxes,ha='center',va='top',fontsize=9)
        style(ax)
    plotters=[trajectories,means,differences,overrides]
    fig,axes=plt.subplots(2,2,figsize=(12,10))
    for ax,plot in zip(axes.flat,plotters):plot(ax)
    fig.suptitle('EPIC research prototype: simulated results',fontsize=18,fontweight='bold',color=ink,y=.98)
    fig.text(.5,.945,'Documentation: 5 clinician pairs  •  CDS: 10,000 alerts per group, seed 42',ha='center',fontsize=10,color='#596D64')
    fig.subplots_adjust(left=.09,right=.97,bottom=.11,top=.88,hspace=.38,wspace=.28)
    fig.text(.09,.043,'All data are simulated; these figures demonstrate the method and do not establish clinical efficacy or causation.\nPanel B is descriptive. Panel C shows a Student t 95% CI; panel D shows Wilson 95% CIs for independent binomial groups.',fontsize=9,color='#596D64',linespacing=1.6)
    for ext in ['png','pdf','svg']:fig.savefig(OUT/f'epic_results.{ext}',dpi=300,facecolor='white')
    plt.close(fig)
    for name,plot in zip(['clinician_pairs','mean_documentation_time','paired_difference','cds_override_rates'],plotters):
        fig,ax=plt.subplots(figsize=(6.5,5))
        plot(ax)
        fig.text(.5,.02,'SIMULATED DATA · Method demonstration only',ha='center',fontsize=9,color='#596D64')
        fig.tight_layout(rect=(0,.055,1,1))
        for ext in ['png','svg']:fig.savefig(OUT/f'{name}.{ext}',dpi=300,facecolor='white')
        plt.close(fig)
    (OUT/'figure_caption.txt').write_text('Figure. Simulated outcomes from the EPIC research prototype. (A) Paired documentation times for five simulated clinicians from Proof of Concept.docx. (B) Mean pre- and post-intervention documentation times of 5.11 and 4.16 minutes, respectively, representing an 18.59% relative reduction. (C) Mean paired reduction of 0.95 minutes (95% Student t CI 0.888–1.012); two-sided paired t(4) = 42.485, p = 1.8348 × 10⁻⁶. (D) Synthetic CDS override rates of 89.37% and 33.15% generated using NumPy default_rng with seed 42, 10,000 alerts per group, and input probabilities of 0.89 and 0.34. Error bars in D are Wilson 95% confidence intervals. All data are simulated; these results do not establish clinical effectiveness or causality. NASA-TLX is omitted because the program has no default validated workload dataset.\n')
    print(json.dumps({'paired_mean':paired['difference'],'paired_ci':paired['ci'],'p':paired['p'],'cds_rates':[g['rate'] for g in cds['groups']],'output_directory':str(OUT)},indent=2))
if __name__=='__main__':main()
