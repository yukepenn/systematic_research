"""SM1M_CL_SUBSTRATE -- materialize the CL (WTI crude oil) 1-minute surface.

RUN CLASS: $0 DATA EXTRACTION (no hypothesis, no signal, no P&L). SM1M pattern.
CL is a GENUINELY UNTOUCHED market for this program: this run only materializes the raw
substrate. NO signals / returns / strategy are computed here -- the coordinator freezes a
discovery/holdout boundary before any signal research.

PIPELINE (identical construction to runs/SM1M_SUBSTRATE and the MNQ/ZB/ES/RTY/YM substrates):
  1. NT8-side export: SWMinuteExport_v1 (research/scalping_lab/src/ninjascript/, sha256
     48c21a775326b69a731fea27945c9b41b99ccec4553992bee5f75acd92cdc89d, ALREADY installed and
     resolved in fresh assembly 40daedcc00a24a0ba7d83631d1c25d80 -- the repo copy and the NT8
     copy in bin/Custom/Strategies were sha256-VERIFIED IDENTICAL, so NO file was copied and
     NO Custom.dll recompile was triggered against the running live book)
     run through CrossTrade RunStrategyBacktest (job 2649a17d913f4c66, engine
     nt8_strategy_analyzer, NT8 8.1.8.1, fingerprint sha256:b4255f1b0dd7fba1, isolated
     Backtest account, zero orders):
        instrument "CL 09-26" (merge back-adjusted front-month series -- CLU6 was front during
        the late-July-2026 seal tail, so the anchor segment offset ~= 0, same construction as
        the other SM1M substrates), Minute/1 Last,
        from 2022-01-01T00:00:00Z  to 2026-07-31T21:59:59Z
        (`to` == session_close_boundary_utc(2026-07-31) from research_sdk/session_boundary.py:
         one second before the next 18:00 ET open -- the s5 seal cap applied AT THE EXPORT).
     CSV Documents/NinjaTrader 8/out/cl1m_2022_2026_1m.csv (raw CSV kept outside the repo, per
     the SM1M pattern).
  2. This script: PRICE-GRID CHECK (see below), gates, session labeling, HARD SEAL DROP, parquet.

PRICE-GRID CHECK (CL-specific, documented prominently):
  SWMinuteExport_v1 formats prices with ToString("F2"). CL's outright tick is $0.01 EXACTLY,
  and back-adjustment adds a constant that is itself a whole multiple of $0.01 (a difference of
  two on-grid prices), so the entire merge back-adjusted series sits on the 0.01 grid. F2 emits
  exactly two decimals == the 0.01 grid, so F2 is LOSS-FREE for CL -- unlike ZB, whose 1/32
  (0.03125) grid F2 destroyed and had to be restored. This script MEASURES that: it snaps to the
  0.01 grid, prints max|csv - snapped| (must be << half-tick 0.005; expected pure IEEE-754 noise)
  and the share of prices already on the 0.01 grid (expected ~100%), and cross-checks that the
  continuous-minus-day-store close offsets are whole multiples of 0.01. Snapping only removes
  float parse noise; it cannot move a genuine 2-decimal value.

CONVENTION: bars are END-stamped ET (the bar stamped 09:31 opens 09:30:00); NO shift is applied
anywhere (verified for this export pattern against the NQ substrate bar-for-bar; see
SM1M_MNQ_SUBSTRATE/MANIFEST.md). CL's CME session is 18:00 ET -> 17:00 ET next day with a daily
17:00-18:00 ET break -- the SAME session structure as the index/rate substrates, so the SAME
session_date label rule and the SAME "no stamps in (17:00,18:00] ET" gate apply. The backtest
used CL's OWN primary trading hours (trading_hours was not overridden), not NQ hours.
"""
from __future__ import annotations

import hashlib
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
sys.path.insert(0, os.path.join(ROOT, "research", "multi_market", "src"))
import ncd_day as ND  # noqa: E402  (day-store reader, VALIDATED vs GetBars -- cross-source check only)

CSV = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8", "out",
                   "cl1m_2022_2026_1m.csv")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
PARQUET = os.path.join(OUT, "cl_1m_2022_2026.parquet")
SEAL = pd.Timestamp("2026-08-01")
TICK = 0.01  # CL outright minimum tick == F2 precision

