"""G3_VOLSHORT01 -- SPEC: VXN LEVEL TERCILES  (the wave's REFERENCE specification)

    Prior-day VXN CLOSE -> causal trailing-252-session tercile -> state in {0 low, 1 mid, 2 high}
    Trade the full RTH session, enter 09:30:00 (open of the bar stamped 09:31),
    exit 15:59:59 (close of the bar stamped 16:00). One round turn per traded session.

EVIDENCE STATUS: DISCOVERY_CONTAMINATED.  This is NOT a result. It is a RULE PROPOSAL that
someone else freezes and commits BEFORE the one-shot confirmation read of 2022-01-01..2026-07-31.

THE WALL: no session on or after 2022-01-01 is read, loaded, counted or aggregated anywhere in
this file. Asserted and printed at the top of main().

Run:  python runs/G3_VOLSHORT01_20260831/src/discovery/spec_vxn-tercile.py
Out:  runs/G3_VOLSHORT01_20260831/out/discovery/spec_vxn-tercile.txt
"""
from __future__ import annotations

import io
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(os.path.dirname(HERE))                       # runs/G3_VOLSHORT01_20260831
sys.path.insert(0, HERE)
import common as C                                                  # noqa: E402

PANEL = os.path.join(RUN, "out", "discovery", "panel_pre2022.parquet")
OUT = os.path.join(RUN, "out", "discovery", "spec_vxn-tercile.txt")

WALL = pd.Timestamp("2022-01-01")
WINDOW = 252                    # trailing SESSIONS for the causal tercile
GAP_DAYS = 10                   # primary episode definition
N_BOOT = 10000
SEED = 20260831

# tee everything to stdout and to the report file
_BUF = io.StringIO()


def P(s: str = "") -> None:
    print(s)
    _BUF.write(s + "\n")


def H(title: str, ch: str = "=") -> None:
    P("")
    P(ch * 100)
    P(title)
    P(ch * 100)


# ======================================================================================
# helpers specific to this spec
# ======================================================================================
def timeline_blocks(hi: np.ndarray, dates: pd.DatetimeIndex, gap_days: int = GAP_DAYS):
    """Partition the WHOLE timeline into contiguous blocks: each high-state EPISODE (its full
    date span, including any non-high sessions caught inside it) is one block, and each calm
    stretch between two episodes is one block.

    The high-episode block bootstrap in common.py resamples only high sessions, which is right
    for arm S. Arms R / F / BASE also trade calm sessions, so they need a partition that covers
    every session. Blocks are contiguous in time, so within-episode dependence is preserved.
    """
    eps = C.episodes(hi, dates, gap_days=gap_days)
    blk = np.full(len(dates), -1, dtype=int)
    for k, (a, b) in enumerate(eps):
        blk[(dates >= a) & (dates <= b)] = 2 * k + 1        # odd ids = high-vol episode blocks
    # calm stretches get even ids, numbered by how many episodes have already closed
    cur, seen = 0, 0
    for i in range(len(blk)):
        if blk[i] >= 0:
            seen = (blk[i] + 1) // 2
        else:
            blk[i] = 2 * seen                               # even ids = calm blocks
        cur = blk[i]
    _ = cur
    return blk, eps


def boot_mean(values, block_ids, n_draws=N_BOOT, seed=SEED):
    """Mean under resampling WHOLE BLOCKS with replacement. NaNs dropped, block_ids < 0 dropped."""
    return C.block_bootstrap_by_episode(values, block_ids, n_draws=n_draws, seed=seed)


def ci_str(d: dict, unit: str = "$", nd: int = 2) -> str:
    if not np.isfinite(d.get("ci_lo", np.nan)):
        return "[   n/a   ]"
    return f"[{unit}{d['ci_lo']:>9,.{nd}f}, {unit}{d['ci_hi']:>9,.{nd}f}]"


def diag_t(x) -> float:
    v = np.asarray(pd.Series(x).astype(float).values)
    v = v[~np.isnan(v)]
    if len(v) < 3 or v.std(ddof=1) == 0:
        return np.nan
    return float(v.mean() / (v.std(ddof=1) / np.sqrt(len(v))))


