"""SMV2R sub_381 — clamp audit (DIAGNOSTIC, seq 381).
Distribution of S = clamp(k*sigma460, 40t, 1200t) per member per bar on dev:
% bars at lower bound, % at upper, by member and by year.
Bound convention (V3 ResolveS): binds when k*sigma <= 40*TICK (lower) or >= 1200*TICK (upper).
Bars with sigma NaN (warmup, first 30 bars of 2022) use the 179t fallback and are excluded
from the clamp denominator (counted separately).
"""
import sys, os, datetime as dt
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
import sm01_solarsim as sm

RUN = os.path.join(ROOT, "runs", "SMV2R_SOLAR_CORE_1")
OUT = os.path.join(RUN, "out"); os.makedirs(OUT, exist_ok=True)
DEV_END = dt.date(2026, 5, 31)

bars = sm.load_bars_3m(os.path.join(ROOT, "runs", "AUDIT03_BARS", "nq_3m_2022_2026.csv"))
bars = bars[bars["sess_date"] <= DEV_END].reset_index(drop=True)
close = bars.close.to_numpy()
sig = sm.sigma_series(close)
year = pd.to_datetime(bars["sess_date"]).dt.year.to_numpy()

LO = 40 * sm.TICK    # 10.0 pts
HI = 1200 * sm.TICK  # 300.0 pts
finite = np.isfinite(sig)
rows = []
for vm in sm.VMS:
    s_raw = vm * sig
    at_lo = finite & (s_raw <= LO)
    at_hi = finite & (s_raw >= HI)
    for yr in sorted(set(year)):
        m = (year == yr) & finite
        rows.append({"member_vm": vm, "year": int(yr), "n_bars": int(m.sum()),
                     "pct_at_lower": float((at_lo & m).sum() / m.sum() * 100) if m.sum() else np.nan,
                     "pct_at_upper": float((at_hi & m).sum() / m.sum() * 100) if m.sum() else np.nan})
    m = finite
    rows.append({"member_vm": vm, "year": "ALL", "n_bars": int(m.sum()),
                 "pct_at_lower": float((at_lo & m).sum() / m.sum() * 100),
                 "pct_at_upper": float((at_hi & m).sum() / m.sum() * 100)})

df = pd.DataFrame(rows)
df.to_csv(os.path.join(OUT, "clamp_audit.csv"), index=False)

allrows = df[df.year == "ALL"]
worst_lo = allrows.pct_at_lower.max(); worst_hi = allrows.pct_at_upper.max()
verdict = "BOUND-IRRELEVANT" if (worst_lo < 1.0 and worst_hi < 1.0) else "BOUND-BINDS"
meta = {"n_nan_sigma_bars": int((~finite).sum()),
        "worst_member_pct_at_lower": float(worst_lo),
        "worst_member_pct_at_upper": float(worst_hi),
        "sigma460_dev_median_pts": float(np.nanmedian(sig)),
        "sigma460_dev_p1_pts": float(np.nanpercentile(sig, 1)),
        "sigma460_dev_p99_pts": float(np.nanpercentile(sig, 99)),
        "lower_bound_pts": LO, "upper_bound_pts": HI, "verdict": verdict}
import json
with open(os.path.join(OUT, "clamp_audit_meta.json"), "w") as f:
    json.dump(meta, f, indent=2)
print(df[df.year == "ALL"].to_string(index=False))
print(json.dumps(meta, indent=2))
