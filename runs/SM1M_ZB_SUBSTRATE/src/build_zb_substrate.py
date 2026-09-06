"""SM1M_ZB_SUBSTRATE -- materialize the owned-but-never-extracted ZB (30Y T-bond) 1-minute surface.

RUN CLASS: $0 DATA EXTRACTION (no hypothesis, no signal, no P&L). SM1M pattern.
DATA_VERDICT_20260831.md called ZB 1-min "not extracted" (1,113 census file-dates from
2023-01-02); external mining called it the only genuinely new raw information surface.

PIPELINE (identical construction to runs/SM1M_SUBSTRATE and the ES/RTY/YM substrates):
  1. NT8-side export: SWMinuteExport_v1 (sha256 48c21a77...cdc89d, re-installed via the
     CLAUDE.md s6 LOCAL PATH, resolved in fresh assembly 40daedcc00a24a0ba7d83631d1c25d80)
     via CrossTrade RunStrategyBacktest job 58daa58aab60476e (nt8_strategy_analyzer,
     NT8 8.1.8.1, fingerprint sha256:b4255f1b0dd7fba1):
        instrument "ZB 09-26" (merge back-adjusted front-month series), Minute/1 Last,
        from 2022-12-24T00:00:00Z  to 2026-07-31T21:59:59Z
        (`to` == session_close_boundary_utc(2026-07-31), research_sdk/session_boundary.py).
     Loaded 1,087,287 bars; CSV Documents/NinjaTrader 8/out/zb1m_2023_2026_1m.csv
     (raw CSV kept outside the repo, per the SM1M pattern).
  2. This script: PRICE-GRID RESTORATION (see below), gates, session labels, HARD SEAL
     DROP, parquet.

PRICE-GRID RESTORATION (ZB-specific, documented prominently):
  SWMinuteExport_v1 formats prices with ToString("F2"). ZB's tick is 1/32 = 0.03125, so the
  CSV carries prices rounded to 0.01. This is EXACTLY invertible: true prices sit on the
  1/32 grid (subset of the 1/64 grid, spacing 0.015625); the F2 rounding error is <= 0.005,
  which is strictly less than the 1/64 half-spacing 0.0078125, so nearest-1/64 snapping of
  the CSV value recovers the true price uniquely regardless of the formatter's tie-breaking.
  The script measures and prints the snap residuals and the share of restored prices that
  sit on the coarser 1/32 grid, and cross-checks restored closes against the TRUE unmerged
  day store (ncd_day.py, format validated against GetBars).

CONVENTION: bars are END-stamped ET; NO shift is applied anywhere (verified for this export
pattern against the NQ substrate bar-for-bar; see SM1M_MNQ_SUBSTRATE/MANIFEST.md).
CBOT 30Y session: 18:00 ET -> 17:00 ET next day, same label rule as the index substrates.
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
import ncd_day as ND  # noqa: E402

CSV = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8", "out",
                   "zb1m_2023_2026_1m.csv")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
PARQUET = os.path.join(OUT, "zb_1m_2023_2026.parquet")
SEAL = pd.Timestamp("2026-08-01")
GRID64 = 1.0 / 64.0

DAY_CHECKS = [("2023-08-15", "ZB 09-23"), ("2024-05-14", "ZB 06-24"), ("2025-10-15", "ZB 12-25")]


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def session_date(ts: pd.Series) -> pd.Series:
    """src/analytics/runlib.py:35 session_date, vectorized (END-stamped ET input, NO shift)."""
    d = ts.dt.normalize()
    d = d.where(ts.dt.hour < 18, d + pd.Timedelta(days=1))
    d = d.where(d.dt.dayofweek != 5, d + pd.Timedelta(days=2))
    d = d.where(d.dt.dayofweek != 6, d + pd.Timedelta(days=1))
    return d


def main():
    print("=" * 100)
    print("=== SM1M_ZB_SUBSTRATE build -- DATA EXTRACTION ONLY (no signal, no P&L)")
    print("=" * 100)
    print(f"    input CSV            {CSV}")
    print(f"    input sha256         {sha256_file(CSV)}")
    df = pd.read_csv(CSV, parse_dates=["time"])
    df["volume"] = df["volume"].astype("int64")
    n0 = len(df)
    print(f"    rows read            {n0:,}")

    # ---- price-grid restoration ---------------------------------------------------------
    print("")
    print("    PRICE-GRID RESTORATION  (F2 CSV -> exact 1/64 grid; see module docstring)")
    resid_max = 0.0
    on32 = None
    for c in ("open", "high", "low", "close"):
        snapped = np.round(df[c].values / GRID64) * GRID64
        resid_max = max(resid_max, float(np.abs(snapped - df[c].values).max()))
        df[c] = snapped
        k64 = np.round(df[c].values / GRID64).astype(np.int64)
        col_on32 = (k64 % 2 == 0)
        on32 = col_on32 if on32 is None else (on32 & col_on32)
    share32 = float(np.mean([(np.round(df[c].values / (1 / 32.0)) * (1 / 32.0) ==
                             df[c].values).mean() for c in ("open", "high", "low", "close")]))
    print(f"      max |csv - snapped|                    {resid_max:.6f}"
          f"   (must be <= 0.005: {'PASS' if resid_max <= 0.005 + 1e-12 else '*** FAIL ***'})")
    print(f"      share of restored prices on 1/32 grid  {share32:.6%}"
          "   (ZB outright tick = 1/32; 1/64-only residents reported, not dropped)")
    assert resid_max <= 0.005 + 1e-12, "F2 inversion assumption violated"

    # ---- structural gates ----------------------------------------------------------------
    dt = df["time"].diff().dropna()
    g1 = bool((dt > pd.Timedelta(0)).all())
    print("")
    print(f"    GATE time strictly increasing            {'PASS' if g1 else '*** FAIL ***'}")
    mins = df["time"].dt.hour * 60 + df["time"].dt.minute
    in_break = int(((mins > 17 * 60) & (mins <= 18 * 60)).sum())
    g2 = in_break == 0
    print(f"    GATE no stamps in (17:00,18:00] ET       {'PASS' if g2 else '*** FAIL ***'}"
          f"  (found {in_break})")
    g3 = bool((df["high"] >= df[["open", "close"]].max(axis=1) - 1e-9).all()
              and (df["low"] <= df[["open", "close"]].min(axis=1) + 1e-9).all())
    print(f"    GATE OHLC sanity (post-restoration)       {'PASS' if g3 else '*** FAIL ***'}")
    g4 = bool((df["volume"] >= 0).all())
    print(f"    GATE volume >= 0                          {'PASS' if g4 else '*** FAIL ***'}")
    assert g1 and g2 and g3 and g4, "STRUCTURAL GATE FAILURE"

    # ---- session labels + HARD SEAL DROP -------------------------------------------------
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

    # ---- cross-check: volume + restored close vs TRUE unmerged day store -----------------
    print("")
    print("    CROSS-CHECK  session minute-volume sum AND restored close vs db/day")
    print("                 (true unmerged contract data; ncd_day.py validated vs GetBars)")
    last_bar = df.groupby("session").tail(1).set_index("session")["close"]
    for s, cid in DAY_CHECKS:
        s0 = pd.Timestamp(s)
        msum = int(df.loc[df["session"] == s0, "volume"].sum())
        day = ND.read_contract(cid)
        if day.empty or s0 not in set(pd.to_datetime(day["date"])):
            print(f"      {s} {cid}: day-store row UNAVAILABLE (informational check skipped)")
            continue
        row = day.loc[pd.to_datetime(day["date"]) == s0].iloc[0]
        dvol = int(row["volume"])
        rel = abs(msum - dvol) / max(dvol, 1)
        c_1m = float(last_bar.get(s0, np.nan))
        dc = float(row["close"])
        print(f"      {s} {cid}: minute-sum {msum:>9,}  day-bar {dvol:>9,}  rel {rel:.4%}"
              f"  {'MATCH' if rel <= 0.02 else 'DIVERGENT (informational)'}"
              f"   close(1m-last) {c_1m:.5f}  day close {dc:.5f}"
              f"  diff {c_1m - dc:+.5f}")

    # ---- back-adjustment profile ---------------------------------------------------------
    print("")
    print("    BACK-ADJUSTMENT PROFILE  (merged 'ZB 09-26' minus true day-store close, median)")
    for cid in sorted({c for _, c in DAY_CHECKS} | {"ZB 03-23", "ZB 09-26"}):
        day = ND.read_contract(cid)
        if day.empty:
            continue
        day = day.set_index(pd.to_datetime(day["date"]))
        common = last_bar.index.intersection(day.index)
        if len(common) < 10:
            continue
        off = (last_bar.loc[common] - day.loc[common, "close"]).median()
        print(f"      {cid}: median(last-1m-close - day-close) over {len(common):>3} sessions"
              f" = {off:+.5f} pts ({off * 32:+.1f}/32nds)")

    # ---- write parquet (schema identical to the other SM1M substrates) -------------------
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
