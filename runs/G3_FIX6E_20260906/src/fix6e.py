"""G3_FIX6E_20260906 -- month-end London 4pm fix equity-hedge rebalancing in 6E (ledger G00091).

Spec: runs/G3_FIX6E_20260906/spec.yaml (frozen before results). Family GENESIS3_EVENT.
World-scan card #23 (G3_WORLDSCAN_20260906/out/survivors.json, evi_rank 23).

FROZEN OBJECT (echoed) + operational pins DECLARED HERE BEFORE ANY RESULT EXISTS
--------------------------------------------------------------------------------
Event axis: JOINT ES(x)6E session dates (house pattern, cf. G3_MEREBAL). For month m:
    T   = LAST joint trading day of month m           (the month-end fix day)
    T-1 = 2nd-to-last, T-2 = 3rd-to-last joint day of m
    T+3 = 3rd joint trading day of month m+1
  SIGNAL_m ("MTD ES return through T-2", causal): self-financing ES MTD return in FRACTION
    units = [sum of ES causal-roll daily point returns over (prev-month last joint close ->
    T-2 close)] / [ES RAW held-front close at prev-month last joint day].
    Numerator is basis-free certified transport (POINTS, DELEV01-safe); denominator is the
    TRUE unadjusted price level -- NOT the additively back-adjusted level, so the DELEV01
    cross-era %-distortion cannot enter. Fraction units make the hedge-demand proxy
    cross-era comparable (ES levels moved ~8x over the sample; raw points would not be).
  Y_FIX_m  = 6E return close(T-1) -> close(T), POINTS (self-financing causal-roll sum).
  Y_REV_m  = 6E return close(T)   -> close(T+3), POINTS.
  PRIMARY: OLS slope of Y_FIX on SIGNAL. Mechanism sign (stated in spec BEFORE results):
    strong US equity month -> hedge-rebalance USD selling -> 6E UP  =>  slope > 0.
  REVERSAL: OLS slope of Y_REV on SIGNAL; flow-then-revert signature => slope < 0.

GATE OPERATIONALIZATION (mechanical, declared before results):
  G1  MDE printed FIRST (full sample AND post-2015 era; slope MDE at one-sided alpha 5%,
      power 80%, from OLS SE; also economic units per +1-sd signal).
  G2  slope_fix > 0 AND event-block bootstrap 95% CI excludes 0 (lo > 0).
      ("significant (event-block bootstrap) with the mechanism sign")
  G3  slope_rev < 0 (the frozen clause is SIGN-ONLY: "reversal-leg slope opposite-signed");
      its bootstrap CI is printed for information but is NOT gate-bearing.
  G4  era split AT the 2015 WM/R fix reform. REFORM DATE PIN: 2015-02-15 (the widened
      5-minute calculation window took effect 15 Feb 2015; FSB/BIS reform reports).
      Event era = POST iff fix day T >= 2015-02-15, else PRE.
      "dead if post-2015 slope ~ 0" operationalized: G4 PASS iff slope_post > 0 AND the
      post-era event-block bootstrap 95% CI excludes 0 (lo > 0). Else FAIL (the card kill).
  G5  cost printed: 1-day hold, 1 RT 6E per event; rungs $4.36 + k*$6.25, k in {1,2}
      (BASIS: COMMISSION+k-TICK MODELED; card's "1-2 pips equivalent" ~ 1-2 ticks).
  DECISION RULE (spec verbatim): G2+G3+G4 PASS -> FIX6E01 candidate. Else closed at scope
      (S28); the 6E session-mechanics cell gets its first entry either way.

NULL / CI machinery (house standard, dependence-preserving):
  CIs: circular event-block bootstrap over the month-end event sequence, block=6 events,
    N=2000, (SIGNAL, Y_FIX, Y_REV) rows resampled JOINTLY; CI = 2.5/97.5 pct of slopes.
  2nd computation: classic OLS normal-approx CI printed next to each bootstrap CI.
  Shift null: shared-draw circular shift of the SIGNAL sequence vs the outcome sequence,
    ONE offset per draw applied to BOTH legs (N=2000, min offset 6); one-sided p printed
    as a further second computation (not gate-bearing).
Conditional table (spec): terciles of |SIGNAL| across all computed events (full-sample cut,
  DESCRIPTIVE -- not gate-bearing), top tercile split by sign(SIGNAL), BOTH signs reported,
  WITH the matched unconditional control rows in the same table (house rule).

POINTS ONLY for all 6E outcome math; the signal denominator is a raw unadjusted level
(stated above). Seal asserted < 2026-08-01 on both inputs. Seed 20260906.
Inputs AS-IS (no rebuild): 6E runs/DAILY_6E_EXTRACT_AUTOPSY_20260906/out/6e_daily.parquet;
ES runs/G3_AUCTCYCLE_20260906/out/es_daily.parquet. shas asserted against their manifests.
"""
from __future__ import annotations

