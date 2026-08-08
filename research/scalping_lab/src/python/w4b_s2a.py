"""W4-B — S2a python analog (owner seed, frozen params) per frozen spec
specs/W4_alpha_wave1.md section "W4-B" (committed before this run). Seed 20260808.

1-min completed bars from sechilo mid (O=first mid_last, H=max mid_high, L=min mid_low,
C=last mid_last per minute). LONG: C > max(prior 20 bars' H) AND CLV=(C-L)/(H-L) >= 0.70
(skip zero-range); 1-3 completed pullback bars, every close >= broken level, >=1 close <
prior close; trigger on 1s series: mid_last > max(pullback bar highs) + 1t, strictly after
the last completed pullback bar's close time; window 10:15-15:15 ET; cooldown 2 completed
1-min bars after exit; ONE trade per impulse. SHORT symmetric (CLV <= 0.30).
Exits: fixed-time {1,2,3,5,8} min at market (PRIMARY = 3 min); brackets (24,8)/(32,10)
cap 300s as secondary diagnostic. C1=2.872t, C2=4.872t. Sequential episode simulation,
conservative same-second-both-crossed -> adverse. Day-clustered bootstrap, 1000 reps.
"""
import glob, os
import numpy as np, pandas as pd
from numba import njit

C1, C2 = 2.872, 4.872
FIXED_MIN = [1, 2, 3, 5, 8]          # primary = 3
BRK = [(24, 8), (32, 10)]
CAP = 300
WIN_LO, WIN_HI = 10 * 3600 + 900, 15 * 3600 + 900   # 10:15 -> 15:15 ET
LOOKBACK = 20
CLV_LONG, CLV_SHORT = 0.70, 0.30
MAX_PB = 3
COOL_BARS = 2                        # 2 completed 1-min bars after exit
SEED = 20260808
NBOOT = 1000

SH = "research/scalping_lab/substrate/sechilo/NQ"
GR = "research/scalping_lab/substrate/grid1s/NQ"
OUTD = "research/scalping_lab/artifacts/w4_s2a"
os.makedirs(OUTD, exist_ok=True)


@njit(cache=True)
def simulate(ml, hi, lo, dec, winm, minute, m0, nb, boL, boS, lvlL, lvlS,
             bH, bL, bC, mode, p1, p2, cap):
    """Sequential state machine. mode 0 = fixed-time (p1 = exit secs);
    mode 1 = bracket (p1=A target ticks, p2=B adverse ticks, cap secs).
    Returns entry idx, dir, gross ticks, outcome (0 fixed / 1 tgt / 2 adv / 3 cap),
    exit idx, impulse-bar minute, entry price."""
    n = ml.shape[0]
    r_ei = np.empty(n, np.int64); r_dir = np.empty(n, np.int8)
    r_g = np.empty(n, np.float64); r_out = np.empty(n, np.int8)
    r_xi = np.empty(n, np.int64); r_bo = np.empty(n, np.int64)
    r_ep = np.empty(n, np.float64)
    m = 0
    armed = 0                       # 0 none, +1 long, -1 short
    bo_min = -10**9; level = 0.0; pb_ext = 0.0; any_dn = False; prev_close = 0.0
    cd_min = -10**18                # first minute eligible as breakout bar
    prev_m = minute[0]
    t = 0
    while t < n:
        cm = minute[t]
        if cm > prev_m:
            for mm in range(prev_m, cm):        # bars mm just completed
                bi = mm - m0
                if bi < 0 or bi >= nb:
                    continue
                if armed != 0:
                    i = mm - bo_min
                    if i >= 1:
                        if i > MAX_PB:
                            armed = 0           # expired without trigger
                        else:
                            c = bC[bi]
                            if not np.isfinite(c):
                                armed = 0
                            elif armed == 1:
                                if c < level:
                                    armed = 0   # close below broken level
                                else:
                                    if bH[bi] > pb_ext:
                                        pb_ext = bH[bi]
                                    if c < prev_close:
                                        any_dn = True
                                    prev_close = c
                            else:
                                if c > level:
                                    armed = 0
                                else:
                                    if bL[bi] < pb_ext:
                                        pb_ext = bL[bi]
                                    if c > prev_close:
                                        any_dn = True
                                    prev_close = c
                if armed == 0 and mm >= cd_min:
                    if boL[bi]:
                        armed = 1; bo_min = mm; level = lvlL[bi]
                        pb_ext = -1e18; any_dn = False; prev_close = bC[bi]
                    elif boS[bi]:
                        armed = -1; bo_min = mm; level = lvlS[bi]
                        pb_ext = 1e18; any_dn = False; prev_close = bC[bi]
            prev_m = cm
        if armed != 0 and any_dn and dec[t] and winm[t]:
            j = cm - bo_min - 1                 # completed pullback bars
            if 1 <= j <= MAX_PB:
                trig = False
                if armed == 1 and ml[t] > pb_ext + 1.0:
                    trig = True
                elif armed == -1 and ml[t] < pb_ext - 1.0:
                    trig = True
                if trig:
                    d = armed
                    e = ml[t]
                    if mode == 0:               # fixed-time market exit
                        tx = t + int(p1)
                        if tx > n - 1:
                            tx = n - 1
                        g = (ml[tx] - e) * d
                        out = 0
                    else:                       # bracket
                        A = p1; B = p2
                        end = min(t + cap, n - 1)
                        res = 0; i2 = t + 1
                        while i2 <= end:
                            up = hi[i2] - e; dn = e - lo[i2]
                            if d == 1:
                                th = up >= A; ah = dn >= B
                            else:
                                th = dn >= A; ah = up >= B
                            if th and ah:
                                res = 2; break  # same-second ambiguity -> adverse
                            if ah:
                                res = 2; break
                            if th:
                                res = 1; break
                            i2 += 1
                        if res == 1:
                            g = A; tx = i2
                        elif res == 2:
                            g = -B; tx = i2
                        else:
                            res = 3; g = (ml[end] - e) * d; tx = end
                        out = res
                    r_ei[m] = t; r_dir[m] = d; r_g[m] = g; r_out[m] = out
                    r_xi[m] = tx; r_bo[m] = bo_min; r_ep[m] = e
                    m += 1
                    armed = 0
                    cd_min = minute[tx] + COOL_BARS + 1   # 2 completed bars after exit
                    prev_m = minute[tx]
                    t = tx + 1
                    continue
        t += 1
    return r_ei[:m], r_dir[:m], r_g[:m], r_out[:m], r_xi[:m], r_bo[:m], r_ep[:m]


