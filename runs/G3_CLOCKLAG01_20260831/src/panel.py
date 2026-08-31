"""G3_CLOCKLAG01 - RTH 30-minute bucket panel.

EVERY definition in this file is frozen by runs/G3_CLOCKLAG01_20260831/spec.yaml section 2 and
may not be varied. In particular:

  * 13 consecutive 30-minute RTH buckets, b = 0..12; bucket b covers [09:30+30b, 09:30+30(b+1)).
    NO OTHER BUCKET WIDTH MAY BE TRIED (spec prohibition 5).
  * Bars are END-STAMPED (CLAUDE.md section 6): the bar stamped 09:31 covers 09:30:00-09:30:59.
    Therefore bucket 0 is the bars STAMPED 09:31..10:00 inclusive, and bucket 12 is the bars
    STAMPED 15:31..16:00 inclusive.
  * r(b,d) = log( last close in bucket b on day d / last close in bucket b-1 on day d ), with
    r(0,d) based on the RTH open = the OPEN of the bar stamped 09:31.
  * Window 2006-01-05 -> 2026-07-31. SEAL: no session >= 2026-08-01 is read.

Data comes from research/weekly_edge/src/run_we_w17.py::load_deep(a, b, extend=True). That module
is IMPORTED, never modified (spec prohibition 2).
"""
from __future__ import annotations

import os
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "weekly_edge", "src"))

# --------------------------------------------------------------------------------------------
# Frozen constants
# --------------------------------------------------------------------------------------------
K_BUCKETS = 13
BUCKET_MINUTES = 30                 # FROZEN. spec prohibition: no other width in this run.
RTH_OPEN_MOD = 570                  # 09:30 as minute-of-day
FIRST_STAMP_MOD = RTH_OPEN_MOD + 1  # 09:31 - the bar whose OPEN is the 09:30:00 print
LAST_STAMP_MOD = RTH_OPEN_MOD + BUCKET_MINUTES * K_BUCKETS   # 16:00

WINDOW_A = "2006-01-05"
WINDOW_B = "2026-07-31 17:00"       # one second before the 2026-08-01 session would matter;
#                                     the 17:00 stamp is the last bar of the 2026-07-31 session.
SEAL_FIRST_FORBIDDEN = np.datetime64("2026-08-01", "D")

ERA_BREAK = np.datetime64("2022-05-01", "D")   # ERABREAK01, p=0.0011. Pooling across it is banned.


def bucket_of_stamp(mod: np.ndarray) -> np.ndarray:
    """Bucket index of a bar STAMPED at minute-of-day `mod`. Valid for 571 <= mod <= 960."""
    return (mod - FIRST_STAMP_MOD) // BUCKET_MINUTES


