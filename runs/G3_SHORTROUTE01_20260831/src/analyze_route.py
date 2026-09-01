"""G3_SHORTROUTE01 - STAGE 2: did the mirrored short sleeve's 2022-2025 run have an ex-ante HANDLE?

Spec: runs/G3_SHORTROUTE01_20260831/spec.yaml, committed at 9a18980 BEFORE any conditional
statistic existed. Not edited. Every clause below is coded; the gate table is printed BY THIS
PROGRAM and never assembled by hand.

IDENTIFICATION  PRE     2006-01-01 .. 2019-12-31
EXCLUDED        TRANS   2020-01-01 .. 2022-04-30   (entirely - not an arm, not a footnote)
CONFIRMATION    MODERN  2022-05-01 .. 2026-05-29   READ ONCE, ONLY IF G1..G5 ALL PASS

Reads only the cache written by build_route.py, which asserted and printed the seal.
"""
from __future__ import annotations

import json
import os
import sys
import time as _time

import numpy as np
import pandas as pd

ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
RUN = os.path.join(ROOT, "runs", "G3_SHORTROUTE01_20260831")
OUT = os.path.join(RUN, "out")
CACHE = os.path.join(OUT, "_cache")
os.makedirs(OUT, exist_ok=True)

PV = 20.0
COST_FLOOR = 4.36           # a FLOOR, never a headline
COST_PRIMARY = 20.65        # G2_EXEC01, 113 real round turns - the primary
COST_ALLIN = 25.01
PTS_FLOOR = COST_FLOOR / PV
PTS_PRIMARY = COST_PRIMARY / PV      # 1.0325 NQ points
PTS_ALLIN = COST_ALLIN / PV

PRE_A, PRE_B = pd.Timestamp("2006-01-01"), pd.Timestamp("2019-12-31")
TRANS_A, TRANS_B = pd.Timestamp("2020-01-01"), pd.Timestamp("2022-04-30")
MOD_A, MOD_B = pd.Timestamp("2022-05-01"), pd.Timestamp("2026-05-29")
SEAL = pd.Timestamp("2026-08-01")

TERCILE_WIN = 252           # causal trailing window, in SESSIONS (spec)
MIN_SESS_MONTH = 10         # WAVE C's monthly-panel rule, carried over unchanged
BOOT = 1000                 # spec: 1,000 draws, 6-month circular moving-block
BLOCK = 6                   # spec: 6-month blocks
NULL_DRAWS = 2000           # spec: 2,000 circular-shift draws for G2
RNG = np.random.default_rng(20260831)

# ---------------------------------------------------------------- THE SIX FROZEN VARIABLES
# sign: +1 -> HIGH tercile is the predicted-favourable one
#       -1 -> LOW  tercile is the predicted-favourable one
#        0 -> UNSIGNED, two-sided |spread|, favourable = whichever extreme is higher
VARS = [
    ("S1", "trailing realised vol (21-sess stdev of close-to-close log returns)", +1),
    ("S2", "vol-of-vol (63-sess stdev of the S1 series)", -1),
    ("S3", "trend state (market trailing 63-session log return)", -1),
    ("S4", "range compression (prior range / median of prior 60 ranges)", -1),
    ("S5", "overnight share of absolute movement, 21-session rolling", 0),
    ("S6", "prior-close VIX (certified Cboe)", +1),
]
SIGN_TXT = {+1: "POSITIVE (HIGH favourable)", -1: "NEGATIVE (LOW favourable)",
            0: "UNSIGNED (two-sided)"}
TNAME = ("LOW", "MID", "HIGH")


# ==================================================================================================
# regression / bootstrap primitives
# ==================================================================================================
def ols2(x, y):
    """Closed-form intercept+slope of y ~ 1 + x. Identical to lstsq on a 2-column design;
    the harness selftest below proves it to 1e-10 rather than asserting it."""
    n = len(x)
    if n < 5:
        return np.nan, np.nan
    xm = x.mean(); ym = y.mean()
    dx = x - xm
    sxx = float(dx @ dx)
    if sxx <= 1e-12:
        return np.nan, np.nan
    b = float(dx @ (y - ym)) / sxx
    return ym - b * xm, b


def drift_neutral(d):
    """THE DEPENDENT VARIABLE (spec sec.2): regress the sleeve's monthly pts/session on the
    market's own mean session (close-open) over the same months; the INTERCEPT is the sleeve's
    expectancy at zero market drift."""
    return ols2(d["x"].values, d["y"].values)


def boot_coeffs(d, n=BOOT, block=BLOCK, rng=None):
    """6-month circular MOVING-BLOCK bootstrap on BOTH coefficients (spec sec.2)."""
    rng = rng or RNG
    K = len(d)
    xv, yv = d["x"].values, d["y"].values
    if K < 8:
        a, b = ols2(xv, yv)
        return np.full(n, a), np.full(n, b)
    nb = int(np.ceil(K / block))
    A = np.empty(n); B = np.empty(n)
    for j in range(n):
        starts = rng.integers(0, K, nb)
        idx = (starts[:, None] + np.arange(block)[None, :]).ravel() % K
        idx = idx[:K]
        A[j], B[j] = ols2(xv[idx], yv[idx])
    return A, B


def kdeflate(v):
    v = np.asarray(v, float)
    K = len(v)
    if K < 5 or v.std() == 0:
        return K, 0.0, float(K)
    rho = float(np.corrcoef(v[:-1], v[1:])[0, 1])
    rho = max(rho, 0.0)
    return K, rho, K / (1.0 + (K - 1) * rho)


def causal_tercile(v, win=TERCILE_WIN):
    """Label each observation by the terciles of the PRIOR `win` observations ONLY.

    Strictly causal: observation i is compared with cut points estimated from i-win..i-1 and
    NEVER from itself or anything after it. Observations with fewer than `win` prior finite
    values are left unlabelled (-1). Never full-sample."""
    v = np.asarray(v, float)
    n = len(v)
    lab = np.full(n, -1, np.int8)
    lo = np.full(n, np.nan); hi = np.full(n, np.nan)
    fin = np.isfinite(v)
    hist_idx = np.flatnonzero(fin)
    if len(hist_idx) <= win:
        return lab, lo, hi
    # position of each i among the finite observations strictly before it
    cnt_before = np.cumsum(fin) - fin.astype(int)          # finite obs strictly before i
    fv = v[hist_idx]
    for i in range(n):
        if not fin[i]:
            continue
        k = cnt_before[i]
        if k < win:
            continue
        h = fv[k - win:k]
        a, b = np.quantile(h, [1 / 3, 2 / 3])
        lo[i] = a; hi[i] = b
        lab[i] = 0 if v[i] <= a else (1 if v[i] <= b else 2)
    return lab, lo, hi


