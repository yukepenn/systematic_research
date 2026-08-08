"""W4-C FSS-5: level sweep -> reclaim (Zone F/S) — sequential episode simulation.
Frozen spec: specs/W4_alpha_wave1.md section "W4-C" (committed before readout). Seed 20260808.

Causal levels per session (all in ticks, from the merged sechilo frame):
  ONH/ONL   = max mid_high / min mid_low over tod in [file start (prior 18:00), 09:30)
  OR15H/OR15L = same over tod in [09:30, 09:45); usable as levels only from 09:45.
  (Running RTH high/low is a listed causal level but the frozen trade sets are exactly
   {ONL, OR15L} long-side and {ONH, OR15H} short-side, so it is not simulated.)

Rule (RECLAIM primary): LONG at low-side level L: sweep = mid_low <= L - pierce (primary
pierce=2t), reclaim = mid_last >= L + 1t within W s of the FIRST sweep second (primary
W=60) -> MARKET entry at the reclaim second. SHORT symmetric at high-side level.
CONTINUATION mirror (frozen diagnostic): on failure to reclaim within W, enter in the
sweep direction at second t0+W. Same brackets.
Brackets (16,6),(24,8); cap 300s; cooldown 60s after each trade exit; one trade per
level per sweep episode — a new episode requires |mid_last - L| >= 8t first (re-arm).
Neighbors (reported always, never selected on): pierce {1t,4t}, window {30s,120s}.
Barriers on per-second mid_high/mid_low; same-second both-crossed -> ADVERSE.
Decisions (sweep detection + entries) only on RTH & quote-alive seconds.
Costs C1=2.872t, C2=4.872t RT. Day-clustered 95% CI: session bootstrap, 1000 reps.
"""
import glob, os
import numpy as np, pandas as pd
from numba import njit

PIERCES = [1.0, 2.0, 4.0]        # 2 = primary; 1/4 = frozen neighbors
WINDOWS = [30, 60, 120]          # 60 = primary; 30/120 = frozen neighbors
BRK = [(16, 6), (24, 8)]
CAP = 300
COOL = 60
REARM = 8.0
C1, C2 = 2.872, 4.872
RTH0, OR15_END, RTH1 = 9*3600+1800, 9*3600+2700, 16*3600

@njit(cache=True)
def simulate_level(ml, hi, lo, dec, avail, L, lvl_side, mode, pierce, W, A, B,
                   cap, cool, rearm):
    """Sequential per-level state machine.
    lvl_side: +1 = low-side level (sweep down / reclaim long), -1 = high-side.
    mode: 0 = RECLAIM trade, 1 = CONTINUATION trade (failure-to-reclaim mirror).
    Returns entry_idx, outcome (1 tgt / 2 adv / 3 cap), gross ticks, n_sweep episodes."""
    n = ml.shape[0]
    e_idx = np.empty(n, np.int64); e_out = np.empty(n, np.int8)
    e_gross = np.empty(n, np.float64)
    m = 0; n_sweep = 0
    t = 0; armed = True; next_ok = 0
    while t < n:
        if not armed:
            d = ml[t] - L
            if d < 0.0: d = -d
            if d >= rearm:
                armed = True          # fall through: same second may sweep again
            else:
                t += 1
                continue
        swept = False
        if dec[t] and avail[t] and t >= next_ok:
            if lvl_side == 1:
                swept = lo[t] <= L - pierce
            else:
                swept = hi[t] >= L + pierce
        if not swept:
            t += 1
            continue
        n_sweep += 1
        t0 = t
        wend = t0 + W
        if wend > n - 1: wend = n - 1
        rec_i = -1
        for i in range(t0, wend + 1):
            if lvl_side == 1:
                if ml[i] >= L + 1.0: rec_i = i; break
            else:
                if ml[i] <= L - 1.0: rec_i = i; break
        te = -1; ddir = 0
        if mode == 0:                                  # RECLAIM side
            if rec_i >= 0 and dec[rec_i]:
                te = rec_i; ddir = 1 if lvl_side == 1 else -1
            resume = (rec_i + 1) if rec_i >= 0 else (wend + 1)
        else:                                          # CONTINUATION mirror
            if rec_i < 0:
                cand = t0 + W
                if cand <= n - 1 and dec[cand]:
                    te = cand; ddir = -1 if lvl_side == 1 else 1
                resume = wend + 1
            else:
                resume = rec_i + 1
        if te >= 0:
            entry = ml[te]
            res = 0; i = te + 1
            end = te + cap
            if end > n - 1: end = n - 1
            while i <= end:
                up = hi[i] - entry; dn = entry - lo[i]
                if ddir == 1:
                    t_hit = up >= A; a_hit = dn >= B
                else:
                    t_hit = dn >= A; a_hit = up >= B
                if a_hit:                              # both-crossed -> adverse too
                    res = 2; break
                if t_hit:
                    res = 1; break
                i += 1
            if res == 1: g = float(A)
            elif res == 2: g = -float(B)
            else:
                res = 3; g = (ml[end] - entry) * ddir; i = end
            e_idx[m] = te; e_out[m] = res; e_gross[m] = g; m += 1
            next_ok = i + cool
            resume = i + 1
        armed = False                                  # disarm until re-arm 8t away
        t = resume
    return e_idx[:m], e_out[:m], e_gross[:m], n_sweep

