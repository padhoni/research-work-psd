"""Separate project simulation from an externally published burnout outcome.
Run: MPLCONFIGDIR=/tmp/epic-matplotlib python3 publication/literature_comparison/create_figure.py
This supplementary comparison does not change canonical project results.
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'results.json'
STUDY='https://pubmed.ncbi.nlm.nih.gov/40620477/'

def main():
    r=json.loads(SOURCE.read_text())['large_example']
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':12,'axes.titleweight':'bold','axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
    pre,post='#8A929B','#16785F'
    def style(ax):
        ax.set_axisbelow(True);ax.grid(axis='y',color='#E5E7EB',lw=.8)
        ax.spines['left'].set_color('#9AA1A9');ax.spines['bottom'].set_color('#9AA1A9')
    def documentation(ax):
        bars=ax.bar(['Pre (simulated)','Post (simulated)'],[r['pre'],r['post']],color=[pre,post],width=.56)
        ax.bar_label(bars,labels=[f"{r['pre']:.2f} min",f"{r['post']:.2f} min"],padding=7,fontweight='bold')
        ax.set(ylabel='Mean documentation time (minutes/encounter)',ylim=(0,6.6),title='A  Documentation burden')
        ax.text(.5,.94,f"{r['reduction']:.2f}% relative reduction",ha='center',va='top',transform=ax.transAxes,color=post,fontweight='bold')
        ax.text(.5,-.17,'PROJECT SIMULATION\n5,000 synthetic clinician pairs',ha='center',va='top',transform=ax.transAxes,fontsize=10,color='#334155')
        style(ax)
    def burnout(ax):
        bars=ax.bar(['Before scribe','After scribe'],[54.9,33.3],color=[pre,post],width=.56)
        ax.bar_label(bars,labels=['54.9%\n(28/51)','33.3%\n(17/51)'],padding=7,fontweight='bold')
        ax.set(ylabel='Respondents reporting burnout (%)',ylim=(0,100),title='B  Burnout prevalence')
        ax.text(.5,.94,'21.6 percentage-point decrease',ha='center',va='top',transform=ax.transAxes,color=post,fontweight='bold')
        ax.text(.5,-.17,'PUBLISHED STUDY — SEPARATE COHORT\n51 paired respondents; PMID: 40620477',ha='center',va='top',transform=ax.transAxes,fontsize=10,color='#334155')
        style(ax)
    fig,axes=plt.subplots(1,2,figsize=(12,6))
    documentation(axes[0]);burnout(axes[1])
    fig.suptitle('Documentation burden and burnout: distinct evidence sources',fontsize=15,fontweight='bold',y=.97)
    fig.subplots_adjust(left=.085,right=.98,bottom=.26,top=.83,wspace=.37)
    fig.text(.5,.045,'Panels describe different datasets and populations. Burnout was not measured by this project.\nDescriptive summaries only; no causal relationship between the two panels is established.',ha='center',fontsize=10,color='#475569')
    save(fig,'documentation_and_burnout');plt.close(fig)
    for name,plot in [('documentation_simulation_only',documentation),('burnout_published_study_only',burnout)]:
        fig,ax=plt.subplots(figsize=(6.5,5.4));plot(ax)
        fig.subplots_adjust(left=.17,right=.96,top=.88,bottom=.23)
        save(fig,name);plt.close(fig)
    caption=f'''Figure. Documentation burden and burnout from distinct evidence sources. (A) Project simulation: mean documentation time in {r['n']:,} synthetic clinician pairs was {r['pre']:.3f} minutes before and {r['post']:.3f} minutes after the simulated intervention, an {r['reduction']:.2f}% relative reduction. The synthetic generating assumptions determine these results; they are not observed clinical effects. (B) External published study: burnout was reported by 28/51 (54.9%) respondents before and 17/51 (33.3%) after digital-scribe use, a decrease of 21.6 percentage points using the reported rounded percentages. This is a separate cohort and is not an outcome measured by the project. Bars are descriptive summaries without inferential error bars. The panels do not establish that documentation savings caused a reduction in burnout.\n\nPanel B source: Effect of a generative artificial intelligence digital scribe on pediatric provider documentation time, cognitive burden, and burnout. JAMIA Open, 2025. PMID: 40620477. {STUDY}\n\nPlacement: the combined figure is appropriate only as an explicitly labeled simulation/literature comparison (e.g., Discussion). For a figure reporting only this project's Results, use documentation_simulation_only and state that burnout was not evaluated.\n'''
    (HERE/'figure_caption.txt').write_text(caption)
    (HERE/'source_data.json').write_text(json.dumps({'documentation':{'source':'project simulation','n':r['n'],'pre':r['pre'],'post':r['post'],'relative_reduction_percent':r['reduction'],'input_sha256':r['reproducibility']['input_sha256']},'burnout':{'source':STUDY,'cohort':'external study, 51 paired respondents','pre_count':28,'post_count':17,'denominator':51,'reported_pre_percent':54.9,'reported_post_percent':33.3,'reported_percentage_point_decrease':21.6},'interpretation':'Separate evidence sources; not joint project outcomes.'},indent=2))
    print('Created combined figure, separate panels, caption, and source data in '+str(HERE))

def save(fig,name):
    for ext in ('png','pdf','svg'):fig.savefig(HERE/f'{name}.{ext}',dpi=300,facecolor='white')

if __name__=='__main__':main()