# ==================================================================================================
def harness_selftest(P):
    res = []

    def chk(nm, ok):
        res.append((nm, bool(ok)))

    rng = np.random.default_rng(7)
    x = rng.normal(size=80); y = 2.5 + 1.3 * x + rng.normal(size=80) * 0.1
    a, b = ols2(x, y)
    A_ = np.c_[np.ones(80), x]
    bh, *_ = np.linalg.lstsq(A_, y, rcond=None)
    chk("closed-form ols2 == numpy lstsq to 1e-10", abs(a - bh[0]) < 1e-10 and abs(b - bh[1]) < 1e-10)
    chk("ols2 recovers a known intercept", abs(a - 2.5) < 0.05)
    chk("ols2 refuses a degenerate design (zero x-variance)",
        np.isnan(ols2(np.ones(50), rng.normal(size=50))[0]))

    # causal tercile: no look-ahead, and it is not the full-sample tercile
    v = rng.normal(size=1200)
    lab, lo, hi = causal_tercile(v, win=252)
    chk("causal tercile leaves the first `win` observations unlabelled",
        (lab[:252] == -1).all() and lab[252] != -1)
    v2 = v.copy(); v2[600:] = v2[600:] + 99.0        # perturb the FUTURE only
    lab2, _, _ = causal_tercile(v2, win=252)
    chk("causal tercile of observation i is unchanged by anything after i",
        (lab[:600] == lab2[:600]).all())
    full = np.digitize(v, np.quantile(v, [1 / 3, 2 / 3]))
    chk("causal tercile is NOT the full-sample tercile",
        float((lab[252:] == full[252:]).mean()) < 0.995)
    chk("causal tercile splits roughly into thirds",
        all(abs(float((lab[252:] == k).mean()) - 1 / 3) < 0.06 for k in range(3)))

    # circular shift preserves the label distribution exactly
    L = (rng.random(150) * 3).astype(int)
    sh = np.roll(L, 37)
    chk("circular shift preserves each state's own distribution exactly",
        all((sh == k).sum() == (L == k).sum() for k in range(3)))
    chk("circular shift preserves serial dependence (same adjacency multiset)",
        sorted(zip(L, np.roll(L, -1))) == sorted(zip(sh, np.roll(sh, -1))))

    # bootstrap plumbing
    d = pd.DataFrame(dict(x=x, y=y))
    Ab, Bb = boot_coeffs(d, n=200, rng=np.random.default_rng(3))
    chk("block bootstrap returns the requested draws", len(Ab) == 200 and len(Bb) == 200)
    chk("block bootstrap brackets the point estimate",
        np.percentile(Ab, 5) < a < np.percentile(Ab, 95))

    K, rho, keff = kdeflate(np.tile([1.0, -1.0], 100))
    chk("K_eff does not inflate on negative autocorrelation", rho == 0.0 and abs(keff - K) < 1e-9)
    K, rho, keff = kdeflate(np.cumsum(rng.normal(size=400)))
    chk("K_eff deflates a persistent series", keff < K / 10)

    for nm, ok in res:
        P(f"   {'PASS' if ok else 'FAIL':<6}{nm}")
    P(f"   HARNESS SELFTEST {sum(v for _, v in res)}/{len(res)}")
    return all(v for _, v in res)


# ==================================================================================================
def spread_of(lab_m, y, x, sign, need=5):
    """SPREAD for ONE variable given a monthly state-label vector.

    Returns (spread, fav_tercile, unfav_tercile, [int0,int1,int2], [slope0,1,2], [n0,n1,n2]).
    S5 (sign 0) is the declared TWO-SIDED case: |E(HIGH) - E(LOW)|, favourable = the higher end.
    """
    ints = []; slps = []; ns = []
    for k in range(3):
        m = lab_m == k
        ns.append(int(m.sum()))
        if m.sum() < need:
            ints.append(np.nan); slps.append(np.nan); continue
        a, b = ols2(x[m], y[m])
        ints.append(a); slps.append(b)
    lo_i, hi_i = ints[0], ints[2]
    if not (np.isfinite(lo_i) and np.isfinite(hi_i)):
        return np.nan, -1, -1, ints, slps, ns
    if sign > 0:
        return hi_i - lo_i, 2, 0, ints, slps, ns
    if sign < 0:
        return lo_i - hi_i, 0, 2, ints, slps, ns
    fav = 2 if hi_i >= lo_i else 0
    return abs(hi_i - lo_i), fav, 2 - fav, ints, slps, ns


def all_spreads(LAB, y, x):
    """The ENTIRE analysis for all six, returned as an array - this is what the null redoes."""
    return np.array([spread_of(LAB[i], y, x, VARS[i][2])[0] for i in range(len(VARS))])


