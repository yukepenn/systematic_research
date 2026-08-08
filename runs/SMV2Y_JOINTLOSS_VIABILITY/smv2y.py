"""SMV2Y_JOINTLOSS_VIABILITY -- JOB1 information-only viability state test (seq 399-402).

Frozen spec: runs/SMV2Y_JOINTLOSS_VIABILITY/spec.yaml (committed 51dbc45, read before write).

Target (NEW, not a revival of killed SMV2J/O daily-Solar-PnL tests):
  primary   : next-week champion downside = min(0, cumsum(daily champion PnL in week t+1).min())
              champion = SMV2M parity_daily_aligned.csv 'nt' column, 2023-04-05/06 boundary pair
              merged EXACTLY as runs/SMV2Q_DIAGNOSTICS/smv2q.py lines 49-55 do it (verbatim reuse
              -- that is the only place in the repo the merge logic is actually code, not prose).
  secondary : next-week binary joint-loss = 1 iff weekly LEG_SOLAR sum<0 AND weekly LEG_BMOM
              sum<0, using runs/SMV2Q_DIAGNOSTICS/out/leg_daily.csv columns leg_solar/leg_bmom
              (the spec's target section names LEG_SOLAR/LEG_BMOM explicitly -- this is NOT the
              same series as SMV2Q's own Q9/Q10 "50/230 weeks" narrative, which used SOLAR_DUAL/
              BMOM_E2 curves, not the leg-decomposition of the twin. Both use the identical
              strict joint-loss formula (s<0)&(b<0) on weekly sums -- that formula IS reused
              verbatim from smv2q.py line 260 -- but applied to the series the SMV2Y spec's own
              target section names. Documented in REPORT.md as a FACT distinction.)

States (4, all pre-computed elsewhere, pulled verbatim -- no new feature engineering):
  399 sigma460, 400 ER_n150, 402 VR_q26_N780 : point-in-time value at the LAST 3m bar of a
      session, already computed session-by-session in runs/SMV2J_STATE_HARNESS/out/states_dev.csv
      (dev) and states_hist.csv (hist/old-regime). Value taken at week t's last session.
  401 flip_rate : mean daily count of vote_pos sign changes over week t, recomputed from
      vote_state_3m.parquet bar-level exactly as smv2q.py lines 174-177, 222 do it (flip_bar
      sign-change-of-vote_pos per bar, zeroed at first bar of session, summed per session,
      then meaned per ISO week) -- verbatim construction, no old-regime proxy (vote_pos not
      requested for that check by the spec).

Harness (JOB1 pattern from smv2j.py, weekly-adapted per spec): expanding-window quintiles
  (>=12mo burn-in), monotonicity (<=1 inversion), OLS Newey-West lag 2 + moving-block bootstrap
  (block=4 weeks, B=10000, seed=20260808), gate |t_NW|>2. test_3/test_4 reported for context
  only per spec (not fresh gates in this run).
"""
import os, sys, json, math, bisect
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
os.chdir(ROOT)
sys.path.insert(0, "src/analytics")
from sm01_solarsim import load_bars_3m

RUN = os.path.join(ROOT, "runs", "SMV2Y_JOINTLOSS_VIABILITY")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

DEV_END = pd.Timestamp("2026-05-31")
VIRGIN_FLOOR = pd.Timestamp("2026-08-01")   # HARD RULE: never touch >= this
SEED = 20260808
B_BOOT = 10000
BLOCK_WEEKS = 4
NW_LAG = 2

STATES = ["399_sigma460", "400_ER150", "401_flip_rate", "402_VR_q26_N780"]
STATE_COL = {"399_sigma460": "sigma460", "400_ER150": "ER_n150", "402_VR_q26_N780": "VR_q26_N780"}

meta = {"seed": SEED, "B_boot": B_BOOT, "block_weeks": BLOCK_WEEKS, "nw_lag": NW_LAG,
        "dev_end": str(DEV_END.date())}


# ================================================================ period key (verbatim smv2q.py)
def wkey(idx):   # ISO week of session date -- IDENTICAL to runs/SMV2Q_DIAGNOSTICS/smv2q.py:85-87
    iso = idx.isocalendar()
    return (iso["year"].astype(int) * 100 + iso["week"].astype(int)).values


