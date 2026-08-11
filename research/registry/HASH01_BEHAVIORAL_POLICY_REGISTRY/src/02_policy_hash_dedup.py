"""HASH01 sec2 -- behavioral policy-hash deduplication for the genuine "same finite controller,
many numeric settings" parameter-sweep families identified in HASH01 sec1 (01_reconcile.py /
out/reconciliation.json).

BOOKKEEPING / AUDIT ONLY (campaign directive sec22-27). This distinguishes REPRESENTATIONAL trial
duplication (many raw numeric settings mapping onto the same discrete finite-state behavior) from
genuine distinct architecture-search decisions. It does NOT shrink the campaign's selection-bias
burden and does NOT restore lost preregistration (sec25/sec66: "statistical tools cannot restore
lost preregistration"). No config here is scored, ranked, selected, or promoted.

SCOPE (disclosed, not silently extrapolated):
  The reconciliation phase (out/reconciliation.json, field "parameter_sweep_experiments") flagged
  18 experiment labels across the three registries as pure numeric-parameter sweeps of one finite
  controller. Of those, exactly TWO -- GRID01_SOLAR_RESOLUTION_CONVERGENCE and
  GRID02_ENDPOINT_PERTURBATION -- vary the Solar-ensemble "VolMult" member-scale axis (the `vms`
  list fed into common.build_pend) with an ALREADY-BUILT, self-checked, re-executable Python
  substrate (research/system_master/GRID01_SOLAR_RESOLUTION_CONVERGENCE/src/grid_core.py) that
  this script reuses VERBATIM (build_pend/member_states/member_trades UNMODIFIED; only `vms`
  varies; sm.sigma_series/vol_period=460 unchanged). This is "the VolMult-grid family" the task
  names as the clearest dedup candidate, and it is the family processed below.

  The other 16 flagged sweep labels (W1_S1/W1_S3/W1_S2/W1b/W1C -- vendor NinjaTrader
  SolarWaveRKReplicaV0 UI parameters TM/SM/Slowdown/WWS, executed in NT8, pre-vendor-independence;
  SW01c/DM01/SMV2*/SMV2Z -- the SMV2 python decoder family's own numeric ladders/thresholds, built
  on a DIFFERENT substrate than grid_core.py; PERT01_STRUCTURAL_INVARIANCE -- perturbs THREE
  different axes (VolPeriod/BAND_DAYS/TiltSma), none of which is `vms`, on its own standalone
  substrate) are STRUCTURALLY DIFFERENT finite controllers or require re-deriving/re-executing a
  substrate this session did not build. Per the task's own instruction ("include others only if
  ... confidently classified as pure numeric sweeps of ONE architecture" -- i.e. the SAME one),
  they are NOT folded in here. Folding non-interchangeable controllers into one hash space would
  manufacture false equivalence, exactly what sec25/sec66 warns against. This is disclosed as a
  scope decision, not a silent omission.

  GRID01 and GRID02 are NOT rows in tested_configs.csv or tested_configs_backfill.csv (confirmed
  by grep -- zero matches for "GRID01"/"GRID02" in either file). They are among the post-gap-note,
  outside-runs/ work the reconciliation phase's git-history audit flagged as same-commit
  (src+out+REPORT.md landing atomically) rather than git-verifiably preregistered. That caveat is
  carried forward here unchanged, not resolved by this script.

RAW CONFIGURATIONS PROCESSED (verbatim from run_grid01.py / run_grid02.py; N_raw = 7):
  GRID01 G7             : [6, 10, 14, 18, 22, 26, 30]                      (7 members)
  GRID01 G13 (incumbent) : [6, 8, 10, ..., 30]                             (13 members)
  GRID01 G25             : [6, 7, 8, ..., 30]                              (25 members)
  GRID01 G49             : [6.5, 7.5, ..., 29.5]                           (24 members)
  GRID02 endpoint_5_29   : [5, 7, 9, ..., 29]                              (13 members)
  GRID02 endpoint_6_30   : [6, 8, 10, ..., 30]  == GRID01 G13, RAW-IDENTICAL (13 members)
  GRID02 endpoint_7_31   : [7, 9, 11, ..., 31]                             (13 members)

LEVEL 1 (raw config identity): the `vms` tuple itself -- already known, read directly from the two
  scripts' own GRIDS dicts (no reconstruction needed; these are DIAGNOSTIC-SCIENCE-ONLY grids that
  were mechanically defined and disclosed in the scripts themselves).
LEVEL 2 (finite-state policy identity): SHA256 of the discrete (T, ProductA bar_pos, ProductB
  bar_pos) integer arrays over the CLAUDE.md canonical window (2023-01-01..2025-02-02).
LEVEL 3 (full-history target-vector identity): same triple, SHA256'd over the FULL loaded history
  (every bar through 2026-07-31, grid_core.py's HEALTH_END).
LEVEL 4 (full-history PnL-vector identity / near-identity): SHA256 of the exact full-history daily
  P&L array per product (ticks=1, canonical commission); where hashes differ, pairwise Pearson
  correlation of the daily P&L vectors is reported, with a threshold DISCLOSED HERE, BEFORE ANY
  RESULT IS COMPUTED: r >= 0.99 is called "practically the same" (near-identity). This threshold is
  fixed at this point in the script, before execution, and is not adjusted after seeing outputs.

Effective independent dimension: eigenvalue participation ratio PR = (sum(eig))^2 / sum(eig^2) on
  the N_raw x N_raw daily-P&L Pearson correlation matrix (Gibbs/Bhatt-style participation-ratio
  formula; standard transparent definition, e.g. as used for correlation/covariance spectra in
  statistical physics and finance -- PR of a correlation matrix with unit diagonal ranges from 1
  (all series identical) to N_raw (all series orthogonal)). Reported ALONGSIDE, not instead of, the
  raw and behavioral (Level 2/3/4) counts -- it is one more perspective, not a replacement trial
  count, and it is computed separately for Product A and Product B (different decoders, different
  P&L streams).
"""
import os
import sys
import json
import hashlib

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
GRID01_SRC = os.path.join(ROOT, "research", "system_master",
                           "GRID01_SOLAR_RESOLUTION_CONVERGENCE", "src")
