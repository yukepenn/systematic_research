"""test_primary_objective_v2.py — self-test for src/analytics/primary_objective_v2.py.

Runs under plain `python` (no pytest). Prints PASS/FAIL per case and exits non-zero on any
failure.

    python src/analytics/test_primary_objective_v2.py

EVERY fixture in this file is SYNTHETIC (fabricated P&L with a fixed seed). No candidate's
daily or intraday P&L is loaded and no strategy is scored here — that is a separate, later,
separately pre-registered pass (O2).

The load-bearing cases:

  D0    v2's bootstrap generators ARE v1's objects, so v1's cases 3 and 4 (byte-exact
        reproduction of the committed capital map and of the published C-P3 disclosure)
        carry over to v2 without a copy that could drift.
  D1-*  pin the aggregation rule: ONE rule (equal-weight mixture), applied to BOTH terms.
        These fail if anyone reverts P_ruin to `max` or CE_g to anything else.
  D4-*  pin the lambda convention: derived, compounded g_ref in fixed_fraction mode, and the
        forfeited horizon is (H_f - H) not (H_f - H/2).
  D9-*  REGRESSION tests for the min_unit path. D9-2 fails on v1's arithmetic. D9-3/D9-4
        fail if the de-sizing trap is ever again allowed to report a finite J silently.
"""
from __future__ import annotations

import math
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import primary_objective as PO1        # noqa: E402  (v1, for regression comparison only)
import primary_objective_v2 as PO      # noqa: E402

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  --  {detail}" if detail else ""))


# --------------------------------------------------------------------------------------
# SYNTHETIC fixtures  (no real series anywhere in this file)
# --------------------------------------------------------------------------------------
def synth_regime_daily(n=1100, seed=11):
    """Fabricated daily $ P&L with REGIME PERSISTENCE, so that block length matters.

    An iid fixture would make moving5 / moving20 / stationary60 agree, and then the D1 cases
    could not tell a mixture from a max. A two-state Markov drift with mean run length 40
    sessions gives the three methods materially different ruin probabilities.
    """
    rng = np.random.default_rng(seed)
    state = 1
    mu = np.empty(n)
    for i in range(n):
        if rng.random() < 1.0 / 40.0:
            state = 1 - state
        mu[i] = 260.0 if state else -170.0
    x = mu + rng.normal(0.0, 1150.0, size=n)
    idx = pd.bdate_range("2022-01-03", periods=n)
    return pd.Series(x, index=idx)


def synth_iid_daily(n=1100, seed=5, mu=80.0, sd=1400.0):
    rng = np.random.default_rng(seed)
    return pd.Series(rng.normal(mu, sd, size=n), index=pd.bdate_range("2022-01-03", periods=n))


DAILY = synth_regime_daily()
NB = 400


# ======================================================================================
# D0 — inherited machinery
# ======================================================================================
def case_D0_generators_are_v1s():
    same = (PO.make_indices is PO1.make_indices and
            PO.parse_method is PO1.parse_method and
            PO._path_stats is PO1._path_stats and
            PO._intraday_path_stats is PO1._intraday_path_stats and
            PO.build_session_logpath is PO1.build_session_logpath and
            PO.reproduce_capital_map is PO1.reproduce_capital_map and
            PO.reproduce_cp3 is PO1.reproduce_cp3)
    check("D0 v2's generators/path machinery ARE v1's objects (cases 3+4 inherited)", same)


# ======================================================================================
# D1 — the aggregation rule
# ======================================================================================
def case_D1_1_pooled_identity(r):
    a = r["aggregation"]
    ms = PO.DEFAULT_METHODS
    ce_mean = float(np.mean([r["growth"]["per_method"][m]["g_ann_mean"] for m in ms]))
    pr_mean = float(np.mean([r["ruin"]["daily_close"][m] for m in ms]))
    j_mean = float(np.mean([a["J_by_method"][m] for m in ms]))
    ok = (abs(a["ce_log_growth_ann"] - ce_mean) < 1e-12 and
          abs(a["p_ruin"] - pr_mean) < 1e-12 and
          abs(a["J"] - j_mean) < 1e-12)
    check("D1-1 mixture == pooled sample == mean over methods, for BOTH terms and for J", ok,
          f"CE_g {a['ce_log_growth_ann']:.9f} vs {ce_mean:.9f}; "
          f"P_ruin {a['p_ruin']:.9f} vs {pr_mean:.9f}")


