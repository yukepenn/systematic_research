"""SMV2AI sub_431 -- replace/blend sweep. 4 arms (REPLACE, BLEND_75/50/25),
13-member VMS unchanged, clamp [40,1200]t unchanged. control = incumbent
(w=1.0, pure sigma460), reused VERBATIM from
runs/SMV2AD_VOLMULT_CEILING/out/e10_daily_dev_control_1200.csv (NOT
re-simulated for its standalone battery numbers, per spec).

sig_arm(t) = w*sigma460(t) + (1-w)*sigma_ATR_eff(t), w = weight on incumbent
close-only sigma460:
  arm_REPLACE   : w=0.00 (sigma460 entirely replaced)
  arm_BLEND_75  : w=0.75
  arm_BLEND_50  : w=0.50
  arm_BLEND_25  : w=0.25
  control       : w=1.00 (reused csv; ALSO recomputed here -- see HYPOTHESIS
                  note below -- purely to obtain a tgt array for the
                  portfolio-blend leg and the flip-count/holding-period
                  diagnostic, which the reused csv does not carry; the
                  recompute is verified byte-close to the reused csv before
                  being trusted for anything.)

Verdict rule (CANDIDATE): Sharpe AND CDaR_0.95 improve vs the sigma460-only
control AND top-10-day retention >=95%.
"""
import sys, os, json, time
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from common import (ROOT, OUT, load_dev_bars, build_pend, build_pend_with_flips,
                     e10_exec, metric_row, INCUMBENT_VMS, build_portfolio_6040,
                     champion_curve, dd_battery)
import sm01_solarsim as sm

t0 = time.time()
bars = load_dev_bars()
n = len(bars)

sigma460 = np.load(os.path.join(OUT, "sigma460_dev.npy"))
sigma_ATR_eff = np.load(os.path.join(OUT, "sigma_atr_eff_dev.npy"))

ARMS = {
    "arm_REPLACE": 0.00,
    "arm_BLEND_25": 0.25,
    "arm_BLEND_50": 0.50,
    "arm_BLEND_75": 0.75,
    "control_w1.00": 1.00,
}

# ---------------------------------------------------------------- control: reused csv (verbatim)
control_daily_reused = pd.read_csv(os.path.join(ROOT, "runs", "SMV2AD_VOLMULT_CEILING", "out",
                                                 "e10_daily_dev_control_1200.csv"))
control_daily_reused["sess"] = pd.to_datetime(control_daily_reused["sess"]).dt.date

rows = []
dailies = {}
tgts = {}
flip_stats = {}

for label, w in ARMS.items():
    sig_arm = w * sigma460 + (1.0 - w) * sigma_ATR_eff
    pend, flips = build_pend_with_flips(bars, sig_arm, INCUMBENT_VMS, smax_ticks=1200.0, smin_ticks=40.0)
    tgt = sm.e10_target(pend)
    daily, bar_pos, bar_pnl = e10_exec(bars, tgt)
    dailies[label] = daily
    tgts[label] = tgt

    if label == "control_w1.00":
        # cross-check: recomputed control must match the reused csv (verifies
        # w=1.00 sig_arm == sigma460 exactly and the pipeline reproduces the
        # spec's frozen ground truth before being trusted for the portfolio leg)
        j = control_daily_reused.merge(
            daily.assign(sess=pd.to_datetime(daily["sess"]).dt.date if daily["sess"].dtype == object
                         else daily["sess"]),
            on="sess", suffixes=("_reused", "_recompute"))
        max_dev = float(np.abs(j["net_reused"] - j["net_recompute"]).max())
        print(f"control cross-check: recomputed vs reused csv, {len(j)}/{len(control_daily_reused)} "
              f"sessions matched, max|dev|=${max_dev:.6f}", flush=True)
        assert max_dev < 1.0, f"control recompute does not match reused csv (max abs dev ${max_dev:.2f})"
        r = metric_row("control_w1.00_recomputed", daily, tgt)
    else:
        r = metric_row(label, daily, tgt)
    r["w_sigma460_weight"] = w
    rows.append(r)

    # flip-count / holding-period diagnostic (member-level trend flips from
    # sm.member_states' `flip` array; HYPOTHESIS/interpretive call -- see report)
    n_flips_per_member = (flips != 0).sum(axis=0)  # (13,)
    total_flips = int(n_flips_per_member.sum())
    mean_flips_per_member = float(n_flips_per_member.mean())
    mean_holding_bars = float(n / mean_flips_per_member) if mean_flips_per_member > 0 else np.nan
    n_sessions = bars["sess_date"].nunique()
    bars_per_session = n / n_sessions
    flip_stats[label] = {
        "arm": label if label != "control_w1.00" else "control_w1.00_recomputed",
        "w_sigma460_weight": w,
        "total_member_flips": total_flips,
        "mean_flips_per_member": mean_flips_per_member,
        "mean_holding_period_bars": mean_holding_bars,
        "mean_holding_period_sessions": mean_holding_bars / bars_per_session,
    }
    print(f"{label}: net={r['net']:.0f} sharpe={r['sharpe']:.3f} CDaR={r['CDaR_0.95']:.0f} "
          f"turnover%={r['turnover_tgt_change_bars_pct']:.3f} mean_flips/member={mean_flips_per_member:.1f} "
          f"mean_holding_bars={mean_holding_bars:.1f}", flush=True)

df = pd.DataFrame(rows)

