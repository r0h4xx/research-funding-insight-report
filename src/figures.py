import json, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.ticker import FuncFormatter
for w in ['Regular','Bold','Italic']: fm.fontManager.addfont(f'/usr/share/fonts/truetype/crosextra/Carlito-{w}.ttf')
plt.rcParams.update({'font.family':'Carlito','font.size':10,'axes.spines.top':False,'axes.spines.right':False,
  'axes.edgecolor':'#555','axes.labelcolor':'#333','xtick.color':'#444','ytick.color':'#444','axes.titleweight':'bold',
  'axes.titlesize':11,'axes.titlelocation':'left','figure.dpi':200})
NAVY='#1F3A5F'; GREY='#A6ADB5'; TEAL='#2A8C82'; RED='#B5473A'; LIGHT='#D9DEE4'
R=json.load(open('results.json'))
def save(f,n): f.savefig(f'figures/{n}.png',bbox_inches='tight',dpi=220); plt.close(f)

# ---- Pipeline diagram (page 2) ----
f,ax=plt.subplots(figsize=(7.2,1.35)); ax.axis('off'); ax.set_xlim(-1.5,101); ax.set_ylim(0,20)
boxes=[(0,'Sources','3 official Dept of\nEducation files'),(20.5,'Extract','Pivot caches and\nRBG tables to CSV'),
 (41,'Clean & link','Name crosswalk,\nmerger, time lag'),(61.5,'Analyse','Shares, ratios,\nlog-log regression'),(82,'Communicate','Report charts and\nTableau dashboard')]
for x,t,s in boxes:
    ax.add_patch(matplotlib.patches.FancyBboxPatch((x,1),17.5,17,boxstyle='round,pad=0.2,rounding_size=1.2',fc='#EEF2F6',ec=NAVY,lw=0.8))
    ax.text(x+8.75,14,t,ha='center',va='center',weight='bold',color=NAVY,fontsize=10)
    ax.text(x+8.75,7,s,ha='center',va='center',fontsize=8.3,color='#333',linespacing=1.15)
for x in [17.9,38.4,58.9,79.4]: ax.annotate('',xy=(x+2.4,9.5),xytext=(x,9.5),arrowprops=dict(arrowstyle='->',color=NAVY,lw=1))
save(f,'pipeline')

# ---- Context (page 4) ----
f,(a1,a2)=plt.subplots(1,2,figsize=(7.4,2.7),gridspec_kw={'width_ratios':[1.05,1]})
yrs=list(range(2017,2027)); rtp=[R['rbg_rtp'][str(y)]/1e9 for y in yrs]; rsp=[R['rbg_rsp'][str(y)]/1e9 for y in yrs]
a1.bar(yrs,rtp,color=NAVY,width=0.7,label='Research Training Program (RTP)'); a1.bar(yrs,rsp,bottom=rtp,color=GREY,width=0.7,label='Research Support Program (RSP)')
a1.set_ylabel('$ billion (nominal)'); a1.set_title('Research block grants by program, 2017–2026',fontsize=10)
a1.annotate('2021: one-off $1.0b\nCOVID-19 RSP top-up',xy=(2021,2.99),xytext=(2021.7,3.05),fontsize=8,color='#333',arrowprops=dict(arrowstyle='-',color='#777',lw=0.6))
a1.set_ylim(0,3.4); a1.legend(frameon=False,fontsize=7.8,loc='upper center',bbox_to_anchor=(0.5,-0.1),ncol=1); a1.set_xticks(yrs[::1]); a1.set_xticklabels([str(y)[2:] if y!=2017 else '2017' for y in yrs],fontsize=8.5)
cs=R['cohort_share']; y9=list(range(2017,2026))
order=['Go8','ATN','non-aligned','IRU','RUN']; lab={'Go8':'Group of Eight','ATN':'ATN','non-aligned':'Non-aligned','IRU':'IRU','RUN':'RUN'}
for k in order:
    v=[cs[k][str(y)] for y in y9]; a2.plot(y9,v,color=NAVY if k=='Go8' else GREY,lw=2 if k=='Go8' else 1.2)
    a2.text(2025.2,{'Go8':v[-1],'ATN':16.2,'non-aligned':12.1,'IRU':8.0,'RUN':3.6}[k],f'{lab[k]} {v[-1]:.1f}%',va='center',fontsize=8,color=NAVY if k=='Go8' else '#555')
