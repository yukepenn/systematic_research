"""NQ1M_BIDASK_EXTRACT_20260906 -- materialize the never-recorded NQ minute Bid/Ask surface.

RUN CLASS: $0 DATA EXTRACTION + one ENGINEERING/COST first-look (no hypothesis, no signal,
no P&L). DATA_VERDICT_20260831.md: "NQ minute Bid/Ask -- 81 sessions -- 0 extracted, never
recorded anywhere"; it is the only owned object that can check the modelled NQ spread
($12.50-$14.44/ctrRT family) at 1-minute resolution.

PIPELINE:
  NT8-side export, SWMinuteExport_v1 (sha256 48c21a77...cdc89d, re-installed via the
  CLAUDE.md s6 LOCAL PATH, fresh assembly 40daedcc00a24a0ba7d83631d1c25d80), four
  CrossTrade RunStrategyBacktest jobs (nt8_strategy_analyzer, NT8 8.1.8.1, fingerprint
  sha256:b4255f1b0dd7fba1), Minute/1 with bars_period.market_data_type = Bid / Ask:

    leg A  "NQ 06-26"  Bid job edd5edb579d648c0 / Ask job ccdce820493a4f72
           from 2026-04-30T22:00:00Z  to 2026-06-11T21:59:59Z
    leg B  "NQ 09-26"  Bid job 0d67c94b4a744416 / Ask job 26e74ef6d05a4c23
           from 2026-06-11T22:00:00Z  to 2026-07-31T21:59:59Z

  Windows are session boundaries from research_sdk/session_boundary.py. The leg split at
  the 2026-06-11/06-12 session boundary matches the local store's own front handoff
  (db/minute/"NQ 06-26" Bid/Ask files end 20260611; "NQ 09-26" files begin 20260608), so
  every retained bar is the FRONT contract's own quote series, served unadjusted (each
  contract is the anchor segment of its own merged request over its retained window --
  verified: probe Last volumes matched the NQ substrate bar-for-bar, and probe 06-26
  prices were the true, un-back-adjusted contract prices).

  The market_data_type plumbing was proven before the full runs: Bid / Ask / Last probes
  over the same window produced three distinct files with bid < ask (e.g. 2026-05-11
  09:31 close 29342.25 / 29342.75 / 29342.75(Last basis-shifted)); NT8 additionally served
  minute BBO back beyond the local store's 2026-05-10 start (provider history), so the
  extract covers every session 2026-05-01 -> 2026-07-31, more than the 81 census dates.

SERIES SEMANTICS (document, don't guess): each leg exports NT8 minute BARS built from the
Bid (resp. Ask) quote stream: OHLC are bid (ask) quote prices; the `volume` field of a
quote-series bar is NT8's quote-side volume aggregate, NOT trade volume. It is carried
through as bid_vol / ask_vol unmodified and unexplained rather than dropped.

FIRST-LOOK measurement printed at the end and embedded in MANIFEST.md:
  per-session median and p90 of (ask_close - bid_close)/0.25 ticks.
  BASIS: SPREAD_ONLY, EVIDENCE: MEASURED (minute-close BBO, burned window).

CONVENTION: bars END-stamped ET, no shift. SEAL: HARD-DROP session >= 2026-08-01.
"""
from __future__ import annotations

import hashlib
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
NT8OUT = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8", "out")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
PARQUET = os.path.join(OUT, "nq_1m_bidask_202605_202607.parquet")
SEAL = pd.Timestamp("2026-08-01")
TICK = 0.25
BURN0 = pd.Timestamp("2026-05-31")

LEGS = [
    ("NQ 06-26", "nqbid0626", "nqask0626", pd.Timestamp("2026-05-01"), pd.Timestamp("2026-06-11")),
    ("NQ 09-26", "nqbid0926", "nqask0926", pd.Timestamp("2026-06-12"), pd.Timestamp("2026-07-31")),
]


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


def load_leg(contract, btag, atag, s_lo, s_hi):
    parts = {}
    for side, tag in (("bid", btag), ("ask", atag)):
        p = os.path.join(NT8OUT, f"{tag}_1m.csv")
        print(f"      {side:<4} csv {p}")
        print(f"           sha256 {sha256_file(p)}")
        d = pd.read_csv(p, parse_dates=["time"])
        d = d.rename(columns={c: f"{side}_{c}" for c in ("open", "high", "low", "close")})
        d = d.rename(columns={"volume": f"{side}_vol"})
        parts[side] = d
    m = parts["bid"].merge(parts["ask"], on="time", how="outer", indicator=True)
    nb, na = len(parts["bid"]), len(parts["ask"])
    unmatched = int((m["_merge"] != "both").sum())
    m = m[m["_merge"] == "both"].drop(columns=["_merge"]).sort_values("time")
    m["session"] = session_date(m["time"])
    kept = m[(m["session"] >= s_lo) & (m["session"] <= s_hi)].copy()
    kept.insert(1, "contract", contract)
    print(f"      bid rows {nb:,}  ask rows {na:,}  timestamp-unmatched {unmatched:,}"
          f"  joined+windowed rows {len(kept):,}"
          f"  sessions {kept['session'].nunique()} ({s_lo.date()} -> {s_hi.date()})")
    return kept


