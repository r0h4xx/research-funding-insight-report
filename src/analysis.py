"""Analysis for the insight report. Every number used in the report is written to results.json."""
import json, numpy as np, pandas as pd, statsmodels.api as sm
UP='data/raw/'
NAME_MAP={'CQUniversity':'Central Queensland University','RMIT University':'Royal Melbourne Institute of Technology',
          'The University of New England':'University of New England','The University of Newcastle':'University of Newcastle'}
c=pd.read_pickle('data/processed/completions.pkl'); e=pd.read_pickle('data/processed/enrolments.pkl')
c['Completions']=c.Completions.astype(float); e['Enrolment_Count']=e.Enrolment_Count.astype(float)
for d in (c,e):
    d['Year']=d.Year.astype(float).astype(int); d['Inst']=d.Institution.replace(NAME_MAP)
r=pd.read_excel(UP+'Research_block_grants_time_series_2021-2026.xlsx',sheet_name='Table 2',header=2)
r['HEP Name']=r['HEP Name'].str.strip()
t3=pd.read_excel(UP+'Research_block_grants_time_series_2021-2026.xlsx',sheet_name='Table 3',header=2)
R={}

R['audit']=dict(rbg_rows=len(r),rbg_years=[int(r.Year.min()),int(r.Year.max())],rbg_dups=int(r.duplicated(['HEP Code','Year','Program']).sum()),
  rbg_na=int(r.isna().sum().sum()),comp_rows=len(c),enr_rows=len(e),comp_na=int(c.isna().sum().sum()),enr_na=int(e.isna().sum().sum()),
  enr_neg_cells=int((e.Enrolment_Count<0).sum()),
  enr_total_2023=int(e[e.Year==2023].Enrolment_Count.sum()),enr_total_2024=int(e[e.Year==2024].Enrolment_Count.sum()),
  dom_comm_2024=int(e[(e.Year==2024)&(e.Citizenship=='Domestic')&(e.Commencing=='Commencing')].Enrolment_Count.sum()),
  add_rsp_2021=float(t3['Additional RSP'].sum()))
coh=r[r.Year==2025].drop_duplicates('HEP Name').set_index('HEP Name').Cohort
rb=r[r.Program.isin(['RTP','RSP'])]

tot=rb.pivot_table(index='Year',columns='Program',values='Amount',aggfunc='sum'); tot['Total']=tot.RTP+tot.RSP
R['rbg_total']={int(y):float(v) for y,v in tot.Total.items()}
R['rbg_rtp']={int(y):float(v) for y,v in tot.RTP.items()}; R['rbg_rsp']={int(y):float(v) for y,v in tot.RSP.items()}
cs=rb[rb.Year.between(2017,2025)].groupby(['Year','Cohort']).Amount.sum().unstack(); cs=cs.div(cs.sum(axis=1),axis=0)*100
R['cohort_share']={k:{int(y):round(v,2) for y,v in cs[k].items()} for k in cs}
# finding 1
hc=c[c.Detailed_Course_Level=='Postgraduate research']; he=e[e.Detailed_Course_Level=='Postgraduate research']
fund=rb[rb.Year==2025].groupby('HEP Name').Amount.sum(); rtp=rb[(rb.Year==2025)&(rb.Program=='RTP')].set_index('HEP Name').Amount
hdrc=hc[hc.Year.isin([2022,2023])].groupby(['Inst','Year']).Completions.sum().unstack().mean(axis=1)
enr=e[e.Year==2023].groupby('Inst').Enrolment_Count.sum()
df=pd.DataFrame({'coh':coh,'fund':fund,'rtp':rtp,'hdrc':hdrc,'enr':enr}).dropna()
g=df.groupby('coh')[['fund','rtp','hdrc','enr']].sum(); sh=g/g.sum()*100
R['f1_shares']=sh.round(2).to_dict(); R['f1_n_joined']=len(df)
R['f1_rtp_per_hdrc']=(g.rtp/g.hdrc).round(0).to_dict()
d=df[df.hdrc>=20].copy(); d['go8']=(d.coh=='Go8').astype(float); d['lh']=np.log(d.hdrc)
X=sm.add_constant(d[['lh','go8']]); m=sm.OLS(np.log(d.rtp),X).fit(); mr=m.get_robustcov_results('HC3')
ci=pd.DataFrame(mr.conf_int(),index=X.columns)
R['model']=dict(n=int(m.nobs),r2=round(m.rsquared,3),elasticity=round(m.params.lh,3),elast_ci=[round(v,2) for v in ci.loc['lh']],
   go8_mult=round(float(np.exp(m.params.go8)),2),go8_ci=[round(float(np.exp(v)),2) for v in ci.loc['go8']],
   excluded=df[df.hdrc<20].index.tolist(),const=float(m.params.const),b_lh=float(m.params.lh),b_go8=float(m.params.go8))
