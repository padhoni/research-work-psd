"""Reference-style CDS figure using canonical simulation outputs.
Run: MPLCONFIGDIR=/tmp/epic-matplotlib python publication/reference_style/create_cds_chart.py
"""
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.ticker import MultipleLocator

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
r=json.loads((ROOT/'publication/results.json').read_text())['cds']
groups=r['groups']
assert r['source']=='simulated'
assert all(g['total']==10000 and g['ci'][0]<=g['rate']<=g['ci'][1] for g in groups)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':17,'axes.titleweight':'bold','axes.labelsize':12,'axes.labelweight':'bold','svg.fonttype':'none','pdf.fonttype':42})
orange,blue='#F4C783','#0072B2'
fig,ax=plt.subplots(figsize=(10,6.8))
values=[g['rate'] for g in groups]
x=[0,1]
ax.bar(x,values,width=.47,color=orange,edgecolor='#433826',linewidth=1.4,zorder=2)
errors=[[g['rate']-g['ci'][0] for g in groups],[g['ci'][1]-g['rate'] for g in groups]]
ax.errorbar(x,values,yerr=errors,fmt='none',ecolor=blue,elinewidth=2,capsize=9,capthick=2,zorder=3)
for i,g in enumerate(groups):
    ax.text(i,g['rate']-7,f"{g['rate']:.2f}%",ha='center',va='top',fontsize=17,fontweight='bold')
    ax.text(i,g['rate']-14,f"{g['overrides']:,}/{g['total']:,}",ha='center',va='top',fontsize=11)
    ax.text(i,g['ci'][1]+2,f"95% CI: {g['ci'][0]:.2f}%–{g['ci'][1]:.2f}%",ha='center',va='bottom',fontsize=10,color=blue)
ax.set(xticks=x,xticklabels=['Legacy CDS scenario','AI-assisted CDS scenario'],ylabel='Alert override rate (%)',xlabel='Simulated scenario',ylim=(0,100),xlim=(-.55,1.55))
ax.yaxis.set_major_locator(MultipleLocator(10))
ax.set_axisbelow(True);ax.grid(axis='y',color='#d0d0d0',linewidth=1)
for spine in ax.spines.values():spine.set_color('#c7c7c7')
ax.legend(handles=[Patch(facecolor=orange,edgecolor='#433826',label='Generated override rate'),Line2D([0],[0],color=blue,marker='|',markersize=12,lw=2,label='Wilson 95% confidence interval')],loc='upper right',frameon=False,fontsize=10)
fig.suptitle('Simulated CDS Alert Override Rates',fontsize=19,fontweight='bold',y=.975)
fig.text(.5,.918,f"10,000 hypothetical alerts per scenario | Seed {r['seed']} | Difference: {r['difference_pp']:.2f} percentage points",ha='center',fontsize=11)
fig.subplots_adjust(left=.10,right=.975,top=.865,bottom=.20)
fig.text(.5,.060,'Synthetic independent alerts; override probabilities of 0.89 and 0.34 were specified as model inputs.\nOverride frequency does not establish alert fatigue reduction or improved medication safety.',ha='center',fontsize=9.5,linespacing=1.6,color='#444444')
for ext in ['png','pdf','svg']:fig.savefig(OUT/f'cds_override_simulation.{ext}',dpi=300,facecolor='white')
plt.close(fig)
with (OUT/'cds_override_simulation.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['scenario','overrides','alerts','rate_percent','wilson_ci_lower_percent','wilson_ci_upper_percent'])
    for g in groups:w.writerow([g['name'],g['overrides'],g['total'],g['rate'],*g['ci']])
(OUT/'cds_override_caption.txt').write_text('''Fig. X. Simulated CDS alert override rates. Two groups of 10,000 hypothetical alerts were generated using assumed override probabilities of 0.89 and 0.34 and NumPy default_rng with seed 42. The generated rates were 89.37% (8,937/10,000) in the legacy CDS scenario and 33.15% (3,315/10,000) in the AI-assisted CDS scenario, a difference of 56.22 percentage points. Blue error bars represent Wilson 95% confidence intervals of 88.75%–89.96% and 32.23%–34.08%, respectively, assuming independent alerts. These differences reflect the input assumptions and do not establish a reduction in alert fatigue or an improvement in clinical safety. No deployment timeline or proactive interaction outcomes were modeled.\n''')
print('Created CDS chart: PNG (300 dpi), PDF, SVG, underlying CSV, and figure caption.')
