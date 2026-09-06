"""G3_ESMR_PORTFOLIO_20260906  (ledger trial G00066, family GENESIS3_DECISION)

Economic adjudication of the already-observed ES MR effect (W2B_EQMR / G00063) as a SHRUNK
portfolio addition to P1.  This is NOT a rescue of G00063 -- its family-corrected FAIL stands.

Frozen object: runs/W2B_EQMR_20260906/out/daily_pnl_ES.csv  (engine_pnl column), used AS-IS.
G0 asserts its sha256 BEFORE anything else runs, then reproduces the P1 daily PnL through the
IDENTICAL code path W2B used for its G6 orthogonality computation (xinst_bench + we_lab
spread_profile) and asserts the daily rho matches the recorded W2B value within +-0.005.

Preregistered construction (spec.yaml, frozen):
  Book(lambda) = P1 + lambda * k * ESMR_s ,  k = sigma(P1)/sigma(ESMR) vol-match,
  two k variants: (a) static full-sample (DESCRIPTIVE), (b) causal expanding (min 250 obs);
  lambda in {0.25, 0.5, 1.0};  shrinkage ESMR_s = ESMR - (1-s)*mean(ESMR), s in
  {1.0, 0.75, 0.5, 0.25, 0} applied to the ESMR leg only.  No optimizer, no other weights,
  NO retuning of anything.

PREREG-AMBIGUITY RESOLUTIONS (fixed here, in code, BEFORE results exist; all documented):
  R1 causal k_t uses observations STRICTLY BEFORE day t (shifted expanding std, ddof=1) and
     requires >= 250 prior obs; before that the ESMR leg weight is 0 (book = P1-alone).
     Zero-weight warmup is the only fully causal choice.
  R2 the shrinkage mean is the FULL-SAMPLE mean of the frozen ESMR series (the spec's literal
     formula); shrinkage is a stress on the observed mean, not a forecast.
  R3 marginal weekly-vol Sharpe = sharpe_wk(book weekly) - sharpe_wk(P1-alone weekly), with
     the identical ISO-week aggregation and sharpe_wk W2B used.
  R4 marginal annualized return = 52 * (mean weekly book - mean weekly P1).
  R5 maxDD and CDaR5 are computed on the DAILY dollar path with research_sdk.eval_battery's
     max_drawdown / cdar(alpha=0.95); "within +5%" means book <= 1.05 * P1-alone.
  R6 s* two-method agreement tolerance: 0.05 in s units (the function is ~linear in s).
  R7 fixed-DD INCOME basis is NOT quoted anywhere in this run: the book REMOVES NO TRADES, so
     a rate-matched random-thinning placebo is undefined (removal rate is zero), and per
     doctrine an unguarded order-statistic income figure is unquotable.  The decision rule's
     maxDD/CDaR5 clauses are DOLLAR TAIL-WORSENING checks (book vs P1 on the same calendar),
     not income normalizations, so the thinning artifact cannot arise there.

SEAL: inputs end 2026-07-31; every loaded series asserts max session < 2026-08-01.
Evidence status: DISCOVERY_CONSUMED (decision analysis of an already-observed effect).
NO deploy.  Either answer closes the question; G00063's statistical verdict is untouched.
"""
from __future__ import annotations

import hashlib
import os
import sys
import time as _t

import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
HERE = os.path.dirname(os.path.abspath(__file__))
RUNDIR = os.path.dirname(HERE)
OUT = os.path.join(RUNDIR, "out")
os.makedirs(OUT, exist_ok=True)

XB_SRC = os.path.join(REPO, "runs", "XINST01_WEEKLY_EDGE_PORT_20260906", "src")
for p in (XB_SRC, os.path.join(REPO, "research", "weekly_edge", "src"), REPO):
    if p not in sys.path:
        sys.path.insert(0, p)
import xinst_bench as XB                                             # noqa: E402
from we_lab import spread_profile                                    # noqa: E402
import research_sdk.eval_battery as EB                               # noqa: E402

SEAL = pd.Timestamp("2026-08-01")
WIN_B = SEAL

# ---- frozen inputs -----------------------------------------------------------------------
ES_CSV = os.path.join(REPO, "runs", "W2B_EQMR_20260906", "out", "daily_pnl_ES.csv")
ES_SHA = "67c97694b373b0c82fe96224555adafd0662863113bf5d5c0dad39e5c31e2318"
RHO_REC = 0.2259743509186386      # W2B G6 recorded daily rho (neighborhood.csv, ES primary)
RHO_TOL = 0.005

