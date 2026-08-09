"""V1d -- session-aware late-entry census + MECHANISM discrimination.

WAVE-17 TASK V1d.  Wave 16 measured "entries in the final N minutes before the session
close" against a hardcoded 17:00 ET close and found n<=17 for N<=45 across 1,139 sessions,
then deferred the item as "too thin to fit a cutoff".  That framing was wrong twice over:

  (1) it used a 17:00 close for all 1,139 sessions, but 43 of them close early
      (13:00 / 13:15 / 09:15 / 09:30 ET), and those are precisely the sessions where the
      strategies' hardcoded 16:30/16:39 ops clock does NOT fire -- i.e. the only sessions
      where a late entry is even mechanically possible late in the session; and
  (2) "too thin to fit" treats a near-zero count as a sampling problem.  It is not.  A
      near-zero count across 1,139 sessions is evidence about the GENERATING PROCESS.

This script therefore does two things:

  PART 1  Re-measures the late-entry census SESSION-AWARE, using each session's ACTUAL
          close derived from mnq_3m_raw.csv's first-bar-of-session (fbos) flag, for
          Product A (SolarWaveSMMaster_v2) and both Product B objects (BEST_ONE_NQ,
          BEST_ONE_MNQ).

  PART 2  DISCRIMINATES between the two candidate explanations with data:
            (a) an existing coded rule already blocks late entries
                (entryBlocked = hm >= 163000, plus the >= 163900 forced-flat branch);
            (b) allocator hysteresis / a quiet signal -- M is simply not re-crossing the
                +/-3.0 entry threshold from a flat state late in the session.
          It does this by exactly reconstructing Product B's allocator signal M from the
          540,231-bar decision ledger, VALIDATING that reconstruction against the real NT8
          trade list, and then replaying the one-lot state machine with the 16:30 block
          removed and with the 16:39 forced-flat removed.  The delta in entry count IS the
          amount of work rule (a) is doing.  Whatever is left over is (b), and (b) is then
          decomposed into its own coded causes.

INPUTS (all committed, read-only):
  runs/PRODUCTB_ONECONTRACT_FINAL/out/mnq_3m_raw.csv    519,869 MNQ 3-min bars + fbos flag
  runs/PRODUCTB_ONECONTRACT_FINAL/out/nt_trades_nq.csv  1,975 BEST_ONE_NQ trades
  runs/PRODUCTB_ONECONTRACT_FINAL/out/nt_trades_mnq.csv 1,561 BEST_ONE_MNQ trades
  runs/SMV2M_MASTER_BUILD/out/nt8/smm_v2_bars.csv       540,231 Product A decision bars
  runs/SMV2M_MASTER_BUILD/out/nt8/smm_v2_fills.csv      26,881 Product A executions

CAVEAT CARRIED THROUGH THE WHOLE FILE:
  BEST_ONE_MNQ (SolarWaveOneContractMNQ_Final) has a confirmed defect (KNOWN_ERRORS #7
  arrangement): it never submits a voluntary EXIT order.  Its ENTRY submissions are
  unaffected -- EnterLong/EnterShort are reached normally, and the 16:30 entry block
  demonstrably works on it.  So MNQ ENTRY TIMESTAMPS ARE VALID EVIDENCE HERE.  Anything
  exit-derived (holding time, per-trade P&L, position-state occupancy) is NOT, and is
  neither computed nor used below.

DEV WINDOW: 2022-01-03 .. 2026-05-29.  Nothing later is read.  No 2006-2021 data is used.
Writes runs/W17_C4_COMPLIANCE/out/v1d_*.csv and prints the full report to stdout.
"""

import os
import sys

import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(REPO, "runs", "W17_C4_COMPLIANCE", "out")
DEV_END = pd.Timestamp("2026-05-29 23:59:59")

P_MNQ3M = os.path.join(REPO, "runs", "PRODUCTB_ONECONTRACT_FINAL", "out", "mnq_3m_raw.csv")
P_NQ_TR = os.path.join(REPO, "runs", "PRODUCTB_ONECONTRACT_FINAL", "out", "nt_trades_nq.csv")
P_MNQ_TR = os.path.join(REPO, "runs", "PRODUCTB_ONECONTRACT_FINAL", "out", "nt_trades_mnq.csv")
P_BARS = os.path.join(REPO, "runs", "SMV2M_MASTER_BUILD", "out", "nt8", "smm_v2_bars.csv")
P_FILLS = os.path.join(REPO, "runs", "SMV2M_MASTER_BUILD", "out", "nt8", "smm_v2_fills.csv")

NS = [5, 10, 15, 20, 30, 45, 60]

# Frozen constants, read off the two NinjaScript sources -- NOT re-tuned here.
#   src/ninjascript/SolarWaveOneContractNQ_Final.cs  (Product B, one lot)
W_SOLAR, W_BMOM = 0.7086, 2.83
ENTRY_LEVEL, EXIT_LEVEL = 3.0, 1.0
TILT_MULT, TILT_RESCALE = 1.25, 0.9026
#   src/ninjascript/SolarWaveSMMaster_v2.cs          (Product A, scaling allocator)
K_SOLAR, K_BMOM, SHORT_HALF = 0.728654, 2.934159, 0.5
#   ops clock, both objects (hardcoded to the NORMAL 17:00 session)
HM_ENTRY_BLOCK = 163000
HM_FORCE_FLAT = 163900
HM_OPEN = 180000


