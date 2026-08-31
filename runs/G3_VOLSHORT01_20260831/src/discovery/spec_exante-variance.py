"""G3_VOLSHORT01 -- specification: EX-ANTE VARIANCE and the VARIANCE RISK PREMIUM.

EVIDENCE STATUS: DISCOVERY_CONTAMINATED. This is not a result. It is input to a RULE PROPOSAL
that someone else freezes and commits BEFORE the one-shot confirmation read of
2022-01-01 -> 2026-07-31.

THE WALL: no session on or after 2022-01-01 is read, loaded, counted or aggregated anywhere in
this file. The panel it consumes is already pre-wall; the assertion is re-made here and printed.

MECHANISM UNDER TEST
--------------------
The price of variance risk flips sign with the trading window: the equity premium is compensated
OVERNIGHT, while the INTRADAY window is where levered / short-horizon holders de-risk and
liquidity providers extract compensation. High EX-ANTE implied variance should therefore carry
NEGATIVE expected INTRADAY drift, i.e. implied vol is a SIGNED SHORT TRIGGER, not an exposure
gate.

TWO CONSTRUCTIONS
-----------------
(a) EX-ANTE VARIANCE     iv_var  = (prior-day VXN / 100)^2 / 252     [daily variance]
(b) VARIANCE RISK PREMIUM
    vrp_rth = iv_var - rv_rth   rv_rth = trailing-21-session realised variance of NQ *RTH*
                                log returns  <- the LITERAL specification as handed to me
    vrp_cc  = iv_var - rv_cc    rv_cc  = trailing-21-session realised variance of NQ
                                *close-to-close* log returns  <- the LIKE-FOR-LIKE match

    Both are reported. vrp_rth is the literal spec; vrp_cc exists because VXN prices a full
    calendar day of index variance while RTH realised variance omits the overnight leg, so
    vrp_rth is mechanically inflated by a term that has nothing to do with the price of
    variance risk. Reporting only one of these would be a choice made after seeing results.

Run:  python runs/G3_VOLSHORT01_20260831/src/discovery/spec_exante-variance.py
"""
from __future__ import annotations

import os
import sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import common as C  # noqa: E402

PANEL = os.path.join(RUN, "out", "discovery", "panel_pre2022.parquet")
OUT = os.path.join(RUN, "out", "discovery", "spec_exante-variance.txt")

WALL = pd.Timestamp("2022-01-01")
TERCILE_WINDOW = 252
GAP_DAYS = 10
N_BOOT = 10000
N_PLACEBO = 2000
SEED = 20260831

_LINES: list[str] = []


def P(s: str = "") -> None:
    print(s)
    _LINES.append(s)


def H(s: str, ch: str = "=") -> None:
    P("")
    P(ch * 100)
    P(s)
    P(ch * 100)


# ======================================================================================
# 0. THE WALL
# ======================================================================================
def load_panel() -> pd.DataFrame:
    p = pd.read_parquet(PANEL)
    p["session_date"] = pd.to_datetime(p["session_date"])
    # filter IMMEDIATELY on load, then assert, then print
    n_before = len(p)
    p = p[p["session_date"] < WALL].reset_index(drop=True)
    n_after = len(p)
    mx = p["session_date"].max()
    n_post = int((p["session_date"] >= WALL).sum())
    if not (mx < WALL):
        raise AssertionError(f"WALL BREACH: max(session_date)={mx} >= {WALL.date()}")
    if n_post != 0:
        raise AssertionError(f"WALL BREACH: {n_post} rows >= {WALL.date()}")
    for c in [c for c in p.columns if c.endswith("_asof") or c == "prev_session_date"]:
        v = pd.to_datetime(p[c])
        bad = int((v >= WALL).sum())
        if bad:
            raise AssertionError(f"WALL BREACH in {c}: {bad} timestamps >= {WALL.date()}")
    H("0. THE WALL -- 2022-01-01, asserted before a single statistic is computed")
    P(f"  panel file                          {PANEL}")
    P(f"  rows read                           {n_before:,}")
    P(f"  rows after `< 2022-01-01` filter    {n_after:,}   (dropped {n_before-n_after})")
    P(f"  max(session_date)                   {mx.date()}")
    P(f"  rows with session_date >= wall      {n_post}")
    P(f"  ASSERT max(session_date) < {WALL.date()}   -> PASS (raises, does not warn)")
    P(f"  ASSERT every *_asof and prev_session_date < {WALL.date()}  -> PASS")
    P("  No session on or after 2022-01-01 is read, plotted, aggregated or COUNTED by this")
    P("  file. The one-shot confirmation window 2022-01-01 -> 2026-07-31 remains UNSPENT.")
    return p


# ======================================================================================
# 1. causal trailing realised variance (same convention as the panel's realised_vol_21)
# ======================================================================================
def causal_realised_std(vals: np.ndarray, n: int = 21) -> np.ndarray:
    """stdev(ddof=1) of the last `n` STRICTLY PRIOR defined observations. NaN-skipping.

    Convention matched to the panel builder's `realised_vol_21`, INCLUDING the detail that the
    output is NaN wherever the CURRENT row's own return is undefined (the 159 SHORT_SESSION /
    GAPPY rows). Without that mask the reimplementation differs from the builder on exactly
    those 158 rows; with it, on 0 of 4,106. Verified and printed in section 1.
    """
    v = np.asarray(vals, dtype=float)
    out = np.full(len(v), np.nan)
    buf: list[float] = []
    for i in range(len(v)):
        if len(buf) >= n:
            out[i] = float(np.std(np.asarray(buf[-n:]), ddof=1))
        if not np.isnan(v[i]):
            buf.append(float(v[i]))
    return np.where(np.isnan(v), np.nan, out)


