"""U4 addendum: full T2c, yearly sigma context, matched-scale CV."""
import sys
import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, REPO + r"\src")
from analytics.dc_overshoot import dc_segments

TICK = 0.25
THETAS = [60, 90, 120, 179, 240, 320, 420, 560, 740]
df = pd.read_csv(REPO + r"\runs\AUDIT03_BARS\nq_3m_2022_2026.csv", parse_dates=["time"])
c = df["close"].to_numpy(float)
years = df["time"].dt.year.to_numpy()
absd = np.abs(np.diff(c, prepend=c[0])) / TICK
sigma = pd.Series(absd).rolling(460, min_periods=460).mean().to_numpy()

print("yearly mean sigma (ticks/bar, 460-bar trailing):")
print(pd.Series(sigma, index=years).groupby(level=0).mean().round(2))

segs = []
for th in THETAS:
    s = dc_segments(c, th, TICK)
    s["theta"] = th
    s["year"] = years[s["i_next"].to_numpy()]
    s["r"] = s["omega"] / TICK / th
    s["sigma_b"] = sigma[s["i_flip"].to_numpy()]
    s["ratio"] = th / s["sigma_b"]
    segs.append(s)
S = pd.concat(segs, ignore_index=True).dropna(subset=["sigma_b"])
S["ratio_dec"] = pd.qcut(S["ratio"], 10)
S["th_grp"] = pd.cut(S["theta"], bins=[0, 130, 330, 800],
                     labels=["th60-120", "th179-320", "th420-740"])
pd.set_option("display.width", 250)
t2c_r = S.pivot_table(index="ratio_dec", columns="th_grp", values="r", aggfunc="mean", observed=True)
t2c_n = S.pivot_table(index="ratio_dec", columns="th_grp", values="r", aggfunc="size", observed=True)
print("\nT2c full — r by pooled theta/sigma decile x theta group:")
print(t2c_r.round(3))
print(t2c_n.fillna(0).astype(int))

# matched-scale CV: theta=179 tick CV vs the band its median ratio lives in
s179 = S[S.theta == 179]
print(f"\ntheta=179 median theta/sigma by year:")
print(s179.groupby("year")["ratio"].median().round(2))
