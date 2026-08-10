"""U6B risk_panel Part 1 (audit) + Part 2 (capital frontier, sec6).

PART 1 AUDIT (executed and printed BEFORE the frontier is built, per directive instruction not
to pick a capital convention after seeing which one flatters a candidate):
  (a) locates the existing house capital-map methodology (capital_needed = p95(bootstrapped
      max-$-drawdown)/thr, runs/PRODUCTB_ONECONTRACT_FINAL/build_parity_and_metrics.py::capital_map)
      and its own prior application to Product A itself
      (runs/W17_C4_COMPLIANCE/out/v1f_capital_map_productA.csv).
  (b) numerically re-verifies O1_OBJECTIVE.md section 2.6's scaling identity ("J at L=0.5/C=100k
      == J at L=1.0/C=200,045") -- on THIS run's own object (U6B CONTROL, genuine-MNQ canonical
      series), not merely citing the prior document's claim about a different series.

PART 2: capital frontier at fixed leverage=1.0, PRE-REGISTERED grid {50k,75k,100k,150k,200k,
300k,500k}, applied identically to CONTROL/F0.5/F0.7 (genuine-MNQ, canonical window <=2026-05-29,
enforced automatically by primary_objective_v2's own dev_window="truncate" truncation at
DEV_END=2026-05-29). Built EXCLUSIVELY through PO2.leverage_curve() (capital held at a fixed
reference, leverage swept), per the task's explicit instruction to reuse leverage_curve as the
capital-sweep tool rather than writing new capital-sweep machinery -- the reparametrization is
the audited identity of (b) above.

Also builds the "equal historical stressed-DD fraction" alternative capital normalization
(candidate's own certified maxDD_eod / 0.25) and Product B (NQ, MNQ) context-only rows.
"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
import primary_objective_v2 as PO2

RUN = os.path.join(ROOT, "runs", "U6B_PRODUCT_A_SCALE_RATE")
OUT = os.path.join(RUN, "risk_panel", "out")
os.makedirs(OUT, exist_ok=True)

CAPITAL_GRID = [50_000.0, 75_000.0, 100_000.0, 150_000.0, 200_000.0, 300_000.0, 500_000.0]
REF_CAPITAL = 100_000.0   # leverage_curve's fixed-capital anchor; house default C=$100k (O1 sec1.1)

CANDIDATES = {
    "CONTROL": os.path.join(RUN, "out", "CONTROL_daily_GENUINE_MNQ.csv"),
    "F0.5": os.path.join(RUN, "out", "F0.5_daily_GENUINE_MNQ.csv"),
    "F0.7": os.path.join(RUN, "out", "F0.7_daily_GENUINE_MNQ.csv"),
}
# own certified canonical maxDD_eod, GENUINE MNQ pricing, from out/u6b_mnq_grid_battery.csv
# (row tag == f"{candidate}_canonical_GENUINE")
OWN_MAXDD_EOD = {"CONTROL": 17069.89999999918, "F0.5": 17390.80000000249, "F0.7": 16977.30000000284}

print("=" * 100)
print("PART 1a -- existing capital-map methodology audit")
print("=" * 100)
print("House rule (runs/PRODUCTB_ONECONTRACT_FINAL/build_parity_and_metrics.py::capital_map):")
print("    capital_needed = p95(bootstrapped max-$-drawdown) / thr")
v1f = pd.read_csv(os.path.join(ROOT, "runs", "W17_C4_COMPLIANCE", "out", "v1f_capital_map_productA.csv"))
v1f_thr25 = v1f[(v1f["stress_mult"] == 1.0) & (v1f["thr"] == 0.25)]
print("Already computed for Product A itself (runs/W17_C4_COMPLIANCE/out/v1f_capital_map_productA.csv, "
      "stress_mult=1.0, thr=0.25 -- the O1 pre-registered tolerance):")
print(v1f_thr25.to_string(index=False))
print(f"-> range across the 3 house bootstrap methods: "
      f"${v1f_thr25['capital_needed'].min():,.0f} .. ${v1f_thr25['capital_needed'].max():,.0f}")
print(f"-> our pre-registered grid {CAPITAL_GRID} spans this range on both sides "
      "(clearly-thin $50k/$75k below it, clearly-generous $300k/$500k above it).")

print()
print("=" * 100)
print("PART 1b -- numerical re-verification of the O1 sec2.6 scaling identity, on U6B CONTROL "
      "genuine-MNQ canonical series")
print("=" * 100)
ctrl_path = CANDIDATES["CONTROL"]
r_a = PO2.primary_objective(ctrl_path, capital=100_000.0, leverage=0.5, leverage_mode="fixed_fraction",
                             label="identity_check_L0.5_C100k")
r_b = PO2.primary_objective(ctrl_path, capital=200_000.0, leverage=1.0, leverage_mode="fixed_fraction",
                             label="identity_check_L1.0_C200k")
for k in ["objective_J", "ce_log_growth_ann", "p_ruin", "J_worst_over_methods"]:
    va, vb = r_a["primary"][k], r_b["primary"][k]
    print(f"  {k}: L=0.5/C=$100,000 -> {va!r}   |   L=1.0/C=$200,000 -> {vb!r}   "
          f"|diff|={abs(va - vb):.3e}")
identity_diff = abs(r_a["primary"]["objective_J"] - r_b["primary"]["objective_J"])
identity_holds = identity_diff < 1e-9
print(f"IDENTITY {'CONFIRMED' if identity_holds else 'FAILED'} (|J diff| = {identity_diff:.3e}, "
      "bit-identical to within float roundoff -- both calls draw from the SAME seeded bootstrap "
      "generator at the SAME n, so this is not merely 'close', it is the same computation reached "
      "two ways). This licenses using PO2.leverage_curve(capital=REF, grid=[REF/c for c in "
      "CAPITAL_GRID]) as the capital-frontier engine below: it IS primary_objective(capital=c, "
      "leverage=1.0) for every c in CAPITAL_GRID, not an approximation of it.")

audit = {
    "capital_map_house_rule": "capital_needed = p95(bootstrapped max-$-drawdown) / thr "
                              "(runs/PRODUCTB_ONECONTRACT_FINAL/build_parity_and_metrics.py::capital_map)",
    "capital_map_productA_at_thr0.25_stress1.0": v1f_thr25.to_dict(orient="records"),
    "scaling_identity_check": {
        "L0.5_C100000": {k: r_a["primary"][k] for k in
                          ["objective_J", "ce_log_growth_ann", "p_ruin", "J_worst_over_methods"]},
        "L1.0_C200000": {k: r_b["primary"][k] for k in
                          ["objective_J", "ce_log_growth_ann", "p_ruin", "J_worst_over_methods"]},
        "abs_diff_J": identity_diff, "identity_confirmed": bool(identity_holds),
    },
    "capital_grid": CAPITAL_GRID, "ref_capital_for_leverage_curve": REF_CAPITAL,
}
with open(os.path.join(OUT, "part1_audit.json"), "w") as f:
    json.dump(audit, f, indent=2, default=float)

print()
print("=" * 100)
print("PART 2 -- capital frontier via PO2.leverage_curve (fixed leverage=1.0 equivalent), "
      "grid = " + str(CAPITAL_GRID))
print("=" * 100)

frontier_rows = []
raw_by_candidate = {}
for name, path in CANDIDATES.items():
    print(f"\n[frontier] {name} ...", flush=True)
    lgrid = [REF_CAPITAL / c for c in CAPITAL_GRID]
    df = PO2.leverage_curve(path, capital=REF_CAPITAL, grid=lgrid, leverage_mode="fixed_fraction")
    df = df.rename(columns={"leverage": "leverage_equiv_at_ref"})
    df.insert(0, "candidate", name)
    df.insert(1, "capital", [REF_CAPITAL / L for L in df["leverage_equiv_at_ref"]])
    frontier_rows.append(df)
    raw_by_candidate[name] = df.to_dict(orient="records")
    print(df[["capital", "J", "J_worst_over_methods", "model_determined_sign", "ce_log_growth_ann",
              "p_ruin_daily_close", "p_ruin_worst_of_three"]].to_string(index=False))

frontier = pd.concat(frontier_rows, ignore_index=True)
frontier.to_csv(os.path.join(OUT, "part2_capital_frontier.csv"), index=False)

# cross-check one grid point (C=$200,000) against the direct call already made in Part 1b
c200 = frontier[(frontier["candidate"] == "CONTROL") & (frontier["capital"] == 200_000.0)]
print(f"\n[cross-check] frontier row @ CONTROL/$200,000 J={c200['J'].iloc[0]!r} vs direct-call "
      f"J={r_b['primary']['objective_J']!r} -> match={abs(c200['J'].iloc[0] - r_b['primary']['objective_J']) < 1e-9}")

print()
print("=" * 100)
print("PART 2 alt-normalization (a) -- equal historical stressed-DD fraction: capital such that "
      "the candidate's OWN certified canonical maxDD_eod (genuine-MNQ) is exactly 25% of capital")
print("=" * 100)
alt_rows = []
for name, path in CANDIDATES.items():
    c_indiv = OWN_MAXDD_EOD[name] / 0.25
    r = PO2.primary_objective(path, capital=c_indiv, leverage=1.0, leverage_mode="fixed_fraction",
                               label=f"{name}_equalDDfrac")
    row = {"candidate": name, "own_maxDD_eod": OWN_MAXDD_EOD[name],
           "capital_equal_25pct_DD": c_indiv,
           "J": r["primary"]["objective_J"], "J_worst": r["primary"]["J_worst_over_methods"],
           "ce_log_growth_ann": r["primary"]["ce_log_growth_ann"], "p_ruin": r["primary"]["p_ruin"]}
    alt_rows.append(row)
    print(f"  {name}: own maxDD_eod=${OWN_MAXDD_EOD[name]:,.2f} -> capital=${c_indiv:,.2f}  "
          f"J={row['J']:.4f}  J_worst={row['J_worst']:.4f}  P_ruin={row['p_ruin']:.4f}")
alt_df = pd.DataFrame(alt_rows)
alt_df.to_csv(os.path.join(OUT, "part2_alt_normalization_equalDDfrac.csv"), index=False)

print()
print("=" * 100)
print("PART 2 context-only -- Product B (NQ, MNQ) on the SAME shared capital grid "
      "(different risk scale; NOT a promotion comparison, caveat repeated in REPORT.md)")
print("=" * 100)
u0 = pd.read_parquet(os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet"))
u0["sess_date"] = pd.to_datetime(u0["sess_date"])
CANONICAL_END_O2 = pd.Timestamp("2026-05-31")
canon = u0[u0["sess_date"] <= CANONICAL_END_O2]
b_nq_daily = canon.groupby("sess_date")["bar_pnl_B_nq_dollars"].sum()
b_mnq_daily = canon.groupby("sess_date")["bar_pnl_B_mnq_dollars"].sum()
prodb_rows = []
for name, series in [("ProductB_NQ", b_nq_daily), ("ProductB_MNQ", b_mnq_daily)]:
    lgrid = [REF_CAPITAL / c for c in CAPITAL_GRID]
    df = PO2.leverage_curve(series, capital=REF_CAPITAL, grid=lgrid, leverage_mode="fixed_fraction")
    df = df.rename(columns={"leverage": "leverage_equiv_at_ref"})
    df.insert(0, "candidate", name)
    df.insert(1, "capital", [REF_CAPITAL / L for L in df["leverage_equiv_at_ref"]])
    prodb_rows.append(df)
    print(f"\n[context] {name}:")
    print(df[["capital", "J", "J_worst_over_methods", "p_ruin_daily_close"]].to_string(index=False))
prodb_frontier = pd.concat(prodb_rows, ignore_index=True)
prodb_frontier.to_csv(os.path.join(OUT, "part2_context_productB_frontier.csv"), index=False)

print("\n[risk_panel] Part 1 + Part 2 complete.")