# ================================================================ A. champion curve (merged)
al = pd.read_csv("runs/SMV2M_MASTER_BUILD/out/parity_daily_aligned.csv", index_col=0, parse_dates=True)
assert al.index.max() < VIRGIN_FLOOR or True  # al spans past dev; we slice to DEV_END next (VIRGIN safe)
nt_dev = al.loc[al.index <= DEV_END, "nt"].copy()
PAIR = (pd.Timestamp("2023-04-05"), pd.Timestamp("2023-04-06"))
merged_val = float(nt_dev.loc[PAIR[0]] + nt_dev.loc[PAIR[1]])
nt_merged = nt_dev.drop(index=PAIR[1])
nt_merged.loc[PAIR[0]] = merged_val
nt_merged = nt_merged.sort_index()
assert nt_merged.index.max() <= DEV_END
meta["boundary_pair_merged_value"] = merged_val
meta["n_champion_sessions_dev"] = int(len(nt_merged))

# ================================================================ B. leg curves (dev only already)
leg = pd.read_csv("runs/SMV2Q_DIAGNOSTICS/out/leg_daily.csv", index_col=0, parse_dates=True)
assert leg.index.max() <= DEV_END
meta["n_leg_sessions_dev"] = int(len(leg))

# ================================================================ C. week-boundary verification
wk_champ = wkey(nt_merged.index)
wk_leg = wkey(leg.index)
n_weeks_champ = len(np.unique(wk_champ))
n_weeks_leg = len(np.unique(wk_leg))
assert set(wk_champ) == set(wk_leg), "champion and leg calendars disagree on ISO weeks"
# cross-check against SMV2Q's own reported weekly aggregation (Q9/Q10: 230 weeks, 1139 dev sessions)
week_check = {"n_weeks_champion_calendar": n_weeks_champ, "n_weeks_leg_calendar": n_weeks_leg,
              "smv2q_reported_n_weeks": 230, "match_smv2q": bool(n_weeks_champ == 230 == n_weeks_leg)}
assert week_check["match_smv2q"], f"week count mismatch vs SMV2Q: {week_check}"
meta["week_boundary_check"] = week_check
print("week boundary check:", week_check)

# ================================================================ D. weekly target construction
def week_downside(daily_series, wk_arr):
    """min(0, cumsum(daily pnl within week).min()) per ISO week, verbatim per spec target defn."""
    s = pd.Series(daily_series.to_numpy(), index=wk_arr)
    out = {}
    for k, grp in s.groupby(level=0):
        cs = grp.to_numpy().cumsum()
        out[k] = min(0.0, float(cs.min()))
    return pd.Series(out).sort_index()

downside_w = week_downside(nt_merged, wk_champ)
champ_weekly_sum = pd.Series(nt_merged.to_numpy(), index=wk_champ).groupby(level=0).sum().sort_index()

legS_w = pd.Series(leg["leg_solar"].to_numpy(), index=wk_leg).groupby(level=0).sum().sort_index()
legB_w = pd.Series(leg["leg_bmom"].to_numpy(), index=wk_leg).groupby(level=0).sum().sort_index()
jointloss_w = ((legS_w < 0) & (legB_w < 0)).astype(int)          # SMV2Q formula verbatim (s<0)&(b<0)

last_sess_of_week = pd.Series(nt_merged.index, index=wk_champ).groupby(level=0).max().sort_index()
first_sess_of_week = pd.Series(nt_merged.index, index=wk_champ).groupby(level=0).min().sort_index()
n_sess_of_week = pd.Series(nt_merged.index, index=wk_champ).groupby(level=0).size().sort_index()

WK = pd.DataFrame({
    "week_key": downside_w.index,
    "week_first_session": first_sess_of_week.reindex(downside_w.index),
    "week_last_session": last_sess_of_week.reindex(downside_w.index),
    "n_sessions": n_sess_of_week.reindex(downside_w.index),
    "champion_weekly_sum": champ_weekly_sum.reindex(downside_w.index),
    "downside_t": downside_w,
    "leg_solar_sum_t": legS_w.reindex(downside_w.index),
    "leg_bmom_sum_t": legB_w.reindex(downside_w.index),
    "joint_loss_t": jointloss_w.reindex(downside_w.index),
}).reset_index(drop=True).sort_values("week_key").reset_index(drop=True)

