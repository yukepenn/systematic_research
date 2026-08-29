"""Program-printed addendum: era/store decomposition of the E1 measured RT cost.

Informational only — the preregistered verdict is decided on the POOLED maximized
overlap (gate GF); this file just decomposes the same measured RTs so the OPTIMISTIC
excess can be located in time. No re-selection, no threshold re-application.
"""
import os

import numpy as np
import pandas as pd

OUT = os.path.join(r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
                   r"\systematic_research", "runs", "G2_EXEC01_P1_EXECUTION_20260828",
                   "out")
R = pd.read_csv(os.path.join(OUT, "rt_cost_distribution.csv"))
ds = R["date"].astype(str)
R["era"] = np.where(ds < "20260101", "2025H2(Aug-Dec)",
                    np.where(ds < "20260531", "2026Jan-May", "2026Jun-Jul(BURNED win)"))
lines = []
lines.append("ERA / STORE DECOMPOSITION OF E1 MEASURED RT COST (printed by program)")
lines.append("pooled preregistered PRIMARY: contract-weighted mean "
             f"${np.average(R['cost_rt'], weights=R['u']):.2f}/ctrRT on "
             f"{len(R)} RTs / {int(R['u'].sum())} ctrRT")
lines.append("")
lines.append(f"{'slice':<26}{'n_rt':>6}{'ctrRT':>7}{'measured$':>11}{'model$':>9}"
             f"{'excess$':>9}")
for key in ("era", "store"):
    for k, g in R.groupby(key):
        mc = np.average(g["cost_rt"], weights=g["u"])
        mm = np.average(g["model_rt"], weights=g["u"])
        lines.append(f"{k:<26}{len(g):>6}{int(g['u'].sum()):>7}{mc:>11.2f}{mm:>9.2f}"
                     f"{mc-mm:>9.2f}")
    lines.append("")
lines.append("NOTE: the pooled OPTIMISTIC excess is concentrated in 2026-Jun-Jul "
             "(inside the burned window); 2025H2 and 2026Jan-May sit in the "
             "UNRESOLVED band on their own. The preregistered verdict is pooled by "
             "design and is not re-decided here.")
txt = "\n".join(lines) + "\n"
with open(os.path.join(OUT, "era_breakdown.txt"), "w", encoding="utf-8") as f:
    f.write(txt)
print(txt)
