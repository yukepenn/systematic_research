"""SMV2AH sub_428 -- old-regime screen (DIAGNOSTIC, conditional on >=1 CANDIDATE
from sub_427, identical contingency structure to SMV2AD/SMV2AG). sub_427
produced ZERO CANDIDATEs across all 16 cells (out/sub427_verdict.json) --
every cell that beat the no-breaker control on CDaR_0.95/worst-day failed to
beat its own matched-placebo's median (gate2), meaning the apparent benefit
is attributable to halting-at-all (any random same-count halt), not to
halting AT THE RIGHT TIME. There is therefore NOTHING TO SCREEN this wave.
Disclosed explicitly (status=NONE_QUALIFIED), not silently skipped, per spec.
"""
import os
import sys
import json

import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from common_ah import OUT

verdict = json.load(open(os.path.join(OUT, "sub427_verdict.json")))
n_candidates = verdict["n_candidates"]

if n_candidates == 0:
    row = {
        "status": "NONE_QUALIFIED",
        "reason": ("sub_427: 0/16 cells qualified as CANDIDATE. Every cell that improved "
                   "CDaR_0.95 AND worst-day vs the no-circuit-breaker control (gate 1) "
                   "FAILED gate 2 (beat its own matched-placebo's median CDaR_0.95 AND "
                   "worst-day) -- see out/gates.csv column gate2_beats_placebo_median_CDaR_"
                   "and_worstday, FALSE in all 16 rows. The apparent tail protection from "
                   "halting at the threshold-crossing bar is statistically indistinguishable "
                   "from (in most cells, WORSE than) halting the same number of sessions at "
                   "a RANDOM bar drawn from the same session's own range -- i.e. the benefit "
                   "comes from halting-at-all (removing exposure for the remainder of a "
                   "session, unconditionally), not from the circuit breaker's own timing "
                   "information. Old-regime screen is conditional on >=1 CANDIDATE; none "
                   "exists this wave, so nothing is rebuilt on the SM06 2006-2021 hist "
                   "substrate."),
        "sub427_n_cells": verdict["n_cells"],
        "sub427_n_candidates": n_candidates,
    }
    pd.DataFrame([row]).to_csv(os.path.join(OUT, "old_regime_screen.csv"), index=False)
    print(json.dumps(row, indent=2))
    print("sub_428: NONE_QUALIFIED -- no candidates to screen.", flush=True)
else:
    raise NotImplementedError(
        "sub_427 produced >=1 CANDIDATE -- old-regime rebuild machinery was not "
        "needed/implemented this wave (SM06 2006-2021 hist substrate + candidate "
        "cell's exact halt policy, floor net>=incumbent-$10k AND maxDD<=1.25x "
        "incumbent). Implement per SMV2AD/sub417_old_regime.py's CANDIDATE_SCREEN "
        "pattern before proceeding -- do not silently skip a real candidate.")
