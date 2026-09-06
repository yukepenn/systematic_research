"""
G2_F11_MC54LEG2_VOLFORECAST_20260906  --  MC-54 leg 2: frozen-profile OOS vol forecast.

Preregistered test (spec.yaml committed before results). Implements EXACTLY:
  - NQ 1-min RTH RV; diurnal profile (mean squared 1-min log return by minute-of-session)
    FROZEN on TRAIN 2022-06-01..2024-12-31, never refit on TEST.
  - Nested HAC(lag5) OLS on TEST 2025-01-01..2026-05-29:
      RAW : rest_of_day_logRV ~ 1 + prior_day_logRV + raw_early
      FULL: RAW + deseason_early
  - Headline: HAC t of deseason_early + OOS incremental adjusted-R2 with stationary
    block-bootstrap CI (mean block 10 sessions, 2000 draws, seed 20260906).
  - G2: MDE (80% power) printed BEFORE the observed incremental value (barrier line).
  - G5: corr(raw_early, deseason_early) + VIF; VIF > 10 => NOT-IDENTIFIED.
  - G0: hard assert min date >= 2022-06-01, max <= 2026-05-29 in every computation.

Implementation choices recorded BEFORE any OOS read (per spec definitions):
  - Diurnal profile is NOT smoothed (raw per-minute mean of squared returns, 390 keys).
  - Bars are END-stamped (CLAUDE.md section 6): RTH = stamps (09:30, 16:00] ET, 390 bars.
    First hour "09:30-10:29 trading time" = end-stamps 09:31..10:30 (60 bars).
    Rest-of-day "10:30-16:00" = end-stamps 10:31..16:00 (330 bars).
  - 1-min log return: first available RTH bar of a session uses its own open->close
    log return (no overnight contamination); every later bar uses close-to-close from
    the previous available RTH bar of the same session.
  - Session completeness filter (fixed before results): >= 54/60 first-hour bars AND
    >= 297/330 rest-of-day bars (90%); sessions failing are dropped and counted.
  - Sessions with zero RV in any used window are dropped (log undefined); counted.
  - prior_day_logRV = log full-day RTH RV (09:30-16:00) of the immediately preceding
    retained session in the admissible era (>= 2022-06-01); TEST rows may lag off the
    last TRAIN-era sessions (still inside the era; G0 asserts over every date used).
  - HAC = Newey-West maxlags 5, z-based p-values (statsmodels default use_t=False).
  - MDE at 80% power, alpha 0.05 two-sided, single added regressor:
      lambda = (z_{0.975}+z_{0.80})^2 = 7.8489;  f2_min = lambda / N_test
      dR2_min = f2_min * (1 - R2_raw) / (1 + f2_min)
      expressed in adjusted units: MDE_adj = adjR2(R2_raw + dR2_min, N, k=3)
                                           - adjR2(R2_raw, N, k=2).
    Uses only N and the RAW (incumbent) model -- nothing from the FULL model.
  - Stationary block bootstrap: circular, geometric block lengths mean 10, resamples
    TEST rows; per draw refit both models by OLS and record dAdjR2 and beta_deseason;
    95% percentile CI, two-sided. rng = np.random.default_rng(20260906).
"""

import sys
import io
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

SEED = 20260906
RUN_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = RUN_DIR / "out"
DATA = (RUN_DIR.parents[1] / "research" / "scalping_lab" / "substrate" / "minute"
        / "NQ" / "nq1m_2005_202605.parquet")

ERA_MIN = pd.Timestamp("2022-06-01")
DEV_END = pd.Timestamp("2026-05-29 23:59:59")
TRAIN_LO, TRAIN_HI = pd.Timestamp("2022-06-01"), pd.Timestamp("2024-12-31")
TEST_LO, TEST_HI = pd.Timestamp("2025-01-01"), pd.Timestamp("2026-05-29")

T_0930 = pd.Timestamp("09:30").time()
T_1030 = pd.Timestamp("10:30").time()
T_1600 = pd.Timestamp("16:00").time()

Z_ALPHA = 1.959963984540054   # z_{0.975}
Z_POWER = 0.8416212335729143  # z_{0.80}


def adj_r2(r2, n, k):
    return 1.0 - (1.0 - r2) * (n - 1) / (n - k - 1)


