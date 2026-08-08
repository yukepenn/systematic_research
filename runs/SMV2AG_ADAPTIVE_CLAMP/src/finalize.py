"""SMV2AG finalize -- consolidate out/portfolio_blend.csv (spec output name) from
sub_424's portfolio file, and write out/gates.csv with the kill_or_keep verdict
per the spec's own rule."""
import os, json
import pandas as pd

sys_path_root = os.path.dirname(__file__)
import sys
sys.path.insert(0, sys_path_root)
from common import OUT

p424 = pd.read_csv(os.path.join(OUT, "portfolio_blend_424.csv"))
p424.insert(0, "sub_test", "sub_424_adaptive_sweep")
p424.to_csv(os.path.join(OUT, "portfolio_blend.csv"), index=False)

sub424_v = json.load(open(os.path.join(OUT, "sub424_verdict.json")))
n_candidates = len(sub424_v["candidates"])

kill_or_keep = ("CONFIRMED-NOT-BENEFICIAL" if n_candidates == 0 else "QUEUE_R2_CONFIRMATION")

gates = pd.DataFrame([
    {"sub_test": "sub_424_adaptive_sweep",
     "rule": "arm improves standalone Sharpe AND CDaR_0.95 vs 1200t control AND retains >=95% top-10-day sum",
     "arms_tested": 6, "candidates": str(sub424_v["candidate_arms"]),
     "n_candidates": n_candidates},
    {"sub_test": "sub_425_old_regime_screen",
     "rule": "DIAGNOSTIC, non-adoption; runs only for candidates from sub_424",
     "arms_tested": 0, "candidates": "[]", "n_candidates": 0},
])
gates["kill_or_keep_verdict"] = kill_or_keep
gates["kill_or_keep_rule"] = (
    "if ZERO arms across sub_424 qualify -> adaptive clamp ceiling (widen-only construction) "
    "is CONFIRMED-NOT-BENEFICIAL, record in CURRENT_TRUTH, close -- together with SMV2AD this "
    "means BOTH the fixed-ceiling-raise and the adaptive-widen-only ceiling ideas are exhausted; "
    "any future clamp-mechanism idea needs a genuinely different shape (e.g. one that can also "
    "tighten, explicitly out of scope here) to be worth a spec. If >=1 arm qualifies -> queue "
    "R2_CONFIRMATION next wave per the standard two-stage process.")
gates.to_csv(os.path.join(OUT, "gates.csv"), index=False)
print(gates.to_string(index=False))
print("\nFINAL VERDICT:", kill_or_keep)