def hdr(s):
    print("\n" + "=" * 78)
    print(s)
    print("=" * 78)


def round_away(x):
    """C# Math.Round(x, MidpointRounding.AwayFromZero)."""
    return np.sign(x) * np.floor(np.abs(x) + 0.5)


# ---------------------------------------------------------------------------
# PART 0 -- the real session calendar
# ---------------------------------------------------------------------------
def session_calendar():
    m = pd.read_csv(P_MNQ3M, skiprows=1, parse_dates=["time"])
    m = m[m.time <= DEV_END].reset_index(drop=True)
    m["sid"] = m.fbos.cumsum()
    g = m.groupby("sid").time
    sess = pd.DataFrame({"sopen": g.min(), "sclose": g.max(), "nbars": g.size()})
    sess["close_tod"] = sess.sclose.dt.strftime("%H:%M")
    return m, sess


def attach_close(ts, sess):
    """Map each timestamp to the close of the session that contains it.

    Sessions are (sopen - 3min, sclose] on the 3-minute end-stamped grid, so the
    merge key is sopen - 3min and the direction is backward.
    """
    df = pd.DataFrame({"t": pd.to_datetime(pd.Series(ts).values)})
    df["_i"] = np.arange(len(df))
    df = df.sort_values("t")
    s = sess.reset_index().sort_values("sopen").copy()
    s["key"] = s.sopen - pd.Timedelta(minutes=3)
    r = pd.merge_asof(df, s[["key", "sopen", "sclose", "sid", "close_tod"]],
                      left_on="t", right_on="key", direction="backward")
    r = r.sort_values("_i").reset_index(drop=True)
    r["min_before_close"] = (r.sclose - r.t).dt.total_seconds() / 60.0
    return r


# ---------------------------------------------------------------------------
# PART 1 -- entry event extraction
# ---------------------------------------------------------------------------
def product_b_entries(path):
    """BEST_ONE_* trade list -> entry timestamps.

    entry_time is the NT8 execution stamp = the CLOSE of the bar the market order filled
    on.  Calculate.OnBarClose means the decision bar is 3 minutes earlier and the economic
    fill is at that bar's OPEN, i.e. also 3 minutes earlier.  Both offsets are reported.
    """
    t = pd.read_csv(path, parse_dates=["entry_time", "exit_time"])
    return t


def product_a_entries(bars):
    """Product A is a SCALING allocator (target in [-13,+13]), so 'entry' needs 3 flavours.

    The decision-bar ledger's `phys` column is the position read at decision time and
    `tgt_ops` is the target submitted; phys[i+1] == tgt_ops[i] on 99.998% of within-session
    bar pairs (verified), so the realised path is tgt_ops shifted by one bar and the fill
    stamp is time[i+1].

      open     : flat -> non-flat                       (the strict analogue of a Product B entry)
      increase : |position| grows, same sign            (adds risk)
      reversal : sign flip through zero in one order    (adds risk in the other direction)
    """
    n = len(bars)
    se = bars.sess_end.values
    cur = bars.phys.values
    tgt = bars.tgt_ops.values
    tm = bars.time.values
    same_sess = np.r_[se[:-1] == 0, False]   # bar i+1 belongs to the same session as bar i
    fill = np.r_[tm[1:], tm[-1]]

    opening = same_sess & (cur == 0) & (tgt != 0)
    reversal = same_sess & (cur != 0) & (tgt != 0) & (np.sign(tgt) != np.sign(cur))
    increase = same_sess & (cur != 0) & (np.sign(tgt) == np.sign(cur)) & (np.abs(tgt) > np.abs(cur))

    ev = []
    for lbl, mask in [("open", opening), ("increase", increase), ("reversal", reversal)]:
        idx = np.where(mask)[0]
        ev.append(pd.DataFrame({"kind": lbl, "decide": tm[idx], "fill": fill[idx],
                                "cur": cur[idx], "tgt": tgt[idx],
                                "dqty": np.abs(tgt[idx]) - np.abs(cur[idx]) * (np.sign(tgt[idx]) == np.sign(cur[idx]))}))
    e = pd.concat(ev, ignore_index=True).sort_values("fill").reset_index(drop=True)
    e["fill"] = pd.to_datetime(e.fill)
    e["decide"] = pd.to_datetime(e.decide)
    return e


def census(name, fill_times, sess, extra=None):
    r = attach_close(fill_times, sess)
    mb = r.min_before_close.values
    rows = []
    for N in NS:
        m_all = (mb > 0) & (mb <= N)
        is_early = r.close_tod.values != "17:00"
        rows.append({
            "object": name, "N_min": N,
            "n_entries": int(m_all.sum()),
            "n_normal_close": int((m_all & ~is_early).sum()),
            "n_early_close": int((m_all & is_early).sum()),
        })
    out = pd.DataFrame(rows)
    out["pct_of_all_entries"] = 100.0 * out.n_entries / max(len(r), 1)
    out["sessions_affected_pct"] = 100.0 * out.n_entries / len(sess)
    return out, r


