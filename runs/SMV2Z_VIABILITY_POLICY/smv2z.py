"""SMV2Z_VIABILITY_POLICY -- seq 403 (policy cells), 404 (placebo), 405 (chronology+oldregime-proxy).
Frozen spec: runs/SMV2Z_VIABILITY_POLICY/spec.yaml (committed fdd0e65, read before write).

Policy: scaled[week t+1] = s * champion_pnl[week t+1] iff sigma460_top_tercile[t] AND
ER150_top_tercile[t] (both measured at week t's close, expanding tercile, >=12mo burn-in,
IDENTICAL construction to SMV2Y's expanding_quintile machinery generalized to n_bins=3);
else unchanged. s in {0.5, 0.7, 0.85}, center 0.7.

Data reuse (per spec CODE MAP, verbatim / minimally-generalized, no reimplementation):
  - champion curve: runs/SMV2M_MASTER_BUILD/out/parity_daily_aligned.csv 'nt', 2023-04-05/06
    boundary pair merged EXACTLY as smv2y.py section A does it (itself IDENTICAL to
    smv2q.py lines 49-55) -- copied verbatim below.
  - states: runs/SMV2Y_JOINTLOSS_VIABILITY/out/target_series.csv columns
    state_399_sigma460 / state_400_ER150 (raw values, already the exact per-week snapshot
    SMV2Y used) -- REUSED, no re-extraction from states_dev.csv.
  - tercile machinery: smv2y.py's expanding_quintile function, copied verbatim and given an
    n_bins parameter (5 for the STEP0 reproduction check, 3 for the tercile flags this run
    actually uses) -- the core bisect.insort expanding-percentile-rank logic is UNCHANGED.
  - gate battery (CDaR/TUW improve, placebo threshold=median+2*IQR over 200 seeds, LOYO+leave-
    2022-out, RTC>=0.97, net retention>=0.97): metric helpers (dd_of/cdar95/tuw_longest/sharpe)
    and the placebo/chronology/RTC/retention PATTERN copied verbatim from
    runs/SMV2N_WINDFALL_POLICY/smv2n.py and runs/SMV2V_ER_DAMPER/smv2v.py, only the trigger
    unit changes (WEEK, not day/multi-day-run) since this policy scales at the weekly level.
  - old-regime proxy (gate 6): runs/SMV2J_STATE_HARNESS/out/states_hist.csv 'net' column (the
    E10-only 2006-2021 curve, exactly what smv2y.py section I used) + sigma460/ER_n150 columns,
    same week_downside()/wkey() construction, own expanding tercile + own 12mo burn-in, per spec.

House bootstrap (non-gating context, per orchestrator instructions): block_bootstrap_delta
(src/analytics/sm_metrics.py), seed=20260808, block=5 on the daily policy-vs-unscaled delta AND
block=4 on the weekly-aggregated policy-vs-unscaled delta (matching SMV2Y's own BLOCK_WEEKS=4).

HARD: no data >= 2026-08-01 ever used; dev sessions <= 2026-05-31 only. no_moves: tercile cut
fixed at n_bins=3 (33/67 split), AND-gate logic fixed, s fixed to the 3 frozen cells.
"""
import os
import sys
import math
import bisect

import numpy as np
import pandas as pd
from scipy import stats

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(REPO, "runs", "SMV2Z_VIABILITY_POLICY")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.join(REPO, "src", "analytics"))
from sm_metrics import block_bootstrap_delta  # noqa: E402

DEV_END = pd.Timestamp("2026-05-31")
VIRGIN_FLOOR = pd.Timestamp("2026-08-01")
CELLS = [0.5, 0.7, 0.85]
CENTER = 0.7
N_PLACEBO = 200
HOUSE_SEED = 20260808
HOUSE_BLOCK_DAILY = 5
HOUSE_BLOCK_WEEKS = 4
HOUSE_NBOOT = 10000


def sgn(v):
    return 0 if v == 0 else (1 if v > 0 else -1)


