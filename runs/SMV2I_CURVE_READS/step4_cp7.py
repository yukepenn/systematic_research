"""Seq 365 — C-P7 windfall pre-test. PURE EVENT STUDY, no policy built this run.

Event: trailing 5d PnL of DUAL6040 (reproduced champion curve) > +2.5 sigma, where sigma is
the EXPANDING std (ddof=1) of the trailing-5d-sum series using STRICTLY PRIOR observations
(through t-1; no contemporaneous inclusion), burn-in >= 365 calendar days from first session.
Threshold is zero-centered (+2.5 sigma above zero, literal spec reading; the r5 mean is small
relative to 2.5 sigma so a mean-centered variant is also reported for transparency).

Read: forward 5d and 10d mean daily PnL after events (days t+1..t+5 / t+1..t+10, full windows
only) vs unconditional base = mean daily PnL over all burn-in-eligible days.
Test: one-sided moving-block bootstrap (CI-type read: block 5, B=10000, seed 20260808) over the
event-level differences f_i - base; p = P_boot(mean >= 0). Base treated as fixed (estimated on
~1000 days; its s.e. is small vs the event-mean s.e. — method note in REPORT).
Verdict: if forward PnL is NOT below base at one-sided p < 0.10 on either horizon -> C-P7 DEAD.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
from smv2i_lib import OUT, SEED, repro_gate

res, DUAL, BM, SIG, vm, cal, champ = repro_gate()
assert res["gate_60_40_atol1e-6"]

x = champ.values
n = len(x)
r5 = pd.Series(x, index=cal).rolling(5).sum()

# expanding sigma of r5 through t-1 (strictly prior), ddof=1
sig = r5.expanding(min_periods=20).std(ddof=1).shift(1)
burn = (cal - cal[0]).days >= 365
elig = burn & sig.notna().values & r5.notna().values

event = elig & (r5.values > 2.5 * sig.values)
event_mc = elig & ((r5.values - r5.expanding(min_periods=20).mean().shift(1).values)
                   > 2.5 * sig.values)  # mean-centered variant (reported only)

base_days = elig
base_mean = x[base_days].mean()

rows = []
for t in np.where(event)[0]:
    fwd5 = x[t + 1:t + 6].mean() if t + 5 < n else np.nan
    fwd10 = x[t + 1:t + 11].mean() if t + 10 < n else np.nan
    rows.append({"sess": cal[t].date(), "r5": r5.values[t], "sigma": sig.values[t],
                 "z": r5.values[t] / sig.values[t], "fwd5_mean": fwd5, "fwd10_mean": fwd10})
ev = pd.DataFrame(rows)

# cluster count: events separated by > 5 trading days start a new cluster
tidx = np.where(event)[0]
n_clusters = int(1 + (np.diff(tidx) > 5).sum()) if len(tidx) else 0


def block_boot_p(diffs, block=5, B=10000, seed=SEED):
    """One-sided p = P_boot(mean(diffs*) >= 0), circular moving-block over the event sequence."""
    d = np.asarray(diffs, dtype=float)
    d = d[~np.isnan(d)]
    m = len(d)
    if m == 0:
        return np.nan, 0
    blk = min(block, m)
    rng = np.random.default_rng(seed)
    nb = int(np.ceil(m / blk))
    starts = rng.integers(0, m, size=(B, nb))
    idx = (starts[:, :, None] + np.arange(blk)[None, None, :]).reshape(B, -1)[:, :m] % m
    means = d[idx].mean(axis=1)
    return float((means >= 0).mean()), m

tests = {}
for h in (5, 10):
    f = ev[f"fwd{h}_mean"].values
    p, m = block_boot_p(f - base_mean)
    tests[f"fwd{h}"] = {"n_events_used": m, "fwd_mean": float(np.nanmean(f)),
                        "base_mean": base_mean, "diff": float(np.nanmean(f) - base_mean),
                        "p_one_sided_below": p}

verdict = "DEAD" if all(np.isnan(tests[k]["p_one_sided_below"])
                        or tests[k]["p_one_sided_below"] >= 0.10 for k in tests) else "QUALIFIES"

# DIAGNOSTIC ONLY (not the spec verdict): de-clustered read, first event of each cluster
first_of_cluster = np.zeros(len(tidx), dtype=bool)
if len(tidx):
    first_of_cluster[0] = True
    first_of_cluster[1:] = np.diff(tidx) > 5
declu = {}
for h in (5, 10):
    f = ev[f"fwd{h}_mean"].values[first_of_cluster]
    p, m = block_boot_p(f - base_mean)
    declu[f"declustered_fwd{h}_p_below"] = p
    declu[f"declustered_fwd{h}_mean"] = float(np.nanmean(f))
    declu[f"declustered_fwd{h}_n"] = m

summ = pd.DataFrame([{
    "n_events": int(event.sum()), "n_clusters": n_clusters,
    "n_events_meancentered_variant": int(event_mc.sum()),
    "n_base_days": int(base_days.sum()), "base_mean_daily": base_mean,
    "fwd5_mean": tests["fwd5"]["fwd_mean"], "fwd5_diff": tests["fwd5"]["diff"],
    "fwd5_p_below": tests["fwd5"]["p_one_sided_below"], "fwd5_n": tests["fwd5"]["n_events_used"],
    "fwd10_mean": tests["fwd10"]["fwd_mean"], "fwd10_diff": tests["fwd10"]["diff"],
    "fwd10_p_below": tests["fwd10"]["p_one_sided_below"], "fwd10_n": tests["fwd10"]["n_events_used"],
    "verdict": verdict, **declu,
}])

ev.to_csv(os.path.join(OUT, "c_p7_events.csv"), index=False)
summ.to_csv(os.path.join(OUT, "c_p7_summary.csv"), index=False)
print(ev.to_string())
print()
print(summ.T.to_string())
