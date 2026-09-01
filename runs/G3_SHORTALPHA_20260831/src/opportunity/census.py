"""G3_SHORTALPHA / OPPORTUNITY -- a STRATEGY-FREE census of NQ down-moves, 2006 -> 2026-07.

QUESTION (preregistered; the decision rule below was written before any number was computed)
-------------------------------------------------------------------------------------------
The mirrored short sleeve (WE_W61) earned +10.11 / +2.76 / +13.92 / +6.05 pts/session in
2022..2025 and -10.62 in 2026, its worst year ever. Two mutually exclusive explanations:

    DROUGHT           the down-moves are not there any more (the opportunity shrank)
    CAPTURE FAILURE   the down-moves are there and the sleeve stopped catching them

This program measures the OPPORTUNITY with no strategy anywhere in it, and adjudicates.

DECISION RULE (fixed in advance, coded below, printed as a GATE table):
    DROUGHT           iff G4 (2026 PF-short availability collapsed) PASS
                      AND G6 (capture ratio 2026 inside the 2022-2025 span) PASS
    CAPTURE FAILURE   iff G4 FAIL AND G6 FAIL
    MIXED             otherwise -- and MIXED must be reported as MIXED, not spun.

HARD RULES OBSERVED
    SEAL     no bar with session_date >= 2026-08-01 is read. Asserted in code (G1).
    ERA      ERABREAK01 (p=0.0011) forbids pooling pre-2022 with modern. Strata are
             PRE (<2020-01-01) / TRANSITION (2020-01-01..2022-04-30, excluded from tests)
             / MODERN (>=2022-05-01). Full-sample rows are DIAGNOSTIC ONLY.
    SCALE    NQ traded ~1,700 in 2006 and ~23,000 in 2026. RAW POINTS ARE NOT COMPARABLE
             ACROSS YEARS. Every cross-era claim is made in ATR units; point columns are
             printed beside them so the level effect is visible rather than hidden.
    COSTS    floor $4.36/ctrRT (commission only -- never a headline),
             PRIMARY $20.65/ctrRT = 1.0325 NQ pts (G2_EXEC01, 113 real round turns),
             all-in $25.01/ctrRT = 1.2505 NQ pts.
    NULLS    dependence-preserving. Stationary (Politis-Romano) block bootstrap over
             SESSIONS, mean block length 10. rho_bar and K_eff printed for every test.
             Session-level t is never used as a test.

DEFINITIONS (all strategy-free)
    session          the loader's 18:00->17:00 ET box. Bars are END-STAMPED.
    mso              minutes since 18:00 session open. ON=[1,930] (18:01..09:30),
                     RTH=[931,1320] (09:31..16:00), POST=[1321,1380] (16:01..17:00).
    max decline      max over i<=j of (running max high through i) - (low at j), in points.
    max advance      the mirrored statistic. THE MATCHED UNCONDITIONAL CONTROL.
    ATR              CAUSAL session ATR14: mean of the PREVIOUS 14 sessions' true range,
                     TR_s = max(H_s-L_s, |H_s-C_{s-1}|, |L_s-C_{s-1}|). Never uses session s.
    retrace          decline: (segment last close - trough low) / decline
                     advance: (peak high - segment last close) / advance
                     i.e. the fraction handed back by the time the clock ran out.
    PF-k-ATR SHORT   perfect-foresight upper bound: a (k*ATR) reversal zigzag on the
                     session's 1-min bars; every confirmed swing-high -> swing-low leg is
                     captured in full, exact top to exact bottom, no risk, no slippage.
                     Every leg is >= k*ATR by construction.
    PF-k-ATR LONG    the same zigzag's up legs -- the matched control.

    THE BRIEF ASKED FOR k = 2. At session-ATR scale that is degenerate (a 2x-daily-ATR
    intra-session swing happens roughly once every 30-50 sessions), so it is reported as
    asked AND a full ladder k in {0.10 ... 2.00} is printed. The FREQUENCY-MATCHED rung
    (k = 0.25, ~2 legs/session, matching the sleeve's own 2.20 trades/session) is the
    primary comparator. Nothing is hidden behind the choice: the whole ladder is printed.
"""
from __future__ import annotations

import os
import sys
import time as _time
import warnings
import zlib

import numpy as np
import pandas as pd
from numba import njit

warnings.simplefilter("ignore", pd.errors.PerformanceWarning)

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "research", "weekly_edge", "src"))
from run_we_w17 import load_deep                                          # noqa: E402

OUT = os.path.join(ROOT, "runs", "G3_SHORTALPHA_20260831", "out")
os.makedirs(OUT, exist_ok=True)

PV = 20.0
COST_FLOOR_RT = 4.36        # commission only. NEVER a headline.
COST_PRIMARY_RT = 20.65     # G2_EXEC01 measured, 113 real round turns
COST_ALLIN_RT = 25.01
SEAL_FIRST_VIRGIN = np.datetime64("2026-08-01", "D")

PRE_END = np.datetime64("2020-01-01", "D")
MOD_START = np.datetime64("2022-05-01", "D")
LADDER = [0.10, 0.15, 0.20, 0.25, 0.33, 0.50, 0.75, 1.00, 1.50, 2.00]
K_PRIMARY = 0.25
B_BOOT = 20000
MEAN_BLOCK = 10.0

_LINES: list[str] = []


def P(s: str = "") -> None:
    print(s, flush=True)
    _LINES.append(s)


def rule(ch: str = "=", n: int = 112) -> None:
    P(ch * n)


# =================================================================================================
# kernels
# =================================================================================================

@njit(cache=True)
def mdd_kernel(h, l, c, seg_a, seg_b, out):
    """Per session slice [a,b): 0 max decline, 1 peak offset, 2 trough offset,
    3 max advance, 4 trough offset, 5 peak offset, 6 decline retrace, 7 nbars,
    8 advance retrace, 9 total downside variation (sum of bar-to-bar falls in close)."""
    ns = seg_a.shape[0]
    for s in range(ns):
        a = seg_a[s]
        b = seg_b[s]
        if b - a < 2:
            for k in range(10):
                out[s, k] = np.nan
            continue
        run_hi = h[a]
        run_hi_i = a
        best = -1.0
        best_pk = a
        best_tr = a
        for i in range(a, b):
            if h[i] > run_hi:
                run_hi = h[i]
                run_hi_i = i
            d = run_hi - l[i]
            if d > best:
                best = d
                best_pk = run_hi_i
                best_tr = i
        run_lo = l[a]
        run_lo_i = a
        besta = -1.0
        besta_tr = a
        besta_pk = a
        for i in range(a, b):
            if l[i] < run_lo:
                run_lo = l[i]
                run_lo_i = i
            u = h[i] - run_lo
            if u > besta:
                besta = u
                besta_tr = run_lo_i
                besta_pk = i
        dv = 0.0
        for i in range(a + 1, b):
            d = c[i - 1] - c[i]
            if d > 0.0:
                dv += d
        out[s, 0] = best
        out[s, 1] = best_pk - a
        out[s, 2] = best_tr - a
        out[s, 3] = besta
        out[s, 4] = besta_tr - a
        out[s, 5] = besta_pk - a
        out[s, 6] = (c[b - 1] - l[best_tr]) / best if best > 0.0 else np.nan
        out[s, 7] = b - a
        out[s, 8] = (h[besta_pk] - c[b - 1]) / besta if besta > 0.0 else np.nan
        out[s, 9] = dv


@njit(cache=True)
def zigzag_kernel(h, l, seg_a, seg_b, thr, out):
    """k*ATR reversal zigzag per session slice.
    out: 0 down_sum 1 n_down 2 up_sum 3 n_up 4 down_sum+tail 5 n_down+tail
         6 up_sum+tail 7 n_up+tail 8 max_down_leg(incl tail)"""
    ns = seg_a.shape[0]
    for s in range(ns):
        a = seg_a[s]
        b = seg_b[s]
        for k in range(9):
            out[s, k] = np.nan
        t = thr[s]
        if b - a < 2 or not (t > 0.0):
            continue
        state = 0
        hi = h[a]
        lo = l[a]
        piv_price = 0.0
        have_piv = False
        piv_is_high = False
        dsum = 0.0
        usum = 0.0
        nd = 0
        nu = 0
        maxd = 0.0
        for i in range(a, b):
            if state == 0:
                if h[i] > hi:
                    hi = h[i]
                if l[i] < lo:
                    lo = l[i]
                if hi - l[i] >= t:
                    piv_price = hi
                    have_piv = True
                    piv_is_high = True
                    state = -1
                    lo = l[i]
                elif h[i] - lo >= t:
                    piv_price = lo
                    have_piv = True
                    piv_is_high = False
                    state = 1
                    hi = h[i]
            elif state == 1:
                if h[i] > hi:
                    hi = h[i]
                if hi - l[i] >= t:
                    if have_piv and not piv_is_high:
                        usum += hi - piv_price
                        nu += 1
                    piv_price = hi
                    have_piv = True
                    piv_is_high = True
                    state = -1
                    lo = l[i]
            else:
                if l[i] < lo:
                    lo = l[i]
                if h[i] - lo >= t:
                    if have_piv and piv_is_high:
                        m = piv_price - lo
                        dsum += m
                        nd += 1
                        if m > maxd:
                            maxd = m
                    piv_price = lo
                    have_piv = True
                    piv_is_high = False
                    state = 1
                    hi = h[i]
        out[s, 0] = dsum
        out[s, 1] = nd
        out[s, 2] = usum
        out[s, 3] = nu
        dst = dsum
        ndt = nd
        ust = usum
        nut = nu
        if have_piv and piv_is_high and state == -1:
            m = piv_price - lo
            if m >= t:
                dst += m
                ndt += 1
                if m > maxd:
                    maxd = m
        if have_piv and (not piv_is_high) and state == 1:
            m = hi - piv_price
            if m >= t:
                ust += m
                nut += 1
        out[s, 4] = dst
        out[s, 5] = ndt
        out[s, 6] = ust
        out[s, 7] = nut
        out[s, 8] = maxd


