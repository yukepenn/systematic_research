#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FT1 — INDEPENDENT (CLEAN-ROOM) REPRODUCTION of the ZBMACRO01 frozen engine.
Run G3_ZBMACRO_FT_20260906, ledger G00083.

CLEAN-ROOM DISCIPLINE: this file is written from the FT0 text in spec.yaml ONLY.
It imports nothing from, and copies nothing from, runs/G3_ZBMACRO_*/src. The frozen
run OUTPUT artifacts (trades.csv from the falsifier run, maemfe.csv from the engine
run) are read solely as the comparison targets the FT1 bar is defined against.

FT0 (verbatim from spec.yaml):
  calendar: NFP_DAY / CPI_DAY per GENESIS_H2_CALENDAR_20260828
  signal:   r1 = close(08:45) - close(08:30) on ZB 1-min (END-stamped, ET). Trade iff r1 < 0.
  action:   SHORT k=2 ZB filled at the close of the 08:46 bar; EXIT buy at the 15:00 bar
            close. No overnight. No other conditions.

IMPLEMENTATION CHOICES (fixed before results, stated):
  * Sessions are 18:00 -> 17:00 ET; a bar stamped >= 18:00 belongs to the NEXT calendar
    day's session. Bars are END-stamped: "close(08:45)" is the close of the bar stamped
    08:45.
  * "close(HH:MM)" is read AS-OF: the last printed bar close at or before HH:MM, looking
    back at most 15 minutes (release mornings print every minute; the lookback only
    protects thin non-event minutes).
  * A session enters the trade list iff it is an NFP/CPI calendar session inside the
    substrate window AND the as-of closes at 08:30, 08:45, 08:46 and 15:00 all exist
    AND r1 < 0. Direction is always SHORT (r1 < 0 by construction).

BAR (spec verbatim): 40/40 dates exact; 08:46 entry fills and 15:00 exit fills < 1e-9 pt.
DATA SEAL: assert substrate max session <= 2026-07-31.
Gate table is program-printed to out/ft1_table.txt. Trades to out/ft1_trades.csv.
"""

import os
import sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN_DIR = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(RUN_DIR, os.pardir, os.pardir))

ZB_PARQUET = os.path.join(REPO, "runs", "SM1M_ZB_SUBSTRATE", "out", "zb_1m_2023_2026.parquet")
NFP_CSV = os.path.join(REPO, "runs", "GENESIS_H2_CALENDAR_20260828", "out",
                       "calendar_artifacts", "daytype_sessions_NFP_DAY.csv")
CPI_CSV = os.path.join(REPO, "runs", "GENESIS_H2_CALENDAR_20260828", "out",
                       "calendar_artifacts", "daytype_sessions_CPI_DAY.csv")
# frozen comparison targets (run OUTPUTS, not src)
TRADES_CSV = os.path.join(REPO, "runs", "G3_ZBMACRO_FALSIFIER_20260906", "out", "trades.csv")
MAEMFE_CSV = os.path.join(REPO, "runs", "G3_ZBMACRO_ENGINE_20260906", "out", "maemfe.csv")
OUT = os.path.join(RUN_DIR, "out")
os.makedirs(OUT, exist_ok=True)

SEAL = pd.Timestamp("2026-07-31").date()
LOOKBACK_MIN = 15
TOL = 1e-9

LINES = []
def say(s=""):
    print(s)
    LINES.append(s)

# ---------------------------------------------------------------- load substrate, sessionize
bars = pd.read_parquet(ZB_PARQUET)
ts = pd.to_datetime(bars["time"])
sess = (ts.dt.normalize() + pd.to_timedelta((ts.dt.hour >= 18).astype(int), unit="D")).dt.date
bars = pd.DataFrame({"ts": ts, "sess": sess, "close": bars["close"].to_numpy()})
assert bars["sess"].max() <= SEAL, f"SEAL VIOLATION: {bars['sess'].max()}"
n_sessions = bars["sess"].nunique()

# ---------------------------------------------------------------- calendar (NFP | CPI in window)
nfp = set(pd.to_datetime(pd.read_csv(NFP_CSV)["session_date"]).dt.date)
cpi = set(pd.to_datetime(pd.read_csv(CPI_CSV)["session_date"]).dt.date)
smin, smax = bars["sess"].min(), bars["sess"].max()
events = sorted(d for d in (nfp | cpi) if smin <= d <= smax)

# ---------------------------------------------------------------- as-of close reader
by_sess = {d: g for d, g in bars.groupby("sess")}

def asof_close(day, hh, mn):
    """Last printed close at or before hh:mn on `day`'s session, lookback <= 15 min."""
    g = by_sess.get(day)
    if g is None:
        return np.nan
    tgt = pd.Timestamp(day) + pd.Timedelta(hours=hh, minutes=mn)
    lo = tgt - pd.Timedelta(minutes=LOOKBACK_MIN)
    w = g[(g["ts"] <= tgt) & (g["ts"] >= lo)]
    return float(w["close"].iloc[-1]) if len(w) else np.nan

