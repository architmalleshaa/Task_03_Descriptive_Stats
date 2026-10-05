from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from textwrap import fill
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':16,'axes.labelsize':11,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':False,'figure.facecolor':'white','axes.facecolor':'white'})
def finish(fig,ax,name,note):
 ax.set_axisbelow(True);ax.grid(axis='x',color='#e2e5e8',linewidth=.7)
 fig.text(.04,.025,note,fontsize=9,color='#4a5058',va='bottom')
 fig.tight_layout(rect=(0,.12,1,1));fig.savefig(OUT/name,dpi=160);plt.close(fig)
d=json.loads((ROOT/'verified_results/comparison/shared_column_statistics.json').read_text())
cols=['issue_msg_type_illuminating','attack_msg_type_illuminating','fundraising_cta_subtype_illuminating','incivility_illuminating']
names=['Issue','Attack','Fundraising','Incivility']
fig,ax=plt.subplots(figsize=(9,5.2));colors=['#2d5b85','#bd7934','#788855']
for i,(dataset,label) in enumerate([('ads','Ads'),('facebook','Facebook posts'),('twitter','Twitter posts')]):
 values=[d[c][dataset]['mean']*100 for c in cols];positions=[j+(i-1)*.24 for j in range(len(cols))]
 ax.barh(positions,values,height=.22,color=colors[i],label=label)
 for y,v in zip(positions,values):ax.text(v+.6,y,f'{v:.1f}',va='center',fontsize=9)
ax.set_yticks(range(4),names);ax.invert_yaxis();ax.set_xlim(0,62);ax.set_xlabel('Recorded positive labels, % of non-missing observations')
ax.set_title('Shared annotation rates in the supplied files',loc='left',pad=18);ax.legend(loc='lower right',frameon=False)
finish(fig,ax,'shared_labels.png','Sources: Task 3 CSVs. Denominators: ads 246,745; Facebook 19,009; Twitter 26,034.\nTwitter has 1,270 missing labels. Full-file periods and sampled populations differ; no platform effect is inferred.')