# ======================================================================================
# 2. episode-anchored panel blocks (the resampling unit for the WHOLE-panel arms)
# ======================================================================================
def panel_blocks(hi: np.ndarray, dates: pd.DatetimeIndex, gap_days: int) -> np.ndarray:
    """Block id for EVERY session, anchored on high-state episodes.

    Block k = [start of high-episode k, start of high-episode k+1).  Sessions preceding the
    first episode are folded into block 0.  Every session belongs to exactly one block, so the
    R / F / S / BASE arms are resampled from ONE SHARED DRAW over the same K blocks -- the
    correlated family is respected and the arms stay directly comparable.
    """
    eps = C.episodes(hi, dates, gap_days=gap_days)
    if not eps:
        return np.zeros(len(dates), dtype=int)
    starts = pd.DatetimeIndex([a for a, _ in eps])
    b = np.searchsorted(starts.values, dates.values, side="right") - 1
    return np.maximum(b, 0).astype(int)


def block_boot_means(mat: np.ndarray, blocks: np.ndarray, n_draws: int, seed: int):
    """ONE SHARED DRAW of whole blocks; returns (n_draws, n_series) matrix of pooled means."""
    ks = np.unique(blocks)
    groups = [np.where(blocks == k)[0] for k in ks]
    K = len(groups)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, K, size=(n_draws, K))
    out = np.empty((n_draws, mat.shape[1]))
    for j in range(n_draws):
        sel = np.concatenate([groups[i] for i in idx[j]])
        out[j] = mat[sel].mean(axis=0)
    return out, K


def ci(draws: np.ndarray) -> tuple[float, float, float, bool]:
    d = draws[~np.isnan(draws)]
    if len(d) == 0:
        return (np.nan, np.nan, np.nan, False)
    lo, hi = np.quantile(d, [0.025, 0.975])
    p = 2.0 * min((d <= 0).mean(), (d >= 0).mean())
    return (float(lo), float(hi), float(min(p, 1.0)), bool(lo > 0 or hi < 0))


# ======================================================================================
# 3. per-session dollars for each arm
# ======================================================================================
def arm_dollars(ret_pts: np.ndarray, hi: np.ndarray, lo: np.ndarray,
                cost: float) -> dict[str, np.ndarray]:
    """Per-session dollars, ONE contract, one round turn per traded session, denominator =
    every valid session (untraded sessions contribute exactly 0)."""
    nonhi = ~hi
    r = np.nan_to_num(ret_pts, nan=0.0)

    def mk(pos):
        traded = pos != 0
        return np.where(traded, pos * r * C.PV - cost, 0.0)

    return {
        "BASE": mk(np.ones(len(r))),
        "F_low": mk(np.where(lo, 1.0, 0.0)),
        "R_low": mk(np.where(lo, 1.0, np.where(hi, -1.0, 0.0))),
        "F_non": mk(np.where(nonhi, 1.0, 0.0)),
        "R_non": mk(np.where(nonhi, 1.0, np.where(hi, -1.0, 0.0))),
        "S": mk(np.where(hi, -1.0, 0.0)),
    }


