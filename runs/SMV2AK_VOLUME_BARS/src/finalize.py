"""SMV2AK finalize -- write out/gates.csv with the kill_or_keep verdict per
the spec's own rule (mirrors runs/SMV2AI_ATR_BLEND/src/finalize.py /
runs/SMV2AD_VOLMULT_CEILING's equivalent)."""
import os, json
import pandas as pd

import sys
sys.path.insert(0, os.path.dirname(__file__))
from common import OUT

sub440_v = json.load(open(os.path.join(OUT, "sub440_verdict.json")))
is_candidate = sub440_v["CANDIDATE"]

old_regime = pd.read_csv(os.path.join(OUT, "old_regime_screen.csv"))
old_regime_status = ("NONE_QUALIFIED" if "status" in old_regime.columns
                      else ("ALL_PASS" if old_regime["screen_pass"].all()
                            else "SOME_FAIL"))

turnover_meta = json.load(open(os.path.join(OUT, "turnover_mechanism_meta.json")))

kill_or_keep = "QUEUE_R2_CONFIRMATION" if is_candidate else "CONFIRMED-NOT-BENEFICIAL"

gates = pd.DataFrame([
    {"sub_test": "sub_438_volume_bar_construction",
     "rule": "DIAGNOSTIC, precedes any signal test; pre-registered V (frozen, not re-tuned after sub_440)",
     "arms_tested": 0, "candidates": "[]", "n_candidates": 0},
    {"sub_test": "sub_439_scale_measurement",
     "rule": "DIAGNOSTIC; pre-registered whole-dev-median R_volbar, N from bar-width distribution, no gate",
     "arms_tested": 0, "candidates": "[]", "n_candidates": 0},
    {"sub_test": "sub_440_ensemble_test",
     "rule": "CANDIDATE iff standalone Sharpe AND CDaR_0.95 improve vs the 3m control AND top-10-day retention >=95%",
     "arms_tested": 1, "candidates": str(["volbar_arm"] if is_candidate else []),
     "n_candidates": int(is_candidate)},
    {"sub_test": "sub_441_old_regime_screen",
     "rule": "DIAGNOSTIC, non-adoption; conditional on sub_440 CANDIDATE; floor net>=incumbent-$10k AND maxDD<=1.25x incumbent, on the DUAL-transformed decision object",
     "arms_tested": int(is_candidate), "candidates": str(["volbar_arm"] if is_candidate else []),
     "n_candidates": int(is_candidate), "old_regime_screen_status": old_regime_status},
    {"sub_test": "sub_442_mechanism_note",
     "rule": "DIAGNOSTIC, always reported; not pass/fail",
     "arms_tested": 1, "candidates": "[]", "n_candidates": 0,
     "pattern_holds_volbar_between_3m_and_5m":
         turnover_meta["pattern_holds_volbar_between_3m_and_5m"]},
])
gates["kill_or_keep_verdict"] = kill_or_keep
gates["kill_or_keep_rule"] = (
    "if the sub_440 arm does NOT qualify as a CANDIDATE -> volume bars are CONFIRMED-NOT-"
    "BENEFICIAL for this system at this calibration, record in CURRENT_TRUTH, close -- no "
    "second bite at THIS SPECIFIC volume threshold without a new mechanism (dollar-volume or "
    "tick-imbalance bars would be a new mechanism, not a re-test). If it DOES qualify -> queue "
    "an R2_CONFIRMATION spec next wave mirroring SMV2AJ's exact gate structure -- no adoption "
    "here.")
gates.to_csv(os.path.join(OUT, "gates.csv"), index=False)
print(gates.to_string(index=False))
print("\nFINAL VERDICT:", kill_or_keep)
