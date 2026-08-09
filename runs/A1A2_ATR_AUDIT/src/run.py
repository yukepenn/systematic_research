"""A1A2_ATR_AUDIT — drawdown complementarity (A1) + market-only mechanism test (A2).
Frozen spec.yaml. Reuses SMV2AJ_ATR_BLEND_R2's saved raw targets/curves; no re-simulation of the
ATR blend itself (frozen w=0.75, not touched)."""
import os, sys, json, datetime as dt
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R2_M5_XINST", "src"))
import sm01_solarsim as sm
import common as C1
import run_m5 as M5REF  # for atr_series(), verbatim reuse

RUN = os.path.join(ROOT, "runs", "A1A2_ATR_AUDIT")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
SRC = os.path.join(ROOT, "runs", "SMV2AJ_ATR_BLEND_R2", "out")
DEV_END = dt.date(2026, 5, 29)
SEED, BLOCK, NBOOT = 20260809, 5, 10000


def battery(x):
    eqd = np.cumsum(x); dd = np.maximum.accumulate(eqd) - eqd
    k = max(1, int(0.05 * len(x)))
    sd = x.std(ddof=1)
    return {"sharpe": float(x.mean() / sd * np.sqrt(252)) if sd > 0 and len(x) > 1 else np.nan,
            "CDaR_0.95": float(np.sort(dd)[::-1][:k].mean()) if len(dd) else 0.0, "net": float(x.sum())}


bars = C1.load_dev_bars()
n = len(bars)
sess = bars["sess_date"].to_numpy()

# ============================================================== self-check: reload raw targets, re-derive
tgt_control = np.load(os.path.join(SRC, "tgt_control_raw_dev.npy"))
tgt_blend75 = np.load(os.path.join(SRC, "tgt_blend75_raw_dev.npy"))
assert len(tgt_control) == n == len(tgt_blend75), "bar-count mismatch vs SMV2AJ's saved targets — STOP"

daily_solar_c, barpos_c, barpnl_c = C1.e10_exec(bars, tgt_control)
daily_solar_b, barpos_b, barpnl_b = C1.e10_exec(bars, tgt_blend75)
cal_solar = daily_solar_c["sess"].astype(str)

curves = pd.read_csv(os.path.join(SRC, "curves.csv"))
curves["sess"] = curves["sess"].astype(str)
solar_net_total = daily_solar_c["net"].sum()
dual_net_total = curves["DUAL_CONTROL"].sum()
selfcheck = {"solar_raw_untitled_net_total": float(solar_net_total),
             "curves_csv_DUAL_CONTROL_net_total": float(dual_net_total),
             "these_are_the_same_object": bool(abs(solar_net_total - dual_net_total) < 1.0),
             "note": "DUAL_CONTROL in curves.csv is the HTF-TILTED Solar leg (dual_htf applied); "
                     "the raw e10_target reconstruction here is UNTILTED. They are expected to "
                     "differ by design (TiltMult/TiltRescale/ShortHalf) — this is documented, not "
                     "an error, and A1/A2 use curves.csv's own DUAL_CONTROL/DUAL_BLEND75 for all "
                     "portfolio-level (tilted) analysis, and the untitled raw reconstruction only "
                     "for the market-state (A2) variables that need bar-level ATR/sigma access."}
json.dump(selfcheck, open(os.path.join(OUT, "selfcheck.json"), "w"), indent=2)
print("=== SELF-CHECK ===\n" + json.dumps(selfcheck, indent=2), flush=True)

DUAL_C = curves.set_index("sess")["DUAL_CONTROL"]
DUAL_B = curves.set_index("sess")["DUAL_BLEND75"]
CAL = DUAL_C.index
diff = (DUAL_B - DUAL_C).reindex(CAL)

# ============================================================== BMOM (for joint-loss-week gate)
bm = pd.read_parquet(os.path.join(ROOT, "runs", "SMV2B_BMOM_EXEC_AUDIT", "out", "ledger_E2_next_open.parquet"))
bm_daily = bm.groupby("sess")["net_c1_ticks"].sum() * 5.0
bm_daily.index = pd.to_datetime(bm_daily.index).astype(str)
bm_daily = bm_daily.reindex(CAL).fillna(0.0)

