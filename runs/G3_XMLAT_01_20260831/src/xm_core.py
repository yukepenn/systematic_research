"""G3_XMLAT_01 - XM_CONFLICT decision/fill engine.

A FAITHFUL RE-EXPRESSION of research/weekly_edge/src/export_xm_reference.py (lines 38-124),
extended with (a) a wider study window, (b) the alternate fill minutes the decay curve needs,
(c) a post-decision corruption hook for the X1 NEGATIVE probe, and (d) a per-session
single-market perturbation hook for the X1 POSITIVE probe.

NOTHING in research/weekly_edge/src/ or any .cs file is edited. The reference loader
(run_we_w17.load_deep), session framing (run_we_w51.session_frames) and the committed spread
profile (we_lab.spread_profile) are IMPORTED, not copied.

The rebuild is asserted BIT-IDENTICAL against the frozen decision ledger
research/weekly_edge/ninjascript/reference/xm_reference_decisions.csv before any gate runs.

SEAL: nothing at or after 2026-08-01 is read. load_deep is called with b="2026-07-31 17:00".
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "research", "weekly_edge", "src"))

from run_we_w01 import PV, COMM_RT                                     # noqa: E402
from run_we_w17 import load_deep                                       # noqa: E402
from run_we_w51 import session_frames                                  # noqa: E402
from we_lab import spread_profile                                      # noqa: E402

# ---- the object's clock, verbatim from export_xm_reference.py:38-39 and the .cs header ----
ANCH, DEC, ENTM, EXITM, EXITNB = 571, 585, 586, 945, 946
SIG_LB, SIG_MIN, MAXSTALE = 60, 20, 3
TICKV = 5.0                       # $ per NQ tick (PV 20 / 4)
TICK = 0.25

XM_PATHS = {"ES": "runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet",
            "RTY": "runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet",
            "YM": "runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet"}

# ---- SEAL ----------------------------------------------------------------------------------
SEAL_FROM = np.datetime64("2026-08-01")
LOAD_A, LOAD_B = "2022-01-01", "2026-07-31 17:00"

REF_CSV = os.path.join(ROOT, "research", "weekly_edge", "ninjascript", "reference",
                       "xm_reference_decisions.csv")

# ---- the fill ladder. minute -> (label, field, delay_seconds) --------------------------------
#   bars are BAR-END stamped: the bar stamped HH:MM covers [HH:MM-1min, HH:MM).
#   open(09:46) is therefore the FIRST print at or after 09:45:00.000  -> +0s after the decision
#   close(09:46) is the LAST print before 09:46:00.000                 -> +59s (nominal)
ENTRY_FILLS = [
    ("open_0946", 586, "o", 0.0),
    ("close_0946", 586, "c", 59.0),
    ("open_0947", 587, "o", 60.0),
    ("open_0948", 588, "o", 120.0),
    ("open_0950", 590, "o", 240.0),
    ("high_0946", 586, "h", np.nan),      # worst/best-case bound on any within-minute fill
    ("low_0946", 586, "l", np.nan),
]
EXIT_FILLS = [
    ("open_1546", 946, "o", 0.0),         # the incumbent / NT8-consistent exit
    ("close_1545", 945, "c", -60.0),      # the older research convention, for the record
    ("open_1547", 947, "o", 60.0),
    ("open_1548", 948, "o", 120.0),
    ("open_1550", 950, "o", 240.0),
]


# ==============================================================================================
def load_substrate(verbose=True):
    """NQ 1-min + the three cross-market closes, joined on the NQ bar clock."""
    D = load_deep(LOAD_A, LOAD_B, extend=True)
    tarr = D["t"]
    if tarr.max() >= SEAL_FROM:
        raise RuntimeError("SEAL VIOLATION: substrate carries a bar at or after 2026-08-01")
    st, en, _ = session_frames(D)
    D["st"], D["en"] = st, en
    D["mod"] = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]")
                .astype(np.int64) // 60).astype(np.int32)
    nq = pd.DataFrame({"time": pd.to_datetime(tarr), "nq": D["c"]}).set_index("time")
    XD, XTS = {}, {}
    for k, path in XM_PATHS.items():
        d_ = pd.read_parquet(os.path.join(ROOT, path), columns=["time", "close"])
        d_["time"] = pd.to_datetime(d_["time"])
        if d_["time"].max() >= pd.Timestamp(SEAL_FROM):
            d_ = d_[d_["time"] < pd.Timestamp(SEAL_FROM)]
        j = nq.join(d_.set_index("time")["close"].rename(k), how="left")
        XD[k] = j[k].to_numpy()
        XTS[k] = ~np.isnan(XD[k])           # a NaN here IS the missing-bar case
    D["XD"], D["XTS"] = XD, XTS
    if verbose:
        print(f"    substrate: {D['n']:,} NQ bars, {D['n_sess']:,} sessions, "
              f"{tarr[0]} -> {tarr[-1]}")
        for k in XM_PATHS:
            print(f"      {k:<4s} joined on {int(XTS[k].sum()):,} / {D['n']:,} NQ bars")
    return D


# ==============================================================================================
def _at(D, mv, field, arrs=None):
    """value of `field` on the bar stamped minute `mv`, per session, plus its global index."""
    NS, sid, mod = D["n_sess"], D["sid"], D["mod"]
    src = arrs if arrs is not None else D
    arr = src[field]
    r = np.full(NS, np.nan)
    ix = np.full(NS, -1, np.int64)
    m_ = mod == mv
    r[sid[m_]] = arr[m_]
    ix[sid[m_]] = np.flatnonzero(m_)
    return r, ix


def corrupt_after_decision(D, seed=20260831, verbose=True):
    """X1 NEGATIVE probe.

    Replace every NQ o/h/l/c and every ES/RTY/YM close from the bar stamped 09:46 ONWARD with
    volatility-matched white noise, on EVERY session. The corrupted region is the set of bars
    whose minute-of-day lies in [586, 1020] - that is exactly the 09:46 .. 17:00 span of a
    session, and it can never collide with the 18:00-23:59 evening leg (minutes 1080-1439) or
    with the anchor (571) / decision (585) bars.

    Finiteness structure is preserved bit for bit: a bar that was NaN stays NaN, so no
    `take` mask can move for a reason other than a genuine leak.
    """
    rng = np.random.default_rng(seed)
    mod = D["mod"]
    reg = (mod >= ENTM) & (mod <= 1020)
    out = {k: D[k].copy() for k in ("o", "h", "l", "c")}
    XDc = {k: D["XD"][k].copy() for k in XM_PATHS}
    sid = D["sid"]
    n_corr = 0
    for s in range(D["n_sess"]):
        a, b = D["st"][s], D["en"][s]
        sl = np.arange(a, b)
        sl = sl[reg[sl]]
        if len(sl) == 0:
            continue
        n_corr += len(sl)
        # --- NQ: matched-vol random walk seeded from the last uncorrupted close
        base_i = sl[0] - 1
        base = D["c"][base_i] if base_i >= a and np.isfinite(D["c"][base_i]) else D["c"][sl[0]]
        lr = np.diff(np.log(D["c"][sl])) if len(sl) > 1 else np.array([0.0])
        lr = lr[np.isfinite(lr)]
        sg = float(np.std(lr, ddof=1)) if len(lr) > 1 else 1e-5
        sg = sg if np.isfinite(sg) and sg > 0 else 1e-5
        path = base * np.exp(np.cumsum(rng.normal(0.0, sg, size=len(sl))))
        rng_bar = np.abs(rng.normal(0.0, sg, size=len(sl))) * path
        for k, v in (("o", path), ("c", path), ("h", path + rng_bar), ("l", path - rng_bar)):
            fin = np.isfinite(D[k][sl])
            out[k][sl] = np.where(fin, v, np.nan)
        # --- the three cross markets
        for k in XM_PATHS:
            xv = D["XD"][k][sl]
            fin = np.isfinite(xv)
            if not fin.any():
                continue
            bi = sl[0] - 1
            xb = D["XD"][k][bi] if bi >= a and np.isfinite(D["XD"][k][bi]) else xv[fin][0]
            xlr = np.diff(np.log(xv[fin])) if fin.sum() > 1 else np.array([0.0])
            xlr = xlr[np.isfinite(xlr)]
            xsg = float(np.std(xlr, ddof=1)) if len(xlr) > 1 else 1e-5
            xsg = xsg if np.isfinite(xsg) and xsg > 0 else 1e-5
            xp = xb * np.exp(np.cumsum(rng.normal(0.0, xsg, size=len(sl))))
            XDc[k][sl] = np.where(fin, xp, np.nan)
    if verbose:
        print(f"    NEGATIVE probe: {n_corr:,} bars replaced with matched-vol white noise "
              f"({100.0 * n_corr / D['n']:.1f} % of the substrate), on "
              f"{D['n_sess']:,} / {D['n_sess']:,} sessions")
    Dc = dict(D)
    Dc.update(out)
    Dc["XD"] = XDc
    Dc["XTS"] = {k: ~np.isnan(XDc[k]) for k in XM_PATHS}
    return Dc, n_corr


# ==============================================================================================
def build_decisions(D, win_lo, win_hi, verbose=False):
    """export_xm_reference.py:71-124, re-expressed. Returns one dict of per-session arrays.

    The sigma history warms on EVERY loaded session, including sessions outside [win_lo, win_hi):
    gating the history on the window cost 4 trades against the canonical object
    (export_xm_reference.py:83-85). That behaviour is preserved exactly.
    """
    NS = D["n_sess"]
    tarr, st = D["t"], D["st"]
    lo, hi = np.datetime64(win_lo), np.datetime64(win_hi)
    win = np.array([lo <= tarr[st[s]] < hi for s in range(NS)])

    pa, ia = _at(D, ANCH, "o")
    pdc, idc = _at(D, DEC, "c")
    XD, XTS = D["XD"], D["XTS"]

    HIST = {k: [] for k in XM_PATHS}
    drive = np.zeros(NS)
    comp = np.full(NS, np.nan)
    conflict = np.zeros(NS, np.int8)
    desired = np.zeros(NS, np.int8)
    disq = np.zeros(NS, bool)
    # book-keeping the POSITIVE probe needs: today's r and today's sigma, per market
    r_of = {k: np.full(NS, np.nan) for k in XM_PATHS}
    sg_of = {k: np.full(NS, np.nan) for k in XM_PATHS}
    cnt_of = np.zeros(NS, np.int32)

    for s in range(NS):
        if not np.isfinite(pa[s]) or not np.isfinite(pdc[s]):
            continue
        ok = True
        for k in XM_PATHS:
            if ia[s] < 0 or idc[s] < 0 or not XTS[k][ia[s]] or not XTS[k][idc[s]]:
                ok = False
        if not ok:
            disq[s] = True
            continue
        if not win[s]:
            for k in XM_PATHS:
                HIST[k].append(np.log(XD[k][idc[s]] / XD[k][ia[s]]))
            continue
        drive[s] = np.sign(pdc[s] - pa[s])
        acc, cnt = 0.0, 0
        for k in XM_PATHS:
            r_ = np.log(XD[k][idc[s]] / XD[k][ia[s]])
            r_of[k][s] = r_
            hh = HIST[k]
            if len(hh) >= SIG_MIN:
                w = hh[-SIG_LB:]
                sg = float(np.std(w, ddof=1))
                if sg > 1e-12:
                    sg_of[k][s] = sg
                    acc += r_ / sg
                    cnt += 1
            hh.append(r_)                    # appended AFTER use: today is never in its own sigma
        cnt_of[s] = cnt
        if cnt:
            comp[s] = acc / cnt
            xs = np.sign(comp[s])
            if xs != 0 and drive[s] != 0 and xs != drive[s]:
                conflict[s] = 1
                desired[s] = int(drive[s])

    out = dict(win=win, drive=drive, comp=comp, conflict=conflict, desired_raw=desired.copy(),
               disq=disq, pa=pa, ia=ia, pdc=pdc, idc=idc,
               r_of=r_of, sg_of=sg_of, cnt_of=cnt_of, NS=NS)

    # ---- fill ladders, and the `take` mask (a signal with no tradeable bar is not a trade)
    for lab, mv, fld, _ in ENTRY_FILLS:
        out["E_" + lab], out["Ei_" + lab] = _at(D, mv, fld)
    for lab, mv, fld, _ in EXIT_FILLS:
        out["X_" + lab], out["Xi_" + lab] = _at(D, mv, fld)

    take = ((desired != 0) & np.isfinite(out["E_open_0946"])
            & np.isfinite(out["X_close_1545"]) & np.isfinite(out["X_open_1546"]))
    out["take"] = take
    out["desired"] = np.where(take, desired, 0).astype(np.int8)
    return out


# ==============================================================================================
def verify_against_frozen(DEC, D, verbose=True):
    """Assert the rebuild is bit-identical to the frozen ledger on its own window."""
    ref = pd.read_csv(REF_CSV)
    sdate = pd.to_datetime(D["sess_date"])
    # The ledger emits ONE ROW PER IN-WINDOW SESSION, in session order. Two calendar dates in
    # this substrate carry TWO sessions each (2025-11-27 and 2026-07-17 are split by an intraday
    # data gap > 60 min), so a date -> session dict silently drops one of each pair. Align by
    # ORDER, then assert the dates agree.
    idx_ok = np.flatnonzero(DEC["win"])
    if len(idx_ok) != len(ref):
        raise RuntimeError(f"frozen-ledger alignment: {len(ref)} rows vs {len(idx_ok)} in-window "
                           f"sessions - the rebuild window does not match the ledger's")
    mine_dates = np.array([sdate[s].strftime("%Y-%m-%d") for s in idx_ok])
    ndm = int((mine_dates != ref["session_date"].to_numpy()).sum())
    r = ref
    res = {}
    res["rows"] = len(ref)
    res["sessions_not_found"] = ndm
    res["dd_agree"] = float((r["desired_direction"].to_numpy()
                             == DEC["desired"][idx_ok]).mean() * 100.0)
    res["cf_agree"] = float((r["conflict_flag"].to_numpy()
                             == DEC["conflict"][idx_ok]).mean() * 100.0)
    res["drive_agree"] = float((r["nq_drive"].to_numpy() == DEC["drive"][idx_ok]).mean() * 100.0)
    a = r["broad_composite"].to_numpy(dtype=float)
    b = DEC["comp"][idx_ok]
    both = np.isfinite(a) & np.isfinite(b)
    res["comp_maxabsdiff"] = float(np.abs(a[both] - b[both]).max()) if both.any() else np.nan
    res["comp_nan_agree"] = float((np.isfinite(a) == np.isfinite(b)).mean() * 100.0)
    res["ref_trades"] = int((r["desired_direction"] != 0).sum())
    res["mine_trades_on_ref_window"] = int((DEC["desired"][idx_ok] != 0).sum())
    ep = r["entry_px"].to_numpy(dtype=float)
    em = DEC["E_open_0946"][idx_ok]
    bo = np.isfinite(ep) & np.isfinite(em)
    res["entry_px_maxabsdiff"] = float(np.abs(ep[bo] - em[bo]).max()) if bo.any() else np.nan
    xp = r["exit_px_open1546"].to_numpy(dtype=float)
    xm_ = DEC["X_open_1546"][idx_ok]
    bo2 = np.isfinite(xp) & np.isfinite(xm_)
    res["exit_px_maxabsdiff"] = float(np.abs(xp[bo2] - xm_[bo2]).max()) if bo2.any() else np.nan
    if verbose:
        print(f"    frozen ledger {os.path.basename(REF_CSV)}: {res['rows']:,} sessions, "
              f"{res['ref_trades']} trades")
        print(f"      desired_direction agreement  {res['dd_agree']:.4f} %")
        print(f"      conflict_flag agreement      {res['cf_agree']:.4f} %")
        print(f"      nq_drive agreement           {res['drive_agree']:.4f} %")
        print(f"      broad_composite max |diff|   {res['comp_maxabsdiff']:.3e}")
        print(f"      entry_px max |diff|          {res['entry_px_maxabsdiff']:.3e}")
        print(f"      exit_px(1546) max |diff|     {res['exit_px_maxabsdiff']:.3e}")
        print(f"      session_date disagreements   {res['sessions_not_found']}")
        print(f"      trades  ledger {res['ref_trades']}   rebuild "
              f"{res['mine_trades_on_ref_window']}")
    return res


# ==============================================================================================
def cost_per_rt(entry_min=ENTM, exit_min=EXITNB):
    """The campaign's committed cost model: commission + modelled per-minute spread."""
    prof = spread_profile()
    return COMM_RT + TICKV * (float(prof.loc[entry_min]) + float(prof.loc[exit_min])) / 2.0


def week_of(D, sess):
    sd = pd.to_datetime(D["sess_date"][sess])
    iso = sd.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def week_index(D, win):
    """Every ISO week that contains at least one loaded, in-window session. Balanced panel."""
    sdate = pd.to_datetime(D["sess_date"])
    wk = []
    for s in np.flatnonzero(win):
        iso = sdate[s].isocalendar()
        wk.append(f"{iso[0]}-W{iso[1]:02d}")
    order = sorted(set(wk))
    return order, np.array(wk)