def case_D1_2_not_max(r):
    ms = PO.DEFAULT_METHODS
    per = [r["ruin"]["daily_close"][m] for m in ms]
    spread = max(per) - min(per)
    ok_fixture = spread > 0.02          # fixture must discriminate, else the test is vacuous
    ok = (ok_fixture and
          r["primary"]["p_ruin"] < max(per) - 1e-9 and
          r["primary"]["p_ruin"] > min(per) + 1e-9)
    check("D1-2 headline P_ruin is the MIXTURE, strictly inside the band (not v1's max)", ok,
          f"per-method {['%.4f' % p for p in per]}, headline {r['primary']['p_ruin']:.4f}, "
          f"spread {spread:.4f}" + ("" if ok_fixture else "  [FIXTURE NOT DISCRIMINATING]"))


def case_D1_3_worst_reported(r):
    a = r["aggregation"]
    jm = a["J_by_method"]
    ok = (abs(a["J_worst"] - min(jm.values())) < 1e-12 and
          a["J_worst_method"] == min(jm, key=jm.get) and
          abs(a["J_best"] - max(jm.values())) < 1e-12)
    signs = {np.sign(a["J"]), np.sign(a["J_worst"]), np.sign(a["J_best"])}
    signs.discard(0.0)
    ok = ok and (a["model_determined_sign"] == (len(signs) > 1))
    check("D1-3 J_worst == min_m J_m (Gamma-minimax companion) and the sign flag is correct",
          ok, f"J {a['J']:+.4f}; per-method " +
          ", ".join(f"{m} {v:+.4f}" for m, v in jm.items()))


def case_D1_4_no_cross_method_mixing(r):
    """The specific v1 defect: growth read off one aggregate, ruin off another."""
    ms = PO.DEFAULT_METHODS
    per_ruin = [r["ruin"]["daily_close"][m] for m in ms]
    lam = r["primary"]["lambda_ruin_per_yr"]
    v1_style = r["primary"]["ce_log_growth_ann"] - lam * max(per_ruin)
    ok = abs(r["primary"]["objective_J"] - v1_style) > 1e-6
    check("D1-4 J is NOT v1's mean-growth-minus-max-ruin hybrid", ok,
          f"v2 J {r['primary']['objective_J']:+.6f} vs v1-style {v1_style:+.6f}")


def case_D1_5_lambda_grid_consistent(r):
    lam = r["primary"]["lambda_ruin_per_yr"]
    got = r["primary"]["objective_J_by_lambda"][str(lam)]
    ok = abs(got - r["primary"]["objective_J"]) < 1e-12
    check("D1-5 the lambda grid contains the calibrated lambda and reproduces J there", ok)


# ======================================================================================
# D4 — the lambda convention
# ======================================================================================
def case_D4_1_derivation():
    lam_ff = PO.franchise_lambda(504, "fixed_fraction")
    lam_fc = PO.franchise_lambda(504, "fixed_contracts")
    expect_ff = (10.0 - 2.0) / 2.0 * PO.G_REF_COMPOUNDED
    expect_fc = (10.0 - 2.0) / 2.0 * PO.G_REF_NONCOMPOUNDED
    ok = (abs(lam_ff - expect_ff) < 1e-12 and abs(lam_fc - expect_fc) < 1e-12 and
          abs(PO.franchise_lambda(2520, "fixed_fraction")) < 1e-12)
    check("D4-1 lambda = (H_f - H)/H * g_ref, and is 0 when H >= H_f", ok,
          f"ff {lam_ff:.6f}, fc {lam_fc:.6f}")


def case_D4_2_convention_matters():
    lam_ff = PO.franchise_lambda(504, "fixed_fraction")
    lam_fc = PO.franchise_lambda(504, "fixed_contracts")
    ratio = lam_ff / lam_fc
    ok = (abs(ratio - PO.G_REF_COMPOUNDED / PO.G_REF_NONCOMPOUNDED) < 1e-12 and
          ratio > 1.4)
    check("D4-2 compounded and non-compounded g_ref give DIFFERENT lambdas (the D4 bug)", ok,
          f"lambda_ff / lambda_fc = {ratio:.4f} "
          f"(g_ref {PO.G_REF_COMPOUNDED:.6f} vs {PO.G_REF_NONCOMPOUNDED:.6f})")