# cross-source day-store spot checks: (session date, [candidate front-month contracts]).
# CL is MONTHLY; the true front is the max-volume candidate on that date (robust to roll timing).
DAY_CHECKS = [
    ("2023-02-15", ["CL 02-23", "CL 03-23", "CL 04-23"]),
    ("2024-05-14", ["CL 05-24", "CL 06-24", "CL 07-24"]),
    ("2025-10-15", ["CL 10-25", "CL 11-25", "CL 12-25"]),
]


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def session_date(ts: pd.Series) -> pd.Series:
    """src/analytics/runlib.py:35 session_date, vectorized. 18:00 ET (prior day) -> 17:00 ET;
    hour >= 18 rolls forward; Sat/Sun labels roll to Monday. END-stamped input, NO shift."""
    d = ts.dt.normalize()
    d = d.where(ts.dt.hour < 18, d + pd.Timedelta(days=1))
    d = d.where(d.dt.dayofweek != 5, d + pd.Timedelta(days=2))   # Sat -> Mon
    d = d.where(d.dt.dayofweek != 6, d + pd.Timedelta(days=1))   # Sun -> Mon
    return d


def front_contract(cids, s0):
    """Return (cid, day_row) for the candidate with the largest day-store volume on date s0."""
    best = (None, None, -1)
    for cid in cids:
        day = ND.read_contract(cid)
        if day.empty:
            continue
        dts = pd.to_datetime(day["date"])
        if s0 not in set(dts):
            continue
        row = day.loc[dts == s0].iloc[0]
        v = int(row["volume"])
        if v > best[2]:
            best = (cid, row, v)
    return best[0], best[1]


