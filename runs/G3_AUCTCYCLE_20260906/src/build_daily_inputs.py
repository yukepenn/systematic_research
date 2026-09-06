"""G3_AUCTCYCLE_20260906 -- STEP 2: build ZN, ZB (primary) and ES (specificity control) daily
continuous series from the per-contract NT8 day .ncd store, EXACTLY the certified way:
same reader research/multi_market/src/ncd_day.py, same causal volume-crossover roll
research/multi_market/src/roll.py, same self-financing return + identity gate, same seal assert
(verbatim extract() from runs/G3_EVENT_GC_20260906/src/build_daily_inputs.py).

SEAL: every session >= 2026-08-01 hard-dropped; asserted. Writes ONLY inside this run dir.
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
CLEAN_GAP_MAX = 5

_fh = open(os.path.join(OUT, "build_inputs_log.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# --------------- verbatim from runs/G3_EVENT_GC_20260906/src/build_daily_inputs.py -------------
def build_returns(panel, held):
    """Self-financing point return (identical to roll.economic_returns) PLUS the capital base
    old_close_prev. Never differences two contracts."""
    o = panel.pivot_table(index="date", columns="contract_id", values="open").sort_index()
    c = panel.pivot_table(index="date", columns="contract_id", values="close").sort_index()
    h = panel.pivot_table(index="date", columns="contract_id", values="high").sort_index()
    lo = panel.pivot_table(index="date", columns="contract_id", values="low").sort_index()
    vol = panel.pivot_table(index="date", columns="contract_id", values="volume").sort_index()
    dates = held.index
    rows = []
    for i in range(1, len(dates)):
        d, dp = dates[i], dates[i - 1]
        tgt, old = held.get(d), held.get(dp)
        if not isinstance(tgt, str) or not isinstance(old, str):
            continue
        try:
            old_c_prev, old_o = c.at[dp, old], o.at[d, old]
            tgt_o, tgt_c = o.at[d, tgt], c.at[d, tgt]
            tgt_h, tgt_l, tgt_v = h.at[d, tgt], lo.at[d, tgt], vol.at[d, tgt]
        except KeyError:
            continue
        if any(pd.isna(x) for x in (old_c_prev, old_o, tgt_o, tgt_c)):
            continue
        overnight = old_o - old_c_prev
        intraday = tgt_c - tgt_o
        rows.append(dict(date=d, held_contract=tgt, old_contract=old,
                         open=tgt_o, high=tgt_h, low=tgt_l, close=tgt_c, volume=int(tgt_v),
                         old_close_prev=old_c_prev,
                         overnight_pts=overnight, intraday_pts=intraday,
                         ret_points=overnight + intraday, rolled=int(old != tgt)))
    df = pd.DataFrame(rows)
    df["cal_gap_days"] = df["date"].diff().dt.days
    df["clean_daily"] = df["cal_gap_days"].fillna(1) <= CLEAN_GAP_MAX
    return df


def extract(root):
    d = load_root(root, Y0, Y1)
    pre_rows, pre_max = len(d), d["date"].max()
    d = d[d["date"] < SEAL].reset_index(drop=True)
    assert d["date"].max() < SEAL, "SEAL VIOLATION"
    led = R.build_roll_ledger(d, root)
    held = R.designated_contract(d, led)
    df = build_returns(d, held)
    er = R.economic_returns(d, held)
    m = df.merge(er[["date", "ret_points"]], on="date", suffixes=("", "_oracle"))
    maxerr = float(np.max(np.abs(m["ret_points"] - m["ret_points_oracle"])))
    assert maxerr < 1e-9, f"identity gate FAILED: {maxerr}"
    b = led.dropna(subset=["info_cutoff"])
    causal_ok = bool((pd.to_datetime(b["info_cutoff"]) < pd.to_datetime(b["decision_date"])).all())
    assert causal_ok, "roll causality FAILED"
    return d, led, df, pre_rows, pre_max, maxerr, causal_ok
# ------------------------------------------------------------------------------------------------


def main():
    P("=" * 100)
    P("=== G3_AUCTCYCLE_20260906  STEP 2: ZN / ZB / ES daily via CERTIFIED causal roll")
    P("=" * 100)
    R.test_no_roll_telescopes(verbose=False)
    R.test_basis_invariance(verbose=False)
    R.test_roll_causality(verbose=False)
    P("    roll.py causal-roll unit tests: telescoping / basis-invariance / causality  ALL PASS")

    manifest = {"seal": str(SEAL.date()), "roll_unit_tests": "ALL PASS"}
    for root in ("ZN", "ZB", "ES"):
        P("")
        P(f"--- {root} DAILY (per-contract day .ncd -> causal roll)")
        d, led, df, pre_rows, pre_max, idgate, causal_ok = extract(root)
        v = validity(d)
        tick = float(d["tick_size"].iloc[0])
        pq = os.path.join(OUT, f"{root.lower()}_daily.parquet")
        df.to_parquet(pq, index=False)
        P(f"    raw panel        {pre_rows:,} contract-days, raw max {pre_max.date()}")
        P(f"    SEAL             dropped >= {SEAL.date()}; retained max {d['date'].max().date()}  "
          f"assert PASS")
        P(f"    panel            {len(d):,} contract-days, {d['contract_id'].nunique()} contracts, "
          f"{d['date'].min().date()} -> {d['date'].max().date()}  tick_size={tick}")
        P(f"    validity         ohlc_bad={v['ohlc_bad']} vol_zero={v['vol_zero']} "
          f"dup={v['dup_contract_dates']}")
        P(f"    roll ledger      {len(led)} rows "
          f"({int((led.reason == 'VOLUME_CROSSOVER').sum())} vol-crossover, "
          f"{int((led.reason == 'PRE_EXPIRY_OVERRIDE').sum())} pre-expiry, "
          f"{int((led.reason == 'INITIALISE').sum())} init); causality PASS")
        P(f"    identity gate    ret_points == roll.economic_returns max err {idgate:.2e}  PASS")
        P(f"    return-days      {len(df):,}  {df['date'].min().date()} -> "
          f"{df['date'].max().date()}  "
          f"({int((~df['clean_daily']).sum())} gap-spanning flagged clean_daily=False)")
        P(f"    WROTE            {pq}")
        manifest[root] = dict(
            rows=int(len(df)),
            span=[str(df["date"].min().date()), str(df["date"].max().date())],
            contracts=int(d["contract_id"].nunique()), tick_size=tick,
            identity_gate_maxerr=idgate, roll_causal=causal_ok,
            seal_max=str(d["date"].max().date()), parquet_sha256=sha256_file(pq),
            roll_ledger=dict(volume=int((led.reason == "VOLUME_CROSSOVER").sum()),
                             pre_expiry=int((led.reason == "PRE_EXPIRY_OVERRIDE").sum()),
                             init=int((led.reason == "INITIALISE").sum())))

    json.dump(manifest, open(os.path.join(OUT, "inputs_manifest.json"), "w", encoding="utf-8"),
              indent=2, default=str)
    P("")
    P("    wrote out/inputs_manifest.json")
    P("=" * 100)
    _fh.close()


if __name__ == "__main__":
    main()