def case_D4_3_no_double_count():
    """lambda*H/g_ref must equal (H_f - H), not (H_f - H/2)."""
    H = 2.0
    lam = PO.franchise_lambda(504, "fixed_fraction")
    implied = lam * H / PO.G_REF_COMPOUNDED
    ok = abs(implied - 8.0) < 1e-12 and abs(implied - 9.0) > 0.5
    check("D4-3 forfeited horizon is (H_f - H) = 8 yr, not v1's (H_f - H/2) = 9 yr", ok,
          f"implied forfeited years = {implied:.6f}")


def case_D4_4_module_default(r):
    lam = r["primary"]["lambda_ruin_per_yr"]
    ok = (r["spec"]["lambda_source"] == "derived" and
          abs(lam - PO.franchise_lambda(504, "fixed_fraction")) < 1e-12 and
          abs(lam - 1.0) > 0.3 and
          r["spec"]["lambda_g_ref_convention"].startswith("compounded"))
    check("D4-4 the module DERIVES lambda (not v1's hard-coded 1.0) in the right convention",
          ok, f"lambda = {lam:.6f}, v1 = 1.0")


def case_D4_5_mode_switches_convention():
    r = PO.primary_objective(DAILY, n_boot=120, leverage_mode="fixed_contracts")
    lam = r["primary"]["lambda_ruin_per_yr"]
    ok = (abs(lam - PO.franchise_lambda(504, "fixed_contracts")) < 1e-12 and
          r["spec"]["lambda_g_ref_convention"].startswith("non-compounded"))
    check("D4-5 fixed_contracts mode uses the NON-compounded g_ref (its own CE_g convention)",
          ok, f"lambda = {lam:.6f}")


def case_D4_6_horizon_rescales():
    a = PO.franchise_lambda(252, "fixed_fraction")     # H = 1 yr
    b = PO.franchise_lambda(504, "fixed_fraction")     # H = 2 yr
    ok = abs(a - 9.0 * PO.G_REF_COMPOUNDED) < 1e-12 and abs(b - 8.0 / 2 * PO.G_REF_COMPOUNDED) < 1e-12
    check("D4-6 lambda tracks the evaluation horizon (v1's constant did not)", ok,
          f"H=1yr -> {a:.4f}, H=2yr -> {b:.4f}")


# ======================================================================================
# D9 — the min_unit path (REGRESSION)
# ======================================================================================
def case_D9_1_floor_to_multiple():
    cases = [(0.3, 0.1), (0.29, 0.01), (2.4, 0.4), (0.7, 0.1), (1.0, 1.0), (7.0, 0.7)]
    ok, detail = True, []
    for x, m in cases:
        v2 = float(PO.floor_to_multiple(x, m))
        naive = float(np.floor(x / m) * m)                      # v1's arithmetic
        if abs(v2 - x) > 1e-9:
            ok = False
        detail.append(f"{x}/{m}: v2 {v2:.6g}, v1 {naive:.6g}")
    # and the regression must actually bite somewhere, else this test proves nothing
    bit = any(abs(np.floor(x / m) * m - x) > 1e-9 for x, m in cases)
    check("D9-1 floor_to_multiple is exact on exact multiples (v1's floor is not)",
          ok and bit, "; ".join(detail))


def case_D9_2_end_to_end_fp():
    """capital=1.0 makes the target size exactly the float literal 0.3; v1 rounds it to 0.2."""
    paths = np.array([[0.01]])
    st2 = PO.fixed_fraction_rounded_stats(paths, 1.0, 0.3, 0.25, 1, True, 0.95, 0.1)
    st1 = PO1._fixed_fraction_rounded_stats(paths, 1.0, 0.3, 0.25, 1, True, 0.95, 0.1)
    eq2 = math.exp(float(st2["terminal_log_wealth"][0]))
    eq1 = math.exp(float(st1["terminal_log_wealth"][0]))
    ok = abs(eq2 - 1.003) < 1e-12 and abs(eq1 - 1.002) < 1e-12
    check("D9-2 REGRESSION: a 0.3-unit target at min_unit 0.1 sizes 0.3 (v1 sized 0.2)", ok,
          f"v2 equity {eq2:.6f} (want 1.003), v1 equity {eq1:.6f}")