VARIANTS = [("fix1", 0, 60.0, 0.0), ("fix2", 0, 120.0, 0.0), ("fix3", 0, 180.0, 0.0),
            ("fix5", 0, 300.0, 0.0), ("fix8", 0, 480.0, 0.0),
            ("brk24_8", 1, 24.0, 8.0), ("brk32_10", 1, 32.0, 10.0)]

rows = []
bo_counts = []
sessions = sorted(os.path.basename(p)[:-8] for p in glob.glob(os.path.join(SH, "s*.parquet")))
print(f"sessions: {len(sessions)}")
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
    dec = ((tod >= 9 * 3600 + 1800) & (tod < 16 * 3600) & (upd60 > 0)).astype(np.bool_)
    winm = ((tod >= WIN_LO) & (tod < WIN_HI)).astype(np.bool_)
    minute = np.floor(tod / 60.0).astype(np.int64)

    # --- 1-min completed bars from sechilo mid on the 1s grid ---
    fb = pd.DataFrame({"m": minute, "ml": ml, "hi": hi, "lo": lo})
    bar = fb.groupby("m").agg(O=("ml", "first"), H=("hi", "max"),
                              L=("lo", "min"), C=("ml", "last"))
    m0 = int(bar.index.min()); m1 = int(bar.index.max())
    bar = bar.reindex(range(m0, m1 + 1))
    nb = len(bar)
    H20 = bar["H"].shift(1).rolling(LOOKBACK, min_periods=LOOKBACK).max()
    L20 = bar["L"].shift(1).rolling(LOOKBACK, min_periods=LOOKBACK).min()
    rng_ok = (bar["H"] - bar["L"]) > 0
    clv = (bar["C"] - bar["L"]) / (bar["H"] - bar["L"])
    boL = ((bar["C"] > H20) & (clv >= CLV_LONG) & rng_ok).fillna(False).values.astype(np.bool_)
    boS = ((bar["C"] < L20) & (clv <= CLV_SHORT) & rng_ok).fillna(False).values.astype(np.bool_)
    lvlL = H20.fillna(np.inf).values
    lvlS = L20.fillna(-np.inf).values
    bH = bar["H"].values; bL = bar["L"].values; bC = bar["C"].values
    bo_counts.append(dict(session=tag, n_boL=int(boL.sum()), n_boS=int(boS.sum())))

    for vname, mode, p1, p2 in VARIANTS:
        ei, dr, gr, ou, xi, bo, ep = simulate(ml, hi, lo, dec, winm, minute, m0, nb,
                                              boL, boS, lvlL, lvlS, bH, bL, bC,
                                              mode, p1, p2, CAP)
        for q in range(len(ei)):
            rows.append(dict(session=tag, variant=vname,
                             dir="long" if dr[q] == 1 else "short",
                             entry_idx=int(ei[q]), entry_tod=float(tod[ei[q]]),
                             entry_px=float(ep[q]), exit_idx=int(xi[q]),
                             exit_tod=float(tod[xi[q]]), gross=float(gr[q]),
                             outcome=int(ou[q]), bo_minute=int(bo[q])))
    print(tag, "done", flush=True)

T = pd.DataFrame(rows)
T.to_csv(os.path.join(OUTD, "w4b_trades.csv"), index=False)
BO = pd.DataFrame(bo_counts)
BO.to_csv(os.path.join(OUTD, "w4b_impulse_counts.csv"), index=False)
NS = len(sessions)
print(f"\nimpulse bars (all sessions): long={BO.n_boL.sum()} short={BO.n_boS.sum()} "
      f"(candidates; window/pullback/trigger filters apply downstream)")