# ---------------------------------------------------------------- top10-day retention vs control
# use the REUSED control csv (spec ground truth) as the retention baseline
base = control_daily_reused.set_index("sess")["net"]
top10 = base.nlargest(10)
ret = {}
for label in ARMS:
    d = dailies[label].copy()
    d["sess"] = pd.to_datetime(d["sess"]).dt.date if d["sess"].dtype == object else d["sess"]
    d = d.set_index("sess")["net"]
    ret[label] = float(d.reindex(top10.index).fillna(0).sum())
ret_control = ret["control_w1.00"]
df["arm_key"] = list(ARMS.keys())
df["pnl_on_control_top10_days"] = df["arm_key"].map(ret)
df["retention_control_top10"] = df["pnl_on_control_top10_days"] / ret_control

ctrl_row = df[df.arm_key == "control_w1.00"].iloc[0]
df["d_sharpe_vs_control"] = df["sharpe"] - ctrl_row["sharpe"]
df["d_CDaR_vs_control"] = ctrl_row["CDaR_0.95"] - df["CDaR_0.95"]  # + = challenger better (lower CDaR)
df["candidate"] = (
    (df["sharpe"] > ctrl_row["sharpe"]) &
    (df["CDaR_0.95"] < ctrl_row["CDaR_0.95"]) &
    (df["retention_control_top10"] >= 0.95) &
    (df["arm_key"] != "control_w1.00")
)

df = df.drop(columns=["arm_key"])
df.to_csv(os.path.join(OUT, "replace_blend_sweep.csv"), index=False)
for label, d in dailies.items():
    d.to_csv(os.path.join(OUT, f"daily_{label}.csv"), index=False)
print("\n=== replace_blend_sweep.csv ===")
print(df.to_string(index=False), flush=True)

# ---------------------------------------------------------------- churn comparison
churn_df = pd.DataFrame(list(flip_stats.values()))
ctrl_flip = churn_df[churn_df.w_sigma460_weight == 1.00].iloc[0]
churn_df["d_mean_flips_per_member_vs_control"] = churn_df["mean_flips_per_member"] - ctrl_flip["mean_flips_per_member"]
churn_df["d_mean_holding_bars_vs_control"] = churn_df["mean_holding_period_bars"] - ctrl_flip["mean_holding_period_bars"]
churn_df["pct_change_flips_vs_control"] = (
    (churn_df["mean_flips_per_member"] / ctrl_flip["mean_flips_per_member"] - 1.0) * 100)
churn_df.to_csv(os.path.join(OUT, "churn_comparison.csv"), index=False)
print("\n=== churn_comparison.csv ===")
print(churn_df.to_string(index=False), flush=True)

# ---------------------------------------------------------------- portfolio blend
port_rows = []
port_curves = {"sess": None}
champ = None
for label in ARMS:
    plabel = label if label != "control_w1.00" else "control_w1.00_recomputed"
    DUAL, portfolio, SIG, Tpp = build_portfolio_6040(bars, tgts[label], plabel)
    cal = DUAL.index
    if champ is None:
        champ = champion_curve(cal)
        port_curves["sess"] = cal
    b_port = dd_battery(cal, portfolio.values, label=f"PORT_{plabel}")
    b_champ = dd_battery(cal, champ.values, label="PORT_INCUMBENT_CHAMPION")
    d_sharpe = b_port["sharpe"] - b_champ["sharpe"]
    d_cdar = b_champ["CDaR5"] - b_port["CDaR5"]
    port_rows.append({
        "arm": plabel, "w_sigma460_weight": ARMS[label],
        "SIG_DUAL_leg_std": SIG,
        "net_portfolio_6040": b_port["net"], "sharpe_portfolio_6040": b_port["sharpe"],
        "CDaR5_portfolio_6040": b_port["CDaR5"], "maxDD_portfolio_6040": b_port["maxDD_eod"],
        "net_champion_6040": b_champ["net"], "sharpe_champion_6040": b_champ["sharpe"],
        "CDaR5_champion_6040": b_champ["CDaR5"], "maxDD_champion_6040": b_champ["maxDD_eod"],
        "d_sharpe_vs_champion": d_sharpe, "d_CDaR_vs_champion": d_cdar,
        "portfolio_beats_champion": bool(d_sharpe > 0 and d_cdar > 0),
    })
    port_curves[f"DUAL_{plabel}"] = DUAL.values
    port_curves[f"PORT_{plabel}"] = portfolio.values
    print(f"portfolio {plabel}: SIG={SIG:.1f} net={b_port['net']:.0f} sharpe={b_port['sharpe']:.3f} "
          f"vs champion sharpe={b_champ['sharpe']:.3f}", flush=True)

pdf = pd.DataFrame(port_rows)
pdf.to_csv(os.path.join(OUT, "portfolio_blend.csv"), index=False)
pd.DataFrame(port_curves).to_csv(os.path.join(OUT, "portfolio_curves_431.csv"), index=False)
print("\n=== portfolio_blend.csv ===")
print(pdf.to_string(index=False), flush=True)

candidates = df[df.candidate]["arm"].tolist()
verdict = {
    "arms": list(ARMS.keys()), "candidates": candidates,
    "any_candidate": bool(len(candidates) > 0),
    "runtime_s": round(time.time() - t0, 1),
}
with open(os.path.join(OUT, "sub431_verdict.json"), "w") as f:
    json.dump(verdict, f, indent=2)
print("\nsub_431 CANDIDATEs:", candidates, flush=True)
print("done sub_431", round(time.time() - t0, 1), "s", flush=True)