sys.path.insert(0, GRID01_SRC)
import grid_core as G   # noqa: E402  -- reused verbatim, not reimplemented

OUT_DIR = os.path.join(ROOT, "research", "registry", "HASH01_BEHAVIORAL_POLICY_REGISTRY", "out")
os.makedirs(OUT_DIR, exist_ok=True)

# --------------------------------------------------------------------- disclosed threshold (fixed
# BEFORE any correlation is computed -- see module docstring Level 4).
NEAR_IDENTITY_CORR_THRESHOLD = 0.99

# --------------------------------------------------------------------- raw configs (verbatim)
RAW_CONFIGS = [
    # (name, source_experiment, vms_list)
    ("GRID01_G7",           "GRID01_SOLAR_RESOLUTION_CONVERGENCE", [6, 10, 14, 18, 22, 26, 30]),
    ("GRID01_G13_incumbent", "GRID01_SOLAR_RESOLUTION_CONVERGENCE", list(range(6, 31, 2))),
    ("GRID01_G25",           "GRID01_SOLAR_RESOLUTION_CONVERGENCE", list(range(6, 31))),
    ("GRID01_G49",           "GRID01_SOLAR_RESOLUTION_CONVERGENCE",
     [round(6.5 + 1.0 * i, 1) for i in range(24)]),
    ("GRID02_endpoint_5_29", "GRID02_ENDPOINT_PERTURBATION", list(range(5, 30, 2))),
    ("GRID02_endpoint_6_30", "GRID02_ENDPOINT_PERTURBATION", list(range(6, 31, 2))),
    ("GRID02_endpoint_7_31", "GRID02_ENDPOINT_PERTURBATION", list(range(7, 32, 2))),
]
N_RAW = len(RAW_CONFIGS)
print(f"[HASH01/02] N_raw configs to process: {N_RAW} (GRID01 x4 + GRID02 x3, GRID02's "
      f"endpoint_6_30 is the SAME raw vms tuple as GRID01's G13 -- flagged below at Level 1 "
      f"before any hashing)", flush=True)

# --------------------------------------------------------------------- Level 1: raw identity
# Raw-tuple duplicate check -- pure Python equality of the parameter list itself, no execution
# needed. This is the trivial case the task asks to surface: literally the same numbers, tested
# under two different experiment labels.
level1_groups = {}
for name, exp, vms in RAW_CONFIGS:
    key = tuple(vms)
    level1_groups.setdefault(key, []).append(name)
level1_dupe_groups = {k: v for k, v in level1_groups.items() if len(v) > 1}
n_unique_level1 = len(level1_groups)
print(f"[HASH01/02] Level 1 (raw parameter tuple): {n_unique_level1} unique tuples out of "
      f"{N_RAW} raw configs. Raw-identical groups: {list(level1_dupe_groups.values())}", flush=True)