def build_panel(verbose=True, log=print):
    """Return the frozen session x bucket panel.

    Returns dict with
        dates   (n_sess,)  datetime64[D] session dates, ascending
        P       (n_sess,13) last close in each bucket
        B       (n_sess,13) base price of each bucket  (B[:,0] = RTH open, B[:,b] = P[:,b-1])
        R       (n_sess,13) r(b,d) = log(P/B)
        drops   dict of diagnostics
    """
    import run_we_w17 as W17                                              # noqa: E402

    D = W17.load_deep(WINDOW_A, WINDOW_B, extend=True)
    t = D["t"]                                # datetime64[s], END-stamped
    o, c = D["o"], D["c"]
    sid = D["sid"]

    day = t.astype("datetime64[D]")
    mod = ((t - day.astype("datetime64[s]")) // np.timedelta64(60, "s")).astype(np.int64)

    # ---- SEAL -------------------------------------------------------------------------------
    sess_date = D["sess_date"]
    n_forbidden = int((sess_date >= SEAL_FIRST_FORBIDDEN).sum())
    if n_forbidden:
        raise RuntimeError(f"SEAL VIOLATION: {n_forbidden} sessions >= 2026-08-01 in the load")
    if verbose:
        log(f"  load_deep(extend=True): {D['n']:,} bars, {D['n_sess']:,} sessions, "
            f"{t[0]} -> {t[-1]}")
        log(f"  SEAL OK: max session date {sess_date.max()} < 2026-08-01 "
            f"(sessions >= seal read: {n_forbidden})")

    # ---- RTH selection ----------------------------------------------------------------------
    sel = (mod >= FIRST_STAMP_MOD) & (mod <= LAST_STAMP_MOD)
    dsel, msel, csel, osel, sidsel = day[sel], mod[sel], c[sel], o[sel], sid[sel]
    bk = bucket_of_stamp(msel)
    assert bk.min() == 0 and bk.max() == K_BUCKETS - 1

    udates, inv = np.unique(dsel, return_inverse=True)
    nd = len(udates)

    # Every RTH calendar date should map to exactly one trading session. It does not when a data
    # hole longer than 60 minutes falls inside RTH, because load_deep's session detector splits on
    # a >60-minute gap. Those dates are DATA HOLES, not alignment errors; they are reported and
    # force-dropped rather than silently repaired.
    sid_min = np.full(nd, np.iinfo(np.int64).max, np.int64)
    sid_max = np.full(nd, -1, np.int64)
    np.minimum.at(sid_min, inv, sidsel)
    np.maximum.at(sid_max, inv, sidsel)
    split_date = sid_min != sid_max
    if verbose and split_date.any():
        log(f"  RTH dates split across sessions by a >60-min intraday data hole: "
            f"{int(split_date.sum())}  {list(udates[split_date].astype(str))}  -> force-dropped")

    # ---- last bar of each (date, bucket) ----------------------------------------------------
    key = inv * K_BUCKETS + bk
    lastpos = np.full(nd * K_BUCKETS, -1, np.int64)
    np.maximum.at(lastpos, key, np.arange(len(key), dtype=np.int64))
    lastpos = lastpos.reshape(nd, K_BUCKETS)

    P = np.full((nd, K_BUCKETS), np.nan)
    ok = lastpos >= 0
    P[ok] = csel[lastpos[ok]]

    # ---- the RTH open: OPEN of the bar stamped 09:31 ----------------------------------------
    is_open_bar = msel == FIRST_STAMP_MOD
    open_pos = np.full(nd, -1, np.int64)
    np.maximum.at(open_pos, inv[is_open_bar], np.arange(len(key), dtype=np.int64)[is_open_bar])
    rth_open = np.where(open_pos >= 0, osel[np.maximum(open_pos, 0)], np.nan)

    # ---- completeness ------------------------------------------------------------------------
    have_open = open_pos >= 0
    have_all = ok.all(axis=1)
    keep = have_open & have_all & ~split_date
    drops = dict(
        rth_dates=int(nd),
        dropped_missing_0931_open=int((~have_open).sum()),
        dropped_incomplete_buckets=int((have_open & ~have_all).sum()),
        dropped_session_split=int(split_date.sum()),
        dropped_session_split_dates=list(udates[split_date].astype(str)),
        kept=int(keep.sum()),
        sessions_ge_seal_read=n_forbidden,
    )
    if verbose:
        log(f"  RTH calendar dates seen              {drops['rth_dates']:,}")
        log(f"  dropped: no bar stamped 09:31        {drops['dropped_missing_0931_open']:,}")
        log(f"  dropped: >=1 empty 30-min bucket     {drops['dropped_incomplete_buckets']:,}")
        log(f"  dropped: intraday session split      {drops['dropped_session_split']:,}")
        log(f"  KEPT complete sessions               {drops['kept']:,}")
        log("  (a session is kept only if the 09:31 bar exists AND all 13 buckets are non-empty;")
        log("   half-days and holiday sessions therefore drop out. No return is interpolated.)")

    dates = udates[keep]
    P = P[keep]
    rth_open = rth_open[keep]
    Bse = np.empty_like(P)
    Bse[:, 0] = rth_open
    Bse[:, 1:] = P[:, :-1]
    R = np.log(P / Bse)

    if not np.isfinite(R).all():
        raise RuntimeError("non-finite bucket return after completeness filter")

    gaps = np.diff(dates).astype("timedelta64[D]").astype(int)
    drops["lag1_calendar_gap_days"] = {
        "1": int((gaps == 1).sum()), "2-4": int(((gaps >= 2) & (gaps <= 4)).sum()),
        ">4": int((gaps > 4).sum()), "max": int(gaps.max()) if len(gaps) else 0}
    if verbose:
        g = drops["lag1_calendar_gap_days"]
        log(f"  day-over-day link gaps: 1d {g['1']:,}  2-4d {g['2-4']:,}  >4d {g['>4']:,}  "
            f"max {g['max']}d   (lag-1 = previous KEPT session; no gap filter is applied)")

    return dict(dates=dates, P=P, B=Bse, R=R, drops=drops)


def era_masks(dates: np.ndarray) -> dict:
    """PRE (2006 -> 2022-04), MODERN (2022-05 -> 2026-07-31), FULL. FULL is a DIAGNOSTIC ONLY."""
    pre = dates < ERA_BREAK
    modern = dates >= ERA_BREAK
    return {"PRE": pre, "MODERN": modern, "FULL": np.ones(len(dates), bool)}


# --------------------------------------------------------------------------------------------
# Self-test of the frozen definitions, on synthetic bars with hand-known answers
# --------------------------------------------------------------------------------------------
def selftest(log=print) -> int:
    checks = []

    def chk(name, cond, detail=""):
        checks.append((name, bool(cond), detail))

    # bucket boundaries, stated in the spec in words, checked here as arithmetic
    chk("09:31 -> bucket 0", bucket_of_stamp(np.array([571]))[0] == 0)
    chk("10:00 -> bucket 0", bucket_of_stamp(np.array([600]))[0] == 0)
    chk("10:01 -> bucket 1", bucket_of_stamp(np.array([601]))[0] == 1)
    chk("10:30 -> bucket 1", bucket_of_stamp(np.array([630]))[0] == 1)
    chk("15:31 -> bucket 12", bucket_of_stamp(np.array([931]))[0] == 12)
    chk("16:00 -> bucket 12", bucket_of_stamp(np.array([960]))[0] == 12)
    chk("13 buckets exactly cover 09:30-16:00",
        LAST_STAMP_MOD - RTH_OPEN_MOD == K_BUCKETS * BUCKET_MINUTES == 390)
    every = bucket_of_stamp(np.arange(FIRST_STAMP_MOD, LAST_STAMP_MOD + 1))
    chk("every RTH stamp lands in 0..12 and each bucket has 30 stamps",
        (np.bincount(every, minlength=13) == 30).all())

    # the return chain: with a synthetic day whose bucket closes are known, r must telescope
    rng = np.random.default_rng(0)
    op = 100.0
    cl = op * np.exp(np.cumsum(rng.normal(0, 0.001, K_BUCKETS)))
    base = np.concatenate([[op], cl[:-1]])
    r = np.log(cl / base)
    chk("returns telescope to the full-RTH log return",
        abs(r.sum() - np.log(cl[-1] / op)) < 1e-12, f"{r.sum()} vs {np.log(cl[-1]/op)}")
    chk("r(0) uses the RTH OPEN as base", abs(r[0] - np.log(cl[0] / op)) < 1e-15)

    # era split
    d = np.array(["2022-04-29", "2022-05-02", "2006-01-05", "2026-07-31"], "datetime64[D]")
    m = era_masks(d)
    chk("2022-04-29 is PRE", m["PRE"][0] and not m["MODERN"][0])
    chk("2022-05-02 is MODERN", m["MODERN"][1] and not m["PRE"][1])
    chk("PRE and MODERN partition FULL", (m["PRE"] ^ m["MODERN"]).all())

    # np.maximum.at last-occurrence semantics, which build_panel relies on for "last bar in bucket"
    a = np.full(3, -1, np.int64)
    np.maximum.at(a, np.array([0, 0, 2, 0]), np.array([5, 9, 1, 7]))
    chk("np.maximum.at picks the largest position (= last bar, series is time-sorted)",
        a[0] == 9 and a[2] == 1 and a[1] == -1, str(a))

    npass = sum(c[1] for c in checks)
    w = max(len(c[0]) for c in checks)
    for name, okk, det in checks:
        log(f"  [{'PASS' if okk else 'FAIL'}] {name:<{w}}  {det}")
    log(f"  panel selftest {npass}/{len(checks)}")
    return 0 if npass == len(checks) else 1


if __name__ == "__main__":
    sys.exit(selftest())
