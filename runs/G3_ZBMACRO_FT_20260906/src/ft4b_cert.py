#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FT4b — OFFLINE CERTIFICATION of src/ZbMacroResponse_v1.cs.
Run G3_ZBMACRO_FT_20260906, ledger G00083.  Precedent: HD-23 offline certification.

WHAT THIS IS: a Python STATE MACHINE MIRRORED, event-for-event, from the .cs source's
OnBarUpdate flow, replayed over the full 923-session ZB substrate under Strategy Analyzer
(historical) semantics — every M1 realtime guard is a constant no-op, EntriesAllowed() is a
constant true, and the calendar is loaded (the deployment CSV = NFP|CPI union).  Each mirror
block cites the .cs line it transcribes (line numbers of src/ZbMacroResponse_v1.cs as
committed in this run).

MIRRORED FLOW (per bar, in .cs order; line numbers of src/ZbMacroResponse_v1.cs @ 849 lines):
  L725-760  session change: overnight-carry fail-safe check (L729-735), per-session state
            reset (eventDay from the calendar, px0830/px0845=NaN, flags cleared), and the
            EARLY-CLOSE guard (L744-759): template session end <= 15:00 ET => STAND ASIDE.
            MIRROR NOTE: NT8 reads the template's ActualSessionEnd (foreknowledge of the
            holiday schedule); the substrate has no template, so the mirror proxies it with
            the session's LAST PRINTED BAR timestamp — metadata look-ahead that stands in
            for the template, never price look-ahead.  (Good Friday 2026-04-03: last bar
            12:15 => early close => stand aside, matching the frozen universe's exclusion.)
  L766      hm == 08:30 exact -> px0830 = Close
  L767-781  hm == 08:45 exact -> px0845 = Close; on a non-early-close event day: missing
            px0830 => STAND ASIDE (fail-closed); else r1 = px0845 - px0830 < 0 => armedShort
  L783-788  event day, hm > 08:45, px0845 missing => STAND ASIDE (fail-closed)
  L792-811  entry: armed & !entryDone: hm == 08:46 exact => EnterShort(K), ledger books
            Close of the 08:46 bar; hm > 08:46 => armed signal EXPIRES unfilled (fail-closed)
  L815-822  exit: short & !exitDone & 15:00 <= hm < 18:00 => ExitShort, ledger books this
            bar's Close (first bar >= 15:00; EXIT-SLIP if hm > 15:00).  NEVER GATED.
  L825-831  last bar of session still short => FLATTEN-FAILSAFE at the session close.

CERT BARS (spec verbatim): decision-series agreement vs FT1 must be 100.000% on event days
AND zero phantom entries on non-event days.  Additionally asserted here: entry/exit fills
agree with FT1 < 1e-9 pt; zero overnight carries; zero flatten-fail-safe invocations.

DATA SEAL: substrate max session <= 2026-07-31 asserted.  Cert table -> out/cert_table.txt.
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
FT1_TRADES = os.path.join(RUN_DIR, "out", "ft1_trades.csv")
OUT = os.path.join(RUN_DIR, "out")
os.makedirs(OUT, exist_ok=True)

SEAL = pd.Timestamp("2026-07-31").date()
TOL = 1e-9

LINES = []
def say(s=""):
    print(s)
    LINES.append(s)

# ---------------------------------------------------------------- substrate, bar-by-bar
bars = pd.read_parquet(ZB_PARQUET)
ts = pd.to_datetime(bars["time"])
hour = ts.dt.hour.to_numpy()
hm = (hour * 100 + ts.dt.minute).to_numpy()
close = bars["close"].to_numpy()
sessd = (ts.dt.normalize() + pd.to_timedelta((hour >= 18).astype(int), unit="D")).dt.date.to_numpy()
n = len(bars)
assert sessd.max() <= SEAL, f"SEAL VIOLATION: {sessd.max()}"
# IsLastBarOfSession mirror: the last row of each session block (substrate is time-ordered)
is_last = np.empty(n, dtype=bool)
is_last[:-1] = sessd[1:] != sessd[:-1]
is_last[-1] = True
# EARLY-CLOSE mirror (L744-759): template session end proxied by the session's last printed
# bar; a session whose last bar is stamped before 15:00 cannot provide the 15:00 exit.
last_hm_of_sess = {}
for i in np.flatnonzero(is_last):
    last_hm_of_sess[sessd[i]] = int(hm[i])

# ---------------------------------------------------------------- calendar (deployment CSV = NFP|CPI)
nfp = set(pd.to_datetime(pd.read_csv(NFP_CSV)["session_date"]).dt.date)
cpi = set(pd.to_datetime(pd.read_csv(CPI_CSV)["session_date"]).dt.date)
cal = nfp | cpi                                     # calLoaded = True (L400)

# ---------------------------------------------------------------- the state machine (mirror)
NaN = float("nan")
sess_rows = {}          # session -> decision record
cur = None              # current session date
event_day = False
px0830 = NaN
px0845 = NaN
armed = False
entry_done = False
exit_done = False
stand_aside = False
my_qty = 0
entry_px = NaN
n_overnight_carry = 0
n_flatten_failsafe = 0
n_exit_slip = 0
n_early_close_standaside = 0
early_close = False

def close_session(d):
    sess_rows[d] = dict(session=d, event=event_day, armed=armed, stand_aside=stand_aside,
                        entered=(not np.isnan(entry_px)), entry_px=entry_px,
                        exit_px=exit_px, exit_hm=exit_hm)

exit_px = NaN
exit_hm = -1

for i in range(n):
    d = sessd[i]
    if d != cur:                                    # L717 session change
        if cur is not None:
            close_session(cur)
        if my_qty < 0:                              # L719-725 OVERNIGHT-CARRY fail-safe
            n_overnight_carry += 1
            my_qty = 0
        cur = d
        event_day = d in cal                        # L738 (calLoaded=True historically)
        early_close = last_hm_of_sess.get(d, 0) < 1500   # L744-759 EARLY-CLOSE guard (proxy)
        px0830 = NaN; px0845 = NaN
        armed = False; entry_done = False; exit_done = False; stand_aside = False
        entry_px = NaN; exit_px = NaN; exit_hm = -1
        if event_day and early_close:
            stand_aside = True
            n_early_close_standaside += 1

    h = hm[i]; c = close[i]
    if h == 830:                                    # L766
        px0830 = c
    if h == 845:                                    # L767-781
        px0845 = c
        if event_day and not early_close:
            if np.isnan(px0830):
                stand_aside = True                  # L775 NO-0830-BAR
            elif px0845 - px0830 < 0:
                armed = True                        # L779 SIGNAL
    if event_day and h > 845 and np.isnan(px0845) and not armed and not stand_aside:
        stand_aside = True                          # L788 NO-0845-BAR

    if armed and not entry_done:                    # L792-811
        if h == 846:
            entry_done = True
            # EntriesAllowed() is a constant true historically (M1, L174-184)
            entry_px = c                            # L801-803 ledger: 08:46 close
            my_qty = -1                             # sign only; K scales, decisions don't
        elif h > 846:
            entry_done = True; armed = False        # L806-810 NO-0846-BAR: signal expires
            stand_aside = True

    if my_qty < 0 and not exit_done and 1500 <= h < 1800:   # L815-822
        if h > 1500:
            n_exit_slip += 1
        exit_px = c; exit_hm = int(h)               # ledger: this bar's close
        my_qty = 0; exit_done = True

    if is_last[i] and my_qty < 0:                   # L825-831 FLATTEN-FAILSAFE
        n_flatten_failsafe += 1
        exit_px = c; exit_hm = int(h)
        my_qty = 0; exit_done = True

close_session(cur)
sm = pd.DataFrame(sess_rows.values())
sm.to_csv(os.path.join(OUT, "ft4b_sessions.csv"), index=False)

# ---------------------------------------------------------------- compare vs FT1
ft1 = pd.read_csv(FT1_TRADES)
ft1_dates = set(pd.to_datetime(ft1["session_date"]).dt.date)
ft1_by_date = {pd.to_datetime(r.session_date).date(): r for r in ft1.itertuples()}

ev = sm[sm["event"]]
nev = sm[~sm["event"]]
n_sessions = len(sm)
n_event = len(ev)

agree = 0
mism = []
max_dentry = 0.0
max_dexit = 0.0
for r in ev.itertuples():
    should = r.session in ft1_dates
    if bool(r.entered) != should:
        mism.append((r.session, "entered=%s vs ft1=%s" % (r.entered, should)))
        continue
    if should:
        f = ft1_by_date[r.session]
        de = abs(r.entry_px - f.entry_0846_px)
        dx = abs(r.exit_px - f.exit_1500_px)
        max_dentry = max(max_dentry, de)
        max_dexit = max(max_dexit, dx)
        if de >= TOL or dx >= TOL:
            mism.append((r.session, "fill diff entry=%g exit=%g" % (de, dx)))
            continue
    agree += 1
agree_pct = 100.0 * agree / n_event if n_event else float("nan")

phantom = int(nev["entered"].sum())
n_entries = int(sm["entered"].sum())
exits_at_1500 = int((sm.loc[sm["entered"], "exit_hm"] == 1500).sum())

say("=" * 106)
say("FT4b -- OFFLINE CERTIFICATION of ZbMacroResponse_v1.cs  (G3_ZBMACRO_FT_20260906, G00083)")
say("Python state-machine mirror of the .cs OnBarUpdate flow (line refs in src/ft4b_cert.py header),")
say("replayed bar-by-bar over the substrate under Strategy Analyzer (historical) semantics.")
say(f"substrate: {os.path.relpath(ZB_PARQUET, REPO)}  sessions={n_sessions} "
    f"({sm['session'].min()} .. {sm['session'].max()})  seal OK (<= {SEAL})")
say(f"calendar: NFP|CPI union; event sessions in window = {n_event}; non-event sessions = {len(nev)}")
say(f"replay: entries={n_entries}  exits at the exact 15:00 bar={exits_at_1500}  "
    f"exit-slips={n_exit_slip}  flatten-failsafes={n_flatten_failsafe}  overnight-carries={n_overnight_carry}")
say(f"early-close stand-asides on event days (fail-closed guard, L744-759): {n_early_close_standaside}")
say("")
say(f"{'GATE':<24}{'SPEC':<50}{'OBSERVED':<38}{'PASS/FAIL':>9}")
say("-" * 121)
g1 = (n_event > 0 and agree == n_event)
say(f"{'C1_event_agreement':<24}{'decision agreement vs FT1 = 100.000% (event days)':<50}"
    f"{'%d/%d = %.3f%%' % (agree, n_event, agree_pct):<38}{'PASS' if g1 else 'FAIL':>9}")
g2 = (phantom == 0)
say(f"{'C2_phantom_entries':<24}{'zero entries on non-event days':<50}"
    f"{'%d phantom on %d non-event sessions' % (phantom, len(nev)):<38}{'PASS' if g2 else 'FAIL':>9}")
g3 = (n_entries == len(ft1_dates) == 40 and max_dentry < TOL and max_dexit < TOL)
say(f"{'C3_fill_identity':<24}{'40 entries; entry+exit fills vs FT1 < 1e-9 pt':<50}"
    f"{'n=%d dEntry=%.3g dExit=%.3g' % (n_entries, max_dentry, max_dexit):<38}{'PASS' if g3 else 'FAIL':>9}")
g4 = (n_overnight_carry == 0 and n_flatten_failsafe == 0)
say(f"{'C4_no_overnight':<24}{'zero overnight carries / flatten fail-safes':<50}"
    f"{'carry=%d failsafe=%d' % (n_overnight_carry, n_flatten_failsafe):<38}{'PASS' if g4 else 'FAIL':>9}")
say("-" * 121)
if mism:
    say("MISMATCHES (all):")
    for d, why in mism:
        say(f"  {d}  {why}")
cert_pass = bool(g1 and g2 and g3 and g4)
say(f"FT4b VERDICT (mechanical): {'PASS -- 100.000% event-day agreement, zero phantoms' if cert_pass else 'FAIL'}")
say("SCOPE: this certifies the DECISION LOGIC offline.  NT8 compile + Strategy Analyzer parity on the")
say("real platform remain DEFERRED to the >= 2026-09-21 window (spec FT4).  EVIDENCE: DISCOVERY_CONSUMED.")
say("=" * 106)

with open(os.path.join(OUT, "cert_table.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(LINES) + "\n")

sys.exit(0 if cert_pass else 1)