def sha256_of_arrays(*arrays):
    h = hashlib.sha256()
    for a in arrays:
        arr = np.ascontiguousarray(a)
        h.update(arr.dtype.str.encode())
        h.update(np.array(arr.shape, dtype=np.int64).tobytes())
        h.update(arr.tobytes())
    return h.hexdigest()


# --------------------------------------------------------------------- build every raw config
records = []
daily_pnl_A = {}   # name -> pd.Series indexed by session date, full history
daily_pnl_B = {}

for name, exp, vms in RAW_CONFIGS:
    print(f"[HASH01/02] building {name} ({len(vms)} members, source={exp}) ...", flush=True)
    PEND, T, consensus = G.build_grid(vms)
    barposA, bpnlA, _M_A = G.product_a_exec(T, ticks=1)
    posB, barposB, bpnlB, _M_B = G.product_b_exec(T, ticks=1)

    # ---- Level 2: canonical-window discrete policy hash (T, ProductA pos, ProductB pos)
    cm = G.CANON_MASK
    level2_hash = sha256_of_arrays(
        T[cm].astype(np.int64), barposA[cm].astype(np.int64), posB[cm].astype(np.int64))
    level2_hash_T_only = sha256_of_arrays(T[cm].astype(np.int64))
    level2_hash_A_only = sha256_of_arrays(barposA[cm].astype(np.int64))
    level2_hash_B_only = sha256_of_arrays(posB[cm].astype(np.int64))

    # ---- Level 3: full-history discrete target-vector hash (every bar through 2026-07-31)
    fm = G.FULL_MASK
    level3_hash = sha256_of_arrays(
        T[fm].astype(np.int64), barposA[fm].astype(np.int64), posB[fm].astype(np.int64))
    level3_hash_T_only = sha256_of_arrays(T[fm].astype(np.int64))
    level3_hash_A_only = sha256_of_arrays(barposA[fm].astype(np.int64))
    level3_hash_B_only = sha256_of_arrays(posB[fm].astype(np.int64))

    # ---- Level 4: full-history daily PnL vector hash (per product, exact) + correlation matrix
    dA = G.daily_net(bpnlA, fm)          # pd.Series indexed by session date
    dB = G.daily_net(bpnlB, fm)
    daily_pnl_A[name] = dA
    daily_pnl_B[name] = dB
    level4_hash_A = sha256_of_arrays(dA.to_numpy())
    level4_hash_B = sha256_of_arrays(dB.to_numpy())
    level4_hash_combined = sha256_of_arrays(dA.to_numpy(), dB.to_numpy())

    records.append({
        "name": name,
        "source_experiment": exp,
        "n_members": len(vms),
        "vms": vms,
        "level1_raw_tuple_key": str(tuple(vms)),
        "level2_policy_hash_canonical": level2_hash,
        "level2_hash_T_only": level2_hash_T_only,
        "level2_hash_productA_only": level2_hash_A_only,
        "level2_hash_productB_only": level2_hash_B_only,
        "level3_target_vector_hash_full": level3_hash,
        "level3_hash_T_only": level3_hash_T_only,
        "level3_hash_productA_only": level3_hash_A_only,
        "level3_hash_productB_only": level3_hash_B_only,
        "level4_pnl_hash_productA_full": level4_hash_A,
        "level4_pnl_hash_productB_full": level4_hash_B,
        "level4_pnl_hash_combined": level4_hash_combined,
        "productA_net_canonical": float(np.asarray(bpnlA)[cm].sum()),
        "productA_net_full": float(np.asarray(bpnlA)[fm].sum()),
        "productB_net_canonical": float(np.asarray(bpnlB)[cm].sum()),
        "productB_net_full": float(np.asarray(bpnlB)[fm].sum()),
    })

df = pd.DataFrame(records)

# --------------------------------------------------------------------- unique counts, levels 2-4
n_unique_level2 = df["level2_policy_hash_canonical"].nunique()
n_unique_level3 = df["level3_target_vector_hash_full"].nunique()
n_unique_level4_A = df["level4_pnl_hash_productA_full"].nunique()
n_unique_level4_B = df["level4_pnl_hash_productB_full"].nunique()
n_unique_level4_combined = df["level4_pnl_hash_combined"].nunique()

