"""ensembles.py — the ONE place campaign ensemble numbers are produced.

Every reviewer of Wave 1c / Wave 2 had to reverse-engineer the conventions because no
driver script was committed. That is a reproducibility defect; this module fixes it.

Conventions, fixed by the 2026-08-07 red-team review and binding from here on:

  * Sharpe is computed on **ALL days of the union calendar**, never on ensemble-active
    days. The active-day basis inflates sparse cells badly (adaptive k=30 reads 1.290
    active vs 0.993 all-days).
  * The calendar is the **union of every family's traded dates**. The archived
    wave1c_table_daily.csv holds 1,285 dates; the union is 1,348. Joining a new family
    onto the archived matrix silently drops real P&L.
  * Ensembles are a strict fixed 1/N mean over members, flat days included as zero. No
    reweighting, ever.
  * Exposure figures are reported as daily signed tilt AND flagged as such; the
    "exposure-matched dollars" transform is convention-dependent (~15% optimistic vs a
    minute-level reconstruction) and must not be quoted as achievable dollars.
"""
from __future__ import annotations

import glob
import re

import numpy as np
import pandas as pd

from execledger import read_exec_ledger, daily_vector
from validation import sharpe, max_drawdown, psr

FAMILIES = {
    "fixed_plateau":  ("research/02_solar_refinements/wave1c/ledgers/w1c__tf3_*_sc_slip1_*.csv", r"_sm(\d+)_"),
    "fixed_wide":     ("research/05_open_axes/fixedwide/*.csv",                                   r"_sm(\d+)_"),
    "adaptive":       ("research/05_open_axes/h006/*.csv",                                        r"_vm(\d+)_"),
    "anchor_ccHL":    ("research/05_open_axes/h008/h008am2*.csv",                                 r"_sm(\d+)_"),
    "combo":          ("research/05_open_axes/combo/*.csv",                                       r"_vm(\d+)_"),
}


def load_family(pattern, key):
    out = {}
    for f in sorted(glob.glob(pattern)):
        t, _ = read_exec_ledger(f)
        if t.empty:
            continue
        out[int(re.search(key, f).group(1))] = daily_vector(t)
    return pd.DataFrame(out).sort_index(axis=1)


def union_calendar(frames):
    idx = None
    for d in frames:
        idx = d.index if idx is None else idx.union(d.index)
    return idx


def ensemble(frame, calendar):
    """Strict 1/N mean on the union calendar, flat days as zero."""
    return frame.reindex(calendar).fillna(0.0).mean(axis=1)


def summarise(series, label, n_members):
    yr = series.groupby(series.index.year).sum()
    return {
        "family": label, "members": n_members, "days": len(series),
        "net": float(series.sum()), "sharpe_all_days": sharpe(series),
        "max_dd": max_drawdown(series), "psr": psr(series),
        "worst_year": float(yr.min()), "positive_years": float((yr > 0).mean()),
    }


def paired_block_bootstrap(x, y, L=20, B=10000, seed=0):
    """Circular block bootstrap of the Sharpe DIFFERENCE, paired on dates."""
    rng = np.random.default_rng(seed)
    x, y = np.asarray(x, float), np.asarray(y, float)
    n = len(x)
    nb = int(np.ceil(n / L))
    d = np.empty(B)
    for b in range(B):
        st = rng.integers(0, n, nb)
        idx = np.concatenate([(np.arange(s, s + L) % n) for s in st])[:n]
        d[b] = sharpe(x[idx]) - sharpe(y[idx])
    return d


def absolute_edge_bootstrap(x, L=20, B=10000, seed=0):
    """P(Sharpe <= 0) for a single series — the ABSOLUTE edge, not a comparison."""
    rng = np.random.default_rng(seed)
    x = np.asarray(x, float)
    n = len(x)
    nb = int(np.ceil(n / L))
    s = np.empty(B)
    for b in range(B):
        st = rng.integers(0, n, nb)
        idx = np.concatenate([(np.arange(k, k + L) % n) for k in st])[:n]
        s[b] = sharpe(x[idx])
    return float((s <= 0).mean())


def build():
    fr = {k: load_family(p, r) for k, (p, r) in FAMILIES.items()}
    cal = union_calendar(fr.values())
    ens = {k: ensemble(v, cal) for k, v in fr.items()}
    # the FAIR fixed comparator: every fixed cell actually tested, not a chosen sub-range
    fixed_all = pd.concat([fr["fixed_plateau"], fr["fixed_wide"]], axis=1)
    ens["fixed_ALL_21"] = ensemble(fixed_all, cal)
    rows = [summarise(ens[k], k, fr[k].shape[1] if k in fr else fixed_all.shape[1])
            for k in list(fr) + ["fixed_ALL_21"]]
    return pd.DataFrame(rows), ens, cal


if __name__ == "__main__":
    tbl, ens, cal = build()
    pd.set_option("display.width", 220)
    print(f"union calendar: {len(cal)} sessions\n")
    print(tbl.round(3).to_string(index=False))

    a, f21, f8 = ens["adaptive"], ens["fixed_ALL_21"], ens["fixed_plateau"]
    print("\nabsolute edge, circular block bootstrap P(Sharpe <= 0):")
    for n, s in [("adaptive", a), ("fixed_ALL_21", f21), ("fixed_plateau", f8)]:
        print(f"  {n:16s} {absolute_edge_bootstrap(s.values):.4f}")

    print("\ncomparative edge, paired block bootstrap of dSharpe:")
    for n, comp in [("vs fixed_ALL_21 (fair)", f21), ("vs fixed_plateau (as published)", f8)]:
        d = paired_block_bootstrap(a.values, comp.values)
        print(f"  {n:34s} obs {sharpe(a.values)-sharpe(comp.values):+.3f}  P(d<=0) {(d<=0).mean():.3f}")
        m = a.index.year != 2025
        d2 = paired_block_bootstrap(a.values[m], comp.values[m])
        print(f"  {'':34s} ex-2025 obs {sharpe(a.values[m])-sharpe(comp.values[m]):+.3f}  "
              f"P(d<=0) {(d2<=0).mean():.3f}  nets: adaptive ${a[m].sum():,.0f} vs comp ${comp[m].sum():,.0f}")
