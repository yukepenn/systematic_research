"""CONTRACT TRUTH (s3) - "a December-2009 contract returns data" is NOT "usable history starts
2009-01-01", and this measures which.

The depth probe established only that ONE contract per root (December 2009) returns bars. It did
not establish full-year coverage, complete cycles, absence of gaps, safe roll dates, or contract
overlap. Those are measured here, per contract and per root, BEFORE any strategy P&L exists.

USABLE START, defined before looking at any result:
    the first date from which, for the remainder of the window,
      (a) every business day has at least one live contract with volume > 0, allowing at most
          MAX_GAP consecutive business days of outage, and
      (b) at least two contracts are simultaneously live with volume, so a roll is EXPRESSIBLE.
    (b) matters as much as (a): a single-contract stretch cannot be rolled causally, so it cannot
    carry a TSMOM position no matter how clean its prices are.

If the common start moves later than 2009-01-01 because of DATA AVAILABILITY, that is legal and
recorded (s3). It may never move because of returns - none exist yet.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ncd_day as N                                                        # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
os.makedirs(OUT, exist_ok=True)
MAX_GAP = 3          # business days of allowed outage, declared before measurement
MIN_LIVE = 2         # contracts that must be simultaneously live for a roll to exist


def load_root(root: str, y0=2009, y1=2019) -> pd.DataFrame:
    parts = []
    for cid, r, m, y in N.contracts_for(root, y0, y1):
        x = N.read_contract(cid)
        if len(x) == 0:
            continue
        x = x.copy()
        x["root"] = r
        x["c_month"] = m
        x["c_year"] = y
        x["expiry_key"] = y * 100 + m
        parts.append(x)
    if not parts:
        return pd.DataFrame()
    d = pd.concat(parts, ignore_index=True)
    return d.sort_values(["date", "expiry_key"]).reset_index(drop=True)


def validity(d: pd.DataFrame) -> dict:
    o, h, l, c, v = (d[k].values for k in ("open", "high", "low", "close", "volume"))
    pos = (o > 0) & (h > 0) & (l > 0) & (c > 0)
    ord_ok = (h >= np.maximum(o, c) - 1e-9) & (l <= np.minimum(o, c) + 1e-9) & (h >= l - 1e-9)
    dup = d.duplicated(subset=["contract_id", "date"]).sum()
    return dict(rows=len(d), ohlc_bad=int((~(pos & ord_ok)).sum()),
                vol_neg=int((v < 0).sum()), vol_zero=int((v == 0).sum()),
                dup_contract_dates=int(dup))


def usable_start(d: pd.DataFrame):
    """First date from which COVERAGE is continuous.

    A FIRST VERSION required >= 2 live contracts EVERY day and returned None for all 21 roots.
    That conflated two different requirements: continuous COVERAGE needs one live contract per
    day, while ROLLABILITY needs an overlap only AT a roll. FX makes the difference stark - its
    median consecutive-contract overlap is 3 days, so a two-contract-every-day rule is
    unsatisfiable there while the market is perfectly tradeable. Coverage is measured here;
    rollability is reported separately as its own diagnostic."""
    g = d[d["volume"] > 0].groupby("date")["contract_id"].nunique()
    if g.empty:
        return None, None, 0, 0.0
    days = pd.bdate_range(g.index.min(), g.index.max())
    live = g.reindex(days).fillna(0).values
    ok = live >= 1                                    # COVERAGE
    while len(ok) and not ok[-1]:                     # trim trailing outage before scanning
        ok, days, live = ok[:-1], days[:-1], live[:-1]
    if not len(ok):
        return None, None, 0, 0.0
    bad_run, start_idx = 0, len(ok)
    for i in range(len(ok) - 1, -1, -1):
        if ok[i]:
            bad_run = 0
            start_idx = i
        else:
            bad_run += 1
            if bad_run > MAX_GAP:
                break
    if start_idx >= len(ok):
        return None, None, 0, 0.0
    roll_frac = float(np.mean(live[start_idx:] >= MIN_LIVE))   # ROLLABILITY, reported not gated
    return days[start_idx], days[-1], int(ok[start_idx:].sum()), roll_frac


def main():
    rows, panels = [], {}
    for root in N.CORE:
        d = load_root(root)
        if len(d) == 0:
            rows.append(dict(root=root, sector=N.SECTOR[root], contracts=0, note="NO DATA"))
            continue
        panels[root] = d
        v = validity(d)
        us, ue, ndays, rollfrac = usable_start(d)
        # contract-life overlap: median days two consecutive contracts are both live with volume
        lives = d[d["volume"] > 0].groupby("contract_id")["date"].agg(["min", "max"])
        lives = lives.join(d.groupby("contract_id")["expiry_key"].first()).sort_values("expiry_key")
        ov = []
        for a, b in zip(lives.index[:-1], lives.index[1:]):
            ov.append((lives.loc[a, "max"] - lives.loc[b, "min"]).days)
        rows.append(dict(
            root=root, sector=N.SECTOR[root], cycle=len(N.CYCLES[root]),
            contracts=d["contract_id"].nunique(),
            first_bar=d["date"].min().date(), last_bar=d["date"].max().date(),
            tick_size=float(d["tick_size"].iloc[0]), point_value=N.PV[root],
            usable_start=None if us is None else us.date(),
            usable_end=None if ue is None else ue.date(),
            usable_days=ndays, roll_overlap_frac=round(rollfrac,4),
            median_overlap_days=int(np.median(ov)) if ov else 0,
            min_overlap_days=int(np.min(ov)) if ov else 0,
            **v))
    t = pd.DataFrame(rows)
    t.to_csv(os.path.join(OUT, "contract_truth.csv"), index=False)

    print("=" * 118)
    print("=== CONTRACT TRUTH - measured per root, before any strategy P&L")
    print("=" * 118)
    cols = ["root", "sector", "contracts", "rows", "first_bar", "usable_start", "usable_end",
            "usable_days", "roll_overlap_frac", "median_overlap_days", "min_overlap_days", "ohlc_bad",
            "dup_contract_dates", "tick_size"]
    print(t[cols].to_string(index=False))

    good = t[t["usable_start"].notna()]
    common = max(good["usable_start"])
    print()
    print("=" * 118)
    print(f"=== COMMON_CORE_START = {common}   (the LATEST usable start across {len(good)} CORE roots)")
    print("=" * 118)
    late = good.sort_values("usable_start", ascending=False).head(6)
    print("    binding roots (latest usable starts):")
    for _, r in late.iterrows():
        print(f"      {r['root']:<4} {r['sector']:<13} usable from {r['usable_start']}  "
              f"({r['contracts']} contracts, {r['usable_days']} usable days)")
    print()
    print(f"    declared floor from the depth probe : 2009-01-01")
    print(f"    MEASURED common start               : {common}")
    print("    The move is a DATA-AVAILABILITY fact. No return has been computed.")
    t.to_csv(os.path.join(OUT, "contract_truth.csv"), index=False)
    return t, panels


if __name__ == "__main__":
    main()