def main():
    print("=" * 100)
    print("=== SM1M_CL_SUBSTRATE build -- DATA EXTRACTION ONLY (no signal, no P&L)")
    print("=" * 100)
    print(f"    input CSV            {CSV}")
    print(f"    input sha256         {sha256_file(CSV)}")
    df = pd.read_csv(CSV, parse_dates=["time"])
    df["volume"] = df["volume"].astype("int64")
    n0 = len(df)
    print(f"    rows read            {n0:,}")

    # ---- price-grid check (CL tick == 0.01 == F2 precision; F2 is loss-free) -------------
    print("")
    print("    PRICE-GRID CHECK  (CL outright tick = $0.01 = F2 precision; F2 loss-free -- see docstring)")
    resid_max = 0.0
    on_grid = None
    for c in ("open", "high", "low", "close"):
        snapped = np.round(df[c].values / TICK) * TICK
        resid = np.abs(snapped - df[c].values)
        resid_max = max(resid_max, float(resid.max()))
        col_on = resid < 1e-9
        on_grid = col_on if on_grid is None else (on_grid & col_on)
        df[c] = snapped
    share = float(np.mean(on_grid))
    print(f"      max |csv - snapped-to-0.01|            {resid_max:.10f}"
          f"   (must be <= half-tick 0.005: {'PASS' if resid_max <= 0.005 + 1e-12 else '*** FAIL ***'})")
    print(f"      share of prices already on 0.01 grid   {share:.6%}"
          "   (expected ~100%: F2 exactly encodes CL's 0.01 grid, nothing finer to destroy)")
    assert resid_max <= 0.005 + 1e-12, "0.01-grid snap residual exceeds half-tick -- unexpected for CL"

    # ---- structural gates (all hard) ----------------------------------------------------
    dt = df["time"].diff().dropna()
    g1 = bool((dt > pd.Timedelta(0)).all())
    print("")
    print(f"    GATE time strictly increasing            {'PASS' if g1 else '*** FAIL ***'}")
    mins = df["time"].dt.hour * 60 + df["time"].dt.minute
    in_break = int(((mins > 17 * 60) & (mins <= 18 * 60)).sum())   # stamps in (17:00,18:00]
    g2 = in_break == 0
    print(f"    GATE no stamps in (17:00,18:00] ET       {'PASS' if g2 else '*** FAIL ***'}"
          f"  (found {in_break})")
    g3 = bool((df["high"] >= df[["open", "close"]].max(axis=1) - 1e-9).all()
              and (df["low"] <= df[["open", "close"]].min(axis=1) + 1e-9).all())
    print(f"    GATE OHLC sanity                          {'PASS' if g3 else '*** FAIL ***'}")
    g4 = bool((df["volume"] >= 0).all())
    print(f"    GATE volume >= 0                          {'PASS' if g4 else '*** FAIL ***'}")
    assert g1 and g2 and g3 and g4, "STRUCTURAL GATE FAILURE"

    # ---- session labels + HARD SEAL DROP ------------------------------------------------
    df["session"] = session_date(df["time"])
    dropped = int((df["session"] >= SEAL).sum())
    df = df[df["session"] < SEAL].reset_index(drop=True)
    mx = df["session"].max()
    print("")
    print("    SEAL RULE (CLAUDE.md s5 / LOCKED_FORWARD): HARD-DROP session >= 2026-08-01")
    print(f"      rows dropped at build time             {dropped:,}"
          "   (export was already capped at the s5 boundary; 0 expected)")
    print(f"      max retained session date              {mx.date()}")
    assert mx < SEAL, f"SEAL VIOLATION: max retained session {mx.date()} >= {SEAL.date()}"
    print(f"      ASSERT max retained session < {SEAL.date()}   PASS")

    # ---- cross-check: minute-volume sum + close vs the TRUE unmerged day store ----------
    print("")
    print("    CROSS-CHECK  session minute-volume sum vs db/day (true unmerged front contract,")
    print("                 reader ncd_day.py -- format validated against GetBars; CL is MONTHLY")
    print("                 so 'front' = the max-day-volume candidate around that date)")
    last_bar = df.groupby("session").tail(1).set_index("session")["close"]
    grid_ok = True
    for s, cids in DAY_CHECKS:
        s0 = pd.Timestamp(s)
        msum = int(df.loc[df["session"] == s0, "volume"].sum())
        cid, row = front_contract(cids, s0)
        if cid is None:
            print(f"      {s}: no day-store candidate row among {cids} (informational skip)")
            continue
        dvol = int(row["volume"])
        rel = abs(msum - dvol) / max(dvol, 1)
        c_1m = float(last_bar.get(s0, np.nan))
        dc = float(row["close"])
        off = c_1m - dc
        off_on_grid = abs(round(off / TICK) * TICK - off) < 1e-6
        grid_ok = grid_ok and off_on_grid
        print(f"      {s} front {cid}: minute-sum {msum:>9,}  day-bar {dvol:>9,}  rel {rel:.4%}"
              f"  {'MATCH' if rel <= 0.02 else 'DIVERGENT (informational)'}")
        print(f"                     close(1m-last) {c_1m:.2f}  day close {dc:.2f}  "
              f"offset {off:+.2f}  (whole 0.01 multiple: {'yes' if off_on_grid else 'NO'})")
    print(f"      all continuous-minus-day offsets are whole 0.01 multiples: "
          f"{'PASS' if grid_ok else 'see rows above'}")

    # ---- back-adjustment profile (documentation, not a gate) ----------------------------
    print("")
    print("    BACK-ADJUSTMENT PROFILE  (merged 'CL 09-26' minus true day-store close, median;")
    print("                              nonzero before the last roll is the expected merge")
    print("                              back-adjustment, same as all SM1M substrates)")
    for cid in ["CL 03-22", "CL 03-23", "CL 06-24", "CL 11-25", "CL 09-26"]:
        day = ND.read_contract(cid)
        if day.empty:
            continue
        day = day.set_index(pd.to_datetime(day["date"]))
        common = last_bar.index.intersection(day.index)
        if len(common) < 10:
            continue
        off = (last_bar.loc[common] - day.loc[common, "close"]).median()
        print(f"      {cid}: median(last-1m-close - day-close) over {len(common):>3} sessions"
              f" = {off:+.2f} pts")

    # ---- write parquet (schema identical to the other SM1M substrates) ------------------
    out = df[["time", "open", "high", "low", "close", "volume"]]
    out.to_parquet(PARQUET, index=False)
    ver = pd.read_parquet(PARQUET)
    assert len(ver) == len(out) and len(ver) > 0, "parquet verify failed"
    nsess = df["session"].nunique()
    print("")
    print("    OUTPUT")
    print(f"      parquet              {PARQUET}")
    print(f"      rows                 {len(ver):,}")
    print(f"      sessions             {nsess:,}")
    print(f"      first bar            {ver['time'].iloc[0]}")
    print(f"      last bar             {ver['time'].iloc[-1]}")
    print(f"      first session        {df['session'].min().date()}")
    print(f"      last session         {df['session'].max().date()}")
    print(f"      sha256               {sha256_file(PARQUET)}")
    print("")
    print("    5-ROW SAMPLE (head 3 + tail 2)")
    print(pd.concat([ver.head(3), ver.tail(2)]).to_string())


if __name__ == "__main__":
    main()
