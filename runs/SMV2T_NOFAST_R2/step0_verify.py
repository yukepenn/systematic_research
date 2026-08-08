"""SMV2T_NOFAST_R2 STEP ZERO — reuse SMV2R's verified simulator cache (no recomputation of
member state machines needed; SMV2R's step0 already verified vote_pend match 100.0000% and
E10 execution to 1.8e-12 $ on this same dev bar substrate). This script:
  1. Loads runs/SMV2R_SOLAR_CORE_1/out/cache_incumbent.npz (pend matrix, 519,714 dev bars x
     13 members) and reconfirms tgt == e10_target(pend) (ALL/incumbent raw core).
  2. Builds the no-FAST (9-member, vm>=14, i.e. "no vm6-12") raw core per spec's mechanical
     member-list rule and cross-checks it bar-for-bar against SMV2R sub_383's own no-FAST
     daily curve (out/daily_cohort_no_FAST.csv) via the verified MNQ E10 executor.
  3. Records the spec-label discrepancy: spec prose says "10-member (no vm6-12)" but the
     VMS list (vm6,8,10,12 removed from 13) is unambiguously 9 members -- identical to
     SMV2R sub_383's no-FAST arm. Not a gate/grid improvisation: the member LIST is fully
     determined by "(no vm6-12)"; only the prose count "10" is wrong (should read 9).

NO data >= 2026-08-01 read. Dev = sessions <= 2026-05-31 (frozen convention).
"""
import sys, os, json, time
import datetime as dt
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "SMV2R_SOLAR_CORE_1"))
import sm01_solarsim as sm
from common_exec import e10_exec  # verified E10 executor, reused verbatim

RUN = os.path.join(ROOT, "runs", "SMV2T_NOFAST_R2")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
DEV_END = dt.date(2026, 5, 31)
SMV2R_OUT = os.path.join(ROOT, "runs", "SMV2R_SOLAR_CORE_1", "out")

t0 = time.time()

bars = sm.load_bars_3m(os.path.join(ROOT, "runs", "AUDIT03_BARS", "nq_3m_2022_2026.csv"))
bars = bars[bars["sess_date"] <= DEV_END].reset_index(drop=True)
print("dev bars:", len(bars), bars.time.min(), "->", bars.time.max(), flush=True)

cache = np.load(os.path.join(SMV2R_OUT, "cache_incumbent.npz"))
pend = cache["pend"]  # (n_bars, 13), verified 100.0000% match to committed substrate in SMV2R step0
assert pend.shape[0] == len(bars), f"cache/bars length mismatch {pend.shape[0]} vs {len(bars)}"

VMS = list(sm.VMS)
assert VMS == list(range(6, 31, 2)) and len(VMS) == 13

# ---- ALL / incumbent raw core: reconfirm tgt reproduction ----
tgt_all = sm.e10_target(pend)
tgt_all_match = bool((tgt_all == cache["tgt"]).all())

# ---- no-FAST raw core: "(no vm6-12)" = drop vm in {6,8,10,12} (the FAST cohort per
#      SMV2R sub_383's own definition) -> 9 members remain (vm14..vm30) ----
FAST = [6, 8, 10, 12]
idx_nofast = [i for i, v in enumerate(VMS) if v not in FAST]
members_nofast = [VMS[i] for i in idx_nofast]
n_members_nofast = len(members_nofast)
tgt_nofast = sm.e10_target(pend[:, idx_nofast])

daily_all, _, _ = e10_exec(bars, tgt_all)
daily_nofast, _, _ = e10_exec(bars, tgt_nofast)

# cross-check ALL core against SMV2R's own cached dev incumbent daily curve
ref_all = pd.read_csv(os.path.join(SMV2R_OUT, "e10_daily_dev_incumbent.csv"))
ref_all["sess"] = pd.to_datetime(ref_all["sess"]).dt.date
da = daily_all.copy(); da["sess"] = pd.to_datetime(da["sess"]).dt.date
j_all = ref_all.merge(da, on="sess", suffixes=("_ref", "_my"))
d_all_max = float(np.abs(j_all["net_ref"] - j_all["net_my"]).max())

# cross-check no-FAST core against SMV2R sub_383's saved no-FAST daily curve
ref_nf = pd.read_csv(os.path.join(SMV2R_OUT, "daily_cohort_no_FAST.csv"))
ref_nf["sess"] = pd.to_datetime(ref_nf["sess"]).dt.date
dn = daily_nofast.copy(); dn["sess"] = pd.to_datetime(dn["sess"]).dt.date
j_nf = ref_nf.merge(dn, on="sess", suffixes=("_ref", "_my"))
d_nf_max = float(np.abs(j_nf["net_ref"] - j_nf["net_my"]).max())

res = {
    "n_dev_bars": int(len(bars)),
    "dev_last_session": str(bars.sess_date.max()),
    "cache_source": "runs/SMV2R_SOLAR_CORE_1/out/cache_incumbent.npz (REUSED, not recomputed)",
    "tgt_all_matches_cache": tgt_all_match,
    "ALL_core_members": VMS, "n_ALL_members": len(VMS),
    "nofast_core_members": members_nofast, "n_nofast_members": n_members_nofast,
    "spec_label_discrepancy": (
        "spec.yaml object_under_test prose says '10-member (no vm6-12)'; the mechanical "
        "rule '(no vm6-12)' removes vm{6,8,10,12} (4 members) from the 13-member ALL "
        "cohort, leaving 9 members (vm14..vm30) -- identical to SMV2R sub_383's no-FAST "
        "arm. The prose count '10' is a labeling error (off by one from the correct 9); "
        "the member LIST itself is unambiguous and used as written. No gate/grid was "
        "improvised -- this is the literal, only-possible reading of '(no vm6-12)'."
    ),
    "ALL_core_dev_daily_max_abs_dev_vs_SMV2R_incumbent_$": d_all_max,
    "ALL_core_sessions_matched": int(len(j_all)), "ALL_core_ref_sessions": int(len(ref_all)),
    "nofast_core_dev_daily_max_abs_dev_vs_SMV2R_sub383_$": d_nf_max,
    "nofast_core_sessions_matched": int(len(j_nf)), "nofast_core_ref_sessions": int(len(ref_nf)),
    "verified": bool(tgt_all_match and d_all_max < 1e-6 and d_nf_max < 1e-6),
    "runtime_s": round(time.time() - t0, 1),
}
with open(os.path.join(OUT, "step0_verify.json"), "w") as f:
    json.dump(res, f, indent=2)
print(json.dumps(res, indent=2))

np.savez_compressed(
    os.path.join(OUT, "cache_dev_cores.npz"),
    pend=pend, tgt_all=tgt_all, tgt_nofast=tgt_nofast, idx_nofast=np.array(idx_nofast),
)
daily_all.to_csv(os.path.join(OUT, "e10_daily_dev_ALL_core.csv"), index=False)
daily_nofast.to_csv(os.path.join(OUT, "e10_daily_dev_noFAST_core.csv"), index=False)
print("cached.", flush=True)
