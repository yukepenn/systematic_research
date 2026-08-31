"""G3_EXECTRUTH_02 - EXECUTABLE OBJECT TRUTH, second attempt.

Executes runs/G3_EXECTRUTH_02_20260831/spec.yaml, committed BEFORE any corrected-arm statistic
was recomputed. Every gate clause in that spec is coded here and the gate table is printed BY
THIS PROGRAM. Zero free parameters: H_CORRECTED is fully determined by two source files.

The harness is REUSED from runs/G3_EXECTRUTH_01_20260831/src/exectruth.py so the two runs are
exactly comparable. The copied chain variants below are byte-for-byte the predecessor's, which
were themselves asserted bit-identical to their canonical originals.

PROHIBITIONS HONOURED (spec section 4 / operator instruction)
  - no order / deploy / enable / disable / backtest / CrossTrade call of any kind
  - no edit to any production .cs file or to anything under research/weekly_edge/src/
    (the ATR double lag is DIAGNOSED here, never patched)
  - no read of any session >= 2026-08-01: dropped before any statistic, count printed
  - no re-snapshot of the export; the predecessor's sha256 is verified and asserted
  - no p-value / hypothesis test anywhere; the gates are agreement thresholds
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
from run_we_w03 import cd_signals                                          # noqa: E402
from run_we_w17 import load_deep                                           # noqa: E402
from run_we_w19 import MEMBERS, QS                                         # noqa: E402
from run_we_w26 import fills_daily                                         # noqa: E402
from run_we_w37 import causal_score, MINHIST                               # noqa: E402
from run_we_w39 import WIN                                                 # noqa: E402
from run_we_w97 import votes                                               # noqa: E402
from run_we_w98 import gfills, arm_kw                                      # noqa: E402
from we_fastctx import fast_build_context, fast_intraday_features          # noqa: E402

RUN = os.path.join(ROOT, "runs", "G3_EXECTRUTH_02_20260831")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
# HARD RULE: the predecessor's snapshot, never re-snapshotted.
SNAP = os.path.join(ROOT, "runs", "G3_EXECTRUTH_01_20260831", "out", "cs_export_snapshot.csv")
SNAP_SHA = "403131d10ab7027d7bbb904204f3409ff6b993daa0a947e703e26ff34ce99999"
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")

# ---- constants READ FROM SOURCE, never chosen here -------------------------------------------
SEAL = np.datetime64("2026-08-01T00:00:00")          # CLAUDE.md section 5: >= this is VIRGIN
BURN = np.datetime64("2026-05-31T00:00:00")          # CLAUDE.md section 5: 05-31 -> 07-31 BURNED
RT_START = np.datetime64("2026-08-31T12:28:00")
A_CANON = np.datetime64("2022-07-01")                # run_we_w103.py:39
B_CANON = np.datetime64("2026-08-01")                # run_we_w103.py:40
L13 = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
CS_TILT_SMA = 50          # WeeklyEdgeP1PCT_v3.cs:1067  tilt is 0 until sessCloses.Count > 50
CS_QUAL_WINDOW = 250      # :773 QualWindow
CS_QUAL_MINHIST = 100     # :773 QualMinHist
CS_BMOM_BAND_DAYS = 14    # :1034 rthDays >= BmomBandDays
CS_RNG_MIN = 20           # :1118 rngHist[tod].Count >= 20
CS_RNG_MEDWIN = 60        # :1118 MedianLast(hist, 60)
CS_RNG_CAP = 200          # :968  lst.Count > 200 -> RemoveAt(0)
CS_SLOT_CAP = 60          # :1058 slotHist cap
CS_SLOT_MEAN = 14         # :1041 Math.Min(14, past.Count)

# predecessor's published EXEC-NATIVE H_STALE numbers (runs/G3_EXECTRUTH_01_20260831/REPORT.md)
PRED_STALE_SCORE = 0.96977
PRED_STALE_SIZE = 0.98992
Q0_TOL_PP = 0.05          # spec Q0: within 0.05 percentage points of BOTH

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
# COPIED CHAIN VARIANTS - byte-for-byte the predecessor's, so the two runs are comparable
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
    features are read at `ent_i - lag` instead of `ent_i`. Asserted == canonical at lag = 0."""
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


def score_detail(Xd, ent_i, window, lag):
    """Per-feature value and threshold at every evaluated entry, for the knife-edge test."""
    feats = [("dist_open", +1, 2 / 3), ("prev_ret", -1, 1 / 3), ("runlen", +1, 0.9),
             ("dist_vwap", +1, 2 / 3), ("delta_mag", +1, 2 / 3)]
    src = np.maximum(np.asarray(ent_i) - lag, 0)
    vals = {k: Xd[k][src] for k, _, _ in feats}
    N = len(ent_i)
    V = np.full((N, 5), np.nan)
    T = np.full((N, 5), np.nan)
    for j in range(N):
        if j < MINHIST:
            continue
        lo_ = max(0, j - window)
        for a_, (k, sgn, q) in enumerate(feats):
            hist = vals[k][lo_:j]
            V[j, a_] = vals[k][j]
            T[j, a_] = np.nanquantile(hist, q)
    return V, T, [f[0] for f in feats]


def gfills_path(D, dir_arr, size_at_entry=None, halt=1300.0, target=1000.0, per_ctr=False):
    """VERBATIM COPY of research/weekly_edge/src/run_we_w98.py::gfills, plus a per-bar signed
    position path so an ACTION series can be derived from the POSITION PATH ALONE."""
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


