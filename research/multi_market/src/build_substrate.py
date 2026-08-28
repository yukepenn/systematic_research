"""CERTIFIED DEVELOPMENT SUBSTRATE - contract truth -> causal roll -> economic return series.

Reads ONLY the db/day .ncd store (TRUE unmerged contract data). The AddDataSeries path is barred
by TSMOM_DATA_CONTRACT.md.

ELIGIBILITY, declared here before any return is examined.
The coverage scan found something a single "common start date" cannot express: every CORE root
covers 94-99 % of business days over 2009-03-30 -> 2019-12, but with recurring holes at contract
transitions, up to 51-56 business days for YM, 6A and the grains. A global start rule is dominated
by the single worst hole and threw away a decade (it produced 2019-12-27, i.e. 3 usable days).

Real multi-market books do not work that way: markets ENTER and LEAVE the eligible universe. So:

    a root is ELIGIBLE on date t iff
      (a) it has a designated contract with a bar on t, and
      (b) at least MIN_RECENT_COVER of the previous LOOKBACK_COVER business days carried a bar,
          so the trend and volatility estimates are actually estimable rather than stale.

    WARMUP_DAYS of valid economic returns are required before a root may carry a position (s8).

Nothing here looks at P&L; eligibility is a function of data presence only.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ncd_day as N                                                        # noqa: E402
import roll as R                                                           # noqa: E402
from contract_truth import load_root                                       # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
os.makedirs(OUT, exist_ok=True)

# DECLARED BEFORE RESULTS
LOOKBACK_COVER = 260
MIN_RECENT_COVER = 200
WARMUP_DAYS = 252
DEV_START = "2009-03-30"      # measured store floor; the frozen 2009-01-01 moves for AVAILABILITY
DEV_END = "2018-12-31"        # frozen chronology, unchanged
# Contract EXPIRY years to load. Extended 2019 -> 2023 so the substrate spans the VALIDATION
# window as well. This is DATA COVERAGE ONLY: the economic-return construction, the roll engine
# and every eligibility rule are byte-identical. No strategy parameter changes.
Y0, Y1 = 2009, 2027
SEAL_CAP = "2026-08-01"   # HARD: no row at or beyond the global seal may enter this substrate


def main():
    all_ret, all_led, rows = [], [], []
    for root in N.CORE:
        d = load_root(root, Y0, Y1)
        if len(d) == 0:
            continue
        led = R.build_roll_ledger(d, root)
        held = R.designated_contract(d, led)
        er = R.economic_returns(d, held)
        if len(er) == 0:
            continue
        er["root"] = root
        er["sector"] = N.SECTOR[root]
        er["point_value"] = N.PV[root]
        er["ret_usd"] = er["ret_points"] * N.PV[root]      # ONE contract, unit economic return

        # ---- eligibility (data presence only)
        er = er[er["date"] < pd.Timestamp(SEAL_CAP)]
        if len(er) == 0:
            continue
        er = er.sort_values("date").reset_index(drop=True)
        days = pd.bdate_range(er["date"].min(), er["date"].max())
        present = pd.Series(0, index=days, dtype=float)
        present.loc[present.index.intersection(pd.DatetimeIndex(er["date"]))] = 1.0
        cover = present.rolling(LOOKBACK_COVER, min_periods=1).sum()
        elig = (cover >= MIN_RECENT_COVER) & (present > 0)
        er["eligible"] = elig.reindex(pd.DatetimeIndex(er["date"])).fillna(False).values
        er["obs_idx"] = np.arange(len(er))
        er.loc[er["obs_idx"] < WARMUP_DAYS, "eligible"] = False

        all_ret.append(er)
        all_led.append(led)
        nroll = int((led["reason"] == "VOLUME_CROSSOVER").sum())
        nforce = int((led["reason"] == "PRE_EXPIRY_OVERRIDE").sum())
        dev = er[(er["date"] >= DEV_START) & (er["date"] <= DEV_END)]
        rows.append(dict(root=root, sector=N.SECTOR[root], contracts=d["contract_id"].nunique(),
                         ret_days=len(er), dev_days=len(dev),
                         dev_eligible_days=int(dev["eligible"].sum()),
                         rolls_volume=nroll, rolls_forced=nforce,
                         first_elig=str(dev.loc[dev["eligible"], "date"].min())[:10]
                         if dev["eligible"].any() else "-",
                         med_abs_ret_usd=round(float(dev["ret_usd"].abs().median()), 2)))
        print(f"  {root:<4} contracts {d['contract_id'].nunique():>4}  ret days {len(er):>5}  "
              f"dev eligible {int(dev['eligible'].sum()):>5}  rolls {nroll:>3}v/{nforce:>3}f",
              flush=True)

    ret = pd.concat(all_ret, ignore_index=True)
    led = pd.concat(all_led, ignore_index=True)
    ret.to_parquet(os.path.join(OUT, "economic_returns.parquet"), index=False)
    led.to_csv(os.path.join(OUT, "ROLL_LEDGER.csv"), index=False)
    summ = pd.DataFrame(rows)
    summ.to_csv(os.path.join(OUT, "substrate_summary.csv"), index=False)

    print()
    print("=" * 110)
    print("=== CERTIFIED DEVELOPMENT SUBSTRATE")
    print("=" * 110)
    print(summ.to_string(index=False))
    dev = ret[(ret["date"] >= DEV_START) & (ret["date"] <= DEV_END)]
    de = dev[dev["eligible"]]
    print()
    print(f"    DEVELOPMENT window      {DEV_START} -> {DEV_END}")
    print(f"    eligible root-days      {len(de):,}")
    print(f"    roots ever eligible     {de['root'].nunique()} of {len(N.CORE)}")
    print(f"    ROLL_LEDGER rows        {len(led):,}  "
          f"({int((led.reason=='VOLUME_CROSSOVER').sum())} volume, "
          f"{int((led.reason=='PRE_EXPIRY_OVERRIDE').sum())} pre-expiry override)")
    cnt = de.groupby("date")["root"].nunique()
    print(f"    eligible roots per day  median {cnt.median():.0f}  min {cnt.min()}  max {cnt.max()}")
    print()
    print("    sector breadth (median eligible roots per day):")
    for s, g in de.groupby("sector"):
        c = g.groupby("date")["root"].nunique()
        print(f"      {s:<14} median {c.median():>4.0f}   of {sum(1 for r in N.CORE if N.SECTOR[r]==s)} roots")

    # ---- CAUSALITY ASSERTION on the real ledger, not just the unit test
    bad = led.dropna(subset=["info_cutoff"])
    assert (pd.to_datetime(bad["info_cutoff"]) < pd.to_datetime(bad["decision_date"])).all(), \
        "ROLL LEDGER CAUSALITY VIOLATION: an info_cutoff is not strictly before its decision date"
    print()
    print("    ASSERTION PASSED: every roll decision's information cutoff is STRICTLY before its")
    print("    decision date, on all", len(bad), "volume-based rolls in the real ledger.")


if __name__ == "__main__":
    main()
