"""SMV2T_NOFAST_R2 — Gate E (portfolio): rebuild DAYONLY_DUAL6040 with the no-FAST DUAL
leg replacing the incumbent DUAL leg, replicating runs/SMV2H_ONECONTRACT/rerank.py's 60/40
cell CONSTRUCTION exactly (same BM component, same weights 0.6/0.4, same vm() equal-vol
rescale mechanism) -- with the vm() scalar SIG re-derived from the new no-FAST DUAL leg's
own daily std (documented below), since that is how rerank.py's own vm() always worked
(SIG = whichever DUAL leg is currently being processed).

Compared against the incumbent champion curve = runs/SMV2H_ONECONTRACT/out/rerank_curves.csv
column "60_40" (== DAYONLY_DUAL_BMOM_60_40 in rerank_portfolios.csv; system_master
CURRENT_TRUTH.md: "SOLAR_PLUS_BMOM (DAYONLY_DUAL6040): PRIMARY DAY-ONLY CHAMPION").
"""
import os, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "SMV2T_NOFAST_R2")
OUT = os.path.join(RUN, "out")

curves = pd.read_csv(os.path.join(OUT, "curves.csv"), parse_dates=["sess"]).set_index("sess")
DUAL_all = curves["DUAL_ALL"]
DUAL_nofast = curves["DUAL_NOFAST"]
cal = curves.index

# ---------------- BM (BMOM E2 next-open), verbatim rerank.py ----------------
bm2 = pd.read_parquet(os.path.join(ROOT, "runs", "SMV2B_BMOM_EXEC_AUDIT", "out",
                                    "ledger_E2_next_open.parquet"))
BM = (bm2.groupby("sess")["net_c1_ticks"].sum() * 5.0)
BM.index = pd.to_datetime(BM.index)
BM = BM.reindex(cal).fillna(0.0)

# ---------------- rerank.py's sim() function, verbatim, applied to the no-FAST DUAL leg
#                  (integrity check only -- DUAL_nofast already comes from gate_AD's
#                  verified e10_exec on the same target; cross-checked below to confirm
#                  the two executors agree bit-for-bit on this leg too) ----------------
import sys
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from sm01_solarsim import load_bars_3m, _fill

def rerank_sim(bars, tgt, comm=0.65, pv=2.0):
    n = len(bars)
    o = bars["open"].to_numpy(); h = bars["high"].to_numpy(); l = bars["low"].to_numpy()
    c = bars["close"].to_numpy(); last = bars["is_last_of_sess"].to_numpy()
    sd = bars["sess_date"].to_numpy()
    cash = 0.0; p = 0; pend = 0; daily = {}; prev = 0.0
    for t in range(n):
        if pend != p:
            d = pend - p; side = 1 if d > 0 else -1
            px = _fill(o[t], h[t], l[t], side)
            cash -= d * px * pv; cash -= abs(d) * comm
            p = pend
        if last[t] and p != 0:
            side = -1 if p > 0 else 1
            px = _fill(o[t], h[t], l[t], side, at_close=c[t])
            cash += p * px * pv; cash -= abs(p) * comm; p = 0; pend = 0
        else:
            pend = int(tgt[t])
        if last[t]:
            eq = cash + p * c[t] * pv
            daily[sd[t]] = eq - prev; prev = eq
    s = pd.Series(daily); s.index = pd.to_datetime(s.index); return s

bars = load_bars_3m(os.path.join(ROOT, "runs", "AUDIT03_BARS", "nq_3m_2022_2026.csv"))
sess = pd.to_datetime(bars["sess_date"]); dev = sess <= pd.Timestamp("2026-05-31")
bars_dev = bars[dev].reset_index(drop=True)
Tpp_nofast_dev = np.load(os.path.join(OUT, "tpp_nofast_dev.npy"))
DUAL_nofast_rerank = rerank_sim(bars_dev, Tpp_nofast_dev)
DUAL_nofast_rerank = DUAL_nofast_rerank.reindex(cal)
xcheck_max_dev = float(np.abs(DUAL_nofast_rerank.values - DUAL_nofast.values).max())
print("DUAL_nofast (e10_exec) vs rerank.py sim() cross-check, max|dev| =", xcheck_max_dev, flush=True)

# ---------------- re-derive vm() scalars for the no-FAST leg ----------------
def rha(x): return np.sign(x) * np.floor(np.abs(x) + 0.5)

SIG_old = float(DUAL_all.std(ddof=1))       # incumbent scalar (rerank.py's original SIG)
SIG_new = float(DUAL_nofast.std(ddof=1))    # re-derived scalar for the no-FAST leg

