"""W2-0 Z1_DEFINITION_AND_NULL_AUDIT (Amendment 4 par.2). Spec frozen before readout.
dc_segments copied VERBATIM from z1_dc_ladder.py lines 10-32 (audit must run the exact
detector). omega recorded there = |ext - prev_ext| = TOTAL MOVEMENT (TM). Identity:
OS = TM - theta. Nulls: NULL-1 discrete +-1 RW; NULL-2 sigma-matched Gaussian;
NULL-3 (primary) empirical |dmid| sequence with iid random signs. Plus direct
entry->exit parity P&L vs the omega algebra. Seed 20260808."""
import glob, os
import numpy as np, pandas as pd
from numba import njit

TH = [5, 10, 20, 40, 80, 160]

@njit(cache=True)
def dc_segments(mid, theta):
    n = mid.shape[0]
    amps = np.empty(n, np.float64); flips = np.empty(n, np.int64); dirs = np.empty(n, np.int8)
    k = 0
    ext = mid[0]; prev_ext = np.nan; up = True
    started = False
    for i in range(1, n):
        p = mid[i]
        if up:
            if p > ext: ext = p
            elif ext - p >= theta:
                if started and not np.isnan(prev_ext):
                    amps[k] = abs(ext - prev_ext); flips[k] = i; dirs[k] = 1; k += 1
                prev_ext = ext; ext = p; up = False; started = True
        else:
            if p < ext: ext = p
            elif p - ext >= theta:
                if started and not np.isnan(prev_ext):
                    amps[k] = abs(ext - prev_ext); flips[k] = i; dirs[k] = -1; k += 1
                prev_ext = ext; ext = p; up = True; started = True
    return amps[:k], flips[:k], dirs[:k]

def stats_for(mid, theta):
    """r_TM, r_OS, algebraic capture, DIRECT flip-to-flip capture (actual flip mids)."""
    amps, flips, dirs = dc_segments(mid, float(theta))
    if len(amps) < 4:
        return None
    r_tm = amps.mean() / theta
    r_os = r_tm - 1.0                      # identity OS = TM - theta
    alg = amps.mean() - 2.0 * theta
    fm = mid[flips]
    # trade k: enter at flip k in NEW trend (opposite of ended segment dirs[k]), exit flip k+1
    pnl = dirs[:-1] * (fm[:-1] - fm[1:])
    return dict(n=len(amps), r_tm=r_tm, r_os=r_os, alg_pc=alg, direct_pc=pnl.mean())

rng = np.random.default_rng(20260808)
rows = []

# ---- NULL-1: discrete symmetric +-1 tick random walk, 5M steps x 8 seeds ----
for seed in range(8):
    r1 = np.random.default_rng(20260808 + seed)
    path = np.cumsum(r1.choice(np.array([-1.0, 1.0]), size=5_000_000))
    for th in TH:
        s = stats_for(path, th)
        if s: rows.append(dict(kind="NULL1_rw", session=f"seed{seed}", theta=th, **s))
    print("NULL1 seed", seed, "done", flush=True)

# ---- empirical sessions: observed + NULL-2 + NULL-3 + parity ----
files = sorted(glob.glob("research/scalping_lab/substrate/raw/NQ/s*.parquet"))
files = [f for f in files if "_rth" not in f]
for pq in files:
    tag = os.path.basename(pq)[:-8]
    df = pd.read_parquet(pq)
    if (df["bip"] == 1).sum() == 0: continue
    df["time"] = pd.to_datetime(df["time"])
    B_ = df[df.bip == 1][["time", "price"]].rename(columns={"price": "bid"})
    A_ = df[df.bip == 2][["time", "price"]].rename(columns={"price": "ask"})
    Q = pd.merge_asof(B_.sort_values("time"), A_.sort_values("time"), on="time").dropna()
    mid = ((Q["bid"].values + Q["ask"].values) / 2.0) / 0.25
    dm = np.diff(mid)
    # NULL-3: same |dm| sequence, iid signs (primary matched martingale null)
    null3 = mid[0] + np.concatenate(([0.0], np.cumsum(np.abs(dm) * rng.choice(np.array([-1.0, 1.0]), size=len(dm)))))
    # NULL-2: iid Gaussian, sigma matched, same length
    null2 = mid[0] + np.concatenate(([0.0], np.cumsum(rng.normal(0.0, dm.std(), size=len(dm)))))
    for th in TH:
        for kind, path in (("OBS", mid), ("NULL3_signflip", null3), ("NULL2_gauss", null2)):
            s = stats_for(path, th)
            if s: rows.append(dict(kind=kind, session=tag, theta=th, **s))
    print(tag, "done", flush=True)