import hashlib
import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
RUNS = os.path.dirname(RUN)
OUT = os.path.join(RUN, "out")
SEAL = pd.Timestamp("2026-08-01")
RNG = np.random.default_rng(20260906)

# ---- preregistered / declared constants (echoed in the gate-table footer) ----
REFORM = pd.Timestamp("2015-02-15")   # WM/R 5-min window effective date (pinned above)
MIN_MONTH_DAYS = 15                   # month integrity guard (house standard)
MIN_NEXT_DAYS = 3                     # need T+1..T+3 in month m+1
CLEAN_GAP_MAX = 5                     # joint-axis calendar-gap guard, days
N_BB, BLOCK_LEN = 2000, 6             # event-block bootstrap (circular, months)
N_SHIFT, MIN_SHIFT = 2000, 6          # shared-draw circular-shift null
PV_6E = 125000.0                      # $ per 1.00 point
TICK_6E = 6.25                        # $ per 0.00005 tick
COMMISSION = 4.36                     # NinjaTrader Brokerage Lifetime, $/ct RT (research basis)
Z_ALPHA_1S, Z_POWER = 1.6449, 0.8416  # one-sided 5%, 80% power

ES_PARQ = os.path.join(RUNS, "G3_AUCTCYCLE_20260906", "out", "es_daily.parquet")
E6_PARQ = os.path.join(RUNS, "DAILY_6E_EXTRACT_AUTOPSY_20260906", "out", "6e_daily.parquet")
ES_SHA_EXPECT = "249921cb6d790b8478910fabbc480e0ac82a3d20a206b38fedb34fa1b2054f91"
E6_SHA_EXPECT = "af70be2d857019b932be715feb8d3362233da6f9278f6e75687b121e8aa19eae"

_fh = open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def joint_daily(es, e6):
    """Map each instrument's self-financing daily point returns onto the JOINT date axis.
    r_X[j] = sum of X's own daily returns in (joint[j-1], joint[j]] -- exact additivity,
    roll-safe (interior X-only days are absorbed into the next joint day's return)."""
    dates = np.intersect1d(es["date"].values, e6["date"].values)
    dates = pd.DatetimeIndex(np.sort(dates))
    out = pd.DataFrame(index=dates)
    specs = (("es", es, es["clean_daily"].values.astype(bool)),
             ("e6", e6, np.isfinite(e6["ret_points"].values)))
    for name, df, base_clean in specs:
        d = df.set_index("date")
        vals = d["ret_points"].values
        bucket = dates.searchsorted(d.index.values, side="left")  # smallest joint date >= X date
        ok = bucket < len(dates)
        g = pd.DataFrame({"b": bucket[ok], "r": vals[ok],
                          "clean": base_clean[ok] & np.isfinite(vals[ok])})
        agg = g.groupby("b").agg(r=("r", "sum"), clean=("clean", "all"))
        r = np.full(len(dates), np.nan)
        cl = np.zeros(len(dates), dtype=bool)
        r[agg.index.values] = agg["r"].values
        cl[agg.index.values] = agg["clean"].values
        r[0] = np.nan                                # spans from X's series start; undefined
        cl[0] = False
        out[f"r_{name}"] = r
        out[f"clean_{name}"] = cl
    gap = out.index.to_series().diff().dt.days.fillna(1)
    out["gap_ok"] = (gap <= CLEAN_GAP_MAX).values
    return out


def win_sum(r, clean, a, b):
    """sum of joint-day returns at positions a+1..b (close[a] -> close[b]); NaN unless ALL clean."""
    if a >= b:
        return np.nan
    seg_r, seg_c = r[a + 1:b + 1], clean[a + 1:b + 1]
    if not seg_c.all():
        return np.nan
    return float(seg_r.sum())


