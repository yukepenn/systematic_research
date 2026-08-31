"""G3_P1GAP01 - LOCKED (Mode B) challenge. Executes runs/G3_P1GAP01_20260831/spec.yaml verbatim.

TWO ARMS ONLY.  A0_INCUMBENT (the executable object's own qty vector) and A1_OPENSTRENGTH
(P1SZ_OPENLOC).  No grid, no variants, no second feature.

The population is the EXECUTABLE object's NT8 closed-trade ledger.  The Python research chain is
NOT used to generate trades - G3_EXECTRUTH_01 established it is object-divergent (double-lagged
ATR) and this run must not inherit that defect.  The incumbent's causal quality score is already
embedded in the ledger's `qty` column; that IS A0's size vector and it is not recomputed.

Evaluator: research_sdk/champion_eval.py (imported, never modified).

NO order, NO deploy, NO CrossTrade, NO read of any session >= 2026-08-01 in the arm window.
"""
from __future__ import annotations

import json
import os
import sys
import math

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, ROOT)

from research_sdk import champion_eval as CE  # noqa: E402

RUN = os.path.join(ROOT, "runs", "G3_P1GAP01_20260831")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

NT8_TRADES = os.path.join(ROOT, "runs", "G2_AUG_INCUMBENT_READ_20260830", "out",
                          "p1_trades_full.csv")
BASELINES = os.path.join(ROOT, "runs", "G2_AUG_INCUMBENT_READ_20260830", "out",
                         "leg_baselines.json")
SESSTRUCT = os.path.join(ROOT, "runs", "G3_SESSTRUCT_00_20260831", "out",
                         "session_structure.parquet")

FEATURE = "open_loc_in_on_range"
COMM_RT = 4.36
FIXED_DD = 20245.0          # champion_eval's target_dd default; the repo-standard risk budget
WIN, MINHIST = 250, 100     # inherited from the incumbent. NOT free parameters of this arm.
MIN_FINITE_HIST = 20        # identical guard to T2_P1SIZE01's causal_threshold_arm
WINDOW_LO = pd.Timestamp("2022-01-02")
WINDOW_HI_SESSION = pd.Timestamp("2026-07-31")   # SEAL: nothing at or after 2026-08-01
COST_LINES = (0.0, 14.44, 20.65)
N_NULL = 1000
N_BOOT = 10000
MEAN_BLOCK = 4.0

_fh = None


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    if _fh:
        _fh.write(s + "\n")
        _fh.flush()


def hr(c="="):
    P(c * 112)


# ==================================================================================================
# primitives (thin wrappers on champion_eval so the algebra is the shared one, not a private copy)
# ==================================================================================================

def weekly_of(dates, pnl, all_weeks):
    _, w = CE.weekly_from_trades(dates, pnl, all_weeks)
    return w


def fixdd(dates, pnl, all_weeks):
    return CE.fixed_dd_income(weekly_of(dates, pnl, all_weeks), FIXED_DD)


def _sorted_quantile(a_sorted, q):
    """numpy's default 'linear' quantile on an ALREADY SORTED finite array."""
    n = len(a_sorted)
    if n == 0:
        return float("nan")
    pos = q * (n - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, n - 1)
    fr = pos - lo
    return float(a_sorted[lo] * (1.0 - fr) + a_sorted[hi] * fr)


# ==================================================================================================
# THE ARM.  One function, used for the real feature AND for every G4b circular shift.
# ==================================================================================================

def a1_sizes(feat_elig, inc_size_elig):
    """A1_OPENSTRENGTH size vector over the ELIGIBLE (post-09:30) subsequence.

    Spec section 3, verbatim:
        s = 2 when open_loc_in_on_range >= tau_i, ELSE THE INCUMBENT SIZE.
        tau_i = the causal (1 - r_i) quantile of open_loc over the PREVIOUS 250 post-09:30
        entries, r_i = the incumbent's own realised size-2 rate over those same 250 entries.
        min-history 100.
    "else the incumbent size" is a UNION, not a replacement: the arm never reduces a size below
    the incumbent's (spec section 3 what_it_does_NOT_do).  Whether that union keeps the contract
    budget matched is exactly what G1 tests; it is not assumed here.

    Undefined feature (degenerate overnight range / unjoined session) -> INCUMBENT size, counted,
    never dropped.
    """
    M = len(feat_elig)
    s = np.array(inc_size_elig, dtype=np.int64, copy=True)
    inc2 = (np.asarray(inc_size_elig) == 2).astype(float)
    taus = np.full(M, np.nan)
    rs = np.full(M, np.nan)
    n_short_hist = 0
    for j in range(M):
        if j < MINHIST:
            continue
        if not np.isfinite(feat_elig[j]):
            continue
        lo = max(0, j - WIN)
        r = float(inc2[lo:j].mean())
        rs[j] = r
        if not np.isfinite(r) or r <= 0.0:
            continue
        h = feat_elig[lo:j]
        h = h[np.isfinite(h)]
        if len(h) < MIN_FINITE_HIST:
            n_short_hist += 1
            continue
        tau = _sorted_quantile(np.sort(h), 1.0 - r)
        taus[j] = tau
        if feat_elig[j] >= tau:
            s[j] = 2
    return s, taus, rs, n_short_hist