def main():
    print("=" * 100)
    print("=== NQ1M_BIDASK_EXTRACT_20260906 build -- DATA EXTRACTION + ENGINEERING FIRST-LOOK")
    print("=" * 100)
    legs = []
    for contract, btag, atag, lo, hi in LEGS:
        print(f"    leg {contract}")
        legs.append(load_leg(contract, btag, atag, lo, hi))
    df = pd.concat(legs, ignore_index=True)

    # ---- structural gates ----------------------------------------------------------------
    print("")
    g1 = bool((df["time"].diff().dropna() > pd.Timedelta(0)).all())
    print(f"    GATE time strictly increasing across legs   {'PASS' if g1 else '*** FAIL ***'}")
    ovl = set(legs[0]["session"]) & set(legs[1]["session"])
    g2 = len(ovl) == 0
    print(f"    GATE leg sessions disjoint                   {'PASS' if g2 else '*** FAIL ***'}")
    mins = df["time"].dt.hour * 60 + df["time"].dt.minute
    in_break = int(((mins > 17 * 60) & (mins <= 18 * 60)).sum())
    g3 = in_break == 0
    print(f"    GATE no stamps in (17:00,18:00] ET           {'PASS' if g3 else '*** FAIL ***'}"
          f"  (found {in_break})")
    for side in ("bid", "ask"):
        ok = bool((df[f"{side}_high"] >= df[[f"{side}_open", f"{side}_close"]].max(axis=1) - 1e-9).all()
                  and (df[f"{side}_low"] <= df[[f"{side}_open", f"{side}_close"]].min(axis=1) + 1e-9).all())
        print(f"    GATE {side} OHLC sanity                        {'PASS' if ok else '*** FAIL ***'}")
        assert ok
    assert g1 and g2 and g3, "STRUCTURAL GATE FAILURE"
    crossed = int((df["ask_close"] < df["bid_close"]).sum())
    print(f"    crossed minute-closes (ask_close < bid_close)  {crossed:,} of {len(df):,}"
          f"  ({crossed / len(df):.4%})  -- retained as-is, reported")

    # ---- HARD SEAL DROP ------------------------------------------------------------------
    dropped = int((df["session"] >= SEAL).sum())
    df = df[df["session"] < SEAL].reset_index(drop=True)
    mx = df["session"].max()
    print("")
    print("    SEAL RULE (CLAUDE.md s5 / LOCKED_FORWARD): HARD-DROP session >= 2026-08-01")
    print(f"      rows dropped at build time             {dropped:,}")
    print(f"      max retained session date              {mx.date()}")
    assert mx < SEAL, f"SEAL VIOLATION: max retained session {mx.date()} >= {SEAL.date()}"
    print(f"      ASSERT max retained session < {SEAL.date()}   PASS")

    # ---- write parquet -------------------------------------------------------------------
    cols = ["time", "session", "contract",
            "bid_open", "bid_high", "bid_low", "bid_close", "bid_vol",
            "ask_open", "ask_high", "ask_low", "ask_close", "ask_vol"]
    out = df[cols]
    out.to_parquet(PARQUET, index=False)
    ver = pd.read_parquet(PARQUET)
    assert len(ver) == len(out) and len(ver) > 0, "parquet verify failed"
    print("")
    print("    OUTPUT")
    print(f"      parquet              {PARQUET}")
    print(f"      rows                 {len(ver):,}")
    print(f"      sessions             {df['session'].nunique():,}")
    print(f"      first bar            {ver['time'].iloc[0]}")
    print(f"      last bar             {ver['time'].iloc[-1]}")
    print(f"      first session        {df['session'].min().date()}")
    print(f"      last session         {df['session'].max().date()}")
    print(f"      sha256               {sha256_file(PARQUET)}")
    print("")
    print("    5-ROW SAMPLE (head 3 + tail 2)")
    with pd.option_context("display.width", 200):
        print(pd.concat([ver.head(3), ver.tail(2)]).to_string())

    # ---- FIRST-LOOK: per-session spread in ticks from minute closes ----------------------
    df["spread_ticks"] = (df["ask_close"] - df["bid_close"]) / TICK
    mins2 = df["time"].dt.hour * 60 + df["time"].dt.minute      # recomputed post-drop
    rth = (mins2 >= 9 * 60 + 31) & (mins2 <= 16 * 60)           # END-stamps 09:31..16:00
    print("")
    print("=" * 100)
    print("    FIRST-LOOK  NQ minute-close BBO spread, per session, in ticks (tick = 0.25)")
    print("    BASIS: SPREAD_ONLY, EVIDENCE: MEASURED (minute-close BBO, burned window)")
    print("    (engineering/cost measurement on <= 2026-07-31 data; sessions < 2026-05-31 are")
    print("     PRE_BURN, >= 2026-05-31 BURNED; none of this is forward evidence)")
    print("=" * 100)
    print(f"    {'session':<12}{'era':<9}{'contract':<9}{'bars':>6}{'median':>8}{'p90':>8}"
          f"{'medRTH':>8}")
    for s, g in df.groupby("session"):
        era = "BURNED" if s >= BURN0 else "PRE_BURN"
        gr = g[rth.loc[g.index]]
        print(f"    {str(s.date()):<12}{era:<9}{g['contract'].iloc[0]:<9}{len(g):>6}"
              f"{g['spread_ticks'].median():>8.2f}{g['spread_ticks'].quantile(0.9):>8.2f}"
              f"{gr['spread_ticks'].median() if len(gr) else float('nan'):>8.2f}")
    allr = df["spread_ticks"]
    print("    " + "-" * 60)
    print(f"    {'ALL':<12}{'':<9}{'':<9}{len(df):>6}{allr.median():>8.2f}"
          f"{allr.quantile(0.9):>8.2f}{df.loc[rth[rth].index, 'spread_ticks'].median():>8.2f}")
    print("")
    print(f"    dollar view: 1 tick = $5.00/NQ contract; median spread "
          f"{allr.median():.2f} t = ${allr.median() * 5:.2f} one-way quote width at minute close")


if __name__ == "__main__":
    main()