def case_D9_3_degeneracy_flagged():
    s = synth_iid_daily()
    r = PO.primary_objective(s, n_boot=200, min_unit=1.0)
    g = r["granularity"]
    warned = any("MIN_UNIT DEGENERATE" in w for w in r["integrity"]["warnings"])
    ok = (g["worst_p_desized_to_zero"] > 0.5 and
          g["degenerate"] is True and
          r["primary"]["objective_J_is_degenerate"] is True and
          math.isnan(r["primary"]["objective_J"]) and
          np.isfinite(r["primary"]["objective_J_before_degeneracy_nan"]) and
          warned)
    check("D9-3 REGRESSION: de-sizing trap is detected, warned, and J is NaN'd", ok,
          f"{g['worst_p_desized_to_zero']:.1%} of paths freeze; "
          f"J_before_nan {r['primary']['objective_J_before_degeneracy_nan']:+.4f}")
    return r


def case_D9_4_trap_cannot_masquerade(r_gran):
    """The exact v1 pathology: granularity makes P_ruin FALL. Pinned so it cannot pass silently."""
    s = synth_iid_daily()
    r_cont = PO.primary_objective(s, n_boot=200)
    ok = (r_gran["primary"]["p_ruin"] < r_cont["primary"]["p_ruin"] - 0.05 and
          r_gran["granularity"]["degenerate"] is True)
    check("D9-4 REGRESSION: granular P_ruin collapses below continuous, and IS flagged", ok,
          f"granular {r_gran['primary']['p_ruin']:.4f} vs continuous "
          f"{r_cont['primary']['p_ruin']:.4f}")


def case_D9_5_fine_granularity_converges():
    s = synth_iid_daily()
    a = PO.primary_objective(s, n_boot=200, min_unit=0.001)
    b = PO.primary_objective(s, n_boot=200)
    ok = (a["granularity"]["degenerate"] is False and
          np.isfinite(a["primary"]["objective_J"]) and
          abs(a["primary"]["objective_J"] - b["primary"]["objective_J"]) < 0.02)
    check("D9-5 fine granularity (min_unit=0.001) converges to the continuous model", ok,
          f"J granular {a['primary']['objective_J']:+.4f} vs continuous "
          f"{b['primary']['objective_J']:+.4f}, "
          f"p_desized {a['granularity']['worst_p_desized_to_zero']:.3f}")


def case_D9_6_no_position_reversal():
    """Negative equity must give ZERO size, not a reversed position (v1 reversed)."""
    paths = np.array([[-2_000_000.0, 1_000_000.0, 1_000_000.0]])
    st2 = PO.fixed_fraction_rounded_stats(paths, 100_000.0, 1.0, 0.25, 3, False, 0.95, 0.1)
    eq2 = float(st2["terminal_equity"][0])
    # v2: step 0 sizes 1.0 unit -> equity -1,900,000; steps 1-2 target -19 units, clamped to
    # ZERO, so equity is frozen. v1 sized -19.0 and traded a reversed position into
    # -20,900,000. Both are floored at _EPS*capital in log space, which is exactly why v1's
    # bug was invisible: only the unclipped equity shows it.
    ok = (st2["granularity"]["n_negative_unit_steps"] == 2 and
          abs(eq2 + 1_900_000.0) < 1e-6 and
          st2["granularity"]["p_equity_nonpositive"] == 1.0)
    check("D9-6 REGRESSION: negative equity -> zero size (frozen), never a reversed position",
          ok, f"terminal equity {eq2:,.0f} (want -1,900,000; v1's reversal gives "
              f"-20,900,000), negative-target steps "
              f"{st2['granularity']['n_negative_unit_steps']}")


def case_D9_7_bankruptcy_from_the_right_model():
    """v1 reported p_equity_nonpositive from the CONTINUOUS clip test even in min_unit mode."""
    s = synth_iid_daily()
    r = PO.primary_objective(s, n_boot=120, min_unit=1.0)
    per = r["ruin"]["p_equity_nonpositive"]["per_method"]
    gran = r["granularity"]["per_method"]
    ok = all(abs(per[m] - gran[m]["p_equity_nonpositive"]) < 1e-12 for m in PO.DEFAULT_METHODS)
    check("D9-7 min_unit mode reports bankruptcy from the STEPPED granular equity", ok)


# ======================================================================================
# D10 — the locked-forward / date guards
# ======================================================================================
def case_D10_1_bare_array_is_undated():
    s, flags = PO.load_daily_pnl(np.array([100.0, -50.0, 25.0]))
    s1, flags1 = PO1.load_daily_pnl(np.array([100.0, -50.0, 25.0]))
    ok = (flags["dated"] is False and any("no usable date index" in w for w in flags["warnings"])
          and flags1["dated"] is True)     # documents the v1 behaviour being repaired
    check("D10-1 bare array is correctly UNDATED and warned (v1 claimed dated=True)", ok,
          f"v2 dated={flags['dated']}, v1 dated={flags1['dated']}")