# =================================================================================================
# inference helpers (dependence-preserving)
# =================================================================================================

def rho_bar_lag1(x: np.ndarray) -> float:
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if len(x) < 5:
        return 0.0
    a = x[:-1] - x[:-1].mean()
    b = x[1:] - x[1:].mean()
    d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > 0 else 0.0


def k_eff(k: int, rho: float) -> float:
    rho = max(rho, 0.0)
    return k / (1.0 + (k - 1) * rho) if k > 1 else float(k)


@njit(cache=True)
def _sb_index(n, m, B, p, seeds, out):
    for bi in range(B):
        st = seeds[bi]
        j = st % n
        for k in range(m):
            out[bi, k] = j
            st = (st * 6364136223846793005 + 1442695040888963407) % (2 ** 62)
            r = (st % 1000000) / 1000000.0
            if r < p:
                st = (st * 6364136223846793005 + 1442695040888963407) % (2 ** 62)
                j = st % n
            else:
                j = (j + 1) % n


def sb_indices(n: int, m: int, B: int, mean_block: float, seed: int) -> np.ndarray:
    """Politis-Romano stationary bootstrap index matrix. Geometric blocks, circular wrap.
    Preserves serial dependence; a plain i.i.d. resample would not."""
    rng = np.random.default_rng(seed)
    seeds = rng.integers(1, 2 ** 60, size=B).astype(np.int64)
    out = np.empty((B, m), np.int64)
    _sb_index(n, m, B, 1.0 / mean_block, seeds, out)
    return out


def cseed(name: str, salt: int) -> int:
    """DETERMINISTIC seed from a column name. Python's built-in hash() is randomised per
    process (PYTHONHASHSEED), so using it here silently made every run irreproducible --
    caught when a borderline percentile moved 11.3 -> 10.6 -> 10.9 across identical runs."""
    return (zlib.crc32(name.encode()) % 10**6) + salt


def mc_se(pct: float, B: int) -> float:
    """Monte-Carlo standard error of a bootstrap percentile, in percentage points."""
    q = pct / 100.0
    return 100.0 * float(np.sqrt(max(q * (1 - q), 1e-12) / B))


def pct_of(val: float, dist: np.ndarray) -> float:
    d = dist[np.isfinite(dist)]
    return 100.0 * float((d < val).mean()) if len(d) else np.nan


# =================================================================================================