# ==================================================================================================
def main():
    global _fh
    _fh = open(os.path.join(OUT, "console.txt"), "w", encoding="utf-8")
    hr()
    P("G3_P1GAP01 - LOCKED (Mode B) CHALLENGE.  spec.yaml committed BEFORE any arm P&L existed.")
    P("Frozen feature: open_loc_in_on_range.  Two arms only.  No grid, no variants.")
    P("LIVE ENABLED = NO.  $0 spent.  No order / deploy / backtest / CrossTrade call.")
    hr()
    P("")
    P("BASE RATE, STATED BEFORE THE RESULT (spec section 6, trap 3):")
    P("  T2_P1SIZE01 ran TWO size maps through THIS SAME causal budget calibrator and both FAILED")
    P("  on G2 and G5.  This class of arm is 0 for 2 in this repository.  If A1 passes, the")
    P("  correct response is disbelief until G4b (the feature null that prices the 11-candidate")
    P("  scan) and G5 (stability) are read - and this report leads with those two.")
    P("")
    P("CEILING, STATED BEFORE THE RESULT (spec section 6, trap 4):")
    P("  Only the post-09:30 entries are eligible.  A layer that cannot touch the majority of the")
    P("  book CANNOT produce a large book-level effect.  A LARGE effect is evidence of a BUG.")

    # ============================================================== load the executable object
    hr()
    P("G0  VERIFICATION - if any clause fails the arms are VOID")
    hr()
    nt = pd.read_csv(NT8_TRADES, parse_dates=["et", "xt"])
    ref = json.load(open(BASELINES))["P1"]
    net_all = float(nt["pnl"].sum())
    g0a = (len(nt) == ref["trades"]) and (abs(net_all - ref["net"]) < 0.005)
    P(f"G0a  ledger rows {len(nt)} (spec 2439) ; net ${net_all:,.2f} vs recorded "
      f"${ref['net']:,.2f} ; |d| = ${abs(net_all-ref['net']):.6f}  -> {'PASS' if g0a else 'FAIL'}")

    per_all = nt["pnl"].to_numpy(float) / nt["qty"].to_numpy(float)
    id1 = float(np.max(np.abs(nt["pnl"].to_numpy(float) - nt["qty"].to_numpy(float) * per_all)))
    id2 = float(np.max(np.abs(nt["comm"].to_numpy(float) - COMM_RT * nt["qty"].to_numpy(float))))
    g0b = (id1 < 1e-9) and (id2 < 1e-9)
    P(f"G0b  size-invariance  max|pnl - qty*(pnl/qty)| = {id1:.3e} (spec <1e-9) ; "
      f"max|comm - 4.36*qty| = {id2:.3e}  -> {'PASS' if g0b else 'FAIL'}")
    P(f"     qty multiset: " + ", ".join(f"{int(q)}x{int((nt.qty==q).sum())}"
                                         for q in sorted(nt.qty.unique())) +
      f" ; total ctrRT {int(nt.qty.sum())}")

    # ------------------------------------------------------------- session date + seal
    et = nt["et"]
    sess = et.dt.normalize() + pd.to_timedelta((et.dt.hour >= 18).astype(int), unit="D")
    nt["session"] = sess.dt.strftime("%Y-%m-%d")
    nt["sess_ts"] = sess

    sealed_mask = nt["sess_ts"] > WINDOW_HI_SESSION
    pre_mask = nt["sess_ts"] < WINDOW_LO
    P("")
    P(f"SEAL   arm window = sessions {WINDOW_LO.date()} .. {WINDOW_HI_SESSION.date()}")
    P(f"       rows DROPPED as sealed (session >= 2026-08-01): {int(sealed_mask.sum())}"
      f"   (net ${nt.loc[sealed_mask,'pnl'].sum():,.2f}, never used in any arm)")
    P(f"       rows dropped as pre-window: {int(pre_mask.sum())}")
    df = nt[~sealed_mask & ~pre_mask].reset_index(drop=True).copy()
    P(f"       arm-window trades: {len(df)}  net ${df.pnl.sum():,.2f}  "
      f"ctrRT {int(df.qty.sum())}")

    # ------------------------------------------------------------- join to the session table
    ss = pd.read_parquet(SESSTRUCT)
    assert int(ss["sealed"].sum()) == 0, "session table carries sealed rows"
    ss = ss[(ss["session"] >= "2022-01-01") & (ss["session"] <= "2026-07-31")].copy()
    ss = ss.sort_values("session").reset_index(drop=True)
    S = len(ss)
    P(f"       session table rows in window: {S}  ({ss.session.min()} .. {ss.session.max()}), "
      f"0 sealed")

    sess_pos = {s: i for i, s in enumerate(ss["session"].tolist())}
    df["spos"] = df["session"].map(sess_pos).fillna(-1).astype(int)
    feat_series = ss[FEATURE].to_numpy(float)
    reason_series = ss["reason"].to_numpy()

    joined = df["spos"].to_numpy() >= 0
    jr = float(joined.mean())
    g0c = jr >= 0.95
    P("")
    P(f"G0c  join rate to the session table: {joined.sum()}/{len(df)} = {100*jr:.2f}%  "
      f"(spec >=95%)  -> {'PASS' if g0c else 'FAIL'}")
    if (~joined).sum():
        bad = df[~joined]
        P(f"     UNMATCHED trades, BY REASON ({len(bad)}):")
        for s_, g in bad.groupby("session"):
            P(f"       session {s_}  n={len(g)}  reason=SESSION_NOT_IN_TABLE "
              f"(no 1-min bars / holiday) entries "
              f"{', '.join(str(x) for x in g.et.dt.strftime('%Y-%m-%d %H:%M').tolist()[:4])}")
    fv = np.where(joined, feat_series[np.maximum(df["spos"].to_numpy(), 0)], np.nan)
    df["open_loc"] = fv
    nan_feat = ~np.isfinite(fv)
    P(f"     joined but feature UNDEFINED (degenerate/unusable session): {int((nan_feat & joined).sum())}")
    if int((nan_feat & joined).sum()):
        for s_, g in df[nan_feat & joined].groupby("session"):
            rr = reason_series[sess_pos[s_]]
            P(f"       session {s_}  n={len(g)}  reason={rr or 'FEATURE_NAN'}")
    P(f"     -> these keep the INCUMBENT size, are COUNTED, and are never dropped (spec trap 6).")

    g0 = g0a and g0b and g0c
    P("")
    P(f"G0 OVERALL: {'PASS' if g0 else 'FAIL'}")
    if not g0:
        P("G0 FAILED -> THE ARMS ARE VOID.  Reporting the verification failure only.")
        json.dump(dict(G0a=bool(g0a), G0b=bool(g0b), G0c=bool(g0c), verdict="VOID"),
                  open(os.path.join(OUT, "gates.json"), "w"), indent=1)
        _fh.close()
        return

    # ============================================================== eligibility
    tod = df["et"].dt.hour * 60 + df["et"].dt.minute
    elig = ((tod >= 9 * 60 + 30) & (tod < 17 * 60)).to_numpy()
    n_elig = int(elig.sum())
    hr()
    P(f"ELIGIBILITY  (spec section 2: the overnight range does not EXIST before 09:30, so applying")
    P(f"             the rule earlier would be a look-ahead of hours - not a tuned scope)")
    hr()
    P(f"  arm-window trades      {len(df)}")
    P(f"  ELIGIBLE (>= 09:30)    {n_elig}   = {100*n_elig/len(df):.1f}% of the book")
    P(f"  pre-09:30 (untouched)  {len(df)-n_elig}")
    P(f"  of the eligible, entries inside the 09:30 minute itself: "
      f"{int(((df.et.dt.hour==9)&(df.et.dt.minute==30)).sum())}")
    P(f"  eligible with an UNDEFINED feature (keep incumbent size): "
      f"{int((nan_feat & elig).sum())}")
    P(f"  ==> EVERY FIGURE BELOW IS CARRIED BY AT MOST {n_elig} TRADES.")

    per = df["pnl"].to_numpy(float) / df["qty"].to_numpy(float)
    sA0 = df["qty"].to_numpy(np.int64)
    dates = df["session"].tolist()
    all_weeks = sorted({CE.iso_week(d) for d in dates})
    yr = df["et"].dt.year.to_numpy()

    # ============================================================== build A1
    ei = np.flatnonzero(elig)
    sA1_e, taus_e, rs_e, n_short = a1_sizes(fv[ei], sA0[ei])
    sA1 = sA0.copy()
    sA1[ei] = sA1_e
    taus = np.full(len(df), np.nan); taus[ei] = taus_e
    rs = np.full(len(df), np.nan); rs[ei] = rs_e

    assert np.all(sA1 >= sA0), "arm reduced a size - violates spec section 3"
    assert np.all(sA1[~elig] == sA0[~elig]), "arm touched a pre-09:30 entry"

    pA0 = per * sA0
    pA1 = per * sA1

    hr()
    P("THE TWO ARMS")
    hr()
    P(f"{'arm':<18}{'trades':>8}{'ctrRT':>8}{'mean sz':>10}{'size-2 n':>10}{'size-2 %':>10}"
      f"{'net $':>15}{'net/week $':>13}")
    for nm, s, p in (("A0_INCUMBENT", sA0, pA0), ("A1_OPENSTRENGTH", sA1, pA1)):
        w = weekly_of(dates, p, all_weeks)
        P(f"{nm:<18}{len(s):>8}{int(s.sum()):>8}{s.mean():>10.4f}{int((s==2).sum()):>10}"
          f"{100*np.mean(s==2):>9.1f}%{p.sum():>15,.2f}{w.mean():>13,.2f}")
    chg = int(np.sum(sA1 != sA0))
    P(f"\nentries whose size CHANGED: {chg}  (all 1->2, all eligible; eligible n = {n_elig})")
    ov_a0 = (sA0[ei] == 2)
    ov_ft = (sA1_e == 2) & ~ov_a0
    P(f"  eligible size-2 sets:  incumbent {int(ov_a0.sum())}  |  feature-added {int(ov_ft.sum())}"
      f"  |  union {int((sA1_e==2).sum())}  of {n_elig} eligible")
    fsel = (sA1_e == 2)
    jac = int((fsel & ov_a0).sum()) / max(1, int((fsel | ov_a0).sum()))
    P(f"  Jaccard(incumbent size-2, A1 size-2) on eligible = {jac:.3f}")
    P(f"  calibrator short-history skips: {n_short}")
    P(f"  mean r_i (incumbent trailing size-2 rate) = {np.nanmean(rs_e):.4f} ; "
      f"mean tau_i = {np.nanmean(taus_e):.4f}")

    # ============================================================== risk vectors
    sesspnl0 = pd.Series(pA0).groupby(df["session"]).sum().to_numpy()
    sesspnl1 = pd.Series(pA1).groupby(df["session"]).sum().to_numpy()
    rv0 = CE.risk_vector("A0_INCUMBENT", dates, pA0, sA0, all_weeks, FIXED_DD, sesspnl0)
    rv1 = CE.risk_vector("A1_OPENSTRENGTH", dates, pA1, sA1, all_weeks, FIXED_DD, sesspnl1)

    hr()
    P(f"THE FULL RISK VECTOR  (research_sdk/champion_eval.risk_vector, fixed-DD budget "
      f"${FIXED_DD:,.0f})   [eligible n = {n_elig}]")
    hr()
    fields = ["n_weeks", "n_trades", "contract_round_turns", "net_total", "net_per_week",
              "median_per_week", "pct_positive_weeks", "weekly_sd", "downside_sd", "es95",
              "worst_week", "worst_5_sessions", "max_dd", "dd_duration_weeks", "peak_contracts",
              "capital_proxy", "fixed_dd_income", "top_1pct_share", "top_10pct_share"]
    P(f"{'field':<24}{'A0_INCUMBENT':>18}{'A1_OPENSTRENGTH':>18}{'A1 - A0':>16}{'A1/A0':>10}")
    d0, d1 = rv0.as_dict(), rv1.as_dict()
    for f in fields:
        a, b = d0[f], d1[f]
        rat = (b / a) if (isinstance(a, (int, float)) and a not in (0,) and np.isfinite(a)) else float("nan")
        P(f"{f:<24}{a:>18,.4f}{b:>18,.4f}{b-a:>16,.4f}{rat:>10.4f}")

    # ============================================================== GATES
    gates = {}
    hr()
    P("PREREGISTERED GATE TABLE - PRINTED BY THE PROGRAM")
    P(f"population: {len(df)} arm-window trades, of which {n_elig} ELIGIBLE (post-09:30)")
    hr()
    rows = []

    # ---- G1 -------------------------------------------------------------------------------
    g1a = abs(sA1.mean() / sA0.mean() - 1.0)
    g1b = abs(sA1.sum() / sA0.sum() - 1.0)
    G1 = (g1a <= 0.02) and (g1b <= 0.02)
    rows.append(("G1 budget matched",
                 "|mean ratio-1|<=0.02 AND |sum ratio-1|<=0.02",
                 f"mean {sA1.mean():.4f}/{sA0.mean():.4f} d={100*g1a:.2f}% ; "
                 f"ctrRT {int(sA1.sum())}/{int(sA0.sum())} d={100*g1b:.2f}%", G1))
    gates["G1"] = dict(passed=bool(G1), mean_ratio=float(sA1.mean()/sA0.mean()),
                       sum_ratio=float(sA1.sum()/sA0.sum()),
                       ctr_A0=int(sA0.sum()), ctr_A1=int(sA1.sum()))

    # ---- G2 -------------------------------------------------------------------------------
    es_floor = rv0.es95 - 0.05 * abs(rv0.es95)
    dd_ceil = rv0.max_dd * 1.05
    c_net = rv1.net_per_week >= rv0.net_per_week
    c_es = rv1.es95 >= es_floor
    c_dd = rv1.max_dd <= dd_ceil
    G2 = c_net and c_es and c_dd
    rows.append(("G2 risk vector",
                 "net/wk>=A0 AND ES95 not worse >5% AND maxDD not worse >5%",
                 f"net/wk {rv1.net_per_week:,.2f} vs {rv0.net_per_week:,.2f} [{'ok' if c_net else 'NO'}] ; "
                 f"ES95 {rv1.es95:,.0f} vs floor {es_floor:,.0f} [{'ok' if c_es else 'NO'}] ; "
                 f"maxDD {rv1.max_dd:,.0f} vs ceil {dd_ceil:,.0f} [{'ok' if c_dd else 'NO'}]", G2))
    gates["G2"] = dict(passed=bool(G2), net_ok=bool(c_net), es_ok=bool(c_es), dd_ok=bool(c_dd),
                       netwk_A0=rv0.net_per_week, netwk_A1=rv1.net_per_week,
                       es95_A0=rv0.es95, es95_A1=rv1.es95,
                       maxdd_A0=rv0.max_dd, maxdd_A1=rv1.max_dd,
                       fixdd_A0=rv0.fixed_dd_income, fixdd_A1=rv1.fixed_dd_income)

    # ---- G3 -------------------------------------------------------------------------------
    t0 = CE.top_k_share(pA0, 0.10)
    t1 = CE.top_k_share(pA1, 0.10)
    G3 = (t1 >= 0.80 * t0) and (rv1.n_trades == rv0.n_trades)
    rows.append(("G3 tail preserved",
                 "top-decile share >= 0.80 x A0 AND trade count identical",
                 f"top10% {100*t1:.1f}% vs A0 {100*t0:.1f}% (ratio {t1/t0:.3f}) ; "
                 f"trades {rv1.n_trades} vs {rv0.n_trades}", G3))
    gates["G3"] = dict(passed=bool(G3), top10_A0=float(t0), top10_A1=float(t1),
                       ratio=float(t1 / t0))

    # ---- G4 : size-label permutation null --------------------------------------------------
    # Fast path for the 2,000 null replications: precompute the week index ONCE and verify it
    # reproduces champion_eval.weekly_from_trades exactly before it is used anywhere.
    _wi = {w: i for i, w in enumerate(all_weeks)}
    widx = np.array([_wi[CE.iso_week(d)] for d in dates], dtype=np.int64)
    NW = len(all_weeks)

    def fast_weekly(p):
        return np.bincount(widx, weights=p, minlength=NW)

    def fast_fixdd(p):
        return CE.fixed_dd_income(fast_weekly(p), FIXED_DD)

    assert np.allclose(fast_weekly(pA0), weekly_of(dates, pA0, all_weeks), atol=1e-9)
    assert np.allclose(fast_weekly(pA1), weekly_of(dates, pA1, all_weeks), atol=1e-9)

    fd1 = fixdd(dates, pA1, all_weeks)
    fd0 = fixdd(dates, pA0, all_weeks)
    rng = np.random.default_rng(20260831)
    nul = np.empty(N_NULL)
    for b in range(N_NULL):
        nul[b] = fast_fixdd(per * rng.permutation(sA1))
    nul = nul[np.isfinite(nul)]
    p95_4 = float(np.percentile(nul, 95))
    pct_4 = float(np.mean(nul < fd1))
    G4 = fd1 > p95_4
    rows.append(("G4 size-label null",
                 f"A1 fixDD wk$ > p95 of {N_NULL} permutations of A1's own size vector",
                 f"A1 ${fd1:,.2f} vs null p95 ${p95_4:,.2f} (mean ${nul.mean():,.2f}, "
                 f"pctile {100*pct_4:.1f})", G4))
    gates["G4"] = dict(passed=bool(G4), fixdd_A1=float(fd1), null_p95=p95_4,
                       null_mean=float(nul.mean()), percentile=100 * pct_4, n=int(len(nul)))

    # ---- G4b : circular-shift feature null (THE GATE THAT PRICES THE 11-CANDIDATE SCAN) -----
    shifts = rng.choice(np.arange(1, S), size=N_NULL, replace=(S - 1) < N_NULL)
    spos_e = df["spos"].to_numpy()[ei]
    nul_b = np.empty(N_NULL)
    for b, k in enumerate(shifts):
        fs = np.roll(feat_series, int(k))
        fe = np.where(spos_e >= 0, fs[np.maximum(spos_e, 0)], np.nan)
        s_e, _, _, _ = a1_sizes(fe, sA0[ei])
        s_full = sA0.copy(); s_full[ei] = s_e
        nul_b[b] = fast_fixdd(per * s_full)
    nul_b = nul_b[np.isfinite(nul_b)]
    p95_4b = float(np.percentile(nul_b, 95))
    pct_4b = float(np.mean(nul_b < fd1))
    G4b = fd1 > p95_4b
    rows.append(("G4b feature null",
                 f"A1 fixDD wk$ > p95 of {N_NULL} CIRCULAR SHIFTS of open_loc across sessions",
                 f"A1 ${fd1:,.2f} vs shift p95 ${p95_4b:,.2f} (mean ${nul_b.mean():,.2f}, "
                 f"pctile {100*pct_4b:.1f})", G4b))
    gates["G4b"] = dict(passed=bool(G4b), fixdd_A1=float(fd1), null_p95=p95_4b,
                        null_mean=float(nul_b.mean()), null_p50=float(np.percentile(nul_b, 50)),
                        null_max=float(nul_b.max()), percentile=100 * pct_4b,
                        n_shifts=int(len(nul_b)), n_sessions=int(S))

    # ---- G5 : stability --------------------------------------------------------------------
    def vec_on(mask):
        aw = sorted({CE.iso_week(d) for d, m in zip(dates, mask) if m})
        dd = [d for d, m in zip(dates, mask) if m]
        w0 = weekly_of(dd, pA0[mask], aw)
        w1 = weekly_of(dd, pA1[mask], aw)
        return dict(n0=float(w0.mean()), n1=float(w1.mean()),
                    e0=CE.expected_shortfall(w0), e1=CE.expected_shortfall(w1),
                    d0=CE.max_drawdown(w0)[0], d1=CE.max_drawdown(w1)[0],
                    f0=CE.fixed_dd_income(w0, FIXED_DD), f1=CE.fixed_dd_income(w1, FIXED_DD))

    def beats(v):
        """The SAME risk-vector criterion as G2, with a strict > on the return leg."""
        return (v["n1"] > v["n0"] and v["e1"] >= v["e0"] - 0.05 * abs(v["e0"])
                and v["d1"] <= 1.05 * v["d0"])

    P("")
    P("G5 detail - 25 rolling 24-month windows.  'beats' = the G2 risk-vector criterion")
    P("            (net/week strictly greater AND ES95 not worse >5% AND maxDD not worse >5%).")
    P(f"{'window start':<14}{'n':>6}{'elig':>6}{'A0 wk$':>11}{'A1 wk$':>11}{'A0 ES95':>11}"
      f"{'A1 ES95':>11}{'A0 DD':>11}{'A1 DD':>11}{'beats':>8}{'fixDD+':>8}")
    starts = pd.date_range("2022-01-01", "2024-08-01", periods=25)
    nwin = win_beat = win_fix = 0
    for st in starts:
        en = st + pd.DateOffset(months=24)
        m = ((df["et"] >= st) & (df["et"] < en)).to_numpy()
        if m.sum() < 100:
            continue
        nwin += 1
        v = vec_on(m)
        bb = beats(v)
        ff = v["f1"] > v["f0"]
        win_beat += int(bb); win_fix += int(ff)
        P(f"{st.strftime('%Y-%m-%d'):<14}{int(m.sum()):>6}{int((m&elig).sum()):>6}"
          f"{v['n0']:>11,.0f}{v['n1']:>11,.0f}{v['e0']:>11,.0f}{v['e1']:>11,.0f}"
          f"{v['d0']:>11,.0f}{v['d1']:>11,.0f}{'YES' if bb else 'no':>8}"
          f"{'YES' if ff else 'no':>8}")
    P("")
    P("G5 detail - leave-one-calendar-year-out (drop the year, recompute on the rest):")
    P(f"{'drop year':<12}{'n':>7}{'elig':>7}{'A0 wk$':>11}{'A1 wk$':>11}{'A0 ES95':>11}"
      f"{'A1 ES95':>11}{'A0 DD':>11}{'A1 DD':>11}{'beats':>8}")
    loyo = 0
    years = sorted(set(yr.tolist()))
    for y in years:
        m = (yr != y)
        v = vec_on(m)
        bb = beats(v)
        loyo += int(bb)
        P(f"ex-{y:<9}{int(m.sum()):>7}{int((m&elig).sum()):>7}{v['n0']:>11,.0f}{v['n1']:>11,.0f}"
          f"{v['e0']:>11,.0f}{v['e1']:>11,.0f}{v['d0']:>11,.0f}{v['d1']:>11,.0f}"
          f"{'YES' if bb else 'no':>8}")
    G5 = (nwin > 0 and win_beat / nwin >= 0.60) and (loyo >= 4)
    rows.append(("G5 stability",
                 ">=60% of 25 rolling 24m windows AND >=4/5 LOYO",
                 f"rolling {win_beat}/{nwin} = {100*win_beat/max(1,nwin):.0f}% ; LOYO {loyo}/{len(years)}",
                 G5))
    gates["G5"] = dict(passed=bool(G5), rolling_beat=int(win_beat), rolling_n=int(nwin),
                       rolling_frac=float(win_beat / max(1, nwin)),
                       rolling_beat_fixdd_only=int(win_fix), loyo=int(loyo), loyo_n=len(years))

    # ---- G6 : stationary bootstrap on the weekly DIFFERENCE --------------------------------
    w0 = weekly_of(dates, pA0, all_weeks)
    w1 = weekly_of(dates, pA1, all_weeks)
    diff = w1 - w0
    boot = CE.stationary_bootstrap(diff, N_BOOT, MEAN_BLOCK, np.random.default_rng(7))
    lo90, hi90 = float(np.percentile(boot, 5)), float(np.percentile(boot, 95))
    G6 = (lo90 > 0) or (hi90 < 0)
    sdd = float(np.std(diff, ddof=1))
    tstat = float(diff.mean() / (sdd / math.sqrt(len(diff)))) if sdd > 0 else float("nan")
    rows.append(("G6 block bootstrap",
                 f"stationary bootstrap (block {MEAN_BLOCK:.0f}wk, {N_BOOT} draws) of weekly "
                 f"(A1-A0): 90% CI excludes 0",
                 f"mean diff ${diff.mean():,.2f}/wk ; CI90 [${lo90:,.2f}, ${hi90:,.2f}] ; "
                 f"t = {tstat:.2f} DIAGNOSTIC ONLY", G6))
    gates["G6"] = dict(passed=bool(G6), diff_mean=float(diff.mean()), ci90=[lo90, hi90],
                       t_DIAGNOSTIC_ONLY=tstat, n_weeks=int(len(diff)))

    # scaled-to-fixed-DD variant, printed as a labelled diagnostic (NOT the gate)
    w0s = w0 * (FIXED_DD / rv0.max_dd)
    w1s = w1 * (FIXED_DD / rv1.max_dd)
    dsc = w1s - w0s
    bsc = CE.stationary_bootstrap(dsc, N_BOOT, MEAN_BLOCK, np.random.default_rng(8))
    lo_s, hi_s = float(np.percentile(bsc, 5)), float(np.percentile(bsc, 95))

    # ---- print the gate table --------------------------------------------------------------
    hr()
    P("GATE / SPEC / OBSERVED / PASS-FAIL")
    hr()
    P(f"{'GATE':<21}{'SPEC':<58}{'PASS-FAIL':>10}")
    for nm, spec, obs, ok in rows:
        P(f"{nm:<21}{spec:<58}{'PASS' if ok else 'FAIL':>10}")
        P(f"{'':<21}OBSERVED: {obs}")
    P("")
    allpass = all(r[3] for r in rows)
    verdict = "CANDIDATE (queued, NOT promoted, NOT built, NOT deployed)" if allpass else "FAIL"
    failed = [r[0].split()[0] for r in rows if not r[3]]
    P(f"VERDICT A1_OPENSTRENGTH (P1SZ_OPENLOC): {verdict}"
      + (f"   failed: {', '.join(failed)}" if failed else ""))
    P(f"  G0 PASS | " + " | ".join(f"{r[0].split()[0]} {'PASS' if r[3] else 'FAIL'}" for r in rows))

    # ============================================================== MANDATORY REPORTING
    hr()
    P(f"MANDATORY REPORTING (spec section 6)   [eligible n = {n_elig} of {len(df)} arm trades]")
    hr()

    P("\n1. A1 - A0 BY CALENDAR YEAR")
    P("   P1 is long-only and open_loc is directional, so part of any win could be a market-")
    P("   direction tilt rather than an excursion forecast.  2022 was a bear year; 2023-2025")
    P("   were not.  This split is mandatory, not optional.")
    P(f"{'year':<7}{'n':>7}{'elig':>7}{'A0 net $':>14}{'A1 net $':>14}{'A1-A0 $':>13}"
      f"{'A1-A0 $/wk':>12}{'A0 ctr':>9}{'A1 ctr':>9}{'sz chg':>8}{'$/extra ctr':>13}")
    yr_rows = []
    for y in years:
        m = yr == y
        aw = sorted({CE.iso_week(d) for d, mm in zip(dates, m) if mm})
        n0 = weekly_of([d for d, mm in zip(dates, m) if mm], pA0[m], aw)
        n1 = weekly_of([d for d, mm in zip(dates, m) if mm], pA1[m], aw)
        dcs = int(sA1[m].sum() - sA0[m].sum())
        dnet = float(pA1[m].sum() - pA0[m].sum())
        P(f"{y:<7}{int(m.sum()):>7}{int((m&elig).sum()):>7}{pA0[m].sum():>14,.0f}"
          f"{pA1[m].sum():>14,.0f}{dnet:>13,.0f}{(n1-n0).mean():>12,.0f}"
          f"{int(sA0[m].sum()):>9}{int(sA1[m].sum()):>9}{int((sA1[m]!=sA0[m]).sum()):>8}"
          f"{(dnet/dcs if dcs else float('nan')):>13,.0f}")
        yr_rows.append(dict(year=int(y), n=int(m.sum()), elig=int((m & elig).sum()),
                            net_A0=float(pA0[m].sum()), net_A1=float(pA1[m].sum()),
                            delta=dnet, delta_per_week=float((n1 - n0).mean()),
                            ctr_A0=int(sA0[m].sum()), ctr_A1=int(sA1[m].sum())))
    P(f"{'ALL':<7}{len(df):>7}{n_elig:>7}{pA0.sum():>14,.0f}{pA1.sum():>14,.0f}"
      f"{pA1.sum()-pA0.sum():>13,.0f}{diff.mean():>12,.0f}{int(sA0.sum()):>9}"
      f"{int(sA1.sum()):>9}{chg:>8}"
      f"{((pA1.sum()-pA0.sum())/(sA1.sum()-sA0.sum()) if sA1.sum()!=sA0.sum() else float('nan')):>13,.0f}")

    P("\n2. COST LINES.  $4.36/ctrRT is already inside the NT8 ledger P&L; the other two are an")
    P("   ADDITIONAL modelled spread charged per contract round turn.  G1 is supposed to force")
    P("   equal contract budgets, so all three lines must agree in SIGN.")
    P(f"{'extra $/ctrRT':<16}{'A0 net/wk':>13}{'A1 net/wk':>13}{'A1-A0 /wk':>12}"
      f"{'A0 fixDD wk':>14}{'A1 fixDD wk':>14}{'A1-A0 fixDD':>14}{'sign':>7}")
    cost_rows = []
    for ex in COST_LINES:
        q0 = per * sA0 - ex * sA0
        q1 = per * sA1 - ex * sA1
        u0 = weekly_of(dates, q0, all_weeks); u1 = weekly_of(dates, q1, all_weeks)
        f0_ = CE.fixed_dd_income(u0, FIXED_DD); f1_ = CE.fixed_dd_income(u1, FIXED_DD)
        d_ = float(u1.mean() - u0.mean())
        P(f"{'+$%.2f' % ex:<16}{u0.mean():>13,.2f}{u1.mean():>13,.2f}{d_:>12,.2f}"
          f"{f0_:>14,.2f}{f1_:>14,.2f}{f1_-f0_:>14,.2f}"
          f"{('+' if d_>0 else ('-' if d_<0 else '0')):>7}")
        cost_rows.append(dict(extra=ex, netwk_A0=float(u0.mean()), netwk_A1=float(u1.mean()),
                              delta_netwk=d_, fixdd_A0=float(f0_), fixdd_A1=float(f1_),
                              delta_fixdd=float(f1_ - f0_)))
    signs = {np.sign(c["delta_netwk"]) for c in cost_rows}
    P(f"   all three cost lines agree in sign: {'YES' if len(signs)==1 else 'NO'}")

    P("\n3. DIAGNOSTICS (labelled; NONE of these is a gate and none can change the verdict)")
    P(f"   G6 on the FIXED-DD-RESCALED weekly difference: mean ${dsc.mean():,.2f}/wk, "
      f"CI90 [{lo_s:,.2f}, {hi_s:,.2f}] -> "
      f"{'excludes 0' if (lo_s>0 or hi_s<0) else 'includes 0'}")
    P(f"   A0 fixed-DD weekly $ = ${fd0:,.2f} ; A1 = ${fd1:,.2f} ; "
      f"ratio {fd1/fd0:.4f} ({100*(fd1/fd0-1):+.1f}%)")
    P(f"   G5 under a fixed-DD-ONLY comparator (the T2_P1SIZE01 convention): "
      f"{win_fix}/{nwin} rolling windows")
    # week-index convention check
    wk_csv = df["wk"].to_numpy()
    wk_sess = np.array([CE.iso_week(d) for d in dates])
    P(f"   week index: this run uses the SESSION date -> ISO week (champion_eval's documented")
    P(f"   convention, and the join key the spec mandates).  The ledger's own `wk` column keys on")
    P(f"   the ENTRY calendar date and differs on {int((wk_csv != wk_sess).sum())} trades "
      f"(Sunday-evening entries).  Both arms share one index, so no gate can turn on it.")

    P("\n4. THE CEILING ARGUMENT, RESTATED AGAINST THE NUMBERS")
    P(f"   eligible trades {n_elig} / {len(df)} = {100*n_elig/len(df):.1f}% of the book.")
    P(f"   eligible net ${pA0[elig].sum():,.0f} of ${pA0.sum():,.0f} = "
      f"{100*pA0[elig].sum()/pA0.sum():.1f}% of A0's net.")
    P(f"   sizes changed on {chg} trades = {100*chg/len(df):.1f}% of the book, "
      f"{100*chg/max(1,n_elig):.1f}% of the eligible set.")
    P(f"   book-level A1-A0 = ${pA1.sum()-pA0.sum():,.0f} over {len(all_weeks)} weeks = "
      f"${diff.mean():,.2f}/week, on {int(sA1.sum()-sA0.sum())} extra contract round turns.")

    # ============================================================== artifacts
    led = pd.DataFrame(dict(
        et=df["et"], xt=df["xt"], session=df["session"], wk_session=wk_sess,
        wk_ledger=df["wk"], year=yr, eligible=elig, joined=joined,
        open_loc=fv, tau=taus, r_incumbent=rs,
        per_ctr=per, qty_A0=sA0, qty_A1=sA1, size_changed=(sA1 != sA0),
        pnl_A0=pA0, pnl_A1=pA1, delta=pA1 - pA0))
    led.to_csv(os.path.join(OUT, "arm_ledger.csv"), index=False)

    gj = dict(
        run_id="G3_P1GAP01_20260831", feature=FEATURE, live_enabled="NO", spend=0,
        orders_placed="NO",
        population=dict(ledger_rows=int(len(nt)), arm_window_trades=int(len(df)),
                        sealed_rows_dropped=int(sealed_mask.sum()),
                        pre_window_rows_dropped=int(pre_mask.sum()),
                        eligible_post_0930=int(n_elig),
                        eligible_pct=float(100 * n_elig / len(df)),
                        sizes_changed=int(chg), weeks=int(len(all_weeks))),
        G0=dict(G0a=bool(g0a), G0b=bool(g0b), G0c=bool(g0c), passed=bool(g0),
                join_rate=float(jr), unmatched=int((~joined).sum()),
                feature_nan_joined=int((nan_feat & joined).sum()),
                identity_pnl=id1, identity_comm=id2, net=net_all, net_reference=ref["net"]),
        **gates,
        by_year=yr_rows, cost_lines=cost_rows,
        risk_vector_A0=rv0.as_dict(), risk_vector_A1=rv1.as_dict(),
        verdict=("CANDIDATE" if allpass else "FAIL"),
        failed_gates=failed,
        diagnostics=dict(fixdd_A0=float(fd0), fixdd_A1=float(fd1),
                         g6_fixdd_scaled_ci90=[lo_s, hi_s],
                         g6_fixdd_scaled_mean=float(dsc.mean()),
                         jaccard_size2_eligible=float(jac),
                         week_index_disagreements=int((wk_csv != wk_sess).sum())),
    )
    json.dump(gj, open(os.path.join(OUT, "gates.json"), "w"), indent=1, default=float)

    hr()
    P("artifacts: out/console.txt  out/gates.json  out/arm_ledger.csv")
    P("NO ORDER PLACED · LIVE = NO · $0 · NOTHING PROMOTED, BUILT OR DEPLOYED")
    hr()
    _fh.close()


if __name__ == "__main__":
    main()