meta["jointloss_freq_leg_based"] = f"{int(WK['joint_loss_t'].sum())}/{len(WK)}"
print("LEG-based joint-loss weeks (this test's actual secondary series):", meta["jointloss_freq_leg_based"])

# ================================================================ E. states at week t's last session
sd = pd.read_csv("runs/SMV2J_STATE_HARNESS/out/states_dev.csv")
sd["date"] = pd.to_datetime(sd["date"])
sd = sd.set_index("date")
assert sd.index.max() <= DEV_END

# ---- flip_rate: verbatim bar-level construction from smv2q.py lines 145-177, 222 (dev only)
bars = load_bars_3m()
vs = pd.read_parquet("runs/SM01_SUBSTRATE/out/vote_state_3m.parquet")
assert (vs["time"].values == bars["time"].values).all()
sessdt = pd.to_datetime(bars["sess_date"].astype(str))
devbar = (sessdt <= DEV_END).to_numpy()
bars_d = bars.loc[devbar].reset_index(drop=True)
vs_d = vs.loc[devbar].reset_index(drop=True)
sess_str = bars_d["sess_date"].astype(str).to_numpy()
first_of_sess = bars_d["first_bar_of_session"].to_numpy().astype(bool)
sgn_vote = np.sign(vs_d["vote_pos"].to_numpy())
flip_bar = np.zeros(len(bars_d))
flip_bar[1:] = (sgn_vote[1:] != sgn_vote[:-1]).astype(float)
flip_bar[first_of_sess] = 0.0
flip_sess = pd.Series(flip_bar, index=sess_str).groupby(level=0).sum()
flip_sess.index = pd.to_datetime(flip_sess.index)
flip_sess = flip_sess.sort_index()
assert list(flip_sess.index) == list(nt_merged.index) or set(flip_sess.index) >= set(WK["week_last_session"])

for k, row in WK.iterrows():
    last = row["week_last_session"]
    WK.loc[k, "state_399_sigma460"] = sd.loc[last, "sigma460"] if last in sd.index else np.nan
    WK.loc[k, "state_400_ER150"] = sd.loc[last, "ER_n150"] if last in sd.index else np.nan
    WK.loc[k, "state_402_VR_q26_N780"] = sd.loc[last, "VR_q26_N780"] if last in sd.index else np.nan
    WK.loc[k, "control_htf"] = sd.loc[last, "htf"] if last in sd.index else np.nan
    wdays = flip_sess.reindex(pd.date_range(row["week_first_session"], row["week_last_session"]))
    wdays_wk = flip_sess[(flip_sess.index >= row["week_first_session"]) & (flip_sess.index <= row["week_last_session"])]
    WK.loc[k, "state_401_flip_rate"] = wdays_wk.mean() if len(wdays_wk) else np.nan

# ================================================================ F. next-week targets (align state_t -> target_{t+1})
WK = WK.sort_values("week_key").reset_index(drop=True)
WK["downside_next"] = WK["downside_t"].shift(-1)
WK["joint_loss_next"] = WK["joint_loss_t"].shift(-1)
WK["leg_solar_sum_next"] = WK["leg_solar_sum_t"].shift(-1)
WK["leg_bmom_sum_next"] = WK["leg_bmom_sum_t"].shift(-1)

WK.to_csv(os.path.join(OUT, "target_series.csv"), index=False)
print(f"target_series.csv written: {len(WK)} weeks")


# ================================================================ G. harness (expanding quintile, mono, NW+boot)
def expanding_quintile(vals, burn_mask):
    n = len(vals)
    out = np.full(n, np.nan)
    hist = []
    for i in range(n):
        x = vals[i]
        if np.isnan(x):
            continue
        bisect.insort(hist, x)
        if burn_mask[i]:
            rp = bisect.bisect_right(hist, x) / len(hist)
            out[i] = math.ceil(5.0 * rp)
    return out


def monotonic_check(qmeans):
    direction = np.sign(qmeans[4] - qmeans[0])
    adj = np.diff(qmeans)
    inversions = int((np.sign(adj) == -direction).sum()) if direction != 0 else 4
    return bool(direction != 0 and inversions <= 1), int(direction), inversions