def dd_of(net):
    eq = np.cumsum(np.asarray(net, dtype=float))
    return np.maximum.accumulate(eq) - eq


def cdar95(net):
    """dd_battery 'CDaR5'-exact (SMV2N/V-identical light implementation)."""
    dd = dd_of(net)
    ddpos = np.sort(dd[dd > 0])[::-1]
    k = max(1, int(0.05 * len(dd)))
    return float(ddpos[:k].mean()) if len(ddpos) else 0.0


def tuw_longest(net):
    """dd_battery 'longest_TUW_days'-exact."""
    dd = dd_of(net)
    uw = dd > 1e-9
    tuw = cur = 0
    for u in uw:
        cur = cur + 1 if u else 0
        tuw = max(tuw, cur)
    return int(tuw)


def sharpe(net):
    net = np.asarray(net, dtype=float)
    sd = net.std(ddof=1)
    return float(net.mean() / sd * np.sqrt(252)) if sd > 0 else np.nan


def wkey(idx):   # ISO week of session date -- IDENTICAL to smv2q.py:85-87 / smv2y.py:64-66
    iso = idx.isocalendar()
    return (iso["year"].astype(int) * 100 + iso["week"].astype(int)).values


def week_downside(daily_series, wk_arr):
    """min(0, cumsum(daily pnl within week).min()) per ISO week -- verbatim smv2y.py:101-108."""
    s = pd.Series(daily_series.to_numpy(), index=wk_arr)
    out = {}
    for k, grp in s.groupby(level=0):
        cs = grp.to_numpy().cumsum()
        out[k] = min(0.0, float(cs.min()))
    return pd.Series(out).sort_index()


def expanding_rank_bucket(vals, burn_mask, n_bins):
    """smv2y.py's expanding_quintile, verbatim core logic, n_bins parametrized
    (5 reproduces SMV2Y exactly; 3 gives this run's tercile buckets)."""
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
            out[i] = math.ceil(n_bins * rp)
    return out


log_lines = []
def log(msg):
    print(msg, flush=True)
    log_lines.append(str(msg))


# ============================================================== 1. load SMV2Y states (REUSE)

WK = pd.read_csv(os.path.join(REPO, "runs", "SMV2Y_JOINTLOSS_VIABILITY", "out", "target_series.csv"))
WK["week_first_session"] = pd.to_datetime(WK["week_first_session"])
WK["week_last_session"] = pd.to_datetime(WK["week_last_session"])
WK = WK.sort_values("week_key").reset_index(drop=True)
assert WK["week_last_session"].max() <= DEV_END, "VIRGIN guard: SMV2Y target_series extends past dev"
n_weeks = len(WK)
log(f"loaded target_series.csv: {n_weeks} weeks, week_key range {WK['week_key'].min()}-{WK['week_key'].max()}")

first_week_last_sess = WK["week_last_session"].iloc[0]
burn_end = first_week_last_sess + pd.DateOffset(years=1)
burn_mask = (WK["week_last_session"] >= burn_end).to_numpy()
log(f"burn_end={burn_end.date()} (>=12mo from first week's last session {first_week_last_sess.date()}); "
    f"n_burn_eligible_weeks={int(burn_mask.sum())}/{n_weeks}")
assert str(burn_end.date()) == "2023-01-07", "burn_end must match SMV2Y's own meta.json burn_end_dev"


# ============================================================== 2. STEP0 repro: quintile machinery vs SMV2Y

harness = pd.read_csv(os.path.join(REPO, "runs", "SMV2Y_JOINTLOSS_VIABILITY", "out", "harness_results.csv"))

