"""G3_VOLSHORT01 -- SPEC: VIX term structure and vol-of-vol.

EVIDENCE STATUS: DISCOVERY_CONTAMINATED.  Nothing in this file is a result.  It exists to
produce a RULE PROPOSAL that someone else freezes and commits BEFORE the one-shot read of
2022-01-01 -> 2026-07-31.

THE WALL.  2022-01-01.  The panel this reads is already < 2022-01-01 by construction
(panel.py enforced it at load); this script RE-ASSERTS it on the artefact and on every
derived frame, and prints the assertion.  No session on or after 2022-01-01 is read, loaded,
plotted, aggregated or counted here.

--------------------------------------------------------------------------------------------
MECHANISM UNDER TEST
--------------------------------------------------------------------------------------------
The price of variance risk flips sign with the trading window: the equity premium is
compensated OVERNIGHT, while the INTRADAY window is where levered / short-horizon holders
de-risk and liquidity providers extract compensation.  High EX-ANTE implied variance should
therefore carry NEGATIVE expected INTRADAY drift, and implied vol should be a SIGNED SHORT
TRIGGER, not an exposure gate.

MY SLICE: scale-free TERM-STRUCTURE and VOL-OF-VOL ratios rather than a raw level.
    (a) ts9  = VIX9D / VIX     very-short vs short end
    (b) ts3  = VIX  / VIX3M    backwardation (>1) vs contango (<1)  -- the classic stress state
    (c) vov  = VVIX / VIX      vol-of-vol relative to vol

--------------------------------------------------------------------------------------------
PRE-DECLARED DESIGN (fixed before any return was touched)
--------------------------------------------------------------------------------------------
POPULATION      session_quality == "FULL" and rth_ret_pts not NaN.  Strict 09:30 -> 16:00.
STATE           common.causal_tercile(ratio, window=252) on the FULL chronological panel
                (all 4,106 rows, so the trailing window sees every prior trading day), then
                the evaluation population is restricted to FULL sessions.  Strictly prior
                observations only; the value at i never enters its own cutoff.
SIGN            For (a) and (b) the STRESS state is the HIGH tercile (state 2): a rising very
                short end, and backwardation, are stress.  For (c) the sign is NOT determined
                a priori, and the predictor-only correlation corr(vov, VIX) = -0.776 (computed
                from ex-ante columns ONLY, no return consulted) says the HIGH tercile of vov is
                a CALM state, not a stress state.  So (c) is run at BOTH ends and COUNTS AS TWO
                TESTS in the family size.  FAMILY SIZE = 4 states x 2 long-leg conventions.
ARMS            common.three_arms -- (R) router, (F) filter, (S) short-only, plus BASE.  All
                three printed together or the result is inadmissible.  R = F + S is asserted.
COSTS           $4.36 FLOOR (never a headline) / $20.65 PRIMARY / $25.01 STRESS per ctrRT.
                NQ = $20/pt, so a full-session round turn must clear 1.0325 pts.
INFERENCE       Session-level t is BANNED as inference (printed only, labelled DIAGNOSTIC).
                (S): whole-episode block bootstrap over high-state episodes, gap_days=10.
                (R)/(F)/(BASE): they trade outside the high state too, so the resampling unit
                is the FULL-TIMELINE ALTERNATING BLOCK partition -- every high-state episode is
                one block and every contiguous non-high stretch between two episodes is one
                block.  Same clustering, complete coverage.  Labelled wherever used.
                K, rho_bar and K_eff = K/(1+(K-1)*rho_bar) are printed together, never K alone.
PLACEBO         Rate-matched, dependence-preserving: EXHAUSTIVE CIRCULAR SHIFT of the state
                array against the return array (all shifts with |k| >= 63 sessions).  Every
                shift has the identical number of short sessions and the identical episode
                block structure; only the alignment to returns is destroyed.  An i.i.d.
                random-short placebo is also printed, labelled as the WEAKER bar it is.

GATES (every clause coded; the PASS/FAIL table is printed by the program, never by hand)
    G1  mean gross short-leg drift in the high state <= -1.0325 pts  (clears the primary cost)
    G2  net(S) at $20.65 > 0 in total dollars
    G3  whole-episode block bootstrap 95% CI of mean net(S) per traded session at $20.65
        excludes zero on the POSITIVE side
    G4  observed total net(S) at $20.65 > 95th percentile of the circular-shift placebo
    G5  router distinguishable from filter: |net(R) - net(F)| at $20.65 is exactly net(S) by
        algebra, so G5 is G3 -- it is printed anyway, with the identity asserted, because the
        brief requires the comparison to be shown and not asserted.
VERDICT         PROMISING requires G1..G4 all PASS on the pre-designated headline state.
                DEAD if the short arm does not clear costs.  AMBIGUOUS only for a genuinely
                borderline case (gate margins inside noise), never as hedging.
HEADLINE STATE  (b) ts3 = VIX/VIX3M, high tercile -- pre-designated, because backwardation is
                the classic stress identifier and is the least confounded with trending
                realised vol.  The other three are reported in full beside it.

Run:  python runs/G3_VOLSHORT01_20260831/src/discovery/spec_term-structure.py
"""
from __future__ import annotations

