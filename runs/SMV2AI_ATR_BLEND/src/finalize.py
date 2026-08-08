"""SMV2AI finalize -- write out/gates.csv with the kill_or_keep verdict per
the spec's own rule (mirrors runs/SMV2AD_VOLMULT_CEILING/src/finalize.py /
runs/SMV2AG_ADAPTIVE_CLAMP's equivalent)."""
import os, json
import pandas as pd

import sys
sys.path.insert(0, os.path.dirname(__file__))
from common import OUT

sub431_v = json.load(open(os.path.join(OUT, "sub431_verdict.json")))
n_candidates = len(sub431_v["candidates"])

old_regime = pd.read_csv(os.path.join(OUT, "old_regime_screen.csv"))
old_regime_status = ("NONE_QUALIFIED" if "status" in old_regime.columns
                      else ("ALL_PASS" if old_regime["screen_pass"].all()
                            else "SOME_FAIL"))

kill_or_keep = ("CONFIRMED-NOT-BENEFICIAL" if n_candidates == 0 else
                "QUEUE_R2_CONFIRMATION")

gates = pd.DataFrame([
    {"sub_test": "sub_430_atr_construction_and_scale_measurement",
     "rule": "DIAGNOSTIC, precedes re-simulation; pre-registered whole-dev-median R_atr, no gate",
     "arms_tested": 0, "candidates": "[]", "n_candidates": 0},
    {"sub_test": "sub_431_replace_and_blend_sweep",
     "rule": "arm improves standalone Sharpe AND CDaR_0.95 vs the sigma460-only (w=1.0) control AND retains >=95% top-10-day sum",
     "arms_tested": 4, "candidates": str(sub431_v["candidates"]),
     "n_candidates": n_candidates},
    {"sub_test": "sub_432_old_regime_screen",
     "rule": "DIAGNOSTIC, non-adoption; runs only for candidates from sub_431; floor net>=incumbent-$10k AND maxDD<=1.25x incumbent",
     "arms_tested": n_candidates, "candidates": str(sub431_v["candidates"]),
     "n_candidates": n_candidates,
     "old_regime_screen_status": old_regime_status},
])
gates["kill_or_keep_verdict"] = kill_or_keep
gates["kill_or_keep_rule"] = (
    "if ZERO arms across sub_431 qualify -> ATR/range-blended threshold estimation is "
    "CONFIRMED-NOT-BENEFICIAL for this system, record in CURRENT_TRUTH, close -- no third "
    "bite at this specific mechanism without a new construction. If >=1 arm qualifies -> "
    "queue an R2_CONFIRMATION spec (SMV2T-style full battery) next wave -- no adoption here.")
gates.to_csv(os.path.join(OUT, "gates.csv"), index=False)
print(gates.to_string(index=False))
print("\nFINAL VERDICT:", kill_or_keep)
