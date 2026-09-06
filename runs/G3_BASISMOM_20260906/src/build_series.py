"""G3_BASISMOM_20260906 -- STEP 0: FRONT-nearby and SECOND-nearby causal continuous series.

Universe {CL, GC, SI, ZN, ZB}, per-contract daily .ncd via the CERTIFIED transport
research/multi_market/src/ncd_day.py and the CERTIFIED causal roll research/multi_market/src/roll.py
(volume-crossover from t-1 information, 5-day pre-expiry buffer, one-way). No new roll is invented:

  FRONT  leg: build_roll_ledger -> designated_contract -> economic_returns   (verbatim, as in
              runs/G3_EVENT_GC_20260906/src/build_daily_inputs.py).
  SECOND leg: the DEFERRED-LEG CONVENTION of runs/CARRY_V1_20260828/src/carry_v1.py, verbatim:
              on each date d, the deferred contract is the NEAREST LATER LISTED MONTH (month_gap
              > 0) relative to the causal front contract, among contracts with a bar on d.
              Its continuous return uses the SAME certified self-financing economic_returns
              (overnight on old, intraday on target; two contracts are NEVER differenced), fed
              with the deferred-leg step function instead of the front one.

POINT BASIS throughout (DELEV01): daily returns are price POINTS; the only price-level arithmetic
is the static slope (P_front - P_second)/month_gap, a DIFFERENCE, defined for negative prices.

SEAL: every session >= 2026-08-01 hard-dropped at load; asserted per root.
Writes ONLY inside runs/G3_BASISMOM_20260906/out/.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
MM = os.path.join(ROOT, "research", "multi_market", "src")
sys.path.insert(0, MM)
import ncd_day as N            # noqa: E402
import roll as R               # noqa: E402
from contract_truth import load_root, validity  # noqa: E402

OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
SEAL = pd.Timestamp("2026-08-01")
Y0, Y1 = 2009, 2027
UNIVERSE = ["CL", "GC", "SI", "ZN", "ZB"]

_fh = open(os.path.join(OUT, "build_log.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def month_gap(a, b):
    return (b[1] - a[1]) * 12 + (b[0] - a[0])


def build_root(root):
    d = load_root(root, Y0, Y1)
    pre_rows, pre_max = len(d), d["date"].max()
    d = d[d["date"] < SEAL].reset_index(drop=True)
    assert d["date"].max() < SEAL, f"SEAL VIOLATION {root}"
    v = validity(d)

    led = R.build_roll_ledger(d[["date", "contract_id", "expiry_key", "open", "high",
                                 "low", "close", "volume"]].copy(), root)
    held = R.designated_contract(d, led)
    er_f = R.economic_returns(d, held).set_index("date")
    b = led.dropna(subset=["info_cutoff"])
    causal_ok = bool((pd.to_datetime(b["info_cutoff"]) < pd.to_datetime(b["decision_date"])).all())
    assert causal_ok, f"roll causality FAILED {root}"

    # ---- deferred leg, carry_v1 convention verbatim -------------------------------------
    meta = d.groupby("contract_id").agg(cmonth=("c_month", "first"), cyear=("c_year", "first"))
    bydate = {pd.Timestamp(dd): set(g) for dd, g in d.groupby("date")["contract_id"]}
    closes = d.set_index(["date", "contract_id"])["close"]
    dates = [pd.Timestamp(x) for x in np.sort(d["date"].unique())]

    recs, h2 = [], {}
    for dd in dates:
        a = held.get(dd)
        if not isinstance(a, str):
            continue
        ka = (int(meta.at[a, "cmonth"]), int(meta.at[a, "cyear"]))
        later = [(c, month_gap(ka, (int(meta.at[c, "cmonth"]), int(meta.at[c, "cyear"]))))
                 for c in bydate.get(dd, set()) if c != a]
        later = [(c, g) for c, g in later if g > 0]
        if not later:
            continue
        defer, gap = min(later, key=lambda x: x[1])          # nearest later LISTED MONTH
        h2[dd] = defer
        try:
            pf, ps = float(closes.loc[(dd, a)]), float(closes.loc[(dd, defer)])
        except KeyError:
            pf, ps = np.nan, np.nan
        recs.append(dict(date=dd, front=a, second=defer, gap=gap,
                         close_front=pf, close_second=ps,
                         slope=(pf - ps) / gap if np.isfinite(pf) and np.isfinite(ps) else np.nan))

    held2 = pd.Series(h2).reindex(held.index)
    both = held2.dropna().index
    n_same = int((held2.loc[both] == held.loc[both]).sum())
    assert n_same == 0, f"second leg equals front leg on {n_same} dates ({root})"

    er_s = R.economic_returns(d, held2).set_index("date")

    x = pd.DataFrame(recs).set_index("date").sort_index()
    x["ret_f"] = er_f["ret_points"].reindex(x.index)
    x["rolled_f"] = er_f["rolled"].reindex(x.index)
    x["ret_s"] = er_s["ret_points"].reindex(x.index)
    x["rolled_s"] = er_s["rolled"].reindex(x.index)
    n_raw = len(x)
    x = x.dropna(subset=["ret_f", "ret_s"])
    x["cal_gap_days"] = x.index.to_series().diff().dt.days

    info = dict(root=root, pre_rows=int(pre_rows), pre_max=str(pre_max.date()),
                rows=int(len(x)), span=[str(x.index.min().date()), str(x.index.max().date())],
                contracts=int(d["contract_id"].nunique()),
                dropped_joint_days=int(n_raw - len(x)),
                min_gap_mo=int(x["gap"].min()), median_gap_mo=float(x["gap"].median()),
                rolls_front=int(x["rolled_f"].sum()), rolls_second=int(x["rolled_s"].sum()),
                seal_max=str(d["date"].max().date()), roll_causal=causal_ok,
                second_distinct_violations=n_same,
                ledger=dict(vol=int((led.reason == "VOLUME_CROSSOVER").sum()),
                            pre_expiry=int((led.reason == "PRE_EXPIRY_OVERRIDE").sum()),
                            init=int((led.reason == "INITIALISE").sum())),
                validity=v)
    return x, info


def main():
    P("=" * 110)
    P("=== G3_BASISMOM_20260906  STEP 0: front-nearby + second-nearby causal continuous series")
    P("=" * 110)
    R.test_no_roll_telescopes(verbose=False)
    R.test_basis_invariance(verbose=False)
    R.test_roll_causality(verbose=False)
    P("    roll.py certified unit tests: telescoping / basis-invariance / causality  ALL PASS")
    P("")

    manifest = {"seal": str(SEAL.date()), "roots": {}}
    for root in UNIVERSE:
        x, info = build_root(root)
        pq = os.path.join(OUT, f"legs_{root}.parquet")
        x.reset_index().to_parquet(pq, index=False)
        info["parquet_sha256"] = sha256_file(pq)
        manifest["roots"][root] = info
        P(f"    {root:<3} rows {info['rows']:>6,}  {info['span'][0]} -> {info['span'][1]}  "
          f"contracts {info['contracts']:>3}  gap(mo) min/med {info['min_gap_mo']}/"
          f"{info['median_gap_mo']:.0f}  rolls f/s {info['rolls_front']}/{info['rolls_second']}  "
          f"seal<{SEAL.date()} PASS  causal PASS  second!=front PASS  "
          f"(dropped joint days {info['dropped_joint_days']})")

    json.dump(manifest, open(os.path.join(OUT, "build_manifest.json"), "w", encoding="utf-8"),
              indent=2, default=str)
    P("")
    P("    wrote out/legs_<ROOT>.parquet x5 + out/build_manifest.json")
    P("=" * 110)
    _fh.close()


if __name__ == "__main__":
    main()