import os
import sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, "..", ".."))
ROOT = os.path.abspath(os.path.join(RUN, "..", ".."))
sys.path.insert(0, HERE)
import common as C  # noqa: E402

PANEL = os.path.join(RUN, "out", "discovery", "panel_pre2022.parquet")
OUT = os.path.join(RUN, "out", "discovery", "spec_term-structure.txt")

WALL = pd.Timestamp("2022-01-01")
GAP_DAYS = 10
WINDOW = 252
NDRAW = 10000
SEED = 20260831

_LINES: list[str] = []


def P(s: str = "") -> None:
    print(s)
    _LINES.append(s)


def H(s: str) -> None:
    P("")
    P("=" * 100)
    P(s)
    P("=" * 100)


# ==================================================================================
# wall
# ==================================================================================
def assert_wall(df: pd.DataFrame, name: str) -> None:
    """Raise -- never warn -- if any date column in df touches 2022-01-01 or later."""
    checked = []
    for col in df.columns:
        s = df[col]
        if not (pd.api.types.is_datetime64_any_dtype(s) or "date" in col or col.endswith("_asof")):
            continue
        d = pd.to_datetime(s, errors="coerce")
        if d.notna().sum() == 0:
            continue
        mx = d.max()
        n_bad = int((d >= WALL).sum())
        if n_bad:
            raise AssertionError(f"WALL BREACH in {name}.{col}: {n_bad} rows >= {WALL.date()}")
        checked.append((col, mx))
    P(f"  [{name}] {len(checked)} date column(s) checked, 0 values >= {WALL.date()}  -> PASS")
    for col, mx in checked:
        P(f"      {col:<22s} max = {mx.date()}")


# ==================================================================================
# blocks
# ==================================================================================
def alternating_blocks(hi_mask: np.ndarray, dates: pd.DatetimeIndex,
                       gap_days: int = GAP_DAYS) -> np.ndarray:
    """Full-timeline block ids: each high-state EPISODE is one block, each contiguous
    non-high stretch between episodes is one block.  Covers every session (no -1)."""
    eids = C.episode_ids(hi_mask, dates, gap_days=gap_days)
    out = np.empty(len(eids), dtype=int)
    b = 0
    prev = None
    for i, e in enumerate(eids):
        key = ("EP", e) if e >= 0 else ("GAP",)
        if prev is None or key != prev:
            if prev is not None:
                b += 1
            prev = key
        out[i] = b
    return out


def boot_ci(values: np.ndarray, block_ids: np.ndarray, n_draws: int = NDRAW,
            seed: int = SEED) -> dict:
    """Block bootstrap of the MEAN over whole blocks.  Blocks are resampled with
    replacement, K times, and the pooled mean recorded."""
    v = np.asarray(values, dtype=float)
    b = np.asarray(block_ids)
    ok = ~np.isnan(v)
    v, b = v[ok], b[ok]
    if len(v) == 0:
        return dict(K=0, mean=np.nan, se=np.nan, ci_lo=np.nan, ci_hi=np.nan,
                    p_two_sided=np.nan, excludes_zero=False)
    groups = [v[b == k] for k in np.unique(b)]
    groups = [g for g in groups if len(g)]
    K = len(groups)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, K, size=(n_draws, K))
    draws = np.empty(n_draws)
    for j in range(n_draws):
        draws[j] = np.concatenate([groups[i] for i in idx[j]]).mean()
    s = C.bootstrap_summary(draws, observed=float(v.mean()))
    s["K"] = K
    s["observed"] = float(v.mean())
    return s


# ==================================================================================
# placebo
# ==================================================================================
def circular_shift_placebo(hi: np.ndarray, ret: np.ndarray, cost: float,
                           min_shift: int = 63) -> dict:
    """EXHAUSTIVE circular shift of the high-state mask against returns.

    Every shift keeps the exact number of short sessions (rate-matched) and the exact
    episode block structure of the state; only the alignment to returns changes.  This is
    the dependence-preserving null the repo mandates -- an i.i.d. random-short draw would
    set a bar that is far too low.
    """
    n = len(hi)
    obs_total = float(np.nansum(np.where(hi, -ret, 0.0)) * C.PV - hi.sum() * cost)
    obs_mean = obs_total / max(int(hi.sum()), 1)
    tot, mn = [], []
    for k in range(min_shift, n - min_shift + 1):
        h = np.roll(hi, k)
        t = float(np.nansum(np.where(h, -ret, 0.0)) * C.PV - h.sum() * cost)
        tot.append(t)
        mn.append(t / max(int(h.sum()), 1))
    tot = np.asarray(tot)
    mn = np.asarray(mn)
    return dict(
        n_shifts=len(tot), obs_total=obs_total, obs_mean=obs_mean,
        p50=float(np.median(tot)), p95=float(np.quantile(tot, 0.95)),
        p99=float(np.quantile(tot, 0.99)),
        pct_rank=float((tot < obs_total).mean()),
        p_one_sided=float((tot >= obs_total).mean()),
        mean_p95=float(np.quantile(mn, 0.95)),
        mean_pct_rank=float((mn < obs_mean).mean()),
    )


