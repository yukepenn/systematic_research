"""U4 — is r = E[omega]/theta invariant in TICK space or SIGMA space?

Pure analytics on runs/AUDIT03_BARS/nq_3m_2022_2026.csv. No config burn.
Reuses src/analytics/dc_overshoot.dc_segments verbatim.
"""
import sys
import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, REPO + r"\src")
from analytics.dc_overshoot import dc_segments  # noqa: E402

TICK = 0.25
THETAS = [60, 90, 120, 179, 240, 320, 420, 560, 740]
SIGMA_WIN = 460  # bars, trailing, causal

df = pd.read_csv(REPO + r"\runs\AUDIT03_BARS\nq_3m_2022_2026.csv", parse_dates=["time"])
c = df["close"].to_numpy(float)
years = df["time"].dt.year.to_numpy()
print(f"bars={len(c)}  span={df.time.iloc[0]} .. {df.time.iloc[-1]}")

# causal sigma: trailing mean |dclose| over 460 bars, in ticks/bar (includes current bar)
absd_ticks = np.abs(np.diff(c, prepend=c[0])) / TICK
sigma = pd.Series(absd_ticks).rolling(SIGMA_WIN, min_periods=SIGMA_WIN).mean().to_numpy()

segs = []
for th in THETAS:
    s = dc_segments(c, th, TICK)
    s["theta"] = th
    s["year"] = years[s["i_next"].to_numpy()]
    s["omega_ticks"] = s["omega"] / TICK
    s["r"] = s["omega_ticks"] / th
    s["sigma_b"] = sigma[s["i_flip"].to_numpy()]
    s["ratio"] = th / s["sigma_b"]  # theta/sigma at birth (dimensionless)
    segs.append(s)
A = pd.concat(segs, ignore_index=True)

pd.set_option("display.width", 200)
pd.set_option("display.float_format", lambda v: f"{v:.3f}")

# ---------- 1. TICK SPACE: r by theta x year ----------
print("\n=== T1: r = mean(omega)/theta, TICK space, by theta x year ===")
r_ty = A.pivot_table(index="theta", columns="year", values="r", aggfunc="mean")
n_ty = A.pivot_table(index="theta", columns="year", values="r", aggfunc="size")
print(r_ty.round(3))
print("\nsegment counts:")
print(n_ty.astype(int))

print("\n=== check: theta=179 yearly mean omega (ticks) and r ===")
chk = A[A.theta == 179].groupby("year").agg(mean_omega_ticks=("omega_ticks", "mean"),
                                            r=("r", "mean"), n=("r", "size"))
print(chk.round(3))

# ---------- 2. SIGMA control ----------
S = A.dropna(subset=["sigma_b"]).copy()
print(f"\nsigma coverage: {len(S)}/{len(A)} segments have sigma_at_birth")
print("theta/sigma ratio quantiles (pooled):")
print(S["ratio"].quantile([0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99]).round(2))
print("sigma_b (ticks/bar) quantiles:", S["sigma_b"].quantile([0.05, 0.5, 0.95]).round(2).to_dict())

# per-theta sigma-at-birth terciles (year-pooled)
S["terc"] = S.groupby("theta")["sigma_b"].transform(
    lambda x: pd.qcut(x, 3, labels=["loVol", "midVol", "hiVol"]))
print("\n=== T2a: r per (theta, sigma-at-birth tercile), year-pooled ===")
t2a = S.pivot_table(index="theta", columns="terc", values="r", aggfunc="mean", observed=True)
t2a_n = S.pivot_table(index="theta", columns="terc", values="r", aggfunc="size", observed=True)
print(t2a.round(3))
print("n per cell (min):", int(t2a_n.min().min()))

print("\n=== T2b: theta=179, r per (tercile, year) ===")
s179 = S[S.theta == 179]
t2b = s179.pivot_table(index="terc", columns="year", values="r", aggfunc="mean", observed=True)
t2b_n = s179.pivot_table(index="terc", columns="year", values="r", aggfunc="size", observed=True)
print(t2b.round(3))
print("n:")
print(t2b_n.astype(int))

# does r depend on theta after controlling for theta/sigma? pooled deciles x theta-group
S["ratio_dec"] = pd.qcut(S["ratio"], 10, labels=False) + 1
S["th_grp"] = pd.cut(S["theta"], bins=[0, 130, 330, 800],
                     labels=["th 60-120", "th 179-320", "th 420-740"])
print("\n=== T2c: r by pooled theta/sigma decile x theta group (theta effect after sigma control) ===")
t2c = S.pivot_table(index="ratio_dec", columns="th_grp", values="r", aggfunc="mean", observed=True)
t2c_n = S.pivot_table(index="ratio_dec", columns="th_grp", values="r", aggfunc="size", observed=True)
print(pd.concat([t2c.round(3), t2c_n.add_prefix("n ")], axis=1))

# ---------- 3. VERDICT metric: CV of r across years ----------
MIN_N = 30

def cv(x):
    x = x.dropna()
    return np.nan if len(x) < 3 else x.std(ddof=1) / x.mean()

# fixed tick-theta: yearly r per theta (cells need >= MIN_N segs)
ry = A.groupby(["theta", "year"]).agg(r=("r", "mean"), n=("r", "size")).reset_index()
ry = ry[ry.n >= MIN_N]
cv_tick = ry.groupby("theta")["r"].apply(cv).rename("CV_r_tick")

# fixed theta/sigma bands: geometric edges covering the pooled data
q01, q99 = S["ratio"].quantile([0.005, 0.995])
edges = np.round(np.geomspace(q01, q99, 11), 1)
S["band"] = pd.cut(S["ratio"], bins=edges)
by = S.groupby(["band", "year"], observed=True).agg(r=("r", "mean"), n=("r", "size")).reset_index()
by = by[by.n >= MIN_N]
cv_sig = by.groupby("band", observed=True)["r"].apply(cv).rename("CV_r_sigma_band")
n_band = S.groupby("band", observed=True).size().rename("n_total")

print("\n=== T3a: CV of yearly r, fixed TICK theta ===")
print(cv_tick.round(4))
print(f"mean CV (tick space) = {cv_tick.mean():.4f}   median = {cv_tick.median():.4f}")

print("\n=== T3b: CV of yearly r, fixed theta/sigma band (edges: " + str(list(edges)) + ") ===")
print(pd.concat([cv_sig, n_band], axis=1).round(4))
w = n_band.reindex(cv_sig.index)
print(f"mean CV (sigma space) = {cv_sig.mean():.4f}   median = {cv_sig.median():.4f}   "
      f"n-weighted = {(cv_sig * w).sum() / w[cv_sig.notna()].sum():.4f}")
wt = ry.groupby('theta')['n'].sum().reindex(cv_tick.index)
print(f"n-weighted CV (tick space) = {(cv_tick * wt).sum() / wt[cv_tick.notna()].sum():.4f}")

# ---------- 4. pooled r(theta) shape ----------
print("\n=== T4: pooled r(theta) ===")
t4 = A.groupby("theta").agg(r=("r", "mean"), n=("r", "size"),
                            mean_omega_ticks=("omega_ticks", "mean"),
                            se=("r", lambda x: x.std(ddof=1) / np.sqrt(len(x))))
print(t4.round(4))
