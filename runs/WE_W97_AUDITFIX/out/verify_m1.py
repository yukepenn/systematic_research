import sys,itertools,numpy as np,pandas as pd
sys.path.insert(0,'research/weekly_edge/src')
from run_we_w51c import dd_profile
d=pd.read_csv('runs/WE_W76_FORWARD2026/out/streams_extended.csv'); d['date']=pd.to_datetime(d['date'])
cl=pd.read_csv('runs/WE_W79_CLIQUE/out/members.csv')
ds=d['date']; iso=ds.dt.isocalendar()
wk=(iso['year'].astype(str)+'-W'+iso['week'].astype(str).str.zfill(2)).to_numpy()
P1=d['P1'].to_numpy(); BM=cl['BMOM'].to_numpy(); X9=cl['X9a'].to_numpy()
DDT=20245.0; cB,cX,cP=12.99*4.90,14.55*10.79,14.52*11.12
def pan(v,m,cw):
    w=pd.Series(v[m]).groupby(wk[m]).sum().to_numpy()-cw
    if len(w)<8: return None
    dp=dd_profile(w)
    return dict(wkpos=100*float((w>0).mean()),weekly_dd=float(w.mean())*DDT/max(dp['maxdd'],1e-9),top5=dp['dd_mean_top5'])
ends=pd.date_range(ds.min()+pd.DateOffset(months=24),ds.max(),freq='ME')
def gate(v,cv,base,cb,s):
    c=dict(m=0,w=0,dd=0,a=0,n=0)
    for e in ends:
        m=np.asarray((ds>e-pd.DateOffset(months=24))&(ds<=e))
        if m.sum()<300: continue
        a=pan(v*s,m,cv*s); b=pan(base,m,cb)
        if a is None or b is None: continue
        c['n']+=1
        x1=a['weekly_dd']>b['weekly_dd']; x2=a['wkpos']>b['wkpos']; x3=a['top5']<b['top5']
        c['m']+=x1;c['w']+=x2;c['dd']+=x3;c['a']+=(x1 and x2 and x3)
    n=max(c['n'],1); return {k:100*v_/n for k,v_ in c.items() if k!='n'}
print("=== CLAIM 1: are two of three legs SCALE-INVARIANT?  (2:3 basket, one 24m window)")
v=2*BM+3*X9; cv=2*cB+3*cX
m=np.asarray((ds>ends[10]-pd.DateOffset(months=24))&(ds<=ends[10]))
for s in (0.05,0.2,1.0,7.3):
    a=pan(v*s,m,cv*s)
    print(f"   scale {s:>5.2f}   weekly_dd {a['weekly_dd']:.10f}   wkpos {a['wkpos']:.10f}   top5 {a['top5']:>12,.2f}")
print("\n=== CLAIM 2: ALL-THREE vs the DIVISOR (this is the number I quoted the owner)")
print(f"{'basket':<10}{'nominal':>9}{'peak':>7}" + "".join(f"{'s='+str(x):>9}" for x in (0.20,0.25,0.333,0.50)))
PEAK={(1,1):3,(1,2):5,(2,3):8,(1,3):7,(2,1):4}
NOM={(1,1):2,(1,2):3,(2,3):5,(1,3):4,(2,1):3}
rows=[]
for nb,nx in [(1,1),(1,2),(2,3),(1,3),(2,1)]:
    v=nb*BM+nx*X9; cv=nb*cB+nx*cX
    line=f"{f'{nb}:{nx}':<10}{NOM[(nb,nx)]:>9}{PEAK[(nb,nx)]:>7}"
    for s in (0.20,0.25,1/3,0.50):
        line+=f"{gate(v,cv,P1,cP,s)['a']:>8.0f}%"
    rows.append((nb,nx,line))
    print(line)
print("\n=== CLAIM 3: the three candidate UNITS, each basket divided by its OWN")
print(f"{'basket':<10}{'NOMINAL (published)':>22}{'PEAK contracts':>18}{'time-weighted':>16}")
TW={(1,1):0.344,(1,2):0.498,(2,3):0.842}; TWP1=0.152
for nb,nx in [(1,1),(1,2),(2,3)]:
    v=nb*BM+nx*X9; cv=nb*cB+nx*cX
    gn=gate(v,cv,P1,cP,1.0/NOM[(nb,nx)])['a']
    gp=gate(v,cv,P1,cP,2.0/PEAK[(nb,nx)])['a']     # P1's own peak is 2
    gt=gate(v,cv,P1,cP,TWP1/TW[(nb,nx)])['a']
    print(f"{f'{nb}:{nx}':<10}{gn:>21.0f}%{gp:>17.0f}%{gt:>15.0f}%")
print("\n=== CLAIM 4: does the ORACLE battery still pass at the scales the table uses?")
for s in (0.20,0.25,1/3,0.50,1.0,2.0):
    o=gate(P1+200.0,cP,P1,cP,s)['a']
    print(f"   P1 + $200/session at scale {s:>5.3f}: ALL-THREE {o:>5.0f} %")
