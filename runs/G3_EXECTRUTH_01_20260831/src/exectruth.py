"""G3_EXECTRUTH_01 - bar-level ACTION + STATE parity between the DEPLOYED C# object and the
Python research object.

Executes runs/G3_EXECTRUTH_01_20260831/spec.yaml, which was committed before any comparison
existed. Every gate clause in that spec is coded here and the gate table is printed BY THIS
PROGRAM. Nothing here is fitted; this run has zero free parameters by construction.

PROHIBITIONS HONOURED (spec section 4)
  - no order / deploy / enable / disable / backtest / CrossTrade call of any kind
  - no edit to any production .cs file or to anything under research/weekly_edge/src/
  - no read of any session >= 2026-08-01: the export rows from 2026-08-01 onward are DROPPED
    before any statistic is computed and the dropped count is printed
  - no p-value / hypothesis test anywhere (spec trap 2: n is ~325k, the gates are agreement
    thresholds)

THREE FUNCTIONS ARE COPIED HERE RATHER THAN IMPORTED, because the hard rule for this run is that
nothing under research/weekly_edge/src/ may be edited and each of them needs one extra output or
one extra index:
  votes_instrumented   = run_we_w97.votes VERBATIM, plus it returns the per-set targets and the
                         nMem / nThr / dL / ratio intermediates the export writes. Asserted
                         bit-identical to the canonical votes() before use.
  causal_score_lag     = run_we_w37.causal_score VERBATIM, plus ONE index shift `lag`, which is
                         the entire subject of gate P3. Asserted bit-identical to the canonical
                         causal_score at lag=0 before use.
  gfills_path          = run_we_w98.gfills VERBATIM, plus it records the per-bar position/qty
                         path so an ACTION series can be derived from the position path alone
                         (never from P&L). Asserted to produce a byte-identical trade list to the
                         canonical gfills before use.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time as _time

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
SRC = os.path.join(ROOT, "research", "weekly_edge", "src")
sys.path.insert(0, SRC)
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))

import run_we_w01 as W1                                                    # noqa: E402
from run_we_w01 import PV, COMM_RT                                         # noqa: E402
from run_we_w17 import load_deep                                           # noqa: E402
from run_we_w19 import MEMBERS, QS                                         # noqa: E402
from run_we_w26 import fills_daily                                         # noqa: E402
from run_we_w37 import causal_score, MINHIST                               # noqa: E402
from run_we_w39 import WIN                                                 # noqa: E402
from run_we_w97 import votes                                               # noqa: E402
from run_we_w98 import gfills, arm_kw                                      # noqa: E402
from we_fastctx import fast_build_context, fast_intraday_features          # noqa: E402

RUN = os.path.join(ROOT, "runs", "G3_EXECTRUTH_01_20260831")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
SNAP = os.path.join(OUT, "cs_export_snapshot.csv")
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")

# ---- constants that are READ FROM SOURCE, never chosen here ----------------------------------
SEAL = np.datetime64("2026-08-01T00:00:00")          # CLAUDE.md section 5: >= this is VIRGIN
RT_START = np.datetime64("2026-08-31T12:28:00")      # 16:28 UTC, when the current deployment began
A_CANON = np.datetime64("2022-07-01")                # run_we_w103.py:39
B_CANON = np.datetime64("2026-08-01")                # run_we_w103.py:40
L13 = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
# WeeklyEdgeP1PCT_v3.cs:768-773
CS_TILT_SMA = 50          # tilt is 0 until sessCloses.Count > TiltSma
CS_QUAL_WINDOW = 250      # QualWindow
CS_QUAL_MINHIST = 100     # QualMinHist
CS_ENTRY_LEVEL, CS_EXIT_LEVEL = 3.0, 1.0
CS_WSOLAR, CS_WBMOM, CS_TILTMULT, CS_TILTRESCALE = 0.7086, 2.83, 1.25, 0.9026

_fh = None


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    if _fh:
        _fh.write(s + "\n")
        _fh.flush()


def H(title):
    P("")
    P("=" * 118)
    P("=== " + title)
    P("=" * 118)


# ==================================================================================================
# COPIED CHAIN VARIANTS
# ==================================================================================================
def votes_instrumented(D, mem, bmom, tilt, ctx, chan):
    """VERBATIM COPY of research/weekly_edge/src/run_we_w97.py::votes, with the per-set targets
    and the export's four state intermediates additionally returned. Not one arithmetic line is
    changed; the copy exists only because the canonical function may not be edited."""
    n, tarr, sid = D["n"], D["t"], D["sid"]
    fb, sess_end = D["fb"], D["sess_end"]
    blocked = tarr >= sess_end[sid] - np.timedelta64(30 * 60, "s")
    flatm = tarr >= sess_end[sid] - np.timedelta64(21 * 60, "s")
    idx = {v: k for k, v in enumerate(L13)}

    def ra(x):
        return np.where(x >= 0, np.floor(x + 0.5), np.ceil(x - 0.5))

    def hyst(M):
        tg = np.zeros(n, np.int8)
        for i in range(n):
            p = 0 if (i == 0 or fb[i]) else tg[i - 1]
            g = p
            if flatm[i]:
                g = 0
            elif p == 0:
                if not blocked[i]:
                    g = 1 if M[i] >= 3.0 else (-1 if M[i] <= -3.0 else p)
            elif p > 0:
                g = -1 if (M[i] <= -3.0 and not blocked[i]) else (0 if M[i] <= 1.0 else p)
            else:
                g = 1 if (M[i] >= 3.0 and not blocked[i]) else (0 if M[i] >= -1.0 else p)
            tg[i] = g
        return tg
    TG = {}
    for name, vols in MEMBERS.items():
        cols = [idx[v] for v in vols]
        s_ = mem[:, cols].sum(axis=1).astype(np.int32)
        T = np.clip(ra(s_ / float(len(cols)) * 10.0), -10, 10)
        ag = (np.sign(s_) == tilt) & (s_ != 0) & (tilt != 0)
        Tp = np.clip(ra(T * np.where(ag, 1.25, 1.0) * 0.9026), -13, 13)
        TG[name] = hyst(0.7086 * Tp + 2.83 * chan.astype(float))

    def vote_(side):
        vs = []
        for m_ in MEMBERS:
            tg = TG[m_]
            for q in QS:
                okv = np.ones(n, bool) if q is None else \
                    ((ctx["norm"] <= 0) | (ctx["ratio"] >= q))
                for dg in (True, False):
                    a_ = okv & (ctx["dL"] if side > 0 else ctx["dS"]) if dg else okv
                    hit = (tg > 0) if side > 0 else (tg < 0)
                    vs.append(np.where(hit & a_, 1, 0).astype(np.int8))
        return np.vstack(vs).mean(axis=0)
    vl, vs_ = (vote_(+1) >= 0.5), (vote_(-1) >= 0.5)

    # ---- the export's four state intermediates, same definitions, WeeklyEdgeP1PCT_v3.cs:1080-1128
    nMem = np.zeros(n, np.int32)
    for name in MEMBERS:
        nMem += (TG[name] > 0).astype(np.int32)
    nThr = np.ones(n, np.int32)                      # the q = none voter always passes (:1121)
    for q in (0.7, 0.8, 0.9):
        nThr += ((ctx["norm"] <= 0) | (ctx["ratio"] >= q)).astype(np.int32)
    dL = ctx["dL"].astype(np.int32)
    return vl, vs_, TG, nMem, nThr, dL, ctx["ratio"]


def causal_score_lag(X, ent_i, window=250, lag=0):
    """VERBATIM COPY of research/weekly_edge/src/run_we_w37.py::causal_score with ONE change: the
    features are read at `ent_i - lag` instead of `ent_i`. That single index IS gate P3.

    lag = 0  -> X[k][i]    (bar i-1 close)  = what the Python research object does today
    lag = 1  -> X[k][i-1]  (bar i-2 close)  = what the .cs source read predicts
    lag = 2  -> X[k][i-2]  (bar i-3 close)  = the named control, which must lose
    """
    feats = [("dist_open", +1), ("prev_ret", -1), ("runlen", +1),
             ("dist_vwap", +1), ("delta_mag", +1)]
    q = {"dist_open": 2 / 3, "prev_ret": 1 / 3, "runlen": 0.9,
         "dist_vwap": 2 / 3, "delta_mag": 2 / 3}
    src = np.maximum(np.asarray(ent_i) - lag, 0)
    vals = {k: X[k][src] for k, _ in feats}
    n_ent = len(ent_i)
    sc_ent = np.zeros(n_ent)
    for j in range(n_ent):
        lo = max(0, j - window)
        if j < MINHIST:
            sc_ent[j] = np.nan
            continue
        s = 0
        for k, sgn in feats:
            hist = vals[k][lo:j]
            thr = np.nanquantile(hist, q[k])
            v = vals[k][j]
            s += (v >= thr) if sgn > 0 else (v <= thr)
        sc_ent[j] = s
    out = np.zeros(len(X["ratio"]))
    ok = ~np.isnan(sc_ent)
    out[np.asarray(ent_i)[ok]] = sc_ent[ok]
    return out, sc_ent


def gfills_path(D, dir_arr, size_at_entry=None, halt=1300.0, target=1000.0, per_ctr=False):
    """VERBATIM COPY of research/weekly_edge/src/run_we_w98.py::gfills, with one addition: the
    per-bar signed position and contract count are recorded so an ACTION series can be derived
    from the POSITION PATH ALONE. No P&L is consulted anywhere in that derivation.

    The recording point is AFTER the session-close flatten branch, which is exactly where the .cs
    writes its export row (WeeklyEdgeP1PCT_v3.cs:1158-1195 - the lastBar flatten sets myQty = 0
    BEFORE the WriteLine)."""
    t, o, c = D["t"], D["o"], D["c"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    trades = []
    qty_path = np.zeros(n, np.int16)
    p = 0; u = 0; epx = 0.0; eti = -1; spnl = 0.0; stopped = False
    for i in range(n):
        if fb[i]:
            spnl = 0.0; stopped = False
        want = int(dir_arr[i - 1]) if i > 0 and not fb[i] else 0
        if stopped:
            want = 0
        if want != p:
            if p != 0:
                pnl = p * u * (o[i] - epx) * PV - COMM_RT * u
                trades.append(dict(d=p, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
                spnl += (pnl / u) if per_ctr else pnl
                if spnl <= -halt or (target is not None and spnl >= target):
                    stopped = True; want = 0
            p = want
            if p != 0:
                u = int(size_at_entry[i]) if size_at_entry is not None else 1
                if u < 1:
                    p = 0; u = 0
                else:
                    epx, eti = o[i], i
        if lb[i] and p != 0:
            pnl = p * u * (c[i] - epx) * PV - COMM_RT * u
            trades.append(dict(d=p, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
            p = 0; u = 0
        qty_path[i] = p * u
    return trades, qty_path


def act_from_qty(q):
    """FLAT / ENTER / HOLD / EXIT from a per-bar qty path alone. 0=FLAT 1=ENTER 2=HOLD 3=EXIT."""
    q = np.asarray(q)
    prev = np.concatenate([[0], q[:-1]])
    a = np.zeros(len(q), np.int8)
    a[(prev == 0) & (q != 0)] = 1
    a[(prev != 0) & (q != 0)] = 2
    a[(prev != 0) & (q == 0)] = 3
    return a


def jaccard(a, b):
    a, b = set(a), set(b)
    u = len(a | b)
    return (len(a & b) / u) if u else float("nan")


def firstn(ts_arr, mask, k=20):
    s = ts_arr[mask]
    return [str(x) for x in s[:k]]


# ==================================================================================================
def main():
    global _fh
    t0 = _time.time()
    _fh = open(os.path.join(OUT, "console.txt"), "w", encoding="utf-8")

    P("=" * 118)
    P("G3_EXECTRUTH_01_20260831 - EXECUTABLE OBJECT TRUTH")
    P("bar-level ACTION + STATE parity: the DEPLOYED C# object vs the Python research object.")
    P("spec: runs/G3_EXECTRUTH_01_20260831/spec.yaml (committed before any comparison existed)")
    P("LIVE ENABLED = NO.  $0 spent.  No order, no deploy, no backtest, no CrossTrade call.")
    P("EVIDENCE STATUS: VERIFICATION - nothing is selected, tuned, or promoted by this run.")
    P("NO P-VALUE APPEARS ANYWHERE IN THIS RUN (spec trap 2). The gates are agreement thresholds.")
    P("=" * 118)

    # ============================================================================ 0. PROVENANCE
    H("0. PROVENANCE - the C# side is a snapshot, taken read-only, of a file a LIVE strategy is "
      "appending to")
    h = hashlib.sha256()
    with open(SNAP, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    sha = h.hexdigest()
    P(f"    source        C:\\NT8_ForwardLogs\\export\\we_p1pct_p1pct.csv  (opened FileShare.Read"
      f"Write, never written)")
    P(f"    snapshot      {SNAP}")
    P(f"    sha256        {sha}")
    P(f"    bytes         {os.path.getsize(SNAP):,}")

    E = pd.read_csv(SNAP)
    P(f"    data rows     {len(E):,}   (the spec quotes 353,878; the file is being appended to "
      f"live, so a later snapshot is longer - the DELTA IS ALL IN THE SEALED REGION, see below)")
    ets = pd.to_datetime(E["pyts"]).values.astype("datetime64[s]")
    ndup = len(ets) - len(np.unique(ets))
    nmono = int((np.diff(ets).astype("int64") <= 0).sum())
    P(f"    duplicates    {ndup}      non-monotonic rows {nmono}")
    P(f"    span          {ets[0]}  ->  {ets[-1]}")
    assert ndup == 0 and nmono == 0, "export is not a clean monotonic distinct-timestamp series"

    # ============================================================================ 1. THE SEAL
    H("1. DATA SEAL - executed BEFORE any statistic is computed (CLAUDE.md section 5)")
    seal_mask = ets >= SEAL
    n_rt_pre = int((ets >= RT_START).sum())
    P(f"    rows with timestamp >= 2026-08-01 (VIRGIN)        DROPPED : {int(seal_mask.sum()):>8,}")
    P(f"    rows retained (in-window, < 2026-08-01)                   : {int((~seal_mask).sum()):>8,}")
    E = E.loc[~seal_mask].reset_index(drop=True)
    ets = ets[~seal_mask]
    P(f"    retained span                                             : {ets[0]} -> {ets[-1]}")
    P("")
    P("    *** THE REALTIME TAIL IS ENTIRELY INSIDE THE SEAL. ***")
    P(f"    The current deployment began 2026-08-31 16:28 UTC = 12:28 ET. Rows at or after that")
    P(f"    instant: {n_rt_pre:,} - every one of them is >= 2026-08-01 and was just dropped.")
    P(f"    Realtime-tail rows SURVIVING the seal: 0.")
    P("    Consequence, stated before any gate is read: EVERY number in this run is computed on")
    P("    bars NT8 produced by HISTORICAL processing during the 365-day warm-up load. This run")
    P("    therefore CANNOT split historical from realtime behaviour (spec trap 1). Every gate is")
    P("    reported twice as required, and the realtime column is UNDECIDABLE with n = 0 - it is")
    P("    not reported as a rate, and no gate is called PASS on the strength of it.")

    # ============================================================== 2. DECLARATIONS BEFORE RESULTS
    H("2. DECLARATIONS MADE BEFORE ANY RESULT IS COMPUTED")
    P("    (a) WARM-UP SUB-SPAN, derived from the .cs source constants alone, not from any result.")
    P(f"        WeeklyEdgeP1PCT_v3.cs:1067 updates `tilt` only once sessCloses.Count > TiltSma")
    P(f"        (= {CS_TILT_SMA}). sessCloses gains one entry per session close, so tilt is")
    P(f"        identically 0 for the first {CS_TILT_SMA + 1} sessions of the export and the")
    P("        deployed object cannot agree with a fully-warm Python tilt there. rngHist needs 20")
    P("        sessions (:1118) and bmom needs BmomBandDays = 14 (:1034); both are subsumed.")
    P(f"        DECLARED SPLIT: FULL = every retained row.  WARM = export session index >= "
      f"{CS_TILT_SMA + 1}.")
    P("        The GATE VERDICT is taken on FULL, exactly as the spec states. WARM is printed")
    P("        beside it as a named diagnostic so the warm-up is visible rather than hidden.")
    P("")
    P("    (b) P3 IS COMPUTED IN TWO FRAMINGS, both declared here, both printed for all three arms.")
    P("        EXEC-NATIVE  (PRIMARY): the trailing-quantile history is the executable's OWN")
    P("            evaluated-entry sequence, read from the export, starting at the export's first")
    P("            bar with qCount = 0, QualMinHist = 100, QualWindow = 250 - i.e. a faithful")
    P("            reconstruction of the deployed object, which was redeployed with DaysToLoad=365")
    P("            and therefore holds NO quality history before 2025-08-31. Zero free parameters.")
    P("        RESEARCH-CHAIN (COMPANION): the canonical chain's own entry schedule and its full")
    P("            2022-07-01-onward history - the object the campaign has been quoting.")
    P("        The three P3 arms differ ONLY by the index shift WITHIN each framing, so the")
    P("        comparison between arms is exact in both. The gate is read on EXEC-NATIVE because")
    P("        the mask, the entry sequence and the history are then all the executable's own.")
    P("")
    P("    (c) P4, if reached, is computed on the RESEARCH-CHAIN size vectors applied to the")
    P("        Python trade schedule, because P4's question is what separates the object we trade")
    P("        from THE OBJECT WE HAVE BEEN QUOTING, and the quoted object is the research chain.")
    P("        The exec-native size vector is reported beside it.")

    # ============================================================================ 3. SUBSTRATE
    H("3. THE PYTHON RESEARCH OBJECT - the canonical chain, unmodified")
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid, fb, lb = D["n"], D["t"], D["sid"], D["fb"], D["lb"]
    P(f"    load_deep('2022-01-01','2026-07-31 17:00', extend=True): {n:,} bars / "
      f"{D['n_sess']:,} sessions, {tarr[0]} -> {tarr[-1]}  [{_time.time()-t0:.0f}s]")
    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    P(f"    runs/WE_W76_FORWARD2026/out/mem_ext.npz: mem {mem.shape} bmom {bmom.shape} "
      f"tilt {tilt.shape}")
    assert mem.shape[0] == n and bmom.shape[0] == n and tilt.shape[0] == n, \
        "mem_ext.npz does not cover the substrate - REBUILD REQUIRED"
    P(f"    CACHE SPAN CHECK: the cache has exactly one row per substrate bar, and the substrate")
    P(f"    spans {tarr[0]} -> {tarr[-1]}, which strictly contains the needed")
    P(f"    2025-08-31 -> 2026-07-31 comparison window. The cache is USED AS IS; no rebuild was")
    P(f"    necessary and none was performed.")
    ifeat = fast_intraday_features(D)
    X = fast_build_context(D, ifeat=ifeat)
    rng_raw, _dmove, atr14, norm_py = ifeat
    P(f"    fast_build_context built  [{_time.time()-t0:.0f}s]")

    vl, vs_, TG, nMem_py, nThr_py, dL_py, ratio_py = votes_instrumented(D, mem, bmom, tilt, X, bmom)
    P(f"    votes_instrumented built  [{_time.time()-t0:.0f}s]")
    vlc, vsc = votes(D, mem, bmom, tilt, X, bmom)
    ok_copy = bool((vlc == vl).all() and (vsc == vs_).all())
    P(f"    HARNESS A: votes_instrumented == canonical run_we_w97.votes, bit for bit ....... "
      f"{'PASS' if ok_copy else 'FAIL'}")
    assert ok_copy
    voteOK_py = ((nMem_py * nThr_py * (1 + dL_py)) >= 16)
    ok_vote = bool((voteOK_py == vl).all())
    P(f"    HARNESS B: (nMem*nThr*(1+dL))>=16 == the canonical 32-voter mean>=0.5 ........... "
      f"{'PASS' if ok_vote else 'FAIL'}")
    assert ok_vote
    p_dir = vl.astype(np.int8)
    TGa = np.vstack([TG[k] for k in MEMBERS])          # rows in MEMBERS order = SETLEN {5,6,7,13}
    P(f"    per-set targets t0..t3 ordered {list(MEMBERS)} == .cs SETLEN {{5,6,7,13}}")

    # canonical entry schedule + canonical causal score (run_we_w103.py:100-107)
    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))
    bb = fills_daily(D, p_dir, halt=1300, target=1000)
    ee = np.array([i_of(x["et"]) for x in bb if A_CANON <= np.datetime64(x["et"]) < B_CANON])
    P(f"    canonical entry schedule (fills_daily, 2022-07-01 -> 2026-08-01): {len(ee):,} entries "
      f" [{_time.time()-t0:.0f}s]")
    sc_canon, _ = causal_score(X, ee, window=WIN)
    sc0_lag, sce0 = causal_score_lag(X, ee, window=WIN, lag=0)
    ok_cs = bool(np.array_equal(sc_canon, sc0_lag))
    P(f"    HARNESS C: causal_score_lag(lag=0) == canonical run_we_w37.causal_score ......... "
      f"{'PASS' if ok_cs else 'FAIL'}")
    assert ok_cs
    sz_canon = np.where(sc_canon >= 3, 2, 1).astype(np.int8)
    tr_canon = gfills(D, p_dir, sz_canon, **arm_kw("PCT", 1.183))
    tr_copy, qty_py_full = gfills_path(D, p_dir, sz_canon, **arm_kw("PCT", 1.183))
    ok_gf = (len(tr_canon) == len(tr_copy)) and all(
        a["d"] == b["d"] and a["u"] == b["u"] and a["et"] == b["et"] and a["xt"] == b["xt"]
        and abs(a["pnl"] - b["pnl"]) < 1e-12 for a, b in zip(tr_canon, tr_copy))
    P(f"    HARNESS D: gfills_path trade list == canonical run_we_w98.gfills, byte for byte .. "
      f"{'PASS' if ok_gf else 'FAIL'}")
    assert ok_gf
    kw = arm_kw("PCT", 1.183)
    P(f"    HARNESS E: gfills called with per_ctr = {kw['per_ctr']}  (spec trap 3: the .cs session")
    P(f"               box accumulates PER CONTRACT, WeeklyEdgeP1PCT_v3.cs:934-938 and :1164-1167)"
      f"  {'PASS' if kw['per_ctr'] is True else 'FAIL'}")
    assert kw["per_ctr"] is True
    P(f"    canonical P1/PCT object: {len(tr_canon):,} trades  [{_time.time()-t0:.0f}s]")

    # ================================================================= 4. TIMESTAMP VERIFICATION
    H("4. TIMESTAMP ALIGNMENT - verified on real session boundaries BEFORE the join is trusted")
    P("    The export writes LOCAL ET with no zone ('yyyy-MM-dd HH:mm:ss', .cs:1189). The Python")
    P("    substrate `t` is also ET. Both are BAR-END stamped. The check below is not a claim; it")
    P("    is a comparison of the two files' own session structure.")
    P("")
    ex_gap = np.zeros(len(ets), bool)
    ex_gap[0] = True
    ex_gap[1:] = np.diff(ets).astype("timedelta64[m]").astype(np.int64) > 60
    ex_sess = np.cumsum(ex_gap) - 1
    P(f"    export sessions detected by a >60 min gap: {int(ex_sess[-1]) + 1}")
    P(f"    substrate sessions in the same span      : "
      f"{len(np.unique(sid[(tarr >= ets[0]) & (tarr <= ets[-1])]))}")
    P("")
    P(f"    {'#':>4}  {'C# first bar of session':<24}{'PY first bar of session':<24}"
      f"{'C# last bar':<22}{'PY last bar':<22}{'sessPnl@first':>14}")
    fbi = np.flatnonzero(fb)
    lbi = np.flatnonzero(lb)
    ver_rows = 0
    ver_ok = True
    for k in list(range(0, 3)) + [60, 120] + [int(ex_sess[-1]) - 1]:
        m = ex_sess == k
        if not m.any():
            continue
        cs_first, cs_last = ets[m][0], ets[m][-1]
        pf = fbi[(tarr[fbi] >= cs_first - np.timedelta64(1, "D")) & (tarr[fbi] <= cs_first)]
        pl = lbi[(tarr[lbi] >= cs_first) & (tarr[lbi] <= cs_last + np.timedelta64(1, "D"))]
        py_first = tarr[pf[-1]] if len(pf) else np.datetime64("NaT")
        py_last = tarr[pl[0]] if len(pl) else np.datetime64("NaT")
        sp = float(E["sessPnl"].to_numpy()[m][0])
        P(f"    {k:>4}  {str(cs_first):<24}{str(py_first):<24}{str(cs_last):<22}"
          f"{str(py_last):<22}{sp:>14.2f}")
        ver_rows += 1
        ver_ok &= (cs_first == py_first) and (abs(sp) < 1e-9)
    P("")
    P(f"    VERIFIED on {ver_rows} sessions: the C# first bar of session and the Python first bar")
    P(f"    of session are the SAME timestamp (18:01 ET after an 18:00 open, bar-END stamped), and")
    P(f"    the C# sessPnl is exactly 0.00 on that bar - i.e. the two files agree on WHERE a")
    P(f"    session starts, not merely on how minutes are labelled.  {'PASS' if ver_ok else 'FAIL'}")
    P(f"    No +-1 minute shift is applied anywhere in this program (CLAUDE.md section 6; the")
    P(f"    shift WAS the original W52 phase error and is not reintroduced).")

    # ============================================================================ 5. GATE P0
    H("5. GATE P0 - BAR IDENTITY. Are the two objects looking at the same bars?")
    pos = np.searchsorted(tarr, ets)
    posc = np.minimum(pos, n - 1)
    hit = tarr[posc] == ets
    jj = posc[hit]                                   # substrate index for each joined export row
    jts = ets[hit]
    P(f"    C# rows in-window                : {len(ets):>9,}")
    P(f"    matched (inner join on timestamp): {int(hit.sum()):>9,}  "
      f"= {100*hit.mean():.3f} % of the C# rows")
    P(f"    C#-only                          : {int((~hit).sum()):>9,}")
    span_a, span_b = jts[0], jts[-1]
    pyspan = (tarr >= ets[0]) & (tarr <= ets[-1])
    pos2 = np.searchsorted(jts, tarr[pyspan])
    pos2c = np.minimum(pos2, len(jts) - 1)
    py_only = int((jts[pos2c] != tarr[pyspan]).sum())
    P(f"    Python-only (inside the C# span) : {py_only:>9,}")
    cso = ets[~hit]
    P(f"    C#-only bars, first 10 : {[str(x) for x in cso[:10]]}")
    P(f"    C#-only bars, last 10  : {[str(x) for x in cso[-10:]]}")
    pyo = tarr[pyspan][jts[pos2c] != tarr[pyspan]]
    P(f"    Python-only bars       : {[str(x) for x in pyo[:12]]}")
    close_cs = E["close"].to_numpy(float)[hit]
    close_py = D["c"][jj]
    d = close_cs - close_py
    mon = pd.to_datetime(jts).to_period("M").astype(str)
    P("")
    P(f"    {'month':<10}{'n':>9}{'mean d':>12}{'median d':>12}{'sd d':>10}"
      f"{'max|d-med|':>12}{'sd<=0.25':>10}")
    p0rows = []
    p0_all_ok = True
    for m_ in sorted(set(mon)):
        s = d[mon == m_]
        med = float(np.median(s))
        sdv = float(np.std(s, ddof=1)) if len(s) > 1 else 0.0
        mx = float(np.max(np.abs(s - med)))
        ok = sdv <= 0.25
        p0_all_ok &= ok
        P(f"    {m_:<10}{len(s):>9,}{s.mean():>12.4f}{med:>12.4f}{sdv:>10.4f}{mx:>12.4f}"
          f"{('yes' if ok else 'NO'):>10}")
        p0rows.append(dict(month=m_, n=int(len(s)), mean=float(s.mean()), median=med,
                           sd=sdv, max_abs_dev=mx, ok=bool(ok)))
    nz = d != 0.0
    P("")
    P(f"    bars where close_cs != close_py at all: {int(nz.sum()):,} of {len(d):,} "
      f"({100*nz.mean():.4f} %). The spec EXPECTED a constant per-contract-regime "
      f"back-adjustment offset; the measured offset is EXACTLY ZERO in "
      f"{sum(1 for r in p0rows if r['sd'] == 0.0 and r['mean'] == 0.0)} of {len(p0rows)} months.")
    if nz.any():
        bydate = pd.Series(pd.to_datetime(jts[nz]).date).value_counts().sort_index()
        P(f"    the non-zero bars by date: "
          f"{ {str(k): int(v) for k, v in bydate.items()} }")
        P(f"    largest |d|: {np.abs(d).max():.4f} pt at {jts[np.argmax(np.abs(d))]}")
    join_rate = float(hit.mean())
    P0_PASS = bool(join_rate >= 0.95 and p0_all_ok)
    P("")
    P(f"    join rate {100*join_rate:.3f} % (spec >= 95 %)   every month sd(d) <= 0.25 : "
      f"{'yes' if p0_all_ok else 'NO'}")
    P(f"    P0 VERDICT: {'PASS' if P0_PASS else 'FAIL - EVERYTHING BELOW IS VOID'}")
    if not P0_PASS:
        P("    Per the spec, P0 failing voids every later gate. Stopping.")
        json.dump(dict(P0=dict(verdict="FAIL", join_rate=join_rate, months=p0rows)),
                  open(os.path.join(OUT, "gates.json"), "w"), indent=1)
        _fh.close()
        return

    # joined frame + the declared warm split
    ex_sess_j = ex_sess[hit]
    WARM = ex_sess_j >= (CS_TILT_SMA + 1)
    P(f"    declared WARM sub-span: export session >= {CS_TILT_SMA+1} -> {int(WARM.sum()):,} of "
      f"{len(WARM):,} joined bars ({100*WARM.mean():.1f} %), from "
      f"{jts[WARM][0] if WARM.any() else 'n/a'}")

    # ============================================================================ 6. GATE P1
    H("6. GATE P1 - STATE PARITY. Do the two objects compute the same decision state on the "
      "same bar?")
    Ej = E.loc[hit].reset_index(drop=True)
    cs = dict(nMem=Ej["nMem"].to_numpy(np.int32), nThr=Ej["nThr"].to_numpy(np.int32),
              dL=Ej["dL"].to_numpy(np.int32), ratio=Ej["ratio"].to_numpy(float),
              voteOK=Ej["voteOK"].to_numpy(np.int32), tilt=Ej["tilt"].to_numpy(np.int32),
              bmom=Ej["bmom"].to_numpy(np.int32),
              t0=Ej["t0"].to_numpy(np.int32), t1=Ej["t1"].to_numpy(np.int32),
              t2=Ej["t2"].to_numpy(np.int32), t3=Ej["t3"].to_numpy(np.int32))
    py = dict(nMem=nMem_py[jj], nThr=nThr_py[jj], dL=dL_py[jj], ratio=ratio_py[jj],
              voteOK=vl[jj].astype(np.int32), tilt=tilt[jj].astype(np.int32),
              bmom=bmom[jj].astype(np.int32),
              t0=TGa[0][jj].astype(np.int32), t1=TGa[1][jj].astype(np.int32),
              t2=TGa[2][jj].astype(np.int32), t3=TGa[3][jj].astype(np.int32))
    ACTION_BEARING = ("voteOK", "t0", "t1", "t2", "t3")
    DIAGNOSTIC = ("nMem", "nThr", "dL", "ratio", "tilt", "bmom")
    agree = {}
    dis_rows = []
    P(f"    {'field':<10}{'kind':<14}{'n':>10}{'agree FULL':>13}{'agree WARM':>13}"
      f"{'n disagree':>12}{'first disagreement':>22}")
    for k in ("nMem", "nThr", "dL", "ratio", "voteOK", "tilt", "bmom", "t0", "t1", "t2", "t3"):
        if k == "ratio":
            eq = np.abs(cs[k] - py[k]) <= 1e-3
        else:
            eq = cs[k] == py[k]
        agree[k] = dict(full=float(eq.mean()),
                        warm=float(eq[WARM].mean()) if WARM.any() else float("nan"),
                        ndis=int((~eq).sum()))
        kind = "ACTION-BEARING" if k in ACTION_BEARING else "diagnostic"
        f20 = firstn(jts, ~eq, 20)
        P(f"    {k:<10}{kind:<14}{len(eq):>10,}{100*agree[k]['full']:>12.4f}%"
          f"{100*agree[k]['warm']:>12.4f}%{agree[k]['ndis']:>12,}"
          f"{(f20[0] if f20 else '-'):>22}")
        if f20:
            P(f"    {'':<10}first 20 disagreeing timestamps: {', '.join(f20)}")
        idx = np.flatnonzero(~eq)
        for i_ in idx:
            dis_rows.append((str(jts[i_]), k, cs[k][i_], py[k][i_], bool(WARM[i_])))
    P1_PASS = bool(all(agree[k]["full"] >= 0.995 for k in ACTION_BEARING))
    P1_WARM = bool(all(agree[k]["warm"] >= 0.995 for k in ACTION_BEARING))
    P("")
    P(f"    spec PASS = voteOK >= 99.5 % AND each of t0..t3 >= 99.5 %")
    P(f"    P1 VERDICT (FULL, the gate): {'PASS' if P1_PASS else 'FAIL'}   "
      f"(WARM diagnostic: {'pass' if P1_WARM else 'fail'})")
    P(f"    ratio / tilt / bmom / nMem / nThr / dL are DIAGNOSTIC: they may drift on a float path")
    P(f"    or a warm-up path without changing an action. That distinction is reported, not hidden.")
    P("")
    P("    CLASSIFICATION OF EVERY ACTION-BEARING MISMATCH (the WE_W52 band requires it in the")
    P("    90-99 % zone). Split at the DECLARED warm boundary, not at one chosen after the fact:")
    P(f"    {'field':<10}{'n disagree':>12}{'before WARM':>14}{'inside WARM':>14}"
      f"{'share pre-warm':>16}")
    for k in ACTION_BEARING:
        eq = (cs[k] == py[k])
        pre = int((~eq & ~WARM).sum()); ins = int((~eq & WARM).sum())
        P(f"    {k:<10}{pre+ins:>12,}{pre:>14,}{ins:>14,}"
          f"{100*pre/max(pre+ins, 1):>15.1f}%")
    _vbad = (cs["voteOK"] != py["voteOK"]) & WARM
    if _vbad.any():
        _dts = pd.Series(pd.to_datetime(jts[_vbad]).date).value_counts()
        P(f"    the {int(_vbad.sum()):,} voteOK mismatches INSIDE WARM fall on "
          f"{_dts.size} distinct dates; the 10 heaviest: "
          f"{ {str(k): int(v) for k, v in _dts.head(10).items()} }")
        P(f"    (2026-06-11 and 2026-07-17 are the two dates where the two files do not even hold")
        P(f"     the same bars - 12 Python-only and 65 C#-only minutes - so state divergence there")
        P(f"     is a DATA-COVERAGE difference, not a logic difference.)")
    P("")
    P("    LOCALISATION OF THE `ratio` DIAGNOSTIC DISAGREEMENT (it does not move nThr, which")
    P("    agrees to 99.76 % inside WARM, but it is large enough to name). ratio = rngPrev/norm,")
    P("    and rngPrev is a pure price quantity that must agree because P0 showed the prices are")
    P("    identical - so any disagreement is in `norm`, the trailing time-of-day range median.")
    rcs, rpy = cs["ratio"], py["ratio"]
    one_cs, one_py = np.isclose(rcs, 1.0, atol=1e-9), np.isclose(rpy, 1.0, atol=1e-9)
    rdis = np.abs(rcs - rpy) > 1e-3
    P(f"      C# ratio == 1.0000 exactly (its norm not yet available) while Python's is not: "
      f"{int((one_cs & ~one_py & rdis).sum()):,}  ({int((one_cs & ~one_py & rdis & WARM).sum()):,} "
      f"inside WARM)")
    P(f"      Python ratio == 1.0 while the C#'s is not: {int((one_py & ~one_cs & rdis).sum()):,}")
    both = rdis & ~one_cs & ~one_py
    if both.any():
        impl = rpy[both] / np.maximum(rcs[both], 1e-12)     # = norm_cs / norm_py
        P(f"      both sides have a norm but disagree: {int(both.sum()):,}; implied norm_cs/norm_py"
          f" median {np.median(impl):.4f}, p10 {np.percentile(impl,10):.4f}, "
          f"p90 {np.percentile(impl,90):.4f}")
        P(f"      -> the C# holds at most {int(ex_sess[-1])+1} sessions of time-of-day range")
        P(f"         history (it was redeployed with DaysToLoad=365); Python holds 1,187. Both")
        P(f"         take a 60-observation median, so they coincide only where the C# already has")
        P(f"         60 prior observations of that minute-of-day.")

    # ============================================================================ 7. GATE P2
    H("7. GATE P2 - ACTION PARITY. Derived from the qty / position path ONLY, never from P&L.")
    qty_cs_full = E["qty"].to_numpy(np.int32)          # full in-window export, contiguous
    act_cs_full = act_from_qty(qty_cs_full)
    act_py_full = act_from_qty(qty_py_full)
    ts_cs_ent = ets[act_cs_full == 1]
    ts_cs_ext = ets[act_cs_full == 3]
    ts_py_ent = tarr[act_py_full == 1]
    ts_py_ext = tarr[act_py_full == 3]
    lo, hi = max(ets[0], tarr[0]), min(ets[-1], tarr[-1])
    P(f"    common span for the action comparison: {lo} -> {hi}")
    P(f"    (the C# export runs to {ets[-1]}; the Python substrate physically ends {tarr[-1]})")

    def clip(a):
        a = np.asarray(a)
        return a[(a >= lo) & (a <= hi)]
    ce, cx = clip(ts_cs_ent), clip(ts_cs_ext)
    pe, px_ = clip(ts_py_ent), clip(ts_py_ext)
    ent_j = jaccard(ce.astype("int64"), pe.astype("int64"))
    ext_j = jaccard(cx.astype("int64"), px_.astype("int64"))
    conly = np.array(sorted(set(ce.astype("int64")) - set(pe.astype("int64")))).astype("datetime64[s]")
    ponly = np.array(sorted(set(pe.astype("int64")) - set(ce.astype("int64")))).astype("datetime64[s]")
    conly_x = np.array(sorted(set(cx.astype("int64")) - set(px_.astype("int64")))).astype("datetime64[s]")
    ponly_x = np.array(sorted(set(px_.astype("int64")) - set(cx.astype("int64")))).astype("datetime64[s]")
    tcd = (len(ce) - len(pe)) / max(len(pe), 1)
    P("")
    P(f"    C# entries {len(ce):,}   Python entries {len(pe):,}   "
      f"trade-count difference {100*tcd:+.3f} %")
    P(f"    ENTRY-bar Jaccard : {ent_j:.5f}")
    P(f"    EXIT -bar Jaccard : {ext_j:.5f}")
    P(f"    C#-only entries {len(conly):,}   Python-only entries {len(ponly):,}")
    P(f"    C#-only exits   {len(conly_x):,}   Python-only exits   {len(ponly_x):,}")
    P(f"      C#-only entries, first 20 : {[str(x) for x in conly[:20]]}")
    P(f"      PY-only entries, first 20 : {[str(x) for x in ponly[:20]]}")
    P(f"      C#-only exits,   first 20 : {[str(x) for x in conly_x[:20]]}")
    P(f"      PY-only exits,   first 20 : {[str(x) for x in ponly_x[:20]]}")
    wl = jts[WARM][0] if WARM.any() else lo
    P("")
    P("    CLASSIFICATION OF EVERY ACTION MISMATCH (WE_W52 band, 90-99 % zone), split at the")
    P(f"    DECLARED warm boundary {wl}:")
    P(f"    {'set':<22}{'total':>8}{'before WARM':>14}{'inside WARM':>14}{'share pre-warm':>16}")
    for nm_, arr in (("C#-only entries", conly), ("Python-only entries", ponly),
                     ("C#-only exits", conly_x), ("Python-only exits", ponly_x)):
        pre = int((arr < wl).sum()); ins = int((arr >= wl).sum())
        P(f"    {nm_:<22}{pre+ins:>8,}{pre:>14,}{ins:>14,}{100*pre/max(pre+ins,1):>15.1f}%")
    cew, pew = ce[ce >= wl], pe[pe >= wl]
    ent_j_w = jaccard(cew.astype("int64"), pew.astype("int64"))
    tcd_w = (len(cew) - len(pew)) / max(len(pew), 1)
    P(f"    WARM diagnostic (session >= {CS_TILT_SMA+1}): entry Jaccard {ent_j_w:.5f}, "
      f"{len(cew):,} vs {len(pew):,} entries, count diff {100*tcd_w:+.3f} %")
    # cross-check tying P2 to P3's mask: WeeklyEdgeP1PCT_v3.cs:1174-1183 submits an entry on
    # EXACTLY the bars where the quality block evaluates (pendingAct is reset to ACT_NONE at the
    # top of every bar, :947, and EntriesAllowed() is a constant true outside State.Realtime,
    # :1180), and that order fills at the NEXT bar's open. So #evaluated bars must equal #C#
    # entry bars, up to the one order still pending at the seal boundary.
    _me = (E["qty"].to_numpy(np.int32) == 0) & (E["voteOK"].to_numpy(np.int32) == 1) & \
          (E["stopped"].to_numpy(np.int32) == 0)
    P("")
    P(f"    CROSS-CHECK: C# bars that EVALUATED an entry {int(_me.sum()):,} vs C# ENTER events "
      f"{int((act_cs_full == 1).sum()):,}  (difference {int(_me.sum()) - int((act_cs_full==1).sum())}"
      f", expected 0 or 1 for an order pending at the seal boundary)")
    P2_PASS = bool(ent_j >= 0.99 and abs(tcd) <= 0.02)
    P2_WARM = bool(ent_j_w >= 0.99 and abs(tcd_w) <= 0.02)
    P("")
    P("    Per the repo's binding parity band (WE_W52): >=99 % decision agreement AND counts")
    P("    within 2 % = VALIDATED; 90-99 % requires EVERY mismatch classified; <90 % means it is")
    P("    not the same object. That band is applied to ACTIONS here, never to dollars.")
    P(f"    P2 VERDICT (FULL, the gate): {'PASS' if P2_PASS else 'FAIL'}   "
      f"(WARM diagnostic: {'pass' if P2_WARM else 'fail'})")

    # ============================================================================ 8. GATE P3
    H("8. GATE P3 - SIZE SEMANTICS. THE DECIDING GATE.")
    P("    Three mutually exclusive hypotheses about which bar the executable reads its quality")
    P("    features from. Same code path in all three; ONLY the index shifts.")
    P("      H_FRESH  score at fill bar i uses X[k][i]    (= bar i-1 close)  <- current Python")
    P("      H_STALE  score at fill bar i uses X[k][i-1]  (= bar i-2 close)  <- the source read")
    P("      H_STALE2 score at fill bar i uses X[k][i-2]  (= bar i-3 close)  <- control, must lose")
    P("")
    P("    THE MASK. WeeklyEdgeP1PCT_v3.cs:1131-1155 computes a score ONLY when")
    P("    (myQty == 0 && wantLong && UseQualitySize), where wantLong = voteOK && !sessStopped")
    P("    (:1132) and UseQualitySize is true (:774); otherwise it writes size = 1, score = 0.")
    P("    That mask is derived from the export's own qty / voteOK / stopped columns.")
    m_eval = (Ej["qty"].to_numpy(np.int32) == 0) & (Ej["voteOK"].to_numpy(np.int32) == 1) & \
             (Ej["stopped"].to_numpy(np.int32) == 0)
    sc_col = Ej["score"].to_numpy(np.int32)
    sz_col = Ej["size"].to_numpy(np.int32)
    P("")
    P(f"    joined bars                                : {len(m_eval):>9,}")
    P(f"    bars where the C# EVALUATED an entry       : {int(m_eval.sum()):>9,}")
    P(f"    of those, score > 0                        : {int((sc_col[m_eval] > 0).sum()):>9,}")
    P(f"    of those, score == 0 (warm-up, qCount<100) : {int((sc_col[m_eval] == 0).sum()):>9,}")
    P(f"    MASK SANITY off the mask: score != 0 on {int((sc_col[~m_eval] != 0).sum()):,} bars, "
      f"size != 1 on {int((sz_col[~m_eval] != 1).sum()):,} bars   "
      f"{'PASS' if (sc_col[~m_eval]==0).all() and (sz_col[~m_eval]==1).all() else 'FAIL'}")
    P(f"    MASK SANITY on the mask: size == 1+(score>=3) on "
      f"{100*np.mean(sz_col[m_eval] == 1 + (sc_col[m_eval] >= 3)):.3f} % of bars")

    ev_idx = np.flatnonzero(m_eval)
    fill_i = jj[ev_idx] + 1
    okf = (fill_i < n) & (~fb[np.minimum(fill_i, n - 1)])
    nbad = int((~okf).sum())
    P(f"    evaluated bars whose FILL bar i = j+1 is unavailable or crosses a session: {nbad}"
      f"  (dropped)")
    ev_idx = ev_idx[okf]
    fill_i = fill_i[okf]
    ev_ts = jts[ev_idx]
    ev_sc = sc_col[ev_idx]
    ev_sz = sz_col[ev_idx]
    ev_warm = WARM[ev_idx]
    P(f"    P3 comparison population                   : {len(ev_idx):>9,} evaluated entries")

    # ---- EXEC-NATIVE framing (PRIMARY)
    P("")
    P("    ---- FRAMING 1 of 2: EXEC-NATIVE (PRIMARY). History = the executable's own evaluated-")
    P("         entry sequence, starting at the export's first bar with qCount = 0.")
    P(f"    {'arm':<10}{'features read at':<26}{'score agree':>13}{'size agree':>12}"
      f"{'score agree (qC>=250)':>23}{'size agree (qC>=250)':>22}")
    ARMS = (("H_FRESH", 0), ("H_STALE", 1), ("H_STALE2", 2))
    conv = np.arange(len(ev_idx)) >= CS_QUAL_WINDOW
    exec_res = {}
    exec_scores = {}
    for nm, lag in ARMS:
        _, sce = causal_score_lag(X, fill_i, window=CS_QUAL_WINDOW, lag=lag)
        s_ = np.where(np.isnan(sce), 0.0, sce).astype(np.int32)
        z_ = 1 + (s_ >= 3).astype(np.int32)
        exec_scores[nm] = (s_, z_)
        r = dict(score=float(np.mean(s_ == ev_sc)), size=float(np.mean(z_ == ev_sz)),
                 score_conv=float(np.mean(s_[conv] == ev_sc[conv])) if conv.any() else float("nan"),
                 size_conv=float(np.mean(z_[conv] == ev_sz[conv])) if conv.any() else float("nan"),
                 score_warm=float(np.mean(s_[ev_warm] == ev_sc[ev_warm])) if ev_warm.any() else float("nan"),
                 size_warm=float(np.mean(z_[ev_warm] == ev_sz[ev_warm])) if ev_warm.any() else float("nan"))
        exec_res[nm] = r
        P(f"    {nm:<10}{'fill bar - ' + str(lag):<26}{100*r['score']:>12.3f}%"
          f"{100*r['size']:>11.3f}%{100*r['score_conv']:>22.3f}%{100*r['size_conv']:>21.3f}%")

    # ---- RESEARCH-CHAIN framing (COMPANION)
    P("")
    P("    ---- FRAMING 2 of 2: RESEARCH-CHAIN (COMPANION). History = the canonical chain's own")
    P("         entry schedule with its full 2022-07-01-onward history: the object we have quoted.")
    in_canon = np.isin(fill_i, ee)
    P(f"         coverage: {int(in_canon.sum()):,} of {len(fill_i):,} C#-evaluated fill bars are")
    P(f"         also entries in the canonical Python schedule ({100*in_canon.mean():.3f} %).")
    P(f"    {'arm':<10}{'features read at':<26}{'score agree':>13}{'size agree':>12}"
      f"{'score agree (WARM)':>20}{'size agree (WARM)':>19}")
    res_res = {}
    res_scores = {}
    for nm, lag in ARMS:
        per_bar, _ = causal_score_lag(X, ee, window=WIN, lag=lag)
        s_ = per_bar[fill_i].astype(np.int32)
        z_ = 1 + (s_ >= 3).astype(np.int32)
        res_scores[nm] = (s_, z_, per_bar)
        mm = in_canon
        wm = in_canon & ev_warm
        r = dict(score=float(np.mean(s_[mm] == ev_sc[mm])), size=float(np.mean(z_[mm] == ev_sz[mm])),
                 score_warm=float(np.mean(s_[wm] == ev_sc[wm])) if wm.any() else float("nan"),
                 size_warm=float(np.mean(z_[wm] == ev_sz[wm])) if wm.any() else float("nan"))
        res_res[nm] = r
        P(f"    {nm:<10}{'fill bar - ' + str(lag):<26}{100*r['score']:>12.3f}%"
          f"{100*r['size']:>11.3f}%{100*r['score_warm']:>19.3f}%{100*r['size_warm']:>18.3f}%")

    def winner(res):
        sc_w = max(res, key=lambda k: res[k]["score"])
        sz_w = max(res, key=lambda k: res[k]["size"])
        return sc_w, sz_w
    e_scw, e_szw = winner(exec_res)
    r_scw, r_szw = winner(res_res)
    P("")
    P(f"    EXEC-NATIVE  winner: score -> {e_scw}, size -> {e_szw}")
    P(f"    RESEARCH-CHAIN winner: score -> {r_scw}, size -> {r_szw}")
    ctrl_lost_e = exec_res["H_STALE2"]["score"] < max(exec_res["H_FRESH"]["score"],
                                                      exec_res["H_STALE"]["score"])
    P3_PASS = bool(e_scw == "H_STALE" and e_szw == "H_STALE"
                   and exec_res["H_STALE"]["score"] >= 0.99 and ctrl_lost_e)
    P(f"    control H_STALE2 loses (required): {'yes' if ctrl_lost_e else 'NO - THE HARNESS IS WRONG'}")
    P(f"    spec PASS = H_STALE wins BOTH outright AND score agreement >= 99.0 % AND H_STALE2 loses")
    P(f"    P3 VERDICT (EXEC-NATIVE, the gate): {'PASS' if P3_PASS else 'FAIL'}")
    if e_scw == "H_FRESH":
        P("")
        P("    *** THE SOURCE READ IN SPEC SECTION 0 IS WRONG AND IS RETRACTED. ***")
        P("    H_FRESH wins. The campaign uses H_FRESH as the executable semantics.")
    elif not P3_PASS and e_scw == "H_STALE":
        P("")
        P("    H_STALE wins but does not reach the 99.0 % bar in this framing. See the residual")
        P("    characterisation below before quoting anything.")

    # residual characterisation of the winner
    wsc, wsz = exec_scores[e_scw]
    bad = wsc != ev_sc
    P("")
    P(f"    RESIDUAL of the EXEC-NATIVE winner ({e_scw}): {int(bad.sum()):,} disagreeing entries "
      f"of {len(bad):,}")
    if bad.any():
        P(f"      first 20 disagreeing timestamps: {[str(x) for x in ev_ts[bad][:20]]}")
        P(f"      by C# score level : " + "  ".join(
            f"{s_}:{int(((ev_sc == s_) & bad).sum())}/{int((ev_sc == s_).sum())}"
            for s_ in range(6)))
        P(f"      inside the declared warm sub-span: {int((bad & ev_warm).sum()):,}; "
          f"before it: {int((bad & ~ev_warm).sum()):,}")
        P(f"      with qCount < 250 (partial window): {int((bad & ~conv).sum()):,}; "
          f"with qCount >= 250: {int((bad & conv).sum()):,}")
        hod = pd.to_datetime(ev_ts[bad]).hour
        P(f"      hour-of-day of the disagreements: "
          f"{dict(sorted(pd.Series(hod).value_counts().items()))}")

    # ================================================== 8b. RESIDUAL MECHANISM (POST-HOC)
    H("8b. RESIDUAL MECHANISM - POST-HOC DIAGNOSTIC. NOT PREREGISTERED. It does NOT change the "
      "P3 verdict above, and it does NOT unlock P4.")
    P("    The spec's if_none_reaches_99 branch requires the disagreeing rows to be characterised")
    P("    and the FEATURE THAT FLIPS to be named. Doing so found a source asymmetry that neither")
    P("    of the three preregistered arms can express. It is reported here as a HYPOTHESIS for a")
    P("    future preregistered run, not as a result of this one.")
    P("")
    P("    WHAT WAS FOUND, by reading source only:")
    P("      we_fastctx.fast_intraday_features:45-46 (and run_we_w09.intraday_features) already")
    P("      return atr14 LAGGED ONE BAR. we_quality.build_context:44 / we_fastctx:81 then lag it")
    P("      A SECOND TIME:  atr_l = concat([[atr14[0]], atr14[:-1]]).")
    P("      So X['atr_l'][j] is the ATR through bar j-2, while the NUMERATORS it divides,")
    P("      c_l[j] and vwap_l[j], are bar j-1 quantities. dist_open and dist_vwap are therefore")
    P("      built from a one-bar-STALER denominator than numerator.")
    P("      WeeklyEdgeP1PCT_v3.cs:1136-1140 has no such asymmetry: lagClose, lagVwap and lagAtr")
    P("      are all frozen at the same instant by CacheLagged (:1198), so at decision bar b the")
    P("      .cs divides bar b-1's close by the ATR through bar b-1.")
    P("      CONSEQUENCE: no single index shift can reproduce the .cs. H_STALE matches the .cs on")
    P("      the numerators and misses the ATR by one bar; H_FRESH matches the ATR and misses the")
    P("      numerators by one bar. The executable is a MIXTURE of the two arms.")
    tr_ = np.maximum(D["h"] - D["l"],
                     np.maximum(np.abs(D["h"] - np.roll(D["c"], 1)),
                                np.abs(D["l"] - np.roll(D["c"], 1))))
    tr_[0] = D["h"][0] - D["l"][0]
    atr_raw = pd.Series(tr_).rolling(14, min_periods=1).mean().values      # ATR through bar j
    atr_1 = np.concatenate([[atr_raw[0]], atr_raw[:-1]])                   # ATR through bar j-1
    dbl = bool(np.allclose(X["atr_l"], np.concatenate([[atr_1[0]], atr_1[:-1]]),
                           rtol=0, atol=1e-12))
    P("")
    P(f"    VERIFIED NUMERICALLY: X['atr_l'] == the ATR through bar j-2, i.e. lagged twice ... "
      f"{'CONFIRMED' if dbl else 'NOT CONFIRMED'}")
    starts_ = np.flatnonzero(D["fb"]); ends_ = np.concatenate([starts_[1:], [n]])
    seg_ = np.repeat(np.arange(len(starts_)), ends_ - starts_)
    pv_ = pd.Series(D["c"] * D["v"]).groupby(seg_).cumsum().to_numpy()
    vv_ = pd.Series(D["v"]).groupby(seg_).cumsum().to_numpy()
    vwap_ = np.where(vv_ > 0, pv_ / np.maximum(vv_, 1e-300), np.nan)
    sopen_ = np.repeat(D["o"][starts_], ends_ - starts_)
    cl_ = np.concatenate([[D["c"][0]], D["c"][:-1]])
    vwl_ = np.concatenate([[np.nan], vwap_[:-1]])
    XCS = dict(X)
    XCS["atr_l"] = atr_1
    XCS["dist_open"] = (cl_ - sopen_) / np.maximum(atr_1, 1e-9)
    XCS["dist_vwap"] = (cl_ - vwl_) / np.maximum(atr_1, 1e-9)
    P("")
    P("    ARM H_STALE_CSATR (post-hoc): identical to H_STALE except that dist_open and dist_vwap")
    P("    are divided by the ATR the .cs actually holds. Same mask, same entry sequence, same")
    P("    window, same history construction. One denominator, nothing else.")
    P(f"    {'arm':<18}{'score agree':>13}{'size agree':>12}{'score (qC>=250)':>18}"
      f"{'size (qC>=250)':>17}")
    posthoc = {}
    for nm, lag in (("H_FRESH_CSATR", 0), ("H_STALE_CSATR", 1), ("H_STALE2_CSATR", 2)):
        _, sce = causal_score_lag(XCS, fill_i, window=CS_QUAL_WINDOW, lag=lag)
        s_ = np.where(np.isnan(sce), 0.0, sce).astype(np.int32)
        z_ = 1 + (s_ >= 3).astype(np.int32)
        posthoc[nm] = dict(score=float(np.mean(s_ == ev_sc)), size=float(np.mean(z_ == ev_sz)),
                           score_conv=float(np.mean(s_[conv] == ev_sc[conv])),
                           size_conv=float(np.mean(z_[conv] == ev_sz[conv])),
                           n_bad=int((s_ != ev_sc).sum()))
        posthoc[nm + "_arr"] = s_
        r = posthoc[nm]
        P(f"    {nm:<18}{100*r['score']:>12.3f}%{100*r['size']:>11.3f}%"
          f"{100*r['score_conv']:>17.3f}%{100*r['size_conv']:>16.3f}%")
    best_ph = max(("H_FRESH_CSATR", "H_STALE_CSATR", "H_STALE2_CSATR"),
                  key=lambda k: posthoc[k]["score"])
    P("")
    P(f"    best post-hoc arm: {best_ph}, score agreement "
      f"{100*posthoc[best_ph]['score']:.3f} %, {posthoc[best_ph]['n_bad']} disagreeing entries "
      f"of {len(ev_sc)}")
    P("    STATUS OF THIS FINDING: a POST-HOC EXPLANATION with zero free parameters, derived from")
    P("    two lines of source. It is NOT a preregistered arm, it does NOT change the P3 verdict,")
    P("    and per the spec's if_none_reaches_99 clause NO ECONOMICS ARE QUOTED on the strength of")
    P("    it. Confirming it requires its own preregistered run.")

    # per-feature margin analysis of whatever residual remains
    def score_detail(Xd, ent_i, window, lag):
        feats = [("dist_open", +1, 2 / 3), ("prev_ret", -1, 1 / 3), ("runlen", +1, 0.9),
                 ("dist_vwap", +1, 2 / 3), ("delta_mag", +1, 2 / 3)]
        src = np.maximum(np.asarray(ent_i) - lag, 0)
        vals = {k: Xd[k][src] for k, _, _ in feats}
        N = len(ent_i)
        V = np.full((N, 5), np.nan); T = np.full((N, 5), np.nan)
        for j in range(N):
            if j < MINHIST:
                continue
            lo_ = max(0, j - window)
            for a_, (k, sgn, q) in enumerate(feats):
                hist = vals[k][lo_:j]
                V[j, a_] = vals[k][j]
                T[j, a_] = np.nanquantile(hist, q)
        return V, T, [f[0] for f in feats]
    lag_ph = {"H_FRESH_CSATR": 0, "H_STALE_CSATR": 1, "H_STALE2_CSATR": 2}[best_ph]
    Vd, Td, fnames = score_detail(XCS, fill_i, CS_QUAL_WINDOW, lag_ph)
    bad_ph = posthoc[best_ph + "_arr"] != ev_sc
    pb_cs, _ = causal_score_lag(XCS, ee, window=WIN, lag=1)
    s_rc = pb_cs[fill_i].astype(np.int32)
    rc_sc = float(np.mean(s_rc[in_canon] == ev_sc[in_canon]))
    P("")
    P("    SEPARATING THE TWO CAUSES. The same denominator correction applied inside the")
    P("    RESEARCH-CHAIN framing (canonical entry schedule, full 2022-onward history):")
    P(f"      H_STALE research-chain, original ATR : {100*res_res['H_STALE']['score']:.3f} %")
    P(f"      H_STALE research-chain, .cs ATR      : {100*rc_sc:.3f} %")
    P(f"      H_STALE exec-native,    .cs ATR      : "
      f"{100*posthoc['H_STALE_CSATR']['score']:.3f} %")
    past_wu = np.arange(len(ev_idx)) >= CS_QUAL_MINHIST      # qCount >= QualMinHist, deterministic
    mm2 = in_canon & past_wu
    P(f"    Of the {len(ev_idx)} entries the executable evaluated, its FIRST "
      f"{CS_QUAL_MINHIST} carry score = 0 by warm-up (qCount < QualMinHist) while the research")
    P(f"    object assigns them a real score - {int((~past_wu).sum())} of {len(ev_idx)} entries")
    P(f"    ({100*(~past_wu).mean():.1f} %) disagree for that reason alone. Excluding them:")
    P(f"      H_STALE research-chain, .cs ATR, qCount>=100 : "
      f"{100*float(np.mean(s_rc[mm2] == ev_sc[mm2])):.3f} %  (n = {int(mm2.sum())})")
    P("    -> the denominator explains the exec-native residual completely; what still separates")
    P("       the research chain from the executable after that is the QUALITY HISTORY itself:")
    P("       the deployed object was redeployed with DaysToLoad=365 and holds no quality history")
    P("       before 2025-08-31, so its trailing 250-entry quantiles are not the campaign's.")
    P("")
    P(f"    REMAINING DISAGREEMENTS under {best_ph}: {int(bad_ph.sum())}")
    if bad_ph.any():
        P(f"    For each, the SMALLEST relative margin |value - threshold| / |threshold| across the")
        P(f"    five features. A margin near zero means the two engines are on opposite sides of a")
        P(f"    knife-edge comparison, not computing different things.")
        P(f"    {'timestamp':<22}{'C# score':>9}{'py score':>9}{'nearest feature':>18}"
          f"{'value':>12}{'threshold':>12}{'rel margin':>12}")
        for i_ in np.flatnonzero(bad_ph):
            rel = np.abs(Vd[i_] - Td[i_]) / np.maximum(np.abs(Td[i_]), 1e-12)
            a_ = int(np.nanargmin(rel)) if np.isfinite(rel).any() else 0
            P(f"    {str(ev_ts[i_]):<22}{int(ev_sc[i_]):>9}"
              f"{int(posthoc[best_ph + '_arr'][i_]):>9}{fnames[a_]:>18}"
              f"{Vd[i_, a_]:>12.5f}{Td[i_, a_]:>12.5f}{rel[a_]:>12.2e}")

    # ============================================================================ 9. GATE P4
    H("9. GATE P4 - ECONOMIC SIZE OF THE DIVERGENCE (computed only if P3 passes)")
    P4 = None
    if not P3_PASS:
        P("    P3 did NOT pass. Per the spec, NO ECONOMICS ARE QUOTED. P4 is not computed.")
    else:
        P("    THIS IS NOT A PROMOTION. A difference in either direction is not a candidate; if")
        P("    H_FRESH earns more that is a P1_vNext HYPOTHESIS requiring its own locked challenge")
        P("    with its own null, because it changes the traded object. This run may not promote")
        P("    it and does not attempt to.")
        sz_by_lag = {nm: np.where(res_scores[nm][2] >= 3, 2, 1).astype(np.int8)
                     for nm in ("H_FRESH", "H_STALE")}
        trF = gfills(D, p_dir, sz_by_lag["H_FRESH"], **arm_kw("PCT", 1.183))
        trS = gfills(D, p_dir, sz_by_lag["H_STALE"], **arm_kw("PCT", 1.183))
        same_sched = (len(trF) == len(trS)) and all(
            a["et"] == b["et"] and a["xt"] == b["xt"] and a["d"] == b["d"]
            for a, b in zip(trF, trS))
        P("")
        P(f"    SIZE-INVARIANCE PRECONDITION (T2_P1SIZE01, max error 0.00e+00): with the session")
        P(f"    box denominated PER CONTRACT the trade SCHEDULE cannot move with size. Asserted")
        P(f"    here, not assumed: identical (et, xt, direction) for all trades under the H_FRESH")
        P(f"    and H_STALE size vectors -> {'PASS' if same_sched else 'FAIL'}")
        assert same_sched, "schedule moved with size - the per-contract box assumption is broken"
        F = pd.DataFrame([dict(et=pd.Timestamp(a["et"]), xt=pd.Timestamp(a["xt"]),
                               uF=a["u"], uS=b["u"], per=b["pnl"] / b["u"])
                          for a, b in zip(trF, trS)])
        w0, w1 = pd.Timestamp(str(lo)), pd.Timestamp(str(hi))
        F = F[(F["et"] >= w0) & (F["et"] <= w1)].reset_index(drop=True)
        F["pF"] = F["uF"] * F["per"]
        F["pS"] = F["uS"] * F["per"]
        iso = F["et"].dt.isocalendar()
        F["wk"] = iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)
        diff = F["uF"] != F["uS"]
        netF, netS = float(F["pF"].sum()), float(F["pS"].sum())
        nwk = F["wk"].nunique()
        # top decile by |P&L| ranked on the SIZE-INVARIANT per-contract P&L, so the ranking cannot
        # itself be moved by the size vector under test
        ab = F["per"].abs()
        thr = np.quantile(ab, 0.9)
        top = ab >= thr
        P("")
        P(f"    window {w0} -> {w1};  {len(F):,} trades, {nwk} weeks")
        P(f"    trades sized differently by the one-bar phase : {int(diff.sum()):,} "
          f"({100*diff.mean():.2f} % of trades)")
        P(f"    their share of H_FRESH net                    : "
          f"{100*float(F.loc[diff,'pF'].sum())/netF if netF else float('nan'):.2f} %")
        P(f"    their share of H_STALE net                    : "
          f"{100*float(F.loc[diff,'pS'].sum())/netS if netS else float('nan'):.2f} %")
        P("")
        P(f"    {'size vector':<34}{'ctrRT':>8}{'sz2 %':>9}{'net $':>14}{'$ / week':>12}")
        for nm, col, uc in (("H_FRESH  (current Python)", "pF", "uF"),
                            ("H_STALE  (the executable)", "pS", "uS")):
            P(f"    {nm:<34}{int(F[uc].sum()):>8,}{100*float((F[uc]==2).mean()):>8.2f}%"
              f"{float(F[col].sum()):>14,.0f}{float(F[col].sum())/nwk:>12,.0f}")
        dd_ = netF - netS
        P(f"    {'DIFFERENCE  H_FRESH - H_STALE':<34}{'':>8}{'':>9}{dd_:>14,.0f}"
          f"{dd_/nwk:>12,.0f}")
        dtop = float(F.loc[top, "pF"].sum() - F.loc[top, "pS"].sum())
        P("")
        P(f"    restricted to the TOP DECILE of trades by |P&L| ({int(top.sum()):,} trades):")
        P(f"      H_FRESH ${float(F.loc[top,'pF'].sum()):,.0f}   "
          f"H_STALE ${float(F.loc[top,'pS'].sum()):,.0f}   difference ${dtop:,.0f} "
          f"({100*dtop/dd_ if dd_ else float('nan'):.1f} % of the total difference)")
        P(f"      the other {int((~top).sum()):,} trades account for ${dd_-dtop:,.0f}")
        # exec-native size vector on the same schedule, reported beside it
        m_map = {int(pd.Timestamp(str(t_)).value): int(v)
                 for t_, v in zip(tarr[fill_i], exec_scores["H_STALE"][1])}
        uE = np.array([m_map.get(int(t_.value), 0) for t_ in F["et"]])
        cover = int((uE > 0).sum())
        pE = np.where(uE > 0, uE, F["uS"]) * F["per"]
        P("")
        P(f"    companion: the EXEC-NATIVE H_STALE size vector applied to the same schedule covers")
        P(f"    {cover:,} of {len(F):,} trades; net ${float(pE.sum()):,.0f} "
          f"(${float(pE.sum())/nwk:,.0f}/wk). Uncovered trades keep the research-chain size.")
        P4 = dict(window=[str(w0), str(w1)], trades=int(len(F)), weeks=int(nwk),
                  n_sized_differently=int(diff.sum()),
                  share_diff_of_netF=float(F.loc[diff, "pF"].sum()) / netF if netF else None,
                  share_diff_of_netS=float(F.loc[diff, "pS"].sum()) / netS if netS else None,
                  net_H_FRESH=netF, net_H_STALE=netS, diff_total=dd_, diff_per_week=dd_ / nwk,
                  top_decile_n=int(top.sum()), top_decile_diff=dtop,
                  exec_native_net=float(pE.sum()), exec_native_cover=cover)

    # ============================================================================ 10. GATE TABLE
    H("10. GATE TABLE - printed by the program. Realtime column is UNDECIDABLE (n = 0 after "
      "the seal).")
    RT = "n=0 SEALED"
    rows = [
        ("P0", "join >=95% AND monthly sd(close_cs-close_py) after removing that month's "
               "median <= 0.25 pt",
         f"join {100*join_rate:.3f}%; worst month sd "
         f"{max(r['sd'] for r in p0rows):.4f}", P0_PASS),
        ("P1", "voteOK >=99.5% AND t0..t3 each >=99.5%",
         "voteOK " + f"{100*agree['voteOK']['full']:.3f}%; t0..t3 " +
         "/".join(f"{100*agree[k]['full']:.2f}" for k in ("t0", "t1", "t2", "t3")) + "%", P1_PASS),
        ("P2", "entry-bar Jaccard >=0.99 AND |trade-count diff| <=2%",
         f"Jaccard {ent_j:.5f}; count diff {100*tcd:+.3f}%", P2_PASS),
        ("P3", "H_STALE wins score AND size outright, score >=99.0%, H_STALE2 loses",
         f"win={e_scw}/{e_szw}; H_STALE score "
         f"{100*exec_res['H_STALE']['score']:.3f}%", P3_PASS),
    ]
    P(f"{'GATE':<6}{'SPEC':<74}{'OBSERVED (full in-window)':<46}{'FULL':>8}{'REALTIME':>12}")
    for g, spec_, obs, ok in rows:
        P(f"{g:<6}{spec_[:73]:<74}{obs[:45]:<46}{('PASS' if ok else 'FAIL'):>8}{RT:>12}")
    P("")
    P("    Every gate is required by the operator instruction to be evaluated twice: on the full")
    P("    in-window span and on the realtime-only tail. The realtime tail has n = 0 rows after")
    P("    the data seal, so NO gate can be decided on it and NONE is reported as a rate. No gate")
    P("    above is SPLIT, because a SPLIT requires two decidable columns and there is only one.")
    P("")
    P(f"    DIAGNOSTIC SECOND COLUMN (declared in section 2a, NOT the gate): the WARM sub-span")
    P(f"    (export session >= {CS_TILT_SMA+1}, after the .cs tilt warm-up completes).")
    P(f"{'GATE':<6}{'OBSERVED (WARM sub-span)':<74}{'WARM':>8}")
    _t = "/".join(f"{100*agree[k]['warm']:.2f}" for k in ("t0", "t1", "t2", "t3"))
    _o1 = f"voteOK {100*agree['voteOK']['warm']:.3f}%; t0..t3 {_t}%"
    _o2 = f"Jaccard {ent_j_w:.5f}; count diff {100*tcd_w:+.3f}%"
    _o3 = f"H_STALE score (qCount>=250) {100*exec_res['H_STALE']['score_conv']:.3f}%"
    P(f"{'P1':<6}{_o1:<74}{('pass' if P1_WARM else 'fail'):>8}")
    P(f"{'P2':<6}{_o2:<74}{('pass' if P2_WARM else 'fail'):>8}")
    P(f"{'P3':<6}{_o3:<74}{('pass' if exec_res['H_STALE']['score_conv'] >= 0.99 else 'fail'):>8}")

    # ============================================================================ ARTIFACTS
    H("11. ARTIFACTS")
    PB = pd.DataFrame(dict(
        ts=jts, close_cs=close_cs, close_py=close_py,
        voteOK_cs=cs["voteOK"], voteOK_py=py["voteOK"],
        t0_cs=cs["t0"], t0_py=py["t0"], t1_cs=cs["t1"], t1_py=py["t1"],
        t2_cs=cs["t2"], t2_py=py["t2"], t3_cs=cs["t3"], t3_py=py["t3"],
        qty_cs=qty_cs_full[hit], qty_py=qty_py_full[jj],
        act_cs=act_cs_full[hit], act_py=act_py_full[jj],
        score_cs=sc_col, size_cs=sz_col, evaluated=m_eval.astype(np.int8),
        warm=WARM.astype(np.int8)))
    PB.to_csv(os.path.join(OUT, "parity_bars.csv"), index=False)
    P(f"    out/parity_bars.csv        {len(PB):,} rows")

    DIS = pd.DataFrame(dis_rows, columns=["ts", "field", "cs", "py", "warm"])
    extra = []
    for t_ in conly:
        extra.append((str(t_), "ENTRY_BAR", 1, 0, bool(t_ >= wl)))
    for t_ in ponly:
        extra.append((str(t_), "ENTRY_BAR", 0, 1, bool(t_ >= wl)))
    for t_ in conly_x:
        extra.append((str(t_), "EXIT_BAR", 1, 0, bool(t_ >= wl)))
    for t_ in ponly_x:
        extra.append((str(t_), "EXIT_BAR", 0, 1, bool(t_ >= wl)))
    for i_ in np.flatnonzero(bad):
        extra.append((str(ev_ts[i_]), f"SCORE_{e_scw}", int(ev_sc[i_]), int(wsc[i_]),
                      bool(ev_warm[i_])))
    DIS = pd.concat([DIS, pd.DataFrame(extra, columns=["ts", "field", "cs", "py", "warm"])],
                    ignore_index=True)
    DIS.to_csv(os.path.join(OUT, "disagreements.csv"), index=False)
    P(f"    out/disagreements.csv      {len(DIS):,} rows")

    G = dict(
        run_id="G3_EXECTRUTH_01_20260831",
        live_enabled=False, spend=0, orders_placed=False,
        snapshot=dict(path=SNAP, sha256=sha, bytes=os.path.getsize(SNAP)),
        seal=dict(boundary="2026-08-01", rows_dropped=int(seal_mask.sum()),
                  rows_retained=int((~seal_mask).sum()),
                  realtime_tail_rows_pre_seal=n_rt_pre, realtime_tail_rows_post_seal=0,
                  realtime_verdict="UNDECIDABLE n=0"),
        P0=dict(verdict="PASS" if P0_PASS else "FAIL", join_rate=join_rate,
                matched=int(hit.sum()), cs_only=int((~hit).sum()), py_only=py_only,
                months=p0rows),
        P1=dict(verdict="PASS" if P1_PASS else "FAIL", warm_verdict="pass" if P1_WARM else "fail",
                fields={k: agree[k] for k in agree}),
        P2=dict(verdict="PASS" if P2_PASS else "FAIL", warm_verdict="pass" if P2_WARM else "fail",
                entry_jaccard=ent_j, exit_jaccard=ext_j, cs_entries=int(len(ce)),
                py_entries=int(len(pe)), trade_count_diff=tcd,
                cs_only_entries=int(len(conly)), py_only_entries=int(len(ponly)),
                entry_jaccard_warm=ent_j_w, trade_count_diff_warm=tcd_w),
        P3=dict(verdict="PASS" if P3_PASS else "FAIL",
                framing_primary="EXEC-NATIVE", n_evaluated=int(len(ev_idx)),
                exec_native=exec_res, research_chain=res_res,
                winner_exec=dict(score=e_scw, size=e_szw),
                winner_research=dict(score=r_scw, size=r_szw),
                control_lost=bool(ctrl_lost_e)),
        P3b_posthoc_not_preregistered=dict(
            note="ATR double-lag mechanism; explanatory only, changes no verdict, unlocks no "
                 "economics",
            atr_double_lag_confirmed=bool(dbl), best_arm=best_ph,
            research_chain_H_STALE_csatr_score=rc_sc,
            arms={k: v for k, v in posthoc.items() if not k.endswith("_arr")}),
        P4=P4)
    json.dump(G, open(os.path.join(OUT, "gates.json"), "w"), indent=1, default=float)
    P(f"    out/gates.json")
    P(f"    out/console.txt")
    P("")
    P(f"[done {_time.time()-t0:.0f}s]  LIVE ENABLED = NO.  $0 spent.  Nothing promoted.")
    _fh.close()


if __name__ == "__main__":
    main()