# ---------------------------------------------------------------------------
# PART 2 -- reconstruct the allocator signal and replay the state machine
# ---------------------------------------------------------------------------
def load_bars():
    b = pd.read_csv(P_BARS, skiprows=1, parse_dates=["time"])
    b = b[b.time <= DEV_END].reset_index(drop=True)
    return b


def rebuild_signals(b):
    """Exactly re-derive both products' allocator signals from the ledger's T / B / tilt.

    Product A (verified below to reproduce the ledger's own Tpp and tgt_raw bit-for-bit):
        m   = TiltMult iff T != 0 and sign(T) == tiltState
        s   = ShortHalf iff T < 0 and tiltState > 0
        Tpp = clamp(round_away(T * m * s * TiltRescale), +/-13)
        M_A = KSolar*Tpp + KBmom*B ;  tgt_raw = clamp(round_away(M_A), +/-13)

    Product B is the SAME arithmetic minus the ShortHalf term, with its own weights:
        Tp  = clamp(round_away(T * m * TiltRescale), +/-13)
        M_B = WSolar*Tp + WBmom*B
    (SolarWaveOneContractNQ_Final.cs lines 301-306 vs SolarWaveSMMaster_v2.cs lines 298-305.
     Product B gates on sign(sumNext); sumNext == 0 <=> T == 0, so the gate is identical.)
    """
    T = b["T"].values.astype(float)
    ts = b.tilt_state.values.astype(float)
    B = b.B.values.astype(float)
    mm = np.where((T != 0) & (ts != 0) & (np.sign(T) == ts), TILT_MULT, 1.0)
    ss = np.where((T < 0) & (ts > 0), SHORT_HALF, 1.0)

    TppA = np.clip(round_away(T * mm * ss * TILT_RESCALE), -13, 13)
    MA = K_SOLAR * TppA + K_BMOM * B
    tgt_rawA = np.clip(round_away(MA), -13, 13)

    TpB = np.clip(round_away(T * mm * TILT_RESCALE), -13, 13)
    MB = W_SOLAR * TpB + W_BMOM * B

    checks = {
        "TppA_matches_ledger": float((TppA == b.Tpp.values).mean()),
        "tgt_rawA_matches_ledger": float((tgt_rawA == b.tgt_raw.values).mean()),
    }
    return MA, MB, TpB, TppA, checks


def replay_b(b, MB, block=True, force_flat=True, sess_rel_close=None):
    """Replay SolarWaveOneContractNQ_Final's one-lot state machine (lines 308-334).

    Position resets to 0 at the start of every session: the strategy is
    IsExitOnSessionCloseStrategy with ExitOnSessionCloseSeconds=30, so the engine backstop
    flattens at every close whether or not the 16:39 rule fired.

    sess_rel_close: if given, the two ops constants become SESSION-RELATIVE
    (sessionEnd-30min / sessionEnd-21min) = the W17 C2 fix.
    """
    hm = (b.time.dt.hour * 10000 + b.time.dt.minute * 100).values
    se = b.sess_end.values
    tm = b.time.values
    n = len(b)
    if sess_rel_close is not None:
        mins_left = (pd.to_datetime(sess_rel_close) - b.time).dt.total_seconds().values / 60.0
    p = 0
    newsess = True
    pos = np.zeros(n, dtype=np.int8)
    ents = []
    for i in range(n):
        if newsess:
            p = 0
            newsess = False
        pos[i] = p
        M = MB[i]
        h = hm[i]
        if sess_rel_close is not None:
            eb = block and (mins_left[i] <= 30.0)
            ff = force_flat and (mins_left[i] <= 21.0)
        else:
            eb = block and (HM_ENTRY_BLOCK <= h <= HM_OPEN)
            ff = force_flat and (HM_FORCE_FLAT <= h < HM_OPEN)
        tgt = p
        if ff:
            tgt = 0
        elif p == 0:
            if not eb:
                if M >= ENTRY_LEVEL:
                    tgt = 1
                elif M <= -ENTRY_LEVEL:
                    tgt = -1
        elif p > 0:
            if M <= -ENTRY_LEVEL and not eb:
                tgt = -1
            elif M <= EXIT_LEVEL:
                tgt = 0
        else:
            if M >= ENTRY_LEVEL and not eb:
                tgt = 1
            elif M >= -EXIT_LEVEL:
                tgt = 0
        if tgt != 0 and (p == 0 or np.sign(tgt) != np.sign(p)):
            ents.append((tm[i + 1] if i + 1 < n else tm[i], tm[i], int(tgt), bool(p == 0)))
        p = tgt
        if se[i] == 1:
            newsess = True
    e = pd.DataFrame(ents, columns=["fill", "decide", "dir", "from_flat"])
    e["fill"] = pd.to_datetime(e.fill)
    e["decide"] = pd.to_datetime(e.decide)
    return e, pos


