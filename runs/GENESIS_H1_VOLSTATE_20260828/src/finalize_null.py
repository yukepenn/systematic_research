"""GENESIS_H1_VOLSTATE_20260828 — finalize: ledger result from the recorded gate state.

Reads out/_gate_state.json (written by run_discovery.py) and writes
out/ledger_result_pending.json. Result mapping per spec_resolutions R15:
PASS iff F1..F4 all pass; NULL when gates fail cleanly; DEFECT on data impossibility.
"""
import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "out"
gs = json.loads((OUT / "_gate_state.json").read_text(encoding="utf-8"))
st = gs["state"]

if gs.get("defect"):
    sys.exit("defect path should have been written by run_discovery — inspect manually")

assert not st["all3_pass"], "F1-F3 passed — this finalizer is only for the clean-NULL path"

metrics = {
    "n_discovery": st["n_disc"],
    "n_T1": st["n_t1"],
    "n_T3": st["n_t3"],
    "uncond_mean_pct": round(st["uncond_mean"], 6),
    "uncond_sd_pct": round(st["uncond_sd"], 6),
    "f1_T3_minus_T1_pct": round(st["f1"]["effect"], 6),
    "f1_t_clustered_monthly": round(st["f1"]["t"], 4),
    "f1_half1_diff_pct_2007_2013": round(st["half1_diff"], 6),
    "f1_half2_diff_pct_2014_2021": round(st["half2_diff"], 6),
    "f2_rv_matched_contrast_pct": round(st["f2"]["effect"], 6),
    "f2_t_clustered_monthly": round(st["f2"]["t"], 4),
    "f3_real_stat_pct": round(st["f3_real"], 6),
    "f3_null_p95_pct": round(st["f3_null_p95"], 6),
    "f3_percentile_rank": round(st["f3_rank_pct"], 2),
    "f3_p_ge": round(st["f3_p_ge"], 4),
    "expiry_rule_validation_pct_exact": 100.0,
    "f4_read": False,
    "parity_run": False,
    "seal_asserts": st["seal_asserts"],
}
note = (
    "H1 VOLSTATE clean NULL at the preregistered formulation. F1 FAIL: T3-T1 = "
    f"{metrics['f1_T3_minus_T1_pct']:.4f}%/session with t = {metrics['f1_t_clustered_monthly']:.2f} "
    "(monthly-clustered) — the preregistered sign (steep contango T3 -> higher next-session NQ "
    "return) is REVERSED in the pooled discovery sample and the halves disagree in sign "
    f"({metrics['f1_half1_diff_pct_2007_2013']:+.4f} / {metrics['f1_half2_diff_pct_2014_2021']:+.4f}). "
    "F2 FAIL (RV-matched contrast keeps the wrong sign). F3 FAIL (real stat at the 11.3th "
    "percentile of 300 whole-session circular-shift nulls). F4 NOT READ; the 2022+ NQ outcome "
    "window remains unread by this family; independent implementation not written (precondition "
    "failed); modern NQ parquet never opened. Secondary non-gate states point the same wrong way "
    "(VXN/VIX spread -0.055%, t -1.87; VIX3M/VIX -0.022%, t -0.74). Diagnostic note: a k=1 "
    "circular probe shows a large CONTEMPORANEOUS basis-return association (+0.30%), i.e. the "
    "curve state co-moves with the session just ended, not the session ahead."
)
(OUT / "ledger_result_pending.json").write_text(json.dumps({
    "trial_id": "G00010",
    "metrics": metrics,
    "result": "NULL",
    "note": note,
}, indent=1), encoding="utf-8")
print("ledger_result_pending.json written: result=NULL")
print(json.dumps(metrics, indent=1))