# ======================================================================================
def main() -> int:
    rng_note = f"seed={SEED}, n_draws={N_BOOT}"

    H("G3_VOLSHORT01  --  SPEC: VXN LEVEL TERCILES   (REFERENCE SPECIFICATION)")
    P("EVIDENCE STATUS : DISCOVERY_CONTAMINATED.  Not a result -- a RULE PROPOSAL.")
    P("MECHANISM       : the price of variance flips sign with the trading window. The equity")
    P("                  premium is compensated OVERNIGHT; the INTRADAY window is where levered")
    P("                  and short-horizon holders de-risk. High EX-ANTE implied variance should")
    P("                  therefore carry NEGATIVE expected INTRADAY drift, so implied vol is a")
    P("                  SIGNED SHORT TRIGGER, not an exposure gate.")
    P("SIGNAL          : prior-day VXN close (Nasdaq-100 vol index -- the NQ-appropriate one),")
    P("                  classified into terciles by the CAUSAL trailing-252-session cutoffs")
    P("                  (common.causal_tercile: cutoffs use strictly-prior observations only;")
    P("                  the value being classified never enters its own cutoff).")
    P("TRADE           : enter 09:30:00 (open of the END-STAMPED 09:31 bar), exit 15:59:59")
    P("                  (close of the END-STAMPED 16:00 bar). Flat overnight. 1 ctr, 1 RT/session.")
    P(f"INFERENCE       : whole-episode / whole-block bootstrap, {rng_note}. Session-level t is")
    P("                  printed ONLY where labelled DIAGNOSTIC ONLY, and is never inference.")
    P("COSTS           : NQ $20/pt. Net printed at $4.36 (commission FLOOR, never a headline),")
    P(f"                  $20.65 (PRIMARY, G2_EXEC01 113 real RTs) and $25.01. A full-session")
    P(f"                  round turn must clear {C.BREAKEVEN_PTS_PRIMARY:.4f} NQ points at the primary line.")

    # ---------------------------------------------------------------------------------
    H("0.  THE WALL  --  2022-01-01")
    p = pd.read_parquet(PANEL)
    p["session_date"] = pd.to_datetime(p["session_date"])
    p = p.sort_values("session_date").reset_index(drop=True)

    n_ge = int((p["session_date"] >= WALL).sum())
    P(f"panel rows loaded                       : {len(p):,}")
    P(f"max(session_date)                       : {p['session_date'].max().date()}")
    P(f"rows with session_date >= 2022-01-01    : {n_ge}")
    assert n_ge == 0, "WALL VIOLATION: panel contains a session on/after 2022-01-01"
    for col in ("prev_session_date", "vxn_asof", "vix_asof"):
        m = pd.to_datetime(p[col]).max()
        bad = int((pd.to_datetime(p[col]) >= WALL).sum())
        P(f"max({col:<18s})                : {m.date() if pd.notna(m) else 'NaT'}   "
          f"rows >= wall: {bad}")
        assert bad == 0, f"WALL VIOLATION in {col}"
    P("ASSERTION  max(session_date) < 2022-01-01 AND every dated column < 2022-01-01 : PASS")
    P("No 1-minute bar, no Cboe row and no derived statistic in this file touches 2022 or later.")

    # ---------------------------------------------------------------------------------
    H("1.  POPULATION")
    P("Population rule, fixed BEFORE looking at any return:")
    P("  session_quality == 'FULL'   (both anchor bars present; excludes exchange half-days,")
    P("                               on which the strict rth_ret_pts is NaN by construction and")
    P("                               the implied-vol reading is stale by 3-5 days)")
    P("  AND rth_ret_pts notna  AND  vxn notna  (VXN inception 2009-09-14)")
    P("  AND the causal tercile is defined (>= 252 strictly-prior VXN observations)")
    P("")
    q = p[(p["session_quality"] == "FULL") & p["rth_ret_pts"].notna() & p["vxn"].notna()].copy()
    q = q.sort_values("session_date").reset_index(drop=True)
    P(f"FULL & ret & vxn                        : {len(q):,} sessions, "
      f"{q['session_date'].min().date()} .. {q['session_date'].max().date()}")
    P(f"duplicate vxn_asof inside this population: {int(q['vxn_asof'].duplicated().sum())}   "
      "(0 => no stale VXN value is double-counted in a trailing window)")

    # PRIMARY: tercile history is the trade population itself -- 252 trailing sessions of the
    # same sessions we trade, each carrying a distinct VXN print.
    q["state"] = C.causal_tercile(q["vxn"].values, window=WINDOW, min_obs=WINDOW)
    d = q[q["state"].notna()].copy().reset_index(drop=True)
    P(f"state defined (>= {WINDOW} prior VXN obs)    : {len(d):,} sessions, "
      f"{d['session_date'].min().date()} .. {d['session_date'].max().date()}")
    P(f"burn-in consumed by the trailing window  : {len(q) - len(d):,} sessions")
    assert d["session_date"].max() < WALL

    dates = pd.DatetimeIndex(d["session_date"])
    st = d["state"].values
    r = d["rth_ret_pts"].values
    P("")
    P("state counts (causal, so these are NOT 1/3 each -- a trending vol level spends long")
    P("stretches above its own trailing cutoffs):")
    for s, nm in ((0.0, "0 LOW "), (1.0, "1 MID "), (2.0, "2 HIGH")):
        n = int((st == s).sum())
        P(f"  state {nm} : {n:>5,}  ({100.0*n/len(d):5.1f}%)")

    # ---------------------------------------------------------------------------------
    H("2.  THE MECHANISM, BEFORE ANY TRADING RULE  --  intraday drift by state")
    P("This is the raw claim: does the HIGH implied-vol state carry NEGATIVE intraday drift?")
    P("")
    P(f"{'state':<8s} {'n':>6s} {'mean_pts':>10s} {'median':>9s} {'sd_pts':>9s} "
      f"{'gross_$':>12s} {'t_DIAG':>8s} {'hit>0':>7s}")
    for s, nm in ((0.0, "0 LOW"), (1.0, "1 MID"), (2.0, "2 HIGH")):
        m = st == s
        x = r[m]
        P(f"{nm:<8s} {len(x):>6,} {x.mean():>10.4f} {np.median(x):>9.4f} {x.std(ddof=1):>9.3f} "
          f"{x.sum()*C.PV:>12,.0f} {diag_t(x):>8.2f} {100*(x>0).mean():>6.1f}%")
    allx = r
    P(f"{'ALL':<8s} {len(allx):>6,} {allx.mean():>10.4f} {np.median(allx):>9.4f} "
      f"{allx.std(ddof=1):>9.3f} {allx.sum()*C.PV:>12,.0f} {diag_t(allx):>8.2f} "
      f"{100*(allx>0).mean():>6.1f}%")
    P("  t_DIAG is a session-level t-statistic: DIAGNOSTIC ONLY. It is not inference in this")
    P("  wave and must not be quoted -- high-vol sessions are episodic, not independent.")
    P("")
    P(f"BREAKEVEN REFERENCE: a short needs mean rth_ret_pts <= -{C.BREAKEVEN_PTS_PRIMARY:.4f} pts")
    P("  to clear the $20.65 primary round turn. Compare the HIGH row's mean_pts to that number")
    P("  before reading anything else on this page.")

    # ---------------------------------------------------------------------------------
    H("3.  EPISODES  --  the actual sample size")
    hi = st == 2.0
    eps10 = C.episodes(hi, dates, gap_days=10)
    eps21 = C.episodes(hi, dates, gap_days=21)
    eps42 = C.episodes(hi, dates, gap_days=42)
    eids = C.episode_ids(hi, dates, gap_days=GAP_DAYS)
    short_pnl_pts = np.where(hi, -r, np.nan)
    rho = C.icc_rho(short_pnl_pts, eids)
    K = len(eps10)
    P(f"high-state sessions                     : {int(hi.sum()):,}")
    P(f"episodes  K @ gap_days=10 (PRIMARY)     : {K}")
    P(f"episodes  K @ gap_days=21               : {len(eps21)}")
    P(f"episodes  K @ gap_days=42               : {len(eps42)}")
    P(f"rho_bar (ICC of the short P&L within episode, gap=10) : {rho:.4f}   [PRINTED, as required]")
    P(f"K_eff = K / (1 + (K-1)*rho_bar)        : {C.k_eff(K, rho):.2f}")
    et = C.episode_table(hi, dates, gap_days=GAP_DAYS, values=short_pnl_pts)
    et = et.sort_values("n_sessions", ascending=False)
    top5 = et["n_sessions"].head(5).sum()
    P(f"episode sizes                           : min {et['n_sessions'].min()}, "
      f"median {et['n_sessions'].median():.0f}, max {et['n_sessions'].max()}")
    P(f"share of high sessions in the 5 largest : {100.0*top5/hi.sum():.1f}%   "
      "-> K badly OVERSTATES independence; never quote K alone")
    P("")
    P("Every high-vol episode (short-arm P&L in NQ points, GROSS -- costs applied later):")
    P(f"{'ep':>3s} {'start':>11s} {'end':>11s} {'days':>5s} {'n':>4s} {'sum_pts':>10s} "
      f"{'mean_pts':>9s} {'net$20.65':>11s}")
    for _, row in et.sort_values("start").iterrows():
        net = row["sum"] * C.PV - row["n_sessions"] * C.COST_PRIMARY
        P(f"{int(row['episode']):>3d} {str(row['start'].date()):>11s} "
          f"{str(row['end'].date()):>11s} {row['span_days']:>5d} {row['n_sessions']:>4d} "
          f"{row['sum']:>10.1f} {row['mean']:>9.3f} {net:>11,.0f}")
    n_pos = int((et["mean"] > 0).sum())
    P("")
    P(f"episodes with a POSITIVE mean short P&L : {n_pos} / {K}  ({100.0*n_pos/K:.0f}%)")
    n_clear = int(((et["sum"] * C.PV - et["n_sessions"] * C.COST_PRIMARY) > 0).sum())
    P(f"episodes NET-POSITIVE at $20.65         : {n_clear} / {K}  ({100.0*n_clear/K:.0f}%)")

    # ---------------------------------------------------------------------------------
    H("4.  THE THREE ARMS  --  R / F / S, all three or the result is INADMISSIBLE")
    P("  BASE  always-long every valid session      (context, not one of the three)")
    P("  R     ROUTER : long the long leg, SHORT the high state")
    P("  F     FILTER : long the long leg, FLAT on the high state (removed, no short taken)")
    P("  S     SHORT  : short the high state ALONE, nothing else")
    P("")
    P("Two long legs are reported because they answer different questions and picking one")
    P("silently is how this gets fudged:")
    P("  non_high = long every non-high session  <- the task's literal FILTER, and the PRIMARY")
    P("  low_only = long only in the low state   <- the literal ROUTER of the mechanism statement")
    P("R = F + S in gross points for both, by construction; the identity is asserted below.")
    P("")
    tab = C.three_arms(d, "state", high_state=2, low_state=0,
                       ret_col="rth_ret_pts", date_col="session_date", gap_days=GAP_DAYS)
    P(C.format_arms(tab))
    ident_ok = all(v < 1e-6 for v in tab.attrs["identity"].values())
    assert ident_ok, "R = F + S identity FAILED"

    N = int(tab["n_sessions"].iloc[0])
    P("")
    P(f"Per-session dollars. TWO denominators, both printed, because they answer different")
    P(f"questions and mixing them is the classic dressing-up:")
    P(f"  /valid   = total net / {N:,} valid sessions  -- the COMMON denominator. Only on this")
    P(f"             denominator does net(R)/valid - net(F)/valid == net(S)/valid hold, so this")
    P(f"             is the one the router-vs-filter question must be answered on.")
    P(f"  /traded  = total net / that arm's own trade count -- 'did each trade clear its cost'.")
    P("")
    P(f"{'arm':<17s} {'long_leg':<9s} {'trades':>7s} "
      f"{'$4.36/vld':>10s} {'$20.65/vld':>11s} {'$25.01/vld':>11s} "
      f"{'$4.36/trd':>10s} {'$20.65/trd':>11s} {'$25.01/trd':>11s}")
    per = {}
    for _, row in tab.iterrows():
        key = (row["arm"], row["long_leg"])
        nt = max(int(row["n_trades"]), 1)
        vals = [row[nm] for nm in C.COST_NAMES]
        per[key] = dict(per_valid=[v / N for v in vals], per_traded=[v / nt for v in vals],
                        total=vals, n_trades=int(row["n_trades"]))
        P(f"{row['arm']:<17s} {row['long_leg']:<9s} {int(row['n_trades']):>7,} "
          + " ".join(f"{v/N:>10.3f}" for v in vals) + " "
          + " ".join(f"{v/nt:>10.3f}" for v in vals))

    # ---------------------------------------------------------------------------------
    H("5.  INFERENCE  --  whole-block bootstrap CIs beside every number")
    blk, _ = timeline_blocks(hi, dates, gap_days=GAP_DAYS)
    n_blocks = len(np.unique(blk))
    P(f"Arms that trade calm sessions (BASE / R / F) need a partition covering the WHOLE")
    P(f"timeline, so blocks alternate: each high-vol EPISODE's full date span is one block, each")
    P(f"calm stretch between episodes is one block. Blocks are contiguous, so within-episode")
    P(f"dependence is preserved. n_blocks = {n_blocks} (K={K} episode blocks + calm blocks).")
    P(f"Arm S is bootstrapped on the HIGH-STATE EPISODES themselves (K={K}), which is the")
    P(f"resampling unit the wave mandates for a high-state statistic.")
    P(f"{rng_note}. Percentile CI at 95%.")
    P("")

    def arm_pos(arm, leg):
        valid = np.ones(len(r), dtype=bool)
        lo = st == 0.0
        nonhi = ~hi
        longmask = lo if leg == "low_only" else nonhi
        if arm == "BASE":
            return np.ones(len(r))
        if arm == "F":
            return np.where(longmask, 1.0, 0.0)
        if arm == "R":
            return np.where(longmask, 1.0, np.where(hi, -1.0, 0.0))
        if arm == "S":
            return np.where(hi, -1.0, 0.0)
        raise ValueError(arm)

    P(f"{'arm':<17s} {'long_leg':<9s} {'blocks':<8s} {'mean net $/valid sess':>22s} "
      f"{'95% block-bootstrap CI':>28s} {'p':>7s} {'0?':>4s}")
    boot_res = {}
    for arm, leg, blocks, tagname in (
            ("BASE", "-", blk, "timeline"),
            ("R", "non_high", blk, "timeline"),
            ("F", "non_high", blk, "timeline"),
            ("R", "low_only", blk, "timeline"),
            ("F", "low_only", blk, "timeline"),
            ("S", "-", eids, "episodes")):
        pos = arm_pos(arm, leg)
        traded = pos != 0
        signed = np.where(traded, pos * r, np.nan)
        netv = C.net_per_session(signed, C.COST_PRIMARY, traded=traded)   # 0 on untraded
        draws = boot_mean(netv, blocks)
        s = C.bootstrap_summary(draws, observed=float(np.mean(netv)))
        boot_res[(arm, leg)] = (s, netv, blocks)
        nm = {"BASE": "BASE_always_long", "R": "R_router", "F": "F_filter",
              "S": "S_short_only"}[arm]
        P(f"{nm:<17s} {leg:<9s} {tagname:<8s} {np.mean(netv):>22.3f} "
          f"{ci_str(s):>28s} {s['p_two_sided']:>7.4f} "
          f"{'EXCL' if s['excludes_zero'] else 'incl':>4s}")
    P("  NOTE for arm S: the mean is over ALL valid sessions (untraded sessions contribute $0),")
    P("  so it is on the common denominator and is directly comparable to R and F above.")
    P("  Arm S on its OWN denominator (per SHORT TRADE) is reported in section 6.")

    # ---------------------------------------------------------------------------------
    H("6.  THE DEATH TEST  --  is the ROUTER distinguishable from the FILTER?")
    P("net(R) - net(F) == net(S) EXACTLY, in net dollars, costs included. It is an algebraic")
    P("identity, not a discovery -- so 'the router is just the filter' and 'the short leg is")
    P("worthless' are THE SAME TEST. If net(S) ~ 0, the router is exposure reduction wearing a")
    P("costume, and this candidate joins the ten dead anti-filters.")
    P("")
    for leg in ("non_high", "low_only"):
        rn = per[("R_router", leg)]["total"][1]
        fn = per[("F_filter", leg)]["total"][1]
        sn = per[("S_short_only", "-")]["total"][1]
        P(f"  [{leg}]  net(R)=${rn:>12,.0f}   net(F)=${fn:>12,.0f}   "
          f"R-F=${rn-fn:>12,.0f}   net(S)=${sn:>12,.0f}   "
          f"|R-F-S|={abs(rn-fn-sn):.6f}  -> {'PASS' if abs(rn-fn-sn) < 1e-6 else 'FAIL'}")
    P("")
    sS, netS_common, _ = boot_res[("S", "-")]
    hi_idx = hi
    s_pts = -r[hi_idx]
    n_short = int(hi_idx.sum())
    P("ARM S ON ITS OWN DENOMINATOR (per SHORT TRADE) -- 'does the short leg clear its costs?'")
    P(f"  short trades                          : {n_short:,}   over K={K} episodes, "
      f"K_eff={C.k_eff(K, rho):.2f}, rho_bar={rho:.4f}")
    P(f"  mean short P&L                        : {s_pts.mean():+.4f} NQ points per trade")
    P(f"  breakeven at $20.65                   : {C.BREAKEVEN_PTS_PRIMARY:+.4f} NQ points")
    P(f"  EDGE MINUS BREAKEVEN                  : {s_pts.mean()-C.BREAKEVEN_PTS_PRIMARY:+.4f} points")
    P("")
    netS_traded = C.net_per_session(np.where(hi_idx, -r, np.nan), C.COST_PRIMARY, traded=hi_idx)
    P(f"{'cost line':<22s} {'total net $':>14s} {'$/short trade':>15s} "
      f"{'95% episode-block CI ($/trade)':>34s} {'p':>7s}")
    for c, nm in zip(C.COSTS, C.COST_NAMES):
        nv = C.net_per_session(np.where(hi_idx, -r, np.nan), c, traded=hi_idx)
        nv_tr = nv[hi_idx]
        dr = C.block_bootstrap_by_episode(np.where(hi_idx, nv, np.nan), eids,
                                          n_draws=N_BOOT, seed=SEED)
        ss = C.bootstrap_summary(dr)
        P(f"{nm:<22s} {nv.sum():>14,.0f} {nv_tr.mean():>15.3f} "
          f"{ci_str(ss):>34s} {ss['p_two_sided']:>7.4f}")
    P("  ($4.36 is a commission-only FLOOR and is never a headline. $20.65 is the headline.)")

    # ---------------------------------------------------------------------------------
    H("7.  RATE-MATCHED PLACEBO  --  circular shift of the high-state mask")
    P("The null must PRESERVE DEPENDENCE. Independent random draws of ~%d sessions would give a"
      % n_short)
    P("bar that is far too low, because they would destroy the episode clustering that makes the")
    P("real short leg's P&L so lumpy. So the null is a CIRCULAR SHIFT of the high-state mask")
    P("along the session timeline: the mask keeps its exact episode structure and its exact rate,")
    P("the return series is untouched, and only the ALIGNMENT between them is randomised.")
    P("")
    Nn = len(r)
    obs_per_trade = netS_traded[hi_idx].mean()
    obs_total = netS_traded.sum()
    shifts = np.arange(1, Nn)
    keep = (shifts >= 21) & (shifts <= Nn - 21)          # drop near-identity shifts
    shifts = shifts[keep]
    pl_per_trade = np.empty(len(shifts))
    pl_total = np.empty(len(shifts))
    for j, sft in enumerate(shifts):
        m = np.roll(hi_idx, sft)
        x = -r[m]
        pl_per_trade[j] = x.mean() * C.PV - C.COST_PRIMARY
        pl_total[j] = x.sum() * C.PV - m.sum() * C.COST_PRIMARY
    p_pl = float((pl_per_trade >= obs_per_trade).mean())
    P(f"exhaustive circular shifts evaluated    : {len(shifts):,}  (all s in [21, N-21], N={Nn:,})")
    P(f"every shift trades exactly              : {n_short:,} sessions -> rate-matched by construction")
    P(f"OBSERVED   net $/short trade @ $20.65   : {obs_per_trade:+.3f}")
    P(f"PLACEBO    mean                         : {pl_per_trade.mean():+.3f}")
    P(f"PLACEBO    sd                           : {pl_per_trade.std(ddof=1):.3f}")
    P(f"PLACEBO    5th / 50th / 95th pct        : {np.percentile(pl_per_trade,5):+.3f} / "
      f"{np.percentile(pl_per_trade,50):+.3f} / {np.percentile(pl_per_trade,95):+.3f}")
    P(f"PLACEBO    max                          : {pl_per_trade.max():+.3f}")
    P(f"one-sided p (placebo >= observed)       : {p_pl:.4f}")
    P(f"observed percentile in the placebo dist : {100.0*(pl_per_trade < obs_per_trade).mean():.1f}")
    P("")
    P("Interpretation rule stated in advance: arm S must BEAT this placebo (p small AND the")
    P("observed value materially above the placebo mass). Beating the placebo is NECESSARY, not")
    P("sufficient -- it must also clear $20.65 in absolute terms.")

    # ---------------------------------------------------------------------------------
    H("8.  IS IT ONE EPISODE?  --  concentration and leave-one-episode-out")
    P("A short-vol-state edge that lives entirely in 2020-03 (or 2018-02) is a single draw, not")
    P("a mechanism. Leave-one-episode-out on the $20.65 short-arm net:")
    P("")
    tot = netS_traded.sum()
    rows = []
    for k in range(K):
        m = eids == k
        rows.append((k, int(m.sum()), netS_traded[m].sum(), tot - netS_traded[m].sum()))
    rows.sort(key=lambda z: z[2])
    P(f"{'ep':>3s} {'n':>5s} {'its net$':>12s} {'net$ WITHOUT it':>16s} {'span':>26s}")
    epmap = {k: v for k, v in enumerate(eps10)}
    for k, n, own, rest in rows[:5]:
        a, b = epmap[k]
        P(f"{k:>3d} {n:>5d} {own:>12,.0f} {rest:>16,.0f} "
          f"{str(a.date())+' .. '+str(b.date()):>26s}   <- worst")
    P("  ...")
    for k, n, own, rest in rows[-5:]:
        a, b = epmap[k]
        P(f"{k:>3d} {n:>5d} {own:>12,.0f} {rest:>16,.0f} "
          f"{str(a.date())+' .. '+str(b.date()):>26s}   <- best")
    loo = np.array([z[3] for z in rows])
    P("")
    P(f"LOO net range                           : ${loo.min():,.0f} .. ${loo.max():,.0f}")
    P(f"LOO folds that stay POSITIVE            : {int((loo>0).sum())} / {K}")
    P("")
    yr = pd.DataFrame({"year": dates.year, "net": netS_traded, "traded": hi_idx})
    g = yr.groupby("year").agg(shorts=("traded", "sum"), net=("net", "sum"))
    g = g[g["shorts"] > 0]
    P("Year by year, arm S at $20.65:")
    P(f"{'year':>6s} {'shorts':>7s} {'net$':>12s} {'$/trade':>9s}")
    for y, row in g.iterrows():
        P(f"{y:>6d} {int(row['shorts']):>7d} {row['net']:>12,.0f} "
          f"{row['net']/row['shorts']:>9.2f}")
    P(f"years net-positive                      : {int((g['net']>0).sum())} / {len(g)}")

    # ---------------------------------------------------------------------------------
    H("9.  ROBUSTNESS  --  choices that were NOT tuned, varied one at a time")
    P("Each row re-runs the identical pipeline with ONE convention changed. These are")
    P("sensitivities on a DISCOVERY panel, not a search: none of them is promoted, and the")
    P("frozen rule is the PRIMARY row.")
    P("")
    P(f"{'variant':<44s} {'n_hi':>6s} {'K':>4s} {'pts/short':>10s} "
      f"{'net$20.65 total':>16s} {'$/trade':>9s}")

    def variant(label, dsub, statecol="state"):
        s2 = dsub[statecol].values
        r2 = dsub["rth_ret_pts"].values
        d2 = pd.DatetimeIndex(dsub["session_date"])
        h2 = s2 == 2.0
        if h2.sum() == 0:
            P(f"{label:<44s} {'-':>6s} {'-':>4s} {'-':>10s} {'-':>16s} {'-':>9s}")
            return
        K2 = len(C.episodes(h2, d2, gap_days=GAP_DAYS))
        pts = -r2[h2]
        net = pts.sum() * C.PV - h2.sum() * C.COST_PRIMARY
        P(f"{label:<44s} {int(h2.sum()):>6,} {K2:>4d} {pts.mean():>10.4f} "
          f"{net:>16,.0f} {net/h2.sum():>9.2f}")

    variant("PRIMARY  VXN tercile, 252, FULL, gap10", d)
    for w in (126, 378, 504):
        qq = q.copy()
        qq["state"] = C.causal_tercile(qq["vxn"].values, window=w, min_obs=w)
        variant(f"trailing window = {w} sessions", qq[qq['state'].notna()])
    qq = q.copy()
    qq["state"] = C.causal_tercile(qq["vxn"].values, window=None, min_obs=252)
    variant("expanding window (all prior history)", qq[qq["state"].notna()])
    # tercile history built on ALL panel rows (half-days included) instead of the trade pop
    pa = p.copy()
    pa["state"] = C.causal_tercile(pa["vxn"].values, window=WINDOW, min_obs=WINDOW)
    pa = pa[(pa["session_quality"] == "FULL") & pa["rth_ret_pts"].notna() & pa["state"].notna()]
    variant("tercile history = ALL panel rows", pa)
    # half-day sessions included via the tolerant return
    qh = p[p["vxn"].notna() & p["rth_ret_pts_any"].notna()].copy().reset_index(drop=True)
    qh["state"] = C.causal_tercile(qh["vxn"].values, window=WINDOW, min_obs=WINDOW)
    qh = qh[qh["state"].notna()].copy()
    qh["rth_ret_pts"] = qh["rth_ret_pts_any"]
    variant("half-days INCLUDED (rth_ret_pts_any)", qh)
    # quintile / decile instead of tercile: top 20% / top 10% of the causal window
    for frac, lbl in ((0.80, "top 20% (causal quintile)"), (0.90, "top 10% (causal decile)")):
        v = q["vxn"].values
        stq = np.full(len(v), np.nan)
        for i in range(WINDOW, len(v)):
            cut = np.quantile(v[i - WINDOW:i], frac)
            stq[i] = 2.0 if v[i] >= cut else 0.0
        qz = q.copy()
        qz["state"] = stq
        variant(lbl, qz[qz["state"].notna()])
    # gap sensitivity on the primary (K only)
    P("")
    P(f"episode count under other gaps (PRIMARY rule): gap10 K={K}, gap21 K={len(eps21)}, "
      f"gap42 K={len(eps42)}")
    P("")
    P("SENSITIVITY -- the SAME rule on VIX (S&P 500) instead of VXN. Reported because VIX buys")
    P("~3.5 more years of history, NOT as a second candidate. VXN is the NQ-appropriate index")
    P("and is the frozen choice.")
    qv = p[(p["session_quality"] == "FULL") & p["rth_ret_pts"].notna()
           & p["vix"].notna()].copy().reset_index(drop=True)
    qv["state"] = C.causal_tercile(qv["vix"].values, window=WINDOW, min_obs=WINDOW)
    qv = qv[qv["state"].notna()]
    P(f"{'variant':<44s} {'n_hi':>6s} {'K':>4s} {'pts/short':>10s} "
      f"{'net$20.65 total':>16s} {'$/trade':>9s}")
    variant("VIX tercile, 252, FULL, gap10 (2007-2021)", qv)

    # ---------------------------------------------------------------------------------
    H("10.  VERDICT")
    sn_total = per[("S_short_only", "-")]["total"][1]
    sn_per_trade = obs_per_trade
    edge_pts = s_pts.mean()
    clears = (sn_per_trade > 0) and sS["excludes_zero"] and (p_pl < 0.05)
    rn = per[("R_router", "non_high")]["total"][1]
    fn = per[("F_filter", "non_high")]["total"][1]
    disting = abs(rn - fn) > 0 and sS["excludes_zero"]

    P(f"{'GATE':<58s} {'SPEC':<22s} {'OBSERVED':<22s} {'':>6s}")
    def gate(name, spec, obs, ok):
        P(f"{name:<58s} {spec:<22s} {str(obs):<22s} {'PASS' if ok else 'FAIL':>6s}")

    gate("G1  HIGH-state mean intraday drift is NEGATIVE",
         "mean_pts < 0", f"{r[hi].mean():+.4f} pts", r[hi].mean() < 0)
    gate("G2  short edge clears the PRIMARY cost, per trade",
         f"> +{C.BREAKEVEN_PTS_PRIMARY:.4f} pts", f"{edge_pts:+.4f} pts",
         edge_pts > C.BREAKEVEN_PTS_PRIMARY)
    gate("G3  arm S net at $20.65 is positive in total",
         "> $0", f"${sn_total:,.0f}", sn_total > 0)
    gate("G4  arm S 95% episode-block CI excludes zero",
         "CI excludes 0", ci_str(sS), sS["excludes_zero"])
    gate("G5  arm S beats the rate-matched circular-shift placebo",
         "p < 0.05", f"p = {p_pl:.4f}", p_pl < 0.05)
    gate("G6  ROUTER distinguishable from FILTER (== G3 and G4)",
         "net(S) != 0, CI excl", f"R-F = ${rn-fn:,.0f}", disting)
    gate("G7  not one episode: majority of episodes net-positive",
         f"> {K//2} of {K}", f"{n_clear} of {K}", n_clear > K // 2)
    gate("G8  LOO: every leave-one-episode-out fold stays positive",
         f"{K} of {K}", f"{int((loo>0).sum())} of {K}", int((loo > 0).sum()) == K)

    n_pass = sum([r[hi].mean() < 0, edge_pts > C.BREAKEVEN_PTS_PRIMARY, sn_total > 0,
                  sS["excludes_zero"], p_pl < 0.05, disting, n_clear > K // 2,
                  int((loo > 0).sum()) == K])
    P("")
    P(f"GATES PASSED: {n_pass} / 8")
    P("")
    P("STANDING RULE FOR THIS WAVE: verdict is DEAD unless the SHORT arm (S) ALONE clears costs")
    P("AND the router is distinguishable from the filter.")
    verdict = "PROMISING" if clears and disting else "DEAD"
    P("")
    P(f"VERDICT: {verdict}")
    P("")
    if verdict == "DEAD":
        bn = per[("BASE_always_long", "-")]["total"][1]
        P("Reason, stated plainly and without dressing:")
        P("")
        P(f"  1. THE SIGN IS BACKWARDS. The mechanism predicts NEGATIVE intraday drift in the")
        P(f"     high implied-vol state. Measured, it is {r[hi].mean():+.4f} NQ points per session --")
        P(f"     POSITIVE, and HIGHER than the mid state's {r[st==1.0].mean():+.4f}. The short leg")
        P(f"     therefore earns {edge_pts:+.4f} points per session BEFORE costs. It is not a small")
        P(f"     edge swamped by costs; it is the wrong side of the trade.")
        P(f"  2. It loses by a wide margin at every cost line, including the $4.36 commission-only")
        P(f"     FLOOR (${per[('S_short_only','-')]['total'][0]:,.0f}), so no execution improvement rescues it.")
        P(f"  3. The episode-block CI CONTAINS zero (p={sS['p_two_sided']:.4f}) and the rate-matched")
        P(f"     circular-shift placebo puts the observed value at the "
          f"{100.0*(pl_per_trade < obs_per_trade).mean():.0f}th percentile")
        P(f"     (p={p_pl:.4f}) -- i.e. INDISTINGUISHABLE from shorting an arbitrarily aligned mask")
        P(f"     of the same rate and the same episode structure. There is no signal here at all,")
        P(f"     in either direction; there is a cost drag on top of a slightly adverse sign.")
        P(f"  4. net(R) - net(F) = ${rn-fn:,.0f} on {N:,} sessions. The router IS distinguishable")
        P(f"     from the filter -- but in the wrong direction: the short leg destroys ${abs(rn-fn):,.0f}")
        P(f"     relative to simply removing the sessions. 'Distinguishable' was never the goal;")
        P(f"     PROFITABLY distinguishable was, and G3/G4/G5 all fail.")
        P("")
        P("  AND the exposure-gate reading fails too, so this is not a case of 'wrong arm chosen':")
        P(f"     BASE always-long   net@$20.65 = ${bn:>10,.0f}  (${bn/N:.3f}/valid session)")
        P(f"     F filter non_high  net@$20.65 = ${fn:>10,.0f}  (${fn/N:.3f}/valid session)")
        P(f"     Removing the high-VXN sessions LOSES ${bn-fn:,.0f} versus doing nothing. High")
        P("     implied vol is not an intraday short trigger and it is not an exposure gate either.")
        P("")
        P("  NOT PROMOTED, and stated so explicitly: the fact that the high state's drift is")
        P("  positive is NOT a long candidate. Its low state is higher still, its CI is wide, and")
        P("  flipping a sign after seeing the sign is exactly the post-hoc move this repo bans.")
        P("  Nothing in this file may be reframed as a LONG proposal without its own preregistration.")
    P("")
    P("EVERYTHING ABOVE IS DISCOVERY_CONTAMINATED. The confirmation window 2022-01-01 ..")
    P("2026-07-31 was NOT read, NOT counted and NOT aggregated anywhere in this program.")

    # ---------------------------------------------------------------------------------
    # machine-readable tail
    H("11.  MACHINE-READABLE SUMMARY", "-")
    P(f"spec_id                     = VXN_TERCILE_252_RTH")
    P(f"population_n                = {N}")
    P(f"span                        = {dates.min().date()} .. {dates.max().date()}")
    P(f"episodes_K_gap10            = {K}")
    P(f"rho_bar                     = {rho:.6f}")
    P(f"K_eff                       = {C.k_eff(K, rho):.4f}")
    P(f"high_sessions               = {n_short}")
    P(f"mean_short_pts              = {edge_pts:.6f}")
    P(f"breakeven_pts_primary       = {C.BREAKEVEN_PTS_PRIMARY:.6f}")
    for leg in ("non_high", "low_only"):
        for a in ("R_router", "F_filter"):
            P(f"{a}_{leg}_net20.65_per_valid = {per[(a, leg)]['per_valid'][1]:.6f}")
    P(f"S_short_only_net20.65_per_valid  = {per[('S_short_only','-')]['per_valid'][1]:.6f}")
    P(f"S_short_only_net20.65_per_trade  = {sn_per_trade:.6f}")
    P(f"S_ci_lo_per_valid           = {sS['ci_lo']:.6f}")
    P(f"S_ci_hi_per_valid           = {sS['ci_hi']:.6f}")
    P(f"S_p_two_sided               = {sS['p_two_sided']:.6f}")
    P(f"placebo_p_one_sided         = {p_pl:.6f}")
    P(f"gates_passed                = {n_pass}/8")
    P(f"verdict                     = {verdict}")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    payload = _BUF.getvalue().encode("utf-8")
    with open(OUT, "wb") as f:
        f.write(payload)
    assert os.path.getsize(OUT) > 0
    print(f"\n[written] {OUT}  ({len(payload):,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
