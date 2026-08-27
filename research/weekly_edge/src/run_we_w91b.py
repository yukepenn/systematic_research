import os,sys,numpy as np,pandas as pd
sys.path.insert(0,'.')
import run_we_w01 as W1
from run_we_w01 import ROOT
from run_we_w17 import load_deep
from run_we_w19 import MEMBERS,QS
from run_we_w38 import sfills
from we_fastctx import fast_build_context
L13=[6,8,10,12,14,16,18,20,22,24,26,28,30]
A=np.datetime64('2022-07-01'); B=np.datetime64('2026-08-01')
D=load_deep('2022-01-01','2026-07-31 17:00',extend=True); W1.DEV_END=pd.Timestamp('2026-07-31').date()
n,tarr,sid=D['n'],D['t'],D['sid']; X=fast_build_context(D)
z=np.load(os.path.join(ROOT,'runs','WE_W76_FORWARD2026','out','mem_ext.npz'))
mem,bmom,tilt=z['mem'],z['bmom'],z['tilt']
fb,sess_end=D['fb'],D['sess_end']
blocked=tarr>=sess_end[sid]-np.timedelta64(30*60,'s'); flatm=tarr>=sess_end[sid]-np.timedelta64(21*60,'s')
idx={v:k for k,v in enumerate(L13)}
ra=lambda x: np.where(x>=0,np.floor(x+0.5),np.ceil(x-0.5))
def hyst(M):
    tgt=np.zeros(n,np.int8)
    for i in range(n):
        p=0 if (i==0 or fb[i]) else tgt[i-1]; g=p
        if flatm[i]: g=0
        elif p==0:
            if not blocked[i]: g=1 if M[i]>=3.0 else (-1 if M[i]<=-3.0 else p)
        elif p>0: g=-1 if (M[i]<=-3.0 and not blocked[i]) else (0 if M[i]<=1.0 else p)
        else: g=1 if (M[i]>=3.0 and not blocked[i]) else (0 if M[i]>=-1.0 else p)
        tgt[i]=g
    return tgt
def TG_for(ch):
    d={}
    for name,vols in MEMBERS.items():
        cols=[idx[v] for v in vols]; s_=mem[:,cols].sum(axis=1).astype(np.int32)
        T=np.clip(ra(s_/float(len(cols))*10.0),-10,10)
        ag=(np.sign(s_)==tilt)&(s_!=0)&(tilt!=0)
        Tp=np.clip(ra(T*np.where(ag,1.25,1.0)*0.9026),-13,13)
        d[name]=hyst(0.7086*Tp+2.83*ch.astype(float))
    return d
def vote_(TGx,side):
    vs=[]
    for m_ in MEMBERS:
        tg=TGx[m_]
        for q in QS:
            okv=np.ones(n,bool) if q is None else ((X['norm']<=0)|(X['ratio']>=q))
            for dg in (True,False):
                a_=okv&(X['dL'] if side>0 else X['dS']) if dg else okv
                hit=(tg>0) if side>0 else (tg<0)
                vs.append(np.where(hit&a_,1,0).astype(np.int8))
    return np.vstack(vs).mean(axis=0)
st=np.zeros(D['n_sess'],np.int64); st[sid[fb]]=np.flatnonzero(fb)
sess_in=np.array([s for s in range(D['n_sess']) if A<=tarr[st[s]]<B])
inw=np.zeros(D['n_sess'],bool); inw[sess_in]=True
def i_of(ts): return int(min(np.searchsorted(tarr,np.datetime64(ts)),n-1))
for lab,ch in (('WITH bmom channel',bmom),('channel ZEROED',np.zeros(n,np.int8))):
    TG=TG_for(ch)
    p=-(vote_(TG,-1)>=0.5).astype(np.int8)
    tr=[x for x in sfills(D,p,halt=1300.0,target=1000.0) if inw[int(sid[i_of(x['et'])])]]
    net=sum(x['pnl'] for x in tr)
    occ=float((p[[i for i in range(n)]]!=0).mean())
    print(f'SHORT sleeve, {lab:20s}: {len(tr):5d} trades  net ${net:12,.0f}  short-target minutes {100*occ:.2f}%')
# how many short-target minutes require bmom == -1 ?
TGb=TG_for(bmom); TG0=TG_for(np.zeros(n,np.int8))
pb=(vote_(TGb,-1)>=0.5); p0=(vote_(TG0,-1)>=0.5)
print(f'short-target minutes: with channel {pb.sum():,}   without {p0.sum():,}   ENABLED-BY-CHANNEL {int((pb&~p0).sum()):,} ({100*(pb&~p0).sum()/max(pb.sum(),1):.1f}% of them)')
print(f'bmom == -1 on {100*(bmom<0).mean():.2f}% of all bars; == +1 on {100*(bmom>0).mean():.2f}%')