rng = np.random.default_rng(SEED)


def boot_ci(sub):
    """Day-clustered CI on per-trade net C1: resample sessions, weight by trade count."""
    gs = sub.groupby("session")["gross"]
    per = (gs.mean() - C1).values
    w = gs.size().values.astype(float)
    if len(per) == 0:
        return np.nan, np.nan
    if len(per) == 1:
        return per[0], per[0]
    idx = np.arange(len(per))
    boots = np.empty(NBOOT)
    for r in range(NBOOT):
        b = rng.choice(idx, len(idx), replace=True)
        boots[r] = np.average(per[b], weights=w[b])
    return np.percentile(boots, 2.5), np.percentile(boots, 97.5)


pooled = []
print("\n=== W4-B S2a — pooled per exit variant (all trades, long+short) ===")
print(f"{'variant':>9} | {'n':>4} {'n/day':>6} {'days':>4} {'win%':>6} | {'gross':>7} "
      f"{'netC1':>7} {'CI_lo':>7} {'CI_hi':>7} | {'netC2':>7}")
for vname, mode, p1, p2 in VARIANTS:
    sub = T[T.variant == vname]
    for side in ("all", "long", "short"):
        ss = sub if side == "all" else sub[sub.dir == side]
        n = len(ss)
        if n == 0:
            pooled.append(dict(variant=vname, side=side, n=0))
            print(f"{vname:>9} [{side:>5}] | {0:>4}  (no trades)")
            continue
        days = ss.session.nunique()
        gross = ss.gross.mean()
        net1 = gross - C1; net2 = gross - C2
        win = (ss.gross > 0).mean()
        lo_, hi_ = boot_ci(ss)
        row = dict(variant=vname, side=side, n=n, n_per_day=n / NS, days=days,
                   win=win, gross=gross, netC1=net1, ci_lo=lo_, ci_hi=hi_, netC2=net2)
        if mode == 1:
            ntgt = int((ss.outcome == 1).sum()); nadv = int((ss.outcome == 2).sum())
            ncap = int((ss.outcome == 3).sum())
            row.update(n_tgt=ntgt, n_adv=nadv, n_cap=ncap,
                       p_tgt=ntgt / max(1, ntgt + nadv))
        else:
            qs = np.percentile(ss.gross.values, [0, 25, 50, 75, 100])
            row.update(g_min=qs[0], g_p25=qs[1], g_p50=qs[2], g_p75=qs[3], g_max=qs[4])
        pooled.append(row)
        star = " *PRIMARY*" if (vname == "fix3" and side == "all") else ""
        print(f"{vname:>9} [{side:>5}] | {n:>4} {n/NS:>6.2f} {days:>4} {100*win:>5.1f}% | "
              f"{gross:>+7.3f} {net1:>+7.3f} {lo_:>+7.3f} {hi_:>+7.3f} | {net2:>+7.3f}{star}")

P = pd.DataFrame(pooled)
P.to_csv(os.path.join(OUTD, "w4b_pooled.csv"), index=False)

print("\n=== fixed-time gross distribution quartiles (ticks, all trades) ===")
print(f"{'variant':>7} {'side':>6} | {'min':>8} {'p25':>7} {'p50':>7} {'p75':>7} {'max':>8}")
for vname in ("fix1", "fix2", "fix3", "fix5", "fix8"):
    for side in ("all", "long", "short"):
        ss = T[T.variant == vname] if side == "all" else \
             T[(T.variant == vname) & (T.dir == side)]
        if len(ss) == 0:
            continue
        qs = np.percentile(ss.gross.values, [0, 25, 50, 75, 100])
        print(f"{vname:>7} {side:>6} | {qs[0]:>8.2f} {qs[1]:>7.2f} {qs[2]:>7.2f} "
              f"{qs[3]:>7.2f} {qs[4]:>8.2f}")

print("\n=== bracket outcome detail ===")
for vname in ("brk24_8", "brk32_10"):
    for side in ("all", "long", "short"):
        ss = T[T.variant == vname] if side == "all" else \
             T[(T.variant == vname) & (T.dir == side)]
        if len(ss) == 0:
            continue
        ntgt = int((ss.outcome == 1).sum()); nadv = int((ss.outcome == 2).sum())
        ncap = int((ss.outcome == 3).sum())
        print(f"{vname:>9} {side:>6}: n={len(ss):>4} tgt={ntgt:>4} adv={nadv:>4} "
              f"cap={ncap:>4} P(tgt-first)={ntgt/max(1,ntgt+nadv):.4f}")

prim = T[T.variant == "fix3"]
print(f"\nPRIMARY (fix3, all): n={len(prim)} netC1={prim.gross.mean()-C1:+.3f}t "
      f"netC2={prim.gross.mean()-C2:+.3f}t")
print("\nW4B DONE")
