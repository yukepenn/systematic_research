"""P0-3: INDEPENDENT IMPLEMENTATION PARITY over all 44 DEVELOPMENT sessions.

Feature-vector and source-timestamp parity here; ACTION parity is completed in the development
runner, which applies the identical fold models to both feature matrices.
"""
from __future__ import annotations

import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "research_sdk"))
import blindguard as BG                                                 # noqa: E402
import esnq_batch as B                                                  # noqa: E402
import esnq_stream as S                                                 # noqa: E402

OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
DEV = os.path.join(RUN, "manifests", "ESNQ_DEV_44.csv")
BLIND = os.path.join(RUN, "manifests", "ESNQ_BLIND_EFFECTIVE_14.csv")
TOL_REL = 1e-9

sess = sorted(BG.load_manifest(DEV))
BG.assert_no_blind_contamination(sess, BLIND, label="parity_44")
BG.assert_no_blind_contamination(sess, os.path.join(RUN, "manifests", "ESNQ_BLIND_15.csv"),
                                 label="parity_44 vs ORIGINAL_15")

rows = []
bparts, sparts = [], []
t00 = time.time()
for i, sd in enumerate(sess, 1):
    b = B.session_features(sd)
    s = S.session_features_stream(sd)
    assert len(b) == len(s) and np.array_equal(b["t"].values, s["t"].values), f"schedule {sd}"
    rec = {"session": sd, "n": len(b)}
    for f in B.FEATURES:
        x, y = b[f].values.astype(float), s[f].values.astype(float)
        m = ~(np.isnan(x) | np.isnan(y))
        rec[f] = float(np.max(np.abs(x[m] - y[m]))) if m.any() else 0.0
        rec[f + "_rel"] = rec[f] / max(1e-12, float(np.nanstd(x)))
        rec[f + "_nanmis"] = int((np.isnan(x) != np.isnan(y)).sum())
    for c in ("long_gross", "short_gross", "max_nq_source_ts", "max_es_source_ts"):
        x, y = b[c].values.astype(float), s[c].values.astype(float)
        m = ~(np.isnan(x) | np.isnan(y))
        rec[c] = float(np.max(np.abs(x[m] - y[m]))) if m.any() else 0.0
    rec["wait_ok_agree"] = int((b["wait_ok"].values == s["wait_ok"].values).sum())
    rows.append(rec)
    bparts.append(b)
    sparts.append(s[B.FEATURES + ["t", "session"]])
    print(f"  [{i:>2}/44] {sd}  worst-rel "
          f"{max(rec[f + '_rel'] for f in B.FEATURES):.2e}  "
          f"src-ts {max(rec['max_nq_source_ts'], rec['max_es_source_ts']):.0f}  "
          f"({time.time() - t00:.0f}s)", flush=True)

P = pd.DataFrame(rows)
P.to_csv(os.path.join(OUT, "parity_44.csv"), index=False)
pd.concat(bparts, ignore_index=True).to_parquet(os.path.join(OUT, "feat_batch.parquet"),
                                                index=False)
pd.concat(sparts, ignore_index=True).to_parquet(os.path.join(OUT, "feat_stream.parquet"),
                                                index=False)
print("")
print("=" * 100)
print("=== P0-3 FEATURE PARITY over 44 sessions")
print("=" * 100)
for f in B.FEATURES:
    print(f"    {f:<16} max abs {P[f].max():>12.4e}   max rel {P[f + '_rel'].max():>12.4e}   "
          f"nan-mismatch {int(P[f + '_nanmis'].sum())}")
for c in ("long_gross", "short_gross", "max_nq_source_ts", "max_es_source_ts"):
    print(f"    {c:<16} max abs {P[c].max():>12.4e}")
print(f"    wait_ok agreement {int(P['wait_ok_agree'].sum()):,} / {int(P['n'].sum()):,}")
ok = (max(P[f + "_rel"].max() for f in B.FEATURES) <= TOL_REL
      and P["max_nq_source_ts"].max() == 0 and P["max_es_source_ts"].max() == 0
      and int(P["wait_ok_agree"].sum()) == int(P["n"].sum())
      and sum(int(P[f + "_nanmis"].sum()) for f in B.FEATURES) == 0)
print(f"\n    >>> FEATURE/TIMESTAMP PARITY {'PASS' if ok else '*** FAIL ***'}")