# ==================================================================================================
# THE ONE-LINE VARIANTS THAT ARE THIS RUN'S SUBJECT
# ==================================================================================================
def fast_intraday_features_nolag(D):
    """VERBATIM COPY of we_fastctx.fast_intraday_features with EXACTLY ONE LINE REMOVED:
        line 46   atr = np.concatenate([[atr[0]], atr[:-1]])
    so the returned atr is the ATR THROUGH BAR j (no lag at all). Used only to construct the
    named control C3. Verified against the canonical by re-applying the removed line."""
    n, sid = D["n"], D["sid"]
    t, o, h, l, c = D["t"], D["o"], D["h"], D["l"], D["c"]
    hm = ((t - t.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60)
    rng = np.zeros(n); dmove = np.zeros(n)
    starts = np.flatnonzero(D["fb"])
    ends = np.concatenate([starts[1:], [D["n"]]])
    for a, b in zip(starts, ends):
        hh = np.maximum.accumulate(h[a:b]); ll = np.minimum.accumulate(l[a:b])
        r = hh - ll
        rng[a:b] = np.concatenate([[0.0], r[:-1]])
        dm = np.abs(c[a:b] - o[a])
        dmove[a:b] = np.concatenate([[0.0], dm[:-1]])
    tr = np.maximum(h - l, np.maximum(np.abs(h - np.roll(c, 1)), np.abs(l - np.roll(c, 1))))
    tr[0] = h[0] - l[0]
    atr = pd.Series(tr).rolling(14, min_periods=1).mean().values
    # <<< we_fastctx.py:46 REMOVED HERE, and nothing else >>>
    df = pd.DataFrame(dict(tod=hm, r=rng))
    g = df.groupby("tod")["r"]
    med = g.transform(lambda x: x.rolling(60, min_periods=1).median().shift(1)).to_numpy()
    prior = g.cumcount().to_numpy()
    norm = np.where(prior >= 20, np.nan_to_num(med, nan=0.0), 0.0)
    return rng, dmove, atr, norm


def build_context_atrlag(D, ifeat, extra_atr_lag):
    """VERBATIM COPY of we_fastctx.fast_build_context with EXACTLY ONE LINE PARAMETERISED:
        line 81   atr_l = np.concatenate([[atr14[0]], atr14[:-1]])     if extra_atr_lag
                  atr_l = atr14                                        otherwise
    Nothing else differs. extra_atr_lag = True reproduces the canonical bit for bit (harness F).
    extra_atr_lag = False is the ENTIRE content of hypothesis H_CORRECTED."""
    n = D["n"]
    c, o, v = D["c"], D["o"], D["v"]
    rng_, dmove, atr14, norm = ifeat
    ratio = np.where(norm > 0, rng_ / np.maximum(norm, 1e-9), 1.0)

    def lag_b(x):
        return np.concatenate([[True], x[:-1]])
    _, cd = cd_signals(D)
    dL, dS = lag_b(cd >= 0), lag_b(cd <= 0)

    starts = np.flatnonzero(D["fb"])
    ends = np.concatenate([starts[1:], [D["n"]]])
    seg = np.repeat(np.arange(len(starts)), ends - starts)
    pv = pd.Series(c * v).groupby(seg).cumsum().to_numpy()
    vv = pd.Series(v).groupby(seg).cumsum().to_numpy()
    vwap = np.where(vv > 0, pv / np.maximum(vv, 1e-300), np.nan)
    sopen = np.repeat(o[starts], ends - starts)

    atr_l = np.concatenate([[atr14[0]], atr14[:-1]]) if extra_atr_lag else atr14
    vwap_l = np.concatenate([[np.nan], vwap[:-1]])
    c_l = np.concatenate([[c[0]], c[:-1]])
    sess_ret = c[ends - 1] - o[starts]
    prev_ret = np.concatenate([[0.0], sess_ret[:-1]])[seg]

    up = np.concatenate([[0], np.sign(np.diff(c))])
    rl = np.zeros(n); r = 0
    for i in range(1, n):
        r = r + 1 if up[i] == up[i - 1] and up[i] != 0 else (1 if up[i] != 0 else 0)
        rl[i] = r * (1 if up[i] > 0 else -1)
    rl_l = np.concatenate([[0], rl[:-1]])
    volnorm = pd.Series(v).rolling(240, min_periods=30).mean().values
    delta_mag = np.concatenate([[0.0], (np.abs(cd) / np.maximum(volnorm, 1e-9))[:-1]])
    return dict(ratio=ratio, norm=norm, dL=dL, dS=dS, atr_l=atr_l,
                dist_open=(c_l - sopen) / np.maximum(atr_l, 1e-9),
                dist_vwap=(c_l - vwap_l) / np.maximum(atr_l, 1e-9),
                prev_ret=prev_ret, runlen=rl_l, delta_mag=delta_mag)


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


# ==================================================================================================
# FORWARD SIMULATIONS OF THE .cs's OWN ACCUMULATORS OVER ITS OWN LOAD SPAN
# Each one is a transcription of a named block of WeeklyEdgeP1PCT_v3.cs and has no free parameter.
# They exist so a residual can be ASSIGNED TO A MECHANISM rather than merely localised.
# ==================================================================================================
def sim_norm_ratio(tod, rng_prev, sess_idx):
    """WeeklyEdgeP1PCT_v3.cs:963-970 (flush at session start), :1116-1119 (norm/ratio),
    :1210-1212 (what CacheLagged records). rngHist is per minute-of-day, appended one value per
    COMPLETED session, capped at 200, read as the median of its LAST 60, gated at Count >= 20."""
    n = len(tod)
    norm = np.zeros(n)
    hist = {}
    pk, pv = [], []
    cur = -1
    for i in range(n):
        if sess_idx[i] != cur:                      # firstBar: flush the previous session
            for k_, v_ in zip(pk, pv):
                lst = hist.get(k_)
                if lst is None:
                    lst = []; hist[k_] = lst
                lst.append(v_)
                if len(lst) > CS_RNG_CAP:
                    lst.pop(0)
            pk, pv = [], []
            cur = sess_idx[i]
        lst = hist.get(tod[i])
        if lst is not None and len(lst) >= CS_RNG_MIN:
            w = sorted(lst[-CS_RNG_MEDWIN:])
            k = len(w)
            norm[i] = w[k // 2] if (k % 2) else 0.5 * (w[k // 2 - 1] + w[k // 2])
        pk.append(tod[i]); pv.append(rng_prev[i])
    ratio = np.where(norm > 0, rng_prev / np.maximum(norm, 1e-9), 1.0)
    return norm, ratio


def sim_tilt(close, sess_idx, last_of_sess):
    """WeeklyEdgeP1PCT_v3.cs:1064-1073. sessCloses starts EMPTY at the export's first bar."""
    n = len(close)
    out = np.zeros(n, np.int32)
    sc = []
    tl = 0
    for i in range(n):
        out[i] = tl
        if last_of_sess[i]:
            sc.append(close[i])
            if len(sc) > CS_TILT_SMA:
                tl = int(np.sign(close[i] - float(np.mean(sc[-CS_TILT_SMA:]))))
            if len(sc) > 600:
                sc.pop(0)
    return out


def sim_dL(close, vol, first_of_sess):
    """WeeklyEdgeP1PCT_v3.cs:975 (cumDelta reset at firstBar), :1126 (dL from lagCumDelta),
    :1220-1222 (the recursion). NOTE lagCumDelta is NOT reset at firstBar - only cumDelta is -
    so the session's first bar reads the PREVIOUS session's final value, exactly as Python's
    lag_b(cd >= 0) does. Run here on the PYTHON volume series: if it reproduces the .cs column
    the volume series agree; if it reproduces Python instead, they do not."""
    n = len(close)
    out = np.zeros(n, np.int32)
    cum = 0.0
    lagcum = 0.0
    lagc = np.nan
    for i in range(n):
        if first_of_sess[i]:
            cum = 0.0
        out[i] = 1 if lagcum >= 0 else 0
        sgn = 0.0 if np.isnan(lagc) else float(np.sign(close[i] - lagc))
        cum += sgn * vol[i]
        lagcum = cum
        lagc = close[i]
    return out


def sim_bmom(hm4, close, open_, vol, last_of_sess):
    """WeeklyEdgeP1PCT_v3.cs:1023-1059. slotHist starts EMPTY at the export's first bar and is
    capped at 60 prior RTH days; the band is the mean of its LAST min(14, count) entries."""
    n = len(close)
    out = np.zeros(n, np.int32)
    slot = {}
    today = {}
    rth_open = False
    rth_days = 0
    bm = 0
    o930 = 0.0
    vpv = 0.0
    vv = 0.0
    for i in range(n):
        hm = int(hm4[i])
        px = close[i]
        if hm == 93100:
            o930 = open_[i]; vpv = 0.0; vv = 0.0; rth_open = True
            today = {}; bm = 0
        if rth_open and 93100 <= hm <= 160000:
            vpv += px * vol[i]; vv += vol[i]
            vw = (vpv / vv) if vv > 0 else px
            today[hm] = abs(px - o930)
            if hm <= 155400 and rth_days >= CS_BMOM_BAND_DAYS:
                past = slot.get(hm)
                if past:
                    kk = min(CS_SLOT_MEAN, len(past))
                    mtod = float(np.mean(past[-kk:]))
                    s = 0
                    if px > max(o930 + mtod, vw):
                        s = 1
                    elif px < min(o930 - mtod, vw):
                        s = -1
                    if s != 0:
                        bm = s
            if hm >= 155700 or last_of_sess[i]:
                bm = 0
        if last_of_sess[i] and rth_open:
            for k_, v_ in today.items():
                lst = slot.get(k_)
                if lst is None:
                    lst = []; slot[k_] = lst
                lst.append(v_)
                if len(lst) > CS_SLOT_CAP:
                    lst.pop(0)
            rth_days += 1
            rth_open = False
        out[i] = bm
    return out


def sim_rthdays(hm4, last_of_sess):
    """rthDays as of each bar - the .cs's own B-MOM warm-up counter (:1058)."""
    n = len(hm4)
    out = np.zeros(n, np.int32)
    rth_open = False
    d = 0
    for i in range(n):
        if int(hm4[i]) == 93100:
            rth_open = True
        out[i] = d
        if last_of_sess[i] and rth_open:
            d += 1
            rth_open = False
    return out


# ==================================================================================================
def main():
    global _fh
    t0 = _time.time()
    _fh = open(os.path.join(OUT, "console.txt"), "w", encoding="utf-8")

    P("=" * 118)
    P("G3_EXECTRUTH_02_20260831 - EXECUTABLE OBJECT TRUTH, SECOND ATTEMPT")
    P("The predecessor's P3 FAILED (96.977 % against 99.0 %). That failure STANDS and is not")
    P("reinterpreted. This run tests a DIFFERENT hypothesis about the object's structure, read out")
    P("of the source on both sides, with zero free parameters, against a RAISED 99.5 % bar.")
    P("spec: runs/G3_EXECTRUTH_02_20260831/spec.yaml (committed before any corrected-arm statistic)")
    P("LIVE ENABLED = NO.  $0 spent.  No order, no deploy, no backtest, no CrossTrade call.")
    P("EVIDENCE STATUS: VERIFICATION - nothing is selected, tuned, or promoted by this run.")
    P("NO P-VALUE APPEARS ANYWHERE IN THIS RUN. The gates are agreement thresholds.")
    P("=" * 118)

    # ============================================================================ 0. PROVENANCE
    H("0. PROVENANCE - the SAME snapshot as the predecessor, verified by hash, never re-taken")
    h = hashlib.sha256()
    with open(SNAP, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    sha = h.hexdigest()
    P(f"    snapshot      {SNAP}")
    P(f"    sha256        {sha}")
    P(f"    spec requires {SNAP_SHA}")
    P(f"    MATCH         {'YES' if sha == SNAP_SHA else 'NO - HARD STOP'}")
    P(f"    bytes         {os.path.getsize(SNAP):,}")
    assert sha == SNAP_SHA, "snapshot hash does not match the spec - the run is not comparable"

    E = pd.read_csv(SNAP)
    ets = pd.to_datetime(E["pyts"]).values.astype("datetime64[s]")
    ndup = len(ets) - len(np.unique(ets))
    nmono = int((np.diff(ets).astype("int64") <= 0).sum())
    P(f"    data rows     {len(E):,}   duplicates {ndup}   non-monotonic {nmono}")
    P(f"    span          {ets[0]}  ->  {ets[-1]}")
    assert ndup == 0 and nmono == 0

    # ============================================================================ 1. THE SEAL
    H("1. DATA SEAL - executed BEFORE any statistic is computed (CLAUDE.md section 5)")
    seal_mask = ets >= SEAL
    n_rt_pre = int((ets >= RT_START).sum())
    P(f"    rows with timestamp >= 2026-08-01 (VIRGIN)        DROPPED : {int(seal_mask.sum()):>8,}")
    P(f"    rows retained (in-window, < 2026-08-01)                   : {int((~seal_mask).sum()):>8,}")
    E = E.loc[~seal_mask].reset_index(drop=True)
    ets = ets[~seal_mask]
    P(f"    retained span                                             : {ets[0]} -> {ets[-1]}")
    P(f"    rows at/after the current deployment start (12:28 ET 08-31): {n_rt_pre:,} - all sealed")
    P(f"    REALTIME-tail rows surviving the seal                      : 0")
    P("    Consequence, stated before any gate is read: every number in this run is computed on")
    P("    bars NT8 produced by HISTORICAL processing. This run cannot split historical from")
    P("    realtime behaviour, exactly as the predecessor could not.")

    # ============================================================== 2. DECLARATIONS BEFORE RESULTS
    H("2. DECLARATIONS MADE BEFORE ANY RESULT IS COMPUTED")
    P("    (a) THE FOUR ARMS. All four share one code path; they differ ONLY in which ATR array")
    P("        the context divides by, and in the index shift applied to the feature read.")
    P("")
    P(f"        {'arm':<14}{'atr_l is ...':<34}{'features read at':<22}{'role'}")
    P(f"        {'H_CORRECTED':<14}{'ATR through bar j-1 (1 lag)':<34}{'fill bar - 1':<22}"
      f"{'THE HYPOTHESIS'}")
    P(f"        {'C1':<14}{'ATR through bar j-2 (2 lags)':<34}{'fill bar - 1':<22}"
      f"{'predecessor H_STALE'}")
    P(f"        {'C2':<14}{'ATR through bar j-1 (1 lag)':<34}{'fill bar - 0':<22}"
      f"{'fresh index shift'}")
    P(f"        {'C3':<14}{'ATR through bar j   (0 lags)':<34}{'fill bar - 1':<22}"
      f"{'both ATR lags removed'}")
    P("")
    P("        H_CORRECTED removes we_fastctx.py:81 and NOTHING ELSE. No threshold, no window, no")
    P("        feature, no sign moves. The .cs side is WeeklyEdgeP1PCT_v3.cs:1213-1218 (lagAtr is")
    P("        the true range through THIS bar) with :1237 (lagClose = this bar's close) - both")
    P("        frozen at the same instant, so the executable's numerator and denominator share one")
    P("        bar. The research chain's do not.")
    P("")
    P("    (b) WIN IS DEFINED BEFORE IT IS MEASURED. H_CORRECTED 'strictly beats' a control when")
    P("        its agreement is STRICTLY GREATER - a tie is a loss. Both metrics must beat all")
    P("        three controls. Q1 PASS = score >= 99.5 % AND size >= 99.5 % AND strict win on")
    P("        score against C1, C2, C3 AND strict win on size against C1, C2, C3.")
    P("")
    P("    (c) WARM-UP SUB-SPAN, taken unchanged from the predecessor, which derived it FROM SOURCE")
    P(f"        before computing anything: WeeklyEdgeP1PCT_v3.cs:1067 leaves tilt identically 0")
    P(f"        until sessCloses.Count > TiltSma = {CS_TILT_SMA}, so WARM = export session index")
    P(f"        >= {CS_TILT_SMA + 1}. Q2 is read on WARM, exactly as the spec instructs. The FULL-")
    P("        SPAN entry Jaccard of 0.852 is NOT re-litigated here and is not expected to pass: it")
    P("        is a warm-up artefact of the executable itself and is recorded as such.")
    P("")
    P("    (d) Q3's RESIDUAL POPULATION and its CAUSE TAXONOMY, both fixed here. The population is")
    P("        every (bar, field) disagreement in the eleven exported state fields on the joined")
    P("        bars, plus every entry-bar and exit-bar action mismatch, plus every score/size")
    P("        mismatch under H_CORRECTED - the same population the predecessor tabulated. Each")
    P("        residual gets EXACTLY ONE cause, by this priority order:")
    P("          1  TILT_*        tilt: the .cs's own 50-session SMA over its own load span")
    P("          2  BMOM_*        bmom: the .cs's own slotHist over its own load span")
    P("          3  NORM_*        ratio/nThr: the .cs's own rngHist over its own load span")
    P("          4  CUMDELTA_*    dL: the .cs's own session-local cumDelta recursion")
    P("          5  CS_INPUT_*    downstream fields the HYBRID vote reproduces once the")
    P("                           executable's OWN tilt/bmom/ratio/norm/dL are substituted in")
    P("          6  DATA_COVERAGE bars in a session where the two files do not hold the same")
    P("                           minutes, or in the session immediately after one (the .cs")
    P("                           accumulators carry across the boundary)")
    P("          7  SCORE_KNIFE_EDGE  a score residual whose smallest relative feature margin")
    P("                           is below 1e-6")
    P("          8  UNEXPLAINED   reported as a fraction, never rounded away")
    P("        Each of causes 1-4 is decided by a FORWARD SIMULATION of the named .cs block over")
    P("        the export's own bars. A cause is assigned only when the simulation REPRODUCES the")
    P("        executable's value on that bar. PASS = >= 95 % assigned.")

    # ============================================================================ 3. SUBSTRATE
    H("3. THE PYTHON RESEARCH OBJECT - the canonical chain, unmodified")
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid, fb, lb = D["n"], D["t"], D["sid"], D["fb"], D["lb"]
    P(f"    load_deep('2022-01-01','2026-07-31 17:00'): {n:,} bars / {D['n_sess']:,} sessions, "
      f"{tarr[0]} -> {tarr[-1]}  [{_time.time()-t0:.0f}s]")
    assert tarr[-1] < SEAL, "substrate crosses the seal"
    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    assert mem.shape[0] == n and bmom.shape[0] == n and tilt.shape[0] == n
    P(f"    mem_ext.npz cache covers the substrate exactly: mem {mem.shape}  [used as is]")

    ifeat = fast_intraday_features(D)
    rng_raw, _dmove, atr14, norm_py = ifeat
    ifeat_nolag = fast_intraday_features_nolag(D)
    atr_raw = ifeat_nolag[2]
    ok_g = bool(np.array_equal(np.concatenate([[atr_raw[0]], atr_raw[:-1]]), atr14))
    P(f"    HARNESS G: re-applying the removed line to the no-lag ATR restores the canonical "
      f"atr14 ... {'PASS' if ok_g else 'FAIL'}")
    assert ok_g

    X = build_context_atrlag(D, ifeat, extra_atr_lag=True)          # the canonical research object
    Xc = fast_build_context(D, ifeat=ifeat)
    bad_f = []
    for k in Xc:
        a, b = np.asarray(Xc[k]), np.asarray(X[k])
        if a.dtype == bool:
            if not (a == b).all():
                bad_f.append(k)
        elif not (np.array_equal(a, b) or
                  (np.allclose(a, b, rtol=0, atol=0, equal_nan=True))):
            bad_f.append(k)
    P(f"    HARNESS F: build_context_atrlag(extra=True) == we_fastctx.fast_build_context, every "
      f"key bit for bit ... {'PASS' if not bad_f else 'FAIL ' + str(bad_f)}")
    assert not bad_f
    XC = build_context_atrlag(D, ifeat, extra_atr_lag=False)        # H_CORRECTED / C2
    XN = build_context_atrlag(D, ifeat_nolag, extra_atr_lag=False)  # C3
    P(f"    HARNESS H: the three contexts differ ONLY in atr_l (and the two quotients it divides)")
    def _same(a, b):
        a, b = np.asarray(a), np.asarray(b)
        if a.dtype == bool:
            return bool((a == b).all())
        return bool(np.array_equal(a, b) or
                    np.allclose(a, b, rtol=0, atol=0, equal_nan=True))
    diffk = sorted(k for k in X if not _same(X[k], XC[k]))
    P(f"               X vs XC differ on: {diffk}   "
      f"{'PASS' if diffk == ['atr_l', 'dist_open', 'dist_vwap'] else 'FAIL'}")
    assert diffk == ["atr_l", "dist_open", "dist_vwap"]
    P(f"    VERIFIED: X['atr_l'] is the ATR through bar j-2, XC['atr_l'] through bar j-1, "
      f"XN['atr_l'] through bar j")
    P(f"               lag(XC.atr_l) == X.atr_l : "
      f"{np.array_equal(np.concatenate([[XC['atr_l'][0]], XC['atr_l'][:-1]]), X['atr_l'])}"
      f"    lag(XN.atr_l) == XC.atr_l : "
      f"{np.array_equal(np.concatenate([[XN['atr_l'][0]], XN['atr_l'][:-1]]), XC['atr_l'])}")
    P(f"    contexts built  [{_time.time()-t0:.0f}s]")

    vl, vs_, TG, nMem_py, nThr_py, dL_py, ratio_py = votes_instrumented(D, mem, bmom, tilt, X, bmom)
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
    TGa = np.vstack([TG[k] for k in MEMBERS])
    P(f"    per-set targets t0..t3 ordered {list(MEMBERS)} == .cs SETLEN {{5,6,7,13}}")

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))
    bb = fills_daily(D, p_dir, halt=1300, target=1000)
    ee = np.array([i_of(x["et"]) for x in bb if A_CANON <= np.datetime64(x["et"]) < B_CANON])
    P(f"    canonical entry schedule (fills_daily, 2022-07-01 -> 2026-08-01): {len(ee):,} entries"
      f"  [{_time.time()-t0:.0f}s]")
    sc_canon, _ = causal_score(X, ee, window=WIN)
    sc0_lag, _ = causal_score_lag(X, ee, window=WIN, lag=0)
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
    P(f"    HARNESS E: gfills called with per_ctr = {kw['per_ctr']} (the .cs session box "
      f"accumulates PER CONTRACT, .cs:934-938/:1164-1167)  "
      f"{'PASS' if kw['per_ctr'] is True else 'FAIL'}")
    assert kw["per_ctr"] is True
    P(f"    canonical P1/PCT object: {len(tr_canon):,} trades  [{_time.time()-t0:.0f}s]")

    # ============================================================================ 4. THE JOIN
    H("4. THE JOIN - the same inner join on timestamp the predecessor used (its P0 PASSED)")
    pos = np.searchsorted(tarr, ets)
    posc = np.minimum(pos, n - 1)
    hit = tarr[posc] == ets
    jj = posc[hit]
    jts = ets[hit]
    close_cs = E["close"].to_numpy(float)[hit]
    close_py = D["c"][jj]
    dclose = close_cs - close_py
    P(f"    C# rows in-window {len(ets):,}   matched {int(hit.sum()):,} "
      f"({100*hit.mean():.3f} %)   C#-only {int((~hit).sum()):,}")
    P(f"    bars where close_cs != close_py: {int((dclose != 0).sum()):,} of {len(dclose):,} "
      f"({100*np.mean(dclose != 0):.4f} %)   max |d| {np.abs(dclose).max():.4f} pt")
    P(f"    PRECONDITION (predecessor P0, PASSED there, re-verified here): join >= 95 % and the")
    P(f"    two price series are identical up to two bars. "
      f"{'OK' if hit.mean() >= 0.95 else 'FAILED'}")
    assert hit.mean() >= 0.95

    ex_gap = np.zeros(len(ets), bool)
    ex_gap[0] = True
    ex_gap[1:] = np.diff(ets).astype("timedelta64[m]").astype(np.int64) > 60
    ex_sess = np.cumsum(ex_gap) - 1
    ex_sess_j = ex_sess[hit]
    WARM = ex_sess_j >= (CS_TILT_SMA + 1)
    wl = jts[WARM][0]
    P(f"    export sessions {int(ex_sess[-1])+1};  declared WARM (session >= {CS_TILT_SMA+1}): "
      f"{int(WARM.sum()):,} of {len(WARM):,} joined bars ({100*WARM.mean():.1f} %), from {wl}")

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
    FIELDS = ("nMem", "nThr", "dL", "ratio", "voteOK", "tilt", "bmom", "t0", "t1", "t2", "t3")
    ACTION_BEARING = ("voteOK", "t0", "t1", "t2", "t3")

    # ==================================================================== 5. Q0 - REPRODUCTION
    H("5. Q0 - PREDECESSOR REPRODUCTION. If this fails the harness changed and NOTHING is "
      "comparable.")
    m_eval = (Ej["qty"].to_numpy(np.int32) == 0) & (Ej["voteOK"].to_numpy(np.int32) == 1) & \
             (Ej["stopped"].to_numpy(np.int32) == 0)
    sc_col = Ej["score"].to_numpy(np.int32)
    sz_col = Ej["size"].to_numpy(np.int32)
    ev_idx = np.flatnonzero(m_eval)
    fill_i = jj[ev_idx] + 1
    okf = (fill_i < n) & (~fb[np.minimum(fill_i, n - 1)])
    ev_idx = ev_idx[okf]
    fill_i = fill_i[okf]
    ev_ts = jts[ev_idx]
    ev_sc = sc_col[ev_idx]
    ev_sz = sz_col[ev_idx]
    ev_warm = WARM[ev_idx]
    conv = np.arange(len(ev_idx)) >= CS_QUAL_WINDOW
    P(f"    exec-native framing, identical to the predecessor: qCount from 0, MinHist "
      f"{CS_QUAL_MINHIST}, Window {CS_QUAL_WINDOW}")
    P(f"    bars where the C# evaluated an entry: {int(m_eval.sum()):,}; dropped for an "
      f"unavailable fill bar: {int((~okf).sum())}; population {len(ev_idx):,}")
    P(f"    MASK SANITY off the mask: score != 0 on {int((sc_col[~m_eval] != 0).sum()):,} bars, "
      f"size != 1 on {int((sz_col[~m_eval] != 1).sum()):,} bars")

    def exec_arm(Xd, lag):
        _, sce = causal_score_lag(Xd, fill_i, window=CS_QUAL_WINDOW, lag=lag)
        s_ = np.where(np.isnan(sce), 0.0, sce).astype(np.int32)
        z_ = 1 + (s_ >= 3).astype(np.int32)
        return s_, z_

    q0_s, q0_z = exec_arm(X, 1)
    q0_score = float(np.mean(q0_s == ev_sc))
    q0_size = float(np.mean(q0_z == ev_sz))
    d_sc = abs(q0_score - PRED_STALE_SCORE) * 100.0
    d_sz = abs(q0_size - PRED_STALE_SIZE) * 100.0
    Q0_PASS = bool(d_sc <= Q0_TOL_PP and d_sz <= Q0_TOL_PP)
    P("")
    P(f"    {'quantity':<34}{'predecessor':>14}{'this run':>14}{'|delta| pp':>12}{'<= 0.05 pp':>12}")
    P(f"    {'H_STALE score agreement':<34}{100*PRED_STALE_SCORE:>13.3f}%{100*q0_score:>13.3f}%"
      f"{d_sc:>12.4f}{('yes' if d_sc <= Q0_TOL_PP else 'NO'):>12}")
    P(f"    {'H_STALE size agreement':<34}{100*PRED_STALE_SIZE:>13.3f}%{100*q0_size:>13.3f}%"
      f"{d_sz:>12.4f}{('yes' if d_sz <= Q0_TOL_PP else 'NO'):>12}")
    P(f"    Q0 VERDICT: {'PASS' if Q0_PASS else 'FAIL - HARNESS CHANGED, NOTHING IS COMPARABLE'}")
    if not Q0_PASS:
        P("")
        P("    Per the spec's if_fail clause: report Q0 only and stop. No other gate is computed.")
        json.dump(dict(run_id="G3_EXECTRUTH_02_20260831", live_enabled=False, spend=0,
                       Q0=dict(verdict="FAIL", score=q0_score, size=q0_size,
                               predecessor_score=PRED_STALE_SCORE,
                               predecessor_size=PRED_STALE_SIZE)),
                  open(os.path.join(OUT, "gates.json"), "w"), indent=1)
        _fh.close()
        return

    # ==================================================================== 6. Q1 - THE DECIDING GATE
    H("6. Q1 - SIZE SEMANTICS UNDER THE CORRECTED ATR. THE DECIDING GATE.")
    ARMS = (("H_CORRECTED", XC, 1), ("C1", X, 1), ("C2", XC, 0), ("C3", XN, 1))
    LABEL = {"H_CORRECTED": "atr b-1, features b-1", "C1": "atr b-2, features b-1  (predecessor)",
             "C2": "atr b-1, features b    (fresh)", "C3": "atr b,   features b-1"}
    q1 = {}
    q1_arr = {}
    P(f"    {'arm':<14}{'construction':<40}{'score agree':>13}{'size agree':>12}"
      f"{'score qC>=250':>15}{'size qC>=250':>14}{'n bad':>7}")
    for nm, Xd, lag in ARMS:
        s_, z_ = exec_arm(Xd, lag)
        q1_arr[nm] = (s_, z_)
        r = dict(score=float(np.mean(s_ == ev_sc)), size=float(np.mean(z_ == ev_sz)),
                 score_conv=float(np.mean(s_[conv] == ev_sc[conv])),
                 size_conv=float(np.mean(z_[conv] == ev_sz[conv])),
                 score_warm=float(np.mean(s_[ev_warm] == ev_sc[ev_warm])),
                 size_warm=float(np.mean(z_[ev_warm] == ev_sz[ev_warm])),
                 n_bad=int((s_ != ev_sc).sum()))
        q1[nm] = r
        P(f"    {nm:<14}{LABEL[nm]:<40}{100*r['score']:>12.3f}%{100*r['size']:>11.3f}%"
          f"{100*r['score_conv']:>14.3f}%{100*r['size_conv']:>13.3f}%{r['n_bad']:>7,}")
    hc = q1["H_CORRECTED"]
    CTRL = ("C1", "C2", "C3")
    win_score = all(hc["score"] > q1[c]["score"] for c in CTRL)
    win_size = all(hc["size"] > q1[c]["size"] for c in CTRL)
    Q1_PASS = bool(hc["score"] >= 0.995 and hc["size"] >= 0.995 and win_score and win_size)
    P("")
    P(f"    population {len(ev_idx):,} evaluated entries (all {int(ev_warm.sum()):,} warm + "
      f"{int((~ev_warm).sum()):,} pre-warm, including the {CS_QUAL_MINHIST} the executable zeroes)")
    P(f"    H_CORRECTED score {100*hc['score']:.3f} %   vs   "
      + "   ".join(f"{c} {100*q1[c]['score']:.3f} %" for c in CTRL))
    P(f"    H_CORRECTED size  {100*hc['size']:.3f} %   vs   "
      + "   ".join(f"{c} {100*q1[c]['size']:.3f} %" for c in CTRL))
    P(f"    strict win on score against all three controls : {'yes' if win_score else 'NO'}")
    P(f"    strict win on size  against all three controls : {'yes' if win_size else 'NO'}")
    P(f"    score >= 99.5 % : {'yes' if hc['score'] >= 0.995 else 'NO'}     "
      f"size >= 99.5 % : {'yes' if hc['size'] >= 0.995 else 'NO'}")
    P(f"    Q1 VERDICT: {'PASS' if Q1_PASS else 'FAIL'}")
    if not Q1_PASS:
        P("")
        P("    Recorded FAIL. The executable is NOT REPRODUCED, Q4 stays locked, and the campaign")
        P("    continues to treat every Python P1 figure as object-divergent.")
    bad_q1 = q1_arr["H_CORRECTED"][0] != ev_sc
    P("")
    P(f"    residual of H_CORRECTED: {int(bad_q1.sum()):,} disagreeing entries of {len(bad_q1):,}")
    if bad_q1.any():
        P(f"      first 20: {[str(x) for x in ev_ts[bad_q1][:20]]}")

    # ================================================================= 7. Q2 - STATE + ACTION
    H("7. Q2 - STATE AND ACTION PARITY ON THE WARM SUB-SPAN")
    agree = {}
    P(f"    {'field':<10}{'kind':<16}{'agree FULL':>13}{'agree WARM':>13}{'n disagree':>12}"
      f"{'disagree in WARM':>18}")
    for k in FIELDS:
        eq = (np.abs(cs[k] - py[k]) <= 1e-3) if k == "ratio" else (cs[k] == py[k])
        agree[k] = dict(full=float(eq.mean()), warm=float(eq[WARM].mean()),
                        ndis=int((~eq).sum()), ndis_warm=int((~eq & WARM).sum()))
        P(f"    {k:<10}{('ACTION-BEARING' if k in ACTION_BEARING else 'diagnostic'):<16}"
          f"{100*agree[k]['full']:>12.4f}%{100*agree[k]['warm']:>12.4f}%"
          f"{agree[k]['ndis']:>12,}{agree[k]['ndis_warm']:>18,}")
    Q2_STATE = bool(all(agree[k]["warm"] >= 0.995 for k in ACTION_BEARING))

    qty_cs_full = E["qty"].to_numpy(np.int32)
    act_cs_full = act_from_qty(qty_cs_full)
    act_py_full = act_from_qty(qty_py_full)
    lo_, hi_ = max(ets[0], tarr[0]), min(ets[-1], tarr[-1])

    def clip(a):
        a = np.asarray(a)
        return a[(a >= lo_) & (a <= hi_)]
    ce = clip(ets[act_cs_full == 1]); pe = clip(tarr[act_py_full == 1])
    cx = clip(ets[act_cs_full == 3]); px_ = clip(tarr[act_py_full == 3])
    ent_j_full = jaccard(ce.astype("int64"), pe.astype("int64"))
    tcd_full = (len(ce) - len(pe)) / max(len(pe), 1)
    cew, pew = ce[ce >= wl], pe[pe >= wl]
    cxw, pxw = cx[cx >= wl], px_[px_ >= wl]
    ent_j_w = jaccard(cew.astype("int64"), pew.astype("int64"))
    ext_j_w = jaccard(cxw.astype("int64"), pxw.astype("int64"))
    tcd_w = (len(cew) - len(pew)) / max(len(pew), 1)
    Q2_ACTION = bool(ent_j_w >= 0.99 and abs(tcd_w) <= 0.02)
    Q2_PASS = bool(Q2_STATE and Q2_ACTION)
    conly = np.array(sorted(set(ce.astype("int64")) - set(pe.astype("int64")))).astype("datetime64[s]")
    ponly = np.array(sorted(set(pe.astype("int64")) - set(ce.astype("int64")))).astype("datetime64[s]")
    conly_x = np.array(sorted(set(cx.astype("int64")) - set(px_.astype("int64")))).astype("datetime64[s]")
    ponly_x = np.array(sorted(set(px_.astype("int64")) - set(cx.astype("int64")))).astype("datetime64[s]")
    P("")
    P(f"    WARM entries: C# {len(cew):,}  Python {len(pew):,}   count diff {100*tcd_w:+.3f} %")
    P(f"    WARM entry-bar Jaccard {ent_j_w:.5f}   WARM exit-bar Jaccard {ext_j_w:.5f}")
    P(f"    FULL-SPAN entry Jaccard {ent_j_full:.5f}, count diff {100*tcd_full:+.3f} % - RECORDED,")
    P(f"      NOT RE-LITIGATED. It is a warm-up artefact of the executable: "
      f"{int((conly < wl).sum())} of {len(conly)} C#-only and {int((ponly < wl).sum())} of "
      f"{len(ponly)} Python-only entries are pre-warm.")
    P("")
    P(f"    {'clause':<40}{'spec':>12}{'observed':>14}{'verdict':>10}")
    for nm_, sp_, ob_ in (("voteOK agreement (WARM)", ">= 99.5 %", agree["voteOK"]["warm"]),
                          ("t0 agreement (WARM)", ">= 99.5 %", agree["t0"]["warm"]),
                          ("t1 agreement (WARM)", ">= 99.5 %", agree["t1"]["warm"]),
                          ("t2 agreement (WARM)", ">= 99.5 %", agree["t2"]["warm"]),
                          ("t3 agreement (WARM)", ">= 99.5 %", agree["t3"]["warm"])):
        P(f"    {nm_:<40}{sp_:>12}{100*ob_:>13.4f}%{('pass' if ob_ >= 0.995 else 'FAIL'):>10}")
    P(f"    {'entry Jaccard (WARM)':<40}{'>= 0.99':>12}{ent_j_w:>14.5f}"
      f"{('pass' if ent_j_w >= 0.99 else 'FAIL'):>10}")
    P(f"    {'trade count difference (WARM)':<40}{'<= 2 %':>12}{100*tcd_w:>13.3f}%"
      f"{('pass' if abs(tcd_w) <= 0.02 else 'FAIL'):>10}")
    P(f"    Q2 VERDICT: {'PASS' if Q2_PASS else 'FAIL'}")
    P(f"    predecessor for comparison: voteOK 99.921 %, t0..t3 >= 99.82 %, Jaccard 0.99065, "
      f"+0.313 %")

    # ================================================================= 8. Q3 - RESIDUAL CAUSES
    H("8. Q3 - EVERY RESIDUAL DISAGREEMENT ASSIGNED TO A NAMED, EVIDENCED CAUSE")
    P("    Each cause below is a FORWARD SIMULATION of a named block of WeeklyEdgeP1PCT_v3.cs,")
    P("    run over the EXPORT's own bars starting from the export's first bar - i.e. over the")
    P("    deployed instance's own 365-day load span, which is not the campaign's history. A")
    P("    residual is assigned only when the simulation REPRODUCES the executable's own value.")
    P("")
    tsj = pd.to_datetime(jts)
    tod_j = (tsj.hour * 60 + tsj.minute).to_numpy(np.int32)
    hm4_j = (tsj.hour * 10000 + tsj.minute * 100).to_numpy(np.int32)
    first_of = np.zeros(len(jj), bool); first_of[0] = True
    first_of[1:] = ex_sess_j[1:] != ex_sess_j[:-1]
    last_of = np.zeros(len(jj), bool); last_of[-1] = True
    last_of[:-1] = ex_sess_j[1:] != ex_sess_j[:-1]

    norm_sim, ratio_sim = sim_norm_ratio(tod_j, rng_raw[jj], ex_sess_j)
    tilt_sim = sim_tilt(close_cs, ex_sess_j, last_of)
    dL_sim = sim_dL(D["c"][jj], D["v"][jj], first_of)
    bmom_sim = sim_bmom(hm4_j, D["c"][jj], D["o"][jj], D["v"][jj], last_of)
    rthdays = sim_rthdays(hm4_j, last_of)
    nThr_sim = np.ones(len(jj), np.int32)
    for q in (0.7, 0.8, 0.9):
        nThr_sim += ((norm_sim <= 0) | (cs["ratio"] >= q)).astype(np.int32)
    P(f"    simulations built  [{_time.time()-t0:.0f}s]")
    P(f"    {'simulation':<34}{'reproduces the export column on':>34}")
    P(f"    {'norm/ratio (.cs:963-970,1116-1119)':<34}"
      f"{100*np.mean(np.abs(ratio_sim - cs['ratio']) <= 1e-3):>33.3f}%")
    P(f"    {'tilt (.cs:1064-1073)':<34}{100*np.mean(tilt_sim == cs['tilt']):>33.3f}%")
    P(f"    {'dL (.cs:975,1126,1220-1222)':<34}{100*np.mean(dL_sim == cs['dL']):>33.3f}%")
    P(f"    {'bmom (.cs:1023-1059)':<34}{100*np.mean(bmom_sim == cs['bmom']):>33.3f}%")
    P(f"    {'nThr from simulated norm':<34}{100*np.mean(nThr_sim == cs['nThr']):>33.3f}%")

    # --- the HYBRID vote: the Python chain fed the EXECUTABLE'S OWN state inputs
    P("")
    P("    THE HYBRID VOTE. The canonical Python chain is re-run with FIVE inputs replaced on the")
    P("    joined window by the executable's own values - tilt, bmom, ratio (export column), norm")
    P("    (simulated) and dL. Nothing else changes. Whatever then agrees was CAUSED by those")
    P("    inputs; whatever still disagrees is not explained by them and is reported as such.")
    tilt_h = tilt.copy(); tilt_h[jj] = cs["tilt"].astype(tilt.dtype)
    bmom_h = bmom.copy(); bmom_h[jj] = cs["bmom"].astype(bmom.dtype)
    ratio_h = np.array(X["ratio"], float); ratio_h[jj] = cs["ratio"]
    norm_h = np.array(X["norm"], float); norm_h[jj] = norm_sim
    dL_h = np.array(X["dL"], bool); dL_h[jj] = cs["dL"].astype(bool)
    ctx_h = dict(X); ctx_h["ratio"] = ratio_h; ctx_h["norm"] = norm_h; ctx_h["dL"] = dL_h
    vlh, _vsh, TGh, nMemh, nThrh, dLh, _rh = votes_instrumented(D, mem, bmom_h, tilt_h,
                                                                ctx_h, bmom_h)
    TGha = np.vstack([TGh[k] for k in MEMBERS])
    hyb = dict(nMem=nMemh[jj], nThr=nThrh[jj], dL=dLh[jj],
               voteOK=vlh[jj].astype(np.int32),
               t0=TGha[0][jj].astype(np.int32), t1=TGha[1][jj].astype(np.int32),
               t2=TGha[2][jj].astype(np.int32), t3=TGha[3][jj].astype(np.int32))
    P(f"    hybrid vote built  [{_time.time()-t0:.0f}s]")
    P(f"    {'field':<10}{'python agrees with .cs':>24}{'hybrid agrees with .cs':>26}")
    for k in ("nMem", "nThr", "dL", "voteOK", "t0", "t1", "t2", "t3"):
        P(f"    {k:<10}{100*np.mean(cs[k] == py[k]):>23.4f}%"
          f"{100*np.mean(cs[k] == hyb[k]):>25.4f}%")

    # --- DATA_COVERAGE sessions, defined structurally
    cs_only_ts = ets[~hit]
    pyspan = (tarr >= ets[0]) & (tarr <= ets[-1])
    pos2 = np.searchsorted(jts, tarr[pyspan])
    pos2c = np.minimum(pos2, len(jts) - 1)
    py_only_ts = tarr[pyspan][jts[pos2c] != tarr[pyspan]]
    bad_sess = set(ex_sess[~hit].tolist())
    for t_ in py_only_ts:                       # the export session that should have held it
        k_ = int(ex_sess[min(np.searchsorted(ets, t_), len(ets) - 1)])
        bad_sess.add(k_)
    cover_sess = set()
    for s_ in bad_sess:
        cover_sess.add(s_); cover_sess.add(s_ + 1)    # the .cs accumulators carry forward one session
    COVER = np.isin(ex_sess_j, sorted(cover_sess))
    P("")
    P(f"    DATA-COVERAGE sessions: {sorted(bad_sess)} (a session where the two files do not hold")
    P(f"    the same minutes) plus the session immediately after each. {int(COVER.sum()):,} joined")
    P(f"    bars ({100*COVER.mean():.3f} %). C#-only minutes {len(cs_only_ts)}, Python-only "
      f"{len(py_only_ts)}.")
    if len(cs_only_ts):
        P(f"      C#-only : {[str(x) for x in cs_only_ts[:6]]} ... "
          f"{[str(x) for x in cs_only_ts[-3:]]}")
    if len(py_only_ts):
        P(f"      PY-only : {[str(x) for x in py_only_ts[:6]]} ... "
          f"{[str(x) for x in py_only_ts[-3:]]}")

    # --- knife-edge margins for any Q1 score residual
    if bad_q1.any():
        Vd, Td, fnames = score_detail(XC, fill_i, CS_QUAL_WINDOW, 1)
    else:
        Vd = Td = None
        fnames = []

    # --- BUILD THE RESIDUAL LEDGER, one row per (bar, field), one cause each
    P("")
    P("    ASSIGNING. Priority order exactly as declared in section 2(d).")
    rows = []
    prewarm_tilt0 = (cs["tilt"] == 0) & (~WARM)
    for k in FIELDS:
        eq = (np.abs(cs[k] - py[k]) <= 1e-3) if k == "ratio" else (cs[k] == py[k])
        idx = np.flatnonzero(~eq)
        for i_ in idx:
            cause = None
            if k == "tilt":
                if prewarm_tilt0[i_]:
                    cause = "TILT_WARMUP_LT_51_SESSIONS"
                elif tilt_sim[i_] == cs["tilt"][i_]:
                    cause = "TILT_OWN_LOAD_SPAN_SIM"
            elif k == "bmom":
                if cs["bmom"][i_] == 0 and rthdays[i_] < CS_BMOM_BAND_DAYS:
                    cause = "BMOM_WARMUP_LT_14_RTH_DAYS"
                elif bmom_sim[i_] == cs["bmom"][i_]:
                    cause = "BMOM_OWN_SLOTHIST_SIM"
            elif k == "ratio":
                if norm_sim[i_] <= 0 and abs(cs["ratio"][i_] - 1.0) <= 1e-9:
                    cause = "NORM_NOT_YET_AVAILABLE"
                elif abs(ratio_sim[i_] - cs["ratio"][i_]) <= 1e-3:
                    cause = "NORM_OWN_LOAD_SPAN_SIM"
            elif k == "nThr":
                if nThr_sim[i_] == cs["nThr"][i_]:
                    cause = "NTHR_FOLLOWS_NORM_SIM"
            elif k == "dL":
                if dL_sim[i_] == cs["dL"][i_]:
                    cause = "CUMDELTA_OWN_SESSION_PATH_SIM"
                elif dL_sim[i_] == py["dL"][i_]:
                    cause = "CUMDELTA_VOLUME_SERIES_DIFFER"
            if cause is None and k in ("nMem", "nThr", "dL", "voteOK", "t0", "t1", "t2", "t3"):
                if hyb[k][i_] == cs[k][i_]:
                    if cs["tilt"][i_] != py["tilt"][i_]:
                        cause = "CS_INPUT_TILT"
                    elif cs["bmom"][i_] != py["bmom"][i_]:
                        cause = "CS_INPUT_BMOM"
                    elif abs(cs["ratio"][i_] - py["ratio"][i_]) > 1e-3:
                        cause = "CS_INPUT_RATIO_NORM"
                    elif cs["dL"][i_] != py["dL"][i_]:
                        cause = "CS_INPUT_DL"
                    else:
                        cause = "CS_INPUT_HYSTERESIS_CARRY"
            if cause is None and COVER[i_]:
                cause = "DATA_COVERAGE"
            if cause is None:
                cause = "UNEXPLAINED"
            rows.append((str(jts[i_]), k, float(cs[k][i_]), float(py[k][i_]),
                         bool(WARM[i_]), cause))

    def act_cause(t_, side):
        i_ = int(np.searchsorted(jts, t_))
        if i_ >= len(jts) or jts[i_] != t_:
            return "BAR_NOT_IN_JOIN"
        if not WARM[i_]:
            return "ACTION_PRE_WARM"
        if cs["voteOK"][i_] != py["voteOK"][i_] or (
                i_ > 0 and cs["voteOK"][i_ - 1] != py["voteOK"][i_ - 1]):
            return "ACTION_FOLLOWS_VOTEOK"
        if COVER[i_]:
            return "DATA_COVERAGE"
        return "UNEXPLAINED"
    for nm_, arr, a_, b_ in (("ENTRY_BAR", conly, 1, 0), ("ENTRY_BAR", ponly, 0, 1),
                             ("EXIT_BAR", conly_x, 1, 0), ("EXIT_BAR", ponly_x, 0, 1)):
        for t_ in arr:
            rows.append((str(t_), nm_, float(a_), float(b_), bool(t_ >= wl), act_cause(t_, a_)))

    for i_ in np.flatnonzero(bad_q1):
        cz = "UNEXPLAINED"
        if Vd is not None:
            rel = np.abs(Vd[i_] - Td[i_]) / np.maximum(np.abs(Td[i_]), 1e-12)
            if np.isfinite(rel).any() and float(np.nanmin(rel)) < 1e-6:
                cz = "SCORE_KNIFE_EDGE"
        gi = ev_idx[i_]
        if cz == "UNEXPLAINED" and COVER[gi]:
            cz = "DATA_COVERAGE"
        rows.append((str(ev_ts[i_]), "SCORE_H_CORRECTED", float(ev_sc[i_]),
                     float(q1_arr["H_CORRECTED"][0][i_]), bool(ev_warm[i_]), cz))
    for i_ in np.flatnonzero(q1_arr["H_CORRECTED"][1] != ev_sz):
        gi = ev_idx[i_]
        rows.append((str(ev_ts[i_]), "SIZE_H_CORRECTED", float(ev_sz[i_]),
                     float(q1_arr["H_CORRECTED"][1][i_]), bool(ev_warm[i_]),
                     "DATA_COVERAGE" if COVER[gi] else "UNEXPLAINED"))

    RES = pd.DataFrame(rows, columns=["ts", "field", "cs", "py", "warm", "cause"])
    RES.to_csv(os.path.join(OUT, "residual_classes.csv"), index=False)
    tot = len(RES)
    unexp = int((RES["cause"] == "UNEXPLAINED").sum())
    assigned = tot - unexp
    Q3_PASS = bool(tot > 0 and assigned / tot >= 0.95)
    P("")
    P(f"    RESIDUAL POPULATION: {tot:,} (bar, field) disagreements")
    P(f"    {'cause':<34}{'n':>10}{'share':>10}{'in WARM':>10}")
    vc = RES["cause"].value_counts()
    for c_, v_ in vc.items():
        P(f"    {c_:<34}{v_:>10,}{100*v_/tot:>9.3f}%"
          f"{int(RES.loc[RES['cause'] == c_, 'warm'].sum()):>10,}")
    P(f"    {'-' * 60}")
    P(f"    {'ASSIGNED':<34}{assigned:>10,}{100*assigned/tot:>9.3f}%")
    P(f"    {'UNEXPLAINED':<34}{unexp:>10,}{100*unexp/tot:>9.3f}%")
    P("")
    P(f"    spec PASS = >= 95 % assigned.  Q3 VERDICT: {'PASS' if Q3_PASS else 'FAIL'}")
    P(f"    THE UNEXPLAINED FRACTION IS {100*unexp/tot:.3f} % AND IS NOT ROUNDED AWAY.")
    if unexp:
        ux = RES[RES["cause"] == "UNEXPLAINED"]
        P(f"    unexplained by field: "
          f"{ {k: int(v) for k, v in ux['field'].value_counts().items()} }")
        P(f"    unexplained inside WARM: {int(ux['warm'].sum()):,} of {unexp:,}")
        P(f"    the 8 heaviest unexplained dates: "
          f"{ {str(k): int(v) for k, v in pd.Series(pd.to_datetime(ux['ts']).dt.date).value_counts().head(8).items()} }")
    P("")
    P("    THE THREE QUESTIONS INHERITED FROM THE PREDECESSOR, ANSWERED:")
    r_sim = int(((RES["field"] == "ratio") & (RES["cause"].isin(
        ["NORM_NOT_YET_AVAILABLE", "NORM_OWN_LOAD_SPAN_SIM"]))).sum())
    r_tot = int((RES["field"] == "ratio").sum())
    P(f"      (a) ratio: {r_sim:,} of {r_tot:,} ({100*r_sim/max(r_tot,1):.2f} %) are reproduced by")
    P(f"          simulating the .cs's OWN rngHist over its OWN load span. The predecessor could")
    P(f"          only localise this to `norm`; it is now assigned to a mechanism.")
    d_sim = int(((RES["field"] == "dL") &
                 (RES["cause"] == "CUMDELTA_OWN_SESSION_PATH_SIM")).sum())
    d_vol = int(((RES["field"] == "dL") &
                 (RES["cause"] == "CUMDELTA_VOLUME_SERIES_DIFFER")).sum())
    P(f"      (b) dL: {int((RES['field'] == 'dL').sum()):,} mismatches. Re-running the .cs's own")
    P(f"          cumDelta recursion on the PYTHON volume series reproduces the .cs on {d_sim:,}")
    P(f"          of them and reproduces PYTHON on {d_vol:,}. The {d_vol:,} are the bars on which")
    P(f"          the two volume series genuinely differ - the export writes no volume column, so")
    P(f"          this is the closest the snapshot permits and it BOUNDS the question rather than")
    P(f"          leaving it open.")
    cov_n = int((RES["cause"] == "DATA_COVERAGE").sum())
    vw = RES[(RES["field"] == "voteOK") & RES["warm"]]
    P(f"      (c) coverage: {cov_n:,} residuals fall in a mismatched-minute session or the one")
    P(f"          after it. Of the {len(vw):,} voteOK mismatches inside WARM, "
      f"{int((vw['cause'] == 'DATA_COVERAGE').sum()):,} are coverage and "
      f"{int((vw['cause'] == 'UNEXPLAINED').sum()):,} are unexplained.")

    # ================================================================= 9. Q4 - ECONOMICS
    H("9. Q4 - ECONOMICS. RUNS ONLY IF Q1 PASSED.")
    Q4 = None
    if not Q1_PASS:
        P("    Q1 did NOT pass. Per the spec, this section does not run and NO DOLLAR FIGURE IS")
        P("    PRODUCED ANYWHERE IN THIS RUN.")
    else:
        P("    THIS IS A CORRECTION TO THE RECORD, NOT A CANDIDATE, NOT AN IMPROVEMENT, AND NOT A")
        P("    P1_vNext. It measures how far the campaign's quoted P1 economics sit from the")
        P("    executable's. Changing what the deployed strategy does remains a separate locked")
        P("    challenge that this run may not open. The deployed strategy was never using the")
        P("    defect, so nothing here is a reason to modify it.")
        P("")
        pb_cor, _ = causal_score_lag(XC, ee, window=WIN, lag=1)
        sz_cor = np.where(pb_cor >= 3, 2, 1).astype(np.int8)
        pb_c1, _ = causal_score_lag(X, ee, window=WIN, lag=1)
        sz_c1 = np.where(pb_c1 >= 3, 2, 1).astype(np.int8)
        pb_c2, _ = causal_score_lag(XC, ee, window=WIN, lag=0)
        sz_c2 = np.where(pb_c2 >= 3, 2, 1).astype(np.int8)
        trR = gfills(D, p_dir, sz_canon, **arm_kw("PCT", 1.183))     # what the chain produced
        trC = gfills(D, p_dir, sz_cor, **arm_kw("PCT", 1.183))       # H_CORRECTED
        same = (len(trR) == len(trC)) and all(
            a["et"] == b["et"] and a["xt"] == b["xt"] and a["d"] == b["d"]
            for a, b in zip(trR, trC))
        P(f"    SIZE-INVARIANCE PRECONDITION (T2_P1SIZE01: pnl_i = s_i * pnl_per_contract_i, max")
        P(f"    error 0.00e+00). Asserted here, not assumed - identical (et, xt, direction) for all")
        P(f"    {len(trR):,} trades under both size vectors: {'PASS' if same else 'FAIL'}")
        assert same, "the trade schedule moved with size; the per-contract box assumption is broken"
        trC1 = gfills(D, p_dir, sz_c1, **arm_kw("PCT", 1.183))
        trC2 = gfills(D, p_dir, sz_c2, **arm_kw("PCT", 1.183))
        same4 = all(len(x) == len(trR) for x in (trC1, trC2)) and all(
            a["et"] == b["et"] and a["et"] == c_["et"] and a["xt"] == b["xt"]
            and a["xt"] == c_["xt"] for a, b, c_ in zip(trR, trC1, trC2))
        P(f"    the same identity asserted for the two decomposition size vectors: "
          f"{'PASS' if same4 else 'FAIL'}")
        assert same4, "a decomposition size vector moved the schedule"
        F = pd.DataFrame([dict(et=pd.Timestamp(a["et"]), xt=pd.Timestamp(a["xt"]),
                               uR=a["u"], uC=b["u"], u1=c_["u"], u2=d_["u"],
                               per=a["pnl"] / a["u"])
                          for a, b, c_, d_ in zip(trR, trC, trC1, trC2)])
        F["pR"] = F["uR"] * F["per"]
        F["pC"] = F["uC"] * F["per"]
        F["p1"] = F["u1"] * F["per"]
        F["p2"] = F["u2"] * F["per"]
        iso = F["et"].dt.isocalendar()
        F["wk"] = iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)
        # The canonical scoring window is run_we_w103.py:39-40. gfills runs over the whole
        # substrate, so trades entered before 2022-07-01 carry size 1 in BOTH vectors by
        # construction and belong to neither object's quoted economics. They contribute exactly
        # zero to the difference; they are excluded so the NET LEVELS are the quoted ones.
        n_before = int((F["et"] < pd.Timestamp(str(A_CANON))).sum())
        d_before = float((F.loc[F["et"] < pd.Timestamp(str(A_CANON)), "pC"]
                          - F.loc[F["et"] < pd.Timestamp(str(A_CANON)), "pR"]).sum())
        P(f"    {n_before:,} trades entered before the canonical scoring window opens "
          f"(2022-07-01); both size vectors assign them 1 by construction and their")
        P(f"    contribution to the difference is ${d_before:,.2f}. They are EXCLUDED so the net")
        P(f"    levels below are the levels the campaign quotes.")
        F = F[(F["et"] >= pd.Timestamp(str(A_CANON))) &
              (F["et"] < pd.Timestamp(str(B_CANON)))].reset_index(drop=True)

        def block(G, label):
            if not len(G):
                P(f"    {label}: EMPTY")
                return None
            nwk = G["wk"].nunique()
            netR, netC = float(G["pR"].sum()), float(G["pC"].sum())
            dif = G["uR"] != G["uC"]
            thr = np.quantile(G["per"].abs(), 0.9)
            top = G["per"].abs() >= thr
            dd = netC - netR
            dtop = float(G.loc[top, "pC"].sum() - G.loc[top, "pR"].sum())
            P("")
            P(f"    ---- {label}")
            P(f"    window {G['et'].min()} -> {G['et'].max()};  {len(G):,} trades, {nwk} weeks")
            P(f"    trades sized differently                      : {int(dif.sum()):,} "
              f"({100*dif.mean():.2f} % of trades)")
            P(f"      their share of the RESEARCH-CHAIN net       : "
              f"{100*float(G.loc[dif,'pR'].sum())/netR if netR else float('nan'):>8.2f} %")
            P(f"      their share of the H_CORRECTED net          : "
              f"{100*float(G.loc[dif,'pC'].sum())/netC if netC else float('nan'):>8.2f} %")
            P(f"    {'size vector':<44}{'ctrRT':>9}{'sz2 %':>9}{'net $':>14}{'$ / week':>12}")
            for nm_, col, uc in (("RESEARCH CHAIN as quoted (ATR double-lagged)", "pR", "uR"),
                                 ("H_CORRECTED  (the executable's semantics)", "pC", "uC"),
                                 ("  decomposition: C1 phase only, ATR uncorrected", "p1", "u1"),
                                 ("  decomposition: C2 ATR only, fresh phase", "p2", "u2")):
                P(f"    {nm_:<44}{int(G[uc].sum()):>9,}{100*float((G[uc] == 2).mean()):>8.2f}%"
                  f"{float(G[col].sum()):>14,.0f}{float(G[col].sum())/nwk:>12,.0f}")
            P(f"    {'DIFFERENCE  H_CORRECTED - RESEARCH CHAIN':<44}{'':>9}{'':>9}{dd:>14,.0f}"
              f"{dd/nwk:>12,.0f}")
            P(f"    top decile by |per-contract P&L| ({int(top.sum()):,} trades): "
              f"research ${float(G.loc[top,'pR'].sum()):,.0f}  corrected "
              f"${float(G.loc[top,'pC'].sum()):,.0f}  difference ${dtop:,.0f} "
              f"({100*dtop/dd if dd else float('nan'):.1f} % of the total)")
            P(f"      the other {int((~top).sum()):,} trades account for ${dd-dtop:,.0f}")
            return dict(label=label, trades=int(len(G)), weeks=int(nwk),
                        n_sized_differently=int(dif.sum()),
                        share_of_trades=float(dif.mean()),
                        share_diff_of_net_research=(float(G.loc[dif, "pR"].sum()) / netR)
                        if netR else None,
                        share_diff_of_net_corrected=(float(G.loc[dif, "pC"].sum()) / netC)
                        if netC else None,
                        net_research_chain=netR, net_h_corrected=netC,
                        net_c1_phase_only=float(G["p1"].sum()),
                        net_c2_atr_only=float(G["p2"].sum()),
                        diff_total=dd, diff_per_week=dd / nwk,
                        top_decile_n=int(top.sum()), top_decile_diff=dtop,
                        rest_diff=dd - dtop)
        b_full = block(F, "CANONICAL WINDOW 2022-07-01 -> 2026-08-01 (the window the campaign "
                          "quotes)")
        pre = F[F["et"] < pd.Timestamp(str(BURN))]
        b_pre = block(pre, "PRE-BURN SUB-WINDOW, entries before 2026-05-31 (CLAUDE.md section 5)")
        ovl = F[(F["et"] >= pd.Timestamp(str(lo_))) & (F["et"] <= pd.Timestamp(str(hi_)))]
        b_ovl = block(ovl, "COMPANION: the export-overlap window only, 2025-08-31 -> 2026-07-31")
        P("")
        P("    READING: the difference is a MEASUREMENT OF THE RESEARCH REPRESENTATION'S ERROR, not")
        P("    a P&L opportunity. The executable has always used the corrected semantics; the")
        P("    number below is how far the quoted figure sits from the traded one, and its sign")
        P("    carries no recommendation.")
        Q4 = dict(full=b_full, pre_burn=b_pre, export_overlap=b_ovl)

    # ============================================================================ 10. GATE TABLE
    H("10. GATE TABLE - printed by the program")
    rows_g = [
        ("Q0", "reproduce predecessor H_STALE 96.977 % / 98.992 % within 0.05 pp",
         f"{100*q0_score:.3f}% / {100*q0_size:.3f}%  (d {d_sc:.4f} / {d_sz:.4f} pp)", Q0_PASS),
        ("Q1", "score >=99.5% AND size >=99.5% AND H_CORRECTED strictly beats C1,C2,C3",
         f"score {100*hc['score']:.3f}% size {100*hc['size']:.3f}%; "
         f"C1 {100*q1['C1']['score']:.2f} C2 {100*q1['C2']['score']:.2f} "
         f"C3 {100*q1['C3']['score']:.2f}", Q1_PASS),
        ("Q2", "WARM: voteOK>=99.5%, t0..t3>=99.5%, entry Jaccard>=0.99, count within 2%",
         f"voteOK {100*agree['voteOK']['warm']:.3f}%; t0..t3 " +
         "/".join(f"{100*agree[k]['warm']:.2f}" for k in ("t0", "t1", "t2", "t3")) +
         f"; J {ent_j_w:.5f}; {100*tcd_w:+.3f}%", Q2_PASS),
        ("Q3", ">=95% of residual disagreements assigned to a named, evidenced cause",
         f"{assigned:,}/{tot:,} = {100*assigned/tot:.3f}% assigned; "
         f"{100*unexp/tot:.3f}% unexplained", Q3_PASS),
        ("Q4", "runs only if Q1 passes",
         ("computed - see section 9" if Q1_PASS else "NOT COMPUTED, no dollar figure exists"),
         Q1_PASS),
    ]
    P(f"{'GATE':<6}{'SPEC':<70}{'OBSERVED':<64}{'VERDICT':>9}")
    for g, sp, ob, okk in rows_g:
        P(f"{g:<6}{sp[:69]:<70}{ob[:63]:<64}{('PASS' if okk else 'FAIL'):>9}")
    P("")
    P("    The REALTIME column is UNDECIDABLE with n = 0 after the seal, exactly as in the")
    P("    predecessor. No gate is decided on it and none is reported as a rate.")
    P("")
    P("    WHAT A PASS DOES NOT MEAN (spec section 3): agreement is not correctness; this run says")
    P("    nothing about whether the executable is good, nothing about the realtime object, and")
    P("    nothing that authorises modifying the deployed strategy.")

    # ============================================================================ 11. ARTIFACTS
    H("11. ARTIFACTS")
    G = dict(
        run_id="G3_EXECTRUTH_02_20260831",
        live_enabled=False, spend=0, orders_placed=False,
        snapshot=dict(path=SNAP, sha256=sha, bytes=os.path.getsize(SNAP),
                      matches_spec=bool(sha == SNAP_SHA), re_snapshotted=False),
        seal=dict(boundary="2026-08-01", rows_dropped=int(seal_mask.sum()),
                  rows_retained=int(len(ets)), realtime_rows_post_seal=0,
                  realtime_verdict="UNDECIDABLE n=0"),
        join=dict(matched=int(hit.sum()), rate=float(hit.mean()),
                  cs_only=int(len(cs_only_ts)), py_only=int(len(py_only_ts))),
        Q0=dict(verdict="PASS" if Q0_PASS else "FAIL", score=q0_score, size=q0_size,
                predecessor_score=PRED_STALE_SCORE, predecessor_size=PRED_STALE_SIZE,
                delta_pp=dict(score=d_sc, size=d_sz)),
        Q1=dict(verdict="PASS" if Q1_PASS else "FAIL", n_evaluated=int(len(ev_idx)),
                bar=dict(score=0.995, size=0.995), arms=q1,
                strict_win_score=bool(win_score), strict_win_size=bool(win_size),
                n_disagreeing=int(bad_q1.sum())),
        Q2=dict(verdict="PASS" if Q2_PASS else "FAIL",
                state={k: agree[k] for k in FIELDS},
                entry_jaccard_warm=ent_j_w, exit_jaccard_warm=ext_j_w,
                trade_count_diff_warm=tcd_w,
                entry_jaccard_full_recorded_not_relitigated=ent_j_full,
                trade_count_diff_full=tcd_full,
                cs_entries_warm=int(len(cew)), py_entries_warm=int(len(pew))),
        Q3=dict(verdict="PASS" if Q3_PASS else "FAIL", population=int(tot),
                assigned=int(assigned), unexplained=int(unexp),
                assigned_fraction=float(assigned / tot),
                unexplained_fraction=float(unexp / tot),
                causes={str(k): int(v) for k, v in vc.items()},
                sim_reproduction=dict(
                    ratio=float(np.mean(np.abs(ratio_sim - cs["ratio"]) <= 1e-3)),
                    tilt=float(np.mean(tilt_sim == cs["tilt"])),
                    dL=float(np.mean(dL_sim == cs["dL"])),
                    bmom=float(np.mean(bmom_sim == cs["bmom"])),
                    nThr=float(np.mean(nThr_sim == cs["nThr"])))),
        Q4=Q4)
    json.dump(G, open(os.path.join(OUT, "gates.json"), "w"), indent=1, default=float)
    P(f"    out/gates.json")
    P(f"    out/residual_classes.csv   {tot:,} rows")
    P(f"    out/console.txt")
    P("")
    P(f"[done {_time.time()-t0:.0f}s]  LIVE ENABLED = NO.  $0 spent.  Nothing promoted.")
    _fh.close()


if __name__ == "__main__":
    main()
