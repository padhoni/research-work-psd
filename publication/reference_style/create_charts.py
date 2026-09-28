"""Generate reference-style figures for the revised paragraph, without editing the paper."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
r=json.loads((ROOT/'publication/results.json').read_text())['large_example']
b=json.loads((ROOT/'publication/literature_comparison/source_data.json').read_text())['burnout']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':13,'axes.titleweight':'bold','axes.labelweight':'bold','svg.fonttype':'none','pdf.fonttype':42})
RED,GREEN='#d9534f','#5cb85c'

def panel(ax,values,category,ylabel,ylim,title,labels,legend_labels,note):
    for x,value,color,label,text in zip([-.18,.18],values,[RED,GREEN],legend_labels,labels):
        bars=ax.bar(x,value,width=.35,color=color,edgecolor='black',linewidth=1.2,label=label)
        ax.bar_label(bars,labels=[text],padding=6,fontsize=12,fontweight='bold')
    ax.set(xlim=(-.7,.7),ylim=ylim,xticks=[0],xticklabels=[category],ylabel=ylabel,title=title)
    ax.tick_params(axis='x',length=0,labelsize=12)
    ax.set_axisbelow(True);ax.grid(axis='y',color='#cfcfcf',linewidth=1)
    for spine in ax.spines.values():spine.set_color('#c7c7c7')
    ax.legend(loc='upper right',frameon=False,fontsize=9)
    ax.text(.5,-.14,note,transform=ax.transAxes,ha='center',va='top',fontsize=10)

def documentation(ax,title):
    panel(ax,[r['pre'],r['post']],'Documentation','Mean minutes per encounter',(0,7.4),title,
          [f"{r['pre']:.3f} min",f"{r['post']:.3f} min"],['Pre (simulated)','Post (simulated)'],
          f"5,000 synthetic pairs | {r['reduction']:.2f}% relative reduction")
    ax.yaxis.set_major_locator(MultipleLocator(1))

def burnout(ax,title):
    panel(ax,[b['reported_pre_percent'],b['reported_post_percent']],'Burnout','Respondents reporting burnout (%)',(0,100),title,
          ['54.9%\n(28/51)','33.3%\n(17/51)'],['Before digital scribe','After digital scribe'],
          'External study: 51 paired respondents\n21.6 percentage-point decrease')
    ax.yaxis.set_major_locator(MultipleLocator(20))

def save(fig,name):
    for ext in ['png','pdf','svg']:fig.savefig(OUT/f'{name}.{ext}',dpi=300,facecolor='white')
    plt.close(fig)

fig,ax=plt.subplots(figsize=(8,5.6))
documentation(ax,'Simulated Documentation Time: Pre vs. Post')
fig.subplots_adjust(left=.13,right=.96,top=.89,bottom=.23)
fig.text(.5,.035,'Simulation only; no live Epic implementation. Order entry and chart review were not evaluated.',ha='center',fontsize=9)
save(fig,'documentation_burden')

fig,axes=plt.subplots(1,2,figsize=(12,6.3))
documentation(axes[0],'A. Documentation — project simulation')
burnout(axes[1],'B. Burnout — separate published study')
fig.subplots_adjust(left=.075,right=.975,top=.84,bottom=.27,wspace=.35)
fig.suptitle('Documentation Burden and Burnout: Separate Evidence Sources',fontsize=15,fontweight='bold',y=.965)
fig.text(.5,.05,'Panel B source: JAMIA Open (2025), PMID: 40620477. Burnout was not measured by this project.\nThe panels are not a shared cohort and do not establish that documentation savings caused reduced burnout.',ha='center',fontsize=9.5,linespacing=1.5)
save(fig,'documentation_and_burnout')

(OUT/'captions.txt').write_text('''DOCUMENTATION-ONLY FIGURE (for project Results)
Fig. X. Simulated documentation time before and after the modeled intervention. Across 5,000 synthetic clinician pairs, mean documentation time was 5.100 and 4.153 minutes per encounter, respectively, corresponding to an 18.58% relative reduction. Bars show descriptive means without error bars. Order-entry and chart-review times were not evaluated. These results illustrate the analytical method and do not establish clinical effectiveness.

COMBINED FIGURE (for an explicitly attributed simulation/literature comparison)
Fig. X. Documentation burden and burnout from separate evidence sources. (A) Project simulation: documentation time decreased from 5.100 to 4.153 minutes per encounter across 5,000 synthetic pairs (18.58% relative reduction). (B) External published pediatric digital-scribe study: reported burnout decreased from 54.9% (28/51) to 33.3% (17/51) among paired respondents, a 21.6 percentage-point decrease using the reported rounded percentages. Bars show descriptive summaries without error bars. Burnout was not measured in the present simulation. The panels represent different populations and do not establish a causal link between documentation savings and burnout.

Panel B source: Effect of a generative artificial intelligence digital scribe on pediatric provider documentation time, cognitive burden, and burnout. JAMIA Open (2025). PMID: 40620477. https://pubmed.ncbi.nlm.nih.gov/40620477/
''')
print('Generated documentation-only and combined figures in PNG, PDF, and SVG, with captions.')