print(f"[HASH01/02] Level 2 (canonical-window discrete policy): {n_unique_level2} unique / {N_RAW} raw", flush=True)
print(f"[HASH01/02] Level 3 (full-history target-vector):        {n_unique_level3} unique / {N_RAW} raw", flush=True)
print(f"[HASH01/02] Level 4 (full-history PnL, ProductA):        {n_unique_level4_A} unique / {N_RAW} raw", flush=True)
print(f"[HASH01/02] Level 4 (full-history PnL, ProductB):        {n_unique_level4_B} unique / {N_RAW} raw", flush=True)
print(f"[HASH01/02] Level 4 (full-history PnL, combined A+B):    {n_unique_level4_combined} unique / {N_RAW} raw", flush=True)


def hash_group_map(colname):
    groups = {}
    for _, row in df.iterrows():
        groups.setdefault(row[colname], []).append(row["name"])
    return {h: members for h, members in groups.items() if len(members) > 1}


dupe_groups_by_level = {
    "level1_raw_tuple": {str(k): v for k, v in level1_dupe_groups.items()},
    "level2_policy_canonical": hash_group_map("level2_policy_hash_canonical"),
    "level3_target_vector_full": hash_group_map("level3_target_vector_hash_full"),
    "level4_pnl_productA_full": hash_group_map("level4_pnl_hash_productA_full"),
    "level4_pnl_productB_full": hash_group_map("level4_pnl_hash_productB_full"),
}
print("[HASH01/02] duplicate groups by level:")
for lvl, groups in dupe_groups_by_level.items():
    print(f"  {lvl}: {groups if groups else '(none -- all 7 raw configs behaviorally distinct at this level)'}")

# --------------------------------------------------------------------- near-identity correlation
# Build the N_raw x N_raw daily-PnL correlation matrix per product (full history, outer-aligned on
# session date; all 7 configs share the identical bar/session timeline from grid_core.py, so this
# is a plain concat + corr, no reindexing surprises expected).
names = [r[0] for r in RAW_CONFIGS]
matA = pd.concat({n: daily_pnl_A[n] for n in names}, axis=1)
matB = pd.concat({n: daily_pnl_B[n] for n in names}, axis=1)
assert matA.isna().sum().sum() == 0 and matB.isna().sum().sum() == 0, \
    "unexpected NaN in daily PnL alignment -- session-date sets differ across configs"

corrA = matA.corr(method="pearson")
corrB = matB.corr(method="pearson")

near_identity_pairs = []
for i in range(N_RAW):
    for j in range(i + 1, N_RAW):
        rA = float(corrA.iloc[i, j])
        rB = float(corrB.iloc[i, j])
        if rA >= NEAR_IDENTITY_CORR_THRESHOLD or rB >= NEAR_IDENTITY_CORR_THRESHOLD:
            near_identity_pairs.append({
                "config_i": names[i], "config_j": names[j],
                "productA_pnl_corr_full": rA, "productB_pnl_corr_full": rB,
                "exact_level4_match_A": bool(df.loc[df.name == names[i], "level4_pnl_hash_productA_full"].iloc[0]
                                              == df.loc[df.name == names[j], "level4_pnl_hash_productA_full"].iloc[0]),
                "exact_level4_match_B": bool(df.loc[df.name == names[i], "level4_pnl_hash_productB_full"].iloc[0]
                                              == df.loc[df.name == names[j], "level4_pnl_hash_productB_full"].iloc[0]),
            })

print(f"[HASH01/02] near-identity pairs (r >= {NEAR_IDENTITY_CORR_THRESHOLD} on either product, "
      f"threshold disclosed a priori in this script's own docstring/constant): "
      f"{len(near_identity_pairs)}", flush=True)
for p in near_identity_pairs:
    print(f"  {p}")


# --------------------------------------------------------------------- effective independent dim
def participation_ratio(corr_matrix: pd.DataFrame) -> dict:
    """PR = (sum(eig))^2 / sum(eig^2). Standard eigenvalue participation-ratio formula for a
    correlation matrix (trace = N, so sum(eig) = N exactly; PR ranges 1..N). Not a novel formula --
    the same construction used for spectral concentration in RMT-style correlation studies."""
    eigvals = np.linalg.eigvalsh(corr_matrix.to_numpy())
    eigvals = np.clip(eigvals, 0.0, None)  # guard tiny negative numerical noise
    s1 = eigvals.sum()
    s2 = (eigvals ** 2).sum()
    pr = float((s1 ** 2) / s2) if s2 > 0 else float("nan")
    return {"eigenvalues": eigvals.tolist(), "sum_eigenvalues": float(s1),
            "sum_sq_eigenvalues": float(s2), "participation_ratio": pr, "n_series": corr_matrix.shape[0]}


