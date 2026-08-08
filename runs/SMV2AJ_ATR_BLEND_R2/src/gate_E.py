"""SMV2AJ_ATR_BLEND_R2 -- Gate E: rebuild DAYONLY_DUAL6040 with the ATR-blended
DUAL leg (arm_BLEND_75, w=0.75) replacing the incumbent DUAL leg, replicating
runs/SMV2H_ONECONTRACT/rerank.py's 60/40 cell CONSTRUCTION exactly (same BM
component, weights 0.6/0.4, vm() equal-vol rescale mechanism -- SIG re-derived
from the new leg's own daily std, documented below), identical to
runs/SMV2T_NOFAST_R2/gate_E.py's construction. Reuses SMV2AI's own
common.build_portfolio_6040 (verbatim reuse, cross-checked below).

Bar: portfolio dSharpe AND dCDaR point-positive vs the incumbent champion
curve (point-positive, not separately bootstrapped -- identical to SMV2T
gate E precedent).
"""
import sys, os, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "SMV2AJ_ATR_BLEND_R2")
OUT = os.path.join(RUN, "out")
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "SMV2AI_ATR_BLEND", "src"))
from common import load_dev_bars, build_portfolio_6040, champion_curve, vm
from smv2_common import dd_battery

bars = load_dev_bars()
tgt_control = np.load(os.path.join(OUT, "tgt_control_raw_dev.npy"))
tgt_blend75 = np.load(os.path.join(OUT, "tgt_blend75_raw_dev.npy"))

DUAL_control, portfolio_control, SIG_control, Tpp_control = build_portfolio_6040(
    bars, tgt_control, "control_w1.00_rebuild")
DUAL_blend75, portfolio_blend75, SIG_blend75, Tpp_blend75 = build_portfolio_6040(
    bars, tgt_blend75, "arm_BLEND_75_rebuild")
cal = DUAL_control.index

# ---- integrity check: DUAL_blend75 / SIG must match SMV2AI's own portfolio_blend.csv row exactly ----
ai_port = pd.read_csv(os.path.join(ROOT, "runs", "SMV2AI_ATR_BLEND", "out", "portfolio_blend.csv"))
ai_row = ai_port[ai_port["arm"] == "arm_BLEND_75"].iloc[0]
sig_dev = abs(SIG_blend75 - ai_row["SIG_DUAL_leg_std"])
print(f"SIG_blend75 recompute vs SMV2AI portfolio_blend.csv: {SIG_blend75:.6f} vs "
      f"{ai_row['SIG_DUAL_leg_std']:.6f} (|dev|={sig_dev:.8f})", flush=True)
assert sig_dev < 1e-6, "SIG (DUAL leg std) recompute does not match SMV2AI's own value"

champ = champion_curve(cal)
b_control_rebuild = dd_battery(cal, portfolio_control.values, label="DAYONLY_DUAL_BMOM_60_40_CONTROL_REBUILD")
b_blend75 = dd_battery(cal, portfolio_blend75.values, label="DAYONLY_DUAL_BMOM_60_40_BLEND75")
b_champ = dd_battery(cal, champ.values, label="DAYONLY_DUAL_BMOM_60_40_INCUMBENT_CHAMPION")

# cross-check incumbent champion curve reconstruction against rerank_portfolios.csv row
champ_row = pd.read_csv(os.path.join(ROOT, "runs", "SMV2H_ONECONTRACT", "out",
                                      "rerank_portfolios.csv")).set_index("label").loc["DAYONLY_DUAL_BMOM_60_40"]
champ_net_dev = abs(b_champ["net"] - champ_row["net"])
champ_sharpe_dev = abs(b_champ["sharpe"] - champ_row["sharpe"])
print(f"incumbent champion curve cross-check: net |dev|={champ_net_dev:.4f}  "
      f"sharpe |dev|={champ_sharpe_dev:.6f}", flush=True)

# cross-check our own control_rebuild reproduces the champion curve exactly (same leg, same
# construction, should be near-identical -- confirms build_portfolio_6040 == rerank.py's own sim)
control_vs_champ_net_dev = abs(b_control_rebuild["net"] - b_champ["net"])
print(f"control_rebuild vs champion net |dev|={control_vs_champ_net_dev:.4f} "
      f"(sigma460-only DUAL leg rebuilt via build_portfolio_6040 should reproduce the champion)", flush=True)

d_sharpe = b_blend75["sharpe"] - b_champ["sharpe"]
d_cdar = b_champ["CDaR5"] - b_blend75["CDaR5"]   # + = challenger (blend75 rebuild) better
gateE_pass = bool(d_sharpe > 0 and d_cdar > 0)

gate_e = pd.DataFrame([{
    "n_days": len(cal),
    "SIG_old_incumbent_DUAL_std": SIG_control, "SIG_new_blend75_DUAL_std": SIG_blend75,
    "weights_DUAL_BM": "0.6 / 0.4 (unchanged, frozen)",
    "net_incumbent_6040": b_champ["net"], "net_blend75_rebuild_6040": b_blend75["net"],
    "sharpe_incumbent_6040": b_champ["sharpe"], "sharpe_blend75_rebuild_6040": b_blend75["sharpe"],
    "d_sharpe": d_sharpe,
    "CDaR5_incumbent_6040": b_champ["CDaR5"], "CDaR5_blend75_rebuild_6040": b_blend75["CDaR5"],
    "d_CDaR": d_cdar,
    "maxDD_incumbent_6040": b_champ["maxDD_eod"], "maxDD_blend75_rebuild_6040": b_blend75["maxDD_eod"],
    "pass_dSharpe_point_positive": bool(d_sharpe > 0),
    "pass_dCDaR_point_positive": bool(d_cdar > 0),
    "gateE_pass": gateE_pass,
    "sig_recompute_vs_smv2ai_max_abs_dev": sig_dev,
    "champion_curve_reconstruction_net_dev_$": champ_net_dev,
    "champion_curve_reconstruction_sharpe_dev": champ_sharpe_dev,
    "control_rebuild_vs_champion_net_dev_$": control_vs_champ_net_dev,
}])
gate_e.to_csv(os.path.join(OUT, "gate_E.csv"), index=False)
print(gate_e.to_string(index=False), flush=True)

pd.DataFrame({"sess": cal, "PORT_INCUMBENT_6040": champ.values,
              "PORT_BLEND75_6040": portfolio_blend75.values,
              "PORT_CONTROL_REBUILD_6040": portfolio_control.values,
              "DUAL_CONTROL": DUAL_control.values, "DUAL_BLEND75": DUAL_blend75.values,
              }).to_csv(os.path.join(OUT, "gate_E_curves.csv"), index=False)

json.dump({"gateE_pass": gateE_pass, "d_sharpe": d_sharpe, "d_CDaR": d_cdar,
           "SIG_old": SIG_control, "SIG_new": SIG_blend75},
          open(os.path.join(OUT, "gate_E_summary.json"), "w"), indent=2)
print("\ndone gate E", flush=True)
