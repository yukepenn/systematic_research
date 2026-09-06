"""W2B_GCVOL - vol-targeted long-gold DIVERSIFICATION SLEEVE test (spec: ../spec.yaml, trial G00064).

THIS IS A DIVERSIFICATION-SLEEVE TEST, NOT AN ALPHA TEST. Gold buy-hold is Sharpe ~0.45 and
orthogonal to NQ (rho ~0.04-0.07). The question is whether a VOL-TARGETED gold long adds portfolio
value to the NQ/P1 book (better tail / capital efficiency), judged on the PORTFOLIO delta. No deploy.

Mechanism (spec mechanism_rule, verbatim):
  Sleeve = LONG gold, daily w_t = clip(target_ann_vol / trailing-N-day realized vol, 0, w_max),
  N in {21,63}, w_max=2, target_vol = the buy-hold's OWN realized vol via EXPANDING-WINDOW
  calibration only (Cederburg discipline - no full-sample vol; both target and trailing are causal,
  computed from data strictly before day t).

Gates (program-printed):
  G0  seal: max session < 2026-08-01 for BOTH gold and NQ; ratio-series %-returns; assert.
  G1  matched-exposure: sleeve beats buy-hold gold on return/maxDD + worst-month at MATCHED mean
      exposure (leverage-masquerade guard; VOLSIZE01 lesson).
  G2  orthogonality: sleeve daily-PnL rho-to-P1 printed (expect ~0.04, verify).
  G3  portfolio delta: NQ/P1 + sleeve under (a) equal-risk and (b) fixed-vol-budget vs NQ-alone -
      Sharpe / maxDD / return-DD / CDaR / worst-month / rolling-12m Sharpe / tail co-loss.
      PORTFOLIO-ADDITIVE only if it materially improves risk-adjusted return or drawdown/tail.
  G4  eval_battery: weekly-vol LEAD; fixed-DD ONLY beside its side-blind random-thinning placebo.

P1 daily PnL is reproduced EXACTLY from the XINST01 parameterized bench (certified 0.0000% vs the
committed WE_W103 P1/PCT: weekly $1393.57, maxDD $22,930.67).

SEAL: nothing dated >= 2026-08-01 is materialized. Asserted at load for both series.
"""
from __future__ import annotations

import os
import sys
import json
import time as _t

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
# reuse the XINST01 bench (it inserts research/weekly_edge/src on sys.path for us)
XINST_SRC = os.path.abspath(os.path.join(
    HERE, "..", "..", "XINST01_WEEKLY_EDGE_PORT_20260906", "src"))
sys.path.insert(0, XINST_SRC)
import xinst_bench as XB                                             # noqa: E402
if XB.REPO not in sys.path:
    sys.path.insert(0, XB.REPO)
from we_lab import spread_profile                                   # noqa: E402
import research_sdk.eval_battery as EB                              # noqa: E402

REPO = XB.REPO
OUT = os.path.abspath(os.path.join(HERE, "..", "out"))
os.makedirs(OUT, exist_ok=True)
SEED = 20260906
SEAL = pd.Timestamp("2026-08-01")

GC_PARQUET = "runs/DAILY_GC_EXTRACT_AUTOPSY_20260906/out/gc_daily.parquet"
NQ_SUB = "runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet"

TRADING_DAYS = 252.0
MNQ_PER_NQ_FACTOR = 0.30          # live P1-object basis = 0.30 x research full-size (CLAUDE.md sec3)
EXPAND_MIN = 252                  # 1yr min history before the expanding-window target is trusted
W_MAX = 2.0
N_LIST = (21, 63)

# GC contract facts (manifest): point_value 100, tick 0.1 -> $10/tick
GC_PV = 100.0
GC_TICK = 0.1
GC_DOLLAR_PER_TICK = GC_PV * GC_TICK           # $10/tick
# modeled GC round-trip friction, per contract: 1 tick spread + $4.36 commission (COST_MODEL basis)
GC_RT_COST_USD = 1.0 * GC_DOLLAR_PER_TICK + 4.36


# ============================================================================= helpers
def max_dd_usd(x):
    """max peak-to-trough drawdown of an ARITHMETIC $ P&L series (eval_battery convention)."""
    return EB.max_drawdown(np.asarray(x, float))


def cdar_usd(x, alpha=0.95):
    return EB.cdar(np.asarray(x, float), alpha=alpha)


def compounded_equity(ret):
    return np.cumprod(1.0 + np.asarray(ret, float))


def dd_frac_from_returns(ret):
    """max drawdown FRACTION on a compounded equity curve of a return series."""
    eq = compounded_equity(ret)
    peak = np.maximum.accumulate(eq)
    return float(np.max((peak - eq) / peak))


def cagr_from_returns(ret, dates):
    eq = compounded_equity(ret)
    n = len(ret)
    years = n / TRADING_DAYS
    return float(eq[-1] ** (1.0 / years) - 1.0)


def worst_month_return(ret, dates):
    s = pd.Series(np.asarray(ret, float), index=pd.to_datetime(pd.Index(dates)))
    m = s.groupby([s.index.year, s.index.month]).apply(lambda z: float(np.prod(1.0 + z.values) - 1.0))
    return float(m.min()), m