# ---- P1 reproduction constants (identical to W2B_EQMR src/eqmr.py p1_daily) --------------
NQ_SUB = "runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet"
PV_NQ = 20.0
TICK_NQ = 0.25
COMM = 4.36

# ---- preregistered grids ------------------------------------------------------------------
LAMBDAS = (0.25, 0.5, 1.0)
SHRINKS = (1.0, 0.75, 0.5, 0.25, 0.0)
KVARS = ("static", "causal")
KMIN = 250                        # min obs for causal expanding k
STOL = 0.05                       # R6: s* two-method agreement tolerance
DEC = dict(kvar="causal", lam=0.5, s=0.5)     # the preregistered decision cell

ES_MARGIN_ASSUMED = 12650.0       # $/contract CME ES initial margin, ASSUMED (ballpark), tag below

_LOG = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    _LOG.append(s)


def to_weekly(dates, daily):
    iso = pd.DatetimeIndex(dates).isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    return pd.Series(np.asarray(daily, float), index=wk).groupby(level=0).sum()


def sharpe_wk(x):
    x = np.asarray(x, float)
    sd = x.std(ddof=1)
    return float(x.mean() / sd * np.sqrt(52)) if sd > 0 else float("nan")


# ================================================================= P1 daily PnL (reproduced)
def p1_daily():
    """IDENTICAL code path to W2B_EQMR_20260906/src/eqmr.py::p1_daily (its G6 input)."""
    prof = spread_profile()
    Dnq, bnq = XB.load_substrate(NQ_SUB, "NQ")
    P(f"  [P1] NQ substrate {bnq['n_bars']:,} bars / {bnq['n_sess']:,} sess "
      f"{bnq['first_sess']} -> {bnq['last_sess']}  seal_ok={bnq['seal_ok']}")
    if not bnq["seal_ok"]:
        raise RuntimeError("SEAL VIOLATION P1/NQ")
    trnq, mnq = XB.build_p1pct(Dnq, PV=PV_NQ, comm=COMM, halt_pts=XB.NQ_HALT_PTS,
                               tgt_pts=XB.NQ_TGT_PTS, smin_pts=None, smax_pts=None,
                               stopm_pts=None, win_a="2022-07-01", win_b=str(WIN_B.date()))
    net_nq, ct_nq, rate_nq, ntr = XB.net_series(Dnq, trnq, PV=PV_NQ, tick=TICK_NQ,
                                                spread_model=("nq_profile", prof),
                                                sess_in=mnq["sess_in"], i_of=mnq["i_of"])
    sd = pd.to_datetime(Dnq["sess_date"])[mnq["sess_in"]]
    daily = pd.Series(net_nq, index=pd.DatetimeIndex(sd).normalize()).groupby(level=0).sum()
    wk = to_weekly(daily.index, daily.to_numpy())
    P(f"  [P1] reproduced P1/PCT: {ntr:,} trades, spread ${rate_nq:.3f}/ctrRT, "
      f"{len(daily):,} P&L days, weekly ${wk.mean():,.2f}")
    return daily


# ================================================================= path statistics
def path_stats(dates, daily):
    daily = np.asarray(daily, float)
    wk = to_weekly(dates, daily)
    mo = pd.Series(daily, index=pd.DatetimeIndex(dates).to_period("M")).groupby(level=0).sum()
    return dict(wk_mean=float(wk.mean()), wk_sh=sharpe_wk(wk.to_numpy()),
                maxdd=EB.max_drawdown(daily), cdar5=EB.cdar(daily, alpha=0.95),
                worst_mo=float(mo.min()), wk=wk)


def book_daily(p1, es, k_t, lam, s, mu_es):
    return p1 + lam * k_t * (es - (1.0 - s) * mu_es)