a2.set_ylim(0,70); a2.text(2017,-17,'2026 excluded: the Adelaide/UniSA merger reclassifies UniSA funding from ATN to Go8.',fontsize=7.6,color='#555'); a2.set_xlim(2017,2027.6); a2.set_ylabel('Share of total RBG (%)'); a2.set_title('Share of RBG funding by university group',fontsize=10)
a2.set_xticks(y9); a2.set_xticklabels([str(y)[2:] if y!=2017 else '2017' for y in y9],fontsize=8.5)
f.tight_layout(w_pad=2.5); save(f,'context')

# ---- Finding 1 ----
d=pd.read_csv('output/model_institutions.csv',index_col=0)
short={'The University of Melbourne':'Melbourne','Monash University':'Monash','The University of Sydney':'Sydney','University of New South Wales':'UNSW',
 'The University of Queensland':'Queensland','The Australian National University':'ANU','The University of Western Australia':'UWA','The University of Adelaide':'Adelaide',
 'Charles Darwin University':'Charles Darwin','Flinders University':'Flinders','Macquarie University':'Macquarie','Western Sydney University':'Western Sydney',
 'Victoria University':'Victoria Uni'}
m=R['model']
f,(b1,b2)=plt.subplots(1,2,figsize=(7.4,4.1),gridspec_kw={'width_ratios':[0.72,1.6]})
sh=R['f1_shares']; cats=[('enr','Students\n(all enrolments, 2023)'),('hdrc','HDR completions\n(2022–23 avg)'),('rtp','RTP funding\n(2025)'),('fund','Total RBG\n(2025)')]
vals=[sh[k]['Go8'] for k,_ in cats]
b1.barh(range(4)[::-1],vals,color=[GREY,GREY,NAVY,NAVY],height=0.6)
for i,v in zip(range(4)[::-1],vals): b1.text(v+1.5,i,f'{v:.0f}%',va='center',fontsize=9.5,weight='bold',color=NAVY if i<2 else '#444')
b1.set_yticks(range(4)[::-1]); b1.set_yticklabels([l for _,l in cats],fontsize=8.3); b1.set_xlim(0,80); b1.set_xticks([])
b1.spines['bottom'].set_visible(False); b1.set_title('Group of Eight share of…',fontsize=10)
go=d.go8==1
b2.scatter(d.hdrc[~go],d.rtp[~go]/1e6,s=22,color=GREY,edgecolor='white',lw=0.5,label='Other universities',zorder=3)
b2.scatter(d.hdrc[go],d.rtp[go]/1e6,s=30,color=NAVY,edgecolor='white',lw=0.5,label='Group of Eight',zorder=4)
xs=np.linspace(20,1150,100)
b2.plot(xs,np.exp(m['const']+m['b_lh']*np.log(xs))/1e6,color=GREY,lw=1,ls='--',zorder=2)
b2.plot(xs,np.exp(m['const']+m['b_go8']+m['b_lh']*np.log(xs))/1e6,color=NAVY,lw=1,ls='--',zorder=2)
b2.set_xscale('log'); b2.set_yscale('log')
b2.xaxis.set_major_formatter(FuncFormatter(lambda v,_:f'{v:,.0f}')); b2.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f'${v:,.0f}m' if v>=1 else f'${v:.1f}m'))
b2.set_xticks([25,50,100,250,500,1000]); b2.set_yticks([2,5,10,25,50,100])
b2.set_xlabel('HDR completions, average of 2022 and 2023 (log scale)'); b2.set_ylabel('RTP allocation, 2025 (log scale)')
off={'Charles Darwin':(-6,5,'right'),'Flinders':(-5,3,'right'),'Macquarie':(5,-9,'left'),'Victoria Uni':(5,-8,'left'),'Melbourne':(-6,4,'right'),'Monash':(0,7,'center'),'ANU':(-6,3,'right'),'UWA':(-6,2,'right'),'Adelaide':(5,-8,'left'),'Western Sydney':(5,-9,'left')}
for n,s in short.items():
    if n in d.index and s in off:
        dx,dy,ha=off[s]; b2.annotate(s,(d.loc[n,'hdrc'],d.loc[n,'rtp']/1e6),xytext=(dx,dy),textcoords='offset points',ha=ha,fontsize=7.6,color=NAVY if d.loc[n,'go8']==1 else '#555')