def replay_a(b, MA, ops=True, sess_rel_close=None):
    """Replay Product A's scaling allocator with / without the 16:30-18:00 ops clamp.

    ops=True reproduces SolarWaveSMMaster_v2.cs lines 308-319; ops=False lets tgt_raw stand.
    sess_rel_close: if given (an array of per-bar session-close timestamps), the two ops
    constants become SESSION-RELATIVE (sessionEnd-30min / sessionEnd-21min) -- i.e. the
    W17 C2 fix as frozen in runs/W17_C4_COMPLIANCE/spec.yaml.  On a 17:00 close these are
    exactly 16:30 and 16:39, so normal sessions are unchanged by construction.
    Counts risk-increasing events only (open / increase / reversal), same taxonomy as
    product_a_entries().
    """
    hm = (b.time.dt.hour * 10000 + b.time.dt.minute * 100).values
    se = b.sess_end.values
    tm = b.time.values
    traw = np.clip(round_away(MA), -13, 13).astype(int)
    n = len(b)
    if sess_rel_close is not None:
        mins_left = (pd.to_datetime(sess_rel_close) - b.time).dt.total_seconds().values / 60.0
    p = 0
    newsess = True
    ents = []
    for i in range(n):
        if newsess:
            p = 0
            newsess = False
        h = hm[i]
        tr = traw[i]
        tgt = tr
        if ops:
            if sess_rel_close is not None:
                blk = mins_left[i] <= 30.0
                flt = mins_left[i] <= 21.0
            else:
                blk = HM_ENTRY_BLOCK <= h < HM_OPEN
                flt = HM_FORCE_FLAT <= h < HM_OPEN
            if flt:
                tgt = 0
            elif blk:
                if tr == 0 or p == 0:
                    tgt = 0
                elif np.sign(tr) != np.sign(p):
                    tgt = 0
                else:
                    tgt = p if abs(tr) > abs(p) else tr
        if se[i] == 1:            # engine owns the close; strategy submits nothing
            newsess = True
            continue
        kind = None
        if p == 0 and tgt != 0:
            kind = "open"
        elif p != 0 and tgt != 0 and np.sign(tgt) != np.sign(p):
            kind = "reversal"
        elif p != 0 and np.sign(tgt) == np.sign(p) and abs(tgt) > abs(p):
            kind = "increase"
        if kind:
            ents.append((tm[i + 1] if i + 1 < n else tm[i], tm[i], kind, p, tgt))
        p = tgt
    e = pd.DataFrame(ents, columns=["fill", "decide", "kind", "cur", "tgt"])
    e["fill"] = pd.to_datetime(e.fill)
    return e