# ---------------------------------------------------------------- FT1 trade construction
rows = []
for d in events:
    c0830 = asof_close(d, 8, 30)
    c0845 = asof_close(d, 8, 45)
    c0846 = asof_close(d, 8, 46)
    c1500 = asof_close(d, 15, 0)
    if any(np.isnan(v) for v in (c0830, c0845, c0846, c1500)):
        continue
    r1 = c0845 - c0830
    if r1 < 0:
        rel = ("NFP" if d in nfp else "") + ("CPI" if d in cpi else "")
        rows.append(dict(session_date=d, release=rel, direction="SHORT",
                         r1_pts=r1, entry_0846_px=c0846, exit_1500_px=c1500))
ft1 = pd.DataFrame(rows)
ft1.to_csv(os.path.join(OUT, "ft1_trades.csv"), index=False)

# ---------------------------------------------------------------- comparison targets
tr = pd.read_csv(TRADES_CSV)
tr_dates = pd.to_datetime(tr["session_date"]).dt.date.to_numpy()
mf = pd.read_csv(MAEMFE_CSV)
mf_dates = pd.to_datetime(mf["session_date"]).dt.date.to_numpy()

say("=" * 100)
say("FT1 -- independent clean-room reproduction of ZBMACRO01  (G3_ZBMACRO_FT_20260906, G00083)")
say(f"substrate: {os.path.relpath(ZB_PARQUET, REPO)}  sessions={n_sessions} ({smin} .. {smax})")
say(f"seal: max session {bars['sess'].max()} <= {SEAL}  OK")
say(f"calendar: NFP|CPI sessions in window = {len(events)}")
say(f"FT1 construction: {len(ft1)} trades (event day, all four as-of closes present, r1 < 0)")
say("")

# gate 1: dates 40/40 exact
g1 = (len(ft1) == 40 and len(tr_dates) == 40
      and all(a == b for a, b in zip(ft1["session_date"].to_numpy(), tr_dates)))
# gate 2: directions -- all SHORT, and every frozen trade is a short (r1<0 in both)
g2 = bool(g1 and (ft1["direction"] == "SHORT").all()
          and float(np.max(np.abs(ft1["r1_pts"].to_numpy() - tr["r1_pts"].to_numpy()))) < TOL
          and (tr["r1_pts"] < 0).all())
# gate 3: entry fills (08:46 close) vs the frozen engine dossier's per-trade entry prices
if g1 and all(a == b for a, b in zip(mf_dates, tr_dates)):
    dmax_entry = float(np.max(np.abs(ft1["entry_0846_px"].to_numpy()
                                     - mf["entry_0846_px"].to_numpy())))
else:
    dmax_entry = np.inf
g3 = dmax_entry < TOL
# gate 4: exit fills (15:00 close) vs the frozen falsifier identity c1500 = c0845 + fwd
#         (c0845 read from the engine dossier's entry_0845_px column; fwd from trades.csv)
if g1:
    exit_frozen = mf["entry_0845_px"].to_numpy() + tr["fwd_0845_1500_pts"].to_numpy()
    dmax_exit = float(np.max(np.abs(ft1["exit_1500_px"].to_numpy() - exit_frozen)))
else:
    dmax_exit = np.inf
g4 = dmax_exit < TOL

say(f"{'GATE':<22}{'SPEC':<52}{'OBSERVED':<40}{'PASS/FAIL':>9}")
say("-" * 123)
say(f"{'FT1_dates':<22}{'40/40 session dates exact vs frozen trades.csv':<52}"
    f"{'%d trades; dates exact=%s' % (len(ft1), g1):<40}{'PASS' if g1 else 'FAIL':>9}")
say(f"{'FT1_directions':<22}{'all SHORT; r1<0 both sides, |dr1|<1e-9':<52}"
    f"{'all SHORT=%s' % g2:<40}{'PASS' if g2 else 'FAIL':>9}")
say(f"{'FT1_entry_fills':<22}{'max|entry(08:46) - frozen| < 1e-9 pt':<52}"
    f"{'max diff = %.3g pt' % dmax_entry:<40}{'PASS' if g3 else 'FAIL':>9}")
say(f"{'FT1_exit_fills':<22}{'max|exit(15:00) - frozen| < 1e-9 pt':<52}"
    f"{'max diff = %.3g pt' % dmax_exit:<40}{'PASS' if g4 else 'FAIL':>9}")
say("-" * 123)
ft1_pass = bool(g1 and g2 and g3 and g4)
say(f"FT1 VERDICT (mechanical): {'PASS -- bar met (40/40 exact, fills < 1e-9 pt)' if ft1_pass else 'FAIL'}")
say("EVIDENCE STATUS: DISCOVERY_CONSUMED (reproduction of frozen in-sample objects; no new claim).")
say("=" * 100)

with open(os.path.join(OUT, "ft1_table.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(LINES) + "\n")

sys.exit(0 if ft1_pass else 1)