def case_D10_2_integer_dates_raise():
    df = pd.DataFrame({"d": [20230103, 20230104, 20230105], "pnl": [1.0, 2.0, 3.0]})
    try:
        PO.load_daily_pnl(df, date_col="d", pnl_col="pnl")
        check("D10-2 integer YYYYMMDD date column raises instead of parsing to 1970", False,
              "no exception")
    except ValueError as e:
        check("D10-2 integer YYYYMMDD date column raises instead of parsing to 1970",
              "pre-1990" in str(e), str(e)[:70])


def case_D10_3_locked_forward_guard():
    s = pd.Series([1.0, 2.0, 3.0],
                  index=pd.to_datetime(["2026-07-30", "2026-07-31", "2026-08-05"]))
    try:
        PO.load_daily_pnl(s)
        check("D10-3 LOCKED_FORWARD guard raises on data >= 2026-08-01", False, "no exception")
    except ValueError as e:
        check("D10-3 LOCKED_FORWARD guard raises on data >= 2026-08-01",
              "LOCKED-FORWARD" in str(e), str(e)[:70])


def case_D10_4_dev_truncation():
    s = pd.Series(np.full(60, 100.0), index=pd.bdate_range("2026-05-01", periods=60))
    got, flags = PO.load_daily_pnl(s)
    ok = got.index.max() <= PO.DEV_END and flags["n_truncated_post_dev"] > 0
    check("D10-4 post-dev sessions truncated and recorded", ok,
          f"kept {len(got)}, dropped {flags['n_truncated_post_dev']}")


# ======================================================================================
# invariants carried over from v1's suite (synthetic fixtures)
# ======================================================================================
def case_M1_determinism():
    a = PO.primary_objective(DAILY, n_boot=150, seed=PO.SEED)
    b = PO.primary_objective(DAILY, n_boot=150, seed=PO.SEED)
    ok = (a["primary"]["objective_J"] == b["primary"]["objective_J"] and
          a["primary"]["p_ruin"] == b["primary"]["p_ruin"])
    check("M1 determinism: same seed -> bit-identical J / P_ruin", ok,
          f"J={a['primary']['objective_J']:.6f}")


def case_M2_analytic_constant():
    n = 1000
    s = pd.Series(np.full(n, 500.0), index=pd.bdate_range("2022-01-03", periods=n))
    r = PO.primary_objective(s, capital=100_000.0, leverage=1.0, n_boot=100)
    expect = math.log1p(500.0 / 100_000.0) * PO.ANN
    ok = (abs(r["primary"]["ce_log_growth_ann"] - expect) < 1e-12 and
          r["primary"]["p_ruin"] == 0.0 and
          abs(r["primary"]["objective_J"] - expect) < 1e-12)
    check("M2 analytic: constant +$500/day -> CE_g = 252*log1p(0.005), P_ruin = 0, J = CE_g",
          ok, f"CE_g={r['primary']['ce_log_growth_ann']:.9f} expected={expect:.9f}")


def case_M3_zero_leverage():
    r = PO.primary_objective(DAILY, leverage=0.0, n_boot=100)
    ok = (r["primary"]["ce_log_growth_ann"] == 0.0 and r["primary"]["p_ruin"] == 0.0 and
          r["primary"]["objective_J"] == 0.0)
    check("M3 leverage 0 -> zero growth, zero ruin, J = 0", ok)


def case_M4_ruin_monotone():
    ps = [PO.primary_objective(DAILY, leverage=L, n_boot=200)["primary"]["p_ruin"]
          for L in (0.25, 0.5, 1.0, 2.0)]
    ok = all(ps[i] <= ps[i + 1] + 1e-12 for i in range(len(ps) - 1))
    check("M4 mixture P_ruin is non-decreasing in leverage", ok,
          " -> ".join(f"{p:.3f}" for p in ps))


def case_M5_absorbing_identity():
    r = PO.primary_objective(DAILY, leverage=0.02, n_boot=150)
    g = r["growth"]["per_method"][PO.DEFAULT_METHODS[0]]
    ok = (r["primary"]["p_ruin"] == 0.0 and
          abs(g["g_ann_mean"] - g["g_ann_nonabsorbing_mean"]) < 1e-12)
    check("M5 no ruin -> absorbing growth == non-absorbing growth", ok)