R = pd.DataFrame(rows)
os.makedirs("research/scalping_lab/artifacts/z1", exist_ok=True)
R.to_csv("research/scalping_lab/artifacts/z1/z1_null_audit.csv", index=False)

print("\n=== r_TM = E[TM]/theta by kind (mean over sessions/seeds) ===")
piv = R.pivot_table(index="theta", columns="kind", values="r_tm", aggfunc="mean").round(4)
print(piv.to_string())
print("\n=== r_OS = E[OS]/theta ===")
print(R.pivot_table(index="theta", columns="kind", values="r_os", aggfunc="mean").round(4).to_string())
print("\n=== algebraic capture/cycle (omega-2theta), ticks ===")
print(R.pivot_table(index="theta", columns="kind", values="alg_pc", aggfunc="mean").round(3).to_string())
print("\n=== DIRECT flip-to-flip capture/cycle (actual flip mids), ticks ===")
print(R.pivot_table(index="theta", columns="kind", values="direct_pc", aggfunc="mean").round(3).to_string())

# paired excess vs NULL-3, day-clustered bootstrap over sessions
print("\n=== OBS minus NULL3 (paired by session): r_TM excess and capture excess ===")
obs = R[R.kind == "OBS"].set_index(["session", "theta"])
n3 = R[R.kind == "NULL3_signflip"].set_index(["session", "theta"])
brng = np.random.default_rng(20260808)
for th in TH:
    o = obs.xs(th, level="theta"); z = n3.xs(th, level="theta")
    common = o.index.intersection(z.index)
    if len(common) < 5: continue
    d_r = (o.loc[common, "r_tm"] - z.loc[common, "r_tm"]).values
    d_cap = (o.loc[common, "direct_pc"] - z.loc[common, "direct_pc"]).values
    def ci(v):
        b = [np.mean(brng.choice(v, len(v), replace=True)) for _ in range(2000)]
        return np.percentile(b, 2.5), np.percentile(b, 97.5)
    lo_r, hi_r = ci(d_r); lo_c, hi_c = ci(d_cap)
    print(f"  theta={th:>3}: d_rTM {d_r.mean():+.4f} [{lo_r:+.4f},{hi_r:+.4f}] | "
          f"d_direct {d_cap.mean():+.3f}t [{lo_c:+.3f},{hi_c:+.3f}] (n={len(common)})")

print("\n=== DIRECT vs ALGEBRAIC on OBS (parity gap, ticks/cycle) ===")
o = R[R.kind == "OBS"]
gap = o.assign(gap=o.direct_pc - o.alg_pc).groupby("theta")["gap"].agg(["mean", "std"]).round(3)
print(gap.to_string())
print("\n=== OBS direct net C1 (direct_pc - 2.872), day-clustered CI ===")
for th in TH:
    v = o[o.theta == th]["direct_pc"].values - 2.872
    if len(v) < 5: continue
    b = [np.mean(brng.choice(v, len(v), replace=True)) for _ in range(2000)]
    print(f"  theta={th:>3}: {v.mean():+.3f}t [{np.percentile(b,2.5):+.3f},{np.percentile(b,97.5):+.3f}]")