SH = "research/scalping_lab/substrate/sechilo/NQ"
GR = "research/scalping_lab/substrate/grid1s/NQ"
OUTD = "research/scalping_lab/artifacts/w4_fss5"
os.makedirs(OUTD, exist_ok=True)

rows, lvl_rows = [], []
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
    dec = ((tod >= RTH0) & (tod < RTH1) & (upd60 > 0)).astype(np.bool_)
    on_m = tod < RTH0
    or_m = (tod >= RTH0) & (tod < OR15_END)
    levels = {}
    if on_m.sum() > 0:
        levels["ONH"] = (float(hi[on_m].max()), -1, (tod >= RTH0))
        levels["ONL"] = (float(lo[on_m].min()), 1, (tod >= RTH0))
    if or_m.sum() > 0:
        levels["OR15H"] = (float(hi[or_m].max()), -1, (tod >= OR15_END))
        levels["OR15L"] = (float(lo[or_m].min()), 1, (tod >= OR15_END))
    lvl_rows.append(dict(session=tag, n_sec=len(f), on_secs=int(on_m.sum()),
                         or_secs=int(or_m.sum()), dec_secs=int(dec.sum()),
                         **{k: v[0] for k, v in levels.items()}))
    for lname, (L, side, avail_arr) in levels.items():
        avail = avail_arr.astype(np.bool_)
        for mode, mname in ((0, "reclaim"), (1, "cont")):
            ddirname = ("long" if side == 1 else "short") if mode == 0 else \
                       ("short" if side == 1 else "long")
            for pierce in PIERCES:
                for W in WINDOWS:
                    for (A, B) in BRK:
                        ei, eo, eg, nsw = simulate_level(
                            ml, hi, lo, dec, avail, L, side, mode, pierce, W,
                            float(A), float(B), CAP, COOL, REARM)
                        rows.append(dict(session=tag, level=lname, mode=mname,
                                         dir=ddirname, pierce=pierce, W=W, A=A, B=B,
                                         n_sweep=nsw, n=len(ei),
                                         n_tgt=int((eo == 1).sum()),
                                         n_adv=int((eo == 2).sum()),
                                         n_cap=int((eo == 3).sum()),
                                         gross_sum=float(eg.sum())))
    print(tag, "done", flush=True)

R = pd.DataFrame(rows)
R.to_csv(os.path.join(OUTD, "w4c_results.csv"), index=False)
pd.DataFrame(lvl_rows).to_csv(os.path.join(OUTD, "w4c_levels.csv"), index=False)
NDAYS = len(sessions)
print(f"\nsessions={NDAYS}  per-session rows={len(R)}")

brng = np.random.default_rng(20260808)
pooled = []
def pool(gsub):
    """Pooled stats + day-clustered bootstrap CI (sessions with >=1 trade)."""
    g = gsub[gsub.n > 0]
    n = int(g.n.sum())
    out = dict(n_sweep=int(gsub.n_sweep.sum()), n=n, days=int((g.n > 0).sum()))
    if n == 0:
        return out
    dec_n = int((g.n_tgt + g.n_adv).sum())
    out["p_tgt"] = g.n_tgt.sum() / dec_n if dec_n else np.nan
    out["n_cap"] = int(g.n_cap.sum())
    gross = g.gross_sum.sum() / n
    out["net1"] = gross - C1; out["net2"] = gross - C2
    per = (g.gross_sum / g.n).values; w = g.n.values
    idx = np.arange(len(per))
    boots = np.empty(1000)
    for r in range(1000):
        b = brng.choice(idx, len(idx), replace=True)
        boots[r] = np.average(per[b], weights=w[b])
    out["ci1_lo"] = np.percentile(boots, 2.5) - C1
    out["ci1_hi"] = np.percentile(boots, 97.5) - C1
    out["ci2_lo"] = out["ci1_lo"] - 2.0; out["ci2_hi"] = out["ci1_hi"] - 2.0
    return out

