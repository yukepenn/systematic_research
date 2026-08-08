"""SMV2AJ_ATR_BLEND_R2 -- Gate D: top-10-day retention >= 1.00 on the
DUAL-transformed dev legs (out/curves.csv). Identical construction to
runs/SMV2T_NOFAST_R2/gate_AD.py's Gate D block.
"""
import os
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "SMV2AJ_ATR_BLEND_R2")
OUT = os.path.join(RUN, "out")

curves = pd.read_csv(os.path.join(OUT, "curves.csv"), parse_dates=["sess"]).set_index("sess")
base = curves["DUAL_CONTROL"]
chal = curves["DUAL_BLEND75"]

top10 = base.nlargest(10)
on_base_days = float(chal.reindex(top10.index).sum())
retention = on_base_days / float(top10.sum())
own_top10 = chal.nlargest(10)
overlap = len(set(top10.index) & set(own_top10.index))

gate_d = pd.DataFrame([{
    "kind": "SUMMARY", "top10_CONTROL_sum": float(top10.sum()),
    "BLEND75_pnl_on_CONTROL_top10_days": on_base_days,
    "retention_CONTROL_top10": retention,
    "BLEND75_own_top10_sum": float(own_top10.sum()),
    "overlap_days": overlap,
    "pass_retention_ge_1.00": bool(retention >= 1.00),
}])
detail_rows = [{"date": d.date(), "CONTROL_pnl": float(base.loc[d]), "BLEND75_pnl": float(chal.loc[d])}
               for d in top10.index]
gate_d_detail = pd.DataFrame(detail_rows)
gate_d.to_csv(os.path.join(OUT, "gate_D.csv"), index=False)
gate_d_detail.to_csv(os.path.join(OUT, "gate_D_top10_detail.csv"), index=False)
print(gate_d.to_string(index=False), flush=True)
print("\n" + gate_d_detail.to_string(index=False), flush=True)
print("\ndone gate D", flush=True)