def ols_slope(x, y):
    """OLS slope + intercept + classic SE of the slope."""
    n = len(x)
    xm, ym = x.mean(), y.mean()
    sxx = float(np.sum((x - xm) ** 2))
    b = float(np.sum((x - xm) * (y - ym)) / sxx)
    a = ym - b * xm
    resid = y - a - b * x
    s2 = float(np.sum(resid ** 2) / (n - 2))
    se = float(np.sqrt(s2 / sxx))
    return b, a, se


def block_boot_slopes(x, y_fix, y_rev, n_bb, block, rng):
    """Circular event-block bootstrap: (x, y_fix, y_rev) rows resampled JOINTLY."""
    m = len(x)
    nb = int(np.ceil(m / block))
    starts = np.floor(rng.random((n_bb, nb)) * m).astype(int)
    bpos = (starts[:, :, None] + np.arange(block)[None, None, :]) % m
    bpos = bpos.reshape(n_bb, -1)[:, :m]
    bf = np.empty(n_bb)
    bv = np.empty(n_bb)
    for i in range(n_bb):
        sel = bpos[i]
        xs = x[sel]
        if np.std(xs) < 1e-12:
            bf[i] = np.nan
            bv[i] = np.nan
            continue
        bf[i], _, _ = ols_slope(xs, y_fix[sel])
        bv[i], _, _ = ols_slope(xs, y_rev[sel])
    return bf, bv


