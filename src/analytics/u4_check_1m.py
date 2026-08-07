"""Validate pipeline vs known DR05-H1 arm(a) band: 1-min NQ, theta=179, yearly mean omega."""
import sys
import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, REPO + r"\src")
from analytics.dc_overshoot import dc_segments

TICK = 0.25
df = pd.read_csv(REPO + r"\runs\B01A_BARS_1M\nq_1m_2022_2026.csv", parse_dates=["time"])
c = df["close"].to_numpy(float)
years = df["time"].dt.year.to_numpy()
s = dc_segments(c, 179, TICK)
s["year"] = years[s["i_next"].to_numpy()]
s["omega_ticks"] = s["omega"] / TICK
out = s.groupby("year").agg(mean_omega_ticks=("omega_ticks", "mean"), n=("omega_ticks", "size"))
out["r"] = out["mean_omega_ticks"] / 179
print(out.round(3))
