"""SMV2AD step0 -- verify the committed simulator reproduces the SM01 dev substrate
for the 1200t/13-member control (integrity gate before any variant run), and cache
sigma460 (smax_ticks-independent) for reuse by sub_415/416.
"""
import sys, os, json, time
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT, OUT, DEV_END, load_dev_bars, build_pend, e10_exec, INCUMBENT_VMS
import sm01_solarsim as sm

t0 = time.time()
bars = load_dev_bars()
print("dev bars:", len(bars), bars.time.min(), "->", bars.time.max(), flush=True)

close = bars["close"].to_numpy()
sig = sm.sigma_series(close)
np.save(os.path.join(OUT, "sigma460_dev.npy"), sig)

# ---- control arm: smax=1200t, incumbent 13-member VMS ----
pend_control = build_pend(bars, sig, INCUMBENT_VMS, smax_ticks=1200.0, smin_ticks=40.0)
tgt_control = sm.e10_target(pend_control)

v = pd.read_parquet(os.path.join(ROOT, "runs", "SM01_SUBSTRATE", "out", "vote_state_3m.parquet"))
v["sess_date"] = pd.to_datetime(v["sess_date"]).dt.date
v = v[v["sess_date"] <= DEV_END].reset_index(drop=True)
assert len(v) == len(bars), f"bar count mismatch {len(v)} vs {len(bars)}"
assert (pd.to_datetime(v["time"]).to_numpy() == bars["time"].to_numpy()).all(), "time axis mismatch"

my_vote_pend = pend_control.sum(axis=1)
match_pend = float((my_vote_pend == v["vote_pend"].to_numpy()).mean())
print("control (1200t/13-member) vote_pend match vs committed SM01 substrate:", match_pend, flush=True)
assert match_pend >= 0.9999, "simulator FAILED to reproduce committed SM01 substrate -- BLOCKED"

daily_control, bar_pos, bar_pnl = e10_exec(bars, tgt_control)
ref = pd.read_csv(os.path.join(ROOT, "runs", "SM01_SUBSTRATE", "out", "e10_daily_py.csv"))
ref["sess"] = pd.to_datetime(ref["sess"]).dt.date
ref = ref[ref["sess"] <= DEV_END]
mm = daily_control.copy(); mm["sess"] = pd.to_datetime(mm["sess"]).dt.date
j = ref.merge(mm, on="sess", suffixes=("_ref", "_my"))
daily_max_dev = float(np.abs(j["net_ref"] - j["net_my"]).max())
print("control daily E10 net cross-check vs e10_daily_py.csv, max|dev| =", daily_max_dev,
      f"({len(j)}/{len(ref)} sessions matched)", flush=True)

res = {
    "n_dev_bars": int(len(bars)), "dev_last_session": str(bars.sess_date.max()),
    "match_vote_pend_control": match_pend,
    "e10_daily_max_abs_dev_$": daily_max_dev,
    "e10_daily_sessions_matched": int(len(j)), "e10_daily_ref_sessions": int(len(ref)),
    "verified": bool(match_pend >= 0.9999 and daily_max_dev < 1.0),
    "runtime_s": round(time.time() - t0, 1),
}
with open(os.path.join(OUT, "step0_verify.json"), "w") as f:
    json.dump(res, f, indent=2)
print(json.dumps(res, indent=2))

np.savez_compressed(os.path.join(OUT, "cache_control_1200.npz"),
                     pend=pend_control, tgt=tgt_control)
daily_control.to_csv(os.path.join(OUT, "e10_daily_dev_control_1200.csv"), index=False)
print("cached.", flush=True)