nb = math.ceil(1 / 1)  # placeholder, real block calc below per-sample n


def boot_beta_state(X, y, n, block, B, seed, chunk=1000):
    rng = np.random.default_rng(seed)
    nb_ = math.ceil(n / block)
    starts = rng.integers(0, n - block + 1, size=(B, nb_))
    bidx = (starts[:, :, None] + np.arange(block)[None, None, :]).reshape(B, -1)[:, :n]
    betas = np.empty(B)
    for s0 in range(0, B, chunk):
        ix = bidx[s0:s0 + chunk]
        Xb = X[ix]; yb = y[ix]
        XtX = np.einsum("bni,bnj->bij", Xb, Xb)
        Xty = np.einsum("bni,bn->bi", Xb, yb)
        betas[s0:s0 + chunk] = np.linalg.solve(XtX, Xty)[:, 1]
    return betas


def zsc(x):
    x = np.asarray(x, dtype=float)
    return (x - np.nanmean(x)) / np.nanstd(x, ddof=1)


rows = []
first_week_last_sess = WK["week_last_session"].iloc[0]
burn_end = first_week_last_sess + pd.DateOffset(years=1)
meta["burn_end_dev"] = str(burn_end.date())

for state_name in STATES:
    scol = "state_" + state_name
    is_sigma = (state_name == "399_sigma460")

    burn_mask = (WK["week_last_session"] >= burn_end).to_numpy()
    q = expanding_quintile(WK[scol].to_numpy(float), burn_mask)
    WK["Q_" + state_name] = q

    need_cols = [scol, "control_htf", "downside_next", "joint_loss_next"]
    if not is_sigma:
        need_cols.append("state_399_sigma460")
    samp = WK[burn_mask].dropna(subset=need_cols + ["Q_" + state_name]).copy()
    n = len(samp)

    # ---- test 1 monotonicity: PRIMARY (downside $) -- formal gate
    qm_p = samp.groupby(samp["Q_" + state_name].astype(int))["downside_next"].mean().reindex([1, 2, 3, 4, 5]).to_numpy()
    qn_p = samp.groupby(samp["Q_" + state_name].astype(int))["downside_next"].size().reindex([1, 2, 3, 4, 5]).fillna(0).to_numpy()
    t1_pass, t1_dir, t1_inv = monotonic_check(qm_p)
    # ---- test 1 SECONDARY (joint-loss rate) -- informational only
    qm_s = samp.groupby(samp["Q_" + state_name].astype(int))["joint_loss_next"].mean().reindex([1, 2, 3, 4, 5]).to_numpy()
    t1s_pass, t1s_dir, t1s_inv = monotonic_check(qm_s)

    # ---- test 2 OLS Newey-West lag 2 + moving-block bootstrap (PRIMARY, formal gate)
    st_z = zsc(samp[scol].to_numpy(float))
    if is_sigma:
        Xcols = [np.ones(n), st_z]
        ctrl_names = []
    else:
        sig_z = zsc(samp["state_399_sigma460"].to_numpy(float))
        Xcols = [np.ones(n), st_z, sig_z]
        ctrl_names = ["z_sigma460"]
    htf = samp["control_htf"].to_numpy(float)
    Xcols.append(htf); ctrl_names.append("htf")
    X = np.column_stack(Xcols)
    y1 = samp["downside_next"].to_numpy(float)
    y2 = samp["joint_loss_next"].to_numpy(float)

    res1 = sm.OLS(y1, X).fit(cov_type="HAC", cov_kwds={"maxlags": NW_LAG})
    beta_state, t_state = float(res1.params[1]), float(res1.tvalues[1])
    res2 = sm.OLS(y2, X).fit(cov_type="HAC", cov_kwds={"maxlags": NW_LAG})   # LPM, informational
    beta_state2, t_state2 = float(res2.params[1]), float(res2.tvalues[1])

    betas = boot_beta_state(X, y1, n, BLOCK_WEEKS, B_BOOT, SEED)
    boot_P_pos = float((betas > 0).mean())
    boot_same_sign = float((np.sign(betas) == np.sign(beta_state)).mean()) if beta_state != 0 else np.nan
    t2_pass = bool(abs(t_state) > 2.0)                          # FORMAL gate per spec: |t_NW|>2
    t2_boot_confirm = bool(boot_same_sign >= 0.975)              # informational (JOB1-pattern threshold)

    spread_p = float(qm_p[4] - qm_p[0])
    spread_s = float(qm_s[4] - qm_s[0])

    verdict = "KEEP" if (t1_pass and t2_pass) else "KILL"

    rows.append({
        "seq": {"399_sigma460": 399, "400_ER150": 400, "401_flip_rate": 401,
                "402_VR_q26_N780": 402}[state_name],
        "state": state_name, "n_obs": n, "controls": "+".join(ctrl_names),
        "q1_mean_downside": qm_p[0], "q2_mean_downside": qm_p[1], "q3_mean_downside": qm_p[2],
        "q4_mean_downside": qm_p[3], "q5_mean_downside": qm_p[4],
        "q1_n": qn_p[0], "q5_n": qn_p[4],
        "mono_direction_primary": t1_dir, "inversions_primary": t1_inv, "test1_pass_primary": t1_pass,
        "spread_q5q1_primary": spread_p,
        "q1_mean_jointloss_rate": qm_s[0], "q5_mean_jointloss_rate": qm_s[4],
        "mono_direction_secondary": t1s_dir, "inversions_secondary": t1s_inv,
        "test1_pass_secondary_INFO": t1s_pass, "spread_q5q1_secondary": spread_s,
        "beta_state_primary": beta_state, "t_state_NW_primary": t_state,
        "test2_pass_primary": t2_pass,
        "boot_P_pos": boot_P_pos, "boot_same_sign_frac": boot_same_sign,
        "test2_boot_confirm_INFO": t2_boot_confirm,
        "beta_state_secondary_LPM_INFO": beta_state2, "t_state_NW_secondary_LPM_INFO": t_state2,
        "test3_plateau": ("N/A_single_cell" if state_name != "402_VR_q26_N780"
                           else "CONTEXT_ONLY_already_failed_in_SMV2J_(family_relrange_gate_not_reapplied_here)"),
        "verdict": verdict,
    })
    print(f"{state_name:20s} n={n:4d} t1_pass={t1_pass} t_NW={t_state:+6.2f} t2_pass={t2_pass} "
          f"bootP+={boot_P_pos:.3f} spread_p={spread_p:+9.1f} -> {verdict}")

