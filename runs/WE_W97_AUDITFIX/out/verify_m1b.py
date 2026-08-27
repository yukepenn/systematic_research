import sys,numpy as np,pandas as pd
sys.path.insert(0,'research/weekly_edge/src')
from run_we_w51c import dd_profile
d=pd.read_csv('runs/WE_W76_FORWARD2026/out/streams_extended.csv'); d['date']=pd.to_datetime(d['date'])
cl=pd.read_csv('runs/WE_W79_CLIQUE/out/members.csv')
ds=d['date']; iso=ds.dt.isocalendar()
wk=(iso['year'].astype(str)+'-W'+iso['week'].astype(str).str.zfill(2)).to_numpy()
P1=d['P1'].to_numpy(); BM=cl['BMOM'].to_numpy(); X9=cl['X9a'].to_numpy()
DDT=20245.0; cB,cX,cP=12.99*4.90,14.55*10.79,14.52*11.12
def wkser(v,m,cw): return pd.Series(v[m]).groupby(wk[m]).sum().to_numpy()-cw
def pan(v,m,cw):
    w=wkser(v,m,cw)
    if len(w)<8: return None
    dp=dd_profile(w)
    return dict(wkpos=100*float((w>0).mean()),weekly=float(w.mean()),
                weekly_dd=float(w.mean())*DDT/max(dp['maxdd'],1e-9),top5=dp['dd_mean_top5'])
ends=pd.date_range(ds.min()+pd.DateOffset(months=24),ds.max(),freq='ME')
ALL=np.ones(len(ds),bool)
print("=== PRINCIPLED SCALE: match each basket's FULL-WINDOW weekly $ to P1's, then run the gate")
print("    (no free choice - income is the thing the owner is buying, and drawdown is the price)")
p1w=pan(P1,ALL,cP)['weekly']
print(f"    P1 full-window weekly = ${p1w:,.0f}\n")
print(f"{'basket':<8}{'income scale':>14}{'money':>8}{'wk+%':>7}{'top5DD':>9}{'ALL-3':>8}"
      f"{'  full top5 @ that scale':>26}{'vs P1':>9}")
rows=[]
for nb,nx in [(1,1),(1,2),(2,3),(1,3),(2,1)]:
    v=nb*BM+nx*X9; cv=nb*cB+nx*cX
    s=p1w/pan(v,ALL,cv)['weekly']
    c=dict(m=0,w=0,dd=0,a=0,n=0)
    for e in ends:
        m=np.asarray((ds>e-pd.DateOffset(months=24))&(ds<=e))
        if m.sum()<300: continue
        a=pan(v*s,m,cv*s); b=pan(P1,m,cP)
        if a is None or b is None: continue
        c['n']+=1
        x1=a['weekly_dd']>b['weekly_dd']; x2=a['wkpos']>b['wkpos']; x3=a['top5']<b['top5']
        c['m']+=x1;c['w']+=x2;c['dd']+=x3;c['a']+=(x1 and x2 and x3)
    n=max(c['n'],1); g={k:100*v_/n for k,v_ in c.items() if k!='n'}
    ft=pan(v*s,ALL,cv*s)['top5']; fp=pan(P1,ALL,cP)['top5']
    print(f"{f'{nb}:{nx}':<8}{s:>14.3f}{g['m']:>7.0f}%{g['w']:>6.0f}%{g['dd']:>8.0f}%{g['a']:>7.0f}%"
          f"{ft:>26,.0f}{100*(ft/fp-1):>+8.1f}%")
    rows.append(dict(basket=f"{nb}:{nx}",income_scale=s,**g,full_top5=ft))
print(f"{'P1':<8}{1.0:>14.3f}{'-':>8}{'-':>7}{'-':>9}{'-':>8}{fp:>26,.0f}{0:>+8.1f}%")
pd.DataFrame(rows).to_csv('runs/WE_W89_CANDCOST/out/gate_by_unit.csv',index=False)
