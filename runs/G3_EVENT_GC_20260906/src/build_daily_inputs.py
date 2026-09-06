"""G3_EVENT_GC_20260906 -- STEP 0: build the two auxiliary daily inputs.

(1) SI daily continuous series from the per-contract NT8 day .ncd store, EXACTLY the way the GC
    autopsy built gc_daily.parquet (same reader research/multi_market/src/ncd_day.py, same causal
    volume-crossover roll research/multi_market/src/roll.py, same self-financing return + identity
    gate, same seal assert).  -> out/si_daily.parquet
(2) NQ daily point-return series aggregated from the DEEP SPINE
    research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet (1-min, END-stamped,
    exchange-session ET, additively back-adjusted).  DELEV01: POINT differences ONLY -- no %
    returns, no level thresholds, ever, on this series.  -> out/nq_daily_spine.parquet
    Plus an ALIGNMENT check series: NQ daily built from the day store (same as GC autopsy's
    extract("NQ")) to verify the spine session-dating matches the day-store dating at lag 0.

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
SPINE = os.path.join(ROOT, "research", "scalping_lab", "substrate", "minute", "NQ",
                     "nq1m_2005_202605.parquet")

_fh = open(os.path.join(OUT, "build_inputs_log.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# ---------------------------------------------------------------- SI: identical to GC autopsy
def build_returns(panel, held):
    """Self-financing point return (identical to roll.economic_returns) PLUS the capital base
    old_close_prev so a basis-free PERCENT return can be formed. Never differences two contracts.
    (Verbatim logic from runs/DAILY_GC_EXTRACT_AUTOPSY_20260906/src/gc_extract_autopsy.py.)"""
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
    df["ret_pct"] = df["ret_points"] / df["old_close_prev"]
    df["overnight_pct"] = df["overnight_pts"] / df["old_close_prev"]
    df["intraday_pct"] = df["intraday_pts"] / df["old_close_prev"]
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


def main():
    P("=" * 100)
    P("=== G3_EVENT_GC_20260906  STEP 0: build SI daily (day store) + NQ daily (deep spine)")
    P("=" * 100)
    R.test_no_roll_telescopes(verbose=False)
    R.test_basis_invariance(verbose=False)
    R.test_roll_causality(verbose=False)
    P("    roll.py causal-roll unit tests: telescoping / basis-invariance / causality  ALL PASS")

    # ---------------- SI from day store (E5 input)
    P("")
    P("--- SI DAILY (per-contract day .ncd -> causal roll), method identical to GC autopsy")
    si_status = {}
    try:
        d, led, si, pre_rows, pre_max, idgate, causal_ok = extract("SI")
        v = validity(d)
        r = si["ret_pct"].fillna(0.0).values
        growth = np.cumprod(1.0 + r)
        last_true_close = float(si["close"].iloc[-1])
        si["close_radj"] = last_true_close * growth / growth[-1]
        pq = os.path.join(OUT, "si_daily.parquet")
        si.to_parquet(pq, index=False)
        P(f"    raw panel        {pre_rows:,} contract-days, raw max {pre_max.date()}")
        P(f"    SEAL             dropped >= {SEAL.date()}; retained max {d['date'].max().date()}  "
          f"assert PASS")
        P(f"    panel            {len(d):,} contract-days, {d['contract_id'].nunique()} contracts, "
          f"{d['date'].min().date()} -> {d['date'].max().date()}")
        P(f"    validity         ohlc_bad={v['ohlc_bad']} vol_zero={v['vol_zero']} "
          f"dup={v['dup_contract_dates']}")
        P(f"    roll ledger      {len(led)} rows "
          f"({int((led.reason == 'VOLUME_CROSSOVER').sum())} vol-crossover, "
          f"{int((led.reason == 'PRE_EXPIRY_OVERRIDE').sum())} pre-expiry, "
          f"{int((led.reason == 'INITIALISE').sum())} init); causality PASS")
        P(f"    identity gate    ret_points == roll.economic_returns max err {idgate:.2e}  PASS")
        P(f"    return-days      {len(si):,}  {si['date'].min().date()} -> {si['date'].max().date()}"
          f"  ({int((~si['clean_daily']).sum())} gap-spanning flagged clean_daily=False)")
        P(f"    WROTE            {pq}")
        si_status = dict(runnable=True, rows=int(len(si)),
                         span=[str(si["date"].min().date()), str(si["date"].max().date())],
                         contracts=int(d["contract_id"].nunique()),
                         identity_gate_maxerr=idgate, roll_causal=causal_ok,
                         seal_max=str(d["date"].max().date()),
                         parquet_sha256=sha256_file(pq),
                         roll_ledger=dict(volume=int((led.reason == "VOLUME_CROSSOVER").sum()),
                                          pre_expiry=int((led.reason == "PRE_EXPIRY_OVERRIDE").sum()),
                                          init=int((led.reason == "INITIALISE").sum())))
    except Exception as e:  # honest failure -> E5 NOT-RUNNABLE
        P(f"    *** SI BUILD FAILED: {type(e).__name__}: {e}")
        si_status = dict(runnable=False, error=f"{type(e).__name__}: {e}")

    # ---------------- NQ daily point returns from the DEEP SPINE
    P("")
    P("--- NQ DAILY from deep spine (1-min, additively back-adjusted -> POINT DIFFERENCES ONLY)")
    sp = pd.read_parquet(SPINE)
    ts = pd.to_datetime(sp["time"])
    P(f"    spine            {len(sp):,} 1-min rows  {ts.min()} -> {ts.max()}")
    # END-stamped, exchange-session ET (18:00 -> 17:00). Bar stamped strictly after 18:00 belongs
    # to the NEXT calendar day's session; stamps <= 18:00 belong to the same calendar day session.
    mins = ts.dt.hour * 60 + ts.dt.minute
    session = ts.dt.normalize() + pd.to_timedelta((mins > 18 * 60).astype(int), unit="D")
    sp = sp.assign(session=session).sort_values(["session", "time"])
    daily = sp.groupby("session").agg(close_adj=("close", "last"), n_bars=("close", "size"))
    daily = daily.reset_index().rename(columns={"session": "date"})
    daily = daily[daily["date"] < SEAL].reset_index(drop=True)
    assert daily["date"].max() < SEAL, "SEAL VIOLATION (NQ spine)"
    daily["ret_pts"] = daily["close_adj"].diff()             # POINT differences only (DELEV01)
    daily["cal_gap_days"] = daily["date"].diff().dt.days
    daily["clean_daily"] = daily["cal_gap_days"].fillna(1) <= CLEAN_GAP_MAX
    daily.loc[~daily["clean_daily"], "ret_pts"] = np.nan
    pqn = os.path.join(OUT, "nq_daily_spine.parquet")
    daily.to_parquet(pqn, index=False)
    P(f"    sessions         {len(daily):,}  {daily['date'].min().date()} -> "
      f"{daily['date'].max().date()}  (seal assert PASS)")
    P(f"    point returns    valid {int(daily['ret_pts'].notna().sum()):,} "
      f"({int((~daily['clean_daily']).sum())} gap-spanning nulled)")
    P(f"    WROTE            {pqn}")

    # ---------------- ALIGNMENT GATE: spine session dating vs day-store dating (phase check)
    P("")
    P("--- ALIGNMENT GATE  (spine NQ session returns vs day-store NQ causal-roll returns)")
    _, _, nqday, _, _, _, _ = extract("NQ")
    j = daily[["date", "ret_pts"]].merge(
        nqday[nqday["clean_daily"]][["date", "ret_points"]], on="date", how="inner").dropna()
    lags = {}
    a = daily.set_index("date")["ret_pts"]
    b = nqday[nqday["clean_daily"]].set_index("date")["ret_points"]
    for lag in (-1, 0, 1):
        bb = b.copy()
        bb.index = bb.index + pd.tseries.offsets.BDay(lag) if lag else bb.index
        jj = pd.concat([a, bb], axis=1, join="inner").dropna()
        lags[lag] = float(jj.iloc[:, 0].corr(jj.iloc[:, 1])) if len(jj) > 100 else np.nan
    P(f"    corr(spine, day-store) by lag (BDay): -1: {lags[-1]:+.3f}   0: {lags[0]:+.3f}   "
      f"+1: {lags[1]:+.3f}   shared dates lag0 n={len(j):,}")
    align_ok = lags[0] > 0.95 and lags[0] > max(abs(lags[-1]), abs(lags[1])) + 0.3
    P(f"    ALIGNMENT: {'PASS' if align_ok else '*** FAIL — session-dating phase error ***'}")

    manifest = dict(
        si=si_status,
        nq_spine=dict(source=os.path.relpath(SPINE, ROOT), sessions=int(len(daily)),
                      span=[str(daily["date"].min().date()), str(daily["date"].max().date())],
                      seal_max=str(daily["date"].max().date()),
                      basis="ADDITIVELY BACK-ADJUSTED -> POINT DIFFERENCES ONLY (DELEV01)",
                      parquet_sha256=sha256_file(pqn)),
        alignment=dict(corr_by_lag={str(k): v for k, v in lags.items()}, ok=bool(align_ok),
                       shared_dates=int(len(j))),
        seal=str(SEAL.date()),
    )
    json.dump(manifest, open(os.path.join(OUT, "inputs_manifest.json"), "w", encoding="utf-8"),
              indent=2, default=str)
    P("")
    P(f"    wrote out/inputs_manifest.json")
    P("=" * 100)
    _fh.close()


if __name__ == "__main__":
    main()
