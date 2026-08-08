"""W3-1 SNAPBACK rule family — sequential episode simulation per frozen spec
specs/W3-1_snapback_rule.md (committed 1b3837d before this run). Seed 20260808."""
import glob, os
import numpy as np, pandas as pd
from numba import njit

KS = [10, 30]
DS = [8, 12, 16]          # 12 = primary; 8/16 = frozen robustness neighbors
BRK = [(24, 8), (32, 10)]
CAP = 300
COOL = 30
C1, C2 = 2.872, 4.872

@njit(cache=True)
def simulate(ml, hi, lo, dec, trig, dirsign, A, B, cap, cool, delay):
    """Sequential: enter at ml[t+delay] on trigger, resolve on hi/lo barriers or cap.
    Returns arrays: entry_idx, outcome (1 tgt/2 adv/3 cap), gross ticks, spread-slot."""
    n = ml.shape[0]
    e_idx = np.empty(n, np.int64); e_out = np.empty(n, np.int8); e_gross = np.empty(n, np.float64)
    m = 0; t = 0
    while t < n - delay - 1:
        if dec[t] and trig[t]:
            te = t + delay
            entry = ml[te]
            res = 0; i = te + 1
            end = min(te + cap, n - 1)
            while i <= end:
                up = hi[i] - entry; dn = entry - lo[i]
                if dirsign == 1:
                    t_hit = up >= A; a_hit = dn >= B
                else:
                    t_hit = dn >= A; a_hit = up >= B
                if t_hit and a_hit: res = 2; break
                if a_hit: res = 2; break
                if t_hit: res = 1; break
                i += 1
            if res == 1: g = float(A)
            elif res == 2: g = -float(B)
            else:
                res = 3; g = (ml[end] - entry) * dirsign; i = end
            e_idx[m] = t; e_out[m] = res; e_gross[m] = g; m += 1
            t = i + cool
        else:
            t += 1
    return e_idx[:m], e_out[:m], e_gross[:m]

SH = "research/scalping_lab/substrate/sechilo/NQ"
GR = "research/scalping_lab/substrate/grid1s/NQ"
OUTD = "research/scalping_lab/artifacts/w31_snapback"
os.makedirs(OUTD, exist_ok=True)

rows = []
sessions = sorted(os.path.basename(p)[:-8] for p in glob.glob(os.path.join(SH, "s*.parquet")))
for tag in sessions:
    d = pd.to_datetime(tag[1:], format="%Y%m%d")
    g = pd.read_parquet(os.path.join(GR, tag + ".parquet"))
    s = pd.read_parquet(os.path.join(SH, tag + ".parquet"))
    g["time"] = pd.to_datetime(g["time"]); s["time"] = pd.to_datetime(s["time"])
    f = g.merge(s, on="time", how="left")
    f["mid_last"] = f["mid_last"].ffill()
    f = f[f["mid_last"].notna()].reset_index(drop=True)
    f["mid_high"] = f["mid_high"].fillna(f["mid_last"])
    f["mid_low"] = f["mid_low"].fillna(f["mid_last"])
    ml = f["mid_last"].values; hi = f["mid_high"].values; lo = f["mid_low"].values
    tod = (f["time"] - d).dt.total_seconds().values
    upd60 = pd.Series((f["bid_upd"] + f["ask_upd"]).values).rolling(60, min_periods=1).sum().values
    dec = ((tod >= 9*3600+1800) & (tod < 16*3600) & (upd60 > 0)).astype(np.bool_)
    spread = f["spread_t"].values
    mls = pd.Series(ml)
    for k in KS:
        retk = (mls - mls.shift(k)).values
        for D in DS:
            for dname, dv in (("long", 1), ("short", -1)):
                trig = (retk <= -D) if dv == 1 else (retk >= D)
                trig = np.where(np.isnan(retk), False, trig).astype(np.bool_)
                for (A, B) in BRK:
                    for delay in (0, 1):
                        ei, eo, eg = simulate(ml, hi, lo, dec, trig, dv, float(A), float(B),
                                              CAP, COOL, delay)
                        if len(ei) == 0: continue
                        sp_ok = spread[ei] <= 2.0
                        rows.append(dict(session=tag, k=k, D=D, dir=dname, A=A, B=B,
                                         delay=delay, n=len(ei),
                                         n_tgt=int((eo == 1).sum()), n_adv=int((eo == 2).sum()),
                                         n_cap=int((eo == 3).sum()), gross_sum=float(eg.sum()),
                                         n_sp2=int(sp_ok.sum()),
                                         gross_sp2=float(eg[sp_ok].sum()),
                                         tgt_sp2=int(((eo == 1) & sp_ok).sum())))
    print(tag, "done", flush=True)

