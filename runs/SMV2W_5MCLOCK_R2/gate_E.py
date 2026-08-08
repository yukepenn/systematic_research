"""SMV2W_5MCLOCK_R2 -- Gate E (portfolio): rebuild DAYONLY_DUAL6040 with the DUAL_5M
leg replacing the incumbent DUAL_ALL leg, replicating runs/SMV2H_ONECONTRACT/rerank.py's
60/40 cell construction exactly (same BM component = BMOM E2 next-open x5.0 ticks, same
weights 0.6/0.4, same vm() equal-vol rescale mechanism) -- with the vm() scalar SIG
re-derived from the new DUAL_5M leg's own daily std, since that is how rerank.py's own
vm() always worked (SIG = whichever DUAL leg is currently being processed). Template
reused verbatim from runs/SMV2T_NOFAST_R2/gate_E.py.

Compared against the incumbent champion curve = runs/SMV2H_ONECONTRACT/out/
rerank_curves.csv column "60_40" (== DAYONLY_DUAL_BMOM_60_40 in rerank_portfolios.csv).

PLUS (spec-required cross-check, "reusing SMV2U's already-computed portfolio numbers as
a cross-check, not a fresh read (they must reconcile before the new bootstrap-based gates
are trusted)"): before trusting this DUAL-transformed portfolio rebuild, we first
reconstruct the RAW (non-DUAL) 5m_time_matched arm's own 60/40 portfolio blend using
SMV2U's exact portfolio_blend() construction (step1_clock_arms.py) and confirm it
reconciles with SMV2U's committed out/portfolio_contrib.csv row
"5m_time_matched_portfolio" -- this is a reconciliation of the raw-leg construction
pipeline, not a substitute for the new DUAL-transformed test.
"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "SMV2W_5MCLOCK_R2")
OUT = os.path.join(RUN, "out")
SMV2U_OUT = os.path.join(ROOT, "runs", "SMV2U_CLOCK_CHALLENGE", "out")
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from smv2_common import dd_battery  # noqa: E402

# ================================================================== PART 1: reconciliation
# (raw, non-DUAL 5m_time_matched arm, portfolio-blended exactly as SMV2U step1 did)
print("=== PART 1: reconciliation vs SMV2U's committed raw-leg portfolio numbers ===", flush=True)

daily5_raw = pd.read_csv(os.path.join(RUN, "out", "e10_daily_dev_5m_time_matched.csv"),
                          parse_dates=["sess"])
arm_series = daily5_raw.set_index("sess")["net"]

bm_ledger = pd.read_parquet(os.path.join(ROOT, "runs", "SMV2B_BMOM_EXEC_AUDIT", "out",
                                         "ledger_E2_next_open.parquet"))
BM_raw = (bm_ledger.groupby("sess")["net_c1_ticks"].sum() * 5.0)
BM_raw.index = pd.to_datetime(BM_raw.index)

inc_daily = pd.read_csv(os.path.join(ROOT, "runs", "SMV2R_SOLAR_CORE_1", "out",
                                     "e10_daily_dev_incumbent.csv"), parse_dates=["sess"])
CAL = inc_daily["sess"]

def vm_series(x, sig):
    return x * (sig / x.std(ddof=1))

def portfolio_blend(leg_daily, bm_daily, cal, ws=0.6, wb=0.4):
    leg = leg_daily.reindex(cal).fillna(0.0)
    bm = bm_daily.reindex(cal).fillna(0.0)
    sig = leg.std(ddof=1)
    p = vm_series(ws * leg + wb * vm_series(bm, sig), sig)
    return p

port_raw5m = portfolio_blend(arm_series, BM_raw, CAL)
pb_raw5m = dd_battery(CAL, port_raw5m.values, label="5m_time_matched_portfolio_RECONCILE")

ref_pc = pd.read_csv(os.path.join(SMV2U_OUT, "portfolio_contrib.csv"))
ref_row = ref_pc[ref_pc["label"] == "5m_time_matched_portfolio"].iloc[0]

recon_fields = ["net", "sharpe", "CDaR5", "maxDD_eod"]
recon = []
for f in recon_fields:
    mine = float(pb_raw5m[f]); theirs = float(ref_row[f])
    dev = abs(mine - theirs)
    recon.append({"field": f, "mine": mine, "smv2u_ref": theirs, "abs_dev": dev,
                  "match": bool(dev < 1e-6 * max(1.0, abs(theirs)))})
recon_df = pd.DataFrame(recon)
recon_all_pass = bool(recon_df["match"].all())
print(recon_df.to_string(index=False))
print(f"\nRECONCILIATION: {'PASS' if recon_all_pass else 'FAIL'} "
      f"({recon_df['match'].sum()}/{len(recon_df)} fields exact) -- raw-leg portfolio "
      f"construction pipeline confirmed before trusting the new DUAL-transformed gate E "
      f"result below.", flush=True)
recon_df.to_csv(os.path.join(OUT, "gate_E_reconciliation.csv"), index=False)

# ================================================================== PART 2: the actual Gate E
# (DUAL_5M-transformed leg, portfolio-composed via rerank.py's exact 60/40 vm construction)
print("\n=== PART 2: Gate E -- DUAL-transformed portfolio rebuild vs incumbent champion ===",
      flush=True)

curves = pd.read_csv(os.path.join(OUT, "curves.csv"), parse_dates=["sess"]).set_index("sess")
DUAL_all = curves["DUAL_ALL"]
DUAL_5m = curves["DUAL_5M"]
cal = curves.index

BM = BM_raw.reindex(cal).fillna(0.0)

def rha(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)

def vm(x, sig):
    return x * (sig / x.std(ddof=1))

SIG_old = float(DUAL_all.std(ddof=1))      # incumbent scalar (rerank.py's original SIG)
SIG_new = float(DUAL_5m.std(ddof=1))       # re-derived scalar for the DUAL_5M leg

BM_vm_old_scale = float(SIG_old / BM.std(ddof=1))
BM_vm_new_scale = float(SIG_new / BM.std(ddof=1))

portfolio_5m_6040 = vm(0.6 * DUAL_5m + 0.4 * vm(BM, SIG_new), SIG_new)

b_5m = dd_battery(cal, portfolio_5m_6040.values, label="DAYONLY_DUAL_BMOM_60_40_5M")

# ---------------- incumbent champion curve ----------------
champ_all = pd.read_csv(os.path.join(ROOT, "runs", "SMV2H_ONECONTRACT", "out", "rerank_curves.csv"),
                         parse_dates=["sess"]).set_index("sess")["60_40"]
champ = champ_all.reindex(cal)
assert champ.isna().sum() == 0, "champion curve missing dev sessions"
b_champ = dd_battery(cal, champ.values, label="DAYONLY_DUAL_BMOM_60_40_INCUMBENT")

champ_row = pd.read_csv(os.path.join(ROOT, "runs", "SMV2H_ONECONTRACT", "out",
                                      "rerank_portfolios.csv")).set_index("label").loc["DAYONLY_DUAL_BMOM_60_40"]
champ_net_dev = abs(b_champ["net"] - champ_row["net"])
champ_sharpe_dev = abs(b_champ["sharpe"] - champ_row["sharpe"])
print(f"incumbent champion curve cross-check: net |dev|={champ_net_dev:.4f}  "
      f"sharpe |dev|={champ_sharpe_dev:.6f}", flush=True)

d_sharpe = b_5m["sharpe"] - b_champ["sharpe"]
d_cdar = b_champ["CDaR5"] - b_5m["CDaR5"]   # + = challenger (5m rebuild) better
gateE_pass = bool(d_sharpe > 0 and d_cdar > 0)

gate_e = pd.DataFrame([{
    "n_days": len(cal),
    "SIG_old_incumbent_DUAL_std": SIG_old, "SIG_new_5m_DUAL_std": SIG_new,
    "BM_vm_scale_old": BM_vm_old_scale, "BM_vm_scale_new": BM_vm_new_scale,
    "weights_DUAL_BM": "0.6 / 0.4 (unchanged, frozen)",
    "net_incumbent_6040": b_champ["net"], "net_5m_rebuild_6040": b_5m["net"],
    "sharpe_incumbent_6040": b_champ["sharpe"], "sharpe_5m_rebuild_6040": b_5m["sharpe"],
    "d_sharpe": d_sharpe,
    "CDaR5_incumbent_6040": b_champ["CDaR5"], "CDaR5_5m_rebuild_6040": b_5m["CDaR5"],
    "d_CDaR": d_cdar,
    "maxDD_incumbent_6040": b_champ["maxDD_eod"], "maxDD_5m_rebuild_6040": b_5m["maxDD_eod"],
    "pass_dSharpe_point_positive": bool(d_sharpe > 0),
    "pass_dCDaR_point_positive": bool(d_cdar > 0),
    "gateE_pass": gateE_pass,
    "champion_curve_reconstruction_net_dev_$": champ_net_dev,
    "champion_curve_reconstruction_sharpe_dev": champ_sharpe_dev,
    "raw_leg_reconciliation_vs_smv2u_pass": recon_all_pass,
}])
gate_e.to_csv(os.path.join(OUT, "gate_E.csv"), index=False)
print(gate_e.to_string(index=False), flush=True)

pd.DataFrame({"sess": cal, "PORT_INCUMBENT_6040": champ.values,
              "PORT_5M_6040": portfolio_5m_6040.values,
              "DUAL_ALL": DUAL_all.values, "DUAL_5M": DUAL_5m.values,
              "BM_E2": BM.values}).to_csv(os.path.join(OUT, "gate_E_curves.csv"), index=False)

json.dump({"gateE_pass": gateE_pass, "d_sharpe": d_sharpe, "d_CDaR": d_cdar,
           "SIG_old": SIG_old, "SIG_new": SIG_new,
           "raw_leg_reconciliation_pass": recon_all_pass},
          open(os.path.join(OUT, "gate_E_summary.json"), "w"), indent=2)
print("\ndone gate E", flush=True)