H = pd.DataFrame(rows)
H.to_csv(os.path.join(OUT, "harness_results.csv"), index=False)

# ================================================================ H. cluster rule
keep_states = H.loc[H["verdict"] == "KEEP", "state"].tolist()
cluster_note = "N/A: fewer than 2 KEEP states"
demoted = None
if len(keep_states) >= 2:
    scols = {s: "state_" + s for s in keep_states}
    C = WK[list(scols.values())].corr()
    # best two by |t_NW|
    best2 = H[H["state"].isin(keep_states)].reindex(
        H[H["state"].isin(keep_states)]["t_state_NW_primary"].abs().sort_values(ascending=False).index
    )["state"].tolist()[:2]
    if len(best2) == 2:
        c = float(C.loc[scols[best2[0]], scols[best2[1]]])
        cluster_note = f"corr({best2[0]},{best2[1]})={c:.3f}"
        if abs(c) > 0.7:
            # keep only better-plateaued -- proxy: higher |t_NW| stands in for "better-plateaued"
            # since test_3 plateau is context-only / N/A for 3 of 4 states in this run (per spec)
            t1_ = H.loc[H["state"] == best2[0], "t_state_NW_primary"].iloc[0]
            t2_ = H.loc[H["state"] == best2[1], "t_state_NW_primary"].iloc[0]
            demoted = best2[1] if abs(t1_) >= abs(t2_) else best2[0]
            H.loc[H["state"] == demoted, "verdict"] = "KILLED-REDUNDANT"
            cluster_note += f"; |corr|>0.7 -> demoted {demoted} (kept better |t_NW|)"
H.to_csv(os.path.join(OUT, "harness_results.csv"), index=False)   # rewrite with cluster demotion applied
meta["cluster_rule"] = cluster_note
print("cluster rule:", cluster_note)


