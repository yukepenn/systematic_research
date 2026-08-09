"""U8B final consolidation -- master 18-cell Stage-1 table (3 features x 6 outcomes) + 12-cell
Stage-2 interaction table (2 independent features x 6 outcomes) + too-good-to-be-true gate scan
across every cell (Stage 1 AND Stage 2) + verdict inputs."""
import os
import json
import numpy as np
import pandas as pd

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")

STAGE1_SOURCES = {
    "(a) MFE": ("outcomes_abde_stage1.json", "a_mfe"),
    "(b) MAE magnitude": ("outcomes_abde_stage1.json", "b_mae"),
    "(d) bars-to-MFE": ("outcomes_abde_stage1.json", "d_bars_to_mfe"),
    "(e) P(top-decile winner)": ("outcomes_abde_stage1.json", "e_top_decile"),
    "(c) reversal hazard": ("outcome_c_stage1.json", None),
    "(f) Product-A scale value": ("outcome_f_stage1.json", None),
}
STAGE2_SOURCES = {
    "(a) MFE": ("outcomes_abde_stage2.json", "a_mfe"),
    "(b) MAE magnitude": ("outcomes_abde_stage2.json", "b_mae"),
    "(d) bars-to-MFE": ("outcomes_abde_stage2.json", "d_bars_to_mfe"),
    "(e) P(top-decile winner)": ("outcomes_abde_stage2.json", "e_top_decile"),
    "(c) reversal hazard": ("outcome_c_stage2.json", None),
    "(f) Product-A scale value": ("outcome_f_stage2.json", None),
}

rows1 = []
for outcome_label, (fname, key) in STAGE1_SOURCES.items():
    with open(os.path.join(OUT, fname)) as fh:
        data = json.load(fh)
    recs = data[key] if key else data
    for res in recs:
        rows1.append({
            "outcome": outcome_label, "feature": res["feature"], "n": res["n_canonical"],
            "raw_spearman": res["raw_spearman"], "resid_spearman": res["residualized_spearman"],
            "delta_r2": res["ols_delta_r2"], "sign_stability": f"{res['n_years_same_sign']}/{res['n_years_total']}",
            "ext_raw": res["extension_raw_spearman"], "ext_resid": res["extension_residualized_spearman"],
            "n_ext": res["n_health_only_extension"],
        })

master1 = pd.DataFrame(rows1)
master1["abs_resid_spearman"] = master1["resid_spearman"].abs()
master1 = master1.sort_values("abs_resid_spearman", ascending=False)
pd.set_option("display.width", 220)
print("=" * 140)
print("U8B MASTER STAGE-1 TABLE -- 18 cells (3 transition features x 6 outcomes), ranked by |residualized Spearman|")
print("=" * 140)
print(master1.drop(columns=["abs_resid_spearman"]).to_string(index=False))
master1.to_csv(os.path.join(OUT, "u8b_master_stage1_table.csv"), index=False)

rows2 = []
for outcome_label, (fname, key) in STAGE2_SOURCES.items():
    with open(os.path.join(OUT, fname)) as fh:
        data = json.load(fh)
    recs = data[key] if key else data
    for res in recs:
        rows2.append({
            "outcome": outcome_label, "feature": res["feature"], "n": res["n"],
            "r2_additive": res["r2_additive"], "r2_interaction": res["r2_interaction"],
            "delta_r2_interaction": res["delta_r2_interaction"],
            "interaction_coef": res["interaction_coef"], "interaction_t": res["interaction_t"],
        })
master2 = pd.DataFrame(rows2)
master2["abs_delta_r2_interaction"] = master2["delta_r2_interaction"].abs()
master2 = master2.sort_values("abs_delta_r2_interaction", ascending=False)
print("\n" + "=" * 140)
print("U8B MASTER STAGE-2 TABLE -- 12 cells (2 independent transition features x 6 outcomes), interaction with |M|, ranked by |delta R^2(interaction)|")
print("=" * 140)
print(master2.drop(columns=["abs_delta_r2_interaction"]).to_string(index=False))
master2.to_csv(os.path.join(OUT, "u8b_master_stage2_table.csv"), index=False)