b2.annotate('Sydney, UNSW,\nQueensland',(d.loc['The University of Sydney','hdrc'],d.loc['The University of Sydney','rtp']/1e6),xytext=(8,-20),textcoords='offset points',fontsize=7.6,color=NAVY,linespacing=1.0)
b2.legend(frameon=False,fontsize=8,loc='upper left'); b2.set_title('RTP funding vs research completions, 39 universities',fontsize=10)
b2.text(0.98,0.04,f"Dashed lines: fitted model. At the same number of\ncompletions, Go8 line sits {m['go8_mult']:.2f}x higher.",transform=b2.transAxes,ha='right',fontsize=7.8,color='#444')
f.tight_layout(w_pad=1.5); save(f,'finding1')

# ---- Finding 2 ----
F=R['f2']; yy=[str(y) for y in range(2020,2025)]; x=list(range(2020,2025))
dc=[F['hdr_comm_dom'][y] for y in yy]; oc=[F['hdr_comm_os'][y] for y in yy]
f,(c1,c2)=plt.subplots(1,2,figsize=(7.4,3.7),gridspec_kw={'width_ratios':[1,1.15]})
c1.plot(x,dc,color=RED,lw=2,marker='o',ms=4); c1.plot(x,oc,color=TEAL,lw=2,marker='o',ms=4)
for s,col,v in ((dc,RED,'Domestic'),(oc,TEAL,'Overseas')):
    c1.text(2020.12,s[0]+(330 if v=='Domestic' else -700),f'{s[0]:,.0f}',fontsize=8,color=col,ha='left')
    c1.text(2024.12,s[-1]+(170 if v=='Overseas' else -230),f'{v} {s[-1]:,.0f}',fontsize=8.3,color=col,weight='bold')
c1.set_ylim(0,10500); c1.set_xlim(2019.7,2025.3); c1.set_xticks(x); c1.set_ylabel('Commencing HDR students (headcount)')
c1.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f'{v:,.0f}')); c1.set_title('New HDR students by citizenship',fontsize=10)
def idx(s,base='2020'): return [s[y]/s[base]*100 for y in yy]
lines=[(idx(F['hdr_comm_os']),TEAL,'Overseas HDR commencements'),(idx(F['hdr_comp_dom']),NAVY,'Domestic HDR completions'),
       (idx(F['all_dom_comm']),GREY,'All domestic commencements'),(idx(F['hdr_comm_dom']),RED,'Domestic HDR commencements')]
for s,col,l in lines:
    c2.plot(x,s,color=col,lw=2 if col!=GREY else 1.6,marker='o',ms=3.5)
    c2.text(2024.12,s[-1],f'{l}\n{s[-1]:.0f}',fontsize=7.8,color=('#6B7580' if col==GREY else col),va='center',linespacing=1.05)
c2.axhline(100,color='#999',lw=0.6,ls=':'); c2.set_ylim(70,160); c2.set_xlim(2019.8,2026.9); c2.set_xticks(x)
c2.set_ylabel('Index (2020 = 100)'); c2.set_title('Change since 2020, indexed',fontsize=10)
f.tight_layout(w_pad=2); save(f,'finding2')
print('ok')