repro_rows = []
for state_name, scol, is_sigma in [("399_sigma460", "state_399_sigma460", True),
                                    ("400_ER150", "state_400_ER150", False)]:
    q5 = expanding_rank_bucket(WK[scol].to_numpy(float), burn_mask, n_bins=5)
    need_cols = [scol, "control_htf", "downside_next", "joint_loss_next"]
    if not is_sigma:
        need_cols.append("state_399_sigma460")
    tmp = WK.copy()
    tmp["Q5_repro"] = q5
    samp = tmp[burn_mask].dropna(subset=need_cols + ["Q5_repro"]).copy()
    qm = samp.groupby(samp["Q5_repro"].astype(int))["downside_next"].mean().reindex([1, 2, 3, 4, 5])
    qn = samp.groupby(samp["Q5_repro"].astype(int))["downside_next"].size().reindex([1, 2, 3, 4, 5]).fillna(0)
    ref = harness.set_index("state").loc[state_name]
    got = {"q1_mean_downside": qm[1], "q2_mean_downside": qm[2], "q3_mean_downside": qm[3],
           "q4_mean_downside": qm[4], "q5_mean_downside": qm[5], "q1_n": qn[1], "q5_n": qn[5]}
    ok = all(abs(float(got[c]) - float(ref[c])) <= 1e-6 for c in
             ["q1_mean_downside", "q2_mean_downside", "q3_mean_downside", "q4_mean_downside", "q5_mean_downside"]) \
        and int(got["q1_n"]) == int(ref["q1_n"]) and int(got["q5_n"]) == int(ref["q5_n"])
    repro_rows.append({"state": state_name, "match_smv2y_quintiles": bool(ok),
                        **{f"got_{k}": v for k, v in got.items()},
                        **{f"ref_{k}": ref[k] for k in got}})
    log(f"STEP0 repro {state_name}: match_SMV2Y_quintiles={ok}")

repro_df = pd.DataFrame(repro_rows)
repro_df.to_csv(os.path.join(OUT, "step0_quintile_repro.csv"), index=False)
STEP0_PASS = bool(repro_df["match_smv2y_quintiles"].all())
if not STEP0_PASS:
    log("STEP0 REPRO FAILED -- expanding-rank machinery does not reproduce SMV2Y's own quintile "
        "cut points. BLOCKED per hard rules (never trust unverified reused machinery).")
    with open(os.path.join(OUT, "BLOCKED.txt"), "w") as f:
        f.write("STEP0 quintile reproduction against SMV2Y harness_results.csv FAILED.\n")
        f.write(repro_df.to_string())
    sys.exit(2)
log("STEP0 PASS: expanding-rank machinery reproduces SMV2Y's own quintile cut points exactly (<=1e-6).")


# ============================================================== 3. tercile flags (n_bins=3) + sanity check

T399 = expanding_rank_bucket(WK["state_399_sigma460"].to_numpy(float), burn_mask, n_bins=3)
T400 = expanding_rank_bucket(WK["state_400_ER150"].to_numpy(float), burn_mask, n_bins=3)
WK["T399_tercile"] = T399
WK["T400_tercile"] = T400
WK["top399"] = (T399 == 3)
WK["top400"] = (T400 == 3)
WK["flag_t"] = WK["top399"].to_numpy() & WK["top400"].to_numpy() & burn_mask

# sanity check: tercile cutoff (rp=2/3) value should sit between the Q3/Q4 (rp=0.6) and Q4/Q5
# (rp=0.8) quintile cutoff VALUES on the same expanding history, at several sample weeks.
def cutoff_values_at(vals, upto_i, rps):
    hist = sorted(v for v in vals[:upto_i + 1] if not np.isnan(v))
    out = []
    for rp in rps:
        idx = min(len(hist) - 1, max(0, int(math.ceil(rp * len(hist))) - 1))
        out.append(hist[idx])
    return out


sanity_rows = []
check_positions = np.linspace(0, n_weeks - 1, 8).astype(int)
check_positions = sorted(set(int(i) for i in check_positions if burn_mask[i]))
for state_name, col in [("399_sigma460", "state_399_sigma460"), ("400_ER150", "state_400_ER150")]:
    vals = WK[col].to_numpy(float)
    for i in check_positions:
        c60, c667, c80 = cutoff_values_at(vals, i, [0.6, 2.0 / 3.0, 0.8])
        between = bool(c60 <= c667 <= c80) or bool(c60 >= c667 >= c80)  # monotone cut in raw-value space
        sanity_rows.append({"state": state_name, "row_i": i, "week_key": int(WK["week_key"].iloc[i]),
                             "q3q4_cut_rp0.60": c60, "tercile_cut_rp0.667": c667, "q4q5_cut_rp0.80": c80,
                             "tercile_between_q3q4_and_q4q5": between})