def vm(x, sig):
    return x * (sig / x.std(ddof=1))

BM_vm_old_scale = float(SIG_old / BM.std(ddof=1))
BM_vm_new_scale = float(SIG_new / BM.std(ddof=1))

portfolio_nofast_6040 = vm(0.6 * DUAL_nofast + 0.4 * vm(BM, SIG_new), SIG_new)

# ---------------- battery (smv2_common.dd_battery, frozen definitions) ----------------
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from smv2_common import dd_battery

b_nofast = dd_battery(cal, portfolio_nofast_6040.values, label="DAYONLY_DUAL_BMOM_60_40_NOFAST")

# ---------------- incumbent champion curve ----------------
champ_all = pd.read_csv(os.path.join(ROOT, "runs", "SMV2H_ONECONTRACT", "out", "rerank_curves.csv"),
                         parse_dates=["sess"]).set_index("sess")["60_40"]
champ = champ_all.reindex(cal)
assert champ.isna().sum() == 0, "champion curve missing dev sessions"
b_champ = dd_battery(cal, champ.values, label="DAYONLY_DUAL_BMOM_60_40_INCUMBENT")

# cross-check incumbent champion curve reconstruction against rerank_portfolios.csv row
champ_row = pd.read_csv(os.path.join(ROOT, "runs", "SMV2H_ONECONTRACT", "out",
                                      "rerank_portfolios.csv")).set_index("label").loc["DAYONLY_DUAL_BMOM_60_40"]
champ_net_dev = abs(b_champ["net"] - champ_row["net"])
champ_sharpe_dev = abs(b_champ["sharpe"] - champ_row["sharpe"])
print(f"incumbent champion curve cross-check: net |dev|={champ_net_dev:.4f}  "
      f"sharpe |dev|={champ_sharpe_dev:.6f}", flush=True)

d_sharpe = b_nofast["sharpe"] - b_champ["sharpe"]
d_cdar = b_champ["CDaR5"] - b_nofast["CDaR5"]   # + = challenger (no-FAST rebuild) better
gateE_pass = bool(d_sharpe > 0 and d_cdar > 0)

gate_e = pd.DataFrame([{
    "n_days": len(cal),
    "SIG_old_incumbent_DUAL_std": SIG_old, "SIG_new_nofast_DUAL_std": SIG_new,
    "BM_vm_scale_old": BM_vm_old_scale, "BM_vm_scale_new": BM_vm_new_scale,
    "weights_DUAL_BM": "0.6 / 0.4 (unchanged, frozen)",
    "net_incumbent_6040": b_champ["net"], "net_nofast_rebuild_6040": b_nofast["net"],
    "sharpe_incumbent_6040": b_champ["sharpe"], "sharpe_nofast_rebuild_6040": b_nofast["sharpe"],
    "d_sharpe": d_sharpe,
    "CDaR5_incumbent_6040": b_champ["CDaR5"], "CDaR5_nofast_rebuild_6040": b_nofast["CDaR5"],
    "d_CDaR": d_cdar,
    "maxDD_incumbent_6040": b_champ["maxDD_eod"], "maxDD_nofast_rebuild_6040": b_nofast["maxDD_eod"],
    "pass_dSharpe_point_positive": bool(d_sharpe > 0),
    "pass_dCDaR_point_positive": bool(d_cdar > 0),
    "gateE_pass": gateE_pass,
    "dual_nofast_executor_crosscheck_max_abs_dev_$": xcheck_max_dev,
    "champion_curve_reconstruction_net_dev_$": champ_net_dev,
    "champion_curve_reconstruction_sharpe_dev": champ_sharpe_dev,
}])
gate_e.to_csv(os.path.join(OUT, "gate_E.csv"), index=False)
print(gate_e.to_string(index=False), flush=True)

pd.DataFrame({"sess": cal, "PORT_INCUMBENT_6040": champ.values,
              "PORT_NOFAST_6040": portfolio_nofast_6040.values,
              "DUAL_ALL": DUAL_all.values, "DUAL_NOFAST": DUAL_nofast.values,
              "BM_E2": BM.values}).to_csv(os.path.join(OUT, "gate_E_curves.csv"), index=False)

json.dump({"gateE_pass": gateE_pass, "d_sharpe": d_sharpe, "d_CDaR": d_cdar,
           "SIG_old": SIG_old, "SIG_new": SIG_new}, open(os.path.join(OUT, "gate_E_summary.json"), "w"), indent=2)
print("\ndone gate E", flush=True)
