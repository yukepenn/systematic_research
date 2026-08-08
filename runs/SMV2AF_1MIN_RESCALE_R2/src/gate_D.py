"""SMV2AF_1MIN_RESCALE_R2 -- Gate D (DIAGNOSTIC, not pass/fail): correlation of the
rescaled-1m arm's daily PnL vs the deployed 3m-incumbent Solar leg's daily PnL (full dev
window + per-year), PLUS one exploratory equal-vol 50/50 blend of
[3m incumbent Solar leg] + [rescaled 1m arm], reusing the vm()/rerank equal-vol-rescale
convention verbatim from runs/SMV2AD_VOLMULT_CEILING/src/common.py's vm()/
build_portfolio_6040() pattern (here: 50/50 weights between two SOLAR legs, not the
Solar/BMOM 60/40 portfolio construction -- the object under test per spec is leg+leg, not
leg+BMOM).
"""
import os, json
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "SMV2AF_1MIN_RESCALE_R2")
OUT = os.path.join(RUN, "out")

curves = pd.read_csv(os.path.join(OUT, "dev_daily_curves.csv"), parse_dates=["sess"])
curves["year"] = curves["sess"].dt.year
x1m = curves["net_1m_rescaled"].to_numpy()
x3m = curves["net_3m_incumbent"].to_numpy()

# ---------------- correlation: full window + per year ----------------
def sharpe(v):
    v = np.asarray(v, dtype=float)
    sd = v.std(ddof=1)
    return v.mean() / sd * np.sqrt(252) if sd > 0 else np.nan

full_corr = float(np.corrcoef(x1m, x3m)[0, 1])
rows = [{"scope": "full_dev", "n_days": len(curves), "corr": full_corr}]
for yr, g in curves.groupby("year"):
    c = float(np.corrcoef(g["net_1m_rescaled"], g["net_3m_incumbent"])[0, 1])
    rows.append({"scope": str(yr), "n_days": len(g), "corr": c})
corr_df = pd.DataFrame(rows)
corr_df.to_csv(os.path.join(OUT, "gate_D_correlation.csv"), index=False)
print(corr_df.to_string(index=False))

low_corr_threshold = 0.5  # disclosed BEFORE results, per spec
low_corr = bool(abs(full_corr) < low_corr_threshold)

# ---------------- vm() verbatim convention (SMV2AD src/common.py) ----------------
def vm(x, sig):
    return x * (sig / x.std(ddof=1))

SIG = float(x3m.std(ddof=1))  # equal-vol-match TO the 3m incumbent leg's own vol (reference leg)
x3m_series = pd.Series(x3m, index=curves["sess"])
x1m_series = pd.Series(x1m, index=curves["sess"])
x1m_vm = vm(x1m_series, SIG)  # rescale the 1m arm to the incumbent's vol
blend = vm(0.5 * x3m_series + 0.5 * x1m_vm, SIG)  # 50/50 equal-vol blend, re-normalized to SIG

def battery(v, k=None):
    v = np.asarray(v, dtype=float)
    eqd = np.cumsum(v); pk = np.maximum.accumulate(eqd); dd = pk - eqd
    kk = k if k is not None else max(1, int(0.05 * len(v)))
    return {"net": v.sum(), "sharpe": sharpe(v), "maxDD_eod": dd.max(),
            "CDaR5": np.sort(dd)[::-1][:kk].mean()}

b_3m = battery(x3m_series.to_numpy())
b_1m = battery(x1m_series.to_numpy())
b_blend = battery(blend.to_numpy())

blend_beats_3m_sharpe = bool(b_blend["sharpe"] > b_3m["sharpe"])
blend_beats_3m_cdar = bool(b_blend["CDaR5"] < b_3m["CDaR5"])  # lower CDaR = better
flag_new_candidate = bool(low_corr and blend_beats_3m_sharpe and blend_beats_3m_cdar)

blend_df = pd.DataFrame([
    {"leg": "3m_incumbent_alone", **b_3m},
    {"leg": "1m_rescaled_alone", **b_1m},
    {"leg": "blend_50_50_volmatched", **b_blend},
])
blend_df["vol_match_target_SIG"] = SIG
blend_df.to_csv(os.path.join(OUT, "gate_D_blend.csv"), index=False)
print("\n" + blend_df.to_string(index=False))

summary = {
    "full_dev_correlation": full_corr,
    "low_corr_threshold_disclosed_before_results": low_corr_threshold,
    "low_corr_flag": low_corr,
    "per_year_correlation": {r["scope"]: r["corr"] for r in rows[1:]},
    "blend_construction": "vm(0.5*3m_incumbent + 0.5*vm(1m_rescaled, SIG=std(3m_incumbent)), SIG) "
                          "-- verbatim SMV2AD common.py vm() convention, 50/50 weights instead of 60/40",
    "sharpe_3m_alone": b_3m["sharpe"], "sharpe_1m_alone": b_1m["sharpe"], "sharpe_blend": b_blend["sharpe"],
    "CDaR5_3m_alone": b_3m["CDaR5"], "CDaR5_1m_alone": b_1m["CDaR5"], "CDaR5_blend": b_blend["CDaR5"],
    "blend_beats_3m_on_sharpe": blend_beats_3m_sharpe,
    "blend_beats_3m_on_cdar": blend_beats_3m_cdar,
    "flag_new_portfolio_blend_candidate_for_R3": flag_new_candidate,
}
json.dump(summary, open(os.path.join(OUT, "gate_D_summary.json"), "w"), indent=2)
print("\n" + json.dumps(summary, indent=2))
print("\ndone gate D")