sanity_df = pd.DataFrame(sanity_rows)
sanity_df.to_csv(os.path.join(OUT, "tercile_sanity_check.csv"), index=False)
SANITY_PASS = bool(sanity_df["tercile_between_q3q4_and_q4q5"].all())
log(f"tercile sanity check (cutoff at rp=2/3 sits between Q3/Q4 and Q4/Q5 quintile cutoffs): "
    f"{SANITY_PASS} ({int(sanity_df['tercile_between_q3q4_and_q4q5'].sum())}/{len(sanity_df)} checkpoints)")
if not SANITY_PASS:
    log("TERCILE SANITY CHECK FAILED -- BLOCKED.")
    with open(os.path.join(OUT, "BLOCKED.txt"), "w") as f:
        f.write("Tercile cutoff sanity check FAILED.\n")
        f.write(sanity_df.to_string())
    sys.exit(2)

n_flag = int(WK["flag_t"].sum())
log(f"AND-gate trigger weeks (both top tercile at week t's close): {n_flag}/{int(burn_mask.sum())} "
    f"burn-eligible weeks")


# ============================================================== 4. champion daily curve (verbatim merge)

al = pd.read_csv(os.path.join(REPO, "runs", "SMV2M_MASTER_BUILD", "out", "parity_daily_aligned.csv"),
                 index_col=0, parse_dates=True)
assert al.index.max() < VIRGIN_FLOOR, "VIRGIN guard: parity_daily_aligned.csv extends into virgin territory"
nt_dev = al.loc[al.index <= DEV_END, "nt"].copy()
PAIR = (pd.Timestamp("2023-04-05"), pd.Timestamp("2023-04-06"))
merged_val = float(nt_dev.loc[PAIR[0]] + nt_dev.loc[PAIR[1]])
nt_merged = nt_dev.drop(index=PAIR[1])
nt_merged.loc[PAIR[0]] = merged_val
nt_merged = nt_merged.sort_index()
assert nt_merged.index.max() <= DEV_END

meta_ref = __import__("json").load(open(os.path.join(REPO, "runs", "SMV2Y_JOINTLOSS_VIABILITY", "out", "meta.json")))
champ_repro_ok = (len(nt_merged) == meta_ref["n_champion_sessions_dev"]
                  and abs(merged_val - meta_ref["boundary_pair_merged_value"]) <= 1e-6)
log(f"champion curve repro vs SMV2Y meta.json: n={len(nt_merged)} (expect {meta_ref['n_champion_sessions_dev']}), "
    f"merged_val={merged_val:.6f} (expect {meta_ref['boundary_pair_merged_value']:.6f}) -> {champ_repro_ok}")
assert champ_repro_ok, "champion curve boundary-pair merge does not reproduce SMV2Y's own values -- BLOCKED"

cal = nt_merged.index
x = nt_merged.to_numpy()
n = len(x)
wk_champ = wkey(cal)


# ============================================================== 5. trigger-week -> scaled-day mask

trigger_week_keys = set()
for i in range(n_weeks - 1):   # last row has no "next" row
    if WK["flag_t"].iloc[i]:
        trigger_week_keys.add(int(WK["week_key"].iloc[i + 1]))
n_scaled_weeks = len(trigger_week_keys)
is_scaled_day = np.isin(wk_champ, list(trigger_week_keys))
n_scaled_days = int(is_scaled_day.sum())
log(f"n_scaled_weeks(receiver, t+1)={n_scaled_weeks} n_scaled_days={n_scaled_days} "
    f"trigger_week_keys={sorted(trigger_week_keys)}")