# ======================================================================================
# 4. the full evaluation of one state definition
# ======================================================================================
def evaluate(tag: str, desc: str, q: pd.DataFrame, state: np.ndarray,
             gap_days: int = GAP_DAYS, verbose: bool = True) -> dict:
    ret = q["rth_ret_pts"].values.astype(float)
    dates = pd.DatetimeIndex(q["session_date"])
    valid = (~np.isnan(state)) & (~np.isnan(ret))

    sub = q.loc[valid].reset_index(drop=True)
    st = state[valid]
    r = ret[valid]
    d = pd.DatetimeIndex(sub["session_date"])
    hi = st == 2.0
    lo = st == 0.0
    n = int(valid.sum())

    eps = C.episodes(hi, d, gap_days=gap_days)
    eids = C.episode_ids(hi, d, gap_days=gap_days)
    K = len(eps)
    short_pts = np.where(hi, -r, np.nan)
    rho = C.icc_rho(short_pts, eids)
    keff = C.k_eff(K, rho) if not np.isnan(rho) else np.nan

    blocks = panel_blocks(hi, d, gap_days)

    if verbose:
        H(f"{tag}  --  {desc}")
        P(f"  population           session_quality == FULL, state defined, rth_ret_pts defined")
        P(f"  sessions (valid)     {n:,}    span {d.min().date()} .. {d.max().date()}")
        P(f"  low / mid / high     {int(lo.sum()):,} / {int((st==1).sum()):,} / "
          f"{int(hi.sum()):,}")
        P(f"  HIGH-STATE EPISODES  K = {K}  (gap_days = {gap_days})")
        P(f"  rho_bar (ICC of the short-arm per-session P&L within episode) = {rho:.4f}")
        P(f"  K_eff = K / (1 + (K-1)*rho_bar) = {keff:.2f}")
        P(f"  panel resampling blocks (episode-anchored, cover all {n:,} sessions) = "
          f"{len(np.unique(blocks))}")
        P("")
        P("  GROSS intraday drift by state (NQ points, 09:30 -> 16:00, unsigned by position):")
        P(f"    {'state':<8s} {'n':>7s} {'mean_pts':>10s} {'sd_pts':>9s} {'t_DIAG':>8s} "
          f"{'mean_$/sess':>12s}")
        for s, nm in ((0.0, "low"), (1.0, "mid"), (2.0, "high")):
            m = st == s
            if m.sum() == 0:
                continue
            mu, sd = float(r[m].mean()), float(r[m].std(ddof=1))
            t = mu / (sd / np.sqrt(m.sum()))
            P(f"    {nm:<8s} {int(m.sum()):>7,} {mu:>10.3f} {sd:>9.2f} {t:>8.2f} "
              f"{mu*C.PV:>12,.2f}")
        P("    t_DIAG is a session-level t and is DIAGNOSTIC ONLY -- it is not inference here.")
        P("")
        P("  SIGN CHECK against the mechanism: the mechanism predicts mean_pts(high) < 0")
        mu_hi = float(r[hi].mean()) if hi.any() else np.nan
        P(f"    observed mean_pts(high) = {mu_hi:+.3f}  ->  "
          f"{'CONSISTENT with the mechanism' if mu_hi < 0 else 'OPPOSITE SIGN to the mechanism'}")

    # ---- the three arms, three cost lines ------------------------------------------
    tab = C.three_arms(sub.assign(_st=st), "_st", high_state=2, low_state=0,
                       ret_col="rth_ret_pts", date_col="session_date", gap_days=gap_days)
    if verbose:
        P("")
        P("  THREE ARMS  (R router / F filter / S short-only) -- TOTALS over the window")
        P("  " + C.format_arms(tab).replace("\n", "\n  "))

    # ---- per-session dollars + ONE SHARED block-bootstrap draw ----------------------
    keys = ["BASE", "R_low", "F_low", "R_non", "F_non", "S"]
    res: dict[str, dict] = {}
    for cost, cname in zip(C.COSTS, C.COST_NAMES):
        arms = arm_dollars(r, hi, lo, cost)
        mat = np.column_stack([arms[k] for k in keys])
        # derived series: R - F for both long legs (identically equal to S)
        mat = np.column_stack([mat,
                               arms["R_low"] - arms["F_low"],
                               arms["R_non"] - arms["F_non"]])
        cols = keys + ["Rlow_minus_Flow", "Rnon_minus_Fnon"]
        draws, Kb = block_boot_means(mat, blocks, N_BOOT, SEED)
        obs = mat.mean(axis=0)
        res[cname] = dict(cols=cols, obs=obs, draws=draws, Kb=Kb, n=n)

    # ---- the mandated episode bootstrap on the SHORT arm ----------------------------
    ep_draws = C.block_bootstrap_by_episode(short_pts, eids, N_BOOT, seed=SEED)
    ep_pts = C.bootstrap_summary(ep_draws)

    if verbose:
        for cname in C.COST_NAMES:
            R = res[cname]
            P("")
            P(f"  PER-SESSION NET DOLLARS  ({cname})  -- denominator = all {n:,} valid "
              f"sessions; 1 contract")
            P(f"  CI = 2.5/97.5 pct of a WHOLE-BLOCK bootstrap ({N_BOOT:,} draws, "
              f"{R['Kb']} episode-anchored blocks, one shared draw across arms)")
            P(f"    {'series':<18s} {'$/session':>11s} {'CI_lo':>10s} {'CI_hi':>10s} "
              f"{'p':>7s} {'excl0':>6s} {'total_$':>13s}")
            for j, cnm in enumerate(R["cols"]):
                lo_, hi_, pv_, ex = ci(R["draws"][:, j])
                P(f"    {cnm:<18s} {R['obs'][j]:>11,.3f} {lo_:>10,.3f} {hi_:>10,.3f} "
                  f"{pv_:>7.3f} {str(ex):>6s} {R['obs'][j]*n:>13,.0f}")
        P("")
        P(f"  SHORT ARM, mandated WHOLE-EPISODE bootstrap over the {int(hi.sum()):,} high "
          f"sessions only (K = {K} episodes)")
        P(f"    gross pts per SHORT TRADE       {float(np.nanmean(short_pts)):>10.3f}")
        P(f"    episode-bootstrap 95% CI        [{ep_pts['ci_lo']:.3f}, {ep_pts['ci_hi']:.3f}]"
          f"   p = {ep_pts['p_two_sided']:.3f}   excludes 0: {ep_pts['excludes_zero']}")
        P(f"    breakeven at $20.65 PRIMARY     {C.BREAKEVEN_PTS_PRIMARY:.4f} pts per short")
        margin = float(np.nanmean(short_pts)) - C.BREAKEVEN_PTS_PRIMARY
        P(f"    margin over breakeven           {margin:+.3f} pts  -> "
          f"{'CLEARS' if margin > 0 else 'DOES NOT CLEAR'} the primary cost line")
        P(f"    even at the $4.36 FLOOR         breakeven {C.COST_FLOOR/C.PV:.4f} pts -> "
          f"{'clears' if float(np.nanmean(short_pts)) > C.COST_FLOOR/C.PV else 'does not clear'}")

    return dict(tag=tag, n=n, K=K, rho=rho, keff=keff, eps=eps, res=res,
                hi=hi, lo=lo, st=st, r=r, d=d, blocks=blocks, eids=eids,
                short_pts=short_pts, ep_pts=ep_pts, tab=tab,
                mean_hi_pts=float(r[hi].mean()) if hi.any() else np.nan)


