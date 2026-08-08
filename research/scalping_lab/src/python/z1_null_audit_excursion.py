"""W2-0 supplement: the published excursion-baseline claim ('uncond +1-2pp over the
gambler's-ruin null = mild momentum') gets the same matched-null treatment. B/(A+B) is
exact only for continuous/unit-step paths; jumps can shift it. Run the EXACT excursion
scan on OBS and on NULL-3 (sign-flipped increments, seed 20260809), paired by session."""
import glob, os
import numpy as np, pandas as pd
from numba import njit

EXC = [(4,2),(6,2),(6,3),(8,4)]

@njit(cache=True)
def excursion(mid, starts, dirs, A, B, cap):
    hit = 0; tot = 0
    for s in range(starts.shape[0]):
        i0 = starts[s]; d = dirs[s]; p0 = mid[i0]
        end = min(i0 + cap, mid.shape[0])
        for i in range(i0+1, end):
            m = (mid[i] - p0) * d
            if m >= A: hit += 1; tot += 1; break
            if m <= -B: tot += 1; break
    return hit, tot

rng = np.random.default_rng(20260809)
rows = []
files = sorted(glob.glob("research/scalping_lab/substrate/raw/NQ/s*.parquet"))
files = [f for f in files if "_rth" not in f]
for pq in files:
    tag = os.path.basename(pq)[:-8]
    df = pd.read_parquet(pq)
    if (df["bip"] == 1).sum() == 0: continue
    df["time"] = pd.to_datetime(df["time"])
    B_ = df[df.bip == 1][["time","price"]].rename(columns={"price": "bid"})
    A_ = df[df.bip == 2][["time","price"]].rename(columns={"price": "ask"})
    Q = pd.merge_asof(B_.sort_values("time"), A_.sort_values("time"), on="time").dropna()
    mid = ((Q["bid"].values + Q["ask"].values) / 2.0) / 0.25
    dm = np.diff(mid)
    null3 = mid[0] + np.concatenate(([0.0], np.cumsum(np.abs(dm) * rng.choice(np.array([-1.0, 1.0]), size=len(dm)))))
    st = np.arange(1000, len(mid) - 1000, 2000).astype(np.int64)
    d1 = np.ones(len(st), np.int64)
    for kind, path in (("OBS", mid), ("NULL3", null3)):
        for (Aq, Bq) in EXC:
            hu, tu = excursion(path, st, d1, float(Aq), float(Bq), 200000)
            hd, td = excursion(path, st, -d1, float(Aq), float(Bq), 200000)
            rows.append(dict(kind=kind, session=tag, A=Aq, Bneg=Bq,
                             p=(hu + hd) / (tu + td), n=tu + td))
    print(tag, "done", flush=True)

R = pd.DataFrame(rows)
R.to_csv("research/scalping_lab/artifacts/z1/z1_null_audit_excursion.csv", index=False)
brng = np.random.default_rng(20260809)
print("\n=== unconditional excursion p: OBS vs matched NULL-3 (paired by session) ===")
for (Aq, Bq) in EXC:
    o = R[(R.kind == "OBS") & (R.A == Aq) & (R.Bneg == Bq)].set_index("session")["p"]
    z = R[(R.kind == "NULL3") & (R.A == Aq) & (R.Bneg == Bq)].set_index("session")["p"]
    c = o.index.intersection(z.index)
    d = (o.loc[c] - z.loc[c]).values
    b = [np.mean(brng.choice(d, len(d), replace=True)) for _ in range(2000)]
    print(f"  +{Aq}/-{Bq}: ruin-null {Bq/(Aq+Bq):.3f} | OBS {o.loc[c].mean():.4f} | NULL3 {z.loc[c].mean():.4f} "
          f"| paired diff {d.mean():+.4f} [{np.percentile(b,2.5):+.4f},{np.percentile(b,97.5):+.4f}] (n={len(c)})")
