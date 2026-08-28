"""CLOSURE DIAGNOSTIC -- was the surface EMPTY, or was the implementation merely EXPENSIVE?

⛔ THIS IS NOT A RESCUE AND NOT A NEW FORMULATION.  It fits nothing, tunes nothing, and changes no
gate.  It measures the association between the ALREADY-FROZEN signal S(i,d) and the subsequent
weekly root return, on the ALREADY-CONSUMED development population, for exactly one purpose: to
decide honestly whether MULTI-MARKET VOLUME / LIQUIDITY should remain on the research frontier as
an open surface, or be recorded as measured-and-empty.

It runs AFTER the gate table.  The verdict is already fixed and nothing here can move it.
None of SPEC 9's forbidden variations is computed: no 20/42/126d, no alternative rebalance, no
sector-only, no long-only, no nonlinear transform, no ML.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
sys.path.insert(0, HERE)
import vl_primary as VP                                                      # noqa: E402

OUT = os.path.join(RUN, "out")
_fh = open(os.path.join(OUT, "vl_closure_diag.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


P("=" * 112)
P("=== VOLUME_LIQUIDITY_V1 CLOSURE DIAGNOSTIC -- empty surface, or expensive implementation?")
P("=== NOT A RESCUE. Nothing is fitted, tuned or re-specified. The verdict is already fixed.")
P("=" * 112)

base = VP.run(date_max=VP.DEV_END)
pos, daily = base["pos"], base["daily"]

# realized weekly root return, in units of that root's own lagged sigma -- the scale the position
# was actually built in, so the correlation is the one the strategy could have monetised
wk = daily.groupby(["root", "monday"]).agg(ret_usd=("ret_usd", "sum")).reset_index()
m = pos[["monday", "root", "sector", "S", "ZVOL", "RELZ", "SIGMA"]].merge(
    wk, on=["root", "monday"], how="inner")
m["fwd_sigma_units"] = m["ret_usd"] / m["SIGMA"]
m = m[np.isfinite(m["fwd_sigma_units"])]

P("")
P(f"    (root, week) observations   {len(m):,}")
P(f"    weeks                       {m['monday'].nunique():,}   roots {m['root'].nunique()}")
P("")
P("--- ASSOCIATION between the FROZEN signal and the SUBSEQUENT weekly root return")
P("    (positive correlation = the frozen sign was right; negative = it was backwards)")
out = {}
for nm, col in (("S  (clipped, sector-demeaned)", "S"),
                ("RELZ (sector-demeaned ZVOL)", "RELZ"),
                ("ZVOL (raw, not demeaned)", "ZVOL")):
    x, y = m[col].values, m["fwd_sigma_units"].values
    r = float(np.corrcoef(x, y)[0, 1])
    # week-clustered standard error: the dependence unit is the WEEK, never the root-week
    byw = m.groupby("monday").apply(
        lambda g: np.corrcoef(g[col], g["fwd_sigma_units"])[0, 1] if len(g) > 2 else np.nan,
        include_groups=False)
    byw = byw[np.isfinite(byw)]
    se = float(byw.std(ddof=1) / np.sqrt(len(byw)))
    P(f"    {nm:<32} pooled r {r:+.5f}    week-mean r {float(byw.mean()):+.5f}  "
      f"+- {se:.5f} (SE over {len(byw)} weeks)   t {float(byw.mean())/se:+.2f}")
    out[col] = dict(pooled_r=r, week_mean_r=float(byw.mean()), week_se=se,
                    t=float(byw.mean()) / se, n_weeks=int(len(byw)))

P("")
P("--- MONOTONICITY: mean subsequent weekly root return by frozen-signal quintile")
P("    Q1 = most NEGATIVE S (HIGH participation, the SHORT leg)")
P("    Q5 = most POSITIVE S (LOW  participation, the LONG  leg -- the claimed premium)")
m["q"] = pd.qcut(m["S"], 5, labels=[1, 2, 3, 4, 5])
qt = m.groupby("q", observed=True).agg(n=("S", "size"), mean_S=("S", "mean"),
                                       mean_fwd=("fwd_sigma_units", "mean"),
                                       median_fwd=("fwd_sigma_units", "median"))
P(f"    {'Q':<4}{'n':>9}{'mean S':>10}{'mean fwd (sigma units)':>26}{'median':>12}")
for q, r_ in qt.iterrows():
    P(f"    {int(q):<4}{int(r_['n']):>9,}{r_['mean_S']:>10.3f}{r_['mean_fwd']:>26.5f}"
      f"{r_['median_fwd']:>12.5f}")
q5_q1 = float(qt.loc[5, "mean_fwd"] - qt.loc[1, "mean_fwd"])
P(f"    Q5 - Q1 = {q5_q1:+.5f} sigma units per week   "
  f"(the claimed premium requires this to be POSITIVE)")
out["q5_minus_q1_sigma_units"] = q5_q1
out["quintiles"] = {int(q): dict(n=int(r_["n"]), mean_S=float(r_["mean_S"]),
                                 mean_fwd=float(r_["mean_fwd"])) for q, r_ in qt.iterrows()}

P("")
P("--- COST-FREE COUNTERFACTUAL: what would the frozen object have earned with ZERO friction?")
P("    This is a DIAGNOSTIC of where the loss lives. It is NOT an alternative cost model and it")
P("    is NOT a gate. D1/D4 already failed on the real cost model.")
g = float(daily["pnl_gross"].sum())
c = float(daily["cost"].sum())
P(f"    GROSS (zero friction)   ${g:>14,.2f}   <-- already NEGATIVE before any cost")
P(f"    costs                   ${c:>14,.2f}")
P(f"    NET                     ${g-c:>14,.2f}")
out["gross"] = g
out["cost"] = c

P("")
P("=" * 112)
if out["S"]["pooled_r"] <= 0 and q5_q1 <= 0 and g <= 0:
    P("=== READING: the surface is EMPTY AS SPECIFIED, not merely expensive.")
    P("===   The frozen signal is not positively associated with the subsequent return, the")
    P("===   quintile spread has the WRONG SIGN, and gross P&L is negative BEFORE any friction.")
    P("===   Costs made a losing object lose more; they did not turn a winner into a loser.")
else:
    P("=== READING: mixed -- see the numbers above; no rescue is authorised either way.")
P("=" * 112)
P("    ⛔ This does NOT license a V2. SPEC 9 names what may not be tried after this failure, and")
P("       every item on that list stays forbidden. A genuinely different future volume hypothesis")
P("       would need a fresh EVI adjudication, a fresh preregistration, and an explicit statement")
P("       of the multiplicity debt this run has already incurred on these dates.")
json.dump(out, open(os.path.join(OUT, "vl_closure_diag.json"), "w", encoding="utf-8"),
          indent=2, default=str)
_fh.close()