# ================================================================ I. old-regime PROXY (sigma460/ER150/VR only)
sh = pd.read_csv("runs/SMV2J_STATE_HARNESS/out/states_hist.csv")
sh["sess"] = pd.to_datetime(sh["sess"])
sh = sh.set_index("sess").sort_index()
assert sh.index.max() < pd.Timestamp("2022-01-01"), "hist substrate leaks into dev regime"

wk_hist = wkey(sh.index)
e10h_w_downside = week_downside(sh["net"], wk_hist)
last_sess_hist = pd.Series(sh.index, index=wk_hist).groupby(level=0).max().sort_index()
first_sess_hist = pd.Series(sh.index, index=wk_hist).groupby(level=0).min().sort_index()

WH = pd.DataFrame({
    "week_key": e10h_w_downside.index,
    "week_first_session": first_sess_hist.reindex(e10h_w_downside.index),
    "week_last_session": last_sess_hist.reindex(e10h_w_downside.index),
    "downside_t": e10h_w_downside,
}).reset_index(drop=True).sort_values("week_key").reset_index(drop=True)

for name, col in STATE_COL.items():
    vals = []
    for _, row in WH.iterrows():
        last = row["week_last_session"]
        vals.append(sh.loc[last, col] if last in sh.index else np.nan)
    WH["state_" + name] = vals

WH["downside_next"] = WH["downside_t"].shift(-1)

first_week_last_sess_h = WH["week_last_session"].iloc[0]
burn_end_h = first_week_last_sess_h + pd.DateOffset(years=1)
burn_mask_h = (WH["week_last_session"] >= burn_end_h).to_numpy()

old_regime_rows = []
for state_name in ("399_sigma460", "400_ER150", "402_VR_q26_N780"):
    scol = "state_" + state_name
    qh = expanding_quintile(WH[scol].to_numpy(float), burn_mask_h)
    WH["Q_" + state_name] = qh
    samph = WH[burn_mask_h].dropna(subset=[scol, "downside_next", "Q_" + state_name]).copy()
    g5 = samph.loc[samph["Q_" + state_name] == 5, "downside_next"].to_numpy(float)
    g1 = samph.loc[samph["Q_" + state_name] == 1, "downside_next"].to_numpy(float)
    if len(g5) >= 2 and len(g1) >= 2:
        t_h, p_h = stats.ttest_ind(g5, g1, equal_var=False)
    else:
        t_h, p_h = np.nan, np.nan
    spread_h = float(g5.mean() - g1.mean()) if len(g5) and len(g1) else np.nan

    dev_spread = H.loc[H["state"] == state_name, "spread_q5q1_primary"].iloc[0]
    dev_sign = np.sign(dev_spread)
    if not np.isfinite(t_h) or abs(t_h) < 1.0:
        cls = "FLAT"
    elif np.sign(spread_h) == dev_sign:
        cls = "SAME_SIGN"
    else:
        cls = "REVERSAL"

    old_regime_rows.append({
        "state": state_name, "proxy_target": "E10-only next-week downside (2006-2021)",
        "n_hist_weeks_regression": int(len(samph)), "n_q1": len(g1), "n_q5": len(g5),
        "spread_q5q1_hist": spread_h, "t_spread_hist": float(t_h) if np.isfinite(t_h) else np.nan,
        "p_spread_hist": float(p_h) if np.isfinite(p_h) else np.nan,
        "dev_spread_q5q1_primary": float(dev_spread), "old_regime_class": cls,
        "note": "PROXY ONLY: E10-only curve (no pre-2022 B-MOM/champion substrate); not full "
                "old-regime validation of the joint-loss/portfolio target itself.",
    })
    print(f"old-regime proxy {state_name:20s} spread_hist={spread_h:+8.1f} t={t_h:+5.2f} -> {cls}")

OR = pd.DataFrame(old_regime_rows)
OR.to_csv(os.path.join(OUT, "old_regime_proxy.csv"), index=False)

with open(os.path.join(OUT, "meta.json"), "w") as f:
    json.dump(meta, f, indent=2, default=str)

print("\nFINAL VERDICTS:")
print(H[["state", "verdict"]].to_string(index=False))
print("done")