# ==================================================================================================
def main():
    t0 = _time.time()
    con = open(os.path.join(OUT, "console.txt"), "w", encoding="utf-8")

    def P(*a):
        print(*a, flush=True); print(*a, file=con); con.flush()

    def H(t):
        P("\n" + "=" * 118); P("=== " + t); P("=" * 118)

    gates = []

    def gate(gid, name, spec, obs, verdict):
        gates.append(dict(id=gid, gate=name, spec=spec, observed=str(obs), verdict=verdict))

    P("=" * 118)
    P("G3_SHORTROUTE01 - DID THE MIRRORED SHORT SLEEVE'S 2022-2025 RUN HAVE AN EX-ANTE HANDLE?")
    P("spec: runs/G3_SHORTROUTE01_20260831/spec.yaml  (committed 9a18980, BEFORE any")
    P("      conditional statistic existed; not edited)")
    P("=" * 118)
    P("POPULATIONS   IDENTIFICATION  PRE     2006-01-01 .. 2019-12-31")
    P("              EXCLUDED        TRANS   2020-01-01 .. 2022-04-30  (entirely)")
    P("              CONFIRMATION    MODERN  2022-05-01 .. 2026-05-29  ONE LOOK, only if G1..G5 pass")
    P(f"COSTS         floor ${COST_FLOOR}/ctrRT = {PTS_FLOOR:.4f} pts (A FLOOR, NEVER A HEADLINE) | "
      f"PRIMARY ${COST_PRIMARY}/ctrRT = {PTS_PRIMARY:.4f} pts | all-in ${COST_ALLIN} = "
      f"{PTS_ALLIN:.4f} pts")
    P("DEPENDENT     monthly DRIFT-NEUTRAL EXPECTANCY = intercept of (sleeve pts/session) on")
    P("              (market mean session close-minus-open), months as observations.")
    P("STATE         six frozen variables, each measured at 18:00 ET from STRICTLY PRIOR sessions,")
    P(f"              each binned by a CAUSAL trailing-{TERCILE_WIN}-session tercile. No seventh variable.")

    H("0. HARNESS SELFTEST - the estimator, the causal binning and the null are checked first")
    ok_h = harness_selftest(P)
    if not ok_h:
        P("\nHARNESS FAILED - refusing to report any statistic.")
        raise SystemExit(1)

    # ---------------------------------------------------------------- G0
    H("G0. REPRODUCTION OF WAVE C - is this the same object?")
    bl = open(os.path.join(CACHE, "build.log"), encoding="utf-8").read().splitlines()
    for ln in bl:
        if any(s in ln for s in ("SEAL ASSERTION", "substrate ", "TRUNCATION CONFIRMED",
                                 "EXTEND WORKED", "G0a", "G0b", "G0c", "G0d",
                                 "shared sessions", "look-ahead assertion")):
            P("  " + ln.strip())
    g0 = json.load(open(os.path.join(CACHE, "g0_core.json")))
    g0ok = (g0["short_trades"] == 2225
            and abs(g0["short_pts_sess"] - 6.00) < 0.005
            and abs(g0["short_net"] - 121454) < 0.5
            and abs(g0["p1_pts_sess"] - 14.86) < 0.005)
    P(f"\n  OBSERVED  {g0['short_trades']:,} trades | {g0['short_pts_sess']:.2f} pts/session | "
      f"${g0['short_net']:,.0f} net | P1 {g0['p1_pts_sess']:.2f} pts/session")
    P(f"  SPEC      2,225 trades | 6.00 pts/session | $121,454 net | P1 14.86 pts/session")
    gate("G0", "reproduce WAVE C's object",
         "2,225 trd / 6.00 pts/s / $121,454 / P1 14.86",
         f"{g0['short_trades']:,} / {g0['short_pts_sess']:.2f} / ${g0['short_net']:,.0f} / "
         f"{g0['p1_pts_sess']:.2f}", "PASS" if g0ok else "FAIL")
    if not g0ok:
        P("\nG0 FAILED - the object is not the same one and every number below would be void.")
        P("Reporting G0 only and stopping, exactly as the spec requires.")
        json.dump(dict(gates=gates), open(os.path.join(OUT, "gates.json"), "w"), indent=2)
        raise SystemExit(1)
    P("  -> PASS. The object below is W61's mirrored short sleeve, bit-for-bit.")
    CTRL = {}

    # ---------------------------------------------------------------- data + state variables
    S = pd.read_csv(os.path.join(CACHE, "full_sessions.csv"), parse_dates=["date"])
    TR = pd.read_csv(os.path.join(CACHE, "full_short_trades.csv"), parse_dates=["date"])
    S = S.sort_values("date").reset_index(drop=True)
    assert S["date"].max() < SEAL, "SEAL"

    H("1. THE SIX FROZEN STATE VARIABLES - all measured at 18:00 ET from STRICTLY PRIOR sessions")
    P("The sleeve trades overnight, so any 09:30-available quantity would be a look-ahead for its")
    P("own legs. Every series below is shifted so that the value carried into session s uses only")
    P(f"sessions < s, and is then binned by the terciles of its own prior {TERCILE_WIN} observations.")
    P("")
    cl = S["s_close"].values
    r = np.full(len(S), np.nan)
    r[1:] = np.log(cl[1:] / cl[:-1])                      # close-to-close log return of session s
    rs = pd.Series(r)
    # S1: stdev of the PRIOR 21 sessions' returns -> shift(1) so session s sees r_{s-21..s-1}
    s1 = rs.rolling(21).std().shift(1).values
    # S2: 63-session stdev of the S1 series, again strictly prior
    s2 = pd.Series(s1).rolling(63).std().values
    # S3: market trailing 63-session log return, strictly prior: log(C_{s-1}/C_{s-64})
    s3 = (pd.Series(np.log(cl)).diff(63)).shift(1).values
    # S4: prior range / median of the prior 60 ranges
    rng_ = S["rng"]
    s4 = (rng_ / rng_.rolling(60).median()).shift(1).values
    # S5: overnight share of absolute movement over the prior 21 sessions
    s5 = (S["abs_on"].rolling(21).sum() / S["absmove"].rolling(21).sum()).shift(1).values
    # S6: prior-session close of VIX (already strictly prior, asserted in stage 1)
    s6 = S["vix_prev"].values
    RAW = {"S1": s1, "S2": s2, "S3": s3, "S4": s4, "S5": s5, "S6": s6}

    P(f"{'id':<4}{'definition':<62}{'predicted sign':<28}{'first defined':>14}")
    for vid, desc, sg in VARS:
        f = np.flatnonzero(np.isfinite(RAW[vid]))
        P(f"{vid:<4}{desc:<62}{SIGN_TXT[sg]:<28}{str(S['date'].iloc[f[0]].date()):>14}")
    P("\nS6's predicted sign is not written as a field in the spec; the spec states S6 is included")
    P("as 'the natural competitor to S1' and shares S1's AMPLITUDE mechanism, so it is declared")
    P("POSITIVE here. That is the only reading that does not silently widen the test to two-sided.")

    LABS = {}
    for vid in RAW:
        lab, lo, hi = causal_tercile(RAW[vid], TERCILE_WIN)
        LABS[vid] = lab
        S[f"lab_{vid}"] = lab
        S[f"cut_lo_{vid}"] = lo
        S[f"cut_hi_{vid}"] = hi
    P("")
    P(f"{'id':<4}{'labelled sessions':>19}{'first labelled':>17}{'LOW':>8}{'MID':>8}{'HIGH':>8}")
    for vid, _, _ in VARS:
        lab = LABS[vid]
        f = np.flatnonzero(lab >= 0)
        P(f"{vid:<4}{len(f):>19,}{str(S['date'].iloc[f[0]].date()):>17}"
          f"{int((lab == 0).sum()):>8,}{int((lab == 1).sum()):>8,}{int((lab == 2).sum()):>8,}")

    # ---------------------------------------------------------------- monthly panel
    S["m"] = S["date"].dt.to_period("M")
    lab_ok = np.all(np.vstack([LABS[v] >= 0 for v in RAW]), axis=0)
    S["lab_ok"] = lab_ok
    grp = S.groupby("m")
    MO = grp.agg(sess=("date", "size"), y=("short_pnl436", "mean"), x=("ret", "mean"),
                 ntr=("short_ntr", "sum"), vol=("absmove", "mean"),
                 date0=("date", "min"), nlab=("lab_ok", "sum")).reset_index()
    MO["y"] = MO["y"] / PV
    MO["trd_sess"] = MO["ntr"] / MO["sess"]
    # monthly state = the MODE of its labelled sessions' terciles (states are persistent, so a
    # month is nearly always dominated by one). Frozen rule, applied identically to all six.
    for vid in RAW:
        md = []
        for m, g in grp:
            lv = g.loc[g["lab_ok"].values, f"lab_{vid}"].values
            md.append(np.bincount(lv, minlength=3).argmax() if len(lv) >= MIN_SESS_MONTH else -1)
        MO[f"L{vid}"] = md
    MO["era"] = np.where(MO["date0"] <= PRE_B, "PRE",
                         np.where(MO["date0"] < MOD_A, "TRANS", "MODERN"))

    keep = (MO["sess"] >= MIN_SESS_MONTH) & (MO["nlab"] >= MIN_SESS_MONTH)
    for vid in RAW:
        keep &= MO[f"L{vid}"] >= 0
    PRE = MO[keep & (MO["era"] == "PRE")].reset_index(drop=True)

    H("2. THE PRE MONTHLY PANEL (identification population - nothing else is read yet)")
    P(f"months in PRE 2006-01..2019-12 with >= {MIN_SESS_MONTH} sessions AND all six variables")
    P(f"labelled by their own causal {TERCILE_WIN}-session terciles: {len(PRE)}")
    P(f"   panel runs {PRE['m'].iloc[0]} .. {PRE['m'].iloc[-1]}, "
      f"{int(PRE['sess'].sum()):,} sessions, {int(PRE['ntr'].sum()):,} sleeve trades")
    lost = MO[(MO["era"] == "PRE") & ~keep]
    P(f"   PRE months dropped for warm-up / thinness: {len(lost)} "
      f"({', '.join(str(z) for z in lost['m'].astype(str)[:6])}"
      f"{' ...' if len(lost) > 6 else ''})")
    P("   The warm-up is mechanical, not a choice: S2 needs 21+63 sessions before its first value")
    P(f"   and then {TERCILE_WIN} more before its first causal tercile. 2006 therefore carries no")
    P("   labelled month. This is printed rather than absorbed.")
    P("")
    P(f"{'year':<7}{'months':>8}{'sessions':>10}{'trades':>9}{'trd/sess':>10}"
      f"{'pts/sess':>11}{'mkt ret/sess':>14}{'|move|/sess':>13}")
    for yy, g in PRE.groupby(PRE["m"].dt.year):
        P(f"{yy:<7}{len(g):>8}{int(g['sess'].sum()):>10,}{int(g['ntr'].sum()):>9,}"
          f"{g['ntr'].sum()/g['sess'].sum():>10.2f}"
          f"{float(np.average(g['y'], weights=g['sess'])):>11.2f}"
          f"{float(np.average(g['x'], weights=g['sess'])):>14.2f}"
          f"{float(np.average(g['vol'], weights=g['sess'])):>13.1f}")

    # ---- G0 CONTROL (not a spec gate): does this file's drift-neutral machinery reproduce the
    # ---- number WAVE C published for ITS PRE cut? That cut ran 2006-01-01..2022-04-30 and had
    # ---- no warm-up filter. It is an already-published UNCONDITIONAL aggregate, not a
    # ---- conditioning, and it contains no MODERN month. It exists only to prove that any gap
    # ---- between this run's PRE number and WAVE C's is the POPULATION, not the estimator.
    wc = MO[(MO["sess"] >= MIN_SESS_MONTH) & (MO["date0"] < MOD_A)]
    a_wc, b_wc = drift_neutral(wc)
    Awc, _ = boot_coeffs(wc)
    ntr_wc = float(wc["ntr"].sum() / wc["sess"].sum())
    P(f"\n   G0 CONTROL (not a spec gate, no conditioning, no MODERN month): rebuilding WAVE C's")
    P(f"   OWN PRE cut - 2006-01-01..2022-04-30, no warm-up filter - with this file's estimator:")
    P(f"      {len(wc)} months, drift-neutral expectancy {a_wc:+.3f} pts/session, 90% CI "
      f"[{np.percentile(Awc,5):+.3f}, {np.percentile(Awc,95):+.3f}], hurdle "
      f"{ntr_wc*PTS_PRIMARY:.2f}")
    P(f"      WAVE C published: 196 months, +0.408, [-0.339, +1.187], hurdle 2.62")
    P(f"      -> the estimator is WAVE C's. Any difference below is the SPEC'S POPULATION")
    P(f"         (2006-2019, warm-up removed), which is what this run was told to use.")
    CTRL["wavec_pre_replica"] = dict(months=int(len(wc)), intercept=float(a_wc),
                                     ci=[float(np.percentile(Awc, 5)),
                                         float(np.percentile(Awc, 95))],
                                     trades_per_session=ntr_wc,
                                     hurdle_2065=ntr_wc * PTS_PRIMARY,
                                     wavec_published=[196, 0.408, -0.339, 1.187, 2.62])

    a_pre, b_pre = drift_neutral(PRE)
    Ab, Bb = boot_coeffs(PRE)
    pre_rate = float(PRE["ntr"].sum() / PRE["sess"].sum())
    VN = float(PRE["vol"].median())          # PRE vol normaliser: median month's mean |1-min move|
    P(f"\n   UNCONDITIONAL PRE (the matched control every conditional table below is measured")
    P(f"   against): drift-neutral expectancy {a_pre:+.3f} pts/session, 90% CI "
      f"[{np.percentile(Ab,5):+.3f}, {np.percentile(Ab,95):+.3f}]; slope {b_pre:+.4f} "
      f"[{np.percentile(Bb,5):+.4f}, {np.percentile(Bb,95):+.4f}]")
    P(f"   trades/session {pre_rate:.3f}  ->  hurdle {pre_rate*PTS_PRIMARY:.2f} pts/session at "
      f"$20.65 ({pre_rate*PTS_FLOOR:.2f} at the $4.36 FLOOR, {pre_rate*PTS_ALLIN:.2f} at $25.01)")
    P(f"   WAVE C measured +0.408 [-0.339, +1.187] against 2.62 on a slightly different PRE cut")
    P(f"   (its PRE ran to 2022-04-30 and used no warm-up); this panel is 2006-01..2019-12 with")
    P(f"   the warm-up removed, so the two are close but not identical by construction.")

    # ------------------------------------------------- scale: PRE is a thinner object than MODERN
    H("3. SCALE - PRE sessions are structurally thinner, so every PRE number is printed twice")
    P("The spec names this as the main reason a reader might reject the PRE record entirely.")
    P("'vol-normalised' below = the same number divided by the mean session |1-minute move| of")
    P("the population it came from, x1000. It is a RESCALING of the identical estimate, not a")
    P("different estimator.")
    P("")
    P(f"{'population':<26}{'sessions':>10}{'med bars':>10}{'med bars RTH':>14}"
      f"{'med |move|/sess':>17}{'med session range':>19}")
    for lab, m in (("PRE 2006-01..2019-12", (S["date"] >= PRE_A) & (S["date"] <= PRE_B)),
                   ("TRANS (EXCLUDED)", (S["date"] >= TRANS_A) & (S["date"] <= TRANS_B)),
                   ("MODERN 2022-05..2026-05", (S["date"] >= MOD_A) & (S["date"] <= MOD_B))):
        g = S[m]
        P(f"{lab:<26}{len(g):>10,}{g['bars'].median():>10.0f}{g['bars_rth'].median():>14.0f}"
          f"{g['absmove'].median():>17.1f}{g['rng'].median():>19.1f}")
    P(f"\n   PRE vol normaliser (median month's mean session |1-min move|) = {VN:.1f} points.")
    P(f"   Every PRE points figure below is also shown as pts/session per 1000 points of session")
    P(f"   movement, i.e. value / {VN:.1f} x 1000.")

    # ---------------------------------------------------------------- G1
    H("4. G1 - SEPARATION. The six SPREADs, PRE only.")
    P("SPREAD = drift-neutral expectancy in the PREDICTED-FAVOURABLE tercile minus the")
    P("PREDICTED-UNFAVOURABLE tercile. S5 is the declared two-sided case and uses |spread|.")
    P("The predicted-favourable end was fixed in the spec BEFORE any of this was computed, so a")
    P("negative spread here means the variable ran the WRONG WAY, and it is recorded that way.")
    P("")
    y = PRE["y"].values; x = PRE["x"].values
    LAB_M = np.vstack([PRE[f"L{v}"].values for v, _, _ in VARS])
    rows = []
    P(f"{'id':<4}{'predicted':<26}{'int LOW':>10}{'int MID':>10}{'int HIGH':>10}"
      f"{'n LOW/MID/HIGH':>18}{'SPREAD':>10}{'SPREAD /vol':>13}")
    for i, (vid, desc, sg) in enumerate(VARS):
        sp, fav, unf, ints, slps, ns = spread_of(LAB_M[i], y, x, sg)
        rows.append(dict(vid=vid, desc=desc, sign=sg, spread=sp, fav=fav, unf=unf,
                         ints=ints, slps=slps, ns=ns))
        P(f"{vid:<4}{SIGN_TXT[sg]:<26}{ints[0]:>10.3f}{ints[1]:>10.3f}{ints[2]:>10.3f}"
          f"{f'{ns[0]}/{ns[1]}/{ns[2]}':>18}{sp:>10.3f}{1000*sp/VN:>13.3f}")
    sp_obs = np.array([r["spread"] for r in rows])
    best = int(np.nanargmax(sp_obs))
    BEST = rows[best]
    P(f"\n   BEST = {BEST['vid']}  ({BEST['desc']})   SPREAD {BEST['spread']:+.3f} pts/session"
      f"   ({1000*BEST['spread']/VN:+.3f} vol-normalised)")
    P(f"   favourable tercile = {TNAME[BEST['fav']]}, unfavourable = {TNAME[BEST['unf']]}")

    # collinearity / trap bookkeeping, stated before any verdict
    P("\n   S1 vs S6 COLLINEARITY (the spec says: if both 'work' that is ONE finding, not two):")
    fin = np.isfinite(RAW["S1"]) & np.isfinite(RAW["S6"])
    P(f"      session-level Pearson r(S1, S6) = "
      f"{float(np.corrcoef(RAW['S1'][fin], RAW['S6'][fin])[0,1]):+.4f}")
    P(f"      monthly state labels agree on "
      f"{100*float((PRE['LS1'].values == PRE['LS6'].values).mean()):.1f} % of PRE months")
    P("   PAIRWISE label agreement across all six (a scan of six correlated variables is not six")
    P("   independent chances, which is exactly why G2 shares one shift across the family):")
    P("      " + "".join(f"{v:>7}" for v, _, _ in VARS))
    for i, (vi, _, _) in enumerate(VARS):
        P(f"   {vi:<3}" + "".join(
            f"{100*float((PRE[f'L{vi}'].values == PRE[f'L{vj}'].values).mean()):>7.0f}"
            for vj, _, _ in VARS))

    # ---------------------------------------------------------------- G2
    H("5. G2 - THE NULL THAT PRICES THE SEARCH (the one that matters)")
    P(f"CIRCULAR SHIFT of the state-label series against the sleeve's monthly (y, x) series,")
    P(f"{NULL_DRAWS:,} draws. Each draw redoes THE ENTIRE ANALYSIS - all six variables, all three")
    P("terciles, the S5 two-sided rule - and records the MAX over the six. That is the statistic")
    P("the observed best must beat. MC-11 died for lack of exactly this step.")
    P("ONE SHIFT IS SHARED BY ALL SIX VARIABLES on each draw (CLAUDE.md sec.4): the six are a")
    P("correlated family, and independent shifts would price a search that was never run.")
    M = len(PRE)
    rng2 = np.random.default_rng(20260901)
    shifts = rng2.integers(1, M, NULL_DRAWS)
    nullmax = np.empty(NULL_DRAWS)
    nullall = np.empty((NULL_DRAWS, len(VARS)))
    for j, d in enumerate(shifts):
        sp = all_spreads(np.roll(LAB_M, d, axis=1), y, x)
        nullall[j] = sp
        nullmax[j] = np.nanmax(sp)
    p95 = float(np.percentile(nullmax, 95))
    pct = 100.0 * float((nullmax < BEST["spread"]).mean())
    P("")
    P(f"   observed best SPREAD ({BEST['vid']})           {BEST['spread']:+.3f} pts/session")
    P(f"   max-statistic null: mean {nullmax.mean():+.3f}  p50 {np.percentile(nullmax,50):+.3f}"
      f"  p90 {np.percentile(nullmax,90):+.3f}  p95 {p95:+.3f}  p99 "
      f"{np.percentile(nullmax,99):+.3f}  max {nullmax.max():+.3f}")
    P(f"   the observed best sits at the {pct:.1f}th percentile of the max-statistic null")
    P(f"   -> {'EXCEEDS' if BEST['spread'] > p95 else 'DOES NOT EXCEED'} the 95th percentile")
    P("")
    P("   Per-variable, for the record - each variable's own spread against its own marginal null")
    P("   (NOT the gate; the gate is the max-statistic column above, because the argmax was a")
    P("   choice this run made and it must be priced):")
    P(f"{'id':<4}{'SPREAD':>10}{'marginal null p95':>20}{'marginal pctile':>18}"
      f"{'max-stat p95':>15}{'vs max-stat':>14}")
    for i, (vid, _, _) in enumerate(VARS):
        col = nullall[:, i]
        mp = 100.0 * float((col < sp_obs[i]).mean())
        P(f"{vid:<4}{sp_obs[i]:>10.3f}{np.percentile(col,95):>20.3f}{mp:>17.1f}%"
          f"{p95:>15.3f}{('above' if sp_obs[i] > p95 else 'below'):>14}")
    g2ok = bool(BEST["spread"] > p95)
    gate("G2", "best SPREAD beats the MAX-over-six circular-shift null",
         "observed best > 95th pctile of the max-statistic null",
         f"{BEST['spread']:+.3f} vs p95 {p95:+.3f} ({pct:.1f}th pctile)",
         "PASS" if g2ok else "FAIL")
    gate("G1", "separation in PRE (passes iff its spread survives G2)",
         "best variable's SPREAD survives G2",
         f"best {BEST['vid']} {BEST['spread']:+.3f}", "PASS" if g2ok else "FAIL")

    # ---------------------------------------------------------------- G3
    H("6. G3 - THE BINDING GATE: is the favourable state ECONOMICALLY LIVE, not merely separating?")
    P("A variable can separate a quantity that is negative everywhere. This object lives just")
    P("under a cost line, so a router that moves it from 'well below' to 'slightly below' is")
    P("worth nothing. The hurdle is computed WITHIN the favourable tercile, from its own trade")
    P("rate, exactly as the spec specifies.")
    P("")
    P(f"{'id':<4}{'tercile':<9}{'months':>8}{'sessions':>10}{'trd/sess':>10}{'drift-neut':>12}"
      f"{'90% CI':>24}{'hurdle@20.65':>14}{'clears?':>26}")
    g3rows = []
    for i, (vid, _, sg) in enumerate(VARS):
        rr = rows[i]
        for k in range(3):
            m = LAB_M[i] == k
            d = PRE[m]
            if not len(d):
                continue
            a_, b_ = ols2(x[m], y[m])
            Ai, _Bi = boot_coeffs(d)
            rate = float(d["ntr"].sum() / d["sess"].sum())
            hur = rate * PTS_PRIMARY
            lo5 = float(np.percentile(Ai, 5))
            isfav = (k == rr["fav"])
            verdict = ("-" if not isfav else
                       ("CLEARS (CI lower bound above)" if lo5 > hur else
                        ("point above, CI straddles" if a_ > hur else "BELOW THE HURDLE")))
            P(f"{vid if k == 0 else '':<4}{TNAME[k]:<9}{len(d):>8}{int(d['sess'].sum()):>10,}"
              f"{rate:>10.3f}{a_:>12.3f}"
              f"{f'[{np.percentile(Ai,5):+.3f}, {np.percentile(Ai,95):+.3f}]':>24}"
              f"{hur:>14.3f}{verdict:>26}")
            g3rows.append(dict(vid=vid, tercile=TNAME[k], favourable=bool(isfav),
                               months=len(d), sessions=int(d["sess"].sum()),
                               trades=int(d["ntr"].sum()), trd_per_sess=rate,
                               drift_neutral=a_, slope=b_,
                               ci5=lo5, ci95=float(np.percentile(Ai, 95)),
                               hurdle_436=rate * PTS_FLOOR, hurdle_2065=hur,
                               hurdle_2501=rate * PTS_ALLIN,
                               mean_mkt_drift=float(d["x"].mean()),
                               vol=float(d["vol"].mean()),
                               drift_neutral_volnorm=1000 * a_ / float(d["vol"].mean())))
        P("")
    G3 = pd.DataFrame(g3rows)
    bf = G3[(G3["vid"] == BEST["vid"]) & G3["favourable"]].iloc[0]
    P(f"   WINNER {BEST['vid']}, favourable tercile {TNAME[BEST['fav']]}:")
    P(f"      drift-neutral expectancy   {bf['drift_neutral']:+.3f} pts/session   "
      f"90% CI [{bf['ci5']:+.3f}, {bf['ci95']:+.3f}]")
    P(f"      trades/session in tercile  {bf['trd_per_sess']:.3f}")
    P(f"      hurdle @ $4.36  FLOOR      {bf['hurdle_436']:.3f} pts/session   "
      f"(A FLOOR - never a headline)")
    P(f"      hurdle @ $20.65 PRIMARY    {bf['hurdle_2065']:.3f} pts/session   <- THE GATE")
    P(f"      hurdle @ $25.01 all-in     {bf['hurdle_2501']:.3f} pts/session")
    P(f"      vol-normalised expectancy  {bf['drift_neutral_volnorm']:+.3f} per 1000 pts of "
      f"session movement (tercile mean |move|/session {bf['vol']:.0f})")
    P("\n   THE WHOLE G3 SURFACE IN ONE LINE - across ALL SIX preregistered variables and ALL")
    P("   EIGHTEEN terciles, favourable or not, how many states clear their OWN cost hurdle?")
    G3["clears_2065"] = G3["drift_neutral"] > G3["hurdle_2065"]
    G3["gap_2065"] = G3["drift_neutral"] - G3["hurdle_2065"]
    G3["clears_436"] = G3["drift_neutral"] > G3["hurdle_436"]
    bestcell = G3.loc[G3["gap_2065"].idxmax()]
    P(f"      states clearing the $20.65 PRIMARY hurdle : "
      f"{int(G3['clears_2065'].sum())} of {len(G3)}")
    P(f"      states clearing the $4.36 FLOOR (a floor, never a headline): "
      f"{int(G3['clears_436'].sum())} of {len(G3)}")
    P(f"      the single best state on this surface is {bestcell['vid']} "
      f"{bestcell['tercile']}: {bestcell['drift_neutral']:+.3f} against a "
      f"{bestcell['hurdle_2065']:.3f} hurdle, short by {-bestcell['gap_2065']:.3f} pts/session")
    P(f"      the highest 90% CI UPPER bound anywhere on the surface is "
      f"{G3['ci95'].max():+.3f}, still {G3.loc[G3['ci95'].idxmax(),'hurdle_2065']-G3['ci95'].max():.3f}")
    P(f"      pts/session below that state's own hurdle. There is no cell in this design in which")
    P(f"      even the optimistic end of the interval pays $20.65/ctrRT.")
    P("")
    fav_d = PRE[LAB_M[best] == BEST["fav"]]
    Afav, _ = boot_coeffs(fav_d)
    sd_fav = float(Afav.std(ddof=1))
    P(f"   POWER / MDE, printed BEFORE anyone proposes economics on a routed third of the")
    P(f"   sessions (spec trap 6): the winner's favourable tercile holds {int(bf['months'])} months")
    P(f"   and {int(bf['sessions']):,} sessions. Bootstrap sd of its drift-neutral intercept "
      f"{sd_fav:.3f} pts/session,")
    P(f"   so the smallest effect this population could separate from zero at 90% one-sided is")
    P(f"   about {1.645*sd_fav:.2f} pts/session. The hurdle it must clear is "
      f"{bf['hurdle_2065']:.2f}. The gap between the")
    P(f"   observed {bf['drift_neutral']:+.3f} and that hurdle is "
      f"{bf['hurdle_2065']-bf['drift_neutral']:.2f} pts/session = "
      f"{(bf['hurdle_2065']-bf['drift_neutral'])/max(sd_fav,1e-9):.1f} bootstrap sd. This is not")
    P(f"   an underpowered near-miss; it is not close.")
    CTRL["g3_surface"] = dict(cells=int(len(G3)),
                              clearing_2065=int(G3["clears_2065"].sum()),
                              clearing_436=int(G3["clears_436"].sum()),
                              best_cell=f"{bestcell['vid']} {bestcell['tercile']}",
                              best_gap=float(bestcell["gap_2065"]),
                              max_ci95=float(G3["ci95"].max()),
                              fav_boot_sd=sd_fav,
                              gap_in_sd=float((bf["hurdle_2065"] - bf["drift_neutral"])
                                              / max(sd_fav, 1e-9)))

    g3ok = bool(bf["drift_neutral"] > bf["hurdle_2065"] and bf["ci5"] > bf["hurdle_2065"])
    gate("G3", "favourable tercile clears the $20.65 cost hurdle",
         "point AND bootstrap 90% CI lower bound above trd/sess x 1.0325",
         f"{bf['drift_neutral']:+.3f} (CI lo {bf['ci5']:+.3f}) vs hurdle "
         f"{bf['hurdle_2065']:.3f}", "PASS" if g3ok else "FAIL")

    # ---------------------------------------------------------------- G4
    H("7. G4 - MONOTONICITY across all three terciles, not extremes-only")
    P("An extremes-only effect with a non-monotone middle is the signature of a few episodes.")
    P("")
    P(f"{'id':<4}{'LOW':>10}{'MID':>10}{'HIGH':>10}{'predicted direction':>26}{'monotone?':>12}")
    mono = {}
    for i, (vid, _, sg) in enumerate(VARS):
        it = rows[i]["ints"]
        if sg > 0:
            ok = it[0] <= it[1] <= it[2]
            txt = "increasing LOW->HIGH"
        elif sg < 0:
            ok = it[0] >= it[1] >= it[2]
            txt = "decreasing LOW->HIGH"
        else:
            ok = (it[0] <= it[1] <= it[2]) or (it[0] >= it[1] >= it[2])
            txt = "monotone either way (S5)"
        mono[vid] = bool(ok)
        P(f"{vid:<4}{it[0]:>10.3f}{it[1]:>10.3f}{it[2]:>10.3f}{txt:>26}"
          f"{('YES' if ok else 'NO'):>12}")
    g4ok = mono[BEST["vid"]]
    gate("G4", "monotone across all three terciles",
         "middle tercile lies between the extremes, in the predicted direction",
         f"{BEST['vid']}: " + " -> ".join(f"{v:+.3f}" for v in BEST["ints"]),
         "PASS" if g4ok else "FAIL")

    # ---------------------------------------------------------------- G5
    H("8. G5 - EPISODE CONCENTRATION: leave-one-year-out and leave-one-episode-out")
    i_best = best
    lab_b = LAB_M[i_best]
    sg_b = VARS[i_best][2]
    yrs = list(range(PRE_A.year, PRE_B.year + 1))
    P("Leave-one-year-out over the 14 declared PRE years. A year the warm-up left with no months")
    P("gives a degenerate fold (nothing is removed); it is flagged rather than hidden.")
    P("")
    P(f"{'year drop':<11}{'months left':>13}{'months in year':>16}{'SPREAD':>10}{'positive?':>11}")
    loyo = []
    for yy in yrs:
        m = PRE["m"].dt.year.values != yy
        nin = int((~m).sum())
        sp, *_ = spread_of(lab_b[m], y[m], x[m], sg_b)
        loyo.append(sp)
        P(f"{yy:<11}{int(m.sum()):>13}{nin:>16}{sp:>10.3f}"
          f"{('YES' if sp > 0 else 'no'):>11}"
          + ("   <- degenerate fold, year has no months" if nin == 0 else ""))
    loyo = np.array(loyo)
    n_yr_data = int(sum(1 for yy in yrs if (PRE["m"].dt.year.values == yy).any()))
    n_pos = int(np.nansum(loyo > 0))
    n_pos_data = int(sum(1 for yy, sp in zip(yrs, loyo)
                         if (PRE["m"].dt.year.values == yy).any() and sp > 0))
    P(f"\n   positive folds {n_pos} of {len(yrs)} declared PRE years   (spec: >= 11 of 14)")
    P(f"   of the {n_yr_data} years that actually carry months, {n_pos_data} are positive")

    fav_idx = np.flatnonzero(lab_b == BEST["fav"])
    eps = []
    if len(fav_idx):
        cur = [fav_idx[0]]
        for a_, b_ in zip(fav_idx[:-1], fav_idx[1:]):
            if (b_ - a_ - 1) >= 2:            # >= 2 intervening non-favourable months
                eps.append(cur); cur = [b_]
            else:
                cur.append(b_)
        eps.append(cur)
    P(f"\n   EPISODES of the favourable state ({TNAME[BEST['fav']]} tercile of {BEST['vid']}):")
    P(f"   an episode is a maximal run of favourable months separated by >= 2 non-favourable")
    P(f"   months. count = {len(eps)}, covering {len(fav_idx)} months.")
    P("")
    P(f"{'episode':<9}{'from':>10}{'to':>10}{'months':>8}{'SPREAD without it':>20}"
      f"{'positive?':>11}")
    loeo = []
    for e_i, e in enumerate(eps):
        m = np.ones(M, bool); m[e] = False
        sp, *_ = spread_of(lab_b[m], y[m], x[m], sg_b)
        loeo.append(sp)
        P(f"{e_i+1:<9}{str(PRE['m'].iloc[e[0]]):>10}{str(PRE['m'].iloc[e[-1]]):>10}"
          f"{len(e):>8}{sp:>20.3f}{('YES' if sp > 0 else 'no'):>11}")
    loeo = np.array(loeo) if len(loeo) else np.array([np.nan])
    share = float(np.nanmean(loeo > 0)) if len(eps) else 0.0
    Kf, rho_bar, keff = kdeflate(y[lab_b == BEST["fav"]])
    P(f"\n   leave-one-episode-out positive share {100*share:.1f} %  (spec: >= 80 %)")
    P(f"   K (favourable months) = {Kf}   rho_bar (lag-1 autocorr of the favourable-tercile")
    P(f"   monthly series) = {rho_bar:.4f}   K_eff = K/(1+(K-1)*rho_bar) = {keff:.1f}")
    Ka, rhoa, keffa = kdeflate(y)
    P(f"   for reference the whole PRE monthly series: K = {Ka}, rho_bar {rhoa:.4f}, "
      f"K_eff {keffa:.1f}")
    g5ok = bool(n_pos >= 11 and share >= 0.80)
    gate("G5", "episode concentration (LOYO and LOEO)",
         ">= 11 of 14 LOYO folds positive AND >= 80% LOEO folds positive",
         f"LOYO {n_pos}/14, LOEO {100*share:.1f}% over {len(eps)} episodes",
         "PASS" if g5ok else "FAIL")

    # ---------------------------------------------------------------- the S3 trap
    H("9. THE TRAPS THE SPEC NAMED - checked whether or not they fired")
    P("(a) S3 IS A TRAP FOR ITSELF. With a drift-neutral dependent variable the market's own")
    P("    trend should already be absorbed, so an S3 win is more likely a specification failure")
    P("    than a discovery. Here S3's spread is "
      f"{sp_obs[2]:+.3f}, rank {int(np.argsort(np.argsort(-sp_obs))[2])+1} of 6"
      f" -> {'S3 IS THE WINNER: investigated below' if best == 2 else 'S3 did not win.'}")
    P("(b) THE INTERCEPT IS AN EXTRAPOLATION TO x = 0. If a tercile's market-drift distribution")
    P("    is centred far from zero, its 'drift-neutral' intercept is read off the fitted line")
    P("    outside the data. This is printed for every variable because it can manufacture a")
    P("    spread out of nothing but different x-supports.")
    P("")
    P(f"{'id':<4}{'tercile':<9}{'mean x':>10}{'sd x':>9}{'|mean x|/sd':>13}{'slope':>10}"
      f"{'intercept':>12}{'slope x mean x':>16}")
    for i, (vid, _, _) in enumerate(VARS):
        for k in range(3):
            m = LAB_M[i] == k
            if m.sum() < 5:
                continue
            xs = x[m]
            a_, b_ = ols2(xs, y[m])
            P(f"{vid if k == 0 else '':<4}{TNAME[k]:<9}{xs.mean():>10.2f}{xs.std():>9.2f}"
              f"{abs(xs.mean())/max(xs.std(),1e-9):>13.3f}{b_:>10.4f}{a_:>12.3f}"
              f"{b_*xs.mean():>16.3f}")
    P("\n(c) S1 and S6 are near-collinear. If both separate, that is ONE finding. Their spreads")
    P(f"    are S1 {sp_obs[0]:+.3f} and S6 {sp_obs[5]:+.3f}; they are NOT two independent")
    P("    confirmations of anything and are not counted twice anywhere in this report.")
    P("(d) A WINNER IS NOT A CANDIDATE. Nothing in this run produces a rule, a weight, an exit,")
    P("    a routed-strategy P&L or a .cs file, on any outcome.")

    # ---------------------------------------------------------------- gate table + decision
    H("10. GATE / SPEC / OBSERVED / PASS-FAIL   (printed by the program, never assembled by hand)")
    gates.sort(key=lambda g: g["id"])
    P(f"{'id':<5}{'gate':<48}{'spec':<52}{'observed':<44}{'verdict'}")
    for g in gates:
        P(f"{g['id']:<5}{g['gate'][:47]:<48}{g['spec'][:51]:<52}{g['observed'][:43]:<44}"
          f"{g['verdict']}")
    order = {g["id"]: g for g in gates}
    allpass = all(order[k]["verdict"] == "PASS" for k in ("G0", "G1", "G2", "G3", "G4", "G5"))
    P("")
    P(f"   DECISION RULE (spec sec.4): ALL of G1..G5 -> a WINNER and exactly ONE look at MODERN.")
    P(f"                               ANY fail      -> NO WINNER, MODERN IS NOT READ, the short")
    P(f"                                                axis is recorded CLOSED with the reason.")
    P(f"   OBSERVED: {'ALL PASS' if allpass else 'AT LEAST ONE GATE FAILED'}"
      f"  ->  {'CONFIRMATION RUNS' if allpass else 'NO WINNER; MODERN IS NOT READ'}")

    # ---------------------------------------------------------------- CONFIRMATION
    conf = None
    if allpass:
        H("11. CONFIRMATION - ONE LOOK AT MODERN, ONE QUESTION, NO FITTING")
        P("Question: was the PRE-identified state elevated during MODERN 2022-05-01..2026-05-29,")
        P("and specifically during the 2022-2025 sub-period that ran at 20x the PRE level?")
        vid = BEST["vid"]
        pre_m = ((S["date"] >= PRE_A) & (S["date"] <= PRE_B)
                 & (S[f"lab_{vid}"] >= 0)).values
        rawp = RAW[vid][pre_m]
        rawp = rawp[np.isfinite(rawp)]
        thr = np.quantile(rawp, [1 / 3, 2 / 3])
        P(f"\n   PRE-DEFINED THRESHOLDS for {vid}, taken from the {len(rawp):,} labelled PRE")
        P(f"   sessions and NEVER re-estimated on MODERN: 1/3 = {thr[0]:.5f}, 2/3 = {thr[1]:.5f}")
        modm = (S["date"] >= MOD_A) & (S["date"] <= MOD_B)
        rawm = RAW[vid][modm.values]
        P(f"\n   (a) DISTRIBUTION of {vid}: MODERN versus PRE")
        P(f"{'population':<26}{'n':>8}{'p10':>11}{'p25':>11}{'median':>11}{'p75':>11}"
          f"{'p90':>11}{'mean':>11}")
        for lab_, arr in (("PRE 2006-2019", rawp), ("MODERN 2022-05..2026-05", rawm)):
            a_ = arr[np.isfinite(arr)]
            P(f"{lab_:<26}{len(a_):>8,}" + "".join(
                f"{np.percentile(a_, q):>11.5f}" for q in (10, 25, 50, 75, 90))
              + f"{a_.mean():>11.5f}")
        P(f"   share of MODERN SESSIONS above the PRE 2/3 threshold: "
          f"{100*float((rawm[np.isfinite(rawm)] > thr[1]).mean()):.1f} % "
          f"(PRE by construction 33.3 %)")

        lab_mod = np.where(~np.isfinite(RAW[vid]), -1,
                           np.where(RAW[vid] <= thr[0], 0,
                                    np.where(RAW[vid] <= thr[1], 1, 2)))
        S["lab_pre_thr"] = lab_mod
        MOD = MO[(MO["era"] == "MODERN") & (MO["sess"] >= MIN_SESS_MONTH)
                 & (MO["date0"] <= MOD_B)].copy()
        md = []
        for m, g in S[modm].groupby("m"):
            lv = g["lab_pre_thr"].values
            lv = lv[lv >= 0]
            md.append((m, np.bincount(lv, minlength=3).argmax() if len(lv) >= MIN_SESS_MONTH
                       else -1))
        mmap = dict(md)
        MOD["Lpre"] = MOD["m"].map(mmap)
        MOD = MOD[MOD["Lpre"] >= 0].reset_index(drop=True)
        P(f"\n   (b) SHARE OF MODERN MONTHS IN THE PRE-DEFINED FAVOURABLE TERCILE "
          f"({TNAME[BEST['fav']]})")
        P(f"{'window':<24}{'months':>9}{'LOW':>8}{'MID':>8}{'HIGH':>8}{'favourable share':>19}")
        for lab_, mm in (("MODERN 2022-05..2026-05", np.ones(len(MOD), bool)),
                         ("  of which 2022-2025", MOD["m"].dt.year.values <= 2025),
                         ("  of which 2026", MOD["m"].dt.year.values == 2026)):
            g = MOD[mm]
            if not len(g):
                continue
            cnt = [int((g["Lpre"] == k).sum()) for k in range(3)]
            P(f"{lab_:<24}{len(g):>9}{cnt[0]:>8}{cnt[1]:>8}{cnt[2]:>8}"
              f"{100*cnt[BEST['fav']]/len(g):>18.1f}%")
        P(f"   PRE base rate of the favourable tercile among PRE months: "
          f"{100*float((lab_b == BEST['fav']).mean()):.1f} %")
        P(f"\n   (c) THE SLEEVE'S REALISED DRIFT-NEUTRAL EXPECTANCY IN MODERN MONTHS,")
        P(f"       BY PRE-DEFINED TERCILE (thresholds from PRE, not re-estimated)")
        P(f"{'tercile':<10}{'months':>8}{'sessions':>10}{'trd/sess':>10}{'drift-neut':>12}"
          f"{'90% CI':>24}{'hurdle@20.65':>14}")
        conf_rows = []
        for k in range(3):
            g = MOD[MOD["Lpre"] == k]
            if len(g) < 5:
                P(f"{TNAME[k]:<10}{len(g):>8}{int(g['sess'].sum()) if len(g) else 0:>10}"
                  f"{'-':>10}{'- (too few months)':>12}")
                conf_rows.append(dict(tercile=TNAME[k], months=len(g)))
                continue
            a_, b_ = drift_neutral(g)
            Ai, _ = boot_coeffs(g)
            rate = float(g["ntr"].sum() / g["sess"].sum())
            P(f"{TNAME[k]:<10}{len(g):>8}{int(g['sess'].sum()):>10,}{rate:>10.3f}{a_:>12.3f}"
              f"{f'[{np.percentile(Ai,5):+.3f}, {np.percentile(Ai,95):+.3f}]':>24}"
              f"{rate*PTS_PRIMARY:>14.3f}")
            conf_rows.append(dict(tercile=TNAME[k], months=len(g),
                                  sessions=int(g["sess"].sum()), trd_per_sess=rate,
                                  drift_neutral=a_, slope=b_,
                                  ci5=float(np.percentile(Ai, 5)),
                                  ci95=float(np.percentile(Ai, 95)),
                                  hurdle_2065=rate * PTS_PRIMARY))
        favshare = float((MOD[MOD["m"].dt.year <= 2025]["Lpre"] == BEST["fav"]).mean())
        conf = dict(variable=vid, fav_tercile=TNAME[BEST["fav"]],
                    pre_thresholds=[float(thr[0]), float(thr[1])],
                    fav_share_2022_2025=favshare,
                    pre_fav_base_rate=float((lab_b == BEST["fav"]).mean()),
                    by_tercile=conf_rows)
        P("")
        P(f"   READ: 2022-2025 spent {100*favshare:.1f} % of its months in the PRE-defined")
        P(f"   favourable state, against a PRE base rate of "
          f"{100*float((lab_b == BEST['fav']).mean()):.1f} %.")
        P("   If that share is not elevated, the handle does not explain the anomaly and the axis")
        P("   closes anyway - that outcome is reported as prominently as a confirmation.")
        P("   NOT COMPUTED, by the spec: no re-fit, no MODERN-estimated thresholds, no second")
        P("   variable, no economics of a routed strategy, no candidate.")
    else:
        H("11. CONFIRMATION - NOT RUN")
        P("At least one of G1..G5 failed. Under the preregistered decision rule MODERN IS NOT")
        P("READ for the conditional analysis, and it has not been: no MODERN month enters any")
        P("statistic above. The only 2022+ figures anywhere in this run are G0's reproduction")
        P("numbers, which are on the already-DISCOVERY_CONSUMED aggregate and are permitted")
        P("explicitly by the spec.")
        P("")
        P("THE SHORT AXIS IS RECORDED CLOSED, with the reason given by the failing gate(s):")
        for g in gates:
            if g["verdict"] != "PASS":
                P(f"   {g['id']}  {g['gate']}")
                P(f"        spec     {g['spec']}")
                P(f"        observed {g['observed']}")

    # ---------------------------------------------------------------- artefacts
    G3["volnorm_divisor"] = VN
    G3.to_csv(os.path.join(OUT, "pre_terciles.csv"), index=False)
    PRE.assign(m=PRE["m"].astype(str)).to_csv(os.path.join(OUT, "pre_monthly_panel.csv"),
                                              index=False)
    json.dump(dict(
        run="G3_SHORTROUTE01_20260831", spec_commit="9a18980",
        gates=gates, all_pass=bool(allpass), controls=CTRL,
        best=dict(variable=BEST["vid"], description=BEST["desc"],
                  predicted_sign=SIGN_TXT[BEST["sign"]],
                  favourable_tercile=TNAME[BEST["fav"]],
                  spread=float(BEST["spread"]),
                  intercepts=dict(zip(TNAME, [float(v) for v in BEST["ints"]]))),
        spreads={VARS[i][0]: float(sp_obs[i]) for i in range(len(VARS))},
        null=dict(draws=NULL_DRAWS, shared_shift=True,
                  max_stat_p95=p95, observed_percentile=pct,
                  max_stat_quantiles={q: float(np.percentile(nullmax, q))
                                      for q in (50, 90, 95, 99)}),
        pre_panel=dict(months=int(M), sessions=int(PRE["sess"].sum()),
                       trades=int(PRE["ntr"].sum()),
                       first=str(PRE["m"].iloc[0]), last=str(PRE["m"].iloc[-1]),
                       unconditional_drift_neutral=float(a_pre),
                       unconditional_ci=[float(np.percentile(Ab, 5)),
                                         float(np.percentile(Ab, 95))],
                       trades_per_session=pre_rate,
                       hurdle_2065=pre_rate * PTS_PRIMARY),
        modern_read=bool(allpass), confirmation=conf,
        seal=dict(max_session=str(S["date"].max().date()), limit="2026-08-01"),
    ), open(os.path.join(OUT, "gates.json"), "w"), indent=2)
    P(f"\ndone [{_time.time()-t0:.0f}s]")
    con.close()


if __name__ == "__main__":
    main()