# ================================================================= main
def main():
    t0 = _t.time()
    P("=" * 112)
    P("G3_ESMR_PORTFOLIO_20260906  trial G00066  family GENESIS3_DECISION")
    P("SHRUNK portfolio contribution of the frozen ES MR series to P1 -- decision analysis, "
      "DISCOVERY_CONSUMED, NO deploy")
    P("NOT a rescue of G00063: its family-corrected FAIL stands untouched.")
    P("=" * 112)

    # ---------------------------------------------------------------- G0: identity + seal
    P("\n[G0] IDENTITY -- frozen input hash, seal, and P1 rho reproduction")
    with open(ES_CSV, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    sha_ok = (sha == ES_SHA)
    P(f"  sha256(daily_pnl_ES.csv) = {sha}")
    P(f"  expected                 = {ES_SHA}   match = {sha_ok}")
    if not sha_ok:
        raise RuntimeError("G0 HASH MISMATCH: frozen ES MR series is not the object W2B wrote.")

    es_df = pd.read_csv(ES_CSV, parse_dates=["date"])
    dates = pd.DatetimeIndex(es_df["date"])
    es = es_df["engine_pnl"].to_numpy(float)
    seal_ok = bool(dates.max() < SEAL)
    P(f"  ES MR series: {len(es)} sessions  {dates.min().date()} -> {dates.max().date()}  "
      f"seal(max<2026-08-01) = {seal_ok}")
    if not seal_ok:
        raise RuntimeError("SEAL VIOLATION: ES series extends past 2026-07-31")

    p1_full = p1_daily()
    p1_seal_ok = bool(p1_full.index.max() < SEAL)
    P(f"  P1 series seal(max<2026-08-01) = {p1_seal_ok}")
    if not p1_seal_ok:
        raise RuntimeError("SEAL VIOLATION: P1 series extends past 2026-07-31")

    # W2B G6 alignment convention, reproduced exactly: P1 reindexed to ES dates, fillna(0)
    p1 = p1_full.reindex(dates).fillna(0.0).to_numpy(float)
    rho = float(pd.Series(es, index=dates).corr(pd.Series(p1, index=dates)))
    rho_ok = bool(abs(rho - RHO_REC) <= RHO_TOL)
    P(f"  daily rho(ESMR, P1) = {rho:+.6f}   recorded W2B value = {RHO_REC:+.6f}   "
      f"|diff| = {abs(rho-RHO_REC):.6f}  (tol {RHO_TOL})  ok = {rho_ok}")
    # extra identity diagnostic (non-binding): the CSV's own stored p1_pnl column
    dmax = float(np.max(np.abs(es_df["p1_pnl"].to_numpy(float) - p1)))
    P(f"  diagnostic: max|reproduced P1 - CSV p1_pnl column| = ${dmax:.6f}")
    n_out = int((~p1_full.index.isin(dates)).sum())
    d_out = float(p1_full[~p1_full.index.isin(dates)].sum())
    P(f"  diagnostic: P1 PnL days outside the ES date basis = {n_out} (${d_out:,.2f}); both book "
      f"and P1-alone are judged on the SAME {len(dates)}-session basis, so the comparison is fair")
    g0 = bool(sha_ok and seal_ok and p1_seal_ok and rho_ok)
    if not g0:
        raise RuntimeError("G0 IDENTITY FAILED -- the inputs are not the objects W2B measured; run void.")

    # ---------------------------------------------------------------- vol-match ratios k
    P("\n[k] VOL-MATCH RATIOS  k = sigma(P1)/sigma(ESMR)  (daily, ddof=1)")
    sd_p1 = float(np.std(p1, ddof=1))
    sd_es = float(np.std(es, ddof=1))
    k_static = sd_p1 / sd_es
    P(f"  sigma(P1) = ${sd_p1:,.2f}/day   sigma(ESMR) = ${sd_es:,.2f}/day   "
      f"k_static = {k_static:.4f}   [DESCRIPTIVE -- uses the full sample]")
    # causal expanding k: strictly-prior data, min 250 obs, else leg weight 0 (R1)
    p1_s = pd.Series(p1)
    es_s = pd.Series(es)
    sd_p1_exp = p1_s.expanding(min_periods=KMIN).std(ddof=1).shift(1)
    sd_es_exp = es_s.expanding(min_periods=KMIN).std(ddof=1).shift(1)
    k_causal = (sd_p1_exp / sd_es_exp).to_numpy(float)
    warm = ~np.isfinite(k_causal)
    k_causal[warm] = 0.0
    n_warm = int(warm.sum())
    P(f"  k_causal: expanding, strictly-prior, min {KMIN} obs; warmup days with leg weight 0 = "
      f"{n_warm}; k_causal range after warmup [{k_causal[~warm].min():.4f}, "
      f"{k_causal[~warm].max():.4f}], final {k_causal[-1]:.4f}")

    mu_es = float(np.mean(es))
    P(f"  full-sample mean(ESMR) = ${mu_es:,.4f}/day  (the shrinkage target, R2)")

    # ---------------------------------------------------------------- P1-alone reference
    ref = path_stats(dates, p1)
    P("\n[REF] P1-ALONE on the common basis:")
    P(f"  weekly ${ref['wk_mean']:,.2f}/wk   weekly-vol Sharpe {ref['wk_sh']:.4f}   "
      f"maxDD ${ref['maxdd']:,.2f}   CDaR5 ${ref['cdar5']:,.2f}   worst month ${ref['worst_mo']:,.2f}")

    # ---------------------------------------------------------------- G1: full marginal table
    P("\n[G1] FULL lambda x s MARGINAL-ECONOMICS TABLE (both k variants; program-printed)")
    P("  marg_Sh = book weekly-vol Sharpe minus P1-alone; marg_ann = 52*(wk mean diff); "
      "DD/CDaR ratios = book/P1-alone")
    hdr = (f"  {'kvar':>7}{'lam':>6}{'s':>6}{'book$/wk':>11}{'bookSh':>8}{'margSh':>9}"
           f"{'marg$ann':>11}{'maxDD$':>10}{'DDrat':>7}{'CDaR5$':>10}{'CDrat':>7}{'worstMo$':>11}")
    P(hdr)
    rows = []
    cells = {}
    n_printed = 0
    for kv in KVARS:
        k_t = np.full(len(es), k_static) if kv == "static" else k_causal
        for lam in LAMBDAS:
            for s in SHRINKS:
                b = book_daily(p1, es, k_t, lam, s, mu_es)
                st = path_stats(dates, b)
                marg_sh = st["wk_sh"] - ref["wk_sh"]
                marg_ann = 52.0 * (st["wk_mean"] - ref["wk_mean"])
                ddrat = st["maxdd"] / ref["maxdd"]
                cdrat = st["cdar5"] / ref["cdar5"]
                row = dict(kvar=kv, lam=lam, s=s, book_wk=st["wk_mean"], book_sh=st["wk_sh"],
                           marg_sh=marg_sh, marg_ann=marg_ann, maxdd=st["maxdd"],
                           dd_ratio=ddrat, cdar5=st["cdar5"], cdar_ratio=cdrat,
                           worst_month=st["worst_mo"])
                rows.append(row)
                cells[(kv, lam, s)] = row
                P(f"  {kv:>7}{lam:>6.2f}{s:>6.2f}{st['wk_mean']:>11,.2f}{st['wk_sh']:>8.4f}"
                  f"{marg_sh:>+9.4f}{marg_ann:>11,.0f}{st['maxdd']:>10,.0f}{ddrat:>7.3f}"
                  f"{st['cdar5']:>10,.0f}{cdrat:>7.3f}{st['worst_mo']:>11,.0f}")
                n_printed += 1
    n_expected = len(KVARS) * len(LAMBDAS) * len(SHRINKS)
    g1 = bool(n_printed == n_expected)
    P(f"  cells printed = {n_printed} / expected {n_expected}  -> G1 = {g1}")
    P("  NOTE (R7): no fixed-DD INCOME figure appears in this run. The book removes zero "
      "trades, so a rate-matched random-thinning placebo is undefined (rate 0); per doctrine "
      "the unguarded figure is unquotable. maxDD/CDaR5 above are DOLLAR tail statistics of "
      "the same calendar path, used only as tail-worsening checks, never as income denominators.")

    # ---------------------------------------------------------------- G2: break-even s*
    P("\n[G2] BREAK-EVEN SHRINKAGE s* -- lambda=0.5, causal k")
    P("  IN WORDS: s* is the fraction of the ES MR leg's full-sample mean that must be retained "
      "for the lambda=0.5 causal-k book's weekly-vol Sharpe to exactly equal P1-alone's. It is "
      "the s at which the MARGINAL weekly-vol Sharpe of that book CROSSES ZERO: for s > s* the "
      "book beats P1-alone on the primary metric, for s < s* it does not. The event is over the "
      "1,053-session 2022-07..2026-07 in-sample path -- DISCOVERY_CONSUMED, not a forward claim.")

    def marg_sh_of(s):
        b = book_daily(p1, es, k_causal, 0.5, s, mu_es)
        wkb = to_weekly(dates, b)
        return sharpe_wk(wkb.to_numpy()) - ref["wk_sh"]

    # method 1: linear interpolation on the preregistered 5-point grid
    gvals = [(s, cells[("causal", 0.5, s)]["marg_sh"]) for s in sorted(SHRINKS)]
    s_interp = None
    for (s_lo, m_lo), (s_hi, m_hi) in zip(gvals[:-1], gvals[1:]):
        if (m_lo <= 0.0 <= m_hi) or (m_hi <= 0.0 <= m_lo):
            s_interp = s_lo + (0.0 - m_lo) * (s_hi - s_lo) / (m_hi - m_lo) if m_hi != m_lo else s_lo
            break
    # method 2: direct sign-scan on a fine grid
    fine = np.round(np.arange(0.0, 1.0001, 0.001), 3)
    mvals = np.array([marg_sh_of(s) for s in fine])
    pos = mvals > 0.0
    s_scan = None
    if pos.any() and (~pos).any():
        # largest s with marg<=0 whose successor is >0 (the crossing from below)
        idx = np.where(~pos[:-1] & pos[1:])[0]
        if len(idx):
            i = idx[-1]
            s_scan = float(fine[i] + (fine[i + 1] - fine[i]) * (0.0 - mvals[i])
                           / (mvals[i + 1] - mvals[i]))
    all_pos = bool(pos.all())
    all_neg = bool((~pos).all())
    if all_pos:
        P("  method 1 (grid interpolation): no sign change on the 5-point grid -- marginal "
        "Sharpe > 0 at EVERY s in [0,1] -> s* < 0 (book beats P1-alone even fully de-meaned)")
        P("  method 2 (direct sign-scan, step 0.001): marginal Sharpe > 0 at all 1001 points "
          "-> s* < 0")
        agree = (s_interp is None)
    elif all_neg:
        P("  method 1 (grid interpolation): no sign change -- marginal Sharpe < 0 at EVERY s "
          "-> s* > 1 (book never beats P1-alone, even unshrunk)")
        P("  method 2 (direct sign-scan, step 0.001): marginal Sharpe < 0 at all 1001 points "
          "-> s* > 1")
        agree = (s_interp is None)
    else:
        P(f"  method 1 (grid interpolation on preregistered 5-point s grid): s* = "
          f"{s_interp if s_interp is not None else float('nan'):.4f}")
        P(f"  method 2 (direct sign-scan, 0.001 grid, exact recompute at each s): s* = "
          f"{s_scan if s_scan is not None else float('nan'):.4f}")
        agree = (s_interp is not None and s_scan is not None
                 and abs(s_interp - s_scan) <= STOL)
    P(f"  methods agree (tol {STOL} in s units, R6) = {agree}")
    for s in sorted(SHRINKS):
        P(f"    marginal weekly-vol Sharpe at s={s:.2f}: {cells[('causal',0.5,s)]['marg_sh']:+.4f}")
    g2 = bool(agree)
    sstar_txt = ("<0 (positive at every s)" if all_pos else
                 (">1 (negative at every s)" if all_neg else f"{s_scan:.4f}"))

    # ---------------------------------------------------------------- supporting (non-binding)
    P("\n[SUPPORT] NON-BINDING DIAGNOSTICS (reported per spec metrics list)")
    wk_p1 = ref["wk"]
    wk_es_raw = to_weekly(dates, es)
    j = pd.concat([wk_p1.rename("p1"), wk_es_raw.rename("es")], axis=1).dropna()
    lose = j[j["p1"] < 0]
    P(f"  losing-P1-week conditional ESMR mean (raw 1-contract engine): "
      f"${lose['es'].mean():,.2f}/wk over {len(lose)} losing weeks of {len(j)} "
      f"(unconditional ${j['es'].mean():,.2f}/wk); weekly rho = {j['p1'].corr(j['es']):+.4f}")
    leg_dec = 0.5 * k_causal * (es - 0.5 * mu_es)
    wk_leg = to_weekly(dates, leg_dec)
    jl = pd.concat([wk_p1.rename("p1"), wk_leg.rename("leg")], axis=1).dropna()
    ll = jl[jl["p1"] < 0]
    P(f"  losing-P1-week conditional DECISION-CELL leg mean (lam=0.5,s=0.5,causal): "
      f"${ll['leg'].mean():,.2f}/wk (unconditional ${jl['leg'].mean():,.2f}/wk)")

    thr_p1 = np.percentile(p1, 10)
    thr_es = np.percentile(es, 10)
    A = p1 <= thr_p1
    B = es <= thr_es
    nA, nB, nAB = int(A.sum()), int(B.sum()), int((A & B).sum())
    exp_ab = nA * nB / len(p1)
    P(f"  worst-decile-day co-loss overlap: P1 worst-decile days {nA}, ESMR worst-decile {nB}, "
      f"joint {nAB} vs {exp_ab:.1f} expected under independence (lift {nAB/exp_ab:.2f}x); "
      f"ESMR<0 on {int((A & (es<0)).sum())}/{nA} of P1's worst-decile days")

    # joint-drawdown windows: worst-decile underwater depth of each series
    def underwater(x):
        c = np.cumsum(np.asarray(x, float))
        z = np.concatenate([[0.0], c])
        return (np.maximum.accumulate(z) - z)[1:]
    uw_p1 = underwater(p1)
    uw_es = underwater(es)
    dA = uw_p1 >= np.percentile(uw_p1, 90)
    dB = uw_es >= np.percentile(uw_es, 90)
    ndA, ndB, ndAB = int(dA.sum()), int(dB.sum()), int((dA & dB).sum())
    P(f"  joint-drawdown days (own worst-decile underwater depth): P1 {ndA}, ESMR {ndB}, "
      f"joint {ndAB} vs {ndA*ndB/len(p1):.1f} expected under independence "
      f"(lift {ndAB/(ndA*ndB/len(p1)):.2f}x)")
    # top-3 P1 drawdown windows and the decision-cell leg PnL inside them
    c = np.cumsum(p1)
    peakv = np.maximum.accumulate(c)
    dd = peakv - c
    troughs = []
    in_dd = dd > 0
    i = 0
    while i < len(dd):
        if in_dd[i]:
            jx = i
            while jx < len(dd) and in_dd[jx]:
                jx += 1
            seg = slice(i, jx)
            t_rel = int(np.argmax(dd[seg]))
            troughs.append((float(dd[seg][t_rel]), i, i + t_rel))
            i = jx
        else:
            i += 1
    troughs.sort(reverse=True)
    P("  top-3 P1 drawdown windows (peak day -> trough day, depth) with leg PnL inside:")
    for depth, i0, it in troughs[:3]:
        leg_sum = float(np.sum(leg_dec[i0:it + 1]))
        es_sum = float(np.sum(es[i0:it + 1]))
        P(f"    {dates[i0].date()} -> {dates[it].date()}  P1 depth ${depth:,.0f}  "
          f"decision-leg PnL ${leg_sum:+,.0f}  raw-ESMR PnL ${es_sum:+,.0f}")

    n_leg = 0.5 * k_static
    P(f"  incremental capital: decision-cell leg ~ lambda*k = 0.5*{k_static:.3f} = {n_leg:.3f} ES "
      f"contracts; ES initial margin ASSUMED ${ES_MARGIN_ASSUMED:,.0f}/contract [ASSUMED, "
      f"MODELED -- not verified today] -> ~${n_leg*ES_MARGIN_ASSUMED:,.0f} incremental margin. "
      f"PRACTICAL MINIMUM: fractional ES is not tradable; nearest implementation is "
      f"{max(1, round(10*n_leg))} MES (MES = 1/10 ES; MES costs per $-vol are WORSE and are NOT "
      f"modeled here). The frozen series is a 37-trade/4yr engine -- execution granularity, not "
      f"capital, is the binding constraint.")

    # ---------------------------------------------------------------- G3: decision rule
    P("\n[G3] PREREGISTERED DECISION RULE -- applied mechanically")
    dc = cells[(DEC["kvar"], DEC["lam"], DEC["s"])]
    a_ok = bool(dc["marg_sh"] > 0.0)
    b_dd = bool(dc["dd_ratio"] <= 1.05)
    b_cd = bool(dc["cdar_ratio"] <= 1.05)
    b_ok = bool(b_dd and b_cd)
    decision = "CLASS-P ADMISSIBLE-LEAD" if (a_ok and b_ok) else "CLOSED-PORTFOLIO-INERT"
    P(f"  cell: s=0.5, lambda=0.5, causal k")
    P(f"  (a) marginal weekly-vol Sharpe = {dc['marg_sh']:+.4f} > 0 ?  {a_ok}")
    P(f"  (b) book maxDD ${dc['maxdd']:,.0f} vs P1 ${ref['maxdd']:,.0f} "
      f"(ratio {dc['dd_ratio']:.4f} <= 1.05 ? {b_dd});  book CDaR5 ${dc['cdar5']:,.0f} vs "
      f"P1 ${ref['cdar5']:,.0f} (ratio {dc['cdar_ratio']:.4f} <= 1.05 ? {b_cd})  -> {b_ok}")
    P(f"  DECISION: {decision}")
    if decision == "CLASS-P ADMISSIBLE-LEAD":
        P("  (licenses ONLY the next stage: dedicated Class-P engine construction + skeptic + "
          "cost stress on ES execution. NEVER promotion, NEVER deploy.)")
    else:
        P("  (the shrunk ES MR leg does not carry positive economic value to P1 under the "
          "preregistered sizing; the portfolio question is CLOSED. G00063's FAIL stands.)")
    g3 = True   # the rule was applied mechanically; the outcome is the classification above

    # ---------------------------------------------------------------- gate table
    gl = []
    gl.append("=" * 112)
    gl.append("G3_ESMR_PORTFOLIO_20260906  trial G00066  family GENESIS3_DECISION -- "
              "PROGRAM-PRINTED GATE TABLE")
    gl.append("shrunk portfolio contribution of frozen ES MR (W2B G00063 object) to P1 | "
              "DISCOVERY_CONSUMED | NO deploy")
    gl.append("=" * 112)
    gl.append(f"{'gate':<6}{'spec':<58}{'observed':<40}{'verdict':>8}")

    def grow(g, spec, obs, ok):
        gl.append(f"{g:<6}{spec:<58}{str(obs)[:38]:<40}{'PASS' if ok else 'FAIL':>8}")

    grow("G0", "sha256 match + seal + rho reproduction within +-0.005",
         f"sha ok; rho {rho:+.4f} vs {RHO_REC:+.4f} (d={abs(rho-RHO_REC):.5f})", g0)
    grow("G1", "full lambda x s marginal-economics table printed",
         f"{n_printed}/{n_expected} cells, both k variants", g1)
    grow("G2", "s* stated in words AND computed two agreeing ways",
         f"s* = {sstar_txt}; agree={agree}", g2)
    grow("G3", "decision rule applied mechanically at s=.5,lam=.5,causal",
         f"(a) margSh {dc['marg_sh']:+.4f}>0:{a_ok} (b) tails:{b_ok}", g3)
    gl.append("")
    gl.append(f"decision cell: marginal weekly-vol Sharpe {dc['marg_sh']:+.4f}; maxDD ratio "
              f"{dc['dd_ratio']:.4f}; CDaR5 ratio {dc['cdar_ratio']:.4f} (bar: <=1.05 each)")
    gl.append(f"==> DECISION: {decision}")
    gl.append("G00063's family-corrected statistical FAIL is UNTOUCHED by this run.")
    gl.append("=" * 112)
    gate_table = "\n".join(gl) + "\n"
    P("\n" + gate_table)
    with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
        f.write(gate_table)

    # ---------------------------------------------------------------- artifacts
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "marginal_table.csv"), index=False)
    b_dec = book_daily(p1, es, k_causal, 0.5, 0.5, mu_es)
    b_dec_s1 = book_daily(p1, es, k_causal, 0.5, 1.0, mu_es)
    pd.DataFrame({
        "date": dates, "p1_pnl": p1, "esmr_pnl": es, "k_causal": k_causal,
        "leg_decision_cell": leg_dec, "book_decision_cell": b_dec,
        "book_lam05_s100_causal": b_dec_s1,
    }).to_csv(os.path.join(OUT, "portfolio_series.csv"), index=False)
    with open(os.path.join(OUT, "run_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(_LOG) + "\n")
    print(f"\n[done {_t.time()-t0:.0f}s] wrote out/gate_table.txt, out/marginal_table.csv, "
          f"out/portfolio_series.csv, out/run_log.txt")
    return dict(g0=g0, g1=g1, g2=g2, g3=g3, decision=decision, cells=cells, ref=ref,
                rho=rho, k_static=k_static, sstar=sstar_txt)


if __name__ == "__main__":
    main()