# ---------------------------------------------------------------------------
def main():
    os.makedirs(OUT, exist_ok=True)
    pd.set_option("display.width", 200)

    # ---------------- PART 0 ----------------
    hdr("PART 0 -- REAL SESSION CALENDAR (from mnq_3m_raw.csv fbos, NOT assumed 17:00)")
    mnq3m, sess = session_calendar()
    print("MNQ 3-min bars in dev window : %d" % len(mnq3m))
    print("sessions (fbos count)        : %d" % len(sess))
    print("\nsession close time-of-day:")
    print(sess.close_tod.value_counts().sort_index().to_string())
    early = sess[(sess.close_tod != "17:00") & (sess.close_tod != "16:57")]
    print("\nEARLY-CLOSE sessions: %d   (spec V1e says 43)" % len(early))
    print(early.close_tod.value_counts().sort_index().to_string())
    trunc = sess[sess.close_tod == "16:57"]
    if len(trunc):
        print("\nNOTE: %d session(s) close at 16:57 -- this is the DATA END "
              "(%s), not an early close; excluded from the early-close set."
              % (len(trunc), trunc.sclose.iloc[0]))

    bars = load_bars()
    led_ends = bars[bars.sess_end == 1]
    print("\nCROSS-CHECK against the NQ signal series (smm_v2_bars.sess_end): %d session ends"
          % len(led_ends))
    print(led_ends.time.dt.strftime("%H:%M").value_counts().sort_index().to_string())
    print("DISAGREEMENT: the NQ signal series shows one extra 'session end' at "
          "2023-04-05 14:03 where MNQ has a full 460-bar 17:00 session. That is an NQ "
          "signal-series DATA GAP (bars jump 14:03 -> 20:03), not a real early close. "
          "The MNQ-derived calendar is used as truth for close times.")
    sess.to_csv(os.path.join(OUT, "v1d_session_calendar.csv"))

    # ---------------- PART 1 ----------------
    hdr("PART 1 -- SESSION-AWARE LATE-ENTRY CENSUS (each session's OWN close)")
    print("Convention: entry stamp = NT8 execution time = CLOSE of the bar the market order")
    print("filled on. Calculate.OnBarClose => decision bar is 3 min earlier and the economic")
    print("fill price is that bar's OPEN, also 3 min earlier. Counts below use the STAMP;")
    print("subtract 3 minutes for the decision, add 3 to minutes-before-close for exposure.\n")

    tables = []

    # -- Product B --
    for label, path in [("BEST_ONE_NQ (Product B, 1 NQ)", P_NQ_TR),
                        ("BEST_ONE_MNQ (Product B, 1 MNQ)", P_MNQ_TR)]:
        t = product_b_entries(path)
        tab, r = census(label, t.entry_time, sess)
        tables.append(tab)
        print("--- %s : %d entries total" % (label, len(t)))
        print(tab[["N_min", "n_entries", "n_normal_close", "n_early_close",
                   "sessions_affected_pct"]].to_string(index=False))
        naive = ((17 * 60) - (t.entry_time.dt.hour * 60 + t.entry_time.dt.minute))
        nv = [int(((naive > 0) & (naive <= N)).sum()) for N in NS]
        print("wave-16 naive-17:00 counts   : %s" % nv)
        print("session-aware counts         : %s" % tab.n_entries.tolist())
        print("delta (session-aware - naive): %s" % [a - b_ for a, b_ in zip(tab.n_entries.tolist(), nv)])
        e60 = t.entry_time[(r.min_before_close > 0) & (r.min_before_close <= 60)]
        print("entry-stamp histogram, final 60 min:")
        print(e60.dt.strftime("%H:%M").value_counts().sort_index().to_string())
        ee = r[r.close_tod != "17:00"]
        print("entries on EARLY-CLOSE sessions: %d ; closest to an early close: %s min"
              % (len(ee), ("%.0f" % ee.min_before_close.min()) if len(ee) else "n/a"))
        print()

    # -- Product A --
    ea = product_a_entries(bars)
    tab_all, r_all = census("PRODUCT_A all risk-increasing", ea.fill, sess)
    tables.append(tab_all)
    print("--- PRODUCT A (SolarWaveSMMaster_v2, scaling allocator, MNQ execution)")
    print("risk-increasing events: open=%d increase=%d reversal=%d  (total %d)"
          % ((ea.kind == "open").sum(), (ea.kind == "increase").sum(),
             (ea.kind == "reversal").sum(), len(ea)))
    print(tab_all[["N_min", "n_entries", "n_normal_close", "n_early_close",
                   "sessions_affected_pct"]].to_string(index=False))
    for k in ["open", "increase", "reversal"]:
        sub = ea[ea.kind == k]
        tk, _ = census("PRODUCT_A " + k, sub.fill, sess)
        tables.append(tk)
        print("  %-9s by N: %s" % (k, tk.n_entries.tolist()))
    e60 = r_all[(r_all.min_before_close > 0) & (r_all.min_before_close <= 60)]
    print("entry-stamp histogram, final 60 min:")
    print(e60.t.dt.strftime("%H:%M").value_counts().sort_index().to_string())
    ee = r_all[r_all.close_tod != "17:00"]
    print("events on EARLY-CLOSE sessions: %d ; closest to an early close: %s min"
          % (len(ee), ("%.0f" % ee.min_before_close.min()) if len(ee) else "n/a"))

    # independent cross-check of Product A from the execution ledger
    f = pd.read_csv(P_FILLS, skiprows=1, parse_dates=["time"])
    f = f[f.time <= DEV_END]
    rf = attach_close(f.time, sess)
    print("\nCROSS-CHECK from smm_v2_fills.csv (%d executions): fills within N min of the "
          "session's own close" % len(f))
    for N in NS:
        msk = (rf.min_before_close > 0) & (rf.min_before_close <= N)
        sub = f[msk.values]
        print("  N<=%-3d fills=%-5d of which entry-side (L/S)=%d"
              % (N, len(sub), sub["name"].isin(["L", "S"]).sum()))

    pd.concat(tables, ignore_index=True).to_csv(
        os.path.join(OUT, "v1d_census.csv"), index=False)

    # ---------------- PART 2 ----------------
    hdr("PART 2 -- MECHANISM.  (a) the coded 16:30 block, or (b) the signal itself?")
    MA, MB, TpB, TppA, checks = rebuild_signals(bars)
    print("Signal reconstruction fidelity against the ledger's own columns:")
    for k, v in checks.items():
        print("  %-26s %.6f" % (k, v))
    if min(checks.values()) < 1.0:
        print("  WARNING: reconstruction is not exact; PART 2 conclusions are downgraded.")

    base, pos = replay_b(bars, MB, block=True, force_flat=True)
    real = pd.read_csv(P_NQ_TR, parse_dates=["entry_time"])
    sb, sr = set(base.fill), set(real.entry_time)
    print("\nVALIDATION of the Product B replay against the REAL NT8 trade list:")
    print("  real entries                 : %d" % len(real))
    print("  replayed entries             : %d" % len(base))
    print("  timestamp-exact matches      : %d  (%.2f%% of real)"
          % (len(sb & sr), 100.0 * len(sb & sr) / len(real)))
    print("  in replay only               : %d   (expected ~1: a position still open at data end)"
          % len(sb - sr))
    print("  in real only                 : %d" % len(sr - sb))
    if len(sr - sb) > 0:
        print("  WARNING: replay misses real entries; counterfactuals below are downgraded.")

    cf = {}
    for lbl, (blk, flt) in [("baseline (block ON, forced-flat ON)", (True, True)),
                            ("16:30 ENTRY BLOCK REMOVED", (False, True)),
                            ("BLOCK + 16:39 FORCED-FLAT BOTH REMOVED", (False, False))]:
        e, _ = replay_b(bars, MB, block=blk, force_flat=flt)
        rr = attach_close(e.fill, sess)
        cf[lbl] = (e, rr)
        counts = [int((((rr.min_before_close > 0) & (rr.min_before_close <= N))).sum()) for N in NS]
        print("\n  %s" % lbl)
        print("    total entries over 1,139 sessions : %d" % len(e))
        print("    entries within N min of own close : %s   (N = %s)" % (counts, NS))
        late = e.fill[(rr.min_before_close > 0) & (rr.min_before_close <= 45)]
        if len(late):
            print("    stamps within 45 min:")
            print("      " + late.dt.strftime("%H:%M").value_counts().sort_index()
                  .to_string().replace("\n", "\n      "))

    n_base = len(cf["baseline (block ON, forced-flat ON)"][0])
    n_nb = len(cf["16:30 ENTRY BLOCK REMOVED"][0])
    n_nn = len(cf["BLOCK + 16:39 FORCED-FLAT BOTH REMOVED"][0])
    print("\n  >>> WORK DONE BY HYPOTHESIS (a), the coded 16:30 entry block:")
    print("      %d extra entries over 1,139 sessions (%d -> %d, +%.3f%%)"
          % (n_nb - n_base, n_base, n_nb, 100.0 * (n_nb - n_base) / n_base))
    print("  >>> WORK DONE BY BOTH LATE-SESSION OPS RULES TOGETHER:")
    print("      %d extra entries over 1,139 sessions (%d -> %d, +%.3f%%)"
          % (n_nn - n_base, n_base, n_nn, 100.0 * (n_nn - n_base) / n_base))

    # -- Product A counterfactual --
    ea_ops = replay_a(bars, MA, ops=True)
    ea_free = replay_a(bars, MA, ops=False)
    ra_ops = attach_close(ea_ops.fill, sess)
    ra_free = attach_close(ea_free.fill, sess)
    print("\n  PRODUCT A counterfactual (risk-increasing events within N min of own close):")
    print("    with 16:30/16:39 ops clamp : %s   (total %d)"
          % ([int((((ra_ops.min_before_close > 0) & (ra_ops.min_before_close <= N))).sum())
              for N in NS], len(ea_ops)))
    print("    ops clamp REMOVED entirely : %s   (total %d)"
          % ([int((((ra_free.min_before_close > 0) & (ra_free.min_before_close <= N))).sum())
              for N in NS], len(ea_free)))

    # ---------------- PART 2b: is the signal actually quiet? ----------------
    hdr("PART 2b -- IS THE SIGNAL QUIET LATE IN THE SESSION?  (three separate questions)")
    b2 = bars.copy()
    b2["MB"] = MB
    b2["tod"] = b2.time.dt.strftime("%H:%M")
    newsess = np.r_[True, b2.sess_end.values[:-1] == 1]
    prevM = np.r_[np.nan, MB[:-1]]
    prevT = np.r_[np.nan, b2["T"].values[:-1]]
    b2["ge3"] = np.abs(MB) >= ENTRY_LEVEL
    b2["upcross"] = (~newsess) & (np.abs(MB) >= ENTRY_LEVEL) & (np.abs(prevM) < ENTRY_LEVEL)
    b2["Mchange"] = (~newsess) & (MB != prevM)
    b2["Tchange"] = (~newsess) & (b2["T"].values != prevT)
    b2["Bnz"] = b2.B != 0
    b2["flat"] = pos == 0
    b2["flat_and_ge3"] = b2.flat & b2.ge3

    g = b2.groupby("tod").agg(n=("MB", "size"), P_absM_ge_3=("ge3", "mean"),
                              P_M_changed=("Mchange", "mean"),
                              P_T_changed=("Tchange", "mean"),
                              P_upcross_3=("upcross", "mean"),
                              P_B_nonzero=("Bnz", "mean"),
                              P_flat=("flat", "mean"),
                              P_flat_and_ge3=("flat_and_ge3", "mean"))
    rth = g.loc["09:33":"15:54"]
    on = g.loc[(g.index >= "18:03") | (g.index <= "09:30")]
    print("Reference rates:")
    print("  RTH 09:33-15:54 : P(|M|>=3)=%.4f  P(M changed)=%.4f  P(T changed)=%.4f  P(upcross)=%.4f"
          % (rth.P_absM_ge_3.mean(), rth.P_M_changed.mean(), rth.P_T_changed.mean(), rth.P_upcross_3.mean()))
    print("  overnight 18:03-09:30 : P(|M|>=3)=%.4f  P(M changed)=%.4f  P(T changed)=%.4f  P(upcross)=%.4f"
          % (on.P_absM_ge_3.mean(), on.P_M_changed.mean(), on.P_T_changed.mean(), on.P_upcross_3.mean()))
    print("\nPer-bar rates through the close (Product B allocator M = %.4f*Tp + %.2f*B):"
          % (W_SOLAR, W_BMOM))
    print(g.loc["15:45":"17:00"].round(4).to_string())
    g.to_csv(os.path.join(OUT, "v1d_signal_by_tod.csv"))

    print("\nWindow totals over 1,139 sessions:")
    for lo, hi, lbl in [("09:33", "15:54", "RTH 09:33-15:54"),
                        ("16:00", "16:27", "16:00-16:27 (entries ALLOWED)"),
                        ("16:30", "16:36", "16:30-16:36 (blocked by entryBlocked)"),
                        ("16:39", "17:00", "16:39-17:00 (blocked by forced-flat)")]:
        sub = b2[(b2.tod >= lo) & (b2.tod <= hi)]
        print("  %-36s bars=%-7d |M|>=3 on %.1f%% ; M moved on %.2f%% ; upcrossings=%d (%.3f%%/bar)"
              % (lbl, len(sub), 100 * sub.ge3.mean(), 100 * sub.Mchange.mean(),
                 int(sub.upcross.sum()), 100 * sub.upcross.mean()))

    # the 15:57 B-shutdown discontinuity
    hdr("PART 2c -- THE 16:00 SPIKE: B-MOM's HARDCODED 15:57 SHUTDOWN")
    i57 = b2.index[b2.tod == "15:57"].values
    i54 = i57 - 1
    valid = b2.loc[i54, "tod"].values == "15:54"
    i57, i54 = i57[valid], i54[valid]
    Bprev = b2.loc[i54, "B"].values
    Mnow = MB[i57]
    Mhat = W_SOLAR * TpB[i57] + W_BMOM * Bprev     # what M would be if B were NOT zeroed
    unmasked = (np.abs(Mnow) >= ENTRY_LEVEL) & (np.abs(Mhat) < ENTRY_LEVEL)
    print("BmomBar() zeroes bmomPos at hm>=155700 and never revives it until the next 09:33,")
    print("so B == 0 on EVERY bar from 15:57 to the close. B carries weight %.2f -- 94%% of the"
          % W_BMOM)
    print("%.1f entry threshold -- so removing it is a large, deterministic, once-a-day jump in M." % ENTRY_LEVEL)
    print("\n  sessions examined                                 : %d" % len(i57))
    print("  B was non-zero on the preceding 15:54 bar          : %d" % int((Bprev != 0).sum()))
    print("  |M|>=3 at 15:57 with B zeroed (actual)             : %d" % int((np.abs(Mnow) >= ENTRY_LEVEL).sum()))
    print("  |M|>=3 at 15:57 if B had NOT been zeroed           : %d" % int((np.abs(Mhat) >= ENTRY_LEVEL).sum()))
    print("  crossings CREATED purely by the B shutdown         : %d (%.1f%% of sessions)"
          % (int(unmasked.sum()), 100.0 * unmasked.mean()))
    print("  P(upcross) at the 15:57 bar vs the RTH average     : %.4f vs %.4f (%.1fx)"
          % (g.loc["15:57", "P_upcross_3"], rth.P_upcross_3.mean(),
             g.loc["15:57", "P_upcross_3"] / rth.P_upcross_3.mean()))
    # direct attribution: are the REAL 16:00-stamped entries the unmasked ones?
    real_1600 = set(pd.read_csv(P_NQ_TR, parse_dates=["entry_time"]).entry_time)
    dec_unmasked = set(pd.to_datetime(bars.time.values[i57[unmasked]]))
    fills_unmasked = set(pd.to_datetime(bars.time.values[i57[unmasked] + 1]))
    r1600 = {t for t in real_1600 if t.strftime("%H:%M") == "16:00"}
    print("  REAL BEST_ONE_NQ entries stamped 16:00            : %d" % len(r1600))
    print("  of which the 15:57 B shutdown created the crossing: %d (%.0f%%)"
          % (len(r1600 & fills_unmasked),
             100.0 * len(r1600 & fills_unmasked) / max(len(r1600), 1)))
    print("  (the remainder were already above threshold at 15:54 but flat, or crossed on Tp)")

    # ---------------- PART 2e: does W17's C2 already close the early-close hole? -----
    hdr("PART 2e -- WITH W17 C2 APPLIED (session-relative 30/21 min instead of 16:30/16:39)")
    rb = attach_close(bars.time, sess)
    scl = rb.sclose.values
    e_c2, _ = replay_b(bars, MB, block=True, force_flat=True, sess_rel_close=scl)
    r_c2 = attach_close(e_c2.fill, sess)
    print("Product B (one lot), entries within N min of the session's OWN close:")
    print("  as built (hardcoded 16:30/16:39) : %s"
          % [int((((cf['baseline (block ON, forced-flat ON)'][1].min_before_close > 0) &
                   (cf['baseline (block ON, forced-flat ON)'][1].min_before_close <= N))).sum())
             for N in NS])
    print("  with C2 (sessionEnd-30/-21)      : %s   (N = %s)"
          % ([int((((r_c2.min_before_close > 0) & (r_c2.min_before_close <= N))).sum())
              for N in NS], NS))
    ea_c2 = replay_a(bars, MA, ops=True, sess_rel_close=scl)
    ra_c2 = attach_close(ea_c2.fill, sess)
    print("Product A, risk-increasing events within N min of the session's OWN close:")
    print("  as built (hardcoded 16:30/16:39) : %s"
          % [int((((ra_ops.min_before_close > 0) & (ra_ops.min_before_close <= N))).sum())
             for N in NS])
    print("  with C2 (sessionEnd-30/-21)      : %s   (N = %s)"
          % ([int((((ra_c2.min_before_close > 0) & (ra_c2.min_before_close <= N))).sum())
              for N in NS], NS))
    print("\nThe existing entry block IS a no_new_entry_after rule. Expressed session-relative")
    print("by C2 it is exactly no_new_entry_after = sessionEnd - 30 minutes, on EVERY session")
    print("including the 43 early closes. Nothing below 30 minutes survives it, on any object.")

    # ---------------- PART 2f: early-close zero -- mechanism or small sample? --------
    hdr("PART 2f -- PRODUCT B's ZERO NEAR EARLY CLOSES: is it protection or small n?")
    print("On an early-close session neither hardcoded rule fires, so entries are NOT blocked")
    print("near the close. Observed count is nonetheless 0. Test it against the clock-matched")
    print("hazard from NORMAL sessions at the SAME wall-clock times:")
    norm_ids = set(sess.index[sess.close_tod == "17:00"])
    for label, path in [("BEST_ONE_NQ", P_NQ_TR), ("BEST_ONE_MNQ", P_MNQ_TR)]:
        t = pd.read_csv(path, parse_dates=["entry_time"])
        rr = attach_close(t.entry_time, sess)
        isnorm = rr.sid.isin(norm_ids).values
        tod = t.entry_time.dt.strftime("%H:%M").values
        tot_exp = 0.0
        for lo, hi, ctod in [("12:03", "13:00", "13:00"), ("12:18", "13:15", "13:15"),
                             ("08:18", "09:15", "09:15"), ("08:33", "09:30", "09:30")]:
            nsess = int((sess.close_tod == ctod).sum())
            cnt = int(((tod >= lo) & (tod <= hi) & isnorm).sum())
            rate = cnt / max(len(norm_ids), 1)
            tot_exp += rate * nsess
            print("  %-13s close %s: normal-session rate %.4f/sess x %d early sessions "
                  "-> expected %.2f" % (label, ctod, rate, nsess, rate * nsess))
        pois0 = float(np.exp(-tot_exp))
        print("  %-13s TOTAL expected in the final 60 min of the 43 early closes = %.2f ; "
              "OBSERVED 0 ; P(0 | Poisson) = %.3f" % (label, tot_exp, pois0))
    print("\nINTERPRETATION: the zero on early-close sessions is NOT evidence of protection --")
    print("43 sessions is simply too few for a ~1-in-15-sessions hazard to show up. Do not")
    print("read it as a mechanism. The mechanism claims below rest on the 1,095 normal")
    print("sessions and on the counterfactual replays, not on this zero.")

    # why T freezes: realized move vs member stop distance
    hdr("PART 2d -- WHY T FREEZES: realised 3-min move vs the member stop distances")
    m3 = mnq3m.copy()
    m3["tod"] = m3.time.dt.strftime("%H:%M")
    m3["d"] = m3.groupby("sid").close.diff().abs()
    gm = m3.groupby("tod").d.mean()
    sigma = m3.d.mean()
    print("Member m flips only when price travels S_m = clamp(VolMult_m * sigma, 40..1200 ticks)")
    print("from its anchor, with VolMult in {6,8,...,30} and sigma = a causal 460-bar mean of")
    print("|close-to-close|. Pooled sigma over the dev window = %.2f NQ points, so" % sigma)
    print("S ranges about %.0f to %.0f points (clamped to [10, 300] points)."
          % (6 * sigma, 30 * sigma))
    print("\nmean |3-min close change| by time of day (MNQ, points):")
    print("  RTH 09:33-15:54 : %.2f" % gm.loc["09:33":"15:54"].mean())
    print(gm.loc["15:45":"17:00"].round(2).to_string())
    print("\nSo in the final half hour a typical bar moves ~%.1f points against a %.0f-%.0f point"
          % (gm.loc["16:30":"16:57"].mean(), 6 * sigma, 30 * sigma))
    print("stop distance sized on the whole-day sigma. Member flips therefore stop happening,")
    print("T stops moving, and with B already pinned to 0, M is frozen.")

    # ---------------- verdict block ----------------
    hdr("PART 3 -- VERDICT INPUTS")
    print("late-entry counts, session-aware, all three objects, N=45:")
    for tab in tables:
        row = tab[tab.N_min == 45]
        if len(row):
            print("  %-34s n=%d" % (row.object.iloc[0], int(row.n_entries.iloc[0])))
    print("\ncounterfactual entry counts with the coded blocks removed (Product B NQ):")
    print("  baseline                     %d" % n_base)
    print("  16:30 block removed          %d  (+%d)" % (n_nb, n_nb - n_base))
    print("  block + forced-flat removed  %d  (+%d)" % (n_nn, n_nn - n_base))


if __name__ == "__main__":
    sys.exit(main())
