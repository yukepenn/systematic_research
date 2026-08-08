"""SMV2AD finalize -- consolidate out/portfolio_blend.csv (spec output name) from
the two sub-test portfolio files, and write out/gates.csv with the kill_or_keep
verdict per the spec's own rule."""
import os, json
import pandas as pd

sys_path_root = os.path.dirname(__file__)
import sys
sys.path.insert(0, sys_path_root)
from common import OUT

p415 = pd.read_csv(os.path.join(OUT, "portfolio_blend_415.csv"))
p415.insert(0, "sub_test", "sub_415_ceiling_sweep")
p416 = pd.read_csv(os.path.join(OUT, "portfolio_blend_416.csv"))
p416.insert(0, "sub_test", "sub_416_extended_cohort")
pd.concat([p415, p416], ignore_index=True).to_csv(os.path.join(OUT, "portfolio_blend.csv"), index=False)

sub415_v = json.load(open(os.path.join(OUT, "sub415_verdict.json")))
sub416_v = json.load(open(os.path.join(OUT, "sub416_verdict.json")))
n_candidates = len(sub415_v["candidates_smax_ticks"]) + len(sub416_v["candidates"])

kill_or_keep = ("CONFIRMED-OPTIMAL-IN-RANGE" if n_candidates == 0 else
                "QUEUE_R2_CONFIRMATION")

gates = pd.DataFrame([
    {"sub_test": "sub_415_ceiling_sweep", "rule": "arm improves standalone Sharpe AND CDaR_0.95 vs 1200t control AND retains >=95% top-10-day sum",
     "arms_tested": 3, "candidates": str(sub415_v["candidates_smax_ticks"]),
     "n_candidates": len(sub415_v["candidates_smax_ticks"])},
    {"sub_test": "sub_416_extended_cohort", "rule": "arm improves standalone Sharpe AND CDaR_0.95 vs 1200t/13-member control AND retains >=95% top-10-day sum",
     "arms_tested": 2, "candidates": str(sub416_v["candidates"]),
     "n_candidates": len(sub416_v["candidates"])},
    {"sub_test": "sub_417_old_regime_screen", "rule": "DIAGNOSTIC, non-adoption; runs only for candidates from 415/416",
     "arms_tested": 0, "candidates": "[]", "n_candidates": 0},
])
gates["kill_or_keep_verdict"] = kill_or_keep
gates["kill_or_keep_rule"] = ("if ZERO arms across sub_415/416 qualify -> CONFIRMED-OPTIMAL-IN-RANGE "
                              "(record in CURRENT_TRUTH, close lead, no third bite without new mechanism). "
                              "If >=1 arm qualifies -> queue R2_CONFIRMATION spec(s) next wave (no adoption this wave).")
gates.to_csv(os.path.join(OUT, "gates.csv"), index=False)
print(gates.to_string(index=False))
print("\nFINAL VERDICT:", kill_or_keep)