for mname in ("reclaim", "cont"):
    hdr = "RECLAIM (primary side)" if mname == "reclaim" else "CONTINUATION mirror (diagnostic)"
    print(f"\n=== W4-C {hdr} — pooled by config ===")
    print(f"{'level':>6} {'dir':>5} {'prc':>3} {'W':>4} {'A':>3} {'B':>3} | {'sweeps':>6} "
          f"{'epi':>5} {'epi/d':>6} {'days':>4} {'P(tgt)':>7} {'BE_C1':>6} | "
          f"{'netC1':>7} {'CI_lo':>7} {'CI_hi':>7} | {'netC2':>7} | {'pass':>4}")
    for lname in ("ONL", "OR15L", "ONH", "OR15H"):
        for pierce in PIERCES:
            for W in WINDOWS:
                for (A, B) in BRK:
                    gsub = R[(R["level"] == lname) & (R["mode"] == mname)
                             & (R["pierce"] == pierce) & (R["W"] == W)
                             & (R["A"] == A) & (R["B"] == B)]
                    if not len(gsub): continue
                    o = pool(gsub)
                    ddir = gsub.dir.iloc[0]
                    star = " *" if (pierce == 2.0 and W == 60) else ""
                    if o["n"] == 0:
                        print(f"{lname:>6} {ddir:>5} {int(pierce):>3} {W:>4} {A:>3} {B:>3} | "
                              f"{o['n_sweep']:>6} {0:>5}  (no trades){star}")
                        pooled.append(dict(level=lname, mode=mname, dir=ddir, pierce=pierce,
                                           W=W, A=A, B=B, **o))
                        continue
                    be1 = (B + C1) / (A + B)
                    ok = (o["net1"] > 0) and (o["ci1_lo"] > -0.5)
                    print(f"{lname:>6} {ddir:>5} {int(pierce):>3} {W:>4} {A:>3} {B:>3} | "
                          f"{o['n_sweep']:>6} {o['n']:>5} {o['n']/NDAYS:>6.2f} {o['days']:>4} "
                          f"{o['p_tgt']:>7.4f} {be1:>6.4f} | {o['net1']:>+7.3f} "
                          f"{o['ci1_lo']:>+7.3f} {o['ci1_hi']:>+7.3f} | {o['net2']:>+7.3f} | "
                          f"{'PASS' if ok else 'fail':>4}{star}")
                    pooled.append(dict(level=lname, mode=mname, dir=ddir, pierce=pierce,
                                       W=W, A=A, B=B, be_c1=be1,
                                       passes=bool(ok), **o))
print("\n(* = primary config pierce=2t, W=60s; others are frozen neighbors."
      "\n pass rule: net C1 > 0 AND CI lower bound > -0.5t; epi/d over all "
      f"{NDAYS} sessions)")

P = pd.DataFrame(pooled)
P.to_csv(os.path.join(OUTD, "w4c_pooled.csv"), index=False)

print("\n=== primary configs (pierce=2, W=60) summary ===")
pr = P[(P["pierce"] == 2.0) & (P["W"] == 60)]
for _, r in pr.iterrows():
    if r["n"] == 0 or not np.isfinite(r.get("net1", np.nan)):
        print(f"  {r['mode']:>7} {r['level']:>6} {r['dir']:>5} +{r['A']}/-{r['B']}: no trades")
    else:
        print(f"  {r['mode']:>7} {r['level']:>6} {r['dir']:>5} +{int(r['A'])}/-{int(r['B'])}: "
              f"n={int(r['n'])} epi/d={r['n']/NDAYS:.2f} days={int(r['days'])} "
              f"P(tgt)={r['p_tgt']:.4f} netC1={r['net1']:+.3f} "
              f"[{r['ci1_lo']:+.3f},{r['ci1_hi']:+.3f}] netC2={r['net2']:+.3f} "
              f"{'PASS' if r['passes'] else 'fail'}")

npass_rec = int(P[(P['mode'] == 'reclaim') & (P['passes'] == True)].shape[0])
npass_cont = int(P[(P['mode'] == 'cont') & (P['passes'] == True)].shape[0])
print(f"\npassing configs: reclaim={npass_rec}/{len(P[P['mode']=='reclaim'])} "
      f"cont={npass_cont}/{len(P[P['mode']=='cont'])}")
print("\nW4C DONE")
