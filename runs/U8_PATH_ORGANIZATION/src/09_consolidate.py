"""U8 final consolidation -- master 12-cell table (3 features x 4 outcomes, 20-bar primary) +
verdict inputs. Prints and writes the single table this family's REPORT is built from."""
import os
import json
import pandas as pd

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")

OUTCOME_FILES = {
    "(a) entry-value (net_pnl)": "outcome_a_results.json",
    "(b) hold-continuation (fwd_5)": "outcome_b_results.json",
    "(c) reversal-hazard (P(hazard_10))": "outcome_c_results.json",
    "(d) Product-A scale value (fwd20/contract)": "outcome_d_results.json",
}

rows = []
for outcome_label, fname in OUTCOME_FILES.items():
    with open(os.path.join(OUT, fname)) as fh:
        data = json.load(fh)
    for res in data["primary_20bar"]:
        rows.append({
            "outcome": outcome_label, "feature": res["feature"], "n": res["n_canonical"],
            "raw_spearman": res["raw_spearman"], "resid_spearman": res["residualized_spearman"],
            "delta_r2": res["ols_delta_r2"], "sign_stability": f"{res['n_years_same_sign']}/{res['n_years_total']}",
            "ext_raw": res["extension_raw_spearman"], "ext_resid": res["extension_residualized_spearman"],
            "n_ext": res["n_health_only_extension"],
        })

master = pd.DataFrame(rows)
master["abs_resid_spearman"] = master["resid_spearman"].abs()
master = master.sort_values("abs_resid_spearman", ascending=False)
pd.set_option("display.width", 200)
print("=" * 130)
print("U8 MASTER TABLE -- 12 required cells (3 features x 4 outcomes, 20-bar primary window), ranked by |residualized Spearman|")
print("=" * 130)
print(master.drop(columns=["abs_resid_spearman"]).to_string(index=False))
master.to_csv(os.path.join(OUT, "u8_master_table.csv"), index=False)

with open(os.path.join(OUT, "step0_summary.json")) as fh:
    step0 = json.load(fh)
print("\n" + "=" * 130)
print("STEP 0 REDUNDANCY RECAP")
print("=" * 130)
print(json.dumps(step0, indent=2))

with open(os.path.join(OUT, "righttail_summary.json")) as fh:
    rt = json.load(fh)
print("\n" + "=" * 130)
print("RIGHT-TAIL CHECK RECAP (strongest cell)")
print("=" * 130)
print(json.dumps(rt, indent=2))

print("\nConsolidation complete.")
