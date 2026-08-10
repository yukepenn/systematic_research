"""O2 -- (i) real-data dry run of primary_objective_v2 (never before exercised on real P&L),
(ii) actual O2 scoring pass on a small, pre-registered Track-L candidate set, per
PREREGISTRATION.md's answers to the blind review's 4 items. Headline: C=$100,000, L=1.0
fixed_fraction (per PREREGISTRATION item a). Reports BOTH mixture and Gamma-minimax J for every
candidate; any sign-flip is INCONCLUSIVE per the binding range-rule policy."""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
import primary_objective_v2 as PO2

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

CANONICAL_END = pd.Timestamp("2026-05-31")


def load_daily(path, net_col="net", date_col="sess", end=CANONICAL_END):
    df = pd.read_csv(path)
    if net_col not in df.columns:
        net_col = "pnl"
    d = pd.to_datetime(df[date_col])
    s = pd.Series(df[net_col].to_numpy(float), index=d).sort_index()
    if end is not None:
        s = s[s.index <= end]
    return s


# ---------------------------------------------------------------- build U0-derived Product-B daily series
u0 = pd.read_parquet(os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet"))
u0["sess_date"] = pd.to_datetime(u0["sess_date"])
canon = u0[u0["sess_date"] <= CANONICAL_END]
b_nq_daily = canon.groupby("sess_date")["bar_pnl_B_nq_dollars"].sum()
b_mnq_daily = canon.groupby("sess_date")["bar_pnl_B_mnq_dollars"].sum()

candidates = {
    "ProductA_LEGACY_PROXY": load_daily(
        os.path.join(ROOT, "runs", "PRICE01_PRODUCT_A_GENUINE_MNQ", "out", "daily_legacy_proxy.csv")),
    "ProductA_GENUINE_MNQ": load_daily(
        os.path.join(ROOT, "runs", "PRICE01_PRODUCT_A_GENUINE_MNQ", "out", "daily_genuine_mnq.csv")),
    "ProductB_NQ": b_nq_daily,
    "ProductB_MNQ": b_mnq_daily,
    "U6B_CONTROL": load_daily(os.path.join(ROOT, "runs", "U6B_PRODUCT_A_SCALE_RATE", "out", "CONTROL_daily.csv")),
    "U6B_F0.5": load_daily(os.path.join(ROOT, "runs", "U6B_PRODUCT_A_SCALE_RATE", "out", "F0.5_daily.csv")),
    "U6B_F0.7": load_daily(os.path.join(ROOT, "runs", "U6B_PRODUCT_A_SCALE_RATE", "out", "F0.7_daily.csv")),
}

# correctness spot-check: certified canonical nets
CERTIFIED = {
    "ProductA_LEGACY_PROXY": 177924.40, "ProductB_NQ": 301915.92, "ProductB_MNQ": 28587.10,
}
for name, cert in CERTIFIED.items():
    got = float(candidates[name].sum())
    status = "PASS" if abs(got - cert) < 1.0 else "MISMATCH"
    print(f"[O2] correctness check {name}: got={got:.2f} certified={cert:.2f} [{status}]", flush=True)
    if status == "MISMATCH":
        raise AssertionError(f"O2 dry-run correctness gate FAILED for {name}: {got} vs {cert}")

rows = []
for name, daily in candidates.items():
    n = len(daily)
    print(f"\n[O2] scoring {name}  n_sessions={n}  net=${daily.sum():,.2f} ...", flush=True)
    res = PO2.primary_objective(daily, capital=100_000.0, leverage=1.0,
                                 leverage_mode="fixed_fraction", label=name)
    prim = res["primary"]
    J_mix = prim["objective_J"]
    P_ruin_mix = prim["p_ruin"]
    CE_g_mix = prim["ce_log_growth_ann"]
    J_worst = prim["J_worst_over_methods"]
    sign_flip = bool(prim["model_determined_sign"])
    verdict = "INCONCLUSIVE" if sign_flip else ("POSITIVE" if J_mix > 0 else "NEGATIVE")
    rows.append({
        "candidate": name, "n_sessions": n, "net_dollars": float(daily.sum()),
        "J_mixture": J_mix, "J_gamma_minimax": J_worst, "CE_g_mixture": CE_g_mix,
        "P_ruin_mixture": P_ruin_mix, "verdict": verdict,
    })
    print(f"[O2] {name}: J_mixture={J_mix:.4f}  J_gamma_minimax={J_worst}  "
          f"P_ruin={P_ruin_mix:.4f}  verdict={verdict}", flush=True)
    # save full raw result for audit trail
    with open(os.path.join(OUT, f"{name}_full_result.json"), "w") as f:
        json.dump(res, f, indent=2, default=str)

summary = pd.DataFrame(rows)
summary.to_csv(os.path.join(OUT, "o2_scoring_summary.csv"), index=False)
print("\n\n=== O2 SCORING SUMMARY ===")
print(summary.to_string(index=False))