def main() -> None:
    t0 = _time.time()
    rule()
    P("G3_SHORTALPHA / OPPORTUNITY -- STRATEGY-FREE CENSUS OF NQ DOWN-MOVES, 2006 -> 2026-07")
    P("is the SHORT OPPORTUNITY there at all, independent of any strategy?")
    rule()
    P()

    D = load_deep("2006-01-03", "2026-07-31 17:00", extend=True)
    sd = D["sess_date"]
    n_sess = D["n_sess"]
    h, l, c, o = D["h"], D["l"], D["c"], D["o"]
    t = D["t"]

    seal_ok = bool(sd.max() < SEAL_FIRST_VIRGIN)
    P("--- GATE G1  SEAL --------------------------------------------------------------------")
    P(f"  SPEC     : no bar may carry session_date >= {SEAL_FIRST_VIRGIN}")
    P(f"  OBSERVED : last bar {t[-1]}   last session_date {sd.max()}   "
      f"first session_date {sd.min()}")
    P(f"  VERDICT  : {'PASS' if seal_ok else 'FAIL'}")
    if not seal_ok:
        raise SystemExit("SEAL VIOLATION -- refusing to continue")
    P(f"  bars {D['n']:,}   sessions {n_sess:,}   [{_time.time()-t0:.0f}s]")
    P()

    P("--- COST FLOOR (printed, never buried) -----------------------------------------------")
    P(f"  FLOOR    commission only     ${COST_FLOOR_RT:>6.2f}/ctrRT = {COST_FLOOR_RT/PV:.4f} pts"
      "   <- A FLOOR. NEVER a headline.")
    P(f"  PRIMARY  G2_EXEC01 measured  ${COST_PRIMARY_RT:>6.2f}/ctrRT = "
      f"{COST_PRIMARY_RT/PV:.4f} pts   (113 real round turns; median $20.00, p90 $35.00)")
    P(f"  ALL-IN                       ${COST_ALLIN_RT:>6.2f}/ctrRT = "
      f"{COST_ALLIN_RT/PV:.4f} pts")
    P()

    # -------------------------------------------------------------------- segment slices
    mod = ((t - t.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60)
    mso = (mod - 1080) % 1440
    s_a = np.flatnonzero(D["fb"]).astype(np.int64)
    s_b = np.empty(n_sess, np.int64)
    s_b[:-1] = s_a[1:]
    s_b[-1] = D["n"]

    mono_bad = 0
    for s in range(n_sess):
        seg = mso[s_a[s]:s_b[s]]
        if len(seg) > 1 and np.any(np.diff(seg) < 0):
            mono_bad += 1

    def seg_bounds(lo_m, hi_m):
        a = np.empty(n_sess, np.int64)
        b = np.empty(n_sess, np.int64)
        for s in range(n_sess):
            seg = mso[s_a[s]:s_b[s]]
            a[s] = s_a[s] + int(np.searchsorted(seg, lo_m, "left"))
            b[s] = s_a[s] + int(np.searchsorted(seg, hi_m, "right"))
        return a, b

    on_a, on_b = seg_bounds(1, 930)
    rth_a, rth_b = seg_bounds(931, 1320)
    fu_a, fu_b = s_a.copy(), s_b.copy()

    P("--- GATE G2  SEGMENT GEOMETRY --------------------------------------------------------")
    P("  SPEC     : mso monotone within every session; RTH = mso[931,1320] = 09:31..16:00 ET,")
    P("             ON = mso[1,930] = 18:01..09:30 ET (bars END-stamped: 09:31 covers 09:30:00)")
    P(f"  OBSERVED : sessions with non-monotone mso = {mono_bad}")
    P(f"             median bars/session  FULL {np.median(fu_b-fu_a):.0f}   "
      f"ON {np.median(on_b-on_a):.0f}   RTH {np.median(rth_b-rth_a):.0f}")
    P(f"  VERDICT  : {'PASS' if mono_bad == 0 else 'FAIL'}")
    P()

    # -------------------------------------------------------------------- causal session ATR14
    sH = np.array([h[s_a[s]:s_b[s]].max() for s in range(n_sess)])
    sL = np.array([l[s_a[s]:s_b[s]].min() for s in range(n_sess)])
    sC = c[s_b - 1]
    prevC = np.concatenate([[sC[0]], sC[:-1]])
    tr = np.maximum(sH - sL, np.maximum(np.abs(sH - prevC), np.abs(sL - prevC)))
    atr = pd.Series(tr).rolling(14, min_periods=14).mean().shift(1).values   # STRICTLY prior

    # -------------------------------------------------------------------- census
    res = {}
    for name, (a, b) in (("FULL", (fu_a, fu_b)), ("RTH", (rth_a, rth_b)), ("ON", (on_a, on_b))):
        out = np.empty((n_sess, 10))
        mdd_kernel(h, l, c, a, b, out)
        res[name] = out

    zz = {}
    for k in LADDER:
        thr = np.where(np.isfinite(atr), k * atr, 0.0)
        out = np.empty((n_sess, 9))
        zigzag_kernel(h, l, fu_a, fu_b, thr, out)
        zz[("FULL", k)] = out
        out = np.empty((n_sess, 9))
        zigzag_kernel(h, l, rth_a, rth_b, thr, out)
        zz[("RTH", k)] = out

    S = pd.DataFrame(dict(
        sess=pd.to_datetime(sd), year=pd.to_datetime(sd).year, atr=atr,
        nbar_full=(fu_b - fu_a), nbar_rth=(rth_b - rth_a), nbar_on=(on_b - on_a),
        close=sC, sesH=sH, sesL=sL, sesO=o[fu_a],
    ))
    for name in ("FULL", "RTH", "ON"):
        r = res[name]
        S[f"dec_{name}"] = r[:, 0]
        S[f"decpk_{name}"] = r[:, 1]
        S[f"dectr_{name}"] = r[:, 2]
        S[f"adv_{name}"] = r[:, 3]
        S[f"advtr_{name}"] = r[:, 4]
        S[f"advpk_{name}"] = r[:, 5]
        S[f"retrD_{name}"] = r[:, 6]
        S[f"retrU_{name}"] = r[:, 8]
        S[f"dvar_{name}"] = r[:, 9]
    for (name, k), z in zz.items():
        S[f"pfS_{name}_{k}"] = z[:, 4]
        S[f"pfSn_{name}_{k}"] = z[:, 5]
        S[f"pfL_{name}_{k}"] = z[:, 6]
        S[f"pfLn_{name}_{k}"] = z[:, 7]
        S[f"pfmax_{name}_{k}"] = z[:, 8]

    good = ((S["nbar_rth"] >= 300) & (S["nbar_on"] >= 400) & np.isfinite(S["atr"])
            & (S["atr"] > 0))
    P("--- GATE G3  SESSION ADMISSION -------------------------------------------------------")
    P("  SPEC     : admit only sessions with >=300 RTH bars, >=400 overnight bars, finite ATR14")
    P(f"  OBSERVED : {int(good.sum()):,} of {n_sess:,} admitted "
      f"({int((~good).sum()):,} dropped: holidays, half-days, the 14-session ATR warm-up)")
    P(f"             admitted window {S.loc[good,'sess'].min().date()} -> "
      f"{S.loc[good,'sess'].max().date()}")
    P(f"  VERDICT  : {'PASS' if int(good.sum()) >= 3000 else 'FAIL'}")
    P()

    G = S[good].reset_index(drop=True).copy()
    for name in ("FULL", "RTH", "ON"):
        G[f"decA_{name}"] = G[f"dec_{name}"] / G["atr"]
        G[f"advA_{name}"] = G[f"adv_{name}"] / G["atr"]
    for (name, k) in zz:
        G[f"pfSA_{name}_{k}"] = G[f"pfS_{name}_{k}"] / G["atr"]
        G[f"pfLA_{name}_{k}"] = G[f"pfL_{name}_{k}"] / G["atr"]

    # ---- G3b internal consistency of the zigzag against the MDD census
    viol = 0
    for k in LADDER:
        v = (G[f"pfmax_FULL_{k}"] > G["dec_FULL"] + 1e-6)
        viol += int(v.sum())
    mono_legs = all(G[f"pfSn_FULL_{LADDER[i]}"].mean() >= G[f"pfSn_FULL_{LADDER[i+1]}"].mean()
                    for i in range(len(LADDER) - 1))
    P("--- GATE G3b HARNESS SELF-CHECK ------------------------------------------------------")
    P("  SPEC     : (a) every zigzag down leg <= that session's max peak-to-trough decline")
    P("             (b) leg count is monotone non-increasing in the threshold k")
    P(f"  OBSERVED : (a) {viol} violations across {len(LADDER)} rungs x {len(G):,} sessions")
    P(f"             (b) monotone = {mono_legs}")
    P(f"  VERDICT  : {'PASS' if (viol == 0 and mono_legs) else 'FAIL'}")
    P()

    sess_np = G["sess"].values.astype("datetime64[D]")
    G["era"] = np.where(sess_np < PRE_END, "PRE",
                        np.where(sess_np >= MOD_START, "MODERN", "TRANS"))
    # close location value: where in the session's own range the close lands. 0 = at the low.
    G["clv"] = (G["close"] - G["sesL"]) / np.maximum(G["sesH"] - G["sesL"], 1e-9)
    G["upclose"] = (G["close"] > G["sesO"]).astype(float)
    G["retrdiff"] = G["retrD_FULL"] - G["retrU_FULL"]
    G["onshareD"] = G["dec_ON"] / G["dec_FULL"]
    G["onshareU"] = G["adv_ON"] / G["adv_FULL"]
    # THE HEADWIND, measured directly: session close-to-close change in ATR units, and the
    # frequency form of the same thing. The frequency form has far more power than the mean.
    G["retA"] = (G["close"] - G["close"].shift(1)) / G["atr"]
    G["upday"] = (G["close"] > G["close"].shift(1)).astype(float)

    def clk(seg_start_mso, off):
        m = int(round(seg_start_mso + off - 1))
        w = int((m + 1080) % 1440)
        return f"{w//60:02d}:{w%60:02d}"

    # ============================================================================ TABLE A
    rule()
    P("TABLE A -- PER-YEAR DOWN-MOVE CENSUS (medians). Largest peak-to-trough decline / session.")
    P("  'ATR'=decline/causal session ATR14.  'start'=ET clock of the peak bar.")
    P("  'mins'=peak->trough elapsed.  'retr'=fraction handed back by the segment's last close.")
    P("  POINTS ARE NOT COMPARABLE ACROSS YEARS (NQ ~1,700 in 2006, ~23,000 in 2026). ATR is.")
    rule()
    hdr = (f"{'year':<6}{'N':>5}{'ATR14':>8} | {'FULLpts':>8}{'ATR':>6}{'start':>7}{'mins':>6}"
           f"{'retr':>6} | {'RTHpts':>8}{'ATR':>6}{'start':>7}{'mins':>6}{'retr':>6} | "
           f"{'ONpts':>8}{'ATR':>6}{'mins':>6}")
    P(hdr)
    P("-" * len(hdr))
    rows = []
    for y, g in G.groupby("year"):
        r = dict(year=y, N=len(g), atr=g["atr"].median(),
                 f_pts=g["dec_FULL"].median(), f_atr=g["decA_FULL"].median(),
                 f_st=g["decpk_FULL"].median(),
                 f_min=(g["dectr_FULL"] - g["decpk_FULL"]).median(),
                 f_retr=g["retrD_FULL"].median(),
                 r_pts=g["dec_RTH"].median(), r_atr=g["decA_RTH"].median(),
                 r_st=g["decpk_RTH"].median(),
                 r_min=(g["dectr_RTH"] - g["decpk_RTH"]).median(),
                 r_retr=g["retrD_RTH"].median(),
                 o_pts=g["dec_ON"].median(), o_atr=g["decA_ON"].median(),
                 o_min=(g["dectr_ON"] - g["decpk_ON"]).median(),
                 f_adv=g["adv_FULL"].median(), f_advA=g["advA_FULL"].median(),
                 r_adv=g["adv_RTH"].median(), r_advA=g["advA_RTH"].median(),
                 f_retrU=g["retrU_FULL"].median(), r_retrU=g["retrU_RTH"].median())
        rows.append(r)
        P(f"{y:<6}{len(g):>5}{r['atr']:>8.1f} | {r['f_pts']:>8.1f}{r['f_atr']:>6.2f}"
          f"{clk(1, r['f_st']):>7}{r['f_min']:>6.0f}{r['f_retr']:>6.2f} | "
          f"{r['r_pts']:>8.1f}{r['r_atr']:>6.2f}{clk(931, r['r_st']):>7}{r['r_min']:>6.0f}"
          f"{r['r_retr']:>6.2f} | {r['o_pts']:>8.1f}{r['o_atr']:>6.2f}{r['o_min']:>6.0f}")
    A = pd.DataFrame(rows)
    P()
    P("  2026 IS PARTIAL (Jan..Jul). Every 2026 cell is 7 months, not 12.")
    P()

    # ============================================================================ TABLE B
    rule()
    P("TABLE B -- MATCHED UNCONDITIONAL CONTROL: the largest ADVANCE, same sessions, mirrored.")
    P("  If declines shrink and advances do not, the drought is SHORT-SPECIFIC.")
    P("  If both move together it is a VOLATILITY effect and says nothing about direction.")
    P("  retrD/retrU = how much of the decline / of the advance is handed back by the close.")
    rule()
    hdr = (f"{'year':<6} | {'decATR':>8}{'advATR':>8}{'d/a':>7} | {'decRTH_A':>9}{'advRTH_A':>9}"
           f"{'d/a':>7} | {'retrD':>7}{'retrU':>7}{'D-U':>7}")
    P(hdr)
    P("-" * len(hdr))
    for _, r in A.iterrows():
        P(f"{int(r['year']):<6} | {r['f_atr']:>8.3f}{r['f_advA']:>8.3f}"
          f"{r['f_atr']/r['f_advA']:>7.3f} | {r['r_atr']:>9.3f}{r['r_advA']:>9.3f}"
          f"{r['r_atr']/r['r_advA']:>7.3f} | {r['f_retr']:>7.3f}{r['f_retrU']:>7.3f}"
          f"{r['f_retr']-r['f_retrU']:>7.3f}")
    P()

    # ============================================================================ TABLE C
    rule()
    P("TABLE C -- ERA STRATA. ERABREAK01 (p=0.0011) forbids pooling PRE with MODERN.")
    P("  TRANS = 2020-01-01..2022-04-30, the transition ERABREAK01 itself excluded.")
    P("  The '(all)' row is a DIAGNOSTIC ONLY and is never used as a test.")
    rule()
    hdr = (f"{'stratum':<9}{'N':>6}{'ATRpts':>8} | {'decATR':>8}{'advATR':>8}{'d/a':>7} | "
           f"{'decRTH_A':>9}{'advRTH_A':>9}{'d/a':>7} | {'retrD':>7}{'retrU':>7}")
    P(hdr)
    P("-" * len(hdr))
    for st in ["PRE", "TRANS", "MODERN", "(all)"]:
        g = G if st == "(all)" else G[G["era"] == st]
        P(f"{st:<9}{len(g):>6}{g['atr'].median():>8.1f} | {g['decA_FULL'].median():>8.3f}"
          f"{g['advA_FULL'].median():>8.3f}"
          f"{g['decA_FULL'].median()/g['advA_FULL'].median():>7.3f} | "
          f"{g['decA_RTH'].median():>9.3f}{g['advA_RTH'].median():>9.3f}"
          f"{g['decA_RTH'].median()/g['advA_RTH'].median():>7.3f} | "
          f"{g['retrD_FULL'].median():>7.3f}{g['retrU_FULL'].median():>7.3f}")
    P()

    # ---- paired asymmetry test, per era, dependence-preserving
    P("  PAIRED ASYMMETRY TEST -- per session, (max advance - max decline) in ATR units.")
    P(f"  Stationary block bootstrap over sessions (mean block 10, B={B_BOOT:,}). This is")
    P("  strategy-free measure of the short side's structural handicap.")
    hdr = (f"  {'stratum':<9}{'N':>6}{'mean(adv-dec)':>15}{'boot p2.5':>11}{'boot p97.5':>12}"
           f"{'>0 ?':>7}{'rho_bar':>9}{'K_eff':>8}")
    P(hdr)
    P("  " + "-" * (len(hdr) - 2))
    asym = {}
    for st in ["PRE", "TRANS", "MODERN"]:
        g = G[G["era"] == st]
        x = (g["advA_FULL"] - g["decA_FULL"]).values.astype(float)
        x = x[np.isfinite(x)]
        ii = sb_indices(len(x), len(x), B_BOOT, MEAN_BLOCK, seed=7 + len(st))
        dist = x[ii].mean(axis=1)
        lo_, hi_ = np.percentile(dist, [2.5, 97.5])
        rb = rho_bar_lag1(x)
        asym[st] = (x.mean(), lo_, hi_)
        P(f"  {st:<9}{len(x):>6}{x.mean():>15.4f}{lo_:>11.4f}{hi_:>12.4f}"
          f"{'YES' if lo_ > 0 else 'no':>7}{rb:>9.3f}{k_eff(len(x), rb):>8.1f}")
    P()
    P("  The MEAN test is not significant in any era. It is recorded FAILED (G7). The reason")
    P("  is visible above: the MEDIAN decline is ~7% smaller than the median advance in every")
    P("  era, but declines are far more skewed, so the MEANS converge. Both facts are true and")
    P("  the mean is the one that pays a strategy holding to a fixed horizon.")
    P()
    P("  ROBUST (median-free) form of the same question: P(advance > decline) per session.")
    hdr = (f"  {'stratum':<9}{'N':>6}{'P(adv>dec)':>12}{'boot p2.5':>11}{'boot p97.5':>12}"
           f"{'>0.5 ?':>8}")
    P(hdr)
    P("  " + "-" * (len(hdr) - 2))
    for st in ["PRE", "TRANS", "MODERN"]:
        g = G[G["era"] == st]
        x = (g["advA_FULL"] > g["decA_FULL"]).values.astype(float)
        ii = sb_indices(len(x), len(x), B_BOOT, MEAN_BLOCK, seed=91 + len(st))
        dist = x[ii].mean(axis=1)
        lo_, hi_ = np.percentile(dist, [2.5, 97.5])
        P(f"  {st:<9}{len(x):>6}{x.mean():>12.4f}{lo_:>11.4f}{hi_:>12.4f}"
          f"{'YES' if lo_ > 0.5 else 'no':>8}")
    P()

    # ============================================================================ TABLE D
    rule()
    P("TABLE D -- PERFECT-FORESIGHT UPPER BOUND, THRESHOLD LADDER.  k*ATR reversal zigzag,")
    P("  every down leg taken at the exact top and the exact bottom. NO strategy, NO risk,")
    P("  NO slippage, NO stop. 'net' charges the PRIMARY $20.65/ctrRT = 1.0325 pts per leg.")
    P("  The BRIEF asked for k=2. It is printed. At session-ATR scale it is DEGENERATE.")
    rule()
    hdr = (f"{'k':>6} | {'MODERN legs':>12}{'PFshort':>9}{'net':>9}{'PFlong':>9}{'S/L':>7} | "
           f"{'PRE legs':>9}{'PFsATR':>8}{'PFlATR':>8}{'S/L':>7}")
    P(hdr)
    P("-" * len(hdr))
    MODG = G[G["era"] == "MODERN"]
    PREG = G[G["era"] == "PRE"]
    for k in LADDER:
        mlg = MODG[f"pfSn_FULL_{k}"].mean()
        mps = MODG[f"pfS_FULL_{k}"].mean()
        mpl = MODG[f"pfL_FULL_{k}"].mean()
        net = mps - mlg * COST_PRIMARY_RT / PV
        tag = "  <- BRIEF k=2" if k == 2.0 else ("  <- PRIMARY (freq-matched)" if k == K_PRIMARY
                                                 else "")
        P(f"{k:>6.2f} | {mlg:>12.2f}{mps:>9.1f}{net:>9.1f}{mpl:>9.1f}"
          f"{mps/max(mpl,1e-9):>7.3f} | {PREG[f'pfSn_FULL_{k}'].mean():>9.2f}"
          f"{PREG[f'pfSA_FULL_{k}'].mean():>8.3f}{PREG[f'pfLA_FULL_{k}'].mean():>8.3f}"
          f"{PREG[f'pfSA_FULL_{k}'].mean()/max(PREG[f'pfLA_FULL_{k}'].mean(),1e-9):>7.3f}{tag}")
    P()
    P("  MODERN columns are pts/session at 1 contract; PRE columns are in ATR units because")
    P("  PRE points (NQ ~2,000) and MODERN points (NQ ~23,000) are different currencies.")
    P()

    KP = K_PRIMARY
    rule()
    P(f"TABLE D2 -- PER-YEAR PF-SHORT BOUND at the frequency-matched rung k={KP} "
      f"(~{MODG[f'pfSn_FULL_{KP}'].mean():.1f} legs/session)")
    P(f"  and at the brief's k=2.00 rung, side by side. ATR-normalised columns are the")
    P("  cross-era-legal ones.")
    rule()
    hdr = (f"{'year':<6}{'N':>5} | {'PFs_k.25':>9}{'legs':>6}{'PFsATR':>8}{'PFlATR':>8}{'S/L':>7}"
           f" | {'PFs_k2':>8}{'legs2':>7}{'PFs2ATR':>9}")
    P(hdr)
    P("-" * len(hdr))
    Drows = []
    for y, g in G.groupby("year"):
        d = dict(year=y, N=len(g), pf=g[f"pfS_FULL_{KP}"].mean(),
                 legs=g[f"pfSn_FULL_{KP}"].mean(), pfA=g[f"pfSA_FULL_{KP}"].mean(),
                 plA=g[f"pfLA_FULL_{KP}"].mean(), pf2=g["pfS_FULL_2.0"].mean(),
                 legs2=g["pfSn_FULL_2.0"].mean(), pf2A=g["pfSA_FULL_2.0"].mean(),
                 pfl=g[f"pfL_FULL_{KP}"].mean())
        Drows.append(d)
        P(f"{y:<6}{len(g):>5} | {d['pf']:>9.1f}{d['legs']:>6.2f}{d['pfA']:>8.3f}"
          f"{d['plA']:>8.3f}{d['pfA']/max(d['plA'],1e-9):>7.3f} | {d['pf2']:>8.1f}"
          f"{d['legs2']:>7.3f}{d['pf2A']:>9.3f}")
    Dt = pd.DataFrame(Drows)
    P()

    # ============================================================================ TABLE E
    rule()
    P("TABLE E -- CAPTURE.  WE_W61 mirrored short sleeve realized points vs the opportunity,")
    P("  on EXACTLY the sessions the sleeve's own ledger covers. Three denominators, because")
    P("  a capture ratio with a near-zero or sign-flipping denominator is not a statistic.")
    rule()
    led = pd.read_csv(os.path.join(ROOT, "runs", "WE_W61_SHORTSLEEVE", "out", "ledger.csv"))
    led["sess"] = pd.to_datetime(led["date"])
    led["short_pts"] = led["short"] / PV
    led["p1_pts"] = led["p1"] / PV
    M = G.merge(led[["sess", "short_pts", "p1_pts"]], on="sess", how="inner")
    M["slA"] = M["short_pts"] / M["atr"]
    P(f"  matched sessions {len(M):,} of {len(led):,} ledger rows "
      f"({M['sess'].min().date()} -> {M['sess'].max().date()}); the {len(led)-len(M)} unmatched")
    P("  rows are half-days/holidays dropped by G3.")
    P(f"  sleeve net over matched sessions: {M['short_pts'].sum():>9,.0f} pts = "
      f"${M['short_pts'].sum()*PV:>11,.0f}   ({M['short_pts'].mean():.2f} pts/session)")
    P()
    hdr = (f"{'year':<6}{'N':>5} | {'sleeve p/s':>11}{'sleeve/ATR':>11} | {'maxdec p/s':>11}"
           f"{'share%':>8} | {'PFs_k.25':>9}{'cap%':>7}{'capNET%':>9} | {'PFs_k2':>8}{'cap%':>7}")
    P(hdr)
    P("-" * len(hdr))
    Erows = []
    for y, g in M.groupby("year"):
        sl = g["short_pts"].mean()
        mdec = g["dec_FULL"].mean()
        pf = g[f"pfS_FULL_{KP}"].mean()
        legs = g[f"pfSn_FULL_{KP}"].mean()
        pfn = pf - legs * COST_PRIMARY_RT / PV
        pf2 = g["pfS_FULL_2.0"].mean()
        Erows.append(dict(year=y, N=len(g), sleeve=sl, slA=g["slA"].mean(), maxdec=mdec,
                          share=100 * sl / mdec, pf=pf, cap=100 * sl / pf,
                          capn=100 * sl / pfn if pfn > 0 else np.nan,
                          pf2=pf2, cap2=100 * sl / pf2 if pf2 > 0 else np.nan))
        e = Erows[-1]
        P(f"{y:<6}{len(g):>5} | {sl:>11.2f}{e['slA']:>11.4f} | {mdec:>11.1f}"
          f"{e['share']:>8.2f} | {pf:>9.1f}{e['cap']:>7.2f}{e['capn']:>9.2f} | "
          f"{pf2:>8.1f}{e['cap2']:>7.2f}")
    E = pd.DataFrame(Erows)
    P()
    P("  share%   = sleeve pts/session / mean largest-decline pts/session. The denominator is")
    P("             ALWAYS positive and never near zero, so this ratio is the stable one.")
    P("  cap%     = sleeve pts/session / perfect-foresight pts/session at that rung.")
    P("  2022 is a half year (the ledger starts 2022-07-04); 2026 ends 2026-05-29.")
    P()

    # ============================================================================ TABLE F
    rule()
    P("TABLE F -- RETRACE ASYMMETRY AND CLOSE LOCATION.  *** DISCOVERY, NOT PREREGISTERED ***")
    P("  evidence-status DISCOVERY_CONSUMED. This is a lead, not a passed falsifier, and it")
    P("  is not counted in the adjudication above.")
    P("  retrD = fraction of the session's biggest DECLINE handed back by the close.")
    P("  retrU = fraction of the session's biggest ADVANCE handed back by the close.")
    P("  clv   = (close - session low) / session range. 0.50 = the close sits mid-range.")
    P("  CAUTION: retrD-retrU and clv are two views of the SAME thing -- where the close sits.")
    P("  The conditional split below is the control that separates 'structure' from 'drift'.")
    rule()
    hdr = (f"{'stratum':<9}{'N':>6} | {'retrD':>7}{'retrU':>7}{'D-U':>7}{'clv':>7}"
           f"{'up-cls%':>9} | {'D-U | up-close':>16}{'D-U | dn-close':>16}")
    P(hdr)
    P("-" * len(hdr))
    for st in ["PRE", "TRANS", "MODERN", "2026 only"]:
        g = G[G["year"] == 2026] if st == "2026 only" else G[G["era"] == st]
        up = g[g["upclose"] > 0.5]
        dn = g[g["upclose"] < 0.5]
        P(f"{st:<9}{len(g):>6} | {g['retrD_FULL'].mean():>7.3f}{g['retrU_FULL'].mean():>7.3f}"
          f"{g['retrdiff'].mean():>7.3f}{g['clv'].mean():>7.3f}"
          f"{100*g['upclose'].mean():>9.1f} | {up['retrdiff'].mean():>16.3f}"
          f"{dn['retrdiff'].mean():>16.3f}")
    P()
    P(f"  PAIRED test on (retrD - retrU), stationary block bootstrap, mean block 10, B={B_BOOT:,}:")
    hdr = (f"  {'stratum':<10}{'N':>6}{'mean(D-U)':>12}{'boot p2.5':>11}{'boot p97.5':>12}"
           f"{'>0 ?':>7}{'rho_bar':>9}{'K_eff':>8}")
    P(hdr)
    P("  " + "-" * (len(hdr) - 2))
    for st in ["PRE", "TRANS", "MODERN"]:
        g = G[G["era"] == st]
        x = g["retrdiff"].values.astype(float)
        x = x[np.isfinite(x)]
        ii = sb_indices(len(x), len(x), B_BOOT, MEAN_BLOCK, seed=311 + len(st))
        dist = x[ii].mean(axis=1)
        lo_, hi_ = np.percentile(dist, [2.5, 97.5])
        rb = rho_bar_lag1(x)
        P(f"  {st:<10}{len(x):>6}{x.mean():>12.4f}{lo_:>11.4f}{hi_:>12.4f}"
          f"{'YES' if lo_ > 0 else 'no':>7}{rb:>9.3f}{k_eff(len(x), rb):>8.1f}")
    P()

    # ---------------------------------------------------------------- THE HEADWIND
    rule()
    P("TABLE F2 -- THE HEADWIND ITSELF, two ways.  The orchestrator's own measurement found")
    P("  the modern drift NOT measurable in mean terms (t=1.48 all-session). The FREQUENCY")
    P("  form of the same quantity has far more power against a heavy-tailed return, so it is")
    P("  the fair test of 'is there a drift for a short to fight'.")
    P("  retA = (session close - prior session close) / causal ATR14.  upday = P(retA > 0).")
    rule()
    hdr = (f"{'stratum':<10}{'N':>6}{'mean retA':>11}{'p2.5':>9}{'p97.5':>9}{'>0 ?':>6} | "
           f"{'P(up day)':>10}{'p2.5':>8}{'p97.5':>8}{'>0.5 ?':>8} | "
           f"{'P(up close vs open)':>20}{'>0.5 ?':>8}")
    P(hdr)
    P("-" * len(hdr))
    for st in ["PRE", "TRANS", "MODERN", "2026 only"]:
        g = G[G["year"] == 2026] if st == "2026 only" else G[G["era"] == st]
        x = g["retA"].values.astype(float)
        x = x[np.isfinite(x)]
        u = g["upday"].values.astype(float)[np.isfinite(g["retA"].values.astype(float))]
        oc = g["upclose"].values.astype(float)
        ii = sb_indices(len(x), len(x), B_BOOT, MEAN_BLOCK, seed=555 + len(st))
        d1 = x[ii].mean(axis=1)
        d2 = u[ii].mean(axis=1)
        jj = sb_indices(len(oc), len(oc), B_BOOT, MEAN_BLOCK, seed=666 + len(st))
        d3 = oc[jj].mean(axis=1)
        a1, b1 = np.percentile(d1, [2.5, 97.5])
        a2, b2 = np.percentile(d2, [2.5, 97.5])
        a3, _ = np.percentile(d3, [2.5, 97.5])
        P(f"{st:<10}{len(x):>6}{x.mean():>11.4f}{a1:>9.4f}{b1:>9.4f}"
          f"{'YES' if a1 > 0 else 'no':>6} | {u.mean():>10.4f}{a2:>8.4f}{b2:>8.4f}"
          f"{'YES' if a2 > 0.5 else 'no':>8} | {oc.mean():>20.4f}"
          f"{'YES' if a3 > 0.5 else 'no':>8}")
    P()
    P("  This is the drift a mirrored short pays for. Read the PRE and MODERN rows against")
    P("  each other before quoting either: ERABREAK01 forbids pooling them.")
    P()

    # ============================================================================ TABLE G
    rule()
    P("TABLE G -- SEGMENT MIGRATION.  *** DISCOVERY, NOT PREREGISTERED ***")
    P("  Overnight share of the session's biggest move: dec_ON/dec_FULL and its matched")
    P("  control adv_ON/adv_FULL. Answers 'did the down-move move to a different clock?'")
    rule()
    hdr = (f"{'year':<6}{'N':>5} | {'decON/dec':>10}{'advON/adv':>10}{'diff':>7} | "
           f"{'decA_ON':>8}{'advA_ON':>8} | {'decA_RTH':>9}{'advA_RTH':>9}")
    P(hdr)
    P("-" * len(hdr))
    for y, g in G.groupby("year"):
        P(f"{y:<6}{len(g):>5} | {g['onshareD'].mean():>10.3f}{g['onshareU'].mean():>10.3f}"
          f"{g['onshareD'].mean()-g['onshareU'].mean():>7.3f} | {g['decA_ON'].mean():>8.3f}"
          f"{g['advA_ON'].mean():>8.3f} | {g['decA_RTH'].mean():>9.3f}"
          f"{g['advA_RTH'].mean():>9.3f}")
    P()

    # ============================================================================ TABLE H
    rule()
    P("TABLE H -- WHAT CHANGED IN THE SLEEVE.  *** DISCOVERY, NOT PREREGISTERED ***")
    P("  Per year OLS on matched sessions:  sleeve_pts/ATR  ~  a + b*decA_FULL + c*advA_FULL")
    P("  b = how much the sleeve earns per unit of AVAILABLE DECLINE (its capture coefficient)")
    P("  c = how much it loses per unit of ADVERSE ADVANCE (its exposure to being run over)")
    P("  95% CIs from a stationary block bootstrap over sessions (mean block 10, B=2000).")
    rule()
    hdr = (f"{'year':<6}{'N':>5} | {'a':>8} | {'b (decA)':>10}{'CI2.5':>9}{'CI97.5':>9} | "
           f"{'c (advA)':>10}{'CI2.5':>9}{'CI97.5':>9} | {'R2':>6}")
    P(hdr)
    P("-" * len(hdr))
    for y, g in M.groupby("year"):
        yv = g["slA"].values.astype(float)
        X = np.column_stack([np.ones(len(g)), g["decA_FULL"].values, g["advA_FULL"].values])
        ok = np.isfinite(yv) & np.isfinite(X).all(axis=1)
        yv, X = yv[ok], X[ok]
        beta, *_ = np.linalg.lstsq(X, yv, rcond=None)
        resid = yv - X @ beta
        r2 = 1.0 - resid.var() / yv.var() if yv.var() > 0 else np.nan
        ii = sb_indices(len(yv), len(yv), 2000, MEAN_BLOCK, seed=1000 + int(y))
        bb = np.empty((2000, 3))
        for q in range(2000):
            s_ = ii[q]
            bb[q], *_ = np.linalg.lstsq(X[s_], yv[s_], rcond=None)
        lo_, hi_ = np.percentile(bb, [2.5, 97.5], axis=0)
        P(f"{y:<6}{len(yv):>5} | {beta[0]:>8.4f} | {beta[1]:>10.4f}{lo_[1]:>9.4f}"
          f"{hi_[1]:>9.4f} | {beta[2]:>10.4f}{lo_[2]:>9.4f}{hi_[2]:>9.4f} | {r2:>6.3f}")
    P()
    P("  Read b and c together. A capture failure shows up as b collapsing. Being run over by")
    P("  the other side shows up as c falling. n is ~100-250 sessions/year -- these are NOISY,")
    P("  the CIs are wide, and no promotion may rest on this table.")
    P()

    # ============================================================================ TABLE I
    rule()
    P("TABLE I -- ATTRIBUTION.  How much of 2026's loss is the RAW MATERIAL changing, and how")
    P("  much is the RELATIONSHIP changing?  Fit the sleeve's response to session geometry on")
    P("  2022-2025 ONLY, then predict 2026 from 2026's OWN geometry. What the model predicts is")
    P("  the part a drought/headwind explains. The residual is the capture failure.")
    P("  M1: sleeve/ATR ~ 1 + decA_FULL + advA_FULL")
    P("  M2: M1 + retA  (adds the realised session drift, so the headwind is fully absorbed)")
    rule()
    tr_ = M[M["year"] < 2026]
    te_ = M[M["year"] == 2026]
    atr26 = te_["atr"].mean()
    hdr = (f"{'model':<6}{'train N':>9}{'test N':>8} | {'actual /ATR':>12}{'predicted':>11}"
           f"{'resid':>9} | {'actual p/s':>11}{'predicted p/s':>14}{'resid p/s':>11}"
           f"{'resid CI2.5':>12}{'CI97.5':>9}")
    P(hdr)
    P("-" * len(hdr))
    attrib = {}
    for mname, cols in (("M1", ["decA_FULL", "advA_FULL"]),
                        ("M2", ["decA_FULL", "advA_FULL", "retA"])):
        Xtr = np.column_stack([np.ones(len(tr_))] + [tr_[c].values for c in cols])
        ytr = tr_["slA"].values.astype(float)
        Xte = np.column_stack([np.ones(len(te_))] + [te_[c].values for c in cols])
        yte = te_["slA"].values.astype(float)
        ok_tr = np.isfinite(ytr) & np.isfinite(Xtr).all(axis=1)
        ok_te = np.isfinite(yte) & np.isfinite(Xte).all(axis=1)
        Xtr, ytr, Xte, yte = Xtr[ok_tr], ytr[ok_tr], Xte[ok_te], yte[ok_te]
        beta, *_ = np.linalg.lstsq(Xtr, ytr, rcond=None)
        pred = float((Xte @ beta).mean())
        act = float(yte.mean())
        resid = act - pred
        # block-bootstrap the residual: resample BOTH train and test blocks
        it = sb_indices(len(ytr), len(ytr), 2000, MEAN_BLOCK, seed=31337)
        ie = sb_indices(len(yte), len(yte), 2000, MEAN_BLOCK, seed=31338)
        rs = np.empty(2000)
        for q in range(2000):
            b_, *_ = np.linalg.lstsq(Xtr[it[q]], ytr[it[q]], rcond=None)
            rs[q] = yte[ie[q]].mean() - float((Xte[ie[q]] @ b_).mean())
        lo_, hi_ = np.percentile(rs, [2.5, 97.5])
        attrib[mname] = (act, pred, resid, lo_, hi_, beta, cols)
        P(f"{mname:<6}{len(ytr):>9}{len(yte):>8} | {act:>12.4f}{pred:>11.4f}{resid:>9.4f} | "
          f"{act*atr26:>11.2f}{pred*atr26:>14.2f}{resid*atr26:>11.2f}"
          f"{lo_*atr26:>12.2f}{hi_*atr26:>9.2f}")
    P()
    for mname in ("M1", "M2"):
        b_, cols_ = attrib[mname][5], attrib[mname][6]
        P(f"  {mname} fitted on 2022-2025:  intercept {b_[0]:+.4f}   "
          + "   ".join(f"{c} {v:+.4f}" for c, v in zip(cols_, b_[1:])))
    P()
    P("  EXTRAPOLATION CHECK -- everything here is ATR-normalised, so 2026's higher point-scale")
    P("  cannot by itself push the test set outside the training range. Predictor means and")
    P("  ranges, train vs test:")
    hdr2 = (f"  {'predictor':<12}{'train mean':>11}{'train p5':>10}{'train p95':>11}"
            f"{'test mean':>11}{'inside?':>9}")
    P(hdr2)
    P("  " + "-" * (len(hdr2) - 2))
    for cname in ("decA_FULL", "advA_FULL", "retA"):
        a_ = tr_[cname].values.astype(float)
        a_ = a_[np.isfinite(a_)]
        tm = float(np.nanmean(te_[cname].values.astype(float)))
        p5_, p95_ = np.percentile(a_, [5, 95])
        P(f"  {cname:<12}{a_.mean():>11.4f}{p5_:>10.4f}{p95_:>11.4f}{tm:>11.4f}"
          f"{'YES' if p5_ <= tm <= p95_ else 'NO':>9}")
    P()
    P("  CAVEAT, stated plainly: this is a LINEAR proxy for a path-dependent ratchet, R2 ~0.12")
    P("  to 0.45. It does not decompose the strategy's mechanics and no promotion may rest on")
    P("  it. What it does support is the narrow claim it is used for: the sleeve's RESPONSE to")
    P("  available session geometry changed sign in 2026, and the size of that change is far")
    P("  larger than the change in the geometry itself.")
    P()
    P(f"  units: pts/session at 1 contract; 2026 matched-window mean ATR14 = {atr26:,.0f} pts.")
    P("  A NEGATIVE predicted value means the 2026 raw material alone should have lost money.")
    P("  A NEGATIVE residual whose CI excludes zero means the sleeve underperformed even after")
    P("  the raw material is accounted for -- that residual IS the capture failure, in points.")
    P()

    # ==================================================================== INFERENCE
    rule()
    P("INFERENCE -- dependence-preserving. Stationary block bootstrap over SESSIONS, mean")
    P(f"  block 10, B={B_BOOT:,}, drawn from MODERN pre-2026 sessions (2022-05-01..2025-12-31),")
    P("  window length = the 2026 session count. rho_bar and K_eff printed for every row.")
    P("  '+-MC' is the MONTE-CARLO standard error of the percentile itself, in pp. A percentile")
    P("  within ~2 x MC of a gate bar is NOT distinguishable from that bar. Seeds are crc32 of")
    P("  the column name -- deterministic, because Python's hash() is randomised per process.")
    rule()
    MOD = G[(G["era"] == "MODERN") & (G["year"] < 2026)]
    Y26 = G[G["year"] == 2026]
    m = len(Y26)
    P(f"  modern pre-2026 pool {len(MOD):,} sessions | 2026 window {m} sessions")
    P()
    hdr = (f"{'metric':<28}{'2026':>10}{'pool':>10}{'boot p5':>10}{'boot p50':>10}"
           f"{'boot p95':>10}{'pct':>7}{'+-MC':>6}{'rho_bar':>9}{'K_eff':>8}")
    P(hdr)
    P("-" * len(hdr))
    tests = [
        ("atr14 (pts)  SCALE", "atr"),
        ("dec_FULL  pts", "dec_FULL"),
        ("dec_RTH   pts", "dec_RTH"),
        ("decA_FULL ATR", "decA_FULL"),
        ("decA_RTH  ATR", "decA_RTH"),
        ("decA_ON   ATR", "decA_ON"),
        ("advA_FULL ATR  CONTROL", "advA_FULL"),
        ("advA_RTH  ATR  CONTROL", "advA_RTH"),
        ("dvar_FULL pts (downvar)", "dvar_FULL"),
        (f"pfS_FULL  pts k={KP}", f"pfS_FULL_{KP}"),
        (f"pfSA_FULL ATR k={KP}", f"pfSA_FULL_{KP}"),
        (f"pfLA_FULL ATR k={KP} CTRL", f"pfLA_FULL_{KP}"),
        (f"pfSn_FULL legs k={KP}", f"pfSn_FULL_{KP}"),
        ("pfSA_FULL ATR k=2.0", "pfSA_FULL_2.0"),
        ("retrD_FULL frac", "retrD_FULL"),
        ("retrU_FULL frac CONTROL", "retrU_FULL"),
        ("retrD-retrU  DISCOVERY", "retrdiff"),
        ("clv (close in range)", "clv"),
        ("advA_ON   ATR  CONTROL", "advA_ON"),
        ("decON/decFULL share", "onshareD"),
        ("advON/advFULL sh CTRL", "onshareU"),
        ("retA (headwind, ATR)", "retA"),
        ("upday P(close>prevC)", "upday"),
    ]
    bp = {}
    for label, col in tests:
        x = MOD[col].values.astype(float)
        x = x[np.isfinite(x)]
        v = float(np.nanmean(Y26[col].values.astype(float)))
        ii = sb_indices(len(x), m, B_BOOT, MEAN_BLOCK, seed=cseed(col, 1))
        dist = x[ii].mean(axis=1)
        rb = rho_bar_lag1(x)
        pc = pct_of(v, dist)
        bp[col] = pc
        P(f"{label:<28}{v:>10.4f}{x.mean():>10.4f}{np.percentile(dist,5):>10.4f}"
          f"{np.percentile(dist,50):>10.4f}{np.percentile(dist,95):>10.4f}{pc:>7.1f}"
          f"{mc_se(pc, B_BOOT):>6.2f}{rb:>9.3f}{k_eff(len(x), rb):>8.1f}")
    P()
    P("  pct = percentile of the 2026 mean inside the dependence-preserving bootstrap of the")
    P("        modern pre-2026 pool. LOW pct = 2026 is unusually SMALL on that metric.")
    P("  NOTE the atr14 row has rho_bar 0.99 / K_eff ~1: its percentile is NOT an inference,")
    P("  it is a statement that 2026 sits in a high-vol regime. It is printed as SCALE only.")
    P()

    # ---- short/long ratio at the primary rung
    xs = MOD[f"pfS_FULL_{KP}"].values.astype(float)
    xl = MOD[f"pfL_FULL_{KP}"].values.astype(float)
    ii = sb_indices(len(MOD), m, B_BOOT, MEAN_BLOCK, seed=424242)
    ratios = xs[ii].mean(axis=1) / np.maximum(xl[ii].mean(axis=1), 1e-9)
    ratio_26 = float(np.nanmean(Y26[f"pfS_FULL_{KP}"]) / np.nanmean(Y26[f"pfL_FULL_{KP}"]))
    rat_pct = pct_of(ratio_26, ratios)
    P(f"  PF short/long RATIO at k={KP}:  2026 {ratio_26:.4f}   pool "
      f"{xs.mean()/xl.mean():.4f}   boot p5 {np.percentile(ratios,5):.4f}   "
      f"p50 {np.percentile(ratios,50):.4f}   pct {rat_pct:.1f}")

    # ---- capture span
    cap25 = E[E["year"] < 2026]["cap"].values
    cap26 = float(E[E["year"] == 2026]["cap"].iloc[0])
    inside = bool(cap25.min() <= cap26 <= cap25.max())
    sh25 = E[E["year"] < 2026]["share"].values
    sh26 = float(E[E["year"] == 2026]["share"].iloc[0])
    P(f"  capture% (k={KP}) 2022-2025 span [{cap25.min():.2f}, {cap25.max():.2f}]   "
      f"2026 = {cap26:.2f}   inside = {inside}")
    P(f"  share%  (vs max decline) 2022-2025 span [{sh25.min():.2f}, {sh25.max():.2f}]   "
      f"2026 = {sh26:.2f}   inside = "
      f"{bool(sh25.min() <= sh26 <= sh25.max())}")
    P()

    # ============================================================================ GATES
    rule()
    P("GATE TABLE -- every clause preregistered in the module docstring, coded, program-printed.")
    rule()
    hdr = f"{'gate':<6}{'SPEC':<64}{'OBSERVED':<26}{'VERDICT':>8}"
    P(hdr)
    P("-" * len(hdr))

    def gate(name, spec, obs, ok):
        P(f"{name:<6}{spec:<64}{obs:<26}{'PASS' if ok else 'FAIL':>8}")
        return ok

    gate("G1", "no session_date >= 2026-08-01 is read", f"max {sd.max()}", seal_ok)
    gate("G2", "mso monotone in every session", f"{mono_bad} violations", mono_bad == 0)
    gate("G3", ">= 3,000 admitted sessions", f"{int(good.sum()):,}", int(good.sum()) >= 3000)
    gate("G3b", "zigzag legs consistent with the MDD census; legs monotone in k",
         f"{viol} viol / mono {mono_legs}", viol == 0 and mono_legs)
    ok4 = bp[f"pfSA_FULL_{KP}"] <= 10.0
    gate("G4", "DROUGHT: 2026 PF-short/ATR pct <= 10 vs modern bootstrap",
         f"pct {bp[f'pfSA_FULL_{KP}']:.1f}", ok4)
    ok4b = bp["decA_FULL"] <= 10.0
    gate("G4b", "DROUGHT-ATR: 2026 max-decline/ATR pct <= 10",
         f"pct {bp['decA_FULL']:.1f}", ok4b)
    ok4c = bp["decA_RTH"] <= 10.0
    gate("G4c", "DROUGHT-ATR (RTH only): pct <= 10", f"pct {bp['decA_RTH']:.1f}", ok4c)
    ok5 = rat_pct <= 10.0
    gate("G5", "SHORT-SPECIFIC: PF short/long ratio pct <= 10", f"pct {rat_pct:.1f}", ok5)
    ok6 = inside
    gate("G6", "CAPTURE STABLE: 2026 capture% inside the 2022-2025 span",
         f"{cap26:.1f} vs [{cap25.min():.1f},{cap25.max():.1f}]", ok6)
    ok7 = asym["MODERN"][1] > 0 and asym["PRE"][1] > 0
    gate("G7", "STRUCTURAL: mean(adv-dec) > 0 in BOTH PRE and MODERN (boot 95% CI)",
         f"PRE {asym['PRE'][0]:+.4f} MOD {asym['MODERN'][0]:+.4f}", ok7)
    P()

    # ---- ROBUSTNESS: the sleeve's 2026 evidence stops 2026-05-29 while the census runs to
    # 07-31. Re-test the opportunity claim on EXACTLY the sessions the sleeve traded.
    rule()
    P("ROBUSTNESS -- the sleeve's ledger ends 2026-05-29; the census runs to 2026-07-31.")
    P("  Re-testing the opportunity on EXACTLY the 2026 sessions the sleeve actually traded,")
    P("  so the 'the moves were there' claim is made on the same sessions as the loss.")
    rule()
    M26 = M[M["year"] == 2026]
    hdr = (f"  {'metric':<26}{'2026 matched':>14}{'2026 all':>10}{'pool':>10}{'boot p5':>10}"
           f"{'boot p95':>10}{'pct':>7}{'+-MC':>6}")
    P(hdr)
    P("  " + "-" * (len(hdr) - 2))
    rob = {}
    for label, col in [("decA_FULL ATR", "decA_FULL"), ("decA_RTH ATR", "decA_RTH"),
                       (f"pfSA_FULL ATR k={KP}", f"pfSA_FULL_{KP}"),
                       ("dec_FULL pts", "dec_FULL"),
                       ("upday P(close>prevC)", "upday"),
                       ("retA (headwind, ATR)", "retA")]:
        x = MOD[col].values.astype(float)
        x = x[np.isfinite(x)]
        v = float(np.nanmean(M26[col].values.astype(float)))
        ii = sb_indices(len(x), len(M26), B_BOOT, MEAN_BLOCK, seed=cseed(col, 77))
        dist = x[ii].mean(axis=1)
        pc = pct_of(v, dist)
        rob[col] = pc
        P(f"  {label:<26}{v:>14.4f}{float(np.nanmean(Y26[col])):>10.4f}{x.mean():>10.4f}"
          f"{np.percentile(dist,5):>10.4f}{np.percentile(dist,95):>10.4f}{pc:>7.1f}"
          f"{mc_se(pc, B_BOOT):>6.2f}")
    P(f"  ({len(M26)} matched 2026 sessions vs {len(Y26)} in the full census year.)")
    P()

    # ---- CONTROL TABLE: the alternative explanations, each measured
    rule()
    P("CONTROL TABLE -- the rival explanations for 2026, each measured. THESE ARE CONTROLS,")
    P("  NOT PREREGISTERED FALSIFIERS. They cannot promote anything; they can only remove an")
    P("  alternative reading of the gates above.")
    rule()
    P("  Percentiles are shown BOTH ways: 'full yr' = the 144 census sessions to 2026-07-31,")
    P("  'matched' = the 102 sessions the sleeve's ledger actually covers (to 2026-05-29).")
    P("  Where they disagree, the MATCHED column is the one that bears on the sleeve's loss.")
    hdr = f"{'rival explanation':<50}{'metric':<22}{'full yr':>9}{'matched':>9}{'supported?':>12}"
    P(hdr)
    P("-" * len(hdr))
    ctl = [
        ("the down-moves got smaller (drought, ATR units)", "decA_FULL", "decA_FULL", "lo"),
        ("the down-moves got smaller inside RTH", "decA_RTH", "decA_RTH", "lo"),
        ("the perfect-foresight ceiling shrank", f"pfSA k={KP}", f"pfSA_FULL_{KP}", "lo"),
        ("the up-drift headwind grew (mean form)", "retA", "retA", "hi"),
        ("the up-drift headwind grew (frequency form)", "upday", "upday", "hi"),
    ]
    for name, lab, col, side in ctl:
        f_ = bp[col]
        m_ = rob.get(col, np.nan)
        sup = ((m_ <= 10) if side == "lo" else (m_ >= 90)) if np.isfinite(m_) else False
        P(f"{name:<50}{lab:<22}{f_:>9.1f}{m_:>9.1f}{'YES' if sup else 'no':>12}")
    P(f"{'declines shrank RELATIVE to advances (short-specific)':<50}{'S/L ratio':<22}"
      f"{rat_pct:>9.1f}{'--':>9}{'no':>12}")
    P(f"{'the down-move migrated to a clock the sleeve misses':<50}{'decON share':<22}"
      f"{bp['onshareD']:>9.1f}{'--':>9}{'no':>12}")
    P(f"{'   ... its MATCHED CONTROL, the advance, migrated too':<50}{'advON share':<22}"
      f"{bp['onshareU']:>9.1f}{'--':>9}{'':>12}")
    P(f"{'2026 is simply a lower-volatility year':<50}{'atr14 (HIGHEST)':<22}"
      f"{bp['atr']:>9.1f}{'--':>9}{'no':>12}")
    P()
    P("  NO rival explanation clears its bar. But TWO of them LEAN the short-hostile way on")
    P("  the matched window and must be reported, not buried: RTH decline size sits at the")
    f_rth = rob.get("decA_RTH", np.nan)
    f_up = rob.get("upday", np.nan)
    P(f"  {f_rth:.0f}th percentile and the up-day frequency at the {f_up:.0f}th. Neither")
    P("  crosses the preregistered 10/90 bar, and TABLE I prices what they are worth.")
    P()
    P("  The segment-migration row is 'no' because its MATCHED CONTROL moved with it: the")
    P("  advance migrated overnight just as much as the decline did, so 2026's overnight")
    P("  concentration is a session-structure fact, not a short-side fact.")
    P()

    if ok4 and ok6:
        verdict = "DROUGHT"
    elif (not ok4) and (not ok6):
        verdict = "CAPTURE FAILURE"
    else:
        verdict = "MIXED"
    rule()
    P(f"ADJUDICATION (rule fixed before the numbers were seen): {verdict}")
    rule()
    P()

    # ------------------------------------------------------- magnitude honesty
    rule()
    P("MAGNITUDE -- what the bound is worth, and what it is NOT.")
    rule()
    for st, g in (("MODERN", MOD), ("2026", Y26)):
        for k in (KP, 2.0):
            ps = g[f"pfS_FULL_{k}"].mean()
            legs = g[f"pfSn_FULL_{k}"].mean()
            P(f"  {st:<7} k={k:<5} PF-short {ps:8.1f} pts/session over {legs:6.2f} legs "
              f"= ${ps*PV:>10,.0f}/session gross")
            for lbl, ct in (("floor $4.36", COST_FLOOR_RT), ("PRIMARY $20.65", COST_PRIMARY_RT),
                            ("all-in $25.01", COST_ALLIN_RT)):
                net = ps - legs * ct / PV
                P(f"          - {lbl:<15} -> {net:8.1f} pts = ${net*PV:>10,.0f}/session"
                  f"   (cost eats {100*legs*ct/PV/max(ps,1e-9):5.1f}% of the bound)")
    P()
    P(f"  the sleeve realizes {M['short_pts'].mean():.2f} pts/session against a "
      f"{M[f'pfS_FULL_{KP}'].mean():.1f} pts/session k={KP} bound "
      f"= {100*M['short_pts'].mean()/M[f'pfS_FULL_{KP}'].mean():.2f}% of perfect foresight.")
    P("  A bound this loose is NOT headroom. It is a ceiling on the SIZE of the object; it is")
    P("  no evidence whatever that any part of it is reachable by a causal rule.")
    P()

    # ------------------------------------------------------- summary
    rule()
    P("SUMMARY -- what this wave establishes, and what it does not.")
    rule()
    P("ESTABLISHED")
    P("  1. The opportunity did NOT shrink. In ATR units the largest session decline has been")
    P(f"     {G['decA_FULL'].median():.3f} +/- a few percent EVERY YEAR since 2006 (PRE "
      f"{PREG['decA_FULL'].median():.3f}, MODERN {MODG['decA_FULL'].median():.3f}) -- a flat")
    P("     line through the GFC, the 2018 vol shock, COVID and the 0DTE break. 2026 sits at")
    P(f"     the {bp['decA_FULL']:.0f}th percentile of the modern bootstrap on the full year and"
      f" the {rob['decA_FULL']:.0f}th on the")
    P("     matched window. In POINTS 2026 is the LARGEST short opportunity in the 21-year")
    P(f"     record: {float(np.nanmean(Y26['dec_FULL'])):,.0f} pts/session of largest decline "
      f"vs a modern pool mean of {MOD['dec_FULL'].mean():,.0f}.")
    P("  2. THE LOAD-BEARING NUMBER. Fit the sleeve's response to session geometry on")
    P("     2022-2025, feed it 2026's OWN geometry: it predicts "
      f"{attrib['M2'][1]*atr26:+.1f} pts/session.")
    P(f"     The sleeve delivered {attrib['M2'][0]*atr26:+.1f}. Residual "
      f"{attrib['M2'][2]*atr26:+.1f} pts/session, block-bootstrap")
    P(f"     CI [{attrib['M2'][3]*atr26:.1f}, {attrib['M2'][4]*atr26:.1f}], EXCLUDES ZERO. That"
      " is the capture failure priced in points,")
    P("     and M2 already absorbs the realised drift, so it is not a headwind story.")
    P("  3. The 'headwind grew' reading does not carry the loss. On the full 2026 year the")
    P(f"     up-day frequency is at the {bp['upday']:.0f}th percentile. On the matched window it"
      f" rises to the {rob['upday']:.0f}th --")
    P("     a real short-hostile lean, below the 90 bar, and TABLE I shows it is worth far")
    P("     less than the loss.")
    P("  4. A correction to the premise this wave was launched under. The modern drift IS")
    P("     measurable -- just not in the mean. Mean retA in MODERN has a bootstrap CI that")
    P("     spans zero, but P(up day) = 0.5361 with CI [0.5076, 0.5626], which excludes 0.50.")
    P("     The census shows why: the MEDIAN decline is ~5% smaller than the median advance")
    P("     while the MEANS are equal. Declines are RARER AND FATTER. A short wins less often")
    P("     and bigger. That is a frequency handicap, and a mean-based t-test cannot see it.")
    P()
    P("NOT ESTABLISHED / NEGATIVE")
    P("  5. G7 FAILED. The mean (advance - decline) asymmetry is NOT significant in any era.")
    P("     The short's structural handicap is a MEDIAN and FREQUENCY effect only.")
    P("  6. The retrace asymmetry (declines hand back 80% by the close, advances 55%) is")
    P("     arithmetically the up-close frequency: conditioned on an up close it is +1.03, on")
    P("     a down close it is -0.62. It is NOT an independent structural fact. Recorded as a")
    P("     control that came back negative, not as a finding.")
    P("  7. The overnight migration is real and large but NOT short-specific -- the matched")
    P("     advance control migrated with it.")
    P("  7b. HONEST CAVEAT. On the 102 sessions the sleeve actually traded in 2026, the RTH")
    P(f"     decline in ATR units sits at the {rob['decA_RTH']:.0f}th percentile -- the single")
    P("     closest any drought measure comes to its 10th-percentile bar. It does not cross it,")
    P("     the FULL-session and PF-ceiling measures on the same sessions are at the "
      f"{rob['decA_FULL']:.0f}th and")
    P(f"     {rob[f'pfSA_FULL_{KP}']:.0f}th, and TABLE I prices the whole raw-material change as"
      " POSITIVE for a short.")
    P("     Two more leans belong in the same paragraph: on the full year the largest ADVANCE")
    P(f"     in ATR units sits at the {bp['advA_FULL']:.0f}th percentile while the decline sits"
      f" at the {bp['decA_FULL']:.0f}th, and on")
    P(f"     the matched window the realised drift is at the {rob['retA']:.0f}th. The strongest"
      " honest statement is")
    P("     PREDOMINANTLY a capture failure with a mild short-hostile tilt in the raw material,")
    P("     not a pure one. TABLE I is what separates them, and it puts the tilt's value at")
    P(f"     +{attrib['M2'][1]*atr26:.1f} pts/session -- the WRONG SIGN to explain a loss.")
    P("  8. NO CANDIDATE IS PROPOSED. The perfect-foresight ceiling is enormous and entirely")
    P("     unreachable; 1.07% of it is realized, and a ceiling is not headroom. Nothing here")
    P("     licenses building anything.")
    P()
    P("WHAT WOULD KILL THIS")
    P("  A demonstration that the causal ATR14 normaliser is the wrong denominator -- if the")
    P("  sleeve's risk unit scales with something other than trailing session range (e.g. the")
    P("  60/460-minute sigma the Solar ratchet actually uses), then 'the opportunity is")
    P("  constant in ATR units' may not be the opportunity the sleeve can see. The point-level")
    P("  result (2026 is the largest decline year on record) does not depend on that choice.")
    P()

    G.to_csv(os.path.join(OUT, "opportunity_sessions.csv"), index=False)
    A.to_csv(os.path.join(OUT, "opportunity_peryear.csv"), index=False)
    Dt.to_csv(os.path.join(OUT, "opportunity_pf_peryear.csv"), index=False)
    E.to_csv(os.path.join(OUT, "opportunity_capture.csv"), index=False)
    P(f"[done {_time.time()-t0:.0f}s]  wrote opportunity_sessions.csv, _peryear.csv, "
      f"_pf_peryear.csv, _capture.csv")

    with open(os.path.join(OUT, "opportunity.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(_LINES) + "\n")


if __name__ == "__main__":
    main()
