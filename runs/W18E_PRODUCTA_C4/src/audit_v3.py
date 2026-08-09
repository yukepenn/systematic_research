"""W18E — Product A C4 audit + the pre-registered inertness falsification test.

Reuses runs/W17_C4_COMPLIANCE/src/c4_audit.py's audit machinery UNMODIFIED (imported, not
copied): position is rebuilt from ORDER ACTIONS, never from the `target` column, which was
the Wave-17 phantom-breach defect.
"""
import os, sys, json
import pandas as pd, numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "runs", "W17_C4_COMPLIANCE", "src"))
import c4_audit as CA

OUT = os.path.join(ROOT, "runs", "W18E_PRODUCTA_C4", "out")
V2 = os.path.join(ROOT, "runs", "SMV2M_MASTER_BUILD", "out", "nt8", "smm_v2_fills.csv")
V3 = os.path.join(OUT, "smm_v3_fills.csv")
DEV_END = pd.Timestamp("2026-05-29 23:59:59")

print("=" * 78)
print("W18E — PRODUCT A C4 AUDIT (pre-registered criterion: ZERO breaches)")
print("=" * 78)

res = {}
print("\n--- BEFORE: SolarWaveSMMaster_v2 ---")
iv2, f2 = CA.intervals_from_fills(V2)
res["v2"] = CA.audit("Product A v2", iv2)

print("\n--- AFTER: SolarWaveSMMaster_v3 ---")
iv3, f3 = CA.intervals_from_fills(V3)
res["v3"] = CA.audit("Product A v3", iv3)

n_breach_v3 = res["v3"][0]
print(f"\n   executions in v2 ledger: {len(f2)}   v3 ledger: {len(f3)}")

# ---------------------------------------------------------- inertness, PER FILL
a = f2.copy(); b = f3.copy()
for d in (a, b):
    d["time"] = pd.to_datetime(d["time"])
a = a[a["time"] <= DEV_END].reset_index(drop=True)
b = b[b["time"] <= DEV_END].reset_index(drop=True)
KEY = ["time", "name", "order_action", "price", "qty"]
ka = a[KEY].astype(str).agg("|".join, axis=1)
kb = b[KEY].astype(str).agg("|".join, axis=1)
sa, sb = pd.Series(ka).value_counts(), pd.Series(kb).value_counts()
only_v2 = (sa - sb.reindex(sa.index).fillna(0)).clip(lower=0)
only_v3 = (sb - sa.reindex(sb.index).fillna(0)).clip(lower=0)
diff = pd.concat([
    pd.DataFrame({"side": "v2_only", "fill": only_v2[only_v2 > 0].index,
                  "n": only_v2[only_v2 > 0].values}),
    pd.DataFrame({"side": "v3_only", "fill": only_v3[only_v3 > 0].index,
                  "n": only_v3[only_v3 > 0].values}),
])
diff.to_csv(os.path.join(OUT, "inertness_diff.csv"), index=False)

summary = {
    "dev_fills_v2": int(len(a)), "dev_fills_v3": int(len(b)),
    "fills_only_in_v2": int(only_v2.sum()), "fills_only_in_v3": int(only_v3.sum()),
    "identical_fills": int(len(a) - only_v2.sum()),
    "pct_fills_differing_v2_basis": float(only_v2.sum() / len(a) * 100),
    "c4_breaches_v2_full_ledger": int(res["v2"][0]),
    "c4_breaches_v3_dev": int(n_breach_v3),
    "PASS_zero_breaches": bool(n_breach_v3 == 0),
}
print("\n=== INERTNESS (per fill, dev window) ===")
print(json.dumps(summary, indent=2))
if len(diff):
    print("\ndiffering fills (all of them):")
    print(diff.to_string(index=False))
json.dump(summary, open(os.path.join(OUT, "c4_audit_v3.json"), "w"), indent=2)
print("\nVERDICT: " + ("PASS" if summary["PASS_zero_breaches"] else "FAIL"))
