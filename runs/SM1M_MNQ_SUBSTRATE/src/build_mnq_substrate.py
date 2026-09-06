"""SM1M_MNQ_SUBSTRATE -- materialize the owned-but-never-extracted MNQ 1-minute surface.

RUN CLASS: $0 DATA EXTRACTION (no hypothesis, no signal, no P&L). SM1M pattern.

PIPELINE (identical construction to runs/SM1M_SUBSTRATE and the ES/RTY/YM substrates):
  1. NT8-side export: SWMinuteExport_v1 (research/scalping_lab/src/ninjascript/, sha256
     48c21a775326b69a731fea27945c9b41b99ccec4553992bee5f75acd92cdc89d, re-installed via the
     CLAUDE.md s6 LOCAL PATH -- file copied into bin/Custom/Strategies, picked up by NT8
     without F5, class resolved in fresh assembly 40daedcc00a24a0ba7d83631d1c25d80)
     run through CrossTrade RunStrategyBacktest (job 7c80c101b6dd471a, engine
     nt8_strategy_analyzer, NT8 8.1.8.1, fingerprint sha256:b4255f1b0dd7fba1):
        instrument "MNQ 09-26" (merge back-adjusted front-month series, same as the
        NQ/ES/RTY/YM substrates), Minute/1 Last,
        from 2021-12-24T00:00:00Z  to 2026-07-31T21:59:59Z
        (`to` == session_close_boundary_utc(2026-07-31) from research_sdk/session_boundary.py:
         one second before the next 18:00 ET open -- the s5 seal cap applied AT THE EXPORT).
     Loaded 1,629,368 bars; CSV Documents/NinjaTrader 8/out/mnq1m_2022_2026_1m.csv
     (raw CSV kept outside the repo, per the SM1M pattern).
  2. This script: gates, session labeling, HARD SEAL DROP, parquet.

WHY NOT A LOCAL .ncd DECODE: there is no working minute-.ncd content parser in this repo.
runs/VOLUME00_20260828 tried three fixed-record layouts structurally and printed
"MINUTE LAYOUT NOT RESOLVED" (out/volume00.txt:104) -- NT8 minute files are variable-length
encoded, unlike the 48-byte-record day files that research/multi_market/src/ncd_day.py reads.
The NT8-side export IS the existing, validated extraction tooling for minute data.

CONVENTION: bars are END-stamped ET (the bar stamped 09:31 opens 09:30:00); NO shift is
applied anywhere. Verified against the NQ substrate before this build: probe session
2026-05-11, NQ Last minute volumes 6848 @ 09:31 / 689 @ 14:00 on 2026-05-12 match
runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet bar-for-bar at identical stamps.
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
                   "mnq1m_2022_2026_1m.csv")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
PARQUET = os.path.join(OUT, "mnq_1m_2022_2026.parquet")
SEAL = pd.Timestamp("2026-08-01")
NQ_REF = os.path.join(ROOT, "runs", "SM1M_SUBSTRATE", "out", "nq_1m_2022_2026.parquet")

# cross-source day-store spot checks: (session date, expected front contract in db/day)
DAY_CHECKS = [("2023-02-15", "MNQ 03-23"), ("2024-05-14", "MNQ 06-24"), ("2025-11-18", "MNQ 12-25")]


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


def main():
    print("=" * 100)
    print("=== SM1M_MNQ_SUBSTRATE build -- DATA EXTRACTION ONLY (no signal, no P&L)")
    print("=" * 100)
    print(f"    input CSV            {CSV}")
    print(f"    input sha256         {sha256_file(CSV)}")
    df = pd.read_csv(CSV, parse_dates=["time"])
    df["volume"] = df["volume"].astype("int64")
    n0 = len(df)
    print(f"    rows read            {n0:,}")

    # ---- structural gates (all hard) ----------------------------------------------------
    dt = df["time"].diff().dropna()
    g1 = bool((dt > pd.Timedelta(0)).all())
    print(f"    GATE time strictly increasing            {'PASS' if g1 else '*** FAIL ***'}")
    mins = df["time"].dt.hour * 60 + df["time"].dt.minute
    in_break = ((mins > 17 * 60) & (mins <= 18 * 60)).sum()   # stamps in (17:00,18:00]
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

    # ---- cross-check A: bar-grid vs the NQ substrate (same family, same template) -------
    print("")
    print("    CROSS-CHECK A  bar-stamp grid vs runs/SM1M_SUBSTRATE nq_1m_2022_2026.parquet")
    nq = pd.read_parquet(NQ_REF, columns=["time"])
    nqt = pd.DatetimeIndex(nq["time"])
    for s in ("2023-06-15", "2025-03-12", "2026-06-10"):
        s0 = pd.Timestamp(s)
        mine = set(df.loc[df["session"] == s0, "time"])
        lo, hi = s0 - pd.Timedelta(hours=6), s0 + pd.Timedelta(hours=17, minutes=1)
        ref_all = nqt[(nqt >= lo) & (nqt <= hi)]
        ref = {t for t in ref_all if (t.hour >= 18 and t.normalize() == s0 - pd.Timedelta(days=1))
               or (t.hour < 18 and t.normalize() == s0)}
        j = len(mine & ref) / max(len(mine | ref), 1)
        print(f"      session {s}: MNQ bars {len(mine):>5}  NQ bars {len(ref):>5}  "
              f"stamp-set Jaccard {j:.4f}")

    # ---- cross-check B: minute-volume sum vs the TRUE unmerged day store ----------------
    print("")
    print("    CROSS-CHECK B  session minute-volume sum vs db/day (true unmerged contract data,")
    print("                   reader ncd_day.py -- format validated against GetBars)")
    for s, cid in DAY_CHECKS:
        s0 = pd.Timestamp(s)
        msum = int(df.loc[df["session"] == s0, "volume"].sum())
        day = ND.read_contract(cid)
        if day.empty or s0 not in set(pd.to_datetime(day["date"])):
            print(f"      {s} {cid}: day-store row UNAVAILABLE (informational check skipped)")
            continue
        dvol = int(day.loc[pd.to_datetime(day["date"]) == s0, "volume"].iloc[0])
        rel = abs(msum - dvol) / max(dvol, 1)
        print(f"      {s} {cid}: minute-sum {msum:>10,}  day-bar {dvol:>10,}  "
              f"rel diff {rel:.4%}  {'MATCH' if rel <= 0.02 else 'DIVERGENT (informational)'}")

    # ---- back-adjustment profile (documentation, not a gate) ----------------------------
    print("")
    print("    BACK-ADJUSTMENT PROFILE  (merged 'MNQ 09-26' series minus true day-store close,")
    print("                              median per year; nonzero before the last rolls is the")
    print("                              expected merge back-adjustment, same as all SM1M substrates)")
    last_bar = df.groupby("session").tail(1).set_index("session")["close"]
    for cid in sorted({c for _, c in DAY_CHECKS} | {"MNQ 03-22", "MNQ 09-26"}):
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

    # ---- write parquet (schema identical to the other four SM1M substrates) -------------
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