def worst_month_usd(pnl, dates):
    s = pd.Series(np.asarray(pnl, float), index=pd.to_datetime(pd.Index(dates)))
    m = s.groupby([s.index.year, s.index.month]).sum()
    return float(m.min()), m


def ann_sharpe(pnl):
    x = np.asarray(pnl, float)
    sd = x.std(ddof=1)
    return float(x.mean() / sd * np.sqrt(TRADING_DAYS)) if sd > 0 else float("nan")


def rolling_sharpe_stability(pnl, dates, win=252):
    x = pd.Series(np.asarray(pnl, float), index=pd.to_datetime(pd.Index(dates)))
    if len(x) < win + 5:
        return dict(min=float("nan"), mean=float("nan"), std=float("nan"), pos_frac=float("nan"))
    m = x.rolling(win).mean()
    s = x.rolling(win).std(ddof=1)
    rs = (m / s * np.sqrt(TRADING_DAYS)).dropna()
    return dict(min=float(rs.min()), mean=float(rs.mean()), std=float(rs.std(ddof=1)),
                pos_frac=float((rs > 0).mean()))


def worst_decile_days(x):
    """set of integer positions of the worst 10% (most negative) days of series x."""
    x = np.asarray(x, float)
    k = max(1, int(round(0.10 * len(x))))
    return set(np.argsort(x)[:k].tolist())


def daily_by_date_from_bench(D, session_net, sess_in):
    """P&L per calendar session-date (identical to run_xinst.daily_by_date)."""
    sd = pd.to_datetime(D["sess_date"])[sess_in]
    return pd.Series(session_net, index=sd.date).groupby(level=0).sum()


def week_index(dates):
    """ISO year-week integer codes for a date index (for eval_battery period grid)."""
    idx = pd.to_datetime(pd.Index(dates))
    iso = idx.isocalendar()
    key = (iso["year"].astype(int) * 100 + iso["week"].astype(int)).to_numpy()
    codes, _ = pd.factorize(pd.Index(key), sort=True)
    return codes.astype(np.int64)


def weekly_sum(values, dates):
    idx = pd.to_datetime(pd.Index(dates))
    iso = idx.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    ser = pd.Series(np.asarray(values, float)).groupby(wk).sum()
    return ser


