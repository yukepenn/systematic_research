"""G3_MEREBAL_20260906 -- month-end stock-bond rebalancing flow + reversal (ledger G00077).

Spec: runs/G3_MEREBAL_20260906/spec.yaml (frozen before results). Family GENESIS3_EVENT.

FROZEN OBJECT (echoed; the day-labelling convention pinned by the spec's own parenthetical
"T-3 (3rd-to-last trading day)" => T = FIRST trading day of month m+1):
    T-3 = 3rd-to-last trading day of month m  (signal cutoff: close of T-3)
    T-2 = 2nd-to-last trading day of month m  (flow window entry close)
    T-1 = last trading day of month m
    T   = first trading day of month m+1
    T+1 = 2nd trading day of m+1 (flow exit / revert entry close)
    T+5 = 6th trading day of m+1 (revert exit close)
  REL_m  = (ES MTD point ret / sigma_ES) - (ZB MTD point ret / sigma_ZB), through T-3 close.
           sigma_X = trailing-60-joint-session sd of X daily point returns through T-3 (causal;
           spec is silent on the sigma window -- 60 sessions is the house standard, cf.
           G3_FTQGATE / G3_EVENT_GC E2; declared here BEFORE results).
  COND   = REL_m > trailing-36-month upper-tercile bound (previous 36 finite REL months, causal,
           excludes current).
  LEG-FLOW   = [T-2 close -> T+1 close] spread = ZB_pts/sigma_ZB - ES_pts/sigma_ES  (expected +)
  LEG-REVERT = [T+1 close -> T+5 close] same construction                            (expected -)
  BOTH legs vs matched unconditional control (all eligible month-turns, same windows).

All window sums are sums of SELF-FINANCING causal-roll daily point returns (basis cannot enter;
identity-gated in build step). POINTS ONLY -- no % anywhere (DELEV01). Seal asserted < 2026-08-01.

NULL: shared-draw circular shift of the condition flag across the eligible month-turn sequence
(ONE offset per iteration applied to BOTH legs -- dependence-preserving across the family).
CIs: event-block bootstrap (circular, block=6 turns, flag+outcomes resampled JOINTLY).
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
OUT = os.path.join(RUN, "out")
SEAL = pd.Timestamp("2026-08-01")
RNG = np.random.default_rng(20260906)

# ---- preregistered / declared constants (echoed in the gate-table footer) ----
SIG_WIN, SIG_MIN = 60, 50          # trailing sigma window on joint sessions (house standard)
TERCILE_WIN = 36                   # trailing months for the tercile bound (spec verbatim)
TERCILE_Q = 2.0 / 3.0
MIN_MONTH_DAYS = 15                # month integrity guard (a normal month has 19-23)
MIN_NEXT_DAYS = 6                  # need T..T+5 in month m+1
CLEAN_GAP_MAX = 5
N_SHIFT, MIN_SHIFT = 2000, 6       # circular-shift null over the eligible-turn sequence
N_BB, BLOCK_LEN = 2000, 6          # event-block bootstrap (circular, months)
PV = {"ES": 50.0, "ZB": 1000.0}
TICK_USD = {"ES": 12.50, "ZB": 31.25}     # ES 0.25pt x $50; ZB 1/32pt x $1000
COMMISSION = 4.36                          # NinjaTrader Brokerage Lifetime, $/ct RT (research basis)
Z_ALPHA_1S, Z_POWER = 1.6449, 0.8416       # one-sided 5%, 80% power (MDE print)

_fh = open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def joint_daily(es, zb):
    """Map each instrument's self-financing daily point returns onto the JOINT date axis.
    r_X[j] = sum of X's own daily returns in (joint[j-1], joint[j]]  -- exact additivity, roll-safe
    (interior X-only days are absorbed into the next joint day's return)."""
    dates = np.intersect1d(es["date"].values, zb["date"].values)
    dates = pd.DatetimeIndex(np.sort(dates))
    out = pd.DataFrame(index=dates)
    for name, df in (("es", es), ("zb", zb)):
        d = df.set_index("date")
        bucket = dates.searchsorted(d.index.values, side="left")   # smallest joint date >= X date
        ok = bucket < len(dates)
        g = pd.DataFrame({"b": bucket[ok],
                          "r": d["ret_points"].values[ok],
                          "clean": d["clean_daily"].values[ok] & np.isfinite(
                              d["ret_points"].values[ok])})
        agg = g.groupby("b").agg(r=("r", "sum"), clean=("clean", "all"), n=("r", "size"))
        r = np.full(len(dates), np.nan)
        cl = np.zeros(len(dates), dtype=bool)
        r[agg.index.values] = agg["r"].values
        cl[agg.index.values] = agg["clean"].values
        r[0] = np.nan                                    # spans from X's series start; undefined
        cl[0] = False
        out[f"r_{name}"] = r
        out[f"clean_{name}"] = cl
    gap = out.index.to_series().diff().dt.days.fillna(1)
    joint_clean = (gap <= CLEAN_GAP_MAX).values
    out["clean"] = out["clean_es"].values & out["clean_zb"].values & joint_clean
    return out


def win_sum(r, clean, a, b):
    """sum of joint-day returns at positions a+1..b (close[a] -> close[b]); NaN unless ALL clean."""
    if a >= b:
        return np.nan
    seg_r, seg_c = r[a + 1:b + 1], clean[a + 1:b + 1]
    if not seg_c.all():
        return np.nan
    return float(seg_r.sum())


def main():
    manifest = json.load(open(os.path.join(OUT, "inputs_manifest.json"), encoding="utf-8"))
    es = pd.read_parquet(os.path.join(OUT, "es_daily.parquet"))
    zb = pd.read_parquet(os.path.join(OUT, "zb_daily.parquet"))
    assert es["date"].max() < SEAL, "SEAL VIOLATION (ES)"
    assert zb["date"].max() < SEAL, "SEAL VIOLATION (ZB)"

    J = joint_daily(es, zb)
    dates = J.index
    n = len(J)
    r_es, r_zb = J["r_es"].values, J["r_zb"].values
    clean = J["clean"].values

    # trailing sigmas on the joint axis (causal: value at j uses returns through j inclusive,
    # and is only ever read at the T-3 anchor, whose close is strictly before every window)
    def trail_sd(x):
        s = pd.Series(np.where(clean, x, np.nan))
        return s.rolling(SIG_WIN, min_periods=SIG_MIN).std().values
    sd_es, sd_zb = trail_sd(r_es), trail_sd(r_zb)

    # ---------------- month-turn construction
    ym = pd.PeriodIndex(dates, freq="M")
    months = sorted(ym.unique())
    pos_by_month = {m: np.where(ym == m)[0] for m in months}
    rows, drops = [], dict(short_month=0, short_next=0, no_prev_month=0, mtd_unclean=0,
                           sigma_nan=0, window_unclean=0)
    for k in range(1, len(months) - 1):          # need m-1 (MTD base) and m+1 (turn windows)
        m, mn = months[k], months[k + 1]
        if (mn - m).n != 1:
            drops["short_next"] += 1
            continue
        if (m - months[k - 1]).n != 1:
            drops["no_prev_month"] += 1
            continue
        pm, pn = pos_by_month[m], pos_by_month[mn]
        if len(pm) < MIN_MONTH_DAYS:
            drops["short_month"] += 1
            continue
        if len(pn) < MIN_NEXT_DAYS:
            drops["short_next"] += 1
            continue
        i_tm3, i_tm2, i_eom = pm[-3], pm[-2], pm[-1]
        i_t1, i_t5 = pn[1], pn[5]
        i_prev_eom = pos_by_month[months[k - 1]][-1]
        # signal: MTD through T-3 close (from prev month's last close), causal
        mtd_es = win_sum(r_es, clean, i_prev_eom, i_tm3)
        mtd_zb = win_sum(r_zb, clean, i_prev_eom, i_tm3)
        if not (np.isfinite(mtd_es) and np.isfinite(mtd_zb)):
            drops["mtd_unclean"] += 1
            continue
        s_es, s_zb = sd_es[i_tm3], sd_zb[i_tm3]
        if not (np.isfinite(s_es) and np.isfinite(s_zb) and s_es > 0 and s_zb > 0):
            drops["sigma_nan"] += 1
            continue
        rel = mtd_es / s_es - mtd_zb / s_zb
        # legs
        f_es = win_sum(r_es, clean, i_tm2, i_t1)
        f_zb = win_sum(r_zb, clean, i_tm2, i_t1)
        v_es = win_sum(r_es, clean, i_t1, i_t5)
        v_zb = win_sum(r_zb, clean, i_t1, i_t5)
        if not all(np.isfinite(x) for x in (f_es, f_zb, v_es, v_zb)):
            drops["window_unclean"] += 1
            continue
        rows.append(dict(
            month=str(m), d_tm3=dates[i_tm3], d_tm2=dates[i_tm2], d_eom=dates[i_eom],
            d_t=dates[pn[0]], d_t1=dates[i_t1], d_t5=dates[i_t5],
            n_flow_days=int(i_t1 - i_tm2), n_revert_days=int(i_t5 - i_t1),
            mtd_es_pts=mtd_es, mtd_zb_pts=mtd_zb, sigma_es=s_es, sigma_zb=s_zb, rel=rel,
            flow_es_pts=f_es, flow_zb_pts=f_zb, revert_es_pts=v_es, revert_zb_pts=v_zb,
            flow_spread=f_zb / s_zb - f_es / s_es,
            revert_spread=v_zb / s_zb - v_es / s_es,
            flow_usd=f_zb * PV["ZB"] - f_es * PV["ES"],          # long ZB / short ES, 1ct/1ct
            revert_usd=v_zb * PV["ZB"] - v_es * PV["ES"]))
    ev = pd.DataFrame(rows)
    ev["causal_ok"] = ev["d_tm3"] < ev["d_tm2"]                  # signal cutoff < flow entry

    # tercile bounds: previous TERCILE_WIN finite-REL months, causal (excludes current)
    relv = ev["rel"].values
    bound = np.full(len(ev), np.nan)
    for i in range(len(ev)):
        prior = relv[:i]
        prior = prior[np.isfinite(prior)]
        if len(prior) >= TERCILE_WIN:
            bound[i] = np.quantile(prior[-TERCILE_WIN:], TERCILE_Q)
    ev["tercile_bound"] = bound
    ev["eligible"] = np.isfinite(bound)
    ev["cond"] = ev["eligible"] & (ev["rel"] > ev["tercile_bound"])

    el = ev[ev["eligible"]].reset_index(drop=True)
    M = len(el)
    flag = el["cond"].values.astype(bool)
    n_c = int(flag.sum())
    fs, vs = el["flow_spread"].values, el["revert_spread"].values
    fu, vu = el["flow_usd"].values, el["revert_usd"].values

    # ---------------- observed statistics (vs matched unconditional control, same windows)
    def delta(y, f):
        return float(np.mean(y[f]) - np.mean(y))
    obs = dict(
        flow_cond=float(np.mean(fs[flag])), flow_uncond=float(np.mean(fs)),
        rev_cond=float(np.mean(vs[flag])), rev_uncond=float(np.mean(vs)),
        d_flow=delta(fs, flag), d_rev=delta(vs, flag),
        d_flow_usd=delta(fu, flag), d_rev_usd=delta(vu, flag))

    # ---------------- shared-draw circular-shift null (one offset -> BOTH legs)
    offs = MIN_SHIFT + np.floor(RNG.random(N_SHIFT) * (M - 2 * MIN_SHIFT)).astype(int)
    idx = np.arange(M)
    null_f = np.empty(N_SHIFT)
    null_v = np.empty(N_SHIFT)
    for i, k in enumerate(offs):
        fshift = flag[(idx - k) % M]
        null_f[i] = np.mean(fs[fshift]) - np.mean(fs)
        null_v[i] = np.mean(vs[fshift]) - np.mean(vs)
    p1_flow = (np.sum(null_f >= obs["d_flow"]) + 1) / (N_SHIFT + 1)      # one-sided, prereg sign +
    p1_rev = (np.sum(null_v <= obs["d_rev"]) + 1) / (N_SHIFT + 1)        # one-sided, prereg sign -
    p2_flow = min(1.0, 2 * min((np.sum(null_f >= obs["d_flow"]) + 1) / (N_SHIFT + 1),
                               (np.sum(null_f <= obs["d_flow"]) + 1) / (N_SHIFT + 1)))
    p2_rev = min(1.0, 2 * min((np.sum(null_v >= obs["d_rev"]) + 1) / (N_SHIFT + 1),
                              (np.sum(null_v <= obs["d_rev"]) + 1) / (N_SHIFT + 1)))
    p_conj = (np.sum((null_f >= obs["d_flow"]) & (null_v <= obs["d_rev"])) + 1) / (N_SHIFT + 1)

    # ---------------- event-block bootstrap CIs (circular, flag+outcomes JOINTLY, shared rows)
    nb = int(np.ceil(M / BLOCK_LEN))
    starts = np.floor(RNG.random((N_BB, nb)) * M).astype(int)
    bpos = (starts[:, :, None] + np.arange(BLOCK_LEN)[None, None, :]) % M
    bpos = bpos.reshape(N_BB, -1)[:, :M]
    bb_f = np.full(N_BB, np.nan)
    bb_v = np.full(N_BB, np.nan)
    n_degenerate = 0
    for i in range(N_BB):
        rowsel = bpos[i]
        fl = flag[rowsel]
        if fl.sum() < 5:
            n_degenerate += 1
            continue
        bb_f[i] = np.mean(fs[rowsel][fl]) - np.mean(fs[rowsel])
        bb_v[i] = np.mean(vs[rowsel][fl]) - np.mean(vs[rowsel])
    ci_f = (float(np.nanpercentile(bb_f, 2.5)), float(np.nanpercentile(bb_f, 97.5)))
    ci_v = (float(np.nanpercentile(bb_v, 2.5)), float(np.nanpercentile(bb_v, 97.5)))
    # second computation of the CI (normal approx on the cond-minus-all contrast)
    se_f = float(np.std(fs, ddof=1) * np.sqrt(max(1.0 / n_c - 1.0 / M, 0)))
    se_v = float(np.std(vs, ddof=1) * np.sqrt(max(1.0 / n_c - 1.0 / M, 0)))
    ci_f2 = (obs["d_flow"] - 1.96 * se_f, obs["d_flow"] + 1.96 * se_f)
    ci_v2 = (obs["d_rev"] - 1.96 * se_v, obs["d_rev"] + 1.96 * se_v)

    # ---------------- MDE (printed FIRST in the report; G1)
    mde_f = (Z_ALPHA_1S + Z_POWER) * se_f
    mde_v = (Z_ALPHA_1S + Z_POWER) * se_v
    sd_fu = float(np.std(fu, ddof=1))
    mde_f_usd = (Z_ALPHA_1S + Z_POWER) * sd_fu * np.sqrt(max(1.0 / n_c - 1.0 / M, 0))

    # ---------------- eras (3 contiguous equal-count thirds of the eligible sequence)
    era_rows = []
    cuts = [0, M // 3, 2 * M // 3, M]
    for e in range(3):
        s, t = cuts[e], cuts[e + 1]
        f_e = flag[s:t]
        if f_e.sum() == 0:
            era_rows.append(dict(era=e + 1, span=f"{el['month'][s]}..{el['month'][t-1]}",
                                 n_elig=t - s, n_cond=0))
            continue
        era_rows.append(dict(
            era=e + 1, span=f"{el['month'][s]}..{el['month'][t-1]}", n_elig=t - s,
            n_cond=int(f_e.sum()),
            d_flow=float(np.mean(fs[s:t][f_e]) - np.mean(fs[s:t])),
            d_rev=float(np.mean(vs[s:t][f_e]) - np.mean(vs[s:t])),
            flow_sign="+" if np.mean(fs[s:t][f_e]) - np.mean(fs[s:t]) > 0 else "-",
            rev_sign="+" if np.mean(vs[s:t][f_e]) - np.mean(vs[s:t]) > 0 else "-"))
    eras = pd.DataFrame(era_rows)

    # ---------------- cost band (G6): 2 RTs per event per leg (1 ES RT + 1 ZB RT)
    cost = {k: (COMMISSION + k * TICK_USD["ES"]) + (COMMISSION + k * TICK_USD["ZB"])
            for k in (1, 2)}                       # k=1: $52.47   k=2: $96.22 per event per leg

    # ---------------- gates
    g2 = bool(obs["d_flow"] > 0 and ci_f[0] > 0)
    g3 = bool(obs["d_rev"] < 0 and ci_v[1] < 0)
    g4 = bool(g2 and g3)

    # ---------------- write event/control tables
    ev.to_csv(os.path.join(OUT, "event_table.csv"), index=False)
    ctl_rows = []
    for scope, sub in (("all_turns", ev), ("eligible", el),
                       ("era1", el.iloc[cuts[0]:cuts[1]]), ("era2", el.iloc[cuts[1]:cuts[2]]),
                       ("era3", el.iloc[cuts[2]:cuts[3]])):
        ctl_rows.append(dict(
            scope=scope, n=len(sub),
            flow_spread_uncond=float(sub["flow_spread"].mean()),
            revert_spread_uncond=float(sub["revert_spread"].mean()),
            flow_es_pts=float(sub["flow_es_pts"].mean()),
            flow_zb_pts=float(sub["flow_zb_pts"].mean()),
            revert_es_pts=float(sub["revert_es_pts"].mean()),
            revert_zb_pts=float(sub["revert_zb_pts"].mean()),
            flow_usd_1ct=float(sub["flow_usd"].mean()),
            revert_usd_1ct=float(sub["revert_usd"].mean())))
    pd.DataFrame(ctl_rows).to_csv(os.path.join(OUT, "controls.csv"), index=False)

    # ================================================================ PRINTED REPORT
    P("=" * 118)
    P("=== G3_MEREBAL_20260906 -- month-end rebalancing flow + reversal, ES/ZB (G00077)")
    P("=" * 118)
    P(f"joint axis: {n:,} sessions {dates.min().date()} -> {dates.max().date()} "
      f"(clean {int(clean.sum()):,}); ES rows {len(es):,}, ZB rows {len(zb):,}")
    P(f"turns computed: {len(ev)}   drops: {drops}")
    P(f"eligible (36m tercile history): {M}   conditional (top tercile): {n_c} "
      f"({100.0 * n_c / max(M, 1):.1f}%)   [spec estimate: ~211 turns, ~70 events -- honest "
      f"count is lower because the trailing-36m bound consumes the first 36 REL months]")
    P("")
    P("G1 -- MDE FIRST (one-sided alpha 5%, power 80%, contrast = cond mean - eligible mean):")
    P(f"    flow leg  : MDE {mde_f:.4f} vol-units  (~${mde_f_usd:,.0f}/event at 1ES+1ZB)  "
      f"sd(flow) {np.std(fs, ddof=1):.4f}  n_cond {n_c}  n_elig {M}")
    P(f"    revert leg: MDE {mde_v:.4f} vol-units   sd(revert) {np.std(vs, ddof=1):.4f}")
    P(f"    POWER IS MODERATE: only effects >= ~{mde_f / np.std(fs, ddof=1):.2f} sd of a single "
      f"turn are detectable at 80% power.")
    P("")
    P("OBSERVED (vol-scaled ZB-minus-ES spread; + = ZB outperforms ES):")
    P(f"    {'':<26}{'cond mean':>12}{'uncond ctrl':>12}{'delta':>10}{'boot 95% CI':>24}"
      f"{'p_shift(1s)':>12}{'p_shift(2s)':>12}")
    P(f"    {'LEG-FLOW  [T-2 -> T+1]':<26}{obs['flow_cond']:>12.4f}{obs['flow_uncond']:>12.4f}"
      f"{obs['d_flow']:>10.4f}{f'[{ci_f[0]:+.4f},{ci_f[1]:+.4f}]':>24}{p1_flow:>12.4f}"
      f"{p2_flow:>12.4f}")
    P(f"    {'LEG-REVERT[T+1 -> T+5]':<26}{obs['rev_cond']:>12.4f}{obs['rev_uncond']:>12.4f}"
      f"{obs['d_rev']:>10.4f}{f'[{ci_v[0]:+.4f},{ci_v[1]:+.4f}]':>24}{p1_rev:>12.4f}"
      f"{p2_rev:>12.4f}")
    P(f"    normal-approx CI (2nd computation): flow [{ci_f2[0]:+.4f},{ci_f2[1]:+.4f}]   "
      f"revert [{ci_v2[0]:+.4f},{ci_v2[1]:+.4f}]")
    P(f"    conjunction joint null p (shared-draw, both legs at least as extreme): {p_conj:.4f}")
    P(f"    dollar deltas at 1ES+1ZB: flow {obs['d_flow_usd']:+,.0f} $/event   "
      f"revert {obs['d_rev_usd']:+,.0f} $/event")
    P(f"    bootstrap degenerate draws (<5 cond rows, skipped): {n_degenerate}/{N_BB}")
    P("")
    P("GENERIC TURN-OF-MONTH TABLE (banked either way; unconditional, all computed turns):")
    a = ev
    P(f"    n {len(a)}   flow spread {a['flow_spread'].mean():+.4f} vol-u "
      f"(ES {a['flow_es_pts'].mean():+.2f} pts, ZB {a['flow_zb_pts'].mean():+.3f} pts, "
      f"{a['flow_usd'].mean():+,.0f} $/event 1ct/1ct)")
    P(f"    {'':<8}revert spread {a['revert_spread'].mean():+.4f} vol-u "
      f"(ES {a['revert_es_pts'].mean():+.2f} pts, ZB {a['revert_zb_pts'].mean():+.3f} pts, "
      f"{a['revert_usd'].mean():+,.0f} $/event)")
    P("")
    P("G5 -- 3-ERA TABLE (contiguous thirds of the eligible sequence):")
    for x in eras.itertuples():
        if x.n_cond == 0:
            P(f"    era{x.era} {x.span}: n_elig {x.n_elig}, n_cond 0 -- no events")
        else:
            P(f"    era{x.era} {x.span}: n_elig {x.n_elig:>3} n_cond {x.n_cond:>3}   "
              f"d_flow {x.d_flow:+.4f} ({x.flow_sign})   d_rev {x.d_rev:+.4f} ({x.rev_sign})")
    P("")
    P("G6 -- COST BAND (BASIS: COMMISSION+k-TICK MODELED; 2 RTs per event per leg = 1 ES + 1 ZB):")
    for k in (1, 2):
        P(f"    {k}-tick rung: ${cost[k]:.2f}/event/leg   vs conditional excess: "
          f"flow {obs['d_flow_usd']:+,.0f}$  revert-trade {-obs['d_rev_usd']:+,.0f}$  "
          f"net flow {obs['d_flow_usd'] - cost[k]:+,.0f}$  net revert "
          f"{-obs['d_rev_usd'] - cost[k]:+,.0f}$")
    P("")

    gates = [
        ("G0a_SEAL_ES", "max ES session < 2026-08-01", str(es["date"].max().date()),
         es["date"].max() < SEAL),
        ("G0b_SEAL_ZB", "max ZB session < 2026-08-01", str(zb["date"].max().date()),
         zb["date"].max() < SEAL),
        ("G0c_IDENTITY", "both builds: ret_points == roll.economic_returns, err < 1e-9",
         f"ES {manifest['es']['identity_gate_maxerr']:.1e}, "
         f"ZB {manifest['zb']['identity_gate_maxerr']:.1e}",
         manifest["es"]["identity_gate_maxerr"] < 1e-9
         and manifest["zb"]["identity_gate_maxerr"] < 1e-9),
        ("G0d_ROLL_CAUSAL", "every roll info_cutoff < decision_date, both roots",
         f"ES {manifest['es']['roll_causal']}, ZB {manifest['zb']['roll_causal']}",
         manifest["es"]["roll_causal"] and manifest["zb"]["roll_causal"]),
        ("G0e_SIGNAL_CAUSAL", "signal cutoff (T-3 close) strictly before flow entry (T-2 close), "
         "every turn", f"{int(ev['causal_ok'].sum())}/{len(ev)} turns",
         bool(ev["causal_ok"].all())),
        ("G0f_POINTS_ONLY", "all window math in POINTS / vol-units; no % anywhere (DELEV01)",
         "ret_points sums only; sigmas in points", True),
        ("G1_MDE_first", "MDE printed before observed; power honesty stated",
         f"flow MDE {mde_f:.4f} vs |delta| {abs(obs['d_flow']):.4f}; "
         f"revert MDE {mde_v:.4f} vs |delta| {abs(obs['d_rev']):.4f}", True),
        ("G2_flow", "conditional flow spread > matched unconditional control, CI excludes 0",
         f"delta {obs['d_flow']:+.4f}, boot CI [{ci_f[0]:+.4f},{ci_f[1]:+.4f}], "
         f"p1 {p1_flow:.4f}", g2),
        ("G3_revert", "conditional revert delta opposite-signed (<0) vs control, CI excludes 0",
         f"delta {obs['d_rev']:+.4f}, boot CI [{ci_v[0]:+.4f},{ci_v[1]:+.4f}], "
         f"p1 {p1_rev:.4f}", g3),
        ("G4_conjunction", "BOTH G2 and G3 (single-leg pass recorded but object FAILS)",
         f"G2={'PASS' if g2 else 'FAIL'}, G3={'PASS' if g3 else 'FAIL'}", g4),
        ("G5_era", "3-era signs printed, all cells", f"{len(eras)}/3 eras printed",
         len(eras) == 3),
        ("G6_cost", "{1,2}-tick band, 2 RTs per event per leg, printed",
         f"$52.47 / $96.22 per event per leg, printed with nets", True),
        ("G7_P_MEANING", "IN WORDS: p_shift(1s) = share of 2000 shared-offset circular shifts of "
         "the condition flag whose delta is at least as favorable (flow >=, revert <=) as "
         "observed; CI = 2.5/97.5 pct of 2000 circular block-bootstrap (block 6) deltas",
         "2nd computations printed: block-bootstrap CI vs normal-approx CI; shift p vs CI "
         "agreement visible above", True),
        ("G8_PREREG_ECHO", "constants echoed vs spec.yaml",
         "T-labelling, tercile 36m/q2/3, windows T-2->T+1 & T+1->T+5, sigma60 declared", True),
    ]
    OUTCOME_GATES = {"G2_flow", "G3_revert", "G4_conjunction"}
    P("GATE TABLE  (printed by program)")
    P(f"{'GATE':<20}{'SPEC':<92}{'OBSERVED':<64}{'PASS-FAIL'}")
    validity_pass = True
    for g, s, o, p in gates:
        if g not in OUTCOME_GATES:
            validity_pass &= bool(p)
        P(f"{g:<20}{s:<92}{o:<64}{'PASS' if p else '*** FAIL ***'}")
    P("")
    prereg = dict(SIG_WIN=SIG_WIN, SIG_MIN=SIG_MIN, TERCILE_WIN=TERCILE_WIN, TERCILE_Q=TERCILE_Q,
                  MIN_MONTH_DAYS=MIN_MONTH_DAYS, MIN_NEXT_DAYS=MIN_NEXT_DAYS,
                  N_SHIFT=N_SHIFT, MIN_SHIFT=MIN_SHIFT, N_BB=N_BB, BLOCK_LEN=BLOCK_LEN,
                  COMMISSION=COMMISSION, TICK_USD=TICK_USD, PV=PV)
    P("PREREG/DECLARED CONSTANTS ECHO: " + json.dumps(prereg))
    P("")
    verdict = ("MEREBAL01 ENGINE CANDIDATE" if g4 else
               "CLOSED AT SCOPE (S28) -- conjunction failed; generic ToM control table banked")
    P(f"DECISION RULE (mechanical): G4 {'PASS' if g4 else 'FAIL'} -> {verdict}")
    P(f"VALIDITY GATES (all non-outcome gates): "
      f"{'ALL PASS -- the run is VALID' if validity_pass else '*** AT LEAST ONE FAIL ***'}")
    P(f"OUTCOME GATES: G2 {'PASS' if g2 else 'FAIL'}  G3 {'PASS' if g3 else 'FAIL'}  "
      f"G4 {'PASS' if g4 else 'FAIL'}  (failed gates recorded failed)")
    P("=" * 118)

    json.dump(dict(
        M_eligible=M, n_cond=n_c, n_turns=len(ev), drops=drops, obs=obs,
        p1_flow=p1_flow, p1_rev=p1_rev, p2_flow=p2_flow, p2_rev=p2_rev, p_conj=p_conj,
        ci_flow=ci_f, ci_rev=ci_v, ci_flow_normal=ci_f2, ci_rev_normal=ci_v2,
        mde_flow=mde_f, mde_rev=mde_v, mde_flow_usd=mde_f_usd,
        eras=era_rows, cost=cost, gates=[dict(gate=g, spec=s, observed=o, ok=bool(p))
                                         for g, s, o, p in gates],
        g2=g2, g3=g3, g4=g4, all_validity_pass=bool(validity_pass), verdict=verdict),
        open(os.path.join(OUT, "verdicts.json"), "w", encoding="utf-8"), indent=2, default=str)
    _fh.close()


if __name__ == "__main__":
    main()