d['pred_ratio']=np.exp(m.resid)
sens=[]
def ent(n): return 'Adelaide University' if n in('The University of Adelaide','University of South Australia') else n
coh2=coh.copy(); coh2['Adelaide University']='Go8'
for alloc,yrs in [(2023,[2020,2021]),(2024,[2021,2022]),(2025,[2022,2023]),(2026,[2023,2024])]:
    hh=hc.assign(Inst=hc.Inst.map(ent)) if alloc==2026 else hc
    rt=r[(r.Program=='RTP')&(r.Year==alloc)].set_index('HEP Name').Amount
    h=hh[hh.Year.isin(yrs)].groupby(['Inst','Year']).Completions.sum().unstack().mean(axis=1)
    dd=pd.DataFrame({'rtp':rt,'h':h,'coh':coh2}).dropna(); dd=dd[dd.h>=20]
    XX=sm.add_constant(pd.DataFrame({'lh':np.log(dd.h),'go8':(dd.coh=='Go8').astype(float)}))
    mm=sm.OLS(np.log(dd.rtp),XX).fit(); cc=pd.DataFrame(mm.get_robustcov_results('HC3').conf_int(),index=XX.columns)
    sens.append(dict(alloc=alloc,yrs=f'{yrs[0]}-{str(yrs[1])[2:]}',n=len(dd),elast=round(mm.params.lh,2),mult=round(float(np.exp(mm.params.go8)),2),
        ci=[round(float(np.exp(v)),2) for v in cc.loc['go8']],r2=round(mm.rsquared,2)))
R['sensitivity']=sens
h2=hc[hc.Year.isin([2022,2023])].copy(); h2['coh']=h2.Inst.map(coh)
f=h2.groupby(['coh','Broad_Field_of_Education_Primary']).Completions.sum().unstack().fillna(0); f=f.div(f.sum(axis=1),axis=0)*100
R['f1_sci_health']=(f['Natural and Physical Sciences']+f['Health']).round(1).to_dict()
d.to_csv('output/model_institutions.csv')
# finding 2
com=e[e.Commencing=='Commencing']
hcom=com[com.Detailed_Course_Level=='Postgraduate research'].groupby(['Citizenship','Year']).Enrolment_Count.sum().unstack()
alld=com[com.Citizenship=='Domestic'].groupby('Year').Enrolment_Count.sum()
hcd=hc.groupby(['Citizenship','Year']).Completions.sum().unstack()
hen=he.groupby(['Citizenship','Year']).Enrolment_Count.sum().unstack()
R['f2']=dict(hdr_comm_dom={int(k):v for k,v in hcom.loc['Domestic'].items()},hdr_comm_os={int(k):v for k,v in hcom.loc['Overseas'].items()},
  all_dom_comm={int(k):v for k,v in alld.items()},hdr_comp_dom={int(k):v for k,v in hcd.loc['Domestic'].items()},
  hdr_comp_os={int(k):v for k,v in hcd.loc['Overseas'].items()},hdr_enr_dom={int(k):v for k,v in hen.loc['Domestic'].items()},
  hdr_enr_os={int(k):v for k,v in hen.loc['Overseas'].items()})
hh=com[(com.Detailed_Course_Level=='Postgraduate research')&(com.Citizenship=='Domestic')].copy(); hh['coh']=hh.Inst.map(coh)
k=hh.dropna(subset=['coh']).groupby(['coh','Year']).Enrolment_Count.sum().unstack(); R['f2_coh_chg']=((k[2024]/k[2020]-1)*100).round(1).to_dict()
u=hh.groupby(['Inst','Year']).Enrolment_Count.sum().unstack(); u=u[u.index.isin(coh.index)].dropna()
R['f2_unis']=dict(n=len(u),declined=int((u[2024]<u[2020]).sum()))
fl=hh.groupby(['Broad_Field_of_Education_Primary','Year']).Enrolment_Count.sum().unstack()
R['f2_field']={i:dict(y20=fl.loc[i,2020],y24=fl.loc[i,2024]) for i in fl.index if i in fl.index and not np.isnan(fl.loc[i,2020])}
# tableau
yrs=range(2020,2025)
def piv(df_,val,filt,col):
    x=df_[filt].groupby(['Inst','Year',col])[val].sum().unstack(col); return x
p=[]
p.append(hc.groupby(['Inst','Year','Citizenship']).Completions.sum().unstack().add_prefix('HDR_completions_'))
p.append(com[com.Detailed_Course_Level=='Postgraduate research'].groupby(['Inst','Year','Citizenship']).Enrolment_Count.sum().unstack().add_prefix('HDR_commencing_'))
p.append(e.groupby(['Inst','Year']).Enrolment_Count.sum().rename('Total_enrolments').to_frame())
panel=pd.concat(p,axis=1).reset_index().rename(columns={'Inst':'Institution'})
rp=rb.pivot_table(index=['HEP Name','Year'],columns='Program',values='Amount',aggfunc='sum').reset_index().rename(columns={'HEP Name':'Institution','RTP':'RBG_RTP','RSP':'RBG_RSP'})
panel=panel.merge(rp,on=['Institution','Year'],how='outer')
panel['Cohort']=panel.Institution.map(coh).fillna(panel.Institution.map({'Adelaide University':'Go8'})).fillna('Not RBG-funded')
panel.sort_values(['Institution','Year']).to_csv('output/institution_year_panel.csv',index=False)
json.dump(R,open('results.json','w'),indent=1,default=float)
print(json.dumps({k:R[k] for k in ['audit','f1_shares','f1_rtp_per_hdrc','model','sensitivity','f1_sci_health','f2_coh_chg','f2_unis']},indent=1,default=float))