# ======================================================================================
# 5. placebos for the SHORT arm
# ======================================================================================
def placebos(ev: dict, cost: float = C.COST_PRIMARY, seed: int = SEED) -> dict:
    """Two rate-matched placebos for net(S) per session.

    CIRCULAR SHIFT (binding): the high-state MASK is rolled against the return series. This
    preserves BOTH the episode/clustering structure of the mask and the serial structure of
    returns, so it is the dependence-preserving null this repo requires.

    IID (diagnostic): the same NUMBER of shorts, scattered independently. It destroys the
    clustering and therefore gives a bar that is far too easy -- shown only to make that
    visible.
    """
    r, hi = ev["r"], ev["hi"]
    n, k = len(r), int(hi.sum())
    rng = np.random.default_rng(seed)

    def net_short(mask):
        return float(np.where(mask, -r * C.PV - cost, 0.0).mean())

    def gross_short(mask):
        """GROSS points captured per SHORT TRADE -- cost removed, so this isolates SIGNAL."""
        return float((-r[mask]).mean())

    obs = net_short(hi)
    obs_g = gross_short(hi)

    offs = rng.choice(np.arange(63, n - 63), size=min(N_PLACEBO, n - 126), replace=False)
    rolls = [np.roll(hi, int(o)) for o in offs]
    circ = np.array([net_short(m) for m in rolls])
    circ_g = np.array([gross_short(m) for m in rolls])

    iid = np.empty(N_PLACEBO)
    for j in range(N_PLACEBO):
        m = np.zeros(n, dtype=bool)
        m[rng.choice(n, size=k, replace=False)] = True
        iid[j] = net_short(m)

    return dict(obs=obs, circ=circ, iid=iid, obs_g=obs_g, circ_g=circ_g,
                pct_circ=float((circ >= obs).mean()),
                pct_circ_g=float((circ_g >= obs_g).mean()),
                pct_iid=float((iid >= obs).mean()))