R = pd.DataFrame(rows)
R.to_csv(os.path.join(OUTD, "w31_results.csv"), index=False)

brng = np.random.default_rng(20260808)
print("\n=== W3-1 SNAPBACK — pooled by config (delay=0) ===")
print(f"{'k':>3} {'D':>3} {'dir':>5} {'A':>3} {'B':>3} | {'epi':>6} {'epi/d':>6} {'P(tgt)':>7} "
      f"{'BE_C1':>6} | {'netC1':>7} {'CI_lo':>7} {'CI_hi':>7} | {'netC2':>7} | {'net1s':>7}")
for k in KS:
    for D in DS:
        for dname in ("long", "short"):
            for (A, B) in BRK:
                g0 = R[(R.k == k) & (R.D == D) & (R.dir == dname) & (R.A == A) & (R.B == B) & (R.delay == 0)]
                g1 = R[(R.k == k) & (R.D == D) & (R.dir == dname) & (R.A == A) & (R.B == B) & (R.delay == 1)]
                if not len(g0): continue
                n = g0.n.sum(); ptgt = g0.n_tgt.sum() / max(1, (g0.n_tgt + g0.n_adv).sum())
                net1 = g0.gross_sum.sum() / n - C1
                net2 = g0.gross_sum.sum() / n - C2
                per = (g0.gross_sum / g0.n - C1).values
                w = g0.n.values
                boots = [np.average(brng.choice(per, len(per), replace=True),
                                    weights=brng.choice(w, len(w), replace=True)) for _ in range(1000)]
                # session bootstrap: resample sessions, weight by episode count (paired)
                idx = np.arange(len(per))
                boots = []
                for _ in range(1000):
                    b = brng.choice(idx, len(idx), replace=True)
                    boots.append(np.average(per[b], weights=w[b]))
                be1 = (B + C1) / (A + B)
                n1s = g1.gross_sum.sum() / max(1, g1.n.sum()) - C1
                star = " *" if D == 12 else ""
                print(f"{k:>3} {D:>3} {dname:>5} {A:>3} {B:>3} | {n:>6} {n/len(g0):>6.1f} {ptgt:>7.4f} "
                      f"{be1:>6.4f} | {net1:>+7.3f} {np.percentile(boots,2.5):>+7.3f} "
                      f"{np.percentile(boots,97.5):>+7.3f} | {net2:>+7.3f} | {n1s:>+7.3f}{star}")
print("\n(* = primary D=12 config; others are frozen robustness neighbors)")

print("\n=== spread<=2 diagnostic (delay=0, primary D=12): net C1 in-filter ===")
for k in KS:
    for dname in ("long", "short"):
        for (A, B) in BRK:
            g0 = R[(R.k == k) & (R.D == 12) & (R.dir == dname) & (R.A == A) & (R.B == B) & (R.delay == 0)]
            if not len(g0) or g0.n_sp2.sum() == 0: continue
            netf = g0.gross_sp2.sum() / g0.n_sp2.sum() - C1
            print(f"  k={k} {dname} +{A}/-{B}: n={g0.n_sp2.sum()} net_C1={netf:+.3f}t "
                  f"(vs all {g0.gross_sum.sum()/g0.n.sum()-C1:+.3f}t)")
print("\nW31 DONE")
