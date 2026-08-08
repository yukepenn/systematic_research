"""Step 0 (MANDATORY): reproduce published 60/40 champion daily curve vs
runs/SMV2H_ONECONTRACT/out/rerank_curves.csv to atol 1e-6. Track BLOCKED if this fails."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from smv2i_lib import OUT, repro_gate

res, DUAL, BM, SIG, vm, cal, champ = repro_gate(atol=1e-6)
df = pd.DataFrame([res])
df.to_csv(os.path.join(OUT, "repro_check.csv"), index=False)
print(df.T.to_string())
print("SIG (DUAL daily std, ddof=1) =", SIG)
if not res["gate_60_40_atol1e-6"]:
    print("REPRO GATE FAILED -> TRACK BLOCKED")
    sys.exit(2)
print("REPRO GATE PASSED")