first_burn_idx = int(np.where(burn_mask)[0][0]) if burn_mask.any() else n_weeks
lo_row = first_burn_idx + 1   # earliest row index a real/placebo SCALED week can occupy


# ============================================================== 6. policy cells

cdar_un = cdar95(x)
tuw_un = tuw_longest(x)
sh_un = sharpe(x)
net_un = float(x.sum())
k_dec = int(np.ceil(0.10 * n))
top_idx = np.argsort(x)[::-1][:k_dec]
top_min = float(x[top_idx].min())
assert (x[top_idx] > 0).all(), "champion top-decile day contains a non-positive day"

daily = pd.DataFrame({"sess": cal, "week_key": wk_champ, "pnl_unscaled": x, "scaled": is_scaled_day})
cell_curves = {}
house_boot_daily = {}
for s in CELLS:
    scale_vec = np.where(is_scaled_day, s, 1.0)
    pol = x * scale_vec
    cell_curves[s] = pol
    daily[f"pnl_s{s:.2f}"] = pol
    house_boot_daily[s] = block_bootstrap_delta(pol, x, block=HOUSE_BLOCK_DAILY, n_boot=HOUSE_NBOOT, seed=HOUSE_SEED)
daily.to_csv(os.path.join(OUT, "policy_daily.csv"), index=False)


# ============================================================== 7. placebo battery (seq 404): same-count non-overlapping trigger-WEEKS

pool_rows_idx = np.array([i for i in range(lo_row, n_weeks) if int(WK["week_key"].iloc[i]) not in trigger_week_keys])
pl_rows = []
for seed in range(1, N_PLACEBO + 1):
    rng = np.random.default_rng(seed)
    ok = len(pool_rows_idx) >= n_scaled_weeks and n_scaled_weeks > 0
    mask_days = np.zeros(n, dtype=bool)
    chosen_weeks = []
    if ok:
        chosen = rng.choice(pool_rows_idx, size=n_scaled_weeks, replace=False)
        chosen_weeks = WK["week_key"].iloc[chosen].astype(int).tolist()
        mask_days = np.isin(wk_champ, chosen_weeks)
    row = {"seed": seed, "feasible": ok, "n_scaled_weeks": n_scaled_weeks, "n_scaled_days": int(mask_days.sum())}
    for s in CELLS:
        if ok:
            pl = x * np.where(mask_days, s, 1.0)
            row[f"dcdar_s{s:.2f}"] = cdar_un - cdar95(pl)
            row[f"dtuw_s{s:.2f}"] = tuw_un - tuw_longest(pl)
        else:
            row[f"dcdar_s{s:.2f}"] = np.nan
            row[f"dtuw_s{s:.2f}"] = np.nan
    pl_rows.append(row)
plc = pd.DataFrame(pl_rows)
plc.to_csv(os.path.join(OUT, "placebo.csv"), index=False)
n_feas = int(plc["feasible"].sum())
log(f"placebo: feasible={n_feas}/{N_PLACEBO} (pool_size={len(pool_rows_idx)}, need={n_scaled_weeks})")


# ============================================================== 8. chronology battery (seq 405a)

years = np.array([d.year for d in cal])
yr_list = sorted(set(years.tolist()))
chron_rows = []
loyo_gate = {}
for s in CELLS:
    pol = cell_curves[s]
    dsh_full = sharpe(pol) - sh_un
    sign_full = sgn(dsh_full)
    chron_rows.append({"s": s, "scope": "full", "sharpe_unscaled": sh_un, "sharpe_policy": sharpe(pol),
                       "dsharpe": dsh_full, "sign": sign_full, "n_days": n})
    agree = 0
    sign_loyo_2022 = None
    for y in yr_list:
        m = years != y
        dsh = sharpe(pol[m]) - sharpe(x[m])
        chron_rows.append({"s": s, "scope": f"loyo_{y}", "sharpe_unscaled": sharpe(x[m]),
                           "sharpe_policy": sharpe(pol[m]), "dsharpe": dsh, "sign": sgn(dsh),
                           "n_days": int(m.sum())})
        if sgn(dsh) == sign_full:
            agree += 1
        if y == 2022:
            sign_loyo_2022 = sgn(dsh)
    for y in yr_list:
        m = years == y
        dsh = sharpe(pol[m]) - sharpe(x[m])
        chron_rows.append({"s": s, "scope": f"year_{y}", "sharpe_unscaled": sharpe(x[m]),
                           "sharpe_policy": sharpe(pol[m]), "dsharpe": dsh, "sign": sgn(dsh),
                           "n_days": int(m.sum())})
    loyo_gate[s] = {"agree": agree, "n_years": len(yr_list),
                    "loyo2022_keeps_sign": bool(sign_loyo_2022 == sign_full),
                    "pass": bool(agree >= 4 and sign_loyo_2022 == sign_full)}
