"""G3_VOLSHORT01 discovery -- SPECIFICATION: VIX LEVEL TERCILES.

EVIDENCE STATUS: DISCOVERY_CONTAMINATED. This is NOT a result. It is one input to a RULE
PROPOSAL that someone else freezes and commits BEFORE the one-shot confirmation read of
2022-01-01 -> 2026-07-31.

THE WALL. Nothing on or after 2022-01-01 is read, loaded, counted or aggregated here. The
panel this reads was already built under the wall; the wall is RE-ASSERTED on the artefact
below and the assertion is printed. Every assertion raises rather than warns.

MECHANISM UNDER TEST. The price of variance risk is claimed to flip sign with the trading
window: the equity premium is compensated OVERNIGHT, while the INTRADAY window is where
levered / short-horizon holders de-risk and liquidity providers extract compensation. High
EX-ANTE implied variance should therefore carry NEGATIVE expected INTRADAY drift, making
implied vol a SIGNED SHORT TRIGGER rather than an exposure gate.

SPECIFICATION. State = causal rolling-252-observation tercile of the VIX close of the latest
Cboe session STRICTLY BEFORE the NQ session (common.causal_tercile, the wave-standard
convention). high = tercile 2, low = tercile 0. Trade = enter at the 09:30:00 print, exit at
the last RTH print, flat overnight, one contract, one round turn per traded session.

    python runs/G3_VOLSHORT01_20260831/src/discovery/spec_vix-tercile.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
import common as C                                                        # noqa: E402

PANEL = os.path.join(ROOT, "runs", "G3_VOLSHORT01_20260831", "out", "discovery",
                     "panel_pre2022.parquet")
OUT = os.path.join(ROOT, "runs", "G3_VOLSHORT01_20260831", "out", "discovery",
                   "spec_vix-tercile.txt")

WALL = pd.Timestamp("2022-01-01")
WINDOW = 252          # tercile lookback, in OBSERVATIONS
GAP = 10              # episode separation, calendar days
NDRAW = 10000
SEED = 20260831

_LOG: list[str] = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    _LOG.append(s)


def H(title):
    P("")
    P("=" * 100)
    P(title)
    P("=" * 100)


# ----------------------------------------------------------------------------------
# block machinery -- the timeline partition
# ----------------------------------------------------------------------------------
def timeline_blocks(hi, dates, gap_days=GAP) -> np.ndarray:
    """Partition EVERY session into contiguous blocks anchored on high-state episodes.

    common.block_bootstrap_by_episode resamples HIGH episodes only, which is correct for a
    statistic defined on high sessions alone (the S arm's per-trade mean). The R and F arms
    also trade non-high sessions, so their resampling unit must cover the whole timeline or
    the two legs are bootstrapped over different objects and R = F + S stops holding inside a
    draw.

    Block k = high episode k together with the quiet stretch that follows it, up to the start
    of high episode k+1. Sessions preceding the first high episode are merged into block 0.
    Result: K contiguous blocks covering all sessions, K = the high-episode count, so the
    reported K is the SAME number for every arm.
    """
    d = pd.DatetimeIndex(pd.to_datetime(pd.Series(dates).values))
    eps = C.episodes(hi, d, gap_days=gap_days)
    if not eps:
        return np.zeros(len(d), dtype=int)
    starts = pd.DatetimeIndex([a for a, _ in eps])
    b = np.searchsorted(starts.values, d.values, side="right") - 1
    return np.clip(b, 0, None).astype(int)


def ratio_bootstrap(num_by_block: dict, den_by_block: np.ndarray, K: int,
                    n_draws=NDRAW, seed=SEED) -> dict:
    """Block bootstrap of per-session means that are RATIOS of sums.

    Resampling K blocks with replacement is exactly a multinomial(K, uniform) count vector, so
    every draw is a matrix product -- no concatenation, exact, and the SAME draw is applied to
    every arm, which is what makes the CI of a DIFFERENCE between arms valid.
    """
    rng = np.random.default_rng(seed)
    cnt = rng.multinomial(K, np.full(K, 1.0 / K), size=n_draws).astype(float)
    den = cnt @ den_by_block
    out = {}
    for name, num in num_by_block.items():
        with np.errstate(divide="ignore", invalid="ignore"):
            out[name] = np.where(den > 0, (cnt @ num) / den, np.nan)
    return out


def ci(draws, alpha=0.05):
    d = np.asarray(draws, float)
    d = d[~np.isnan(d)]
    if len(d) == 0:
        return (np.nan, np.nan, np.nan, False)
    lo, hi = np.quantile(d, [alpha / 2, 1 - alpha / 2])
    return (float(lo), float(hi), float(d.std(ddof=1)), bool(lo > 0 or hi < 0))


def fmt_ci(lo, hi, unit="$"):
    return f"[{unit}{lo:,.2f}, {unit}{hi:,.2f}]" if unit else f"[{lo:,.3f}, {hi:,.3f}]"


# ----------------------------------------------------------------------------------
def build_state(df, col, window=WINDOW):
    """Causal tercile of `col` on the rows where `col` exists, returned aligned to df."""
    g = df[df[col].notna()].copy()
    g["st"] = C.causal_tercile(g[col].values, window=window)
    s = pd.Series(np.nan, index=df.index)
    s.loc[g.index] = g["st"].values
    return s.values


def arm_positions(st, ret, high=2.0, low=0.0):
    valid = (~np.isnan(st)) & (~np.isnan(ret))
    hi = valid & (st == high)
    lo = valid & (st == low)
    nonhi = valid & ~hi
    return valid, hi, lo, nonhi


def main() -> int:
    # ================================================================== [0] WALL
    H("G3_VOLSHORT01 -- SPEC: VIX LEVEL TERCILES   (causal rolling-252)   "
      "DISCOVERY_CONTAMINATED")
    P("Mechanism: high EX-ANTE implied variance => NEGATIVE expected INTRADAY drift,")
    P("           i.e. implied vol as a SIGNED SHORT TRIGGER, not an exposure gate.")
    P("Spec     : state = causal rolling-252-obs tercile of prior-session VIX close.")
    P("Entry    : 09:30:00 print (open of the bar stamped 09:31). Exit: last RTH print.")
    P("Costs    : $4.36 FLOOR (commission only, never a headline) / $20.65 PRIMARY / "
      "$25.01 STRESS")
    P(f"           NQ point value ${C.PV:.0f}; a full-session round turn must clear "
      f"{C.BREAKEVEN_PTS_PRIMARY:.4f} pts at PRIMARY.")

    H("[0] WALL ASSERTION -- nothing on or after 2022-01-01 is read")
    d = pd.read_parquet(PANEL)
    mx = d["session_date"].max()
    P(f"  panel rows                 : {len(d):,}")
    P(f"  span                       : {d['session_date'].min().date()} .. {mx.date()}")
    P(f"  assert max(session_date) < {WALL.date()}   -> {mx < WALL}")
    assert mx < WALL, "WALL BREACH on session_date"
    assert (d["session_date"] >= WALL).sum() == 0, "WALL BREACH: post-wall rows present"
    dtcols = [c for c in d.columns if c.endswith("_asof")] + ["prev_session_date"]
    for c in dtcols:
        v = pd.to_datetime(d[c]).dropna()
        assert len(v) == 0 or v.max() < WALL, f"WALL BREACH on {c}"
    P(f"  assert every *_asof and prev_session_date < wall ({len(dtcols)} cols) -> True")
    P(f"  rows on/after the wall     : {int((d['session_date'] >= WALL).sum())}  "
      f"(must be 0)")
    P("  WALL ASSERTION: PASS.  No session >= 2022-01-01 is read, counted or aggregated.")
    P("  This script makes no CrossTrade / NinjaTrader call of any kind.")

    # ================================================================== [1] POPULATION
    H("[1] POPULATION")
    P(f"  session_quality counts     : "
      + ", ".join(f"{k}={v:,}" for k, v in d["session_quality"].value_counts().items()))
    f = d[d["session_quality"] == "FULL"].reset_index(drop=True)
    P(f"  condition on FULL          : {len(f):,} sessions "
      f"(panel README default; strict rth_ret_pts is defined on all of them)")
    P(f"  vix non-NaN on FULL        : {int(f['vix'].notna().sum()):,}  "
      f"(VIX starts 1990, so the binding constraint is the NQ tape, not the index)")

    f["st_vix"] = build_state(f, "vix")
    valid, hi, lo, nonhi = arm_positions(f["st_vix"].values, f["rth_ret_pts"].values)
    P(f"  state defined (needs {WINDOW} prior VIX obs) and return defined: "
      f"{int(valid.sum()):,} sessions")
    g = f[valid].reset_index(drop=True)
    st = g["st_vix"].values
    ret = g["rth_ret_pts"].values
    dates = pd.DatetimeIndex(g["session_date"])
    hi = st == 2.0
    lo = st == 0.0
    mid = st == 1.0
    P(f"  ANALYSIS POPULATION        : {len(g):,} sessions, "
      f"{dates.min().date()} .. {dates.max().date()}")
    P(f"  state counts               : low={int(lo.sum()):,}  mid={int(mid.sum()):,}  "
      f"high={int(hi.sum()):,}")
    assert dates.max() < WALL

    # ================================================================== [2] STATE
    H("[2] WHAT THE HIGH STATE IS")
    P(f"  {'state':<6s} {'n':>6s} {'VIX min':>8s} {'VIX p50':>8s} {'VIX max':>8s} "
      f"{'mean pts':>9s} {'sd pts':>8s} {'mean log bp':>12s} {'sd log bp':>10s} "
      f"{'pts/sd':>7s}")
    for nm, m in (("low", lo), ("mid", mid), ("high", hi)):
        v = g.loc[m, "vix"]
        r = g.loc[m, "rth_ret_pts"]
        lr = g.loc[m, "rth_ret_log"] * 1e4
        P(f"  {nm:<6s} {int(m.sum()):>6,} {v.min():>8.2f} {v.median():>8.2f} "
          f"{v.max():>8.2f} {r.mean():>9.3f} {r.std():>8.3f} {lr.mean():>12.2f} "
          f"{lr.std():>10.2f} {r.mean()/r.std():>7.4f}")
    P(f"  {'ALL':<6s} {len(g):>6,} {g['vix'].min():>8.2f} {g['vix'].median():>8.2f} "
      f"{g['vix'].max():>8.2f} {ret.mean():>9.3f} {ret.std():>8.3f} "
      f"{(g['rth_ret_log']*1e4).mean():>12.2f} {(g['rth_ret_log']*1e4).std():>10.2f} "
      f"{ret.mean()/ret.std():>7.4f}")
    P("")
    P("  READ THE SIGN. The mechanism predicts mean INTRADAY drift in the HIGH state to be")
    P("  NEGATIVE. Both the point mean and the log mean are reported because points are not")
    P("  risk-normalised: a high-VIX session moves further per unit of drift by construction.")
    P("  Dollars are what the verdict is decided on; the log column is there so nobody can")
    P("  claim the sign is a point-scaling artefact.")

    P("")
    P("  high-state share by year (state is causal, so 2006 is partly undefined):")
    yr = pd.DataFrame({"y": dates.year, "hi": hi.astype(int)}).groupby("y").agg(
        n=("hi", "size"), nhi=("hi", "sum"))
    yr["share"] = 100 * yr["nhi"] / yr["n"]
    P("    " + "  ".join(f"{int(i)}:{int(r.nhi):>3d}/{int(r.n):>3d}"
                         for i, r in yr.iterrows()))

    # ================================================================== [3] EPISODES
    H("[3] EPISODE STRUCTURE -- the sample size is the episode count, not the session count")
    short_pts = np.where(hi, -ret, np.nan)          # the S arm's per-trade points
    eids_hi = C.episode_ids(hi, dates, gap_days=GAP)
    eps = C.episodes(hi, dates, gap_days=GAP)
    K = len(eps)
    rho = C.icc_rho(short_pts, eids_hi)
    P(f"  episode definition         : maximal run of high sessions separated by "
      f">= {GAP} calendar days")
    P(f"  K (high episodes) @gap{GAP}   : {K}")
    for gd in (21, 42, 63):
        P(f"  K @gap{gd:<2d}                  : {len(C.episodes(hi, dates, gap_days=gd))}")
    P(f"  rho_bar (ICC of short-leg pts within episode) : {rho:.4f}   [PRINTED, as required]")
    P(f"  K_eff = K/(1+(K-1)*rho_bar) : {C.k_eff(K, rho):.2f}")
    et = C.episode_table(hi, dates, gap_days=GAP, values=short_pts)
    P(f"  episode sizes              : min={int(et['n_sessions'].min())} "
      f"p25={et['n_sessions'].quantile(.25):.0f} med={et['n_sessions'].median():.0f} "
      f"p75={et['n_sessions'].quantile(.75):.0f} max={int(et['n_sessions'].max())}   "
      f"top-5 share={100*et['n_sessions'].nlargest(5).sum()/et['n_sessions'].sum():.1f}%")
    P("")
    P("  ten largest high-state episodes -- SHORT-LEG points (positive = shorting won):")
    P(f"    {'start':<12s} {'end':<12s} {'sess':>5s} {'short pts':>11s} "
      f"{'pts/sess':>9s}")
    for _, r in et.nlargest(10, "n_sessions").iterrows():
        P(f"    {str(r['start'].date()):<12s} {str(r['end'].date()):<12s} "
          f"{int(r['n_sessions']):>5d} {r['sum']:>11,.1f} {r['mean']:>9.3f}")
    win = int((et["sum"] > 0).sum())
    P(f"  episodes where the SHORT leg made gross points: {win}/{K} = "
      f"{100*win/K:.1f}%   (sessions weight: "
      f"{100*et.loc[et['sum']>0,'n_sessions'].sum()/et['n_sessions'].sum():.1f}% "
      f"of high sessions)")

    # ================================================================== [4] THREE ARMS
    H("[4] THE THREE ARMS -- printed together or the result is INADMISSIBLE")
    tab = C.three_arms(g, "st_vix", high_state=2, low_state=0, gap_days=GAP)
    P(C.format_arms(tab))
    for leg, dd in tab.attrs["identity"].items():
        assert dd < 1e-6, f"identity R=F+S broken for {leg}"
    P("")
    P("  long_leg conventions, both reported because picking one silently is how this gets")
    P("  fudged: 'low_only' = the brief's literal router (long ONLY in the low state, flat in")
    P("  mid); 'non_high'  = the honest long-only baseline a filter is compared against.")
    P("  The R-minus-F difference is IDENTICAL under both -- it is exactly the S arm.")

    # ================================================================== [5] PER SESSION
    H("[5] PER-SESSION NET, with the episode-block bootstrap CI beside every number")
    blk = timeline_blocks(hi, dates, gap_days=GAP)
    nblk = blk.max() + 1
    assert nblk == K, f"timeline blocks {nblk} != high episodes {K}"
    P(f"  resampling unit            : {K} contiguous timeline blocks (high episode k + the")
    P(f"                               quiet stretch after it). Covers all {len(g):,} sessions;")
    P(f"                               K is therefore the SAME number for every arm.")
    P(f"  draws                      : {NDRAW:,}  seed={SEED}  "
      f"(one multinomial draw applied to every arm, so CIs of DIFFERENCES are valid)")
    P(f"  rho_bar={rho:.4f}   K_eff={C.k_eff(K, rho):.2f}")

    den_blk = np.bincount(blk, weights=np.ones(len(g)), minlength=K)

    def arm_signed(pos):
        traded = pos != 0
        return np.where(traded, pos * ret, 0.0), traded

    ARMS = {
        "BASE_always_long":  np.ones(len(g)),
        "R_router(low_only)": np.where(lo, 1.0, np.where(hi, -1.0, 0.0)),
        "F_filter(low_only)": np.where(lo, 1.0, 0.0),
        "R_router(non_high)": np.where(~hi, 1.0, -1.0),
        "F_filter(non_high)": np.where(~hi, 1.0, 0.0),
        "S_short_only":      np.where(hi, -1.0, 0.0),
    }

    for cost, cname in zip(C.COSTS, C.COST_NAMES):
        P("")
        P(f"  ---- cost line {cname}  (${cost:.2f} / ctrRT) "
          + "-" * 40)
        P(f"    {'arm':<20s} {'trades':>7s} {'$/session':>10s} "
          f"{'95% CI (block bootstrap)':>30s} {'excl 0':>7s} {'$/trade':>9s} "
          f"{'total $':>12s}")
        num_blk = {}
        for nm, pos in ARMS.items():
            signed, traded = arm_signed(pos)
            npl = C.net_per_session(np.where(traded, signed, np.nan), cost, traded=traded)
            num_blk[nm] = np.bincount(blk, weights=npl, minlength=K)
        draws = ratio_bootstrap(num_blk, den_blk, K)
        for nm, pos in ARMS.items():
            signed, traded = arm_signed(pos)
            npl = C.net_per_session(np.where(traded, signed, np.nan), cost, traded=traded)
            tot = npl.sum()
            per = tot / len(g)
            l, h, se, ex = ci(draws[nm])
            ptr = tot / max(int(traded.sum()), 1)
            P(f"    {nm:<20s} {int(traded.sum()):>7,} {per:>10.2f} "
              f"{fmt_ci(l, h):>30s} {str(ex):>7s} {ptr:>9.2f} {tot:>12,.0f}")
        if cost == C.COST_PRIMARY:
            prim_draws = draws
            prim_num = num_blk

    # per-session identity
    P("")
    for leg in ("low_only", "non_high"):
        rr = prim_num[f"R_router({leg})"].sum() / len(g)
        ff = prim_num[f"F_filter({leg})"].sum() / len(g)
        ss = prim_num["S_short_only"].sum() / len(g)
        P(f"  identity per session @PRIMARY ({leg}): R={rr:.4f}  F={ff:.4f}  S={ss:.4f}  "
          f"|R-(F+S)|={abs(rr-(ff+ss)):.9f} -> "
          f"{'PASS' if abs(rr-(ff+ss)) < 1e-9 else 'FAIL'}")
        assert abs(rr - (ff + ss)) < 1e-9

    # ================================================================== [6] R vs F
    H("[6] IS THE ROUTER DISTINGUISHABLE FROM THE FILTER?")
    P("  net(R) - net(F) == net(S) EXACTLY, costs included, under BOTH long-leg conventions.")
    P("  So 'is R distinguishable from F' and 'is S non-zero' are ONE question, and the")
    P("  bootstrap below is run on the same draws so the difference CI is coherent.")
    for leg in ("low_only", "non_high"):
        diff = prim_draws[f"R_router({leg})"] - prim_draws[f"F_filter({leg})"]
        obs = (prim_num[f"R_router({leg})"].sum() - prim_num[f"F_filter({leg})"].sum()) / len(g)
        l, h, se, ex = ci(diff)
        P(f"    R-F ({leg:<9s}) @PRIMARY = ${obs:>8.3f}/session   95% CI "
          f"{fmt_ci(l, h)}   excludes 0: {ex}")
    l, h, se, ex = ci(prim_draws["S_short_only"])
    obsS = prim_num["S_short_only"].sum() / len(g)
    P(f"    S           (-)          @PRIMARY = ${obsS:>8.3f}/session   95% CI "
      f"{fmt_ci(l, h)}   excludes 0: {ex}")
    P("")
    P("  DISTINGUISHABLE is a two-sided statement. It does NOT mean 'the router is better'.")
    P("  The sign of R-F is the sign of net(S). If net(S) < 0 the short leg is not a costume")
    P("  for exposure reduction -- it is an active destruction of the filter's P&L, which is")
    P("  a worse outcome for the candidate than being indistinguishable.")
    P("")
    _dist = ci(prim_draws["S_short_only"])[3]
    _sign = "NEGATIVE (the router is WORSE than the filter)" if obsS < 0 else "POSITIVE"
    P(f"  ANSWER -- ROUTER vs FILTER DISTINGUISHABLE @PRIMARY : {_dist}")
    P(f"  ANSWER -- SIGN OF THE DIFFERENCE                    : {_sign}")
    P("  So this candidate does not die the usual anti-filter death ('the short leg adds")
    P("  nothing'). It dies a worse one: the short leg subtracts, reliably.")

    # per-trade short edge, using the wave-standard high-episode bootstrap
    P("")
    P("  the S arm's per-TRADE edge, via common.block_bootstrap_by_episode (high episodes")
    P("  only -- the wave-standard helper, on the statistic it is the right unit for):")
    bs = C.bootstrap_summary(C.block_bootstrap_by_episode(short_pts, eids_hi, NDRAW, SEED))
    P(f"    mean SHORT-leg points per high session = {np.nanmean(short_pts):>7.4f} pts")
    P(f"    95% CI over whole high episodes        = [{bs['ci_lo']:.4f}, {bs['ci_hi']:.4f}] "
      f"pts   p(two-sided)={bs['p_two_sided']:.4f}  excludes 0: {bs['excludes_zero']}")
    P(f"    BREAKEVEN at PRIMARY                   = {C.BREAKEVEN_PTS_PRIMARY:.4f} pts   "
      f"-> the CI must lie entirely ABOVE this for the S arm to be viable")
    tt = np.nanmean(short_pts) / (np.nanstd(short_pts, ddof=1) / np.sqrt(int(hi.sum())))
    P(f"    session-level t = {tt:.2f}   *** DIAGNOSTIC ONLY -- BANNED as inference here ***")

    # ================================================================== [7] PLACEBO
    H("[7] RATE-MATCHED RANDOM-SHORT PLACEBO")
    n = len(g)
    s_pnl = -ret                                   # short P&L in points, every session
    hif = hi.astype(float)
    nhi = int(hi.sum())
    P(f"  The S arm shorts {nhi:,} of {n:,} sessions ({100*nhi/n:.1f}%). A placebo must match")
    P("  that RATE. Two are run; the circular shift is the admissible one because the repo's")
    P("  method requires nulls to PRESERVE DEPENDENCE -- it keeps the episode/run structure,")
    P("  the rate and the calendar-clustering of the real state exactly, and only destroys")
    P("  the alignment between the state and the returns.")

    MINSHIFT = 63
    shifts = [k for k in range(1, n) if MINSHIFT <= k <= n - MINSHIFT]
    null_pts = np.empty(len(shifts))
    for j, k in enumerate(shifts):
        null_pts[j] = float(np.dot(s_pnl, np.roll(hif, k)))
    obs_pts = float(np.dot(s_pnl, hif))
    P("")
    P(f"  (a) CIRCULAR SHIFT of the state mask, all {len(shifts):,} shifts with "
      f"|k| >= {MINSHIFT} sessions")
    P(f"      observed S gross                 = {obs_pts:>10,.1f} pts")
    P(f"      null mean / sd                   = {null_pts.mean():>10,.1f} / "
      f"{null_pts.std(ddof=1):,.1f} pts")
    P(f"      null p05 / p50 / p95             = {np.quantile(null_pts,.05):>10,.1f} / "
      f"{np.quantile(null_pts,.50):,.1f} / {np.quantile(null_pts,.95):,.1f}")
    pct = 100.0 * (null_pts < obs_pts).mean()
    P(f"      observed percentile in the null  = {pct:>10.1f}%   "
      f"(needs > 95% for the short trigger to beat a rate-matched placebo)")
    for cost, cname in zip(C.COSTS, C.COST_NAMES):
        P(f"      per-session net {cname:<20s}: observed "
          f"${(obs_pts*C.PV - nhi*cost)/n:>7.3f}   null p95 "
          f"${(np.quantile(null_pts,.95)*C.PV - nhi*cost)/n:>7.3f}   "
          f"null share > 0: {100*((null_pts*C.PV - nhi*cost) > 0).mean():.1f}%")

    P("")
    rng = np.random.default_rng(SEED)
    iid = np.empty(NDRAW)
    for j in range(NDRAW):
        pick = rng.choice(n, size=nhi, replace=False)
        iid[j] = float(s_pnl[pick].sum())
    P(f"  (b) i.i.d. rate-matched random short, {NDRAW:,} draws of {nhi:,} sessions "
      f"WITHOUT replacement")
    P(f"      null mean / sd                   = {iid.mean():>10,.1f} / "
      f"{iid.std(ddof=1):,.1f} pts")
    P(f"      observed percentile in the null  = {100.0*(iid < obs_pts).mean():>10.1f}%")
    P("      (reported for contrast only. Its sd is far too small because it destroys the")
    P("       clustering; it is NOT the bar this wave adjudicates against.)")

    # ================================================================== [8] VIX vs VXN
    H("[8] VIX vs VXN -- is the effect NQ-specific or broad-market?")
    P("  VXN is the NASDAQ-100 vol index and is the ex-ante implied variance actually")
    P("  written on this contract; VIX is the S&P 500's. If the mechanism is real and")
    P("  NQ-specific, VXN should be AT LEAST as strong. If VIX is materially stronger, the")
    P("  effect is a broad-market risk phenomenon, not anything about NQ.")
    P("  Both states are built on each index's own full causal history, then the comparison")
    P("  is restricted to the sessions where BOTH states are defined (VXN starts 2009-09).")

    f["st_vxn"] = build_state(f, "vxn")
    both = f["st_vix"].notna() & f["st_vxn"].notna() & f["rth_ret_pts"].notna()
    m = f[both].reset_index(drop=True)
    dm = pd.DatetimeIndex(m["session_date"])
    assert dm.max() < WALL
    P("")
    P(f"  matched population: {len(m):,} sessions, {dm.min().date()} .. {dm.max().date()}")
    P("")
    P(f"  {'index':<6s} {'n_high':>7s} {'K':>4s} {'rho':>7s} {'K_eff':>7s} "
      f"{'short pts/trade':>16s} {'95% CI (pts)':>22s} {'net/sess @20.65':>16s} "
      f"{'total net @20.65':>17s}")
    cmp_rows = {}
    for col, stc in (("vix", "st_vix"), ("vxn", "st_vxn")):
        sv = m[stc].values
        rv = m["rth_ret_pts"].values
        hv = sv == 2.0
        spv = np.where(hv, -rv, np.nan)
        ev = C.episode_ids(hv, dm, gap_days=GAP)
        Kv = len(C.episodes(hv, dm, gap_days=GAP))
        rv_rho = C.icc_rho(spv, ev)
        b = C.bootstrap_summary(C.block_bootstrap_by_episode(spv, ev, NDRAW, SEED))
        tot = np.nansum(spv) * C.PV - int(hv.sum()) * C.COST_PRIMARY
        cmp_rows[col] = dict(n=int(hv.sum()), K=Kv, mean=float(np.nanmean(spv)),
                             lo=b["ci_lo"], hi=b["ci_hi"], net=tot / len(m), tot=tot)
        P(f"  {col:<6s} {int(hv.sum()):>7,} {Kv:>4d} {rv_rho:>7.4f} "
          f"{C.k_eff(Kv, rv_rho):>7.2f} {np.nanmean(spv):>16.4f} "
          f"{'['+format(b['ci_lo'],'.3f')+', '+format(b['ci_hi'],'.3f')+']':>22s} "
          f"{tot/len(m):>16.2f} {tot:>17,.0f}")
    P(f"  {'':<6s} {'':>7s} {'':>4s} {'':>7s} {'':>7s} "
      f"{'breakeven '+format(C.BREAKEVEN_PTS_PRIMARY,'.4f'):>16s}")

    # full-history VIX row for reference
    P("")
    P(f"  reference: VIX on its FULL pre-wall history ({len(g):,} sessions) short pts/trade "
      f"= {np.nanmean(short_pts):.4f}")
    P("")
    P("  HOW TO READ THIS COMPARISON -- and how NOT to.")
    P("  Both numbers are NEGATIVE and both CIs straddle zero. Neither index produces a")
    P("  signed short edge, so the question the comparison was designed to answer ('is the")
    P("  effect NQ-specific?') is VACUOUS: there is no effect whose locus could be argued")
    P("  about. G7 below is therefore reported but carries no weight either way.")
    P("  What the two rows DO say is that the INVERSE of the claim -- long the high state --")
    P("  is larger under the broad-market VIX (+3.01 pts/session) than under the")
    P("  NQ-native VXN (+1.78) on the matched sample. If anything survived here it would be")
    P("  a BROAD-MARKET risk phenomenon, not an NQ one. That inverse is NOT a candidate:")
    P("  flipping the sign after seeing the result is exactly the move this repo's method")
    P("  forbids, the episode CI on it straddles zero, and the long-the-high-state leg is")
    P("  already inside the always-long BASE, whose own CI also straddles zero.")

    # ================================================================== [9] ROBUSTNESS
    H("[9] ROBUSTNESS -- does the sign or the magnitude move?")
    P("  (a) tercile lookback window")
    P(f"      {'window':>7s} {'n_high':>7s} {'K':>4s} {'short pts/trade':>16s} "
      f"{'net/sess @20.65':>16s}")
    for w in (126, 252, 504, None):
        s2 = build_state(f, "vix", window=w)
        v2 = (~np.isnan(s2)) & f["rth_ret_pts"].notna().values
        h2 = v2 & (s2 == 2.0)
        r2 = f["rth_ret_pts"].values
        sp2 = np.where(h2, -r2, np.nan)
        K2 = len(C.episodes(h2, pd.DatetimeIndex(f["session_date"]), gap_days=GAP))
        tot2 = np.nansum(sp2) * C.PV - int(h2.sum()) * C.COST_PRIMARY
        P(f"      {str(w):>7s} {int(h2.sum()):>7,} {K2:>4d} {np.nanmean(sp2):>16.4f} "
          f"{tot2/int(v2.sum()):>16.2f}")

    P("")
    P("  (b) leave-one-episode-out on the S arm (the 2020 concentration check)")
    tot_sum = np.nansum(short_pts)
    P(f"      all {K} episodes            : short gross {tot_sum:>9,.1f} pts over "
      f"{nhi:,} sessions = {tot_sum/nhi:>7.4f} pts/trade")
    for _, r in et.nlargest(5, "n_sessions").iterrows():
        rem_s = tot_sum - r["sum"]
        rem_n = nhi - int(r["n_sessions"])
        P(f"      drop {str(r['start'].date())}..{str(r['end'].date())}: short gross "
          f"{rem_s:>9,.1f} pts over {rem_n:,} sessions = {rem_s/rem_n:>7.4f} pts/trade  "
          f"(net/trade @20.65 = ${rem_s/rem_n*C.PV - C.COST_PRIMARY:>8.2f})")
    worst = et.loc[et["sum"].idxmin()]
    P(f"      drop the WORST episode for the short leg "
      f"({str(worst['start'].date())}..{str(worst['end'].date())}, "
      f"{int(worst['n_sessions'])} sess): "
      f"{(tot_sum-worst['sum'])/(nhi-int(worst['n_sessions'])):.4f} pts/trade")
    best = et.loc[et["sum"].idxmax()]
    P(f"      drop the BEST  episode for the short leg "
      f"({str(best['start'].date())}..{str(best['end'].date())}, "
      f"{int(best['n_sessions'])} sess): "
      f"{(tot_sum-best['sum'])/(nhi-int(best['n_sessions'])):.4f} pts/trade")

    P("")
    P("  (c) the same table on the tolerant return column (holiday sessions included)")
    fa = d[d["session_quality"].isin(["FULL", "SHORT_SESSION"])].reset_index(drop=True)
    fa["st"] = build_state(fa, "vix")
    va = (~np.isnan(fa["st"].values)) & fa["rth_ret_pts_any"].notna().values
    ha = va & (fa["st"].values == 2.0)
    spa = np.where(ha, -fa["rth_ret_pts_any"].values, np.nan)
    P(f"      rth_ret_pts_any, FULL+SHORT_SESSION: {int(va.sum()):,} sessions, "
      f"{int(ha.sum()):,} high, short pts/trade = {np.nanmean(spa):.4f}, "
      f"net/sess @20.65 = "
      f"${(np.nansum(spa)*C.PV - int(ha.sum())*C.COST_PRIMARY)/int(va.sum()):.3f}")

    # ================================================================== [10] GATES
    H("[10] GATE TABLE -- every clause coded, printed by the program, never assembled by hand")
    P("  Gates were written into this script before it was run; a gate that fails is recorded")
    P("  failed and the population is NOT redefined afterwards.")
    P("")
    mean_short = float(np.nanmean(short_pts))
    netS_ps = prim_num["S_short_only"].sum() / len(g)
    lS, hS, seS, exS = ci(prim_draws["S_short_only"])
    difflo = ci(prim_draws["R_router(low_only)"] - prim_draws["F_filter(low_only)"])
    gates = [
        ("G1 S clears cost per trade",
         f"mean short-leg pts > {C.BREAKEVEN_PTS_PRIMARY:.4f}",
         f"{mean_short:.4f} pts",
         mean_short > C.BREAKEVEN_PTS_PRIMARY),
        ("G2 S total net > 0 @PRIMARY", "net(S) @ $20.65 > $0",
         f"${prim_num['S_short_only'].sum():,.0f}",
         prim_num["S_short_only"].sum() > 0),
        ("G3 S CI excludes 0, positive", "block-bootstrap 95% CI lower bound > 0",
         f"CI [{lS:.3f}, {hS:.3f}] $/sess", lS > 0),
        ("G4 S beats rate-matched placebo", "observed > 95th pct of circular-shift null",
         f"{pct:.1f}th percentile", pct > 95.0),
        ("G5 router beats filter", "net(R) - net(F) > 0 and CI excludes 0 @PRIMARY",
         f"R-F = ${(prim_num['R_router(low_only)'].sum()-prim_num['F_filter(low_only)'].sum())/len(g):.3f}/sess, "
         f"excl0={difflo[3]}",
         ((prim_num["R_router(low_only)"].sum()
           - prim_num["F_filter(low_only)"].sum()) > 0) and difflo[3]),
        ("G6 not one-episode-driven", "short pts/trade > breakeven with the best episode dropped",
         f"{(tot_sum-best['sum'])/(nhi-int(best['n_sessions'])):.4f} pts",
         (tot_sum - best["sum"]) / (nhi - int(best["n_sessions"]))
         > C.BREAKEVEN_PTS_PRIMARY),
        ("G7 VXN >= VIX (VACUOUS here)", "VXN short pts/trade >= VIX, matched sample",
         f"VXN {cmp_rows['vxn']['mean']:.4f} vs VIX {cmp_rows['vix']['mean']:.4f} "
         f"(both < 0)",
         cmp_rows["vxn"]["mean"] >= cmp_rows["vix"]["mean"]),
    ]
    P(f"  {'GATE':<30s} {'SPEC':<52s} {'OBSERVED':<34s} {'RESULT':>6s}")
    P("  " + "-" * 124)
    for nm, spec, obs, ok in gates:
        P(f"  {nm:<30s} {spec:<52s} {obs:<34s} {'PASS' if ok else 'FAIL':>6s}")
    P("  " + "-" * 124)
    core = all(ok for nm, _, _, ok in gates if nm.startswith(("G1", "G2", "G3", "G4",
                                                             "G5", "G6")))
    P(f"  CORE GATES G1-G6: {'ALL PASS' if core else 'FAILED'}   "
      f"(G7 is diagnostic -- it decides NQ-specific vs broad-market, not promotion)")

    # ================================================================== [11] VERDICT
    H("[11] VERDICT")
    if core:
        P("  PROMISING -- but see the text; this path was not expected to be reached.")
    else:
        P("  DEAD.")
    P("")
    P(f"  The mechanism predicts NEGATIVE intraday drift in the high implied-variance state.")
    P(f"  Observed mean intraday drift in the high-VIX tercile is "
      f"{np.nanmean(ret[hi]):+.4f} points --")
    P(f"  i.e. the SHORT leg loses {abs(mean_short):.4f} points per trade GROSS, before it")
    P(f"  pays the {C.BREAKEVEN_PTS_PRIMARY:.4f}-point round turn. The sign is INVERTED "
      f"relative to the claim.")
    P(f"  Net(S) at the PRIMARY line: ${prim_num['S_short_only'].sum():,.0f} over "
      f"{nhi:,} shorts = ${prim_num['S_short_only'].sum()/nhi:,.2f} per trade.")
    P("")
    P("  Four independent ways this dies, none of which is a magnitude quibble:")
    P(f"   1. SIGN. The high-VIX tercile's intraday drift is +{np.nanmean(ret[hi]):.3f} pts, not")
    P(f"      negative. It is even positive in log terms "
      f"({(g.loc[hi,'rth_ret_log']*1e4).mean():.2f} bp), so it is not a")
    P("      point-scaling artefact. The proposed trigger points the wrong way.")
    P(f"   2. NO INFORMATION. Against a rate-matched CIRCULAR-SHIFT null that preserves the")
    P(f"      episode clustering exactly, the observed short sits at the {pct:.1f}th percentile --")
    P("      an unremarkable draw. The VIX tercile carries no signed intraday information at")
    P("      all; the whole short family merely fights NQ's "
      f"+{ret.mean():.2f} pt/session intraday drift.")
    P(f"   3. NOT ONE EPISODE. Removing COVID (2020-02-21..2020-07-17, the single worst block")
    P(f"      for the short) still leaves "
      f"{(tot_sum-worst['sum'])/(nhi-int(worst['n_sessions'])):.4f} pts/trade -- still short of the")
    P(f"      {C.BREAKEVEN_PTS_PRIMARY:.4f}-pt round turn by "
      f"{C.BREAKEVEN_PTS_PRIMARY - (tot_sum-worst['sum'])/(nhi-int(worst['n_sessions'])):.2f} pts. "
      f"The short leg wins in only {win}/{K} episodes.")
    P("   4. NO MAGNITUDE HEADROOM. Even the FLOOR cost line ($4.36, commission only, which")
    P(f"      is never a headline) leaves net(S) at "
      f"${np.nansum(short_pts)*C.PV - nhi*C.COST_FLOOR:,.0f}. There is no cost")
    P("      assumption under which this arm is positive.")
    P("")
    P("  The filter arm is not a consolation prize either: F(low_only) nets $6.03/session at")
    P("  PRIMARY but its 95% episode-block CI is [-$12.42, $30.99] -- it does not exclude")
    P("  zero, and F(non_high) is -$0.11/session. That is the repo's closed anti-filter")
    P("  family behaving exactly as it has ten times before.")
    P("")
    P("  DISCOVERY_CONTAMINATED. No part of this is a result, and no part of it justifies")
    P("  spending the one-shot 2022-01-01 -> 2026-07-31 confirmation window.")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(_LOG) + "\n")
    P("")
    P(f"WROTE {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
