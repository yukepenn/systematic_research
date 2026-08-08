"""SMV2F — leverage frontier under long-dependence resampling ($100k base, compounded)."""
import sys, os
import numpy as np, pandas as pd
sys.path.insert(0, "src/analytics")

OUT = "runs/SMV2F_LEVERAGE_ROBUST/out"; os.makedirs(OUT, exist_ok=True)
SEED, NB, CAP = 20260808, 2000, 100_000.0
cur = pd.read_csv("runs/SMV2A_DD_RECONCILE/out/daily_curves.csv", parse_dates=["sess"])
cal = pd.DatetimeIndex(cur["sess"]); n = len(cal)
objs = {"A_SOLAR_E10": cur["A"].to_numpy(), "E_PORT_TILT_532": cur["E"].to_numpy(),
        "C_DAYONLY_SOLAR_BMOM": cur["C"].to_numpy(), "G_ONELOT_NQ": cur["G"].to_numpy()}

rng = np.random.default_rng(SEED)
years = cal.year.to_numpy(); qkey = cal.year * 10 + cal.quarter

def idx_moving_block(L):
    nb = int(np.ceil(n / L))
    starts = rng.integers(0, n, size=(NB, nb))
    idx = (starts[:, :, None] + np.arange(L)[None, None, :]) % n
    return idx.reshape(NB, -1)[:, :n]

def idx_stationary(mean_L):
    p = 1.0 / mean_L
    idx = np.empty((NB, n), dtype=np.int64)
    cur_i = rng.integers(0, n, size=NB)
    for t in range(n):
        jump = rng.random(NB) < p
        cur_i = np.where(jump, rng.integers(0, n, size=NB), (cur_i + 1) % n)
        idx[:, t] = cur_i
    return idx

def idx_group(keys):
    uk = np.unique(keys)
    groups = [np.where(keys == k)[0] for k in uk]
    out = np.empty((NB, n), dtype=np.int64)
    for b in range(NB):
        parts = []
        total = 0
        while total < n:
            gi = groups[rng.integers(0, len(uk))]
            parts.append(gi); total += len(gi)
        out[b] = np.concatenate(parts)[:n]
    return out

methods = {"L5": idx_moving_block(5), "L20": idx_moving_block(20),
           "L60": idx_moving_block(60), "L120": idx_moving_block(120),
           "stat60": idx_stationary(60), "quarter": idx_group(qkey), "year": idx_group(years)}

def dd_prob_and_growth(pnl, idx, f, thr):
    r = f * pnl[idx] / CAP
    eq = np.cumprod(1.0 + np.clip(r, -0.95, None), axis=1)
    peak = np.maximum.accumulate(eq, axis=1)
    dd = 1.0 - eq / peak
    p_exceed = (dd.max(axis=1) > thr).mean()
    g = np.median(eq[:, -1] ** (252.0 / n) - 1.0)
    return p_exceed, g

rows = []
for oname, pnl in objs.items():
    for mname, idx in methods.items():
        for thr in (0.15, 0.20, 0.25, 0.30):
            lo_f, hi_f = 0.0, 8.0
            for _ in range(14):
                mid = 0.5 * (lo_f + hi_f)
                p, _ = dd_prob_and_growth(pnl, idx, mid, thr)
                if p > 0.05: hi_f = mid
                else: lo_f = mid
            fstar = lo_f
            _, g = dd_prob_and_growth(pnl, idx, fstar, thr)
            rows.append({"object": oname, "method": mname, "thr": thr, "f_star": fstar,
                         "median_growth": g})
            print(f"{oname} {mname} thr={thr:.2f} f*={fstar:.2f} growth={g*100:.1f}%")
df = pd.DataFrame(rows)
df.to_csv(f"{OUT}/frontier_robust.csv", index=False)
piv = df[df.thr == 0.25].pivot(index="object", columns="method", values="median_growth")
print("\nMedian growth at P(DD>25%)<=5%:"); print((piv * 100).round(1).to_string())