def iid_short_placebo(n_valid: int, n_short: int, ret: np.ndarray, cost: float,
                      n_draws: int = 5000, seed: int = SEED) -> dict:
    """Rate-matched i.i.d. random-short placebo.  Printed only as the WEAKER bar; it
    destroys the clustering and therefore understates the null spread."""
    rng = np.random.default_rng(seed)
    r = ret[~np.isnan(ret)]
    tot = np.empty(n_draws)
    for j in range(n_draws):
        pick = rng.choice(len(r), size=n_short, replace=False)
        tot[j] = float(-r[pick].sum() * C.PV - n_short * cost)
    return dict(p50=float(np.median(tot)), p95=float(np.quantile(tot, 0.95)),
                sd=float(tot.std(ddof=1)))


# ==================================================================================
# one state, fully evaluated
# ==================================================================================
def evaluate(pf: pd.DataFrame, state_col: str, label: str, high_state: int,
             low_state: int, ratio_col: str) -> dict:
    dates = pd.DatetimeIndex(pf["session_date"])
    st = pf[state_col].astype(float).values
    ret = pf["rth_ret_pts"].astype(float).values
    valid = (~np.isnan(st)) & (~np.isnan(ret))
    hi = valid & (st == float(high_state))
    lo = valid & (st == float(low_state))
    nonhi = valid & ~hi

    H(f"STATE: {label}")
    P(f"  ratio column        {ratio_col}")
    P(f"  high (short) state  causal_tercile(window={WINDOW}) == {high_state}")
    P(f"  low  (long)  state  causal_tercile(window={WINDOW}) == {low_state}")
    P(f"  evaluable sessions  {int(valid.sum()):,}   "
      f"span {dates[valid].min().date()} .. {dates[valid].max().date()}")
    P(f"  high sessions       {int(hi.sum()):,}  ({hi.sum()/max(valid.sum(),1):.1%})")
    P(f"  low  sessions       {int(lo.sum()):,}")

    # ---- what IS this state, in ex-ante terms ---------------------------------
    P("")
    P("  WHAT THE STATE IS (ex-ante columns only -- no return consulted):")
    P(f"    {'state':<8s} {'n':>6s} {'ratio_mean':>11s} {'VIX_mean':>9s} {'VXN_mean':>9s} "
      f"{'rvol21_mean':>12s}")
    for nm, m in (("high", hi), ("mid", valid & (st == 1.0)), ("low", lo)):
        if m.sum() == 0:
            continue
        P(f"    {nm:<8s} {int(m.sum()):>6,} {np.nanmean(pf[ratio_col].values[m]):>11.4f} "
          f"{np.nanmean(pf['vix'].values[m]):>9.2f} {np.nanmean(pf['vxn'].values[m]):>9.2f} "
          f"{np.nanmean(pf['realised_vol_21'].values[m]):>12.5f}")

    # ---- episodes -------------------------------------------------------------
    eps = C.episodes(hi, dates, gap_days=GAP_DAYS)
    eids = C.episode_ids(hi, dates, gap_days=GAP_DAYS)
    short_pts = np.where(hi, -ret, np.nan)
    rho = C.icc_rho(short_pts, eids)
    K = len(eps)
    Ke = C.k_eff(K, rho)
    et = C.episode_table(hi, dates, gap_days=GAP_DAYS, values=short_pts)
    P("")
    P(f"  EPISODES (maximal runs of the high state separated by >= {GAP_DAYS} calendar days)")
    P(f"    K = {K}   rho_bar = {rho:.4f}   K_eff = K/(1+(K-1)*rho_bar) = {Ke:.2f}")
    if K:
        sz = et["n_sessions"].values
        P(f"    episode size: min={sz.min()} p25={np.percentile(sz,25):.0f} "
          f"median={np.median(sz):.0f} p75={np.percentile(sz,75):.0f} max={sz.max()}   "
          f"singletons={int((sz==1).sum())}")
        top = et.sort_values("n_sessions", ascending=False).head(5)
        P(f"    top-5 episodes carry {top['n_sessions'].sum()/sz.sum():.1%} of all high sessions:")
        for _, r in top.iterrows():
            P(f"      {r['start'].date()} .. {r['end'].date()}  {int(r['n_sessions']):>4d} sess"
              f"   short-leg sum {r['sum']:>10,.1f} pts   mean {r['mean']:>7.3f} pts")
    P("    K alone is NOT the sample size.  K, rho_bar and K_eff are quoted together.")

    # ---- magnitude, in points, against the 1.0325 pt floor ---------------------
    hs = short_pts[hi]
    mean_short_pts = float(np.nanmean(hs))
    P("")
    P("  MAGNITUDE -- the thing that actually decides this")
    P(f"    mean SHORT-leg gross drift in the high state : {mean_short_pts:+.4f} pts/session")
    P(f"    (equivalently mean intraday drift            : {-mean_short_pts:+.4f} pts/session)")
    P(f"    cost floor a full-session round turn must clear at $20.65 : "
      f"{C.BREAKEVEN_PTS_PRIMARY:.4f} pts")
    P(f"    margin over the primary cost                  : "
      f"{mean_short_pts - C.BREAKEVEN_PTS_PRIMARY:+.4f} pts")
    t_diag = mean_short_pts / (np.nanstd(hs, ddof=1) / np.sqrt(np.sum(~np.isnan(hs))))
    P(f"    session-level t = {t_diag:+.2f}   <-- DIAGNOSTIC ONLY, BANNED AS INFERENCE "
      f"(sessions inside an episode are not independent)")

    # ---- is the sign one episode? ---------------------------------------------
    P("")
    P("  IS THE SIGN ONE EPISODE?  (the obvious skeptic question -- 2020 is huge)")
    em = et["mean"].values if K else np.array([])
    es = et["sum"].values if K else np.array([])
    n_pos = int((em > 0).sum())
    P(f"    episodes whose SHORT leg made money (mean > 0): {n_pos}/{K} = "
      f"{n_pos/max(K,1):.1%}   <- if the short edge were real this would be well over half")
    P(f"    per-episode short-leg mean (pts): median {np.median(em):+.3f}  "
      f"p25 {np.percentile(em,25):+.3f}  p75 {np.percentile(em,75):+.3f}")
    P("    LEAVE-ONE-EPISODE-OUT jackknife on the pooled short-leg mean (pts/session):")
    jk = []
    for k in range(K):
        keep = (eids >= 0) & (eids != k)
        jk.append(float(np.nanmean(short_pts[keep])))
    jk = np.asarray(jk)
    worst = int(np.argmax(jk))
    P(f"      full-sample {mean_short_pts:+.4f}   jackknife range [{jk.min():+.4f}, "
      f"{jk.max():+.4f}]   episodes that flip the sign to >= "
      f"+{C.BREAKEVEN_PTS_PRIMARY:.4f}: {int((jk >= C.BREAKEVEN_PTS_PRIMARY).sum())}")
    P(f"      dropping the single most favourable-to-drop episode "
      f"({et.iloc[worst]['start'].date()}..{et.iloc[worst]['end'].date()}, "
      f"{int(et.iloc[worst]['n_sessions'])} sess) still leaves {jk[worst]:+.4f} pts")
    n_flip = int((jk >= C.BREAKEVEN_PTS_PRIMARY).sum())
    if n_flip == 0:
        P("    -> NO single episode can be removed to make the short leg clear its cost.")
        P("       The verdict below does not rest on one episode (e.g. March 2020).")
    else:
        P(f"    -> WARNING: {n_flip} single-episode deletion(s) DO flip the short leg above")
        P("       its cost floor. The verdict below IS one-episode fragile -- say so.")

    # ---- the three arms -------------------------------------------------------
    tab = C.three_arms(pf, state_col, high_state=high_state, low_state=low_state,
                       ret_col="rth_ret_pts", date_col="session_date", gap_days=GAP_DAYS)
    P("")
    P("  THREE ARMS -- TOTAL dollars, 1 contract, one round turn per traded session")
    for ln in C.format_arms(tab).split("\n"):
        P("  " + ln)

    row = lambda a, l: tab[(tab["arm"] == a) & (tab["long_leg"] == l)].iloc[0]
    n_sess = int(row("BASE_always_long", "-")["n_sessions"])

    P("")
    P(f"  PER-SESSION dollars (total net / {n_sess:,} common-population sessions) and")
    P("  PER-TRADE dollars (total net / that arm's own traded sessions), at each cost line")
    P(f"    {'arm':<17s} {'long_leg':<9s} {'trades':>7s}"
      + "".join(f" {nm.split('_')[1]+'/sess':>13s} {nm.split('_')[1]+'/trade':>14s}"
                for nm in C.COST_NAMES))
    per_sess = {}
    for _, r in tab.iterrows():
        cells = ""
        for nm in C.COST_NAMES:
            ps = r[nm] / n_sess
            pt = r[nm] / r["n_trades"] if r["n_trades"] else np.nan
            cells += f" {ps:>13.3f} {pt:>14.3f}"
            per_sess[(r["arm"], r["long_leg"], nm)] = ps
        P(f"    {r['arm']:<17s} {r['long_leg']:<9s} {int(r['n_trades']):>7,}" + cells)

    # ---- bootstrap CIs --------------------------------------------------------
    blocks_all = alternating_blocks(hi, dates, gap_days=GAP_DAYS)
    P("")
    P("  EPISODE-BLOCK BOOTSTRAP -- 95% CI of MEAN NET DOLLARS PER SESSION")
    P("    (S) resamples WHOLE HIGH-STATE EPISODES, the unit the brief mandates.")
    P("    (R)/(F)/(BASE) trade outside the high state, so they resample the FULL-TIMELINE")
    P("    ALTERNATING BLOCKS: every high episode is one block, every non-high stretch")
    P("    between two episodes is one block.  Same clustering, complete coverage.")
    P(f"    n_draws = {NDRAW:,}, seed = {SEED}")
    P("")
    P(f"    {'arm':<17s} {'long_leg':<9s} {'unit':<10s} {'blocks':>7s} {'cost':<20s} "
      f"{'mean$/sess':>11s} {'CI_lo':>9s} {'CI_hi':>9s} {'p':>7s} {'excl0':>6s}")

    cis = {}
    arms_spec = [
        ("BASE_always_long", "-", np.where(valid, 1.0, 0.0)),
        ("R_router", "low_only", np.where(lo, 1.0, np.where(hi, -1.0, 0.0))),
        ("F_filter", "low_only", np.where(lo, 1.0, 0.0)),
        ("R_router", "non_high", np.where(nonhi, 1.0, np.where(hi, -1.0, 0.0))),
        ("F_filter", "non_high", np.where(nonhi, 1.0, 0.0)),
        ("S_short_only", "-", np.where(hi, -1.0, 0.0)),
    ]
    for arm, leg, pos in arms_spec:
        traded = valid & (pos != 0)
        signed = np.where(traded, pos * np.nan_to_num(ret, nan=0.0), np.nan)
        if arm == "S_short_only":
            unit, bid = "episode", eids
            keep = eids >= 0
        else:
            unit, bid = "alt-block", blocks_all
            keep = valid
        for cost, nm in zip(C.COSTS, C.COST_NAMES):
            net = C.net_per_session(signed, cost, traded=traded)
            v = np.where(keep, net, np.nan)
            s = boot_ci(v, np.where(keep, bid, -1))
            cis[(arm, leg, nm)] = s
            P(f"    {arm:<17s} {leg:<9s} {unit:<10s} {s['K']:>7d} {nm:<20s} "
              f"{s['observed']:>11.3f} {s['ci_lo']:>9.3f} {s['ci_hi']:>9.3f} "
              f"{s['p_two_sided']:>7.3f} {str(s['excludes_zero']):>6s}")

    # ---- router vs filter, explicitly -----------------------------------------
    P("")
    P("  ROUTER vs FILTER -- the costume test, at the PRIMARY cost line")
    nmP = C.COST_NAMES[1]
    for leg in ("low_only", "non_high"):
        nR = row("R_router", leg)[nmP]
        nF = row("F_filter", leg)[nmP]
        nS = row("S_short_only", "-")[nmP]
        P(f"    long_leg={leg:<9s}  net(R)=${nR:>12,.0f}   net(F)=${nF:>12,.0f}   "
          f"net(R)-net(F)=${nR-nF:>12,.0f}   net(S)=${nS:>12,.0f}   "
          f"identity |diff|={abs((nR-nF)-nS):.6f}")
    P("    R - F == S exactly (algebra, asserted above).  So 'is the router distinguishable")
    P("    from the filter' and 'is net(S) distinguishable from zero' are ONE test.  The CI")
    P("    on the S row above IS the router-vs-filter test.")

    # ---- placebo --------------------------------------------------------------
    ret_v = np.where(valid, ret, np.nan)
    pl = circular_shift_placebo(hi.astype(bool), np.nan_to_num(ret_v, nan=0.0),
                                C.COST_PRIMARY)
    ii = iid_short_placebo(int(valid.sum()), int(hi.sum()), ret[valid], C.COST_PRIMARY)
    P("")
    P("  RATE-MATCHED PLACEBO for arm (S), at $20.65 -- total net dollars")
    P(f"    PRIMARY, dependence-preserving: EXHAUSTIVE CIRCULAR SHIFT, {pl['n_shifts']:,} shifts")
    P(f"      identical short count and identical episode block structure on every shift")
    P(f"      observed net(S)        ${pl['obs_total']:>12,.0f}")
    P(f"      placebo median         ${pl['p50']:>12,.0f}")
    P(f"      placebo 95th pct       ${pl['p95']:>12,.0f}")
    P(f"      placebo 99th pct       ${pl['p99']:>12,.0f}")
    P(f"      observed percentile     {pl['pct_rank']:>12.1%}      "
      f"one-sided p = {pl['p_one_sided']:.4f}")
    P(f"    SECONDARY (weaker bar, clustering destroyed -- do NOT adjudicate on this):")
    P(f"      i.i.d. random-short placebo median ${ii['p50']:>12,.0f}   "
      f"95th pct ${ii['p95']:>12,.0f}   sd ${ii['sd']:>10,.0f}")

    # ---- gates ----------------------------------------------------------------
    sS = cis[("S_short_only", "-", nmP)]
    g = {}
    g["G1"] = dict(
        gate="mean gross short-leg drift clears the primary cost",
        spec=f"mean short-leg pts <= -{C.BREAKEVEN_PTS_PRIMARY:.4f}"
             f"  (i.e. short-leg gross >= +{C.BREAKEVEN_PTS_PRIMARY:.4f})",
        obs=f"{mean_short_pts:+.4f} pts",
        ok=bool(mean_short_pts >= C.BREAKEVEN_PTS_PRIMARY))
    g["G2"] = dict(
        gate="net(S) at $20.65 is positive",
        spec="total net(S) > $0",
        obs=f"${row('S_short_only','-')[nmP]:,.0f}",
        ok=bool(row("S_short_only", "-")[nmP] > 0))
    g["G3"] = dict(
        gate="episode-block 95% CI of mean net(S)/session excludes zero, positive side",
        spec="ci_lo > 0",
        obs=f"mean {sS['observed']:.3f}  CI [{sS['ci_lo']:.3f}, {sS['ci_hi']:.3f}]  "
            f"K={sS['K']}",
        ok=bool(sS["ci_lo"] > 0))
    g["G4"] = dict(
        gate="net(S) beats the rate-matched circular-shift placebo",
        spec="observed > placebo 95th percentile",
        obs=f"obs ${pl['obs_total']:,.0f} vs p95 ${pl['p95']:,.0f}  "
            f"(pctile {pl['pct_rank']:.1%})",
        ok=bool(pl["obs_total"] > pl["p95"]))
    idmax = max(abs((row("R_router", leg)[nmP] - row("F_filter", leg)[nmP])
                    - row("S_short_only", "-")[nmP]) for leg in ("low_only", "non_high"))
    g["G5"] = dict(
        gate="router distinguishable from filter (identity-equivalent to G3)",
        spec="R - F == S asserted, and G3 PASS",
        obs=f"|R-F-S| = {idmax:.6f}; G3 = {'PASS' if g['G3']['ok'] else 'FAIL'}",
        ok=bool(idmax < 1e-6 and g["G3"]["ok"]))

    P("")
    P("  GATE TABLE (printed by the program)")
    P(f"    {'gate':<5s} {'description':<62s} {'spec':<44s} {'observed':<46s} {'verdict':<7s}")
    for k in ("G1", "G2", "G3", "G4", "G5"):
        v = g[k]
        P(f"    {k:<5s} {v['gate']:<62s} {v['spec']:<44s} {v['obs']:<46s} "
          f"{'PASS' if v['ok'] else 'FAIL':<7s}")
    n_pass = sum(1 for k in g if g[k]["ok"])
    P(f"    -> {n_pass}/5 PASS")

    return dict(
        label=label, state_col=state_col, K=K, rho=rho, K_eff=Ke, n_sess=n_sess,
        n_high=int(hi.sum()), mean_short_pts=mean_short_pts, tab=tab, cis=cis,
        per_sess=per_sess, placebo=pl, gates=g, n_pass=n_pass,
        span=(dates[valid].min().date(), dates[valid].max().date()))


