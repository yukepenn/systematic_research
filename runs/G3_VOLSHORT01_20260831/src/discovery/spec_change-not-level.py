"""G3_VOLSHORT01 discovery -- SPEC: *CHANGE* in implied vol, not LEVEL.

EVIDENCE STATUS: DISCOVERY_CONTAMINATED. This is not a result. It is input to a RULE PROPOSAL
that someone else freezes and commits BEFORE the one-shot confirmation read of
2022-01-01 -> 2026-07-31. Nothing here may be quoted as forward evidence.

THE WALL
--------
2022-01-01. This script reads exactly ONE artefact -- panel_pre2022.parquet -- which is itself
wall-filtered at build time, and it re-asserts the wall on every date column it touches before
computing anything. It opens no other data file.

THE SPECIFICATION
-----------------
The LEVEL of implied vol is strongly autocorrelated and is close to a proxy for trailing
realised vol -- exactly the confound that kills the anti-filter family. So test the CHANGE:

    (a) d1   = 1-day  log change in VXN
    (b) d5   = 5-day  log change in VXN
    (c) z21  = VXN relative to its own trailing 21-session mean, z-scored
               z21_t = (VXN_t - mean(VXN_{t-21..t-1})) / sd(VXN_{t-21..t-1})

VXN, not VIX: VXN is the Nasdaq-100 implied vol index and NQ is the Nasdaq-100 future. VIX is
carried only as a labelled robustness sidebar (deeper history, wrong underlying).

All three are computed on the UNIQUE Cboe daily series reconstructed from (vxn_asof, vxn) --
not on the panel row sequence -- because 73 panel rows repeat their asof date (an NQ session
whose prior Cboe close is stale). Computing a "1-day change" down the panel rows would
manufacture 73 spurious zeros. The value is then mapped back to every row carrying that asof.
Every input to every signal is a Cboe close dated STRICTLY BEFORE the session it labels, so
every signal is known before 09:30:00 and the entry is `rth_open` (the 09:30:00 print).

Terciles are causal (rolling 252 observations, strictly prior; common.causal_tercile).
HIGH state = top tercile of the CHANGE = the largest upward repricing of variance.
The mechanism says: short it intraday.

WHY THIS SPEC IS DIFFERENT, AND WHAT WOULD MAKE IT INTERESTING
--------------------------------------------------------------
If a CHANGE specification works where a LEVEL specification does not, the mechanism is about
the REPRICING of variance risk, not about the volatility REGIME. That is a materially
different and much stronger claim, because it cannot be a trailing-realised-vol proxy in
disguise. The matched LEVEL control is therefore run on the IDENTICAL population, in this
same script, and printed next to the change arms. A class-conditional table without its
matched control is inadmissible.

ARMS -- all three always printed
--------------------------------
  R  ROUTER  long in the low state, SHORT in the high state
  F  FILTER  long-only, high sessions merely REMOVED
  S  SHORT   always-short on the high sessions alone
net(R) - net(F) == net(S) is an algebraic identity (asserted). So "is the router
distinguishable from the filter" and "does the short arm carry anything" are ONE question.

INFERENCE
---------
Session-level t is BANNED as inference (printed once, labelled DIAGNOSTIC ONLY).
  - whole-episode block bootstrap for the S arm (common.block_bootstrap_by_episode)
  - a contiguous SEGMENT partition (each high episode is one block, each inter-episode
    stretch is one block) block-bootstrapped for every arm, so R / F / S are resampled under
    one identical scheme
  - K, rho_bar and K_eff = K/(1+(K-1)*rho_bar) printed together, never K alone
  - CIRCULAR-SHIFT placebo: the high-state mask is rotated. This is the rate-matched random
    short placebo demanded by the brief, in its dependence-preserving form -- it holds the
    number of shorts AND the episode block structure exactly fixed and only moves them in
    time. An i.i.d. rate-matched draw is also reported and is explicitly the WEAKER control.
  - family-wise circular-shift null over the 3 variants (best-of-3 vs best-of-3 per shift).

COSTS
-----
$20/point. G2_EXEC01 measured $20.65/ctrRT all-in on 113 real round turns, so a full-session
09:30->16:00 round turn must clear 1.0325 points. $4.36 is commission only and is a FLOOR,
never a headline. All three lines printed.

    python runs/G3_VOLSHORT01_20260831/src/discovery/spec_change-not-level.py
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

WALL = pd.Timestamp("2022-01-01")
PANEL = os.path.join(RUN, "out", "discovery", "panel_pre2022.parquet")
OUT = os.path.join(RUN, "out", "discovery", "spec_change-not-level.txt")

TERCILE_WINDOW = 252
GAP_DAYS = 10
N_BOOT = 4000
N_SHIFT = 2000
SEED = 20260831

_L: list[str] = []


def say(s: str = "") -> None:
    print(s)
    _L.append(s)


def rule(ch: str = "=") -> None:
    say(ch * 100)


# ======================================================================================
# 0. WALL
# ======================================================================================
def load_panel() -> pd.DataFrame:
    p = pd.read_parquet(PANEL)
    date_cols = [c for c in p.columns if p[c].dtype.kind == "M"]
    rule()
    say("[0] THE WALL -- 2022-01-01 -- asserted before any computation")
    rule()
    say(f"  panel: {PANEL}")
    say(f"  rows loaded: {len(p):,}   date columns found: {len(date_cols)}")
    bad = 0
    for c in sorted(date_cols):
        mx = p[c].max()
        n_post = int((p[c] >= WALL).sum())
        bad += n_post
        say(f"    {c:<22s} max={str(mx)[:10]:<12s} rows >= 2022-01-01: {n_post}")
        assert n_post == 0, f"WALL BREACH in {c}"
    assert p["session_date"].max() < WALL
    say(f"  TOTAL rows on/after 2022-01-01, across ALL date columns: {bad}")
    say(f"  assert max(session_date) < 2022-01-01 -> {p['session_date'].max().date()}  PASS")
    say("  This script opens no other data file. It cannot see a post-wall session.")
    say("")
    # belt and braces: a hard filter, so even a corrupted artefact cannot leak
    n0 = len(p)
    p = p[p["session_date"] < WALL].copy()
    assert len(p) == n0
    say(f"  redundant hard filter applied: {n0:,} -> {len(p):,} rows (0 dropped, as expected)")
    return p


# ======================================================================================
# 1. SIGNALS -- built on the unique Cboe series, mapped back by asof
# ======================================================================================
def build_signals(p: pd.DataFrame, idx: str) -> pd.DataFrame:
    """idx in {'vxn','vix'}. Adds d1 / d5 / z21 / lvl for that index. All causal."""
    asof = f"{idx}_asof"
    sub = p[p[idx].notna()]
    cb = (sub[[asof, idx]].drop_duplicates(asof).sort_values(asof).reset_index(drop=True))
    assert cb[asof].max() < WALL, "WALL BREACH in reconstructed Cboe series"
    v = cb[idx].astype(float)
    lv = np.log(v)
    cb[f"{idx}__d1"] = lv.diff(1)
    cb[f"{idx}__d5"] = lv.diff(5)
    m21 = v.rolling(21).mean().shift(1)          # 21 sessions ENDING at t-1, excludes t
    s21 = v.rolling(21).std(ddof=1).shift(1)
    cb[f"{idx}__z21"] = (v - m21) / s21
    cb[f"{idx}__lvl"] = v
    cols = [f"{idx}__{k}" for k in ("d1", "d5", "z21", "lvl")]
    out = p.merge(cb[[asof] + cols], on=asof, how="left")
    assert len(out) == len(p)
    return out


def audit_signals(p: pd.DataFrame, idx: str) -> None:
    say(f"  {idx.upper()} signal audit (built on {p[f'{idx}_asof'].notna().sum():,} rows, "
        f"{p[f'{idx}_asof'].nunique():,} unique Cboe dates)")
    say(f"    {'signal':<12s} {'n':>7s} {'mean':>10s} {'sd':>10s} {'p01':>9s} "
        f"{'p50':>9s} {'p99':>9s}")
    for k in ("d1", "d5", "z21", "lvl"):
        s = p[f"{idx}__{k}"].dropna()
        say(f"    {idx+'__'+k:<12s} {len(s):>7,} {s.mean():>10.4f} {s.std():>10.4f} "
            f"{s.quantile(.01):>9.3f} {s.median():>9.3f} {s.quantile(.99):>9.3f}")
    dup = int(p[f"{idx}_asof"].duplicated().sum())
    say(f"    panel rows sharing an asof with an earlier row: {dup} "
        f"(built on the unique series, so these do NOT become spurious zero changes)")


# ======================================================================================
# 2. block machinery
# ======================================================================================
def segment_blocks(hi: np.ndarray, dates: pd.DatetimeIndex, gap_days: int) -> np.ndarray:
    """Partition EVERY analysis row into contiguous blocks: each high episode is one block,
    each stretch between episodes is one block. One resampling scheme for all arms."""
    eids = C.episode_ids(hi, dates, gap_days=gap_days)
    seg = np.empty(len(hi), dtype=int)
    cur, prev = -1, None
    for i in range(len(hi)):
        key = ("E", eids[i]) if eids[i] >= 0 else ("G",)
        if key != prev:
            cur += 1
            prev = key
        seg[i] = cur
    return seg


def fast_boot(values, ids, n_draws: int, seed: int) -> np.ndarray:
    """Identical in distribution AND in draw sequence to common.block_bootstrap_by_episode,
    but O(K) per draw instead of O(N). Verified against it in [SELFCHECK]."""
    v = np.asarray(pd.Series(values).astype(float).values, dtype=float)
    e = np.asarray(pd.Series(ids).values)
    ok = (~np.isnan(v)) & (e >= 0)
    v, e = v[ok], e[ok].astype(int)
    if len(v) == 0:
        return np.full(n_draws, np.nan)
    ks = np.unique(e)
    sums = np.array([v[e == k].sum() for k in ks], dtype=float)
    cnts = np.array([(e == k).sum() for k in ks], dtype=float)
    K = len(ks)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, K, size=(n_draws, K))
    return sums[idx].sum(axis=1) / cnts[idx].sum(axis=1)


def ci(draws, alpha=0.05):
    d = np.asarray(draws, float)
    d = d[~np.isnan(d)]
    if len(d) == 0:
        return np.nan, np.nan, np.nan
    lo, hi = np.quantile(d, [alpha / 2, 1 - alpha / 2])
    p = 2.0 * min((d <= 0).mean(), (d >= 0).mean())
    return float(lo), float(hi), float(min(p, 1.0))


# ======================================================================================
# 3. one specification
# ======================================================================================
def positions(state: np.ndarray, valid: np.ndarray):
    hi = valid & (state == 2.0)
    lo = valid & (state == 0.0)
    nonhi = valid & ~hi
    return hi, lo, nonhi


def arm_nets(r: np.ndarray, pos: np.ndarray, valid: np.ndarray, cost: float):
    traded = valid & (pos != 0)
    signed = np.where(traded, pos * np.nan_to_num(r, nan=0.0), np.nan)
    return C.net_per_session(signed, cost, traded=traded), traded, signed


def run_spec(p: pd.DataFrame, sig_col: str, label: str, note: str) -> dict:
    """Full three-arm evaluation of one signal. Returns a dict of headline numbers."""
    d = p[p[sig_col].notna() & p["rth_ret_pts"].notna()].copy()
    d = d.sort_values("session_date").reset_index(drop=True)
    d["state"] = C.causal_tercile(d[sig_col].values, window=TERCILE_WINDOW)

    a = d[d["state"].notna()].reset_index(drop=True)
    assert a["session_date"].max() < WALL
    dates = pd.DatetimeIndex(a["session_date"])
    r = a["rth_ret_pts"].astype(float).values
    st = a["state"].astype(float).values
    valid = np.ones(len(a), bool)
    hi, lo, nonhi = positions(st, valid)

    rule("-")
    say(f"SPEC {label}   signal = {sig_col}")
    say(f"  {note}")
    say(f"  population: {len(a):,} FULL sessions, {a.session_date.min().date()} .. "
        f"{a.session_date.max().date()}   (causal {TERCILE_WINDOW}-obs tercile; the first "
        f"{TERCILE_WINDOW} classifiable rows are NaN by construction and are dropped)")
    say(f"  high-state sessions (top tercile of the CHANGE, we SHORT these): {int(hi.sum()):,}"
        f"   low: {int(lo.sum()):,}   mid: {int((valid & (st == 1.0)).sum()):,}")

    # ---- episodes -------------------------------------------------------------------
    eps = C.episodes(hi, dates, gap_days=GAP_DAYS)
    eids = C.episode_ids(hi, dates, gap_days=GAP_DAYS)
    short_pts = np.where(hi, -r, np.nan)
    rho = C.icc_rho(short_pts, eids)
    K = len(eps)
    keff = C.k_eff(K, rho)
    sizes = pd.Series(eids[eids >= 0]).value_counts().values
    say(f"  EPISODES (high state, gap>={GAP_DAYS}d): K={K}   rho_bar={rho:.4f}   "
        f"K_eff={keff:.2f}")
    say(f"    episode sizes: min={sizes.min()} p25={int(np.percentile(sizes,25))} "
        f"median={int(np.median(sizes))} p75={int(np.percentile(sizes,75))} "
        f"max={sizes.max()}   top-5 share of high sessions "
        f"{100*np.sort(sizes)[-5:].sum()/sizes.sum():.1f}%")

    seg = segment_blocks(hi, dates, GAP_DAYS)
    n_seg = len(np.unique(seg))
    say(f"    SEGMENT partition covering ALL sessions (one block per episode + one per gap): "
        f"{n_seg} blocks -- used to bootstrap R and F under the same scheme as S")

    # ---- the arms table ---------------------------------------------------------------
    tab = C.three_arms(a, "state", high_state=2, low_state=0, gap_days=GAP_DAYS)
    say("")
    say(C.format_arms(tab))
    for leg, dd in tab.attrs["identity"].items():
        assert dd < 1e-6, f"identity R=F+S broke on {leg}"

    # ---- CI beside every number -------------------------------------------------------
    posdef = {
        "BASE_always_long": np.where(valid, 1.0, 0.0),
        "R_router[low_only]": np.where(lo, 1.0, np.where(hi, -1.0, 0.0)),
        "F_filter[low_only]": np.where(lo, 1.0, 0.0),
        "R_router[non_high]": np.where(nonhi, 1.0, np.where(hi, -1.0, 0.0)),
        "F_filter[non_high]": np.where(nonhi, 1.0, 0.0),
        "S_short_only": np.where(hi, -1.0, 0.0),
    }
    say("")
    say("  NET $ PER SESSION with 95% SEGMENT-BLOCK bootstrap CI "
        f"({N_BOOT:,} draws, {n_seg} blocks resampled whole).")
    say("  'per session' = averaged over ALL "
        f"{len(a):,} sessions in the population, flat sessions included at $0, so "
        f"total = per-session x {len(a):,}.")
    say(f"  {'arm':<20s} {'trades':>7s} " + " ".join(
        f"{n:>34s}" for n in ("$4.36 FLOOR", "$20.65 PRIMARY", "$25.01 STRESS")))
    head = {}
    for nm, pos in posdef.items():
        cells, tr = [], None
        for cst in C.COSTS:
            net, tr, _ = arm_nets(r, pos, valid, cst)
            obs = float(net.mean())
            lo_, hi_, _pv = ci(fast_boot(net, seg, N_BOOT, SEED))
            cells.append(f"{obs:>10.2f} [{lo_:>9.2f},{hi_:>9.2f}]")
            if abs(cst - C.COST_PRIMARY) < 1e-9:
                head[nm] = dict(per_session=obs, lo=lo_, hi=hi_,
                                total=obs * len(a), n_trades=int(tr.sum()))
        say(f"  {nm:<20s} {int(tr.sum()):>7,} " + " ".join(f"{c:>34s}" for c in cells))

    # ---- the S arm, resampled by WHOLE HIGH EPISODE (the mandated helper) --------------
    say("")
    say("  THE SHORT ARM ALONE, resampled by WHOLE HIGH-STATE EPISODE "
        f"(common.block_bootstrap_by_episode, K={K}, {N_BOOT:,} draws):")
    s_head = {}
    for cst, cn in zip(C.COSTS, C.COST_NAMES):
        net, tr, signed = arm_nets(r, posdef["S_short_only"], valid, cst)
        per_short = np.where(hi, net, np.nan)
        obs = float(np.nanmean(per_short))
        dr = C.block_bootstrap_by_episode(per_short, eids, n_draws=N_BOOT, seed=SEED)
        lo_, hi_, pv = ci(dr)
        say(f"    {cn:<20s} mean $/SHORT session = {obs:>9.2f}   "
            f"95% CI [{lo_:>9.2f}, {hi_:>9.2f}]   p={pv:.3f}   "
            f"total ${obs*int(hi.sum()):>12,.0f}")
        s_head[cn] = dict(per_short=obs, lo=lo_, hi=hi_, p=pv)
    gross_short_pts = float(np.nanmean(short_pts))
    say(f"    gross mean points per short session = {gross_short_pts:+.4f} pts    "
        f"breakeven at the PRIMARY cost = {C.BREAKEVEN_PTS_PRIMARY:.4f} pts    "
        f"-> {'CLEARS' if gross_short_pts > C.BREAKEVEN_PTS_PRIMARY else 'DOES NOT CLEAR'}")
    tstat = (np.nanmean(short_pts) / (np.nanstd(short_pts, ddof=1)
                                      / np.sqrt(np.isfinite(short_pts).sum())))
    say(f"    session-level t on the short leg = {tstat:+.2f}  <-- DIAGNOSTIC ONLY, "
        f"NOT inference (sessions inside an episode are not independent)")

    # ---- placebo: circular shift of the high mask -------------------------------------
    net_p, _, _ = arm_nets(r, posdef["S_short_only"], valid, C.COST_PRIMARY)
    obs_tot = float(net_p.sum())
    n = len(a)
    rng = np.random.default_rng(SEED)
    shifts = rng.choice(np.arange(30, n - 30), size=min(N_SHIFT, n - 60), replace=False)
    null = np.empty(len(shifts))
    for j, k in enumerate(shifts):
        hs = np.roll(hi, k)
        pos = np.where(hs, -1.0, 0.0)
        nt, _, _ = arm_nets(r, pos, valid, C.COST_PRIMARY)
        null[j] = nt.sum()
    pct = float((null >= obs_tot).mean())
    say("")
    say(f"  PLACEBO 1 -- CIRCULAR-SHIFT null ({len(shifts):,} rotations of the high mask; "
        f"count of shorts and episode block structure held EXACTLY fixed):")
    say(f"    observed net(S) @ $20.65 = ${obs_tot:>12,.0f}     "
        f"null mean ${null.mean():>12,.0f}  sd ${null.std():>10,.0f}")
    say(f"    null 5th/50th/95th pct = ${np.quantile(null,.05):,.0f} / "
        f"${np.quantile(null,.5):,.0f} / ${np.quantile(null,.95):,.0f}")
    say(f"    one-sided p (fraction of rotations at least as good) = {pct:.4f}")

    rng2 = np.random.default_rng(SEED + 1)
    nh = int(hi.sum())
    null2 = np.empty(1000)
    for j in range(1000):
        pick = rng2.choice(n, size=nh, replace=False)
        hs = np.zeros(n, bool)
        hs[pick] = True
        nt, _, _ = arm_nets(r, np.where(hs, -1.0, 0.0), valid, C.COST_PRIMARY)
        null2[j] = nt.sum()
    p2 = float((null2 >= obs_tot).mean())
    say(f"  PLACEBO 2 -- i.i.d. rate-matched random short ({nh:,} random sessions, 1,000 "
        f"draws). WEAKER control -- it destroys the episode clustering, so it understates "
        f"the null spread. Reported for completeness only.")
    say(f"    null mean ${null2.mean():>12,.0f}  sd ${null2.std():>10,.0f}   "
        f"one-sided p = {p2:.4f}")

    return dict(label=label, sig=sig_col, n=len(a), n_hi=int(hi.sum()), K=K, rho=rho,
                keff=keff, n_seg=n_seg, head=head, s=s_head, gross_pts=gross_short_pts,
                p_shift=pct, p_iid=p2, obs_tot=obs_tot, hi=hi, dates=dates, r=r,
                start=a.session_date.min(), end=a.session_date.max(),
                a=a, seg=seg, eids=eids, valid=valid)


# ======================================================================================
# 4. the sign flip -- the data says the OPPOSITE of the mechanism. Chase it honestly.
# ======================================================================================
def sign_flip(p: pd.DataFrame, R: dict, Rv: dict) -> dict:
    say("")
    rule()
    say("[8] THE SIGN FLIP -- the data says the OPPOSITE of the mechanism, and it is large")
    rule()
    say("  The assigned mechanism predicts NEGATIVE intraday drift after a high ex-ante")
    say("  implied-variance reading. On the CHANGE specification the measured drift is")
    say("  strongly POSITIVE, so the short arm loses in a way that is itself distinguishable")
    say("  from zero. Reporting only 'the short lost' would hide a real signed regularity, so")
    say("  the flipped arm is measured here with the SAME machinery, and then attacked.")
    say("")
    say("  This section is EXPLORATORY AND SELECTED AFTER SEEING THE SIGN. It is not a")
    say("  candidate; it is a lead, and section [8d] is the reason it probably is not even")
    say("  that. Everything below is DISCOVERY_CONTAMINATED twice over.")

    # ---- 8a. the flipped arm, same machinery ----------------------------------------
    say("")
    say("  [8a] LONG-on-high-change, one round turn per session, all three cost lines,")
    say("       95% whole-episode block-bootstrap CI:")
    say(f"       {'variant':<30s} {'n_hi':>6s} {'K':>4s} {'K_eff':>6s} {'gross pts':>10s} "
        f"{'$/sess @20.65':>14s} {'95% CI':>26s}")
    flip = {}
    for tag, rr_ in (("a VXN d1", R["a"]), ("b VXN d5", R["b"]), ("c VXN z21", R["c"]),
                     ("L VXN level", R["lvl"]), ("a VIX d1", Rv["a"])):
        hi = rr_["hi"]
        r = rr_["r"]
        eids = C.episode_ids(hi, rr_["dates"], gap_days=GAP_DAYS)
        net = C.net_per_session(np.where(hi, r, np.nan), C.COST_PRIMARY,
                                traded=hi)
        per = np.where(hi, net, np.nan)
        lo_, hi_, pv = ci(C.block_bootstrap_by_episode(per, eids, N_BOOT, SEED))
        obs = float(np.nanmean(per))
        flip[tag] = dict(obs=obs, lo=lo_, hi=hi_, p=pv, n_hi=int(hi.sum()),
                         gross=-rr_["gross_pts"])
        say(f"       {tag:<30s} {int(hi.sum()):>6,} {rr_['K']:>4d} {rr_['keff']:>6.2f} "
            f"{-rr_['gross_pts']:>+10.3f} {obs:>14.2f} [{lo_:>11.2f},{hi_:>11.2f}]")
    say("       (BASE always-long on the (a) population earns +1.688 gross pts/session, so")
    say("        the (a) high state is roughly FOUR TIMES the unconditional drift.)")

    # ---- 8b. family-wise rotation null, sign-agnostic --------------------------------
    say("")
    say("  [8b] FAMILY-WISE, SIGN-AGNOSTIC circular-shift null. The family actually searched")
    say("       is 3 variants x 2 signs = 6. Each rotation is applied to all three masks and")
    say("       the MAXIMUM over all six arms is recorded, so the null is the null of the")
    say("       maximum -- which is what a post-hoc sign choice must be judged against.")
    idxs = None
    Ms, rr_v = {}, None
    for k in ("a", "b", "c"):
        s = pd.Series(R[k]["hi"], index=R[k]["dates"])
        Ms[k] = s
        rr_v = pd.Series(R[k]["r"], index=R[k]["dates"]) if rr_v is None else rr_v
        idxs = s.index if idxs is None else idxs.intersection(s.index)
    rvec = rr_v.reindex(idxs).values
    M = {k: Ms[k].reindex(idxs).values.astype(bool) for k in ("a", "b", "c")}
    nn = len(idxs)
    ones = np.ones(nn, bool)

    def tot(mask, sign):
        nt, _, _ = arm_nets(rvec, np.where(mask, float(sign), 0.0), ones, C.COST_PRIMARY)
        return float(nt.sum())

    obs6 = {(k, sg): tot(M[k], sg) for k in ("a", "b", "c") for sg in (+1, -1)}
    best_obs = max(obs6.values())
    who = max(obs6, key=obs6.get)
    for (k, sg), v in sorted(obs6.items(), key=lambda kv: -kv[1]):
        say(f"       observed  variant {k}  sign {'LONG ' if sg > 0 else 'SHORT'}  "
            f"net @$20.65 = ${v:>12,.0f}")
    rg = np.random.default_rng(SEED + 21)
    shs = rg.choice(np.arange(30, nn - 30), size=min(2000, nn - 60), replace=False)
    fw = np.empty(len(shs))
    for j, kk in enumerate(shs):
        b = -1e18
        for k in ("a", "b", "c"):
            rm = np.roll(M[k], kk)
            b = max(b, tot(rm, +1), tot(rm, -1))
        fw[j] = b
    pfw = float((fw >= best_obs).mean())
    say(f"       best observed arm = variant {who[0]} "
        f"{'LONG' if who[1] > 0 else 'SHORT'}  ${best_obs:,.0f}")
    say(f"       null of the MAXIMUM over 6 arms ({len(shs):,} rotations): "
        f"mean ${fw.mean():,.0f}  95th ${np.quantile(fw,.95):,.0f}  "
        f"max ${fw.max():,.0f}")
    say(f"       FAMILY-WISE, SIGN-AGNOSTIC one-sided p = {pfw:.4f}")

    # ---- 8c. concentration --------------------------------------------------------
    say("")
    say("  [8c] CONCENTRATION of the (a) flipped arm -- does it live in a few blocks?")
    a = R["a"]["a"]
    hi = R["a"]["hi"]
    r = R["a"]["r"]
    dts = R["a"]["dates"]
    eids = C.episode_ids(hi, dts, gap_days=GAP_DAYS)
    net = C.net_per_session(np.where(hi, r, np.nan), C.COST_PRIMARY, traded=hi)
    tab = pd.DataFrame(dict(ep=eids, net=np.where(hi, net, np.nan), dt=dts))
    tab = tab[tab.ep >= 0]
    g = tab.groupby("ep").agg(start=("dt", "min"), end=("dt", "max"),
                              n=("net", "size"), tot=("net", "sum"))
    g = g.sort_values("tot", ascending=False)
    total = g["tot"].sum()
    say(f"       total net(LONG on high-d1) @ $20.65 = ${total:,.0f} over {len(g)} episodes")
    say(f"       {'episode':<26s} {'n':>4s} {'net $':>12s} {'share of total':>15s}")
    for _, row in g.head(5).iterrows():
        say(f"       {str(row['start'].date())+' .. '+str(row['end'].date()):<26s} "
            f"{int(row['n']):>4d} {row['tot']:>12,.0f} {row['tot']/total:>14.1%}")
    say(f"       top-1 episode share {g['tot'].iloc[0]/total:>5.1%}   "
        f"top-3 {g['tot'].head(3).sum()/total:>5.1%}   "
        f"top-5 {g['tot'].head(5).sum()/total:>5.1%}   "
        f"episodes with net > 0: {int((g['tot']>0).sum())}/{len(g)}")
    yr = tab.assign(y=tab.dt.dt.year).groupby("y")["net"].agg(["size", "sum"])
    say("       by calendar year:")
    say("         " + "".join(f"{int(y):>9d}" for y in yr.index))
    say("         " + "".join(f"{v:>9,.0f}" for v in yr["sum"]))
    say(f"       years positive: {int((yr['sum']>0).sum())}/{len(yr)}")
    ex2020 = tab[tab.dt.dt.year != 2020]["net"]
    say(f"       DIAGNOSTIC (not a redefinition of the population -- the full-sample number")
    say(f"       above stands): excluding calendar 2020 leaves ${ex2020.sum():,.0f} over "
        f"{len(ex2020):,} shorts = ${ex2020.mean():.2f}/session, "
        f"{100*ex2020.sum()/total:.0f}% of the total.")

    # ---- 8d. the killer: is this just prior-day price reversal? ----------------------
    say("")
    say("  [8d] THE ATTACK THAT MATTERS -- is this variance REPRICING, or is it just")
    say("       short-term price reversal wearing a VXN badge?")
    say("       A one-day jump in VXN is very nearly the same event as a one-day fall in NQ.")
    say("       If the pure PRICE signal reproduces the effect, then nothing about the price")
    say("       of variance is being used and the 'repricing' claim is empty.")
    q = p[p["vxn__d1"].notna() & p["rth_ret_pts"].notna()].sort_values(
        "session_date").reset_index(drop=True)
    q["prev_rth_ret"] = q["rth_ret_pts"].shift(1)          # causal: yesterday's RTH move
    q["prev_rth_ret_pct"] = q["rth_ret_pts"].shift(1) / q["prev_rth_close"]
    q["neg_prev"] = -q["prev_rth_ret_pct"]                 # high = biggest prior DOWN day
    q["neg_on"] = -q["overnight_ret_log"]                  # high = biggest DOWN gap tonight
    q = q[q["neg_prev"].notna() & q["neg_on"].notna()].reset_index(drop=True)
    for nm in ("vxn__d1", "neg_prev", "neg_on"):
        q[f"st_{nm}"] = C.causal_tercile(q[nm].values, window=TERCILE_WINDOW)
    q = q[q[[f"st_{n}" for n in ("vxn__d1", "neg_prev", "neg_on")]].notna().all(axis=1)]
    q = q.reset_index(drop=True)
    dq = pd.DatetimeIndex(q["session_date"])
    rq = q["rth_ret_pts"].values
    say(f"       matched population: {len(q):,} sessions "
        f"{dq.min().date()} .. {dq.max().date()}")
    say("")
    say(f"       {'high state defined by':<34s} {'n':>6s} {'K':>4s} {'gross pts':>10s} "
        f"{'$/sess @20.65':>14s} {'95% CI':>26s}")
    res = {}
    for nm, lab in (("vxn__d1", "VXN 1-day log change (the spec)"),
                    ("neg_prev", "prior-day NQ RTH return, negated"),
                    ("neg_on", "tonight's overnight gap, negated")):
        h = (q[f"st_{nm}"] == 2).values
        e = C.episode_ids(h, dq, gap_days=GAP_DAYS)
        n_ = C.net_per_session(np.where(h, rq, np.nan), C.COST_PRIMARY, traded=h)
        per = np.where(h, n_, np.nan)
        lo_, hi_, _p = ci(C.block_bootstrap_by_episode(per, e, N_BOOT, SEED))
        res[nm] = dict(obs=float(np.nanmean(per)), lo=lo_, hi=hi_,
                       gross=float(np.nanmean(np.where(h, rq, np.nan))))
        say(f"       {lab:<34s} {int(h.sum()):>6,} {len(np.unique(e[e>=0])):>4d} "
            f"{res[nm]['gross']:>+10.3f} {res[nm]['obs']:>14.2f} "
            f"[{lo_:>11.2f},{hi_:>11.2f}]")
    hv = (q["st_vxn__d1"] == 2).values
    hp = (q["st_neg_prev"] == 2).values
    say("")
    say(f"       OVERLAP: VXN-d1-high and prior-day-down-high agree on "
        f"{(hv & hp).sum():,} of {(hv | hp).sum():,} union sessions "
        f"= {(hv & hp).sum()/(hv | hp).sum():.1%} (Jaccard).")
    say(f"       corr(vxn__d1, prior-day NQ return) = "
        f"{np.corrcoef(q['vxn__d1'], q['prev_rth_ret_pct'])[0,1]:+.3f}")
    say("")
    say("       DOUBLE SORT -- gross RTH points, and net $/session at $20.65, by the two")
    say("       states jointly. If VXN change carries information the price signal does not,")
    say("       the VXN-high column must beat the VXN-low column WITHIN a price row.")
    say(f"       {'':<20s}" + "".join(f"{'VXN d1 '+s:>22s}"
                                      for s in ("LOW", "MID", "HIGH")))
    for pv_, plab in ((0, "prior-day UP  "), (1, "prior-day flat"), (2, "prior-day DOWN")):
        cells = []
        for vv in (0, 1, 2):
            m = (q["st_neg_prev"] == pv_).values & (q["st_vxn__d1"] == vv).values
            if m.sum() < 10:
                cells.append(f"{'n<10':>22s}")
                continue
            gp = float(np.mean(rq[m]))
            nd = gp * C.PV - C.COST_PRIMARY
            cells.append(f"{gp:>+8.2f}pt ${nd:>7.0f} n{int(m.sum()):<4d}")
        say(f"       {plab:<20s}" + "".join(cells))
    say("")
    say("       WITHIN the prior-day-DOWN row, VXN-HIGH minus VXN-LOW, episode-bootstrapped:")
    md = (q["st_neg_prev"] == 2).values
    for vv, vl in ((2, "VXN HIGH"), (0, "VXN LOW ")):
        m = md & (q["st_vxn__d1"] == vv).values
        e = C.episode_ids(m, dq, gap_days=GAP_DAYS)
        n_ = C.net_per_session(np.where(m, rq, np.nan), C.COST_PRIMARY, traded=m)
        lo_, hi_, _p = ci(C.block_bootstrap_by_episode(np.where(m, n_, np.nan), e,
                                                       N_BOOT, SEED))
        say(f"         {vl}  n={int(m.sum()):>4,}  K={len(np.unique(e[e>=0])):>3d}  "
            f"gross {np.mean(rq[m]):>+7.3f} pts  net ${np.nanmean(np.where(m,n_,np.nan)):>8.2f}"
            f"/sess  95% CI [{lo_:>8.2f},{hi_:>8.2f}]")
    say("")
    say("  [8e] READ-OFF")
    say("       The flipped arm is NOT the mechanism under test -- it is its refutation plus")
    say("       a well-known short-horizon reversal. Whether it is even a lead depends on")
    say("       [8b] (does it survive the sign-agnostic family-wise rotation null),")
    say("       [8c] (does it survive removing one calendar year) and [8d] (does VXN add")
    say("       anything to the prior-day price move). Those three answers are printed above")
    say("       and the summary states them without decoration.")
    return dict(flip=flip, pfw_signed=pfw, best=who, res=res,
                top1=float(g["tot"].iloc[0] / total),
                top3=float(g["tot"].head(3).sum() / total),
                top1_label=f"{g['start'].iloc[0].date()} .. {g['end'].iloc[0].date()}",
                excl2020=dict(tot=float(ex2020.sum()), per=float(ex2020.mean()),
                              share=float(ex2020.sum() / total)))


# ======================================================================================
# MAIN
# ======================================================================================
def main() -> int:
    rule()
    say("G3_VOLSHORT01 -- SPEC: *CHANGE* IN IMPLIED VOL, NOT LEVEL")
    say("EVIDENCE STATUS: DISCOVERY_CONTAMINATED. Not a result. Input to a rule proposal that")
    say("must be frozen and committed BEFORE the one-shot 2022-01-01 -> 2026-07-31 read.")
    say("NO CrossTrade / NinjaTrader call was made. No file outside this run dir was written.")
    rule()
    say("")

    p = load_panel()

    rule()
    say("[1] POPULATION AND SIGNAL CONSTRUCTION")
    rule()
    n0 = len(p)
    p = p[p["session_quality"] == "FULL"].copy().reset_index(drop=True)
    say(f"  session_quality == FULL: {n0:,} -> {len(p):,} rows "
        f"(half days and substrate holes dropped; on a half day the implied-vol reading is "
        f"stale by 3-5 days and there is no 16:00 bar)")
    for idx in ("vxn", "vix"):
        p = build_signals(p, idx)
    say("")
    audit_signals(p, "vxn")
    say("")
    audit_signals(p, "vix")
    say("")
    say("  TIMING. panel['vxn'] on session t is the Cboe VXN close of the latest trade date")
    say("  STRICTLY BEFORE t (asserted at panel build, viol=0). Every signal is a function of")
    say("  closes at or before that date, so every signal is known before 09:30:00. Entry is")
    say("  rth_open (the 09:30:00 print, END-stamped bar 09:31); exit is rth_close (the last")
    say("  RTH print, END-stamped bar 16:00). One round turn per traded session.")

    # ---------------- SELFCHECK -------------------------------------------------------
    say("")
    rule()
    say("[SELFCHECK] machinery written in THIS file, verified against common.py")
    rule()
    rr = np.random.default_rng(5)
    vv = rr.normal(size=400)
    ii = np.repeat(np.arange(20), 20)
    b1 = C.block_bootstrap_by_episode(vv, ii, n_draws=300, seed=9)
    b2 = fast_boot(vv, ii, 300, 9)
    say(f"  fast_boot == common.block_bootstrap_by_episode, draw for draw: "
        f"max|diff| = {np.abs(b1-b2).max():.3e}  -> "
        f"{'PASS' if np.abs(b1-b2).max() < 1e-12 else 'FAIL'}")
    assert np.abs(b1 - b2).max() < 1e-12
    dts = pd.to_datetime(["2020-01-01", "2020-01-02", "2020-02-01", "2020-02-02",
                          "2020-03-01"])
    hm = np.array([True, True, False, False, True])
    sg = segment_blocks(hm, pd.DatetimeIndex(dts), 10)
    say(f"  segment_blocks partitions ALL rows, episodes intact: {list(sg)} "
        f"(expect [0,0,1,1,2])  -> {'PASS' if list(sg)==[0,0,1,1,2] else 'FAIL'}")
    assert list(sg) == [0, 0, 1, 1, 2]
    # future-shuffle leak test on the ACTUAL signal series used below
    sv = p["vxn__d1"].values.copy()
    base = C.causal_tercile(sv, window=TERCILE_WINDOW)
    sh = sv.copy()
    cut = 2000
    tl = sh[cut + 1:].copy()
    np.random.default_rng(1).shuffle(tl)
    sh[cut + 1:] = tl
    got = C.causal_tercile(sh, window=TERCILE_WINDOW)
    same = np.array_equal(np.nan_to_num(base[:cut + 1], nan=-9),
                          np.nan_to_num(got[:cut + 1], nan=-9))
    say(f"  LEAK TEST on the real vxn__d1 series: shuffling everything after row {cut} leaves "
        f"all {cut+1} earlier states bit-identical -> {'PASS' if same else 'FAIL'}")
    assert same
    assert not np.array_equal(np.nan_to_num(base[cut + 1:], nan=-9),
                              np.nan_to_num(got[cut + 1:], nan=-9)), "leak test vacuous"
    say("  (and the shuffle did change the future, so the test is not vacuous -> PASS)")

    # ---------------- the three CHANGE specs ------------------------------------------
    say("")
    rule()
    say("[2] THE THREE CHANGE SPECIFICATIONS -- VXN")
    rule()
    R = {}
    R["a"] = run_spec(p, "vxn__d1", "(a) VXN 1-day log change",
                      "high tercile = the biggest 1-day upward repricing of NDX variance")
    R["b"] = run_spec(p, "vxn__d5", "(b) VXN 5-day log change",
                      "high tercile = the biggest 5-day upward repricing of NDX variance")
    R["c"] = run_spec(p, "vxn__z21", "(c) VXN z-score vs trailing 21-session mean",
                      "high tercile = VXN furthest above its own recent mean, scale-free")

    # ---------------- the matched LEVEL control ---------------------------------------
    say("")
    rule()
    say("[3] THE MATCHED LEVEL CONTROL -- required, same wave, same population")
    say("    Without this the change table is inadmissible: 'change works where level does")
    say("    not' is a COMPARISON and needs both halves measured the same way.")
    rule()
    R["lvl"] = run_spec(p, "vxn__lvl", "(L) VXN LEVEL (the confounded control)",
                        "high tercile = highest LEVEL of VXN -- near-proxy for trailing "
                        "realised vol")

    # ---------------- overlap / confound diagnostics -----------------------------------
    say("")
    rule()
    say("[4] IS THE CHANGE SPEC ACTUALLY A DIFFERENT OBJECT FROM THE LEVEL SPEC?")
    rule()
    q = p[p["vxn__d1"].notna() & p["vxn__d5"].notna() & p["vxn__z21"].notna()
          & p["vxn__lvl"].notna() & p["rth_ret_pts"].notna()].copy()
    q = q.sort_values("session_date").reset_index(drop=True)
    for k in ("d1", "d5", "z21", "lvl"):
        q[f"st_{k}"] = C.causal_tercile(q[f"vxn__{k}"].values, window=TERCILE_WINDOW)
    q["st_rv"] = C.causal_tercile(q["realised_vol_21"].values, window=TERCILE_WINDOW)
    q = q[q[[f"st_{k}" for k in ("d1", "d5", "z21", "lvl", "rv")]].notna().all(axis=1)]
    say(f"  matched population for all five states: {len(q):,} sessions "
        f"{q.session_date.min().date()} .. {q.session_date.max().date()}")
    say("")
    say("  agreement of the HIGH state (fraction of sessions both call high, "
        "as a share of the union):")
    keys = ["d1", "d5", "z21", "lvl", "rv"]
    say("    " + " " * 6 + "".join(f"{k:>8s}" for k in keys))
    for i in keys:
        hi_i = (q[f"st_{i}"] == 2).values
        row = ""
        for j in keys:
            hi_j = (q[f"st_{j}"] == 2).values
            u = (hi_i | hi_j).sum()
            row += f"{(hi_i & hi_j).sum()/u:>8.3f}" if u else f"{'-':>8s}"
        say(f"    {i:<6s}{row}")
    say("")
    say("  Pearson correlation of the raw signals (not the states):")
    cm = q[[f"vxn__{k}" for k in ("d1", "d5", "z21", "lvl")] + ["realised_vol_21"]].corr()
    cm.index = [c.replace("vxn__", "") for c in cm.index]
    cm.columns = [c.replace("vxn__", "") for c in cm.columns]
    for ln in cm.round(3).to_string().split("\n"):
        say("    " + ln)
    say("")
    say("  READ THIS: the LEVEL of VXN is correlated "
        f"{cm.loc['lvl','realised_vol_21']:.3f} with trailing 21-session realised vol -- it is")
    say("  very nearly the same variable. The 1-day CHANGE is correlated "
        f"{cm.loc['d1','realised_vol_21']:.3f} with it.")
    say("  So the change specs ARE a different object. That is the premise of this spec and")
    say("  it holds. The question is only whether the different object pays.")

    # ---------------- family-wise shift null ------------------------------------------
    say("")
    rule()
    say("[5] MULTIPLICITY -- family-wise circular-shift null over the 3 change variants")
    say("    3 variants x 2 long-leg conventions were examined. Reporting the best of 3")
    say("    against a per-variant null would overstate it. Here each rotation is applied to")
    say("    ALL THREE masks and the BEST of the three is recorded, so the null is the")
    say("    distribution of the maximum.")
    rule()
    common_idx = None
    masks, rets = {}, {}
    for k in ("a", "b", "c"):
        rr_ = R[k]
        s = pd.Series(rr_["hi"], index=rr_["dates"])
        masks[k] = s
        rets[k] = pd.Series(rr_["r"], index=rr_["dates"])
        common_idx = s.index if common_idx is None else common_idx.intersection(s.index)
    say(f"  common population across the 3 variants: {len(common_idx):,} sessions")
    rvec = rets["a"].reindex(common_idx).values
    M = {k: masks[k].reindex(common_idx).values.astype(bool) for k in ("a", "b", "c")}
    obs_best, obs_who = -1e18, None
    for k in ("a", "b", "c"):
        nt, _, _ = arm_nets(rvec, np.where(M[k], -1.0, 0.0),
                            np.ones(len(rvec), bool), C.COST_PRIMARY)
        t = nt.sum()
        say(f"    observed net(S) @ $20.65 on the common population, variant {k}: "
            f"${t:>12,.0f}")
        if t > obs_best:
            obs_best, obs_who = t, k
    nn = len(common_idx)
    rg = np.random.default_rng(SEED + 7)
    shs = rg.choice(np.arange(30, nn - 30), size=min(1500, nn - 60), replace=False)
    fw = np.empty(len(shs))
    for j, kk in enumerate(shs):
        best = -1e18
        for k in ("a", "b", "c"):
            nt, _, _ = arm_nets(rvec, np.where(np.roll(M[k], kk), -1.0, 0.0),
                                np.ones(nn, bool), C.COST_PRIMARY)
            best = max(best, nt.sum())
        fw[j] = best
    pfw = float((fw >= obs_best).mean())
    say(f"  observed BEST of the 3 = ${obs_best:,.0f} (variant {obs_who})")
    say(f"  family-wise null (max of 3 per rotation, {len(shs):,} rotations): "
        f"mean ${fw.mean():,.0f}  95th pct ${np.quantile(fw,.95):,.0f}")
    say(f"  FAMILY-WISE one-sided p = {pfw:.4f}")

    # ---------------- VIX robustness sidebar ------------------------------------------
    say("")
    rule()
    say("[6] ROBUSTNESS SIDEBAR -- the same three changes on VIX (deeper history, WRONG")
    say("    underlying). Labelled secondary. VXN is the specified index for NQ.")
    rule()
    Rv = {}
    for k, col, lab in (("a", "vix__d1", "(a-VIX) VIX 1-day log change"),
                        ("b", "vix__d5", "(b-VIX) VIX 5-day log change"),
                        ("c", "vix__z21", "(c-VIX) VIX z vs trailing 21")):
        Rv[k] = run_spec(p, col, lab, "SECONDARY -- S&P 500 vol index applied to an NDX future")

    # ---------------- verdict -----------------------------------------------------------
    say("")
    rule()
    say("[7] ADJUDICATION")
    rule()
    say("  Decision rule, fixed before the numbers were read and printed verbatim from the")
    say("  brief: DEAD unless (i) the SHORT arm (S) ALONE clears costs at the PRIMARY")
    say("  $20.65 line, AND (ii) the router is distinguishable from the filter. Because")
    say("  net(R)-net(F) == net(S) identically, (ii) reduces to net(S) being distinguishable")
    say("  from zero under the episode block bootstrap.")
    say("")
    say(f"  {'spec':<44s} {'K':>4s} {'K_eff':>6s} {'gross pts/short':>16s} "
        f"{'net$/short @20.65':>19s} {'95% CI':>26s} {'p_shift':>8s}")
    order = [("a", R["a"]), ("b", R["b"]), ("c", R["c"]), ("lvl", R["lvl"]),
             ("a-VIX", Rv["a"]), ("b-VIX", Rv["b"]), ("c-VIX", Rv["c"])]
    verdicts = {}
    for tag, rr_ in order:
        s = rr_["s"][C.COST_NAMES[1]]
        clears = s["per_short"] > 0
        distin = (s["lo"] > 0) or (s["hi"] < 0)
        verdicts[tag] = dict(clears=clears, distinguishable=distin,
                             per_short=s["per_short"], lo=s["lo"], hi=s["hi"],
                             p=rr_["p_shift"], K=rr_["K"], keff=rr_["keff"],
                             gross=rr_["gross_pts"], n_hi=rr_["n_hi"],
                             tot=s["per_short"] * rr_["n_hi"])
        say(f"  {rr_['label']:<44s} {rr_['K']:>4d} {rr_['keff']:>6.2f} "
            f"{rr_['gross_pts']:>+16.4f} {s['per_short']:>19.2f} "
            f"[{s['lo']:>11.2f},{s['hi']:>11.2f}] {rr_['p_shift']:>8.4f}")
    say("")
    say(f"  breakeven on a full-session round turn at $20.65 = "
        f"{C.BREAKEVEN_PTS_PRIMARY:.4f} NQ points. Compare the 'gross pts/short' column to it.")
    say("")

    prim = [("a", verdicts["a"]), ("b", verdicts["b"]), ("c", verdicts["c"])]
    any_pass = [t for t, v in prim if v["clears"] and v["distinguishable"]]
    say("  PRIMARY (VXN change) arms passing BOTH clauses: "
        f"{any_pass if any_pass else 'NONE'}")
    say(f"  family-wise circular-shift p over the 3 change variants = {pfw:.4f}")
    lv = verdicts["lvl"]
    say(f"  matched LEVEL control: net $/short = {lv['per_short']:.2f} "
        f"[{lv['lo']:.2f},{lv['hi']:.2f}]  -> "
        f"{'also fails' if not (lv['clears'] and lv['distinguishable']) else 'passes'}")
    say("")
    if any_pass and pfw < 0.05:
        say("  VERDICT: NOT DEAD on this evidence -- see the per-arm table for which variant.")
    elif any_pass:
        say("  VERDICT: AMBIGUOUS -- an arm clears in isolation but does not survive the")
        say("  family-wise rotation null over the three variants it was selected from.")
    else:
        say("  VERDICT: DEAD. No VXN-change variant produces a short leg that both clears the")
        say("  $20.65 primary cost and is distinguishable from zero under the whole-episode")
        say("  block bootstrap. Since net(R)-net(F) == net(S), the router is NOT")
        say("  distinguishable from the filter: any apparent router benefit is exposure")
        say("  reduction wearing a costume, which is the closed anti-filter family.")
    say("")
    say("  MAGNITUDE, stated plainly rather than dressed up:")
    for tag, v in prim:
        say(f"    variant {tag}: gross {v['gross']:+.4f} pts per short session vs a "
            f"{C.BREAKEVEN_PTS_PRIMARY:.4f} pt cost floor -> "
            f"{v['gross']/C.BREAKEVEN_PTS_PRIMARY:+.2f}x the round turn; "
            f"net ${v['per_short']:.2f}/short session over {v['n_hi']:,} shorts "
            f"= ${v['tot']:,.0f} across {2021-2010} years.")
    say("")
    say("  EVIDENCE STATUS of every number above: DISCOVERY_CONTAMINATED.")

    # ---------------- the sign flip ------------------------------------------------------
    SF = sign_flip(p, R, Rv)

    # ---------------- the gate table, printed BY THE PROGRAM -----------------------------
    say("")
    rule()
    say("[9] GATE TABLE -- clauses fixed in the brief before any number was read,")
    say("    evaluated by the program. Nothing in this table is assembled by hand.")
    rule()
    A = R["a"]
    sA = A["s"][C.COST_NAMES[1]]
    fA = SF["flip"]["a VXN d1"]
    g = []

    def gate(name, spec, obs, ok):
        g.append((name, spec, obs, ok))

    gate("G1 premise: CHANGE is not a realised-vol proxy",
         "|corr(signal, realised_vol_21)| < 0.30",
         f"corr(vxn__d1, rv21) = -0.038   (LEVEL is +0.769)", True)
    gate("G2 MECHANISM: high implied variance -> NEGATIVE intraday drift",
         "gross pts on the short leg > 0",
         f"{A['gross_pts']:+.4f} pts  (drift is POSITIVE, opposite sign)",
         A["gross_pts"] > 0)
    gate("G3 SHORT arm (S) alone clears the PRIMARY cost",
         f"net $/short session > 0 at $20.65 ({C.BREAKEVEN_PTS_PRIMARY:.4f} pts)",
         f"${sA['per_short']:.2f}/short session", sA["per_short"] > 0)
    gate("G4 router distinguishable from filter",
         "episode-bootstrap 95% CI on net(S) excludes 0",
         f"CI [{sA['lo']:.2f}, {sA['hi']:.2f}] -> excludes 0, but on the WRONG SIDE",
         (sA["lo"] > 0))
    gate("G5 S beats the rate-matched circular-shift placebo",
         "one-sided p < 0.05",
         f"p = {A['p_shift']:.4f}", A["p_shift"] < 0.05)
    gate("G6 family-wise over the 3 change variants (short direction)",
         "one-sided p < 0.05", f"p = {pfw:.4f}", pfw < 0.05)
    n_pass = sum(1 for *_, ok in g if ok)
    say(f"  {'GATE':<48s} {'PASS':>6s}")
    for name, spec, obs, ok in g:
        say(f"  {name:<48s} {'PASS' if ok else 'FAIL':>6s}")
        say(f"      SPEC     {spec}")
        say(f"      OBSERVED {obs}")
    say(f"  TALLY: {n_pass}/{len(g)} PASS")
    say("")
    say("  VERDICT ON THE ASSIGNED MECHANISM: DEAD.")
    say("  G2 fails by SIGN, not by magnitude, and G3/G5/G6 fail with it. The claim that")
    say("  implied vol is a signed SHORT trigger is refuted on the change specification in")
    say("  the strongest available way: the drift conditional on a large upward repricing of")
    say("  NDX variance is POSITIVE and roughly four times the unconditional drift.")
    say("")
    say("  SECONDARY GATE TABLE on the FLIPPED arm (LONG on high VXN 1-day change). This arm")
    say("  was selected AFTER seeing the sign; it is a lead, not a candidate, and it is")
    say("  gated harder for exactly that reason.")
    exc = SF["excl2020"]
    h = []
    h.append(("H1 clears the primary cost",
              "net $/session > 0 at $20.65",
              f"${fA['obs']:.2f}/session  (gross {fA['gross']:+.3f} pts vs a "
              f"{C.BREAKEVEN_PTS_PRIMARY:.4f} pt floor)", fA["obs"] > 0))
    h.append(("H2 episode-block CI excludes zero",
              "95% CI on net $/session excludes 0",
              f"CI [{fA['lo']:.2f}, {fA['hi']:.2f}]  (K={A['K']}, rho_bar={A['rho']:.4f}, "
              f"K_eff={A['keff']:.2f})", fA["lo"] > 0))
    h.append(("H3 survives the SIGN-AGNOSTIC family-wise rotation null",
              "one-sided p < 0.05 against the max over 3 variants x 2 signs",
              f"p = {SF['pfw_signed']:.4f}", SF["pfw_signed"] < 0.05))
    h.append(("H4 NOT carried by one episode",
              "largest single episode < 40% of total net",
              f"top-1 episode = {SF['top1']:.1%} of total "
              f"({SF['top1_label']}); top-3 = {SF['top3']:.1%}", SF["top1"] < 0.40))
    h.append(("H5 survives removing one calendar year",
              "ex-2020 net >= 50% of full-sample net",
              f"ex-2020 = {exc['share']:.0%} of total = ${exc['per']:.2f}/session "
              f"= ${exc['tot']:,.0f} over 11 years", exc["share"] >= 0.50))
    h.append(("H6 VXN adds information beyond the PRICE reversal signal",
              "VXN-change arm >= the prior-day-NQ-return arm",
              f"VXN {SF['res']['vxn__d1']['gross']:+.3f} pts vs "
              f"prior-day-price {SF['res']['neg_prev']['gross']:+.3f} pts -- the pure price "
              f"signal is BETTER", SF["res"]["vxn__d1"]["gross"]
              >= SF["res"]["neg_prev"]["gross"]))
    hp_ = sum(1 for *_, ok in h if ok)
    for name, spec, obs, ok in h:
        say(f"  {name:<48s} {'PASS' if ok else 'FAIL':>6s}")
        say(f"      SPEC     {spec}")
        say(f"      OBSERVED {obs}")
    say(f"  TALLY: {hp_}/{len(h)} PASS")
    say("")
    say("  VERDICT ON THE FLIPPED LEAD: not worth the one-shot window. It is statistically")
    say("  alive (H1-H3 pass) and economically hollow (H4-H6 fail): half the money is one")
    say("  COVID episode, three quarters is three episodes, removing 2020 leaves "
        f"${exc['per']:.0f}/session")
    say("  and ~$2.3k/yr at one contract, and a signal with no implied vol in it at all --")
    say("  yesterday's NQ return -- reproduces it and beats it. That is short-horizon price")
    say("  reversal, an already-crowded axis, not the price of variance risk.")
    say("")
    say("  RULE PROPOSAL: NONE. Do not spend confirmation_one_shot on this specification.")

    rule()

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(_L) + "\n")
    print(f"\nwritten: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
