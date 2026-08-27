import os,sys,itertools,numpy as np,pandas as pd
sys.path.insert(0,'research/weekly_edge/src')
from run_we_w51c import dd_profile
R='.'
d=pd.read_csv('runs/WE_W76_FORWARD2026/out/streams_extended.csv'); d['date']=pd.to_datetime(d['date'])
cl=pd.read_csv('runs/WE_W79_CLIQUE/out/members.csv')
nf=pd.read_csv('runs/WE_W93_NETFUSE/out/series.csv'); nf['date']=pd.to_datetime(nf['date'])
assert (d['date'].values==nf['date'].values).all()
ds=d['date']; iso=ds.dt.isocalendar()
wk=(iso['year'].astype(str)+'-W'+iso['week'].astype(str).str.zfill(2)).to_numpy()
P1=d['P1'].to_numpy(); BM=cl['BMOM'].to_numpy(); X9=cl['X9a'].to_numpy(); NF=nf['NETFUSE_1'].to_numpy()
# candidate-specific cost per week (W89 FACTs)
C={'P1':14.52*11.12,'BMOM':12.99*4.90,'X9a':14.55*10.79,'NETFUSE_1':14.52*18.28}
OBJ={
 'P1 (1 unit)':            (P1, C['P1']),
 'BMOM alone (1 ctr)':     (BM, C['BMOM']),
 'X9a alone (1 unit)':     (X9, C['X9a']),
 '1B:2X  (3 nominal)':     (BM+2*X9, C['BMOM']+2*C['X9a']),
 '2B:3X  (5 nominal)':     (2*BM+3*X9, 2*C['BMOM']+3*C['X9a']),
 'NETFUSE_1 (1 unit)':     (NF, C['NETFUSE_1']),
}
PER={'FULL 22-07..26-07':np.ones(len(ds),bool),
     'trail 24m':(ds>=pd.Timestamp('2024-08-01')).to_numpy(),
     'trail 12m':(ds>=pd.Timestamp('2025-08-01')).to_numpy(),
     '2026 YTD':(ds.dt.year==2026).to_numpy()}
def pan(v,m,cw):
    w=pd.Series(v[m]).groupby(wk[m]).sum().to_numpy()-cw
    dp=dd_profile(w); stk=max((len(list(g)) for c,g in itertools.groupby(w<0) if c),default=0)
    return dict(nwk=len(w),wkpos=100*float((w>0).mean()),weekly=float(w.mean()),
                med=float(np.median(w)),maxdd=dp['maxdd'],top5=dp['dd_mean_top5'],
                worst=float(w.min()),streak=stk,ann=52*float(w.mean()),
                t=float(w.mean())/max(w.std(ddof=1)/np.sqrt(len(w)),1e-9))
rows=[]
for k,(v,cw) in OBJ.items():
    for p,m in PER.items():
        a=pan(v,m,cw); rows.append(dict(obj=k,period=p,**a))
T=pd.DataFrame(rows)
for p in PER:
    print(f"\n{'='*118}\n=== {p}\n{'='*118}")
    print(f"{'object':<22}{'wks':>5}{'wk $':>9}{'ann $':>11}{'wk+%':>8}{'med wk':>9}{'t':>7}{'maxDD':>10}{'top5DD':>9}{'worst':>10}{'strk':>6}")
    for k in OBJ:
        a=T[(T.obj==k)&(T.period==p)].iloc[0]
        print(f"{k:<22}{a.nwk:>5.0f}{a.weekly:>9,.0f}{a.ann:>11,.0f}{a.wkpos:>7.1f}%{a.med:>9,.0f}{a.t:>7.2f}{a.maxdd:>10,.0f}{a.top5:>9,.0f}{a.worst:>10,.0f}{a.streak:>6.0f}")
print(f"\n{'='*118}\n=== AT MATCHED RISK: each scaled so its FULL-WINDOW max drawdown = $20,245, then income\n{'='*118}")
print(f"{'object':<22}{'scale':>7}{'ann FULL':>12}{'ann t24':>12}{'ann t12':>12}{'ann 2026':>12}{'worst wk':>11}")
for k,(v,cw) in OBJ.items():
    f=pan(v,PER['FULL 22-07..26-07'],cw); s=20245.0/f['maxdd']
    a24=pan(v,PER['trail 24m'],cw); a12=pan(v,PER['trail 12m'],cw); a26=pan(v,PER['2026 YTD'],cw)
    print(f"{k:<22}{s:>7.2f}{s*f['ann']:>12,.0f}{s*a24['ann']:>12,.0f}{s*a12['ann']:>12,.0f}{s*a26['ann']:>12,.0f}{s*f['worst']:>11,.0f}")
print("\n=== per-year weekly $ (candidate-specific cost)")
yr=ds.dt.year.to_numpy()
print(f"{'object':<22}"+''.join(f"{y:>10}" for y in sorted(set(yr))))
for k,(v,cw) in OBJ.items():
    print(f"{k:<22}"+''.join(f"{pan(v,yr==y,cw)['weekly']:>10,.0f}" for y in sorted(set(yr))))
T.to_csv('runs/WE_W89_CANDCOST/out/head_to_head.csv',index=False)