def main():
    # ---------------- inputs AS-IS, sha-asserted, seal-asserted
    es_sha, e6_sha = sha256(ES_PARQ), sha256(E6_PARQ)
    assert es_sha == ES_SHA_EXPECT, f"ES sha mismatch: {es_sha}"
    assert e6_sha == E6_SHA_EXPECT, f"6E sha mismatch: {e6_sha}"
    es = pd.read_parquet(ES_PARQ)
    e6 = pd.read_parquet(E6_PARQ)
    assert es["date"].max() < SEAL, "SEAL VIOLATION (ES)"
    assert e6["date"].max() < SEAL, "SEAL VIOLATION (6E)"

    auct_manifest = json.load(open(os.path.join(
        RUNS, "G3_AUCTCYCLE_20260906", "out", "inputs_manifest.json"), encoding="utf-8"))
    e6_meta = json.load(open(os.path.join(
        RUNS, "DAILY_6E_EXTRACT_AUTOPSY_20260906", "out", "extract_meta.json"),
        encoding="utf-8"))

    J = joint_daily(es, e6)
    dates = J.index
    r_es, r_e6 = J["r_es"].values, J["r_e6"].values
    cl_es = (J["clean_es"] & J["gap_ok"]).values
    cl_e6 = (J["clean_e6"] & J["gap_ok"]).values
    es_close_raw = es.set_index("date")["close"].reindex(dates).values  # true held-front level

    # ---------------- month-end event construction
    ym = pd.PeriodIndex(dates, freq="M")
    months = sorted(ym.unique())
    pos_by_month = {m: np.where(ym == m)[0] for m in months}
    rows = []
    drops = dict(no_prev_month=0, short_month=0, short_next=0,
                 signal_unclean=0, fix_unclean=0, rev_unclean=0)
    for k in range(1, len(months) - 1):
        m, mn = months[k], months[k + 1]
        if (m - months[k - 1]).n != 1:
            drops["no_prev_month"] += 1
            continue
        if (mn - m).n != 1:
            drops["short_next"] += 1
            continue
        pm, pn = pos_by_month[m], pos_by_month[mn]
        if len(pm) < MIN_MONTH_DAYS:
            drops["short_month"] += 1
            continue
        if len(pn) < MIN_NEXT_DAYS:
            drops["short_next"] += 1
            continue
        i_tm2, i_tm1, i_t = pm[-3], pm[-2], pm[-1]
        i_t3 = pn[2]
        i_prev_eom = pos_by_month[months[k - 1]][-1]
        # signal: ES MTD through T-2 close (from prev month's last joint close), causal
        mtd_es_pts = win_sum(r_es, cl_es, i_prev_eom, i_tm2)
        base = es_close_raw[i_prev_eom]
        if not (np.isfinite(mtd_es_pts) and np.isfinite(base) and base > 0):
            drops["signal_unclean"] += 1
            continue
        signal = mtd_es_pts / base
        y_fix = win_sum(r_e6, cl_e6, i_tm1, i_t)      # close(T-1) -> close(T), points
        if not np.isfinite(y_fix):
            drops["fix_unclean"] += 1
            continue
        y_rev = win_sum(r_e6, cl_e6, i_t, i_t3)       # close(T) -> close(T+3), points
        if not np.isfinite(y_rev):
            drops["rev_unclean"] += 1
            continue
        rows.append(dict(
            month=str(m), d_prev_eom=dates[i_prev_eom], d_tm2=dates[i_tm2],
            d_tm1=dates[i_tm1], d_fix=dates[i_t], d_t3=dates[i_t3],
            n_fix_days=int(i_t - i_tm1), n_rev_days=int(i_t3 - i_t),
            es_base_close=base, mtd_es_pts=mtd_es_pts, signal=signal,
            y_fix_pts=y_fix, y_rev_pts=y_rev,
            y_fix_usd=y_fix * PV_6E, y_rev_usd=y_rev * PV_6E,
            era="POST" if dates[i_t] >= REFORM else "PRE"))
    ev = pd.DataFrame(rows)
    ev["causal_ok"] = (ev["d_tm2"] < ev["d_tm1"]) & (ev["d_tm1"] < ev["d_fix"])
    M = len(ev)
    x = ev["signal"].values
    yf = ev["y_fix_pts"].values
    yv = ev["y_rev_pts"].values
    era_post = (ev["era"] == "POST").values

    # ---------------- observed slopes (full sample + eras)
    b_fix, a_fix, se_fix = ols_slope(x, yf)
    b_rev, a_rev, se_rev = ols_slope(x, yv)
    b_fix_pre, _, se_fix_pre = ols_slope(x[~era_post], yf[~era_post])
    b_fix_post, _, se_fix_post = ols_slope(x[era_post], yf[era_post])
    b_rev_pre, _, _ = ols_slope(x[~era_post], yv[~era_post])
    b_rev_post, _, _ = ols_slope(x[era_post], yv[era_post])

    # ---------------- event-block bootstrap CIs (rows JOINTLY; full sample, then post era)
    bf, bv = block_boot_slopes(x, yf, yv, N_BB, BLOCK_LEN, RNG)
    ci_fix = (float(np.nanpercentile(bf, 2.5)), float(np.nanpercentile(bf, 97.5)))
    ci_rev = (float(np.nanpercentile(bv, 2.5)), float(np.nanpercentile(bv, 97.5)))
    bf_post, bv_post = block_boot_slopes(x[era_post], yf[era_post], yv[era_post],
                                         N_BB, BLOCK_LEN, RNG)
    ci_fix_post = (float(np.nanpercentile(bf_post, 2.5)),
                   float(np.nanpercentile(bf_post, 97.5)))
    ci_rev_post = (float(np.nanpercentile(bv_post, 2.5)),
                   float(np.nanpercentile(bv_post, 97.5)))
    bf_pre, bv_pre = block_boot_slopes(x[~era_post], yf[~era_post], yv[~era_post],
                                       N_BB, BLOCK_LEN, RNG)
    ci_fix_pre = (float(np.nanpercentile(bf_pre, 2.5)), float(np.nanpercentile(bf_pre, 97.5)))
    ci_rev_pre = (float(np.nanpercentile(bv_pre, 2.5)), float(np.nanpercentile(bv_pre, 97.5)))
    # 2nd computation: classic OLS normal-approx CIs
    ci_fix2 = (b_fix - 1.96 * se_fix, b_fix + 1.96 * se_fix)
    ci_rev2 = (b_rev - 1.96 * se_rev, b_rev + 1.96 * se_rev)
    ci_fix_post2 = (b_fix_post - 1.96 * se_fix_post, b_fix_post + 1.96 * se_fix_post)

    # ---------------- shared-draw circular-shift null (ONE offset -> BOTH legs)
    offs = MIN_SHIFT + np.floor(RNG.random(N_SHIFT) * (M - 2 * MIN_SHIFT)).astype(int)
    idx = np.arange(M)
    null_f = np.empty(N_SHIFT)
    null_v = np.empty(N_SHIFT)
    for i, k in enumerate(offs):
        xs = x[(idx - k) % M]
        null_f[i], _, _ = ols_slope(xs, yf)
        null_v[i], _, _ = ols_slope(xs, yv)
    p1_fix = (np.sum(null_f >= b_fix) + 1) / (N_SHIFT + 1)   # one-sided, prereg sign +
    p1_rev = (np.sum(null_v <= b_rev) + 1) / (N_SHIFT + 1)   # one-sided, prereg sign -

    # ---------------- G1 MDE (printed FIRST)
    mde_fix = (Z_ALPHA_1S + Z_POWER) * se_fix
    mde_fix_post = (Z_ALPHA_1S + Z_POWER) * se_fix_post
    sd_x = float(np.std(x, ddof=1))
    sd_x_post = float(np.std(x[era_post], ddof=1))

    # ---------------- conditional table: terciles of |signal| (descriptive, full-sample cut)
    q1, q2 = np.quantile(np.abs(x), [1.0 / 3.0, 2.0 / 3.0])
    terc = np.where(np.abs(x) <= q1, "T1_low", np.where(np.abs(x) <= q2, "T2_mid", "T3_top"))
    ev["abs_terc"] = terc
    ev["sig_sign"] = np.where(x > 0, "pos", np.where(x < 0, "neg", "zero"))
    trows = []

    def cellrow(label, mask):
        n = int(mask.sum())
        if n == 0:
            return dict(cell=label, n=0)
        return dict(
            cell=label, n=n,
            mean_signal=float(np.mean(x[mask])),
            fix_pts=float(np.mean(yf[mask])), fix_usd=float(np.mean(yf[mask]) * PV_6E),
            rev_pts=float(np.mean(yv[mask])), rev_usd=float(np.mean(yv[mask]) * PV_6E),
            fix_pts_sd=float(np.std(yf[mask], ddof=1)) if n > 1 else np.nan)
    trows.append(cellrow("ALL (uncond control)", np.ones(M, dtype=bool)))
    trows.append(cellrow("ALL sig>0", x > 0))
    trows.append(cellrow("ALL sig<0", x < 0))
    for t in ("T1_low", "T2_mid", "T3_top"):
        trows.append(cellrow(f"{t} all", terc == t))
        trows.append(cellrow(f"{t} sig>0", (terc == t) & (x > 0)))
        trows.append(cellrow(f"{t} sig<0", (terc == t) & (x < 0)))
    tt = pd.DataFrame(trows)

    # mechanism-direction P&L (descriptive): long 6E when sig>0, short when sig<0, fix day only
    dir_pnl = np.where(x > 0, yf, -yf)
    top = terc == "T3_top"
    dir_top_usd = float(np.mean(dir_pnl[top]) * PV_6E)
    dir_all_usd = float(np.mean(dir_pnl) * PV_6E)

    # ---------------- G5 cost rungs
    cost = {k: COMMISSION + k * TICK_6E for k in (1, 2)}

    # ---------------- gates (mechanical, exactly as declared in the header)
    g2 = bool(b_fix > 0 and ci_fix[0] > 0)
    g3 = bool(b_rev < 0)
    g4 = bool(b_fix_post > 0 and ci_fix_post[0] > 0)
    candidate = g2 and g3 and g4

    # ---------------- write tables
    ev.to_csv(os.path.join(OUT, "regression.csv"), index=False)
    tt.to_csv(os.path.join(OUT, "tercile_table.csv"), index=False)
    json.dump(dict(
        seal="2026-08-01",
        es=dict(path=os.path.relpath(ES_PARQ, RUNS), sha256=es_sha, rows=int(len(es)),
                span=[str(es['date'].min().date()), str(es['date'].max().date())],
                reused_as_is_from="G3_AUCTCYCLE_20260906",
                identity_gate_maxerr=auct_manifest["ES"]["identity_gate_maxerr"],
                roll_causal=auct_manifest["ES"]["roll_causal"]),
        e6=dict(path=os.path.relpath(E6_PARQ, RUNS), sha256=e6_sha, rows=int(len(e6)),
                span=[str(e6['date'].min().date()), str(e6['date'].max().date())],
                reused_as_is_from="DAILY_6E_EXTRACT_AUTOPSY_20260906",
                identity_vs_certified_s7_maxerr=e6_meta["point_return_reproduction"][
                    "max_abs_err_vs_certified_s7"],
                roll_note=e6_meta["roll_method"][:120]),
    ), open(os.path.join(OUT, "inputs_manifest.json"), "w", encoding="utf-8"), indent=2)

    # ================================================================ PRINTED REPORT
    W = 118
    P("=" * W)
    P("=== G3_FIX6E_20260906 -- month-end London-fix equity-hedge rebalancing in 6E (G00091)")
    P("=" * W)
    P(f"inputs AS-IS: ES {os.path.basename(ES_PARQ)} sha256 {es_sha}")
    P(f"              6E {os.path.basename(E6_PARQ)} sha256 {e6_sha}")
    P(f"joint axis: {len(J):,} sessions {dates.min().date()} -> {dates.max().date()}; "
      f"ES rows {len(es):,}, 6E rows {len(e6):,}")
    P(f"month-end events computed: {M}   drops: {drops}   "
      f"eras: PRE {int((~era_post).sum())} (< {REFORM.date()}) / POST {int(era_post.sum())}")
    P(f"signal: ES MTD self-financing return through T-2 close, FRACTION units "
      f"(points sum / raw prev-EOM close); sd(signal) {sd_x:.4f} "
      f"({sd_x * 100:.2f}% per month); outcome units: 6E POINTS")
    P("")
    P("G1 -- MDE FIRST (one-sided alpha 5%, power 80%; slope units: 6E points per 1.00 = "
      "100% ES MTD):")
    P(f"    full sample : MDE slope {mde_fix:.5f}  (per +1-sd signal event: "
      f"{mde_fix * sd_x:.5f} pts = ${mde_fix * sd_x * PV_6E:,.0f})   n {M}")
    P(f"    post-2015   : MDE slope {mde_fix_post:.5f}  (per +1-sd post signal: "
      f"{mde_fix_post * sd_x_post:.5f} pts = ${mde_fix_post * sd_x_post * PV_6E:,.0f})   "
      f"n {int(era_post.sum())}")
    P(f"    POWER HONESTY: only slopes >= MDE are detectable at 80% power; the era gate G4 "
      f"runs at n {int(era_post.sum())}.")
    P("")
    P("OBSERVED SLOPES (OLS; y = 6E points, x = ES MTD fraction):")
    P(f"    {'leg':<28}{'slope':>10}{'boot 95% CI':>26}{'OLS-normal CI (2nd)':>26}"
      f"{'p_shift(1s)':>12}")
    P(f"    {'FIX  close(T-1)->close(T)':<28}{b_fix:>10.5f}"
      f"{f'[{ci_fix[0]:+.5f},{ci_fix[1]:+.5f}]':>26}"
      f"{f'[{ci_fix2[0]:+.5f},{ci_fix2[1]:+.5f}]':>26}{p1_fix:>12.4f}")
    P(f"    {'REV  close(T)->close(T+3)':<28}{b_rev:>10.5f}"
      f"{f'[{ci_rev[0]:+.5f},{ci_rev[1]:+.5f}]':>26}"
      f"{f'[{ci_rev2[0]:+.5f},{ci_rev2[1]:+.5f}]':>26}{p1_rev:>12.4f}")
    P(f"    economic scale: +1-sd signal ({sd_x * 100:.2f}% ES month) -> fix-day "
      f"{b_fix * sd_x:+.5f} pts = ${b_fix * sd_x * PV_6E:+,.0f}/event")
    P("")
    P("G4 -- ERA SPLIT AT THE 2015 WM/R REFORM (2015-02-15; fix-day date decides era):")
    P(f"    {'era':<10}{'n':>5}{'fix slope':>12}{'boot 95% CI':>26}{'rev slope':>12}"
      f"{'rev boot CI':>26}")
    P(f"    {'PRE':<10}{int((~era_post).sum()):>5}{b_fix_pre:>12.5f}"
      f"{f'[{ci_fix_pre[0]:+.5f},{ci_fix_pre[1]:+.5f}]':>26}{b_rev_pre:>12.5f}"
      f"{f'[{ci_rev_pre[0]:+.5f},{ci_rev_pre[1]:+.5f}]':>26}")
    P(f"    {'POST':<10}{int(era_post.sum()):>5}{b_fix_post:>12.5f}"
      f"{f'[{ci_fix_post[0]:+.5f},{ci_fix_post[1]:+.5f}]':>26}{b_rev_post:>12.5f}"
      f"{f'[{ci_rev_post[0]:+.5f},{ci_rev_post[1]:+.5f}]':>26}")
    P(f"    post-era OLS-normal CI (2nd computation): "
      f"[{ci_fix_post2[0]:+.5f},{ci_fix_post2[1]:+.5f}]")
    P("")
    P("CONDITIONAL TABLE -- |signal| terciles (full-sample cut, DESCRIPTIVE), both signs, "
      "with matched unconditional controls:")
    P(f"    {'cell':<24}{'n':>5}{'mean sig':>10}{'fix pts':>10}{'fix $':>10}{'rev pts':>10}"
      f"{'rev $':>10}")
    for r in tt.itertuples():
        if r.n == 0:
            P(f"    {r.cell:<24}{r.n:>5}{'--':>10}{'--':>10}{'--':>10}{'--':>10}{'--':>10}")
        else:
            P(f"    {r.cell:<24}{r.n:>5}{r.mean_signal:>10.4f}{r.fix_pts:>10.5f}"
              f"{r.fix_usd:>10.0f}{r.rev_pts:>10.5f}{r.rev_usd:>10.0f}")
    P(f"    mechanism-direction fix-day P&L (long 6E if sig>0 else short): "
      f"all ${dir_all_usd:+,.0f}/event   top-|signal| tercile ${dir_top_usd:+,.0f}/event "
      f"(GROSS, descriptive)")
    P("")
    P("G5 -- COST (BASIS: COMMISSION+k-TICK MODELED; 1-day hold, 1 RT 6E per event):")
    for k in (1, 2):
        P(f"    {k}-tick rung: ${cost[k]:.2f}/event   vs top-tercile mechanism-direction "
          f"gross ${dir_top_usd:+,.0f} -> net ${dir_top_usd - cost[k]:+,.0f}")
    P("")

    gates = [
        ("G0a_SEAL_ES", "max ES session < 2026-08-01", str(es["date"].max().date()),
         es["date"].max() < SEAL),
        ("G0b_SEAL_6E", "max 6E session < 2026-08-01", str(e6["date"].max().date()),
         e6["date"].max() < SEAL),
        ("G0c_INPUTS_AS_IS", "sha256 of both parquets == their source manifests "
         "(ES: AUCTCYCLE; 6E: DAILY_6E autopsy)",
         f"ES {es_sha[:12]}.. OK, 6E {e6_sha[:12]}.. OK", True),
        ("G0d_IDENTITY", "certified transports: ES identity-gate maxerr < 1e-9; "
         "6E reproduces certified s7 exactly",
         f"ES {auct_manifest['ES']['identity_gate_maxerr']:.1e}, 6E "
         f"{e6_meta['point_return_reproduction']['max_abs_err_vs_certified_s7']:.1e}",
         auct_manifest["ES"]["identity_gate_maxerr"] < 1e-9
         and e6_meta["point_return_reproduction"]["max_abs_err_vs_certified_s7"] < 1e-9),
        ("G0e_ROLL_CAUSAL", "ES roll causal (manifest); 6E roll = fixed 5-day pre-expiry "
         "(s6-sanctioned, named)", f"ES {auct_manifest['ES']['roll_causal']}, 6E "
         f"{e6_meta['roll_counts']}", bool(auct_manifest["ES"]["roll_causal"])),
        ("G0f_SIGNAL_CAUSAL", "signal cutoff (T-2 close) strictly before fix-leg entry "
         "(T-1 close) strictly before fix day, every event",
         f"{int(ev['causal_ok'].sum())}/{M} events", bool(ev["causal_ok"].all())),
        ("G0g_POINTS", "6E outcome math in POINTS (self-financing sums); signal denominator "
         "= RAW unadjusted ES close, never a back-adjusted level (DELEV01)",
         "ret_points sums; base = held-front close", True),
        ("G1_MDE_first", "printed (full + post-era) before observed",
         f"full {mde_fix:.5f} vs |slope| {abs(b_fix):.5f}; post {mde_fix_post:.5f} vs "
         f"{abs(b_fix_post):.5f}", True),
        ("G2_slope", "fix-day slope > 0 (mechanism sign) AND event-block boot 95% CI "
         "excludes 0", f"slope {b_fix:+.5f}, CI [{ci_fix[0]:+.5f},{ci_fix[1]:+.5f}], "
         f"p_shift {p1_fix:.4f}", g2),
        ("G3_reversal", "reversal-leg slope opposite-signed (< 0); frozen clause is "
         "SIGN-ONLY, CI informational",
         f"slope {b_rev:+.5f}, CI [{ci_rev[0]:+.5f},{ci_rev[1]:+.5f}]", g3),
        ("G4_era_2015", "post-2015 slope > 0 AND post-era boot 95% CI excludes 0 "
         "(dead if ~0)", f"post slope {b_fix_post:+.5f}, CI "
         f"[{ci_fix_post[0]:+.5f},{ci_fix_post[1]:+.5f}]", g4),
        ("G5_cost", "1-day hold cost rungs printed with nets",
         f"${cost[1]:.2f} / ${cost[2]:.2f} per event RT, printed", True),
        ("G6_CI_MEANING", "IN WORDS: boot CI = 2.5/97.5 pct of 2000 circular block-bootstrap "
         "(block 6) OLS slopes, (signal,fix,rev) rows resampled JOINTLY over the month-end "
         "sequence; p_shift = share of 2000 shared-offset circular shifts of the signal "
         "sequence (ONE offset per draw, BOTH legs) with slope at least as favorable "
         "(fix >=, rev <=) as observed",
         "2nd computations printed: OLS-normal CIs next to every boot CI", True),
        ("G7_PREREG_ECHO", "constants echoed vs spec.yaml + header pins",
         "T=last joint day; windows (T-1->T),(T->T+3); signal MTD..T-2; reform 2015-02-15; "
         "block 6; seed 20260906", True),
    ]
    OUTCOME_GATES = {"G2_slope", "G3_reversal", "G4_era_2015"}
    P("GATE TABLE  (printed by program)")
    P(f"{'GATE':<20}{'SPEC':<92}{'OBSERVED':<64}{'PASS-FAIL'}")
    validity_pass = True
    for g, s, o, p in gates:
        if g not in OUTCOME_GATES:
            validity_pass &= bool(p)
        P(f"{g:<20}{s:<92}{o:<64}{'PASS' if p else '*** FAIL ***'}")
    P("")
    prereg = dict(REFORM=str(REFORM.date()), MIN_MONTH_DAYS=MIN_MONTH_DAYS,
                  MIN_NEXT_DAYS=MIN_NEXT_DAYS, CLEAN_GAP_MAX=CLEAN_GAP_MAX, N_BB=N_BB,
                  BLOCK_LEN=BLOCK_LEN, N_SHIFT=N_SHIFT, MIN_SHIFT=MIN_SHIFT, PV_6E=PV_6E,
                  TICK_6E=TICK_6E, COMMISSION=COMMISSION, SEED=20260906)
    P("PREREG/DECLARED CONSTANTS ECHO: " + json.dumps(prereg))
    P("")
    verdict = ("FIX6E01 ENGINE CANDIDATE" if candidate else
               "CLOSED AT SCOPE (S28) -- 6E session-mechanics cell gets its first entry")
    P(f"DECISION RULE (mechanical, spec verbatim): G2 {'PASS' if g2 else 'FAIL'} + "
      f"G3 {'PASS' if g3 else 'FAIL'} + G4 {'PASS' if g4 else 'FAIL'} -> {verdict}")
    P(f"VALIDITY GATES (all non-outcome gates): "
      f"{'ALL PASS -- the run is VALID' if validity_pass else '*** AT LEAST ONE FAIL ***'}")
    P(f"OUTCOME GATES: G2 {'PASS' if g2 else 'FAIL'}  G3 {'PASS' if g3 else 'FAIL'}  "
      f"G4 {'PASS' if g4 else 'FAIL'}  (failed gates recorded failed)")
    P("=" * W)

    json.dump(dict(
        n_events=M, drops=drops, n_pre=int((~era_post).sum()), n_post=int(era_post.sum()),
        slope_fix=b_fix, slope_rev=b_rev, ci_fix=ci_fix, ci_rev=ci_rev,
        ci_fix_normal=ci_fix2, ci_rev_normal=ci_rev2,
        slope_fix_pre=b_fix_pre, slope_fix_post=b_fix_post,
        slope_rev_pre=b_rev_pre, slope_rev_post=b_rev_post,
        ci_fix_pre=ci_fix_pre, ci_fix_post=ci_fix_post,
        ci_rev_pre=ci_rev_pre, ci_rev_post=ci_rev_post, ci_fix_post_normal=ci_fix_post2,
        p1_fix=p1_fix, p1_rev=p1_rev, mde_fix=mde_fix, mde_fix_post=mde_fix_post,
        sd_signal=sd_x, sd_signal_post=sd_x_post,
        dir_all_usd=dir_all_usd, dir_top_usd=dir_top_usd, cost=cost,
        gates=[dict(gate=g, spec=s, observed=o, ok=bool(p)) for g, s, o, p in gates],
        g2=g2, g3=g3, g4=g4, candidate=candidate,
        all_validity_pass=bool(validity_pass), verdict=verdict,
        es_sha256=es_sha, e6_sha256=e6_sha),
        open(os.path.join(OUT, "verdicts.json"), "w", encoding="utf-8"), indent=2,
        default=str)
    _fh.close()


if __name__ == "__main__":
    main()