# ============================================================== A1: drawdown-complementarity audit
eq = np.cumsum(DUAL_C.to_numpy()); peak = np.maximum.accumulate(eq); dd = peak - eq
n_days = len(CAL)
k1 = max(1, int(0.01 * n_days)); k5 = max(1, int(0.05 * n_days))
worst1_idx = np.argsort(DUAL_C.to_numpy())[:k1]
worst5_idx = np.argsort(DUAL_C.to_numpy())[:k5]
dd_episode_mask = dd > 1e-9
cdar_idx = np.argsort(dd)[::-1][:k5]

a1_worst_days = pd.DataFrame({
    "sess": np.array(CAL)[worst5_idx], "DUAL_CONTROL": DUAL_C.to_numpy()[worst5_idx],
    "DUAL_BLEND75": DUAL_B.to_numpy()[worst5_idx], "diff": diff.to_numpy()[worst5_idx],
}).sort_values("DUAL_CONTROL")
a1_worst_days.to_csv(os.path.join(OUT, "a1_worst_days.csv"), index=False)

n_improved = int((diff.to_numpy()[worst5_idx] > 0).sum())
n_worsened = int((diff.to_numpy()[worst5_idx] < 0).sum())

# weekly
cal_dt = pd.to_datetime(CAL)
weekly_c = pd.Series(DUAL_C.to_numpy(), index=cal_dt).resample("W").sum()
weekly_b = pd.Series(DUAL_B.to_numpy(), index=cal_dt).resample("W").sum()
weekly_bm = pd.Series(bm_daily.to_numpy(), index=cal_dt).resample("W").sum()
weekly_solar_c = pd.Series(DUAL_C.to_numpy(), index=cal_dt).resample("W").sum()  # same as weekly_c (Solar leg IS DUAL here)
joint_loss_weeks = (weekly_c < 0) & (weekly_bm < 0)
a1_joint_loss = pd.DataFrame({
    "week": weekly_c.index[joint_loss_weeks].astype(str),
    "solar_week_net": weekly_c[joint_loss_weeks].to_numpy(),
    "bmom_week_net": weekly_bm[joint_loss_weeks].to_numpy(),
    "blend75_week_net": weekly_b[joint_loss_weeks].to_numpy(),
    "diff_week": (weekly_b - weekly_c)[joint_loss_weeks].to_numpy(),
})
a1_joint_loss.to_csv(os.path.join(OUT, "a1_joint_loss_weeks.csv"), index=False)
n_joint_loss_weeks = int(joint_loss_weeks.sum())
n_joint_loss_improved = int((a1_joint_loss["diff_week"] > 0).sum())

# drawdown episodes (contiguous runs)
ep_id = (~dd_episode_mask).cumsum()
ep_df = pd.DataFrame({"sess": CAL, "in_episode": dd_episode_mask, "ep_id": ep_id, "diff": diff.to_numpy(),
                       "DUAL_CONTROL": DUAL_C.to_numpy()})
episodes = []
for eid, g in ep_df[ep_df["in_episode"]].groupby("ep_id"):
    episodes.append({"ep_id": int(eid), "n_days": len(g), "start": g["sess"].iloc[0], "end": g["sess"].iloc[-1],
                      "control_net_in_ep": float(g["DUAL_CONTROL"].sum()), "diff_in_ep": float(g["diff"].sum())})
ep_out = pd.DataFrame(episodes).sort_values("n_days", ascending=False)
ep_out.to_csv(os.path.join(OUT, "a1_dd_episodes.csv"), index=False)

