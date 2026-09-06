"""
MARKET AUTOPSY — RTY (E-mini Russell 2000), point value $50.

Cross-asset Wave 1, descriptive science per NQ_RESEARCH_PLAYBOOK.md §9 / transfer-checklist §6.
This is DESCRIPTIVE SCIENCE (a market autopsy), NOT a falsifiable test — DISCOVERY_CONSUMED.
No strategy, no P&L, no ledger trial, no promotion.

DISCIPLINE (enforced in code):
  * POINTS BASIS ONLY. The substrate is additively back-adjusted (DELEV01 law): absolute levels
    are shifted, so every return / range / threshold is a POINT difference, never % of price and
    never a level threshold.
  * NATIVE SESSION determined from RTY's OWN volume profile (printed), not assumed from NQ.
  * HARD-DROP any session >= 2026-08-01 at load; print the retained boundary.

Outputs (runs/CROSSASSET_W1_RTY_AUTOPSY_20260906/out/):
  returns_by_tod.csv, distribution.txt, dependence.txt, path.txt, session.txt
  + volume_profile.txt, nq_correlation.txt, autopsy_console.txt (full log)
"""
from __future__ import annotations
import sys, os, math
import numpy as np
import pandas as pd

RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

RTY_PATH = os.path.abspath(os.path.join(RUN, "..", "SM1M_RTY_SUBSTRATE", "out", "rty_1m_2022_2026.parquet"))
NQ_PATH  = os.path.abspath(os.path.join(RUN, "..", "SM1M_SUBSTRATE", "out", "nq_1m_2022_2026.parquet"))

PV_RTY = 50.0   # $/point
PV_NQ  = 20.0   # $/point

SEAL = pd.Timestamp("2026-08-01")  # sessions >= this are VIRGIN, hard-dropped

# RTH window (minute-of-day of END-stamp): 09:31 .. 16:00  (opens 09:30, closes 16:00)
RTH_OPEN_MOD  = 9*60 + 31   # 571  (first RTH bar END-stamp; opens 09:30)
RTH_CLOSE_MOD = 16*60       # 960  (last RTH bar END-stamp; ends 16:00)
OR_END_MOD    = 10*60       # 600  (opening-range = 09:31..10:00 = first 30 min)