pd.DataFrame(chron_rows).to_csv(os.path.join(OUT, "chronology.csv"), index=False)
log(f"LOYO gates: { {s: loyo_gate[s]['pass'] for s in CELLS} }")


# ============================================================== 9. gate 6: old-regime AND-gate proxy (seq 405b)

sh = pd.read_csv(os.path.join(REPO, "runs", "SMV2J_STATE_HARNESS", "out", "states_hist.csv"))
sh["sess"] = pd.to_datetime(sh["sess"])
sh = sh.set_index("sess").sort_index()
assert sh.index.max() < pd.Timestamp("2022-01-01"), "hist substrate leaks into dev regime"

# cross-check states_hist.csv 'net' == SM06's own e10_daily_hist.csv (same object, sanity check)
e10h = pd.read_csv(os.path.join(REPO, "runs", "SM06_SOLAR_HISTORY", "out", "e10_daily_hist.csv"))
e10h["sess"] = pd.to_datetime(e10h["sess"])
e10h = e10h.set_index("sess").sort_index()
common_idx = sh.index.intersection(e10h.index)
net_cross_check = float(np.max(np.abs(sh.loc[common_idx, "net"].to_numpy() - e10h.loc[common_idx, "net"].to_numpy())))
log(f"states_hist.csv 'net' vs SM06 e10_daily_hist.csv 'net' max abs diff over {len(common_idx)} common "
    f"sessions: {net_cross_check:.10f} (0 => identical source, confirms states_hist.csv net IS the "
    f"E10-only hist curve smv2y.py section I actually used)")

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

STATE_COL = {"399_sigma460": "sigma460", "400_ER150": "ER_n150"}
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
log(f"old-regime proxy: {len(WH)} hist weeks, own burn_end={burn_end_h.date()}, "
    f"n_burn_eligible={int(burn_mask_h.sum())}")

Th399 = expanding_rank_bucket(WH["state_399_sigma460"].to_numpy(float), burn_mask_h, n_bins=3)
Th400 = expanding_rank_bucket(WH["state_400_ER150"].to_numpy(float), burn_mask_h, n_bins=3)
WH["top399"] = (Th399 == 3)
WH["top400"] = (Th400 == 3)
WH["flag_proxy"] = WH["top399"].to_numpy() & WH["top400"].to_numpy() & burn_mask_h

samp_h = WH[burn_mask_h].dropna(subset=["downside_next"]).copy()
flagged_h = samp_h[samp_h["flag_proxy"]]
baseline_h = samp_h[~samp_h["flag_proxy"]]
n_flag_h = len(flagged_h)
n_base_h = len(baseline_h)

if n_flag_h >= 2 and n_base_h >= 2:
    t_h, p_h = stats.ttest_ind(flagged_h["downside_next"].to_numpy(), baseline_h["downside_next"].to_numpy(),
                                equal_var=False)
else:
    t_h, p_h = np.nan, np.nan
flagged_mean_h = float(flagged_h["downside_next"].mean()) if n_flag_h else np.nan
baseline_mean_h = float(baseline_h["downside_next"].mean()) if n_base_h else np.nan
overall_mean_h = float(samp_h["downside_next"].mean())
diff_h = flagged_mean_h - baseline_mean_h if (n_flag_h and n_base_h) else np.nan