def case_M6_mc_se_scales():
    a = PO.primary_objective(DAILY, n_boot=250)["primary"][
        "monte_carlo_se_NOT_a_CI_on_the_process"]
    b = PO.primary_objective(DAILY, n_boot=1000)["primary"][
        "monte_carlo_se_NOT_a_CI_on_the_process"]
    ratio = b / a
    ok = a > 0 and 0.3 < ratio < 0.8
    check("M6 Monte-Carlo se is reported and scales ~1/sqrt(n_boot)", ok,
          f"se(250)={a:.5f}, se(1000)={b:.5f}, ratio {ratio:.3f} (expect ~0.5)")


def case_M7_ruin_time_reported(r):
    v = r["ruin"]["mean_first_ruin_years_given_ruin"]
    ok = v is None or (0.0 < v <= 2.0 + 1e-9)
    check("M7 mean time-to-ruin is measured (the quantity v1's lambda merely assumed)", ok,
          f"{v:.3f} yr (v1 section 1.5 assumed 1.00 yr)" if v is not None else "no ruin")


def case_M8_fixed_contracts_runs():
    r = PO.primary_objective(DAILY, n_boot=150, leverage_mode="fixed_contracts")
    ok = np.isfinite(r["primary"]["objective_J"]) and 0.0 <= r["primary"]["p_ruin"] <= 1.0
    check("M8 fixed_contracts mode runs and returns a finite J", ok,
          f"J={r['primary']['objective_J']:.4f}")


def case_M9_scale_invariance():
    a = PO.primary_objective(DAILY, capital=100_000.0, leverage=0.5, n_boot=200)
    b = PO.primary_objective(DAILY, capital=200_000.0, leverage=1.0, n_boot=200)
    ok = abs(a["primary"]["objective_J"] - b["primary"]["objective_J"]) < 1e-9
    check("M9 fixed_fraction depends on L and C only through L/C", ok,
          f"{a['primary']['objective_J']:.9f} vs {b['primary']['objective_J']:.9f}")


def main():
    t0 = time.time()
    print("primary_objective_v2 self-test  (ALL FIXTURES SYNTHETIC)\n" + "-" * 78)
    print(f"fixture: fabricated regime-switching daily P&L, n={len(DAILY)}, "
          f"{DAILY.index.min().date()} .. {DAILY.index.max().date()}, "
          f"net ${DAILY.sum():,.0f} (NOT a strategy)")
    print(f"lambda (fixed_fraction, H=504) = {PO.DEFAULT_LAMBDA_FIXED_FRACTION:.6f}   "
          f"(v1 used 1.0)")
    print("-" * 78)

    r = PO.primary_objective(DAILY, n_boot=NB, label="synthetic")

    case_D0_generators_are_v1s()
    case_D1_1_pooled_identity(r)
    case_D1_2_not_max(r)
    case_D1_3_worst_reported(r)
    case_D1_4_no_cross_method_mixing(r)
    case_D1_5_lambda_grid_consistent(r)
    case_D4_1_derivation()
    case_D4_2_convention_matters()
    case_D4_3_no_double_count()
    case_D4_4_module_default(r)
    case_D4_5_mode_switches_convention()
    case_D4_6_horizon_rescales()
    case_D9_1_floor_to_multiple()
    case_D9_2_end_to_end_fp()
    rg = case_D9_3_degeneracy_flagged()
    case_D9_4_trap_cannot_masquerade(rg)
    case_D9_5_fine_granularity_converges()
    case_D9_6_no_position_reversal()
    case_D9_7_bankruptcy_from_the_right_model()
    case_D10_1_bare_array_is_undated()
    case_D10_2_integer_dates_raise()
    case_D10_3_locked_forward_guard()
    case_D10_4_dev_truncation()
    case_M1_determinism()
    case_M2_analytic_constant()
    case_M3_zero_leverage()
    case_M4_ruin_monotone()
    case_M5_absorbing_identity()
    case_M6_mc_se_scales()
    case_M7_ruin_time_reported(r)
    case_M8_fixed_contracts_runs()
    case_M9_scale_invariance()

    n_fail = sum(1 for _, ok in RESULTS if not ok)
    print("-" * 78)
    print(f"{len(RESULTS) - n_fail}/{len(RESULTS)} PASS   ({time.time() - t0:.1f}s)")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