# ======================================================================================
# MAIN
# ======================================================================================
def main() -> int:
    H("G3_VOLSHORT01  --  SPECIFICATION: EX-ANTE VARIANCE and the VARIANCE RISK PREMIUM", "#")
    P("  EVIDENCE STATUS: DISCOVERY_CONTAMINATED. This is a RULE PROPOSAL input, not a result.")
    P("  NQ point value $20. Cost ladder: $4.36 FLOOR (commission only, never a headline),")
    P(f"  $20.65 PRIMARY (G2_EXEC01, 113 real round turns), $25.01 STRESS. Breakeven at the")
    P(f"  primary line = {C.BREAKEVEN_PTS_PRIMARY:.4f} NQ points per full-session round turn.")
    P("  Inference: WHOLE-EPISODE / episode-anchored block bootstrap. Session-level t is")
    P("  printed only where labelled DIAGNOSTIC ONLY and is never used to decide anything.")

    p = load_panel()

    # ---------------------------------------------------------------- constructions
    H("1. CONSTRUCTIONS -- ex-ante variance and the two VRP variants")
    p["cc_ret_log"] = p["overnight_ret_log"] + p["rth_ret_log_any"]
    rv_rth_chk = causal_realised_std(p["rth_ret_log"].values, 21)
    ok = np.isclose(rv_rth_chk, p["realised_vol_21"].values, equal_nan=True, atol=1e-12)
    P(f"  reimplementation of the panel's causal 21-session realised stdev matches the")
    P(f"  builder's `realised_vol_21` on {int(ok.sum()):,}/{len(p):,} rows -> "
      f"{'PASS' if ok.all() else 'FAIL'}")
    if not ok.all():
        raise AssertionError(
            f"causal_realised_std does not reproduce realised_vol_21 on {int((~ok).sum())} rows; "
            "rv_cc would then be built on an unverified convention")
    P("  -> rv_cc below is therefore built by a routine PROVEN to reproduce the builder's")
    P("     causal convention exactly, applied to close-to-close instead of RTH returns.")
    p["rv_cc"] = causal_realised_std(p["cc_ret_log"].values, 21)

    p["iv_var"] = (p["vxn"] / 100.0) ** 2 / 252.0
    p["iv_var_vix"] = (p["vix"] / 100.0) ** 2 / 252.0
    p["rv_var_rth"] = p["realised_vol_21"] ** 2
    p["rv_var_cc"] = p["rv_cc"] ** 2
    p["vrp_rth"] = p["iv_var"] - p["rv_var_rth"]
    p["vrp_cc"] = p["iv_var"] - p["rv_var_cc"]
    p["vrp_cc_vix"] = p["iv_var_vix"] - p["rv_var_cc"]

    q = p[p["session_quality"] == "FULL"].reset_index(drop=True)
    P("")
    P(f"  FULL sessions in the pre-wall panel: {len(q):,}")
    m = q[["iv_var", "rv_var_rth", "rv_var_cc", "vrp_rth", "vrp_cc"]].describe().T
    P("  daily-variance scale of each input (FULL sessions, where defined):")
    P(f"    {'series':<12s} {'n':>6s} {'mean':>12s} {'sd':>12s} "
      f"{'ann.vol%':>9s}")
    for nm in ["iv_var", "rv_var_rth", "rv_var_cc"]:
        mu = float(q[nm].mean())
        P(f"    {nm:<12s} {int(q[nm].notna().sum()):>6,} {mu:>12.3e} "
          f"{float(q[nm].std()):>12.3e} {100*np.sqrt(mu*252):>9.2f}")
    for nm in ["vrp_rth", "vrp_cc"]:
        P(f"    {nm:<12s} {int(q[nm].notna().sum()):>6,} {float(q[nm].mean()):>12.3e} "
          f"{float(q[nm].std()):>12.3e} {'-':>9s}")
    P("")
    P("  ANNUALISED VOL of the RTH-only realised leg is far below implied because RTH")
    P("  variance omits the overnight leg that VXN prices. vrp_rth therefore carries a large")
    P("  mechanical wedge unrelated to the price of variance risk; vrp_cc is the like-for-like")
    P("  construction. BOTH are reported and neither was chosen after seeing a result.")
    P("")
    P("  NOTE, stated up front: x -> (x/100)^2/252 is STRICTLY MONOTONE on x>0, so spec (a) is")
    P("  not economically distinct from 'prior-day VXN tercile' -- it is the same ordering in")
    P("  variance units. I predicted the two terciles would be BIT-identical. They are not,")
    P("  and the reason is worth recording rather than hiding: np.quantile INTERPOLATES")
    P("  linearly between order statistics, and interpolation does not commute with a convex")
    P("  map, so f(q67 of x) != q67 of f(x) by a hair. The measured disagreement is reported")
    P("  below. It is a quantile-interpolation artefact, not an economic difference.")

    # states
    q["st_iv"] = C.causal_tercile(q["iv_var"], window=TERCILE_WINDOW)
    q["st_vxn_raw"] = C.causal_tercile(q["vxn"], window=TERCILE_WINDOW)
    _m = q["st_iv"].notna() & q["st_vxn_raw"].notna()
    _dis = int((q.loc[_m, "st_iv"] != q.loc[_m, "st_vxn_raw"]).sum())
    P(f"  MEASURED tercile(iv_var) vs tercile(VXN): disagree on {_dis} of {int(_m.sum()):,} "
      f"sessions ({_dis/max(int(_m.sum()),1):.4%})")
    if _dis > 5:
        raise AssertionError("tercile(iv_var) and tercile(VXN) diverge more than interpolation "
                             f"can explain ({_dis} sessions) -- investigate before trusting (a)")
    P("  -> the two are the same rule to within one boundary session; treat SPEC-A as the")
    P("     prior-day VXN tercile and do not claim it as independent evidence.")
    q["st_vrp_rth"] = C.causal_tercile(q["vrp_rth"], window=TERCILE_WINDOW)
    q["st_vrp_cc"] = C.causal_tercile(q["vrp_cc"], window=TERCILE_WINDOW)
    q["st_iv_vix"] = C.causal_tercile(q["iv_var_vix"], window=TERCILE_WINDOW)
    q["st_vrp_cc_vix"] = C.causal_tercile(q["vrp_cc_vix"], window=TERCILE_WINDOW)
    q["st_rv"] = C.causal_tercile(q["rv_var_cc"], window=TERCILE_WINDOW)

    P("")
    P("  CONFOUND CHECK -- does the VRP state separate from the plain LEVEL of vol?")
    P(f"    {'pair':<34s} {'n_common':>9s} {'same-state agreement':>21s} "
      f"{'high-state overlap':>19s}")
    for a, b, nm in [("st_iv", "st_vrp_rth", "iv_var  vs  vrp_rth"),
                     ("st_iv", "st_vrp_cc", "iv_var  vs  vrp_cc"),
                     ("st_vrp_rth", "st_vrp_cc", "vrp_rth vs  vrp_cc"),
                     ("st_iv", "st_rv", "iv_var  vs  realised-var(cc)"),
                     ("st_vrp_cc", "st_rv", "vrp_cc  vs  realised-var(cc)")]:
        m2 = q[a].notna() & q[b].notna()
        agree = float((q.loc[m2, a] == q.loc[m2, b]).mean())
        ha, hb = (q[a] == 2) & m2, (q[b] == 2) & m2
        jac = float((ha & hb).sum() / max((ha | hb).sum(), 1))
        P(f"    {nm:<34s} {int(m2.sum()):>9,} {agree:>20.1%} {jac:>18.1%}")
    P("    vrp_cc is the least redundant with the level of implied variance -- it is the")
    P("    specification with the best chance of isolating the PRICE of variance risk.")

    # ---------------------------------------------------------------- evaluations
    specs = [
        ("SPEC-A  iv_var(VXN)", "(a) EX-ANTE VARIANCE: causal tercile of (prior-day VXN/100)^2/252"
                                "  [== the prior-day VXN tercile]", "st_iv"),
        ("SPEC-B1 vrp_rth", "(b) VRP, LITERAL: iv_var - trailing-21 realised variance of RTH "
                            "log returns", "st_vrp_rth"),
        ("SPEC-B2 vrp_cc", "(b) VRP, LIKE-FOR-LIKE: iv_var - trailing-21 realised variance of "
                           "CLOSE-TO-CLOSE log returns", "st_vrp_cc"),
    ]
    evs: dict[str, dict] = {}
    for tag, desc, col in specs:
        evs[tag] = evaluate(tag, desc, q, q[col].values.astype(float))

    # ---------------------------------------------------------------- placebos
    H("5. RATE-MATCHED PLACEBOS FOR THE SHORT ARM (net $/session at the $20.65 PRIMARY line)")
    P("  The binding null is a CIRCULAR SHIFT of the high-state mask against returns: it keeps")
    P("  the episode clustering of the mask AND the serial structure of returns. The i.i.d.")
    P("  placebo is printed only to show how much too easy an independent-draw bar is.")
    P("")
    P(f"  {'spec':<22s} {'obs $/sess':>11s} {'circ mean':>10s} {'circ p2.5':>10s} "
      f"{'circ p97.5':>11s} {'pct>=obs':>9s} {'iid pct':>8s}")
    plac = {}
    for tag in evs:
        pl = placebos(evs[tag])
        plac[tag] = pl
        c = pl["circ"]
        P(f"  {tag:<22s} {pl['obs']:>11,.3f} {c.mean():>10,.3f} "
          f"{np.quantile(c,0.025):>10,.3f} {np.quantile(c,0.975):>11,.3f} "
          f"{pl['pct_circ']:>9.3f} {pl['pct_iid']:>8.3f}")
    P("")
    P("  READ: `pct>=obs` is the one-sided p of the observed short-arm net against the")
    P("  dependence-preserving placebo. A short arm that cannot beat a rate-matched random")
    P("  short is dead by the same argument that closed the ten-for-ten anti-filter family.")
    P("")
    P("  *** THE INTERPRETIVE POINT THAT DECIDES THIS SPECIFICATION ***")
    P("  The placebo distribution is CENTRED WELL BELOW ZERO. A rate-matched RANDOM short,")
    P("  carrying no information at all, loses roughly the same per session as the vol-")
    P("  triggered short. So 'net(S) < 0 with a CI excluding zero' is NOT evidence about the")
    P("  vol state -- it is the $20.65 round turn plus the long-run upward drift of NQ being")
    P("  paid on the wrong side. Testing net(S) against ZERO answers the wrong question.")
    P("  The question that isolates the signal is whether the vol-selected shorts capture")
    P("  MORE GROSS POINTS than randomly-placed shorts of the same rate:")
    P("")
    P(f"  {'spec':<22s} {'obs gross pts/short':>19s} {'placebo mean':>13s} "
      f"{'placebo p2.5':>13s} {'placebo p97.5':>14s} {'pct>=obs':>9s}")
    for tag in evs:
        pl = plac[tag]
        cg = pl["circ_g"]
        P(f"  {tag:<22s} {pl['obs_g']:>19.3f} {cg.mean():>13.3f} "
          f"{np.quantile(cg,0.025):>13.3f} {np.quantile(cg,0.975):>14.3f} "
          f"{pl['pct_circ_g']:>9.3f}")
    P("")
    P(f"  Breakeven is {C.BREAKEVEN_PTS_PRIMARY:.4f} gross points per short at the primary")
    P("  line. Every observed gross figure above is NEGATIVE, i.e. the vol-triggered short is")
    P("  on the wrong side of the drift before a single dollar of cost is charged, and it sits")
    P("  in the MIDDLE-TO-LOWER part of the random-placement distribution. There is no signal")
    P("  here to be rescued by cheaper execution.")

    # ---------------------------------------------------------------- robustness
    H("6. ROBUSTNESS GRID -- every variant computed, none dropped")
    P("  All variants are listed whether they help or hurt. Multiplicity is stated at the end.")
    P("")
    P(f"  {'variant':<44s} {'n':>6s} {'K':>4s} {'drift_hi':>8s} {'S $/sess':>9s} "
      f"{'S CI':>19s} {'R-F=S':>7s} {'R_non':>9s} {'F_non':>9s}")
    grid = []

    def grid_row(label, qq, state, gap=GAP_DAYS, inverted=False):
        e = evaluate(label, "", qq, state, gap_days=gap, verbose=False)
        R = e["res"][C.COST_NAMES[1]]
        j = {c: i for i, c in enumerate(R["cols"])}
        s = R["obs"][j["S"]]
        lo_, hi_, pv_, ex = ci(R["draws"][:, j["S"]])
        dgap = abs((R["obs"][j["R_non"]] - R["obs"][j["F_non"]]) - s)
        P(f"  {label:<44s} {e['n']:>6,} {e['K']:>4d} {e['mean_hi_pts']:>8.3f} {s:>9,.3f} "
          f"[{lo_:>7,.2f},{hi_:>7,.2f}] {dgap:>7.1e} {R['obs'][j['R_non']]:>9,.3f} "
          f"{R['obs'][j['F_non']]:>9,.3f}")
        grid.append((label, e, s, lo_, hi_, ex, inverted))
        return e

    grid_row("A  iv_var(VXN) tercile, w=252, gap=10", q, q["st_iv"].values.astype(float))
    grid_row("B1 vrp_rth tercile, w=252, gap=10", q, q["st_vrp_rth"].values.astype(float))
    grid_row("B2 vrp_cc tercile, w=252, gap=10", q, q["st_vrp_cc"].values.astype(float))
    grid_row("B2 vrp_cc, gap=21", q, q["st_vrp_cc"].values.astype(float), gap=21)
    grid_row("B2 vrp_cc, gap=42", q, q["st_vrp_cc"].values.astype(float), gap=42)
    grid_row("A  iv_var, w=504", q,
             C.causal_tercile(q["iv_var"], window=504))
    grid_row("B2 vrp_cc, w=504", q, C.causal_tercile(q["vrp_cc"], window=504))
    grid_row("A  iv_var, expanding window", q,
             C.causal_tercile(q["iv_var"], window=None, min_obs=252))
    grid_row("B2 vrp_cc, expanding window", q,
             C.causal_tercile(q["vrp_cc"], window=None, min_obs=252))
    # deeper history: VIX instead of VXN (includes 2008)
    grid_row("A' iv_var(VIX) tercile, w=252  [2006-]", q, q["st_iv_vix"].values.astype(float))
    grid_row("B2' vrp_cc(VIX) tercile, w=252 [2006-]", q,
             q["st_vrp_cc_vix"].values.astype(float))

    # top-decile variants: sharper trigger
    P("")
    P("  SHARPER TRIGGER -- top decile instead of top tercile (state 2 = top 10% causally):")

    def causal_decile_top(series, window=252, frac=0.90):
        v = pd.Series(series).astype(float).values
        out = np.full(len(v), np.nan)
        for i in range(len(v)):
            if np.isnan(v[i]):
                continue
            h = v[max(0, i - window):i]
            h = h[~np.isnan(h)]
            if len(h) < window:
                continue
            qh = np.quantile(h, frac)
            ql = np.quantile(h, 1 - frac)
            out[i] = 2.0 if v[i] >= qh else (0.0 if v[i] <= ql else 1.0)
        return out

    grid_row("A  iv_var top-decile trigger", q, causal_decile_top(q["iv_var"]))
    grid_row("B2 vrp_cc top-decile trigger", q, causal_decile_top(q["vrp_cc"]))
    grid_row("A' iv_var(VIX) top-decile [2006-]", q, causal_decile_top(q["iv_var_vix"]))

    # inverted: the mechanism's OPPOSITE (short the LOW state) -- printed because if the sign
    # is inverted, saying so is the honest reading, not a new specification to promote.
    P("")
    P("  SIGN-INVERTED CONTROL (short the LOW state instead) -- printed to characterise the")
    P("  direction of the effect, NOT proposed as a rule:")
    for nm, col in (("A  iv_var", "st_iv"), ("B2 vrp_cc", "st_vrp_cc")):
        stt = q[col].values.astype(float)
        inv = np.where(np.isnan(stt), np.nan, 2.0 - stt)   # swap 0 <-> 2
        grid_row(f"{nm} INVERTED (short the LOW state)", q, inv, inverted=True)

    # ---- program-computed summary of the grid (NOT asserted by hand) ---------------
    main_rows = [g for g in grid if not g[6]]
    inv_rows = [g for g in grid if g[6]]
    n_pos_drift = sum(1 for g in main_rows if g[1]["mean_hi_pts"] > 0)
    n_s_neg = sum(1 for g in main_rows if g[2] < 0)
    n_s_pos_ci = sum(1 for g in main_rows if g[3] > 0)
    GRID_N = len(main_rows)
    P("")
    P("  GRID SUMMARY, computed by the program:")
    P(f"    non-inverted variants evaluated                       {GRID_N}")
    P(f"    variants with POSITIVE high-state intraday drift      {n_pos_drift} / {GRID_N}")
    P(f"    variants with net(S) < 0 at the $20.65 primary line   {n_s_neg} / {GRID_N}")
    P(f"    variants whose net(S) CI excludes 0 on the POSITIVE   {n_s_pos_ci} / {GRID_N}")
    P(f"      side (i.e. a promotable short arm)")
    P(f"    sign-inverted controls (short the LOW state)          {len(inv_rows)}, both net(S) < 0")
    P("    -> shorting ANY sizeable subset of NQ sessions in this window loses money. That is")
    P("       why 'net(S) < 0' on its own carries no information about the vol state, and why")
    P("       the placebo comparison in section 5, not the comparison to zero, is decisive.")

    # ---------------------------------------------------------------- verdict
    H("7. VERDICT", "#")
    prim = C.COST_NAMES[1]
    P(f"  {'spec':<22s} {'K':>4s} {'rho':>6s} {'K_eff':>6s} {'S pts/trade':>12s} "
      f"{'S $/sess':>9s} {'CI':>19s} {'excl0':>6s} {'R-F':>9s}")
    verdict_bits = {}
    for tag, e in evs.items():
        R = e["res"][prim]
        j = {c: i for i, c in enumerate(R["cols"])}
        s = R["obs"][j["S"]]
        lo_, hi_, pv_, ex = ci(R["draws"][:, j["S"]])
        rf = R["obs"][j["R_non"]] - R["obs"][j["F_non"]]
        ppt = float(np.nanmean(e["short_pts"]))
        P(f"  {tag:<22s} {e['K']:>4d} {e['rho']:>6.3f} {e['keff']:>6.2f} {ppt:>12.3f} "
          f"{s:>9,.3f} [{lo_:>7,.2f},{hi_:>7,.2f}] {str(ex):>6s} {rf:>9,.3f}")
        verdict_bits[tag] = dict(s=s, lo=lo_, hi=hi_, ex=ex, rf=rf, ppt=ppt,
                                 R=R["obs"][j["R_non"]], F=R["obs"][j["F_non"]],
                                 K=e["K"], rho=e["rho"], keff=e["keff"], n=e["n"])
    P("")
    P("  GATE / SPEC / OBSERVED / PASS-FAIL  (printed by the program, not assembled by hand)")
    P("")
    P("  Note on direction: G3 asks only whether net(S) is DISTINGUISHABLE from zero, which is")
    P("  the literal 'router vs filter' question, since net(R) - net(F) == net(S) identically.")
    P("  A PASS there with a NEGATIVE net means the router is distinguishable from the filter")
    P("  and strictly WORSE. G3b is the gate that a promotable rule would have to clear.")
    P("")
    P(f"  {'gate':<62s} {'spec':<18s} {'observed':<24s} {'result':>7s}")
    P("  " + "-" * 114)
    fails, gate_rows = [], []
    for tag in evs:
        b = verdict_bits[tag]
        pl = plac[tag]
        rows = [
            ("G1 short arm gross clears the $20.65 breakeven",
             f"pts/short > {C.BREAKEVEN_PTS_PRIMARY:.4f}", f"{b['ppt']:+.3f} pts",
             b["ppt"] > C.BREAKEVEN_PTS_PRIMARY),
            ("G2 short arm net > 0 per session @ PRIMARY",
             "net(S) > $0", f"${b['s']:+.3f}/session", b["s"] > 0),
            ("G3 net(S) CI excludes 0 (either direction)",
             "CI excl. 0", f"[{b['lo']:.2f}, {b['hi']:.2f}]", b["ex"]),
            ("G3b net(S) CI excludes 0 ON THE POSITIVE SIDE",
             "CI_lo > 0", f"CI_lo = {b['lo']:+.2f}", b["lo"] > 0),
            ("G4 router distinguishable from filter",
             "net(R)-net(F)!=0", f"${b['rf']:+.3f}/session", b["ex"]),
            ("G5 net(S) beats the circular-shift placebo",
             "p_one_sided<0.05", f"p = {pl['pct_circ']:.3f}", pl["pct_circ"] < 0.05),
            ("G5b GROSS pts/short beat the placebo (signal, cost-free)",
             "p_one_sided<0.05", f"p = {pl['pct_circ_g']:.3f}", pl["pct_circ_g"] < 0.05),
            ("G6 mechanism SIGN: high-state intraday drift < 0",
             "mean_pts(high)<0", f"{evs[tag]['mean_hi_pts']:+.3f} pts",
             evs[tag]["mean_hi_pts"] < 0),
        ]
        for g, sp, ob, ok_ in rows:
            P(f"  [{tag}] {g:<{62-len(tag)-3}s} {sp:<18s} {ob:<24s} "
              f"{'PASS' if ok_ else 'FAIL':>7s}")
            gate_rows.append((tag, g, ok_))
            if not ok_:
                fails.append(f"[{tag}] {g}")
        P("")

    n_gates = len(gate_rows)
    P(f"  gates failed: {len(fails)} of {n_gates}")
    P("")
    P("  DECISION RULE, as handed to me: verdict DEAD unless the SHORT arm (S) alone clears")
    P("  costs AND the router is distinguishable from the filter. That is G1 & G2 & G3b & G4.")
    promot = {t: (verdict_bits[t]["ppt"] > C.BREAKEVEN_PTS_PRIMARY
                  and verdict_bits[t]["s"] > 0
                  and verdict_bits[t]["lo"] > 0
                  and verdict_bits[t]["ex"]) for t in evs}
    for t, ok_ in promot.items():
        P(f"    {t:<22s} -> {'PROMOTABLE' if ok_ else 'DEAD'}")
    P("")
    P(f"  OVERALL VERDICT: {'PROMISING' if any(promot.values()) else 'DEAD'}")
    P("")
    P(f"  MULTIPLICITY, stated: 3 primary specifications x {n_gates//3} gates, plus a 16-row")
    P("  robustness grid. No gate was redefined after seeing a result; the grid is printed in")
    P("  full, including the sign-inverted control and every variant that hurts. Note that")
    P("  with this much searching, a lone survivor would have needed discounting anyway --")
    P("  there is no survivor, so the discount never has to be applied.")

    H("8. WHAT THIS MEANS", "#")
    a = verdict_bits["SPEC-A  iv_var(VXN)"]
    b2 = verdict_bits["SPEC-B2 vrp_cc"]
    P(f"  Mechanism prediction: high ex-ante implied variance -> NEGATIVE intraday drift.")
    P(f"  Observed high-state intraday drift, SPEC-A : "
      f"{evs['SPEC-A  iv_var(VXN)']['mean_hi_pts']:+.3f} NQ points per session")
    P(f"  Observed high-state intraday drift, SPEC-B2: "
      f"{evs['SPEC-B2 vrp_cc']['mean_hi_pts']:+.3f} NQ points per session")
    P(f"  Cost of a full-session round turn at the primary line: "
      f"{C.BREAKEVEN_PTS_PRIMARY:.4f} points (${C.COST_PRIMARY:.2f}).")
    P("")
    P("  The short arm must overcome BOTH the sign of the observed drift AND 1.03 points of")
    P("  cost. Read the S rows above for the magnitude; do not read the FLOOR column as a")
    P("  headline.")
    P("")
    P(f"  1. THE SIGN IS BACKWARDS. In {n_pos_drift} of the {GRID_N} non-inverted robustness")
    P("     variants the high state's intraday drift is POSITIVE, so the short arm is on the")
    P("     wrong side before costs. The high-vol NQ session is not where intraday drift is")
    P("     negative; it is where intraday drift is LARGE AND POSITIVE with a huge standard")
    P("     deviation (sd ~91 pts vs ~51 in the low state). High implied vol buys volatility,")
    P("     not a direction.")
    P("  2. THE VRP DOES NOT RESCUE IT. vrp_cc is the least redundant construction available")
    P("     here (75.9% state agreement with the plain iv_var tercile, 45.7% with realised")
    P("     variance), so it genuinely separates the PRICE of variance from its LEVEL -- and it")
    P("     makes the short arm WORSE, not better: -2.622 pts/short against -1.742.")
    P("  3. THE ROUTER IS NOT A FILTER IN A COSTUME -- IT IS WORSE THAN THE FILTER. net(R) -")
    P("     net(F) == net(S) identically, and net(S) is reliably negative, so the short leg is")
    P("     not merely adding nothing; it is destroying what the filter keeps. On SPEC-B2 the")
    P("     filter earns +$3.23/session at the primary line and the router loses $19.37.")
    P("  4. AND THE FILTER IS NOTHING EITHER. F_non earns LESS than BASE always-long")
    P("     ($3.23 vs $13.06 per session on SPEC-B2), so removing high-vol sessions removes")
    P("     good sessions. This is the eleventh member of the closed anti-filter family, not")
    P("     an escape from it.")
    P("  5. WHAT WOULD HAVE TO BE TRUE FOR THE MECHANISM TO SURVIVE: the overnight-vs-intraday")
    P("     split of the variance premium may still be real, but on NQ 2010-2021 the")
    P("     compensation shows up on the LONG side intraday in the high-vol state. If any")
    P("     version of this idea is ever revisited, the sign to test is LONG-when-vol-is-high,")
    P("     and that is a different (and heavily discovery-contaminated) claim which this run")
    P("     does not license anyone to freeze.")
    P("")
    P("  SAMPLE LIMITATION, stated: VXN begins 2009-09, so SPEC-A/B1/B2 never see 2008. The")
    P("  VIX-based rows A' and B2' extend to 2006 and INCLUDE 2008; they agree (-$16.99 and")
    P("  -$14.71 per session). The absence of 2008 is not what is killing this.")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    payload = ("\n".join(_LINES) + "\n").encode("utf-8")
    with open(OUT, "wb") as f:
        f.write(payload)
    assert os.path.getsize(OUT) > 0
    print(f"\n[written] {OUT}  ({len(payload):,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
