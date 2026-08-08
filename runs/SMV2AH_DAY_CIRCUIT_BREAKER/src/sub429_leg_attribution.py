"""SMV2AH sub_429 -- mechanism note (DIAGNOSTIC, always reported): for object B
(the portfolio), what fraction of triggered-session halts would have been
triggered by the Solar/DUAL leg's own MTM vs the B-MOM leg's vs both
simultaneously. Mirrors SMV2AA's leg-asymmetry diagnostic discipline.

At each triggered session's trigger bar t0 (object B's own combined intraday
MTM first crossing the threshold -- trigger set is mode-independent, same set
used for both FREEZE and FLATTEN), decompose the portfolio's cumulative MTM
at t0 into its two additive leg contributions (exact, since the 60/40 blend
is a fixed linear combination of the two legs' own bar_pnl):
  contrib_dual(t0) = c_combo * 0.6 * (DUAL leg's OWN session-cumulative MTM at t0)
  contrib_bm(t0)   = c_combo * 0.4 * c_BM * (BM leg's OWN session-cumulative MTM at t0)
  contrib_dual(t0) + contrib_bm(t0) == intraday_mtm_B(t0)  (verified below)
Classify each triggered session by which leg supplied the majority of the
(necessarily negative, since t0 is below threshold) combined shortfall.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from common_ah import OUT, load_dev_bars, build_objects

print("loading dev bars + rebuilding objects ...", flush=True)
bars = load_dev_bars()
obj = build_objects(bars)
sess_id = bars["sess_id"].to_numpy()
c_BM, c_combo = obj["c_BM"], obj["c_combo"]

intraday = pd.read_parquet(os.path.join(OUT, "intraday_mtm_series.parquet"))
intraday["_pos"] = np.arange(len(intraday))

# BM leg's OWN (unscaled) per-session cumulative MTM -- not saved by sub_426
# (which only kept the dual-only and portfolio-combined columns); cheap to add.
bm_only_cum = pd.Series(obj["BM_bar_pnl"]).groupby(sess_id).cumsum().to_numpy()
intraday["intraday_mtm_BM_only"] = bm_only_cum

calib = pd.read_csv(os.path.join(OUT, "threshold_calibration.csv"))
rows = []
detail_rows = []
for pct in (1, 2, 5, 10):
    thr = float(calib[(calib.object == "B_DAYONLY_DUAL6040") & (calib.percentile == pct)]
                ["threshold_dollars"].iloc[0])
    mask = intraday["intraday_mtm_B"].to_numpy() < thr
    sub = intraday.loc[mask, ["sess_id", "_pos"]]
    first_bar = sub.groupby("sess_id")["_pos"].min()

    for sid, t0 in first_bar.items():
        r = intraday.iloc[t0]
        contrib_dual = c_combo * 0.6 * r["intraday_mtm_A"]
        contrib_bm = c_combo * 0.4 * c_BM * r["intraday_mtm_BM_only"]
        combined = contrib_dual + contrib_bm
        recon_diff = combined - r["intraday_mtm_B"]
        dual_neg = contrib_dual < 0
        bm_neg = contrib_bm < 0
        total_neg_mag = abs(min(contrib_dual, 0.0)) + abs(min(contrib_bm, 0.0))
        dual_share = abs(min(contrib_dual, 0.0)) / total_neg_mag if total_neg_mag > 0 else np.nan
        if dual_neg and not bm_neg:
            cls = "SOLAR_ONLY"
        elif bm_neg and not dual_neg:
            cls = "BMOM_ONLY"
        elif dual_neg and bm_neg:
            if dual_share >= 0.67:
                cls = "BOTH_NEGATIVE_SOLAR_DOMINANT"
            elif dual_share <= 0.33:
                cls = "BOTH_NEGATIVE_BMOM_DOMINANT"
            else:
                cls = "BOTH_NEGATIVE_COMPARABLE"
        else:
            cls = "NEITHER_NEGATIVE_ANOMALY"  # should not occur
        detail_rows.append({
            "percentile": pct, "sess_id": int(sid), "trigger_bar_pos": int(t0),
            "portfolio_mtm_at_trigger": float(r["intraday_mtm_B"]),
            "contrib_dual": float(contrib_dual), "contrib_bm": float(contrib_bm),
            "recon_check_diff": float(recon_diff), "dual_share_of_negative": float(dual_share),
            "classification": cls,
        })

detail = pd.DataFrame(detail_rows)
recon_max = detail["recon_check_diff"].abs().max()
print(f"leg-decomposition reconciliation: max abs diff (contrib_dual+contrib_bm) vs "
      f"portfolio MTM at trigger = ${recon_max:.6f}", flush=True)
assert recon_max < 0.01, "leg attribution decomposition does not reconcile"

for pct in (1, 2, 5, 10):
    d = detail[detail.percentile == pct]
    vc = d["classification"].value_counts()
    n = len(d)
    row = {"percentile": pct, "n_triggered": n}
    for cls in ("SOLAR_ONLY", "BMOM_ONLY", "BOTH_NEGATIVE_SOLAR_DOMINANT",
                "BOTH_NEGATIVE_BMOM_DOMINANT", "BOTH_NEGATIVE_COMPARABLE", "NEITHER_NEGATIVE_ANOMALY"):
        row[f"n_{cls}"] = int(vc.get(cls, 0))
        row[f"pct_{cls}"] = 100.0 * vc.get(cls, 0) / n if n else 0.0
    row["mean_dual_share_of_negative"] = float(d["dual_share_of_negative"].mean())
    rows.append(row)
    print(f"p{pct} (n_trig={n}): " + ", ".join(f"{k}={v}" for k, v in vc.to_dict().items()) +
          f" | mean_dual_share={row['mean_dual_share_of_negative']:.2f}", flush=True)

summary = pd.DataFrame(rows)
summary.to_csv(os.path.join(OUT, "leg_attribution.csv"), index=False)
detail.to_csv(os.path.join(OUT, "leg_attribution_detail.csv"), index=False)
print(summary.to_string(index=False), flush=True)
print("done sub_429", flush=True)