# ==================================================================================
# main
# ==================================================================================
def main() -> int:
    H("G3_VOLSHORT01 -- SPEC: VIX TERM STRUCTURE AND VOL-OF-VOL")
    P("EVIDENCE STATUS: DISCOVERY_CONTAMINATED.  This is a RULE PROPOSAL, not a result.")
    P("The one-shot confirmation window 2022-01-01 -> 2026-07-31 is UNSPENT and UNREAD.")

    H("[0] THE WALL -- 2022-01-01")
    p = pd.read_parquet(PANEL)
    p["session_date"] = pd.to_datetime(p["session_date"])
    p = p.sort_values("session_date").reset_index(drop=True)
    assert_wall(p, "panel_pre2022")
    mx = p["session_date"].max()
    assert mx < WALL, f"WALL BREACH: max session_date {mx} >= {WALL}"
    P(f"  hard assert: max(session_date) = {mx.date()} < {WALL.date()}  -> PASS")
    P(f"  rows = {len(p):,}   span {p['session_date'].min().date()} .. {mx.date()}")
    P("  NO session on or after 2022-01-01 is read, loaded, aggregated or counted anywhere")
    P("  in this script.  No CrossTrade / NinjaTrader call is made.")

    H("[1] RATIOS -- scale-free by construction")
    p["ts9"] = p["vix9d"] / p["vix"]
    p["ts3"] = p["vix"] / p["vix3m"]
    p["vov"] = p["vvix"] / p["vix"]
    P("  ts9 = VIX9D / VIX    very-short vs short end")
    P("  ts3 = VIX   / VIX3M  backwardation (>1) vs contango (<1)")
    P("  vov = VVIX  / VIX    vol-of-vol relative to vol")
    P("")
    P("  NOTE ON WHICH INDEX.  VXN is the Nasdaq-100 vol index and is the right EX-ANTE")
    P("  implied variance for NQ.  But the certified free Cboe complex has NO 9-day and NO")
    P("  3-month NASDAQ analogue -- VIX9D and VIX3M are S&P-500 tenors.  A term-structure")
    P("  ratio must therefore be built inside ONE family, so all three ratios here are")
    P("  S&P-family.  corr(VIX, VXN) = "
      f"{p[['vix','vxn']].corr().iloc[0,1]:.3f} on the joint sample, so the S&P surface is a")
    P("  close proxy for the NASDAQ level -- but this is a REAL substitution and the frozen")
    P("  rule must name it.")
    P("")
    P(f"    {'ratio':<6s} {'n':>6s} {'first':<12s} {'mean':>8s} {'sd':>8s} {'min':>8s} "
      f"{'max':>8s} {'corr_VIX':>9s}")
    for c in ("ts9", "ts3", "vov"):
        s = p[c].dropna()
        P(f"    {c:<6s} {len(s):>6,} {str(p.loc[p[c].notna(),'session_date'].min().date()):<12s} "
          f"{s.mean():>8.4f} {s.std():>8.4f} {s.min():>8.4f} {s.max():>8.4f} "
          f"{p[[c,'vix']].corr().iloc[0,1]:>9.3f}")
    P("")
    P("  corr(vov, VIX) = "
      f"{p[['vov','vix']].corr().iloc[0,1]:.3f}.  This is computed from EX-ANTE PREDICTOR")
    P("  COLUMNS ONLY -- no return was consulted -- and it says the HIGH tercile of vov is a")
    P("  CALM state, not a stress state.  The mechanism under test is about high implied")
    P("  variance, so vov is run at BOTH ends and counts as TWO tests in the family.")

    H("[2] STATES -- causal rolling-252 tercile, strictly prior observations only")
    for c in ("ts9", "ts3", "vov"):
        p[f"st_{c}"] = C.causal_tercile(p[c].values, window=WINDOW)
    P("  causal_tercile(window=252): the cutoffs at position i are the 1/3 and 2/3 quantiles")
    P("  of positions [i-252, i).  The value at i is classified but never enters its own")
    P("  cutoff.  common.py's future-shuffle leak test covers this (47/47 PASS).")
    P("  Terciles are computed on the FULL chronological panel (all 4,106 rows) so the")
    P("  trailing window sees every prior trading day; the EVALUATION population is then")
    P("  restricted to FULL sessions.  Both steps use only pre-09:30 information.")
    P("")
    P(f"    {'state':<10s} {'defined':>8s} {'low':>7s} {'mid':>7s} {'high':>7s} {'first_defined':<14s}")
    for c in ("ts9", "ts3", "vov"):
        s = p[f"st_{c}"]
        P(f"    st_{c:<7s} {s.notna().sum():>8,} {int((s==0).sum()):>7,} "
          f"{int((s==1).sum()):>7,} {int((s==2).sum()):>7,} "
          f"{str(p.loc[s.notna(),'session_date'].min().date()):<14s}")

    H("[3] POPULATION")
    pf = p[(p["session_quality"] == "FULL") & p["rth_ret_pts"].notna()].reset_index(drop=True)
    assert_wall(pf[["session_date", "prev_session_date"]], "FULL-population")
    assert pf["session_date"].max() < WALL
    P(f"  session_quality == FULL and rth_ret_pts not NaN : {len(pf):,} sessions")
    P(f"  span {pf['session_date'].min().date()} .. {pf['session_date'].max().date()}")
    P(f"  mean rth_ret_pts (always-long, gross) = {pf['rth_ret_pts'].mean():+.4f} pts/session")
    P("  Excluded: 134 SHORT_SESSION (exchange half days -- no 16:00 bar, and a stale")
    P("  implied-vol reading) and 25 GAPPY (substrate holes).  Stated, not discovered.")

    H("[4] MULTIPLE COMPARISONS -- declared before the tables")
    P("  Family evaluated in this specification:")
    P("    1. ts9 high tercile   (short the high state)")
    P("    2. ts3 high tercile   (short the high state)   <-- PRE-DESIGNATED HEADLINE")
    P("    3. vov high tercile   (short the high state)")
    P("    4. vov low  tercile   (short the low state -- the stress end of vov)")
    P("  x 2 long-leg conventions (low_only, non_high) reported for each.")
    P("  FAMILY SIZE = 4 states.  A per-state 5% test therefore has a family-wise error rate")
    P("  near 19% if any-of-four is treated as a hit.  Bonferroni within this specification")
    P("  alone is alpha = 0.0125.  The wave as a whole runs several specifications, so the")
    P("  true family is larger still and the frozen rule must be ONE state, named in advance.")

    results = {}
    results["ts9_high"] = evaluate(pf, "st_ts9", "(a) ts9 = VIX9D/VIX, HIGH tercile shorted",
                                   2, 0, "ts9")
    results["ts3_high"] = evaluate(pf, "st_ts3",
                                   "(b) ts3 = VIX/VIX3M, HIGH tercile shorted "
                                   "[PRE-DESIGNATED HEADLINE]", 2, 0, "ts3")
    results["vov_high"] = evaluate(pf, "st_vov", "(c) vov = VVIX/VIX, HIGH tercile shorted "
                                   "(this is the CALM end -- see corr)", 2, 0, "vov")
    results["vov_low"] = evaluate(pf, "st_vov", "(d) vov = VVIX/VIX, LOW tercile shorted "
                                  "(the STRESS end of vov)", 0, 2, "vov")

    # ==============================================================================
    H("[5] CROSS-STATE SUMMARY -- all four, at the PRIMARY cost line $20.65/ctrRT")
    nmP = C.COST_NAMES[1]
    P(f"  {'state':<38s} {'n_hi':>6s} {'K':>4s} {'rho':>6s} {'K_eff':>6s} "
      f"{'shortpts':>9s} {'net(S)$':>11s} {'S$/sess':>9s} {'S CI_lo':>9s} {'S CI_hi':>9s} "
      f"{'plc_pct':>8s} {'gates':>6s}")
    for k, r in results.items():
        tab = r["tab"]
        nS = tab[tab["arm"] == "S_short_only"].iloc[0][nmP]
        s = r["cis"][("S_short_only", "-", nmP)]
        P(f"  {r['label'][:38]:<38s} {r['n_high']:>6,} {r['K']:>4d} {r['rho']:>6.3f} "
          f"{r['K_eff']:>6.2f} {r['mean_short_pts']:>+9.3f} {nS:>11,.0f} "
          f"{s['observed']:>9.3f} {s['ci_lo']:>9.3f} {s['ci_hi']:>9.3f} "
          f"{r['placebo']['pct_rank']:>7.1%} {r['n_pass']:>4d}/5")

    P("")
    P("  ROUTER vs FILTER across all four states (net dollars per COMMON-POPULATION session)")
    P(f"  {'state':<38s} {'leg':<9s} {'R$/sess':>9s} {'F$/sess':>9s} {'R-F':>9s} "
      f"{'BASE$/sess':>11s}")
    for k, r in results.items():
        for leg in ("low_only", "non_high"):
            R = r["per_sess"][("R_router", leg, nmP)]
            F = r["per_sess"][("F_filter", leg, nmP)]
            B = r["per_sess"][("BASE_always_long", "-", nmP)]
            P(f"  {r['label'][:38]:<38s} {leg:<9s} {R:>9.3f} {F:>9.3f} {R-F:>9.3f} "
              f"{B:>11.3f}")

    # ==============================================================================
    H("[6] VERDICT")
    head = results["ts3_high"]
    P("  PRE-DESIGNATED HEADLINE STATE: (b) ts3 = VIX/VIX3M, high tercile shorted.")
    P("")
    hg = head["gates"]
    P(f"    {'gate':<5s} {'description':<62s} {'verdict':<7s}")
    for kk in ("G1", "G2", "G3", "G4", "G5"):
        P(f"    {kk:<5s} {hg[kk]['gate']:<62s} {'PASS' if hg[kk]['ok'] else 'FAIL':<7s}")
    P("")
    all_pass = all(hg[kk]["ok"] for kk in ("G1", "G2", "G3", "G4"))
    any_pass = any(r["gates"]["G1"]["ok"] and r["gates"]["G2"]["ok"] for r in results.values())
    if all_pass:
        v = "PROMISING"
    elif any_pass:
        v = "AMBIGUOUS"
    else:
        v = "DEAD"
    P(f"  HEADLINE GATES G1-G4: {'ALL PASS' if all_pass else 'NOT ALL PASS'}")
    P(f"  any state in the family with G1 AND G2 PASS: {any_pass}")
    P(f"  VERDICT (computed, not asserted): {v}")
    P("")
    P("  MAGNITUDE, stated plainly:")
    for k, r in results.items():
        m = r["mean_short_pts"]
        P(f"    {r['label'][:52]:<52s} short-leg drift {m:+.3f} pts vs a "
          f"{C.BREAKEVEN_PTS_PRIMARY:.3f} pt cost floor -> "
          f"{'CLEARS' if m >= C.BREAKEVEN_PTS_PRIMARY else 'DOES NOT CLEAR'}")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    body = ("\n".join(_LINES) + "\n").encode("utf-8")
    with open(OUT, "wb") as f:
        f.write(body)
    assert os.path.getsize(OUT) > 0
    print(f"\nwrote {OUT}  ({len(body):,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