def load_sessions():
    df = pd.read_parquet(DATA)
    df["time"] = pd.to_datetime(df["time"])
    # Admissible era filter FIRST; no pre-2022-06 row enters any computation.
    df = df[(df["time"] >= ERA_MIN) & (df["time"] <= DEV_END)].copy()
    # G0 hard assert on every row that any computation can see.
    assert df["time"].min() >= ERA_MIN, "G0 SEAL VIOLATION: date < 2022-06-01"
    assert df["time"].max() <= DEV_END, "G0 SEAL VIOLATION: date > 2026-05-29"
    tt = df["time"].dt.time
    rth = df[(tt > T_0930) & (tt <= T_1600)].copy()  # end-stamps 09:31..16:00
    rth["date"] = rth["time"].dt.date
    rth["tod"] = rth["time"].dt.time
    rth = rth.sort_values("time").reset_index(drop=True)
    # within-session 1-min log return: first bar open->close, then close-to-close
    logc = np.log(rth["close"].to_numpy())
    logo = np.log(rth["open"].to_numpy())
    grp_first = ~pd.Series(rth["date"]).eq(pd.Series(rth["date"]).shift(1)).to_numpy()
    r = np.empty(len(rth))
    r[grp_first] = (logc - logo)[grp_first]
    r[~grp_first] = (logc - np.roll(logc, 1))[~grp_first]
    rth["r2"] = r * r
    return rth


def per_session_frame(rth, profile=None):
    """Return per-session table: n_fh, n_rod, rv_fh_raw, rv_fh_deseason, rv_rod, rv_day."""
    is_fh = rth["tod"] <= T_1030      # 09:31..10:30 end-stamps
    is_rod = rth["tod"] > T_1030      # 10:31..16:00 end-stamps
    g = rth.groupby("date")
    out = pd.DataFrame({
        "n_fh": rth[is_fh].groupby("date").size(),
        "n_rod": rth[is_rod].groupby("date").size(),
        "rv_fh_raw": rth[is_fh].groupby("date")["r2"].sum(),
        "rv_rod": rth[is_rod].groupby("date")["r2"].sum(),
        "rv_day": g["r2"].sum(),
    })
    if profile is not None:
        fh = rth[is_fh].copy()
        fh["w"] = fh["r2"] / fh["tod"].map(profile)
        out["rv_fh_deseason"] = fh.groupby("date")["w"].sum()
    return out.reset_index()