# expected direction established by SMV2Y's own dev-side finding (both spread_q5q1_primary < 0,
# i.e. higher-risk state -> MORE NEGATIVE downside_next): FACT, from harness_results.csv
DEV_EXPECTED_SIGN = -1  # flagged (both top tercile) should show MORE NEGATIVE downside_next than baseline

if not np.isfinite(t_h) or abs(t_h) < 1.0:
    old_regime_class = "FLAT"
elif np.isfinite(diff_h) and sgn(diff_h) == DEV_EXPECTED_SIGN:
    old_regime_class = "SAME_SIGN"
else:
    old_regime_class = "REVERSAL"

gate6_pass = bool(old_regime_class != "REVERSAL")
log(f"old-regime proxy AND-gate: n_flag={n_flag_h} n_baseline={n_base_h} flagged_mean={flagged_mean_h:.1f} "
    f"baseline_mean={baseline_mean_h:.1f} diff={diff_h:.1f} t={t_h:.2f} p={p_h:.4f} -> {old_regime_class} "
    f"(gate6_pass={gate6_pass})")

oldregime_row = {
    "proxy_target": "E10-only next-week downside (2006-2021), same AND-gate construction",
    "n_hist_weeks": len(WH), "n_burn_eligible": int(burn_mask_h.sum()),
    "n_flagged_and_gate_weeks": n_flag_h, "n_baseline_weeks": n_base_h,
    "flagged_mean_downside_next": flagged_mean_h, "baseline_mean_downside_next": baseline_mean_h,
    "overall_mean_downside_next": overall_mean_h, "diff_flagged_minus_baseline": diff_h,
    "t_welch": float(t_h) if np.isfinite(t_h) else np.nan, "p_welch": float(p_h) if np.isfinite(p_h) else np.nan,
    "dev_expected_sign": DEV_EXPECTED_SIGN,
    "old_regime_class": old_regime_class, "gate6_pass": gate6_pass,
    "note": "PROXY ONLY: E10-only curve (no pre-2022 B-MOM/champion substrate), states_hist.csv "
            "sigma460/ER_n150; not full old-regime validation of the champion twin AND-gate policy.",
}
pd.DataFrame([oldregime_row]).to_csv(os.path.join(OUT, "oldregime_proxy.csv"), index=False)


# ============================================================== 10. house bootstrap (non-gating context)

wk_pol_sum = {}
for s in CELLS:
    ps = pd.Series(cell_curves[s], index=wk_champ).groupby(level=0).sum().sort_index()
    us = pd.Series(x, index=wk_champ).groupby(level=0).sum().sort_index()
    assert (ps.index == us.index).all()
    hb_w = block_bootstrap_delta(ps.to_numpy(), us.to_numpy(), block=HOUSE_BLOCK_WEEKS,
                                 n_boot=HOUSE_NBOOT, seed=HOUSE_SEED)
    wk_pol_sum[s] = hb_w


# ============================================================== 11. gates + policy_cells.csv (seq 403)