pr_A = participation_ratio(corrA)
pr_B = participation_ratio(corrB)
print(f"[HASH01/02] Effective independent dimension (participation ratio), Product A: "
      f"PR={pr_A['participation_ratio']:.3f} out of N_raw={N_RAW}", flush=True)
print(f"[HASH01/02] Effective independent dimension (participation ratio), Product B: "
      f"PR={pr_B['participation_ratio']:.3f} out of N_raw={N_RAW}", flush=True)
pr_effective_avg = float(np.mean([pr_A["participation_ratio"], pr_B["participation_ratio"]]))

# --------------------------------------------------------------------- write outputs
csv_path = os.path.join(OUT_DIR, "policy_hash_results.csv")
df_out = df.drop(columns=["vms"]).copy()
df_out["vms"] = df["vms"].apply(lambda v: ";".join(str(x) for x in v))
df_out.to_csv(csv_path, index=False)
print(f"[HASH01/02] wrote {csv_path} ({len(df_out)} rows)", flush=True)

summary = {
    "scope_note": (
        "VolMult-grid family only (GRID01_SOLAR_RESOLUTION_CONVERGENCE + "
        "GRID02_ENDPOINT_PERTURBATION), reusing grid_core.py verbatim. The other 16 sweep labels "
        "flagged by the reconciliation phase use structurally different controllers (vendor NT8 "
        "RKReplica TM/SM/Slowdown/WWS; the SMV2 python decoder family's own ladders; PERT01's "
        "3-axis VolPeriod/BAND_DAYS/TiltSma OAT) and are NOT folded into this hash space -- doing "
        "so would manufacture false equivalence across non-interchangeable controllers. This is a "
        "disclosed scope decision, not silent extrapolation. Neither GRID01 nor GRID02 appears as "
        "a seq row in tested_configs.csv or tested_configs_backfill.csv (verified by grep, zero "
        "matches); both are post-gap-note, outside-runs/ work with the same-commit "
        "(non-git-verifiably-preregistered) caveat the reconciliation phase already disclosed for "
        "that wave -- unchanged here, not resolved."
    ),
    "n_raw_in_family_processed": N_RAW,
    "family_source_experiments": ["GRID01_SOLAR_RESOLUTION_CONVERGENCE", "GRID02_ENDPOINT_PERTURBATION"],
    "canonical_window": {"start": str(G.CANON_START.date()), "end": str(G.CANON_END.date())},
    "full_history_window": {"start": str(pd.to_datetime(G.SD.min()).date()),
                             "end": str(pd.to_datetime(G.SD.max()).date())},
    "n_unique_level1_raw_tuple": n_unique_level1,
    "n_unique_level2_policy_canonical": int(n_unique_level2),
    "n_unique_level3_target_vector_full": int(n_unique_level3),
    "n_unique_level4_pnl_hash_productA_full": int(n_unique_level4_A),
    "n_unique_level4_pnl_hash_productB_full": int(n_unique_level4_B),
    "n_unique_level4_pnl_hash_combined_full": int(n_unique_level4_combined),
    "duplicate_groups_by_level": dupe_groups_by_level,
    "near_identity_correlation_threshold_disclosed_a_priori": NEAR_IDENTITY_CORR_THRESHOLD,
    "near_identity_pairs": near_identity_pairs,
    "participation_ratio_productA": pr_A,
    "participation_ratio_productB": pr_B,
    "participation_ratio_effective_dim_avg_A_B": pr_effective_avg,
    "participation_ratio_caveat": (
        "PR is reported alongside, not instead of, the raw (N_raw=7) and behavioral (Level 2/3/4 "
        "unique) counts. It is a continuous spectral-concentration statistic over ALL 7 raw "
        "configs' full-history daily P&L correlation matrix (including the GRID01 G13 / GRID02 "
        "endpoint_6_30 raw-identical pair, which necessarily contributes r=1.0 exactly and pulls "
        "PR down from 7 accordingly) -- it is not a replacement trial count and should not be "
        "read as 'the campaign really only ran PR trials'."
    ),
    "correlation_matrix_productA": corrA.round(6).to_dict(),
    "correlation_matrix_productB": corrB.round(6).to_dict(),
    "records": records,
}
json_path = os.path.join(OUT_DIR, "policy_hash_results.json")
with open(json_path, "w") as f:
    json.dump(summary, f, indent=2, default=str)
print(f"[HASH01/02] wrote {json_path}", flush=True)

print("\n[HASH01/02] DONE. Bookkeeping/audit only -- no config selected, ranked, or promoted. "
      "This does not resolve or shrink the registry's selection-bias burden.")