_LOG = []
def log(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    _LOG.append(s)

def sess_date(ts: pd.Series) -> pd.Series:
    """CME index-future session label: 18:00 ET -> 17:00 ET next cal day.
    Bars END-stamped; hour>=18 rolls forward to next calendar day's session."""
    d = ts.dt.normalize()
    return (d.where(ts.dt.hour < 18, d + pd.Timedelta(days=1))).dt.date

def load(path, tag):
    df = pd.read_parquet(path)
    df = df.sort_values("time").reset_index(drop=True)
    n0 = len(df)
    df["sess"] = sess_date(df["time"])
    sess_ts = pd.to_datetime(df["sess"])
    keep = sess_ts < SEAL
    dropped = int((~keep).sum())
    df = df[keep].reset_index(drop=True)
    df["mod"] = df["time"].dt.hour*60 + df["time"].dt.minute
    log(f"[LOAD {tag}] rows={n0} -> {len(df)} after seal-drop (dropped {dropped} rows with session >= {SEAL.date()})")
    log(f"[LOAD {tag}] retained time range: {df['time'].min()} .. {df['time'].max()}")
    log(f"[LOAD {tag}] retained session range: {df['sess'].min()} .. {df['sess'].max()}  (n sessions={df['sess'].nunique()})")
    return df

def moments(x):
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    n = len(x); m = x.mean(); s = x.std(ddof=1)
    sk = ((x-m)**3).mean() / (s**3) if s>0 else np.nan
    ku = ((x-m)**4).mean() / (s**4) - 3.0 if s>0 else np.nan   # excess kurtosis
    return n, m, s, sk, ku

def acf(x, lags):
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    x = x - x.mean(); n=len(x); denom=(x*x).sum()
    out=[]
    for L in lags:
        if L>=n: out.append(np.nan); continue
        out.append((x[L:]*x[:-L]).sum()/denom)
    return out

def variance_ratio(r, q):
    """Lo-MacKinlay VR(q) on a return series r (already 1-period). Overlapping."""
    r = np.asarray(r, float); r = r[~np.isnan(r)]
    n = len(r)
    if n < q+1: return np.nan, np.nan
    mu = r.mean()
    var1 = ((r-mu)**2).sum()/(n-1)
    # q-period overlapping sums
    cs = np.cumsum(r)
    qsum = cs[q-1:] - np.concatenate(([0.0], cs[:-q]))  # length n-q+1, overlapping q-sums
    # Lo-MacKinlay overlapping unbiased normalizer m = q(n-q+1)(1-q/n); this makes sigma_c^2
    # the PER-PERIOD-equivalent variance of the q-period return, so VR = sigma_c^2/sigma_a^2
    # (VR~1 for a random walk; <1 mean-revert; >1 trend). Do NOT divide by q again.
    mnorm = q*(n-q+1)*(1 - q/n)
    sigma_c2 = ((qsum - q*mu)**2).sum()/mnorm
    vr = sigma_c2/var1 if var1>0 else np.nan
    return vr, var1

# ============================================================================
log("="*90)
log("MARKET AUTOPSY — RTY (E-mini Russell 2000), point value $50.  DESCRIPTIVE, DISCOVERY_CONSUMED.")
log("POINTS BASIS ONLY (additively back-adjusted substrate; DELEV01 law).")
log("="*90)

rty = load(RTY_PATH, "RTY")

# ---------------------------------------------------------------------------
# 0) VOLUME PROFILE — confirm the NATIVE session empirically
# ---------------------------------------------------------------------------
vp_lines=[]
def vlog(*a):
    s=" ".join(str(x) for x in a); vp_lines.append(s)
vlog("RTY NATIVE-SESSION VOLUME PROFILE (from RTY's own data — not assumed)")
vlog("="*80)
hr = rty.groupby(rty["time"].dt.hour)["volume"].agg(["sum","count"])
hr["vol_share_%"] = (hr["sum"]/hr["sum"].sum()*100).round(2)
vlog("Volume by HOUR (ET, END-stamp):")
vlog(hr.to_string())
vlog("")
vlog(f"Distinct minute-of-day buckets present: {rty['mod'].nunique()}  (1380 = 23h => ETH spans 18:00->17:00 with a 17:00-18:00 break)")
mvol = rty.groupby("mod")["volume"].sum()
vlog("")
vlog("Minute-of-day volume around key boundaries (mod = HH*60+MM of END-stamp):")
for label, lo, hi in [("RTH OPEN 09:25-09:40", 9*60+25, 9*60+40),
                      ("RTH CLOSE 15:55-16:05", 15*60+55, 16*60+5),
                      ("MAINT BREAK 16:58-18:03", 16*60+58, 18*60+3)]:
    vlog(f"  -- {label} --")
    for mod in range(lo, hi+1):
        if mod in mvol.index:
            vlog(f"    {mod//60:02d}:{mod%60:02d}  vol={int(mvol.loc[mod]):>10d}")
vlog("")
vlog("DETERMINED NATIVE SESSION:")
vlog("  ETH (full electronic): 18:00 -> 17:00 ET next day (~23h), maintenance halt 17:00-18:00 ET.")
vlog("  RTH (cash-equity core): 09:30 -> 16:00 ET (first bar END-stamped 09:31 opens 09:30;")
vlog("       last bar END-stamped 16:00; the 16:00 print carries the settlement volume spike).")
vlog("  Volume mass: hours 09-10 (open drive) + 15-16 (cash close) dominate; 17:00 hour ~0 (break).")
vlog("  This is CME equity-index structure CONFIRMED from RTY's own tape, NOT copied from NQ.")
with open(os.path.join(OUT,"volume_profile.txt"),"w") as f: f.write("\n".join(vp_lines)+"\n")
log("\n".join(vp_lines))

# ---------------------------------------------------------------------------
# Build per-session anchor table (RTH open/close/high/low, prior levels, half-day flag)
# ---------------------------------------------------------------------------
rty["is_rth"] = (rty["mod"] >= RTH_OPEN_MOD) & (rty["mod"] <= RTH_CLOSE_MOD)
rth = rty[rty["is_rth"]].copy()

def first_last(g):
    return pd.Series({
        "rth_open":  g["open"].iloc[0],
        "rth_close": g["close"].iloc[-1],
        "rth_high":  g["high"].max(),
        "rth_low":   g["low"].min(),
        "rth_first_mod": g["mod"].iloc[0],
        "rth_last_mod":  g["mod"].iloc[-1],
        "rth_nbars": len(g),
    })
anc = rth.groupby("sess").apply(first_last, include_groups=False)
anc = anc.reset_index().sort_values("sess").reset_index(drop=True)
anc["sess"] = pd.to_datetime(anc["sess"])
anc["dow"] = anc["sess"].dt.dayofweek  # 0=Mon
anc["is_halfday"] = anc["rth_last_mod"] < RTH_CLOSE_MOD  # ended before 16:00

# opening-range (first 30 min 09:31..10:00)
orb = rth[rth["mod"] <= OR_END_MOD].groupby("sess").agg(or_high=("high","max"), or_low=("low","min"))
orb = orb.reset_index(); orb["sess"]=pd.to_datetime(orb["sess"])
anc = anc.merge(orb, on="sess", how="left")

# ---------------------------------------------------------------------------
# Overnight windows: every non-RTH bar buckets to the NEXT RTH open it precedes.
# ---------------------------------------------------------------------------
open_times = rth.groupby("sess")["time"].min().sort_values()   # first RTH bar time per session
open_sess  = pd.to_datetime(open_times.index)
open_arr   = open_times.values.astype("datetime64[ns]")
non = rty[~rty["is_rth"]].copy()
idx = np.searchsorted(open_arr, non["time"].values.astype("datetime64[ns]"), side="left")
valid = idx < len(open_arr)
non = non[valid].copy()
non["on_target"] = pd.to_datetime(open_sess[idx[valid]].values)
on_stats = non.groupby("on_target").agg(on_high=("high","max"), on_low=("low","min"),
                                         on_nbars=("close","size"),
                                         on_first_close=("close","first"), on_last_close=("close","last"))
on_stats = on_stats.reset_index().rename(columns={"on_target":"sess"})
anc = anc.merge(on_stats, on="sess", how="left")

# prior-session RTH close/high/low
anc["prev_rth_close"] = anc["rth_close"].shift(1)
anc["prev_rth_high"]  = anc["rth_high"].shift(1)
anc["prev_rth_low"]   = anc["rth_low"].shift(1)

# ---- POINT return decompositions (all in POINTS) ----
anc["ret_rth"]  = anc["rth_close"] - anc["rth_open"]                 # intraday RTH move
anc["ret_on"]   = anc["rth_open"]  - anc["prev_rth_close"]           # overnight (prev RTH close -> today RTH open)
anc["ret_c2c"]  = anc["rth_close"] - anc["prev_rth_close"]           # daily close-to-close (== ret_on + ret_rth)
anc["gap"]      = anc["rth_open"]  - anc["prev_rth_close"]           # opening gap (== ret_on)
anc["rth_range"]= anc["rth_high"]  - anc["rth_low"]
anc["on_range"] = anc["on_high"]   - anc["on_low"]
anc["or_range"] = anc["or_high"]   - anc["or_low"]

log(f"\n[ANCHORS] sessions in table: {len(anc)}; half-days (RTH ended <16:00): {int(anc['is_halfday'].sum())}")
log(f"[ANCHORS] identity check ret_c2c == ret_on+ret_rth : max abs diff = "
    f"{np.nanmax(np.abs(anc['ret_c2c'] - (anc['ret_on']+anc['ret_rth']))):.6f} pts")

# =====================================================================================
# (A) RETURNS
# =====================================================================================
# ---- 1-min within-segment point returns for time-of-day profile ----
rty["ret1"] = rty["close"].diff()
gap_ok = (rty["time"].diff() == pd.Timedelta(minutes=1)) & (rty["sess"].values == rty["sess"].shift(1).values)
rty.loc[~gap_ok, "ret1"] = np.nan  # only contiguous 1-min steps

# 30-min buckets across the full 23h session (label by bucket start clock)
rty["b30"] = (rty["mod"]//30)*30
tod = rty.groupby("b30")["ret1"].agg(n="count", mean_pt="mean", std_pt="std", sum_pt="sum")
tod = tod.reset_index()
tod["clock"] = tod["b30"].apply(lambda m: f"{int(m)//60:02d}:{int(m)%60:02d}")
tod["seg"] = np.where((tod["b30"]>=RTH_OPEN_MOD-1)&(tod["b30"]<=RTH_CLOSE_MOD-1),"RTH","ETH_overnight")
tod["t_stat"] = tod["mean_pt"]/(tod["std_pt"]/np.sqrt(tod["n"].clip(lower=1)))
tod_out = tod[["clock","seg","n","mean_pt","std_pt","sum_pt","t_stat"]].copy()
tod_out.to_csv(os.path.join(OUT,"returns_by_tod.csv"), index=False)

R=[]
def rlog(*a):
    s=" ".join(str(x) for x in a); R.append(s)
rlog("RTY RETURNS — POINTS BASIS.  point value $50/pt.")
rlog("="*90)
rlog("\n[A1] POINT-RETURN BY TIME-OF-DAY (30-min buckets of contiguous 1-min close-to-close, POINTS)")
rlog("  clock=bucket start (ET, END-stamp); mean/std/sum in POINTS; t = mean/(std/sqrt(n)).")
rlog(tod_out.to_string(index=False, float_format=lambda v:f"{v:.5f}"))

# session vs overnight
def blk(name, s):
    n,m,sd,sk,ku = moments(s)
    rlog(f"  {name:<28} n={n:>5}  mean={m:+.4f}  std={sd:.3f}  sum={np.nansum(s):+.1f}  skew={sk:+.3f}  exkurt={ku:+.2f}")
rlog("\n[A2] SESSION vs OVERNIGHT (per-session POINT returns)")
blk("RTH intraday (open->close)", anc["ret_rth"])
blk("Overnight (pClose->open)",   anc["ret_on"])
blk("Close-to-close (daily)",     anc["ret_c2c"])
rlog(f"  => share of total drift: RTH sum={np.nansum(anc['ret_rth']):+.1f}pt  ON sum={np.nansum(anc['ret_on']):+.1f}pt")

# day-of-week
rlog("\n[A3] DAY-OF-WEEK (per-session POINT returns; 0=Mon .. 4=Fri)")
downames={0:"Mon",1:"Tue",2:"Wed",3:"Thu",4:"Fri"}
for d in range(5):
    sub=anc[anc["dow"]==d]
    nc,mc,sdc,_,_=moments(sub["ret_c2c"])
    _,mr,_,_,_=moments(sub["ret_rth"])
    _,mo,_,_,_=moments(sub["ret_on"])
    rlog(f"  {downames[d]}  c2c n={nc:>4} mean={mc:+.4f} std={sdc:6.3f} | RTH mean={mr:+.4f} | ON mean={mo:+.4f}")

# conditional on prior-day / overnight sign
def cond_sign(cond_series, out_series, label):
    m = ~(np.isnan(cond_series) | np.isnan(out_series))
    c=cond_series[m]; o=out_series[m]
    up = o[c>0]; dn=o[c<0]
    def sr(x):
        n,mn,sd,_,_=moments(x);
        return f"n={n:>4} mean={mn:+.4f} std={sd:6.3f} P(out>0)={np.mean(x>0)*100:5.1f}%"
    rlog(f"  {label}")
    rlog(f"     after UP   : {sr(up)}")
    rlog(f"     after DOWN : {sr(dn)}")
    return up,dn
rlog("\n[A4] CONDITIONAL ON PRIOR SIGN (continuation vs reversal, POINTS)")
anc["prev_ret_c2c"]=anc["ret_c2c"].shift(1)
anc["prev_ret_rth"]=anc["ret_rth"].shift(1)
cond_sign(anc["prev_ret_c2c"].values, anc["ret_c2c"].values, "prior daily c2c sign -> today daily c2c")
cond_sign(anc["prev_ret_rth"].values, anc["ret_rth"].values, "prior RTH sign -> today RTH")
cond_sign(anc["ret_on"].values,       anc["ret_rth"].values, "today overnight sign -> today RTH (does the gap continue?)")

with open(os.path.join(OUT,"returns_summary.txt"),"w") as f: f.write("\n".join(R)+"\n")
log("\n".join(R))

# =====================================================================================
# (B) DISTRIBUTION
# =====================================================================================
D=[]
def dlog(*a):
    s=" ".join(str(x) for x in a); D.append(s)
dlog("RTY DISTRIBUTION — POINTS BASIS.")
dlog("="*90)
for name,ser in [("daily close-to-close", anc["ret_c2c"]),
                 ("RTH intraday", anc["ret_rth"]),
                 ("overnight", anc["ret_on"]),
                 ("1-min RTH", rty.loc[rty["is_rth"],"ret1"])]:
    n,m,sd,sk,ku=moments(ser)
    x=np.asarray(ser,float); x=x[~np.isnan(x)]
    q=np.percentile(x,[0.1,1,5,25,50,75,95,99,99.9])
    dlog(f"\n[B] {name}: n={n} mean={m:+.4f} std={sd:.4f} skew={sk:+.3f} exkurt={ku:+.2f} POINTS")
    dlog(f"     pctiles(pt) 0.1%={q[0]:+.2f} 1%={q[1]:+.2f} 5%={q[2]:+.2f} 25%={q[3]:+.2f} "
         f"50%={q[4]:+.2f} 75%={q[5]:+.2f} 95%={q[6]:+.2f} 99%={q[7]:+.2f} 99.9%={q[8]:+.2f}")
    dlog(f"     min={x.min():+.2f} max={x.max():+.2f}  (in $: 1pt=${PV_RTY:.0f}; std=${sd*PV_RTY:,.0f})")
    # extreme-move frequency vs gaussian
    for k in (2,3,4,5):
        f_emp=np.mean(np.abs(x-m) > k*sd)*100
        dlog(f"     |z|>{k}: empirical {f_emp:6.3f}%  (gaussian {(2*(1-0.5*(1+math.erf(k/np.sqrt(2)))))*100:6.3f}%)")

# gap distribution
dlog("\n[B-GAP] OPENING GAP = RTH_open(D) - RTH_close(D-1), POINTS")
g=anc["gap"].dropna().values
n,m,sd,sk,ku=moments(g)
qg=np.percentile(g,[1,5,25,50,75,95,99])
dlog(f"  n={n} mean={m:+.4f} std={sd:.3f} skew={sk:+.3f} exkurt={ku:+.2f}")
dlog(f"  |gap| median={np.median(np.abs(g)):.3f}pt mean={np.mean(np.abs(g)):.3f}pt")
dlog(f"  pctiles 1%={qg[0]:+.2f} 5%={qg[1]:+.2f} 25%={qg[2]:+.2f} 50%={qg[3]:+.2f} 75%={qg[4]:+.2f} 95%={qg[5]:+.2f} 99%={qg[6]:+.2f}")
dlog(f"  P(gap up)={np.mean(g>0)*100:.1f}%  P(|gap|<2pt)={np.mean(np.abs(g)<2)*100:.1f}%  P(|gap|>10pt)={np.mean(np.abs(g)>10)*100:.1f}%")

# intraday vs overnight range + realized vol
dlog("\n[B-RANGE] RANGE (POINTS): RTH high-low vs OVERNIGHT high-low")
for name,ser in [("RTH range", anc["rth_range"]),("Overnight range", anc["on_range"]),("Opening-range 30m", anc["or_range"])]:
    x=ser.dropna().values
    dlog(f"  {name:<18} mean={x.mean():7.3f} med={np.median(x):7.3f} std={x.std(ddof=1):7.3f} "
         f"p5={np.percentile(x,5):6.2f} p95={np.percentile(x,95):7.2f} max={x.max():7.2f}")
rr=(anc["rth_range"]/anc["on_range"]).replace([np.inf,-np.inf],np.nan).dropna()
dlog(f"  RTH/Overnight range ratio: median={rr.median():.3f} mean={rr.mean():.3f}")

# realized vol (points): per-session sqrt sum of squared 1-min contiguous returns
rv_rth = rty[rty["is_rth"]].groupby("sess")["ret1"].apply(lambda r: np.sqrt(np.nansum(r.values**2)))
non["ret1_on"] = non.groupby("on_target")["close"].diff()
rv_on  = non.groupby("on_target")["ret1_on"].apply(lambda r: np.sqrt(np.nansum(r.values**2)))
dlog("\n[B-RV] REALIZED VOL per session (sqrt sum sq 1-min POINT returns)")
dlog(f"  RTH  RV: mean={rv_rth.mean():.3f} med={rv_rth.median():.3f} p95={np.percentile(rv_rth.dropna(),95):.2f}")
dlog(f"  ONite RV: mean={rv_on.mean():.3f} med={rv_on.median():.3f} p95={np.percentile(rv_on.dropna(),95):.2f}")
dlog(f"  RTH/ON RV ratio (median of per-session): {(rv_rth/rv_on).replace([np.inf,-np.inf],np.nan).median():.3f}")

with open(os.path.join(OUT,"distribution.txt"),"w") as f: f.write("\n".join(D)+"\n")
log("\n".join(D))

# =====================================================================================
# (C) DEPENDENCE
# =====================================================================================
DEP=[]
def plog(*a):
    s=" ".join(str(x) for x in a); DEP.append(s)
plog("RTY DEPENDENCE — POINTS BASIS.")
plog("="*90)
lags=[1,2,3,4,5,10,20]
plog("\n[C1] RETURN AUTOCORRELATION (ACF)")
for name,ser in [("daily c2c", anc["ret_c2c"]),("RTH", anc["ret_rth"]),("overnight", anc["ret_on"]),
                 ("1-min RTH", rty.loc[rty["is_rth"],"ret1"])]:
    a=acf(ser.values if hasattr(ser,'values') else ser, lags)
    plog(f"  {name:<12} " + " ".join(f"L{L}={v:+.4f}" for L,v in zip(lags,a)))

plog("\n[C2] SIGN PERSISTENCE")
for name,ser in [("daily c2c", anc["ret_c2c"]),("RTH", anc["ret_rth"]),("overnight", anc["ret_on"])]:
    s=ser.dropna().values; sg=np.sign(s); sg=sg[sg!=0]
    same=np.mean(sg[1:]==sg[:-1])*100
    pup=np.mean(s>0)*100
    plog(f"  {name:<12} P(same sign as prev)={same:5.1f}%  P(up)={pup:5.1f}%  (indep would be {pup**2/100+(100-pup)**2/100:5.1f}%)")

plog("\n[C3] VOLATILITY AUTOCORRELATION (|ret| and RV clustering)")
for name,ser in [("|daily c2c|", anc["ret_c2c"].abs()),("RTH RV", rv_rth),("daily range", anc["rth_range"])]:
    a=acf(ser.values, lags)
    plog(f"  {name:<12} " + " ".join(f"L{L}={v:+.4f}" for L,v in zip(lags,a)))

plog("\n[C4] VARIANCE RATIO (Lo-MacKinlay, overlapping). VR<1 mean-revert, >1 trend/persistent.")
for name,ser in [("daily c2c", anc["ret_c2c"].dropna().values),
                 ("RTH", anc["ret_rth"].dropna().values),
                 ("1-min RTH", rty.loc[rty["is_rth"],"ret1"].dropna().values)]:
    row=[]
    for q in (2,5,10,20):
        vr,_=variance_ratio(ser,q); row.append(f"VR({q})={vr:.3f}")
    plog(f"  {name:<12} " + "  ".join(row))

plog("\n[C5] CONDITIONAL CONTINUATION vs REVERSAL (magnitude, POINTS)")
# after a big up/down day (top/bottom tercile of prior c2c), mean of today
pc=anc["prev_ret_c2c"]; tc=anc["ret_c2c"]
m=~(pc.isna()|tc.isna()); pc=pc[m]; tc=tc[m]
q33,q67=np.percentile(pc,[33.3,66.7])
for lab,mask in [("prior bottom-tercile", pc<=q33),("prior mid", (pc>q33)&(pc<q67)),("prior top-tercile", pc>=q67)]:
    n,mn,sd,_,_=moments(tc[mask.values])
    plog(f"  {lab:<22} today c2c mean={mn:+.4f} std={sd:6.3f} n={n} P(up)={np.mean(tc[mask.values]>0)*100:5.1f}%")

with open(os.path.join(OUT,"dependence.txt"),"w") as f: f.write("\n".join(DEP)+"\n")
log("\n".join(DEP))

# =====================================================================================
# (D) PATH
# =====================================================================================
P=[]
def qlog(*a):
    s=" ".join(str(x) for x in a); P.append(s)
qlog("RTY PATH STRUCTURE — POINTS BASIS. (RTH session as the unit of a path)")
qlog("="*90)
# per-RTH-session efficiency ratio, MFE/MAE, tortuosity
def path_stats(g):
    c=g["close"].values; o=g["open"].values[0]; h=g["high"].values; l=g["low"].values
    if len(c)<2: return pd.Series({"er":np.nan,"tort":np.nan,"net":np.nan,"pathlen":np.nan,
                                   "mfe":np.nan,"mae":np.nan})
    net=c[-1]-o
    steps=np.abs(np.diff(np.concatenate(([o],c))))  # from open through closes
    pathlen=steps.sum()
    er=abs(net)/pathlen if pathlen>0 else np.nan
    mfe=h.max()-o    # max favorable (long frame)
    mae=o-l.min()    # max adverse (long frame)
    return pd.Series({"er":er,"tort":(1/er if er>0 else np.nan),"net":net,"pathlen":pathlen,"mfe":mfe,"mae":mae})
ps=rth.groupby("sess").apply(path_stats, include_groups=False)
qlog("\n[D1] EFFICIENCY RATIO (Kaufman) per RTH session = |net| / sum|1-min step|.  1=straight, 0=noise.")
er=ps["er"].dropna()
qlog(f"  ER: mean={er.mean():.4f} med={er.median():.4f} p10={np.percentile(er,10):.4f} p90={np.percentile(er,90):.4f}")
qlog(f"  TORTUOSITY (1/ER): median={ps['tort'].replace([np.inf,-np.inf],np.nan).dropna().median():.3f}")
qlog(f"  (low ER => choppy/noisy intraday path; high ER => directional/trending day)")
qlog(f"  daily path length (sum|1-min step|, pts): mean={ps['pathlen'].mean():.2f} med={ps['pathlen'].median():.2f}")
qlog(f"  net |displacement| (pts): mean={ps['net'].abs().mean():.2f} med={ps['net'].abs().median():.2f}")

qlog("\n[D2] MFE / MAE per RTH session (long-frame from RTH open, POINTS)")
for nm,ser in [("MFE (max high-open)", ps["mfe"]),("MAE (open-min low)", ps["mae"])]:
    x=ser.dropna().values
    qlog(f"  {nm:<22} mean={x.mean():7.3f} med={np.median(x):7.3f} p90={np.percentile(x,90):7.2f}")
# excursion relative to realized net move, directionally
merged=ps.join(anc.set_index(pd.to_datetime(anc["sess"]).dt.date)[["ret_rth"]], how="left")
up=merged[merged["ret_rth"]>0]; dn=merged[merged["ret_rth"]<0]
qlog(f"  On UP days   (net>0): median MFE={up['mfe'].median():.2f} median MAE(heat)={up['mae'].median():.2f}  -> heat/target={up['mae'].median()/max(up['mfe'].median(),1e-9):.2f}")
qlog(f"  On DOWN days (net<0): median MAE={dn['mae'].median():.2f} median MFE(heat)={dn['mfe'].median():.2f}")

qlog("\n[D3] COMPRESSION / EXPANSION (range clustering)")
anc2=anc.copy()
anc2["range_ma20"]=anc2["rth_range"].rolling(20).mean().shift(1)
anc2["range_ratio"]=anc2["rth_range"]/anc2["range_ma20"]
rr=anc2["range_ratio"].dropna()
qlog(f"  today RTH range / trailing-20 mean range: median={rr.median():.3f} p10={np.percentile(rr,10):.3f} p90={np.percentile(rr,90):.3f}")
a=acf(anc["rth_range"].values,[1,2,3,5,10])
qlog(f"  RTH-range ACF: " + " ".join(f"L{L}={v:+.4f}" for L,v in zip([1,2,3,5,10],a)))
# does a compressed day (bottom-tercile range) precede expansion?
q33r=np.percentile(anc2["rth_range"].dropna(),33.3)
anc2["prev_range"]=anc2["rth_range"].shift(1)
comp=anc2[anc2["prev_range"]<=q33r]["rth_range"]; noncomp=anc2[anc2["prev_range"]>q33r]["rth_range"]
qlog(f"  next-day RTH range after a bottom-tercile (compressed) day: mean={comp.mean():.2f} vs after non-compressed {noncomp.mean():.2f}")

with open(os.path.join(OUT,"path.txt"),"w") as f: f.write("\n".join(P)+"\n")
log("\n".join(P))

# =====================================================================================
# (E) SESSION STRUCTURE
# =====================================================================================
S=[]
def slog(*a):
    s=" ".join(str(x) for x in a); S.append(s)
slog("RTY SESSION STRUCTURE — POINTS BASIS. (descriptive geometry, not strategies)")
slog("="*90)
a=anc.dropna(subset=["on_high","on_low","prev_rth_close"]).copy()

slog("\n[E1] OVERNIGHT HIGH/LOW takeout by RTH")
tk_h=(a["rth_high"]>a["on_high"]).mean()*100
tk_l=(a["rth_low"]<a["on_low"]).mean()*100
both=((a["rth_high"]>a["on_high"])&(a["rth_low"]<a["on_low"])).mean()*100
neither=((a["rth_high"]<=a["on_high"])&(a["rth_low"]>=a["on_low"])).mean()*100
slog(f"  RTH takes out overnight HIGH: {tk_h:.1f}%   overnight LOW: {tk_l:.1f}%")
slog(f"  takes out BOTH: {both:.1f}%   NEITHER (RTH inside overnight range): {neither:.1f}%")

slog("\n[E2] OPENING RANGE (first 30 min, 09:30-10:00)")
a2=anc.dropna(subset=["or_high","or_low"]).copy()
a2["or_contains_high"]=a2["rth_high"]<=a2["or_high"]
a2["or_contains_low"]=a2["rth_low"]>=a2["or_low"]
a2["or_holds"]=a2["or_contains_high"]&a2["or_contains_low"]
slog(f"  OR range as % of full RTH range: median={ (a2['or_range']/a2['rth_range']).median()*100:.1f}%")
slog(f"  session HIGH set inside OR window: {a2['or_contains_high'].mean()*100:.1f}%   session LOW inside OR: {a2['or_contains_low'].mean()*100:.1f}%")
slog(f"  RTH stays entirely inside the OR (no breakout either side): {a2['or_holds'].mean()*100:.1f}%")
# breakout side vs close side
up_brk=a2[a2["rth_high"]>a2["or_high"]]
slog(f"  when OR high is broken, close finishes above OR high: {(up_brk['rth_close']>up_brk['or_high']).mean()*100:.1f}%")

slog("\n[E3] GAP behavior (POINTS)")
ag=anc.dropna(subset=["gap","prev_rth_close"]).copy()
gup=ag[ag["gap"]>0]; gdn=ag[ag["gap"]<0]
fill_up=(gup["rth_low"]<=gup["prev_rth_close"]).mean()*100
fill_dn=(gdn["rth_high"]>=gdn["prev_rth_close"]).mean()*100
slog(f"  gap-up sessions: {len(gup)} ({len(gup)/len(ag)*100:.1f}%); gap filled (RTH trades back to prev close): {fill_up:.1f}%")
slog(f"  gap-dn sessions: {len(gdn)} ({len(gdn)/len(ag)*100:.1f}%); gap filled: {fill_dn:.1f}%")
# gap continuation: does RTH extend in gap direction?
slog(f"  gap-up  -> RTH ret mean={gup['ret_rth'].mean():+.3f}pt (continuation if >0)")
slog(f"  gap-dn  -> RTH ret mean={gdn['ret_rth'].mean():+.3f}pt")

slog("\n[E4] PRIOR-DAY LEVELS (PDH/PDL touch by today's RTH)")
ap=anc.dropna(subset=["prev_rth_high","prev_rth_low"]).copy()
slog(f"  RTH touches prior-day HIGH (PDH): {(ap['rth_high']>=ap['prev_rth_high']).mean()*100:.1f}%")
slog(f"  RTH touches prior-day LOW  (PDL): {(ap['rth_low']<=ap['prev_rth_low']).mean()*100:.1f}%")
slog(f"  RTH stays inside prior-day range: {((ap['rth_high']<ap['prev_rth_high'])&(ap['rth_low']>ap['prev_rth_low'])).mean()*100:.1f}%")

slog("\n[E5] HALF-DAY / DATA notes")
slog(f"  half-day sessions (RTH ended <16:00): {int(anc['is_halfday'].sum())} of {len(anc)} (US early closes 13:00/13:15).")
slog(f"  These are retained for daily-return continuity but flagged; excluding them changes RTH means negligibly.")

with open(os.path.join(OUT,"session.txt"),"w") as f: f.write("\n".join(S)+"\n")
log("\n".join(S))

# =====================================================================================
# (F) NQ CORRELATION — daily POINT-return correlation on shared dates
# =====================================================================================
CC=[]
def clog(*a):
    s=" ".join(str(x) for x in a); CC.append(s)
clog("RTY <-> NQ DAILY POINT-RETURN CORRELATION (diversification pre-read)")
clog("="*90)
nq = load(NQ_PATH, "NQ")
nq["is_rth"]=(nq["mod"]>=RTH_OPEN_MOD)&(nq["mod"]<=RTH_CLOSE_MOD)
nqrth=nq[nq["is_rth"]]
nq_anc=nqrth.groupby("sess").agg(rth_open=("open","first"),rth_close=("close","last")).reset_index()
nq_anc["sess"]=pd.to_datetime(nq_anc["sess"]); nq_anc=nq_anc.sort_values("sess")
nq_anc["ret_c2c"]=nq_anc["rth_close"]-nq_anc["rth_close"].shift(1)
nq_anc["ret_rth"]=nq_anc["rth_close"]-nq_anc["rth_open"]

rty_d=anc[["sess","ret_c2c","ret_rth"]].rename(columns={"ret_c2c":"rty_c2c","ret_rth":"rty_rth"})
nq_d =nq_anc[["sess","ret_c2c","ret_rth"]].rename(columns={"ret_c2c":"nq_c2c","ret_rth":"nq_rth"})
mrg=rty_d.merge(nq_d,on="sess",how="inner").dropna()
clog(f"\n  shared sessions (dev window, <2026-08-01): {len(mrg)}")
clog(f"  window: {mrg['sess'].min().date()} .. {mrg['sess'].max().date()}")
from numpy import corrcoef
def spearman(a,b):
    ra=pd.Series(a).rank().values; rb=pd.Series(b).rank().values
    return corrcoef(ra,rb)[0,1]
for lab,x,y in [("daily close-to-close", mrg["rty_c2c"], mrg["nq_c2c"]),
                ("RTH intraday",         mrg["rty_rth"], mrg["nq_rth"])]:
    pear=corrcoef(x,y)[0,1]; sp=spearman(x.values,y.values)
    clog(f"  {lab:<22} Pearson rho={pear:+.4f}   Spearman={sp:+.4f}   (POINT-return basis)")
# per-year
mrg["yr"]=mrg["sess"].dt.year
clog("\n  per-year daily c2c Pearson rho (points):")
for yr,sub in mrg.groupby("yr"):
    if len(sub)>20:
        clog(f"    {yr}: rho={corrcoef(sub['rty_c2c'],sub['nq_c2c'])[0,1]:+.4f}  (n={len(sub)})")
# beta of RTY on NQ (points, informational)
b=np.polyfit(mrg["nq_c2c"],mrg["rty_c2c"],1)[0]
clog(f"\n  OLS slope d(RTY_pt)/d(NQ_pt) = {b:.4f} pts/pt (informational; not a hedge ratio in $)")
clog(f"  In $ terms 1 RTY-pt=${PV_RTY:.0f}, 1 NQ-pt=${PV_NQ:.0f}.")
clog("\n  READ: RTY is another CME equity-index; expect HIGH co-movement with NQ. A high rho means")
clog("  RTY as a *directional clone* adds little diversification — its value to the book would have")
clog("  to come from a NATIVE mechanism whose *underwater curve* decouples, not from the index itself.")
with open(os.path.join(OUT,"nq_correlation.txt"),"w") as f: f.write("\n".join(CC)+"\n")
log("\n".join(CC))

# save full console
with open(os.path.join(OUT,"autopsy_console.txt"),"w") as f: f.write("\n".join(_LOG)+"\n")
log("\n[DONE] all tables written to out/.")