cells_rows = []
for s in CELLS:
    pol = cell_curves[s]
    cd = cdar95(pol)
    tu = tuw_longest(pol)
    net_p = float(pol.sum())
    dcdar = cdar_un - cd
    dtuw = tuw_un - tu
    rtc = float(pol[top_idx].sum() / x[top_idx].sum())
    ret = net_p / net_un

    pc = plc[plc["feasible"]]
    med_c = float(pc[f"dcdar_s{s:.2f}"].median()) if n_feas else np.nan
    iqr_c = float(pc[f"dcdar_s{s:.2f}"].quantile(0.75) - pc[f"dcdar_s{s:.2f}"].quantile(0.25)) if n_feas else np.nan
    med_t = float(pc[f"dtuw_s{s:.2f}"].median()) if n_feas else np.nan
    iqr_t = float(pc[f"dtuw_s{s:.2f}"].quantile(0.75) - pc[f"dtuw_s{s:.2f}"].quantile(0.25)) if n_feas else np.nan
    thr_c = med_c + 2.0 * iqr_c if n_feas else np.nan
    thr_t = med_t + 2.0 * iqr_t if n_feas else np.nan

    g1_c = bool(cd < cdar_un)
    g1_t = bool(tu < tuw_un)
    g2_c = bool(n_feas > 0 and dcdar > thr_c)
    g2_t = bool(n_feas > 0 and dtuw > thr_t)
    g3 = loyo_gate[s]["pass"]
    g4 = bool(rtc >= 0.97)
    g5 = bool(ret >= 0.97)
    g6 = gate6_pass  # not cell-specific (state/AND-gate construction shared across s)
    hb_d = house_boot_daily[s]
    hb_w = wk_pol_sum[s]
    cells_rows.append({
        "s": s, "n_days": n, "n_weeks": n_weeks, "n_scaled_weeks": n_scaled_weeks,
        "n_scaled_days": n_scaled_days,
        "net_unscaled": net_un, "net_policy": net_p, "net_retention": ret,
        "cdar95_unscaled": cdar_un, "cdar95_policy": cd, "dcdar": dcdar,
        "tuw_unscaled": tuw_un, "tuw_policy": tu, "dtuw": dtuw,
        "maxdd_unscaled": float(dd_of(x).max()), "maxdd_policy": float(dd_of(pol).max()),
        "sharpe_unscaled": sh_un, "sharpe_policy": sharpe(pol), "dsharpe_full": sharpe(pol) - sh_un,
        "rtc": rtc, "rtc_k_days": k_dec, "rtc_topdecile_min_pnl": top_min,
        "placebo_n_feasible": n_feas,
        "placebo_dcdar_median": med_c, "placebo_dcdar_iqr": iqr_c, "placebo_dcdar_thresh": thr_c,
        "placebo_dtuw_median": med_t, "placebo_dtuw_iqr": iqr_t, "placebo_dtuw_thresh": thr_t,
        "loyo_agree_count": loyo_gate[s]["agree"], "loyo_n_years": loyo_gate[s]["n_years"],
        "loyo2022_keeps_sign": loyo_gate[s]["loyo2022_keeps_sign"],
        "gate1_cdar_improve": g1_c, "gate1_tuw_improve": g1_t,
        "gate2_cdar_gt_placebo": g2_c, "gate2_tuw_gt_placebo": g2_t,
        "gate3_loyo": g3, "gate4_rtc": g4, "gate5_retention": g5, "gate6_oldregime_proxy": g6,
        "all_gates_pass": bool(g1_c and g1_t and g2_c and g2_t and g3 and g4 and g5 and g6),
        "house_boot_daily_delta_mean": hb_d["delta"], "house_boot_daily_p_leq_0": hb_d["p_leq_0"],
        "house_boot_daily_ci_lo": hb_d["ci_lo"], "house_boot_daily_ci_hi": hb_d["ci_hi"],
        "house_boot_weekly_delta_mean": hb_w["delta"], "house_boot_weekly_p_leq_0": hb_w["p_leq_0"],
        "house_boot_weekly_ci_lo": hb_w["ci_lo"], "house_boot_weekly_ci_hi": hb_w["ci_hi"],
    })
cells = pd.DataFrame(cells_rows)
cells.to_csv(os.path.join(OUT, "policy_cells.csv"), index=False)

center_row = cells[cells["s"] == CENTER].iloc[0]
verdict = "SURVIVES" if bool(cells["all_gates_pass"].all()) else "KILLED"
log("\n" + cells.T.to_string())
log(f"\nVERDICT (all 3 cells must pass, no_moves): {verdict}")
log(f"ALL-CELLS pass: {cells['all_gates_pass'].tolist()}")
log(f"center(s=0.7) all_gates_pass: {bool(center_row['all_gates_pass'])}")

with open(os.path.join(OUT, "run_log.txt"), "w") as f:
    f.write("\n".join(log_lines))