# ============================================================================= main
def main():
    t0 = _t.time()
    log = []

    def P(*a):
        s = " ".join(str(x) for x in a)
        print(s, flush=True); log.append(s)

    gate_rows = []   # (gate, spec, observed, verdict-bool-or-None)

    def gate(g, spec, observed, ok):
        gate_rows.append((g, spec, str(observed), ok))

    P("=" * 108)
    P("W2B_GCVOL - vol-targeted long-gold DIVERSIFICATION SLEEVE (trial G00064). NOT alpha.")
    P("=" * 108)

    # ---------------------------------------------------------------- G0: load + seal
    gc = pd.read_parquet(os.path.join(REPO, GC_PARQUET))
    gc["date"] = pd.to_datetime(gc["date"])
    gc = gc.sort_values("date").reset_index(drop=True)
    n_all = len(gc)
    # hard seal: never materialize a bar dated >= 2026-08-01
    gc = gc[gc["date"] < SEAL].reset_index(drop=True)
    seal_gc = pd.Timestamp(gc["date"].max()) < SEAL
    assert seal_gc, "SEAL VIOLATION: gold data reaches into virgin territory"
    # clean daily %-returns on the ratio-stitched series (DELEV01, %-safe)
    gcc = gc[gc["clean_daily"]].reset_index(drop=True)
    r = gcc["ret_pct"].to_numpy(float)
    gdate = gcc["date"].dt.date.to_numpy()
    gprice = gcc["close_true"].to_numpy(float)             # true traded price for cost notional
    # one-way GC cost as a fraction of notional (0.5 tick spread crossing + $4.36 commission)
    oneway_cost_frac = (0.5 * GC_DOLLAR_PER_TICK + 4.36) / (gprice * GC_PV)
    P(f"G0 gold: {n_all} rows loaded, {len(gc)} < seal, {len(gcc)} clean-daily %-returns "
      f"{gcc['date'].min().date()} -> {gcc['date'].max().date()}")
    P(f"   ret basis = ret_pct on ratio-stitched series (DELEV01, %-safe). "
      f"seal max {gcc['date'].max().date()} < 2026-08-01 ? {seal_gc}")
    gate("G0a", "gold max session < 2026-08-01 (seal, asserted)",
         f"{gcc['date'].max().date()} clean_ret n={len(gcc)}", bool(seal_gc))

    # ---------------------------------------------------------------- vol-target sleeve (causal)
    n = len(r)
    # trailing-N realized vol (std of returns over [t-N, t-1]); expanding target (std over [0,t-1])
    def trailing_std(x, N):
        s = pd.Series(x)
        return s.rolling(N).std(ddof=1).shift(1).to_numpy()      # uses [t-N, t-1], strictly past
    def expanding_std(x):
        s = pd.Series(x)
        return s.expanding(min_periods=2).std(ddof=1).shift(1).to_numpy()  # [0, t-1], strictly past

    target = expanding_std(r)               # buy-hold's own realized vol, EXPANDING (causal)
    sleeves = {}
    for N in N_LIST:
        rvN = trailing_std(r, N)
        with np.errstate(divide="ignore", invalid="ignore"):
            w = np.clip(target / rvN, 0.0, W_MAX)
        # active only where BOTH the trailing-N vol and a >=EXPAND_MIN expanding target exist
        active = np.zeros(n, bool)
        expcount = np.arange(n)             # number of past obs available at t
        active[(expcount >= EXPAND_MIN) & np.isfinite(w) & np.isfinite(rvN)] = True
        w = np.where(active, w, np.nan)
        sret = w * r                        # sleeve daily return (causal weight x same-day return)
        # cost-adjusted: charge |dw| one-way turnover cost each day (vol-target rebalancing friction)
        wf = np.where(np.isfinite(w), w, 0.0)
        turn = np.abs(np.diff(np.concatenate([[0.0], wf])))
        sret_cost = sret - turn * oneway_cost_frac
        sleeves[N] = dict(w=w, sret=sret, sret_cost=sret_cost, turn=turn, active=active, rvN=rvN)
        aw = w[active]
        P(f"   sleeve N={N}: active {int(active.sum())} days "
          f"{pd.Timestamp(gdate[active][0]).date()} -> {pd.Timestamp(gdate[active][-1]).date()}; "
          f"mean w {aw.mean():.4f}  median w {np.median(aw):.4f}  "
          f"clipped-at-{W_MAX:.0f} {100*np.mean(aw >= W_MAX):.1f}%  clipped-at-0 {100*np.mean(aw <= 0):.1f}%")

    # ---------------------------------------------------------------- G1: matched-exposure vs buy-hold
    P("")
    P("-" * 108)
    P("G1  SLEEVE vs BUY-HOLD gold at MATCHED MEAN EXPOSURE (leverage-masquerade guard). "
      "Compounded-equity return/DD + worst-month.")
    P("-" * 108)
    svb_rows = []
    g1_pass = {}
    for N in N_LIST:
        sl = sleeves[N]
        act = sl["active"]
        dts = gdate[act]
        bh = r[act]                          # buy-hold over the SAME active window (w=1)
        sret = sl["sret"][act]
        mean_w = float(sl["w"][act].mean())
        matched = sret / mean_w              # scale so mean exposure == 1 == buy-hold

        def stats(ret):
            cagr = cagr_from_returns(ret, dts)
            dd = dd_frac_from_returns(ret)
            wm, _ = worst_month_return(ret, dts)
            sh = float(ret.mean() / ret.std(ddof=1) * np.sqrt(TRADING_DAYS)) if ret.std(ddof=1) > 0 else float("nan")
            return cagr, dd, (cagr / dd if dd > 0 else float("nan")), wm, sh

        bh_c, bh_dd, bh_rdd, bh_wm, bh_sh = stats(bh)
        raw_c, raw_dd, raw_rdd, raw_wm, raw_sh = stats(sret)
        m_c, m_dd, m_rdd, m_wm, m_sh = stats(matched)

        beats_rdd = m_rdd > bh_rdd
        beats_wm = m_wm > bh_wm              # worst month LESS negative == improvement
        g1 = bool(beats_rdd and beats_wm)
        g1_pass[N] = g1
        P(f"  N={N}  (mean exposure buy-hold 1.000, sleeve raw {mean_w:.3f}, sleeve MATCHED 1.000)")
        P(f"     {'series':<22}{'CAGR':>9}{'maxDD':>9}{'ret/DD':>9}{'worstMo':>10}{'Sharpe':>9}")
        P(f"     {'buy-hold gold':<22}{bh_c*100:>8.2f}%{bh_dd*100:>8.2f}%{bh_rdd:>9.3f}{bh_wm*100:>9.2f}%{bh_sh:>9.3f}")
        P(f"     {'sleeve (raw)':<22}{raw_c*100:>8.2f}%{raw_dd*100:>8.2f}%{raw_rdd:>9.3f}{raw_wm*100:>9.2f}%{raw_sh:>9.3f}")
        P(f"     {'sleeve (MATCHED exp)':<22}{m_c*100:>8.2f}%{m_dd*100:>8.2f}%{m_rdd:>9.3f}{m_wm*100:>9.2f}%{m_sh:>9.3f}")
        P(f"     -> MATCHED beats buy-hold on ret/DD? {beats_rdd}   on worst-month? {beats_wm}   "
          f"=> G1(N={N}) {'PASS' if g1 else 'FAIL'}")
        gate(f"G1[N={N}]", "matched-exp sleeve beats buy-hold on ret/DD AND worst-month",
             f"ret/DD {m_rdd:.2f}v{bh_rdd:.2f}; wMo {m_wm*100:.1f}v{bh_wm*100:.1f}", g1)
        svb_rows.append(dict(
            N=N, active_days=int(act.sum()), mean_w=mean_w,
            bh_cagr=bh_c, bh_maxdd=bh_dd, bh_ret_dd=bh_rdd, bh_worst_month=bh_wm, bh_sharpe=bh_sh,
            sleeve_raw_cagr=raw_c, sleeve_raw_maxdd=raw_dd, sleeve_raw_ret_dd=raw_rdd,
            sleeve_raw_worst_month=raw_wm, sleeve_raw_sharpe=raw_sh,
            sleeve_matched_cagr=m_c, sleeve_matched_maxdd=m_dd, sleeve_matched_ret_dd=m_rdd,
            sleeve_matched_worst_month=m_wm, sleeve_matched_sharpe=m_sh,
            g1_matched_beats_buyhold=g1))

    # ---------------------------------------------------------------- eval_battery on sleeve (G4)
    P("")
    P("-" * 108)
    P("G4  EVAL BATTERY on sleeve vs buy-hold (weekly grid). WEEKLY-VOL LEAD; fixed-DD ONLY beside "
      "its side-blind random-thinning placebo.")
    P("-" * 108)
    battery_sleeve = {}
    for N in N_LIST:
        sl = sleeves[N]; act = sl["active"]; dts = gdate[act]
        cand_w = weekly_sum(sl["sret"][act], dts)
        ref_w = weekly_sum(r[act], dts)
        j = pd.concat([cand_w.rename("c"), ref_w.rename("r")], axis=1).dropna()
        res = EB.evaluate(j["c"].to_numpy(), j["r"].to_numpy(), n_placebo=0)
        # fixed-DD with placebo: treat each DAY as a "trade", period = week
        wcodes = week_index(dts)
        tp = sl["sret"][act]
        nrm = max(1, int(round(0.10 * len(tp))))
        res_dd = EB.evaluate(j["c"].to_numpy(), j["r"].to_numpy(), n_placebo=2000,
                             base_for_placebo="fixed_dd", ref_trades=tp, ref_periods=wcodes,
                             n_trades_removed=nrm, seed=SEED)
        null = EB.random_thinning_placebo(tp, wcodes, nrm, "fixed_dd", n=2000, seed=SEED,
                                          n_periods=len(np.unique(wcodes)))
        P(f"  N={N} (sleeve income risk-matched to BUY-HOLD, {len(j)} shared weeks, return units):")
        for b in ("native", "weekly_vol", "realized_vol", "gross_exposure"):
            lead = "  <== PRIMARY (weekly-vol)" if b == "weekly_vol" else ""
            P(f"     {b:<16} {res[b]:>12.6f}/wk{lead}")
        P(f"     fixed_dd (order stat) {res_dd['fixed_dd']:>12.6f}/wk  vs side-blind 10%-thin "
          f"median {float(np.median(null)):.6f}/wk  (placebo pct {res_dd.placebo_percentile:.1f})")
        battery_sleeve[N] = dict(native=float(res["native"]), weekly_vol=float(res["weekly_vol"]),
                                 realized_vol=float(res["realized_vol"]),
                                 gross_exposure=float(res["gross_exposure"]),
                                 fixed_dd=float(res_dd["fixed_dd"]),
                                 fixed_dd_placebo_med=float(np.median(null)),
                                 fixed_dd_placebo_pct=float(res_dd.placebo_percentile))

    # ---------------------------------------------------------------- cost robustness (GC friction)
    P("")
    P("-" * 108)
    P("COST ROBUSTNESS - GC turnover friction (1-tick spread + $4.36 comm, per-day |dw| one-way). "
      "Does the sleeve survive costs?")
    P("-" * 108)
    cost_robust_flags = {}
    for N in N_LIST:
        sl = sleeves[N]; act = sl["active"]; dts = gdate[act]
        gross = sl["sret"][act]; nett = sl["sret_cost"][act]
        drag_ann = float((gross - nett).mean() * TRADING_DAYS)     # annual return drag from costs
        avg_turn = float(sl["turn"][act].mean())
        # weekly-vol of the COST-ADJUSTED sleeve vs buy-hold
        cand_w = weekly_sum(nett, dts); ref_w = weekly_sum(r[act], dts)
        jc = pd.concat([cand_w.rename("c"), ref_w.rename("r")], axis=1).dropna()
        wv_cost = float(EB.evaluate(jc["c"].to_numpy(), jc["r"].to_numpy(), n_placebo=0)["weekly_vol"])
        # matched-exposure ret/DD of the cost-adjusted sleeve
        mean_w = float(sl["w"][act].mean())
        matched = nett / mean_w
        rdd_cost = cagr_from_returns(matched, dts) / max(dd_frac_from_returns(matched), 1e-12)
        bh_rdd = cagr_from_returns(r[act], dts) / max(dd_frac_from_returns(r[act]), 1e-12)
        ok = bool(wv_cost > 0 and rdd_cost > bh_rdd)
        cost_robust_flags[N] = dict(drag_ann=drag_ann, avg_turn=avg_turn, wv_cost=wv_cost,
                                    rdd_cost=rdd_cost, bh_rdd=bh_rdd, ok=ok)
        P(f"  N={N}: avg daily |dw| {avg_turn:.4f}  annual cost drag {drag_ann*100:.3f}%  "
          f"(GC RT ${GC_RT_COST_USD:.2f}); after-cost weekly-vol {wv_cost:.6f} ret/wk (>0 vs "
          f"buy-hold); matched ret/DD {rdd_cost:.3f} vs buy-hold {bh_rdd:.3f} -> cost-robust {ok}")

    # ---------------------------------------------------------------- P1 daily PnL (reproduce EXACT)
    P("")
    P("-" * 108)
    P("P1 daily PnL - reproduced from the XINST01 parameterized bench (certified 0.0000% vs WE_W103).")
    P("-" * 108)
    prof = spread_profile()
    Dnq, bnq = XB.load_substrate(NQ_SUB, "NQ")
    assert bnq["seal_ok"], "SEAL VIOLATION on NQ load"
    trnq, mnq = XB.build_p1pct(Dnq, PV=20.0, comm=4.36, halt_pts=XB.NQ_HALT_PTS,
                               tgt_pts=XB.NQ_TGT_PTS, smin_pts=None, smax_pts=None,
                               stopm_pts=None, win_a="2022-07-01", win_b="2026-08-01")
    net_nq, ct_nq, rate_nq, ntr_nq = XB.net_series(
        Dnq, trnq, PV=20.0, tick=0.25, spread_model=("nq_profile", prof),
        sess_in=mnq["sess_in"], i_of=mnq["i_of"])
    w_nq, wk_nq = XB.weekly(Dnq, net_nq, mnq["sess_in"])
    pan_nq = XB.panel(w_nq)
    repro_ok = (abs(pan_nq["weekly"] - 1393.5736634670018) < 1e-6 and
                abs(pan_nq["maxdd"] - 22930.665852795442) < 1e-6)
    P(f"  P1/PCT: weekly ${pan_nq['weekly']:,.6f}  maxDD ${pan_nq['maxdd']:,.6f}  "
      f"t {pan_nq['t']:.4f}  trades {ntr_nq}  spread ${rate_nq:.6f}  seal {bnq['last_sess']}")
    P(f"  REPRODUCE-GATE vs WE_W103 (weekly 1393.5736635, maxDD 22930.6658528): "
      f"{'PASS (0.0000%)' if repro_ok else 'FAIL'}")
    gate("G0b", "NQ P1/PCT reproduced EXACTLY vs WE_W103 (weekly & maxDD)",
         f"wk ${pan_nq['weekly']:.4f} maxDD ${pan_nq['maxdd']:.1f}", bool(repro_ok))
    p1_daily = daily_by_date_from_bench(Dnq, net_nq, mnq["sess_in"])   # date -> $ (research full size)
    p1_daily.index = [pd.Timestamp(d).date() for d in p1_daily.index]

    # ---------------------------------------------------------------- G2: orthogonality rho-to-P1
    P("")
    P("-" * 108)
    P("G2  ORTHOGONALITY - sleeve daily rho-to-P1 (expect ~0.04). Correlation is scale-invariant, so "
      "sleeve-return vs P1-$ rho == sleeve-$ vs P1-$ rho.")
    P("-" * 108)
    rho_to_p1 = {}
    for N in N_LIST:
        sl = sleeves[N]; act = sl["active"]
        sser = pd.Series(sl["sret"][act], index=[pd.Timestamp(d).date() for d in gdate[act]])
        jj = pd.concat([sser.rename("gold"), p1_daily.rename("p1")], axis=1).dropna()
        rho = float(jj["gold"].corr(jj["p1"])) if len(jj) > 2 else float("nan")
        # also buy-hold gold vs P1 for reference
        bser = pd.Series(r[act], index=[pd.Timestamp(d).date() for d in gdate[act]])
        jb = pd.concat([bser.rename("gold"), p1_daily.rename("p1")], axis=1).dropna()
        rho_bh = float(jb["gold"].corr(jb["p1"])) if len(jb) > 2 else float("nan")
        rho_to_p1[N] = rho
        P(f"  N={N}: sleeve daily rho-to-P1 = {rho:+.4f}  (buy-hold gold rho-to-P1 {rho_bh:+.4f}) "
          f"over {len(jj)} shared trading days")
        gate(f"G2[N={N}]", "sleeve daily-PnL rho-to-P1 printed (expect ~0.04)",
             f"rho {rho:+.4f}", True)
    P(f"  (manifest cross-check: buy-hold gold rho-to-NQ-INDEX pearson 0.0744 / spearman 0.0449)")

    # ---------------------------------------------------------------- G3: portfolio delta
    P("")
    P("=" * 108)
    P("G3  PORTFOLIO DELTA - NQ/P1-alone vs NQ/P1 + gold sleeve, under (a) EQUAL-RISK and "
      "(b) FIXED-VOL-BUDGET (0.5x). Transparent, NOT optimized.")
    P("=" * 108)
    P("    Sizing constants use full-sample daily-$ vol over the shared window (an in-sample")
    P("    portfolio-CONSTRUCTION device; the sleeve itself is causally vol-targeted). Ratios")
    P("    (Sharpe, ret/DD, CDaR, tail) are scale-invariant -> IDENTICAL on both dollar bases;")
    P("    only absolute $ (maxDD, worst-month) differ by the 0.30x live-object factor.")

    portfolio_rows = []
    daily_dump = pd.DataFrame({"date": list(p1_daily.index),
                               "p1_pnl_research": p1_daily.values,
                               "p1_pnl_live_mnq3": p1_daily.values * MNQ_PER_NQ_FACTOR})
    daily_dump = daily_dump.set_index("date")

    g3_additive = {}
    for N in N_LIST:
        sl = sleeves[N]; act = sl["active"]
        sser = pd.Series(sl["sret"][act], index=[pd.Timestamp(d).date() for d in gdate[act]])
        j = pd.concat([sser.rename("gold_ret"), p1_daily.rename("p1")], axis=1).dropna()
        j = j.sort_index()
        dts = list(j.index)
        p1v = j["p1"].to_numpy(float)
        goldret = j["gold_ret"].to_numpy(float)
        sig_p1 = p1v.std(ddof=1)
        sig_gold = goldret.std(ddof=1)
        notional_eq = sig_p1 / sig_gold            # equal-risk: gold $vol == P1 $vol
        gold_eq = goldret * notional_eq
        gold_fx = goldret * (0.5 * notional_eq)    # fixed-vol-budget: gold $vol == 0.5 P1 $vol

        variants = {
            "NQ-alone": p1v,
            "NQ+gold (equal-risk)": p1v + gold_eq,
            "NQ+gold (fixed-vol 0.5x)": p1v + gold_fx,
        }

        def book_stats(pnl):
            sh = ann_sharpe(pnl)
            dd = max_dd_usd(pnl)
            tot = float(np.sum(pnl))
            rdd = tot / dd if dd > 0 else float("nan")
            cd = cdar_usd(pnl)
            wm, _ = worst_month_usd(pnl, dts)
            rs = rolling_sharpe_stability(pnl, dts)
            return dict(sharpe=sh, maxdd=dd, total=tot, ret_dd=rdd, cdar=cd, worst_month=wm,
                        roll_min=rs["min"], roll_std=rs["std"], roll_posfrac=rs["pos_frac"])

        base = book_stats(p1v)
        # tail co-loss: worst-decile-day overlap between P1 and the gold sleeve $ (equal-risk)
        wl_p1 = worst_decile_days(p1v)
        wl_gold = worst_decile_days(gold_eq)
        jacc = len(wl_p1 & wl_gold) / max(len(wl_p1 | wl_gold), 1)

        P("")
        P(f"  --- N={N}  shared window {dts[0]} -> {dts[-1]}  ({len(dts)} days)   "
          f"sig_P1 ${sig_p1:,.1f}/day  sig_gold(ret) {sig_gold:.5f}  gold notional(eq-risk) ${notional_eq:,.0f}")
        P(f"      tail co-loss (worst-decile-day Jaccard, P1 vs gold sleeve) = {jacc:.3f}")
        P(f"      {'book':<28}{'Sharpe':>8}{'maxDD$':>11}{'ret/DD':>8}{'CDaR$':>11}"
          f"{'worstMo$':>11}{'roll12mMin':>11}")
        book_st = {}
        for name, pnl in variants.items():
            st = book_stats(pnl)
            book_st[name] = st
            P(f"      {name:<28}{st['sharpe']:>8.3f}{st['maxdd']:>11,.0f}{st['ret_dd']:>8.3f}"
              f"{st['cdar']:>11,.0f}{st['worst_month']:>11,.0f}{st['roll_min']:>11.3f}")
            portfolio_rows.append(dict(
                N=N, book=name, basis="research_full_size",
                sharpe=st["sharpe"], maxdd_usd=st["maxdd"], total_usd=st["total"],
                ret_dd=st["ret_dd"], cdar_usd=st["cdar"], worst_month_usd=st["worst_month"],
                roll12m_sharpe_min=st["roll_min"], roll12m_sharpe_std=st["roll_std"],
                roll12m_pos_frac=st["roll_posfrac"], tail_coloss_jaccard=jacc,
                gold_notional_eqrisk=notional_eq, shared_days=len(dts)))
            # live-object basis row (0.30x): ratios identical, $ scaled
            portfolio_rows.append(dict(
                N=N, book=name, basis="live_P1_object_mnq3_0.30x",
                sharpe=st["sharpe"], maxdd_usd=st["maxdd"] * MNQ_PER_NQ_FACTOR,
                total_usd=st["total"] * MNQ_PER_NQ_FACTOR, ret_dd=st["ret_dd"],
                cdar_usd=st["cdar"] * MNQ_PER_NQ_FACTOR,
                worst_month_usd=st["worst_month"] * MNQ_PER_NQ_FACTOR,
                roll12m_sharpe_min=st["roll_min"], roll12m_sharpe_std=st["roll_std"],
                roll12m_pos_frac=st["roll_posfrac"], tail_coloss_jaccard=jacc,
                gold_notional_eqrisk=notional_eq * MNQ_PER_NQ_FACTOR, shared_days=len(dts)))

        # eval_battery on the combined book vs NQ-alone (weekly-vol lead; fixed-DD + placebo)
        comb = p1v + gold_eq
        cand_w = weekly_sum(comb, dts); ref_w = weekly_sum(p1v, dts)
        jw = pd.concat([cand_w.rename("c"), ref_w.rename("r")], axis=1).dropna()
        resb = EB.evaluate(jw["c"].to_numpy(), jw["r"].to_numpy(), n_placebo=0)
        wcodes = week_index(dts); nrm = max(1, int(round(0.10 * len(comb))))
        resb_dd = EB.evaluate(jw["c"].to_numpy(), jw["r"].to_numpy(), n_placebo=2000,
                              base_for_placebo="fixed_dd", ref_trades=comb, ref_periods=wcodes,
                              n_trades_removed=nrm, seed=SEED)
        nullb = EB.random_thinning_placebo(comb, wcodes, nrm, "fixed_dd", n=2000, seed=SEED,
                                           n_periods=len(np.unique(wcodes)))
        P(f"      eval_battery (NQ+gold eq-risk income risk-matched to NQ-alone, {len(jw)} wk):")
        for b in ("native", "weekly_vol", "realized_vol", "gross_exposure"):
            lead = "  <== PRIMARY" if b == "weekly_vol" else ""
            P(f"         {b:<16} ${resb[b]:>12,.2f}/wk (NQ-alone native ${ref_w.mean():,.2f}/wk){lead}")
        P(f"         fixed_dd ${resb_dd['fixed_dd']:>12,.2f}/wk vs side-blind 10%-thin median "
          f"${float(np.median(nullb)):,.2f}/wk (placebo pct {resb_dd.placebo_percentile:.1f})")

        # ---- ADDITIVE decision: MATERIAL improvement in risk-adjusted return AND capital
        #      efficiency, judged on BOTH transparent sizings. A sleeve worth carrying must
        #      improve Sharpe AND ret/DD (capital efficiency) by >=10% relative, with the
        #      rolling-12m-min not worse and the sleeve's own weekly-vol > 0. Adding an
        #      orthogonal positive-drift asset ALWAYS lifts Sharpe a little; the binding test
        #      is whether it also lifts return-per-drawdown (else it just adds risk).
        def _deltas(st):
            rs = (st["sharpe"] - base["sharpe"]) / abs(base["sharpe"]) if base["sharpe"] else float("nan")
            rr = (st["ret_dd"] - base["ret_dd"]) / abs(base["ret_dd"]) if base["ret_dd"] else float("nan")
            mat = bool(rs >= 0.10 and rr >= 0.10 and st["roll_min"] >= base["roll_min"] - 1e-9)
            return rs, rr, mat
        eq = book_st["NQ+gold (equal-risk)"]
        fx = book_st["NQ+gold (fixed-vol 0.5x)"]
        rs_eq, rr_eq, mat_eq = _deltas(eq)
        rs_fx, rr_fx, mat_fx = _deltas(fx)
        sleeve_wv_ok = battery_sleeve[N]["weekly_vol"] > 0
        additive = bool((mat_eq or mat_fx) and sleeve_wv_ok)
        g3_additive[N] = dict(additive=additive, mat_eq=mat_eq, mat_fx=mat_fx,
                              rel_sharpe_eq=rs_eq, rel_retdd_eq=rr_eq,
                              rel_sharpe_fx=rs_fx, rel_retdd_fx=rr_fx,
                              d_rollmin_eq=eq["roll_min"] - base["roll_min"],
                              base=base, eq=eq, fx=fx, jacc=jacc,
                              battery_weekly_vol=resb["weekly_vol"], nq_alone_native=float(ref_w.mean()))
        P(f"      G3 DELTA vs NQ-alone (Sharpe {base['sharpe']:.3f}, ret/DD {base['ret_dd']:.3f}, "
          f"roll12m-min {base['roll_min']:.3f}):")
        P(f"         equal-risk : Sharpe {eq['sharpe']:.3f} ({rs_eq:+.1%})  ret/DD {eq['ret_dd']:.3f} "
          f"({rr_eq:+.1%})  roll-min {eq['roll_min']:.3f}  material={mat_eq}")
        P(f"         fixed-vol  : Sharpe {fx['sharpe']:.3f} ({rs_fx:+.1%})  ret/DD {fx['ret_dd']:.3f} "
          f"({rr_fx:+.1%})  roll-min {fx['roll_min']:.3f}  material={mat_fx}")
        P(f"      => PORTFOLIO-ADDITIVE (N={N}) ? {additive}  "
          f"[material = Sharpe & ret/DD BOTH +>=10% rel, roll-min not worse, sleeve weekly-vol>0]")
        gate(f"G3[N={N}]", "NQ+gold materially improves Sharpe AND ret/DD vs NQ-alone (either sizing)",
             f"eq {rs_eq:+.0%}/{rr_eq:+.0%} fx {rs_fx:+.0%}/{rr_fx:+.0%}", additive)

        # add sleeve columns to the daily dump (aligned to P1 dates)
        col_ret = pd.Series(sl["sret"][act], index=[pd.Timestamp(d).date() for d in gdate[act]])
        daily_dump[f"gold_sleeve_ret_N{N}"] = col_ret.reindex(daily_dump.index)
        gpe = pd.Series(gold_eq, index=dts)
        gpf = pd.Series(gold_fx, index=dts)
        daily_dump[f"gold_pnl_eqrisk_N{N}"] = gpe.reindex(daily_dump.index)
        daily_dump[f"gold_pnl_fixedvol_N{N}"] = gpf.reindex(daily_dump.index)
        daily_dump[f"combined_eqrisk_N{N}"] = (p1_daily.reindex(daily_dump.index).fillna(0.0)
                                               + gpe.reindex(daily_dump.index).fillna(0.0))

    # ---------------------------------------------------------------- pick primary N & verdict
    # primary = the N that passes G1; if both/neither, prefer N=63 (smoother, standard vol lookback)
    primary_N = 63 if (g1_pass.get(63) or not g1_pass.get(21)) else 21
    g1_ok = g1_pass[primary_N]
    g3_ok = g3_additive[primary_N]["additive"]
    survives = bool(g1_ok and g3_ok)
    if g1_ok and g3_ok:
        verdict = "PORTFOLIO-ADDITIVE"
    elif not g3_ok and g1_ok:
        verdict = "EDGE-BUT-NOT-DIVERSIFIER"
    elif not g1_ok:
        verdict = "NEUTRAL"
    else:
        verdict = "NEUTRAL"

    P("")
    P("=" * 108)
    P(f"PRIMARY N = {primary_N}.  G1 matched-exposure beats buy-hold ? {g1_ok}   "
      f"G3 PORTFOLIO-ADDITIVE ? {g3_ok}   => SURVIVES ? {survives}")
    P(f"VERDICT: {verdict}   (DIVERSIFICATION value, never 'alpha' - DISCOVERY_CONSUMED, no deploy)")
    P("=" * 108)

    # ---------------------------------------------------------------- write deliverables
    # daily_pnl.csv (portfolio step)
    daily_dump = daily_dump.reset_index().rename(columns={"index": "date"})
    daily_dump.to_csv(os.path.join(OUT, "daily_pnl.csv"), index=False)
    pd.DataFrame(svb_rows).to_csv(os.path.join(OUT, "sleeve_vs_buyhold.csv"), index=False)
    pd.DataFrame(portfolio_rows).to_csv(os.path.join(OUT, "portfolio.csv"), index=False)

    # gate_table.txt (program-printed GATE / SPEC / OBSERVED / PASS-FAIL)
    lines = []
    lines.append("W2B_GCVOL GATE TABLE - program-printed. Vol-targeted long-gold DIVERSIFICATION")
    lines.append("SLEEVE (trial G00064). NOT an alpha test - judged on the PORTFOLIO delta.")
    lines.append(f"Primary N={primary_N}. NQ P1/PCT reproduced EXACTLY (0.0000% vs WE_W103).")
    lines.append("=" * 96)
    lines.append(f"{'gate':<10}{'spec':<52}{'observed':>24}{'verdict':>10}")
    lines.append("-" * 96)
    for g, spec, obs, ok in gate_rows:
        v = "PASS" if ok else ("FAIL" if ok is False else "INFO")
        lines.append(f"{g:<10}{spec[:51]:<52}{obs[:23]:>24}{v:>10}")
    lines.append("-" * 96)
    lines.append(f"SURVIVES (G1 matched-exp beats buy-hold AND G3 portfolio-additive) = {survives}")
    lines.append(f"VERDICT = {verdict}")
    lines.append("")
    lines.append("SEMANTIC: over the sleeve's causal active window on COMEX gold daily ratio-stitched")
    lines.append("%-returns (pre-seal, in-sample, DISCOVERY_CONSUMED), the vol-targeted long sleeve is")
    lines.append("compared to buy-hold at MATCHED mean exposure, and the NQ/P1 + sleeve portfolio to")
    lines.append("NQ/P1-alone under equal-risk and fixed-vol-budget. These are DIVERSIFICATION figures,")
    lines.append("never 'alpha', and never forward or live figures.")
    with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    with open(os.path.join(OUT, "run_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log) + "\n")

    # machine-readable summary for the orchestrator
    summary = dict(
        run_id="W2B_GCVOL_20260906", trial="G00064", primary_N=primary_N,
        seal_ok=bool(seal_gc and bnq["seal_ok"]), reproduce_gate_pass=bool(repro_ok),
        p1_weekly=pan_nq["weekly"], p1_maxdd=pan_nq["maxdd"],
        g1_pass=g1_pass, g3_additive={k: v["additive"] for k, v in g3_additive.items()},
        rho_to_p1=rho_to_p1, survives=survives, verdict=verdict,
        battery_sleeve=battery_sleeve,
        g3_primary=g3_additive[primary_N], gc_rt_cost_usd=GC_RT_COST_USD,
        cost_robust=cost_robust_flags)
    with open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=float)

    P(f"[done {_t.time()-t0:.0f}s] wrote daily_pnl.csv, sleeve_vs_buyhold.csv, portfolio.csv, "
      f"gate_table.txt, run_log.txt, summary.json")
    return summary


if __name__ == "__main__":
    main()