def main():
    buf = io.StringIO()

    class Tee:
        def write(self, s):
            sys.__stdout__.write(s)
            buf.write(s)

        def flush(self):
            sys.__stdout__.flush()

    sys.stdout = Tee()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    rth = load_sessions()
    obs_min, obs_max = rth["time"].min(), rth["time"].max()

    dts = pd.to_datetime(pd.Series(rth["date"].unique()))
    train_dates = set(dts[(dts >= TRAIN_LO) & (dts <= TRAIN_HI)].dt.date)
    test_dates = set(dts[(dts >= TEST_LO) & (dts <= TEST_HI)].dt.date)

    # ---- diurnal profile FROZEN on TRAIN only ----
    trn = rth[rth["date"].isin(train_dates)]
    # completeness for profile estimation: use all TRAIN RTH bars (mean by minute)
    profile = trn.groupby("tod")["r2"].mean()  # 390 keys, NOT smoothed
    assert profile.min() > 0, "degenerate diurnal profile"

    # ---- per-session quantities (profile applied everywhere, frozen) ----
    ses = per_session_frame(rth, profile=profile)
    n_all = len(ses)
    complete = (ses["n_fh"] >= 54) & (ses["n_rod"] >= 297)
    n_dropped_incomplete = int((~complete).sum())
    ses = ses[complete].copy()
    nonzero = (ses["rv_fh_raw"] > 0) & (ses["rv_rod"] > 0) & (ses["rv_day"] > 0) & \
              (ses["rv_fh_deseason"] > 0)
    n_dropped_zero = int((~nonzero).sum())
    ses = ses[nonzero].sort_values("date").reset_index(drop=True)

    ses["prior_day_logRV"] = np.log(ses["rv_day"]).shift(1)
    ses["raw_early"] = np.log(ses["rv_fh_raw"])
    ses["deseason_early"] = np.log(ses["rv_fh_deseason"])
    ses["y"] = np.log(ses["rv_rod"])

    test = ses[ses["date"].isin(test_dates)].dropna(
        subset=["prior_day_logRV"]).reset_index(drop=True)
    N = len(test)

    # G0 re-assert on the exact rows used in the regression
    dmin, dmax = pd.Timestamp(min(test["date"])), pd.Timestamp(max(test["date"]))
    seal_ok = (obs_min >= ERA_MIN and obs_max <= DEV_END
               and dmin >= TEST_LO and dmax <= TEST_HI)
    assert seal_ok, "G0 SEAL VIOLATION on regression rows"

    test.to_csv(OUT_DIR / "sessions_test.csv", index=False)

    # ---- G1 semantic sentence ----
    g1 = ("G1 SEMANTIC: population = TEST-era (2025-01-01..2026-05-29) NQ RTH sessions "
          f"(N={N}); event = whether DESEASONALIZED first-hour log RV adds forecast power "
          "for rest-of-day (10:30-16:00) log RV beyond prior-day log RV and RAW first-hour "
          "log RV (partial contribution in a nested HAC(5) OLS).")
    print(g1)

    # ---- RAW (incumbent) model ----
    X_raw = sm.add_constant(test[["prior_day_logRV", "raw_early"]])
    X_full = sm.add_constant(test[["prior_day_logRV", "raw_early", "deseason_early"]])
    y = test["y"]
    m_raw = sm.OLS(y, X_raw).fit(cov_type="HAC", cov_kwds={"maxlags": 5})
    r2_raw = m_raw.rsquared

    # ---- G2: MDE BEFORE the observed value (barrier line) ----
    lam = (Z_ALPHA + Z_POWER) ** 2
    f2_min = lam / N
    dr2_min = f2_min * (1.0 - r2_raw) / (1.0 + f2_min)
    mde_adj = adj_r2(r2_raw + dr2_min, N, 3) - adj_r2(r2_raw, N, 2)
    print(f"G2 MDE-BEFORE-LOOKING: MDE(80% power, alpha=.05, 1 added regressor, N={N}, "
          f"RAW R2={r2_raw:.4f}) = incremental R2 {dr2_min:.5f} "
          f"(adjusted units {mde_adj:.5f})")
    print("---------------- BARRIER: everything above printed before the observed "
          "incremental value ----------------")

    # ---- FULL model (observed) ----
    m_full = sm.OLS(y, X_full).fit(cov_type="HAC", cov_kwds={"maxlags": 5})
    beta = m_full.params["deseason_early"]
    t_hac = m_full.tvalues["deseason_early"]
    p_hac = m_full.pvalues["deseason_early"]
    adj_raw_v = adj_r2(r2_raw, N, 2)
    adj_full_v = adj_r2(m_full.rsquared, N, 3)
    d_adj = adj_full_v - adj_raw_v

    # ---- G5 collinearity ----
    corr_rd = float(np.corrcoef(test["raw_early"], test["deseason_early"])[0, 1])
    aux = sm.OLS(test["deseason_early"],
                 sm.add_constant(test[["prior_day_logRV", "raw_early"]])).fit()
    vif = 1.0 / (1.0 - aux.rsquared)

    # ---- stationary block bootstrap (mean block 10, 2000 draws) ----
    def fit_r2(Xm, yv):
        b, *_ = np.linalg.lstsq(Xm, yv, rcond=None)
        e = yv - Xm @ b
        ssr = float(e @ e)
        sst = float(((yv - yv.mean()) ** 2).sum())
        return 1.0 - ssr / sst, b

    Xr = X_raw.to_numpy()
    Xf = X_full.to_numpy()
    yv = y.to_numpy()
    B = 2000
    boot_dadj = np.empty(B)
    boot_beta = np.empty(B)
    p_geo = 1.0 / 10.0
    for b_i in range(B):
        idx = np.empty(N, dtype=int)
        pos = 0
        while pos < N:
            start = rng.integers(0, N)
            length = min(int(rng.geometric(p_geo)), N - pos)
            idx[pos:pos + length] = (start + np.arange(length)) % N
            pos += length
        r2r, _ = fit_r2(Xr[idx], yv[idx])
        r2f, bf = fit_r2(Xf[idx], yv[idx])
        boot_dadj[b_i] = adj_r2(r2f, N, 3) - adj_r2(r2r, N, 2)
        boot_beta[b_i] = bf[3]
    ci_dadj = np.percentile(boot_dadj, [2.5, 97.5])
    ci_beta = np.percentile(boot_beta, [2.5, 97.5])

    # ---- gates ----
    g3_pass = (p_hac <= 0.05) and (d_adj > 0) and (ci_dadj[0] > 0)
    not_identified = vif > 10.0
    underpowered = (not g3_pass) and (mde_adj > 3.0 * abs(d_adj))

    if not_identified:
        verdict = "NOT-IDENTIFIED"
    elif g3_pass:
        verdict = "PASS"
    elif underpowered:
        verdict = "UNDERPOWERED_STILL"
    else:
        verdict = "FAIL"

    rows = [
        ("G0_seal_era",
         "min>=2022-06-01 & max<=2026-05-29, every computation",
         f"min={obs_min} max={obs_max} test[{dmin.date()}..{dmax.date()}]",
         "PASS" if seal_ok else "FAIL"),
        ("G1_semantic", "population+event sentence printed", "printed above", "PASS"),
        ("G2_MDE_first",
         "MDE printed BEFORE observed incremental value",
         f"MDE dAdjR2={mde_adj:.5f} printed above barrier", "PASS"),
        ("G3_primary",
         "HAC p<=0.05 AND dAdjR2>0 beyond bootstrap CI lower bound",
         f"t={t_hac:.3f} p={p_hac:.4f} dAdjR2={d_adj:.5f} "
         f"CI[{ci_dadj[0]:.5f},{ci_dadj[1]:.5f}]",
         "PASS" if g3_pass else "FAIL"),
        ("G4_power",
         "if G3 fails: UNDERPOWERED_STILL when MDE > 3x|obs|",
         f"MDE={mde_adj:.5f} vs 3x|obs|={3*abs(d_adj):.5f} -> "
         + ("UNDERPOWERED_STILL" if underpowered else
            ("adequately powered" if not g3_pass else "n/a (G3 passed)")),
         "PASS"),
        ("G5_collinearity",
         "print corr+VIF; VIF>10 => NOT-IDENTIFIED",
         f"corr(raw,deseason)={corr_rd:.4f} VIF={vif:.2f}"
         + (" -> NOT-IDENTIFIED" if not_identified else ""),
         "PASS" if not not_identified else "NOT-IDENTIFIED"),
    ]

    print()
    print(f"{'GATE':<18}| {'SPEC':<55}| {'OBSERVED':<75}| PASS-FAIL")
    print("-" * 165)
    for g, s, o, pf in rows:
        print(f"{g:<18}| {s:<55}| {o:<75}| {pf}")
    print()
    print(f"VERDICT: {verdict}")
    print(f"HEADLINE: deseason_early HAC(5) t={t_hac:.3f} (p={p_hac:.4f}), "
          f"OOS incremental adjR2={d_adj:.5f} "
          f"(bootstrap 95% CI [{ci_dadj[0]:.5f}, {ci_dadj[1]:.5f}]), "
          f"beta={beta:.4f} CI [{ci_beta[0]:.4f}, {ci_beta[1]:.4f}]")
    print(f"N_test={N}  sessions_total={n_all}  dropped_incomplete={n_dropped_incomplete}"
          f"  dropped_zero_rv={n_dropped_zero}  train_sessions={len(train_dates)}")
    print("EVIDENCE STATUS: DISCOVERY_CONSUMED (all numbers).")

    (OUT_DIR / "gate_table.txt").write_text(buf.getvalue(), encoding="utf-8")

    # ---- regression summary file ----
    with open(OUT_DIR / "regression_summary.txt", "w", encoding="utf-8") as f:
        f.write(f"run_id: G2_F11_MC54LEG2_VOLFORECAST_20260906  seed={SEED}\n")
        f.write(f"N_test={N}  TRAIN sessions={len(train_dates)} (profile frozen, "
                f"no smoothing)\n\n")
        f.write("=== RAW model: y ~ 1 + prior_day_logRV + raw_early  [HAC lag 5] ===\n")
        f.write(str(m_raw.summary()) + "\n\n")
        f.write("=== FULL model: RAW + deseason_early  [HAC lag 5] ===\n")
        f.write(str(m_full.summary()) + "\n\n")
        f.write(f"R2_raw={r2_raw:.6f} adjR2_raw={adj_raw_v:.6f}\n")
        f.write(f"R2_full={m_full.rsquared:.6f} adjR2_full={adj_full_v:.6f}\n")
        f.write(f"incremental adjR2 = {d_adj:.6f}\n")
        f.write(f"MDE (80% power) incremental R2 = {dr2_min:.6f}; adjusted units = "
                f"{mde_adj:.6f}\n")
        f.write(f"corr(raw_early, deseason_early) = {corr_rd:.6f}\n")
        f.write(f"VIF(deseason_early | 1, prior_day_logRV, raw_early) = {vif:.4f}\n")
        f.write(f"bootstrap (stationary, mean block 10, B=2000, seed {SEED}):\n")
        f.write(f"  dAdjR2 95% CI = [{ci_dadj[0]:.6f}, {ci_dadj[1]:.6f}]\n")
        f.write(f"  beta_deseason 95% CI = [{ci_beta[0]:.6f}, {ci_beta[1]:.6f}]\n")
        f.write(f"VERDICT: {verdict}\n")

    return verdict


if __name__ == "__main__":
    main()