a1_summary = {
    "worst5pct_days": {"n": k5, "n_improved_by_blend": n_improved, "n_worsened": n_worsened,
                        "mean_diff": float(diff.to_numpy()[worst5_idx].mean())},
    "cdar_tail_episode_days": {"n": k5, "mean_diff": float(diff.to_numpy()[cdar_idx].mean()),
                                "sum_diff": float(diff.to_numpy()[cdar_idx].sum())},
    "joint_solar_bmom_loss_weeks": {"n_weeks": n_joint_loss_weeks, "n_improved": n_joint_loss_improved,
                                     "mean_diff_per_week": float(a1_joint_loss["diff_week"].mean()) if n_joint_loss_weeks else np.nan},
    "top10_longest_dd_episodes": {"n_episodes_examined": min(10, len(ep_out)),
                                   "mean_diff_in_top10_longest": float(ep_out.head(10)["diff_in_ep"].mean()) if len(ep_out) else np.nan,
                                   "n_improved_of_top10": int((ep_out.head(10)["diff_in_ep"] > 0).sum())},
    "full_sample_diff": {"mean": float(diff.mean()), "sum": float(diff.sum())},
}
json.dump(a1_summary, open(os.path.join(OUT, "a1_summary.json"), "w"), indent=2)
print("\n=== A1 SUMMARY ===\n" + json.dumps(a1_summary, indent=2), flush=True)

# ============================================================== A2: market-only mechanism test
close = bars["close"].to_numpy()
sig460 = sm.sigma_series(close)
atr = M5REF.atr_series(bars)
ok = np.isfinite(sig460) & np.isfinite(atr) & (sig460 > 0)
r_bar = np.full(n, np.nan)
r_bar[ok] = atr[ok] / sig460[ok]
r_df = pd.DataFrame({"sess": sess.astype(str), "r": r_bar})
r_by_sess = r_df.groupby("sess")["r"].mean()
r_dev = (r_by_sess - 1.0).reindex(CAL)

terc = pd.qcut(r_dev, 3, labels=["LOW_R_DEV", "MID_R_DEV", "HIGH_R_DEV"])
tercile_df = pd.DataFrame({"sess": CAL, "r_dev": r_dev.to_numpy(), "tercile": terc.to_numpy(),
                            "diff": diff.to_numpy()})
tercile_summary = tercile_df.groupby("tercile", observed=True)["diff"].agg(["mean", "count", "sum"])
tercile_summary.to_csv(os.path.join(OUT, "a2_tercile_test.csv"))
print("\n=== A2 TERCILE TEST (market-only R_dev = ATR/sigma460 - 1) ===")
print(tercile_summary.to_string(), flush=True)

# bootstrap uncertainty on tercile means (paired, block=5)
rng = np.random.default_rng(SEED)
boot_results = {}
for tname in ("LOW_R_DEV", "MID_R_DEV", "HIGH_R_DEV"):
    x = tercile_df.loc[tercile_df["tercile"] == tname, "diff"].to_numpy()
    nb = int(np.ceil(len(x) / BLOCK))
    starts = rng.integers(0, len(x), size=(NBOOT, nb))
    idx = ((starts[:, :, None] + np.arange(BLOCK)[None, None, :]) % len(x)).reshape(NBOOT, -1)[:, :len(x)]
    means = x[idx].mean(axis=1)
    boot_results[tname] = {"point_mean": float(x.mean()), "q05": float(np.quantile(means, 0.05)),
                            "q95": float(np.quantile(means, 0.95)), "P_gt0": float((means > 0).mean())}
json.dump(boot_results, open(os.path.join(OUT, "a2_bootstrap.json"), "w"), indent=2)
print("\n=== A2 BOOTSTRAP ===\n" + json.dumps(boot_results, indent=2), flush=True)

mechanism_confirmed = bool(
    boot_results["HIGH_R_DEV"]["point_mean"] > boot_results["MID_R_DEV"]["point_mean"]
    and boot_results["HIGH_R_DEV"]["point_mean"] > boot_results["LOW_R_DEV"]["point_mean"]
)
a2_verdict = {"mechanism_confirmed": mechanism_confirmed,
              "HIGH_R_DEV_mean_diff": boot_results["HIGH_R_DEV"]["point_mean"],
              "MID_R_DEV_mean_diff": boot_results["MID_R_DEV"]["point_mean"],
              "LOW_R_DEV_mean_diff": boot_results["LOW_R_DEV"]["point_mean"],
              "A3_LICENSED": mechanism_confirmed}
json.dump(a2_verdict, open(os.path.join(OUT, "a2_verdict.json"), "w"), indent=2)
print("\n=== A2 VERDICT ===\n" + json.dumps(a2_verdict, indent=2), flush=True)
print("\n=== A1A2 DONE ===", flush=True)
