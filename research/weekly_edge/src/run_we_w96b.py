import os,sys,numpy as np,pandas as pd
sys.path.insert(0,'.')
import run_we_w01 as W1
from run_we_w01 import ROOT
from run_we_w17 import load_deep
from we_channels import session_clock, _mtod
D=load_deep('2022-01-01','2026-07-31 17:00',extend=True); W1.DEV_END=pd.Timestamp('2026-07-31').date()
n,sid,o,c=D['n'],D['sid'],D['o'],D['c']
hhmmss,seg,in_rth,_=session_clock(D)
so=pd.Series(o).groupby(sid).transform('first').to_numpy()
mt=_mtod(np.abs(c-so),seg,hhmmss,in_rth,mask=np.ones(n,bool))
df=pd.DataFrame(dict(hh=hhmmss//10000, hm=hhmmss, mt=mt, disp=np.abs(c-so)))
df=df[np.isfinite(df.mt)]
print("median mtod THRESHOLD (points) by entry hour, and the median |px-sessOpen| there:")
print(f"{'hour':>6}{'median mtod':>14}{'median |disp|':>15}{'ratio disp/mtod':>18}")
for h in [18,19,20,21,22,23,0,1,2,3,4,5,6,7,8,9]:
    g=df[df.hh==h]
    if not len(g): continue
    print(f"{h:>6}{g.mt.median():>14.2f}{g.disp.median():>15.2f}{(g.disp/g.mt.replace(0,np.nan)).median():>18.2f}")
g=df[(df.hm>=180100)&(df.hm<=180500)]
print(f"\n18:01-18:05 slots only: median mtod = {g.mt.median():.3f} pts  ({g.mt.median()/0.25:.1f} ticks)")
print(f"                        median |px-sessOpen| = {g.disp.median():.3f} pts")
print(f"   -> at the session open the 'typical displacement by this time of day' is near ZERO,")
print(f"      so ANY move crosses it. The rule degenerates to 'take the sign of the first move'.")