# too-good-to-be-true gate: scan every delta_r2 (Stage 1) and delta_r2_interaction (Stage 2)
print("\n" + "=" * 140)
print("TOO-GOOD-TO-BE-TRUE GATE SCAN (threshold: delta R^2 > 0.02)")
print("=" * 140)
max_dr2_stage1 = master1["delta_r2"].abs().max()
max_dr2_stage2 = master2["delta_r2_interaction"].abs().max()
print(f"max |delta R^2| Stage 1 (18 cells): {max_dr2_stage1:.5f}  "
      f"({'FLAG - STOP AND INVESTIGATE' if max_dr2_stage1 > 0.02 else 'below threshold, no flag'})")
print(f"max |delta R^2(interaction)| Stage 2 (12 cells): {max_dr2_stage2:.5f}  "
      f"({'FLAG - STOP AND INVESTIGATE' if max_dr2_stage2 > 0.02 else 'below threshold, no flag'})")

with open(os.path.join(OUT, "step0_summary.json")) as fh:
    step0 = json.load(fh)
print("\n" + "=" * 140)
print("STEP 0 REDUNDANCY RECAP")
print("=" * 140)
print(json.dumps(step0, indent=2))

with open(os.path.join(OUT, "righttail_summary.json")) as fh:
    rt = json.load(fh)
print("\n" + "=" * 140)
print("RIGHT-TAIL CHECK RECAP (strongest cell)")
print("=" * 140)
print(json.dumps(rt, indent=2))

with open(os.path.join(OUT, "session_interaction.json")) as fh:
    sess = json.load(fh)
print("\n" + "=" * 140)
print("SESSION INTERACTION RECAP (strongest cell)")
print("=" * 140)
for name in ["blended", "RTH", "ETH"]:
    r = sess[name]
    print(f"  {name:10s} n={r['n_canonical']:5d}  raw_rho={r['raw_spearman']:+.4f}  "
          f"resid_rho={r['residualized_spearman']:+.4f}  delta_r2={r['ols_delta_r2']:+.5f}")

verdict = {
    "step0_any_redundant": step0["any_flagged_redundant_gt_0.7"],
    "step0_max_abs_rho": step0["max_abs_rho_vs_level_or_momentum"],
    "mirror_rho_reversal_vs_run_persistence_transition": step0["mirror_check_reversal_rate_vs_run_persistence_transition_rho"],
    "strongest_cell": "(a) MFE: reversal_rate_transition vs mfe_final",
    "strongest_resid_spearman": float(master1.iloc[0]["resid_spearman"]),
    "strongest_delta_r2": float(master1.iloc[0]["delta_r2"]),
    "strongest_sign_stability": master1.iloc[0]["sign_stability"],
    "max_dr2_stage1": float(max_dr2_stage1),
    "max_dr2_stage2": float(max_dr2_stage2),
    "tgtbt_gate_triggered": bool(max_dr2_stage1 > 0.02 or max_dr2_stage2 > 0.02),
    "righttail_top20_excluded_by_hard_filter": rt["top20_n_excluded_by_hard_good_filter"],
    "righttail_top20_bad_tercile_rate": rt["top20_n_bad_tercile"] / 20,
    "righttail_population_bad_tercile_rate": rt["population_bad_tercile_rate"],
    "session_rth_delta_r2": sess["RTH"]["ols_delta_r2"],
    "session_eth_delta_r2": sess["ETH"]["ols_delta_r2"],
}
with open(os.path.join(OUT, "u8b_verdict_inputs.json"), "w") as fh:
    json.dump(verdict, fh, indent=2)
print("\n" + "=" * 140)
print("VERDICT INPUTS")
print("=" * 140)
print(json.dumps(verdict, indent=2))
print("\nConsolidation complete.")
