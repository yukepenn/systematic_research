"""W18R1 STEP 1 — D4 intraday profile. Merged into M1 per MEGA PROMPT V7 §C-2.

A DIAGNOSTIC and a result in its own right. Reported whatever it shows, including if it
FALSIFIES M1's premise (the falsification bar is written in the frozen spec and is applied
mechanically here).
"""
import os, json
import numpy as np, pandas as pd

import common as C
import sm01_solarsim as sm

os.makedirs(C.OUT, exist_ok=True)
bars = C.load_dev_bars()
n = len(bars)
print(f"dev bars {n}  sessions {bars['sess_date'].nunique()} "
      f"{bars['time'].min()} -> {bars['time'].max()}", flush=True)

slot = C.slot_index(bars)
d = C.abs_dclose(bars)
sigma = sm.sigma_series(bars["close"].to_numpy())
tod = pd.to_datetime(bars["time"]).dt.strftime("%H:%M").to_numpy()

# ---------------------------------------------------------------- 1a. raw profile
df = pd.DataFrame({"slot": slot, "tod": tod, "d": d, "sigma": sigma})
g = df.groupby("slot")
prof = pd.DataFrame({
    "slot": g.size().index,
    "tod": g["tod"].first().to_numpy(),
    "n_bars": g.size().to_numpy(),
    "mean_abs_dclose": g["d"].mean().to_numpy(),
})
prof["f_dev_unconditional"] = prof["mean_abs_dclose"] / (d.sum() / len(d))

# ---------------------------------------------------------------- 1b. THE PREMISE TEST
# r_s = mean over bars in slot s of |dclose_t| / sigma460_t.  M1's premise is r_s strongly
# non-flat.  PRE-REGISTERED FALSIFICATION: if max/min over slots with >= 200 bars is < 1.5,
# the premise is REJECTED and that is the headline finding.
df["ratio"] = np.where(np.isfinite(df["sigma"]) & (df["sigma"] > 0), df["d"] / df["sigma"], np.nan)
gr = df.groupby("slot")["ratio"]
prof["r_s"] = gr.mean().reindex(prof["slot"]).to_numpy()
prof["r_s_n"] = gr.count().reindex(prof["slot"]).to_numpy()

thick = prof[prof["r_s_n"] >= 200].copy()
r_max, r_min = float(thick["r_s"].max()), float(thick["r_s"].min())
ratio_spread = r_max / r_min if r_min > 0 else np.inf
premise_rejected = bool(ratio_spread < 1.5)
premise = {
    "n_slots_total": int(len(prof)),
    "n_slots_thick_ge200bars": int(len(thick)),
    "r_s_max": r_max, "r_s_max_tod": str(thick.loc[thick["r_s"].idxmax(), "tod"]),
    "r_s_min": r_min, "r_s_min_tod": str(thick.loc[thick["r_s"].idxmin(), "tod"]),
    "max_over_min": float(ratio_spread),
    "preregistered_bar": 1.5,
    "PREMISE_REJECTED": premise_rejected,
    "f_dev_peak_over_trough": float(thick["f_dev_unconditional"].max() /
                                    thick["f_dev_unconditional"].min()),
}
print("\n=== PREMISE TEST ===")
print(json.dumps(premise, indent=2), flush=True)

# ---------------------------------------------------------------- 1c. incumbent by slot
PEND, FLIPS = C.build_pend_with_flips(bars, sigma)
tgt = sm.e10_target(PEND)
daily, bar_pos, bar_pnl = C.e10_exec(bars, tgt)

tgt_change = np.zeros(n, dtype=int); tgt_change[1:] = (np.diff(tgt) != 0).astype(int)
entries = np.zeros(n, dtype=int); exits = np.zeros(n, dtype=int)
prev = np.concatenate([[0], bar_pos[:-1]])
entries[(prev == 0) & (bar_pos != 0)] = 1
exits[(prev != 0) & (bar_pos == 0)] = 1

inc = pd.DataFrame({
    "slot": slot, "tod": tod,
    "member_flips": (FLIPS != 0).sum(axis=1),
    "tgt_change": tgt_change, "entries": entries, "exits": exits,
    "bar_pnl": bar_pnl, "abs_tgt": np.abs(tgt),
})
gi = inc.groupby("slot")
by_slot = pd.DataFrame({
    "slot": gi.size().index, "tod": gi["tod"].first().to_numpy(),
    "n_bars": gi.size().to_numpy(),
    "member_flips": gi["member_flips"].sum().to_numpy(),
    "tgt_changes": gi["tgt_change"].sum().to_numpy(),
    "entries": gi["entries"].sum().to_numpy(),
    "exits": gi["exits"].sum().to_numpy(),
    "net_pnl": gi["bar_pnl"].sum().to_numpy(),
    "mean_abs_tgt": gi["abs_tgt"].mean().to_numpy(),
})
by_slot["flips_per_bar"] = by_slot["member_flips"] / by_slot["n_bars"]
by_slot["pnl_per_tgt_change"] = np.where(by_slot["tgt_changes"] > 0,
                                          by_slot["net_pnl"] / by_slot["tgt_changes"], np.nan)
by_slot = by_slot.merge(prof[["slot", "r_s", "f_dev_unconditional"]], on="slot", how="left")

# ---------------------------------------------------------------- 1d. the three cohorts
# defined once in the frozen spec and NOT re-cut after seeing results
hh = pd.to_datetime(bars["time"]).dt.hour.to_numpy()
cohort = np.where(hh >= 18, "EVENING", np.where(hh < 9, "OVERNIGHT", "RTH"))
inc["cohort"] = cohort; df["cohort"] = cohort
gc = inc.groupby("cohort")
coh = pd.DataFrame({
    "cohort": gc.size().index, "n_bars": gc.size().to_numpy(),
    "member_flips": gc["member_flips"].sum().to_numpy(),
    "tgt_changes": gc["tgt_change"].sum().to_numpy(),
    "entries": gc["entries"].sum().to_numpy(),
    "exits": gc["exits"].sum().to_numpy(),
    "net_pnl": gc["bar_pnl"].sum().to_numpy(),
})
coh["share_of_bars"] = coh["n_bars"] / n
coh["share_of_pnl"] = coh["net_pnl"] / bar_pnl.sum()
coh["flips_per_bar"] = coh["member_flips"] / coh["n_bars"]
coh["mean_r_s"] = df.groupby("cohort")["ratio"].mean().reindex(coh["cohort"]).to_numpy()
coh["mean_abs_dclose"] = df.groupby("cohort")["d"].mean().reindex(coh["cohort"]).to_numpy()
coh["pnl_per_tgt_change"] = coh["net_pnl"] / coh["tgt_changes"]

print("\n=== COHORTS (incumbent) ===")
print(coh.to_string(index=False), flush=True)

prof.to_csv(os.path.join(C.OUT, "d4_slot_profile.csv"), index=False)
by_slot.to_csv(os.path.join(C.OUT, "d4_incumbent_by_slot.csv"), index=False)
coh.to_csv(os.path.join(C.OUT, "d4_cohorts.csv"), index=False)
json.dump(premise, open(os.path.join(C.OUT, "d4_premise_test.json"), "w"), indent=2)
pd.DataFrame([premise]).to_csv(os.path.join(C.OUT, "d4_premise_test.csv"), index=False)
np.save(os.path.join(C.OUT, "sigma460_dev.npy"), sigma)
daily.to_csv(os.path.join(C.OUT, "daily_control_rebuilt.csv"), index=False)
np.save(os.path.join(C.OUT, "tgt_control.npy"), tgt)

# control cross-check against the committed SMV2AD artifact (frozen spec requires this
# discrepancy be reported BEFORE any gate is read)
ref = pd.read_csv(os.path.join(C.ROOT, "runs", "SMV2AD_VOLMULT_CEILING", "out",
                                "e10_daily_dev_control_1200.csv"))
# NOTE: sess is datetime.date in `daily` and str in the committed CSV; cast BOTH or the
# merge silently yields zero rows (it did, on the first pass — reported in REPORT.md).
_d = daily.copy(); _d["sess"] = _d["sess"].astype(str)
ref["sess"] = ref["sess"].astype(str)
m = _d.merge(ref, on="sess", suffixes=("_new", "_ref"))
chk = {"n_sess_new": int(len(daily)), "n_sess_ref": int(len(ref)), "n_matched": int(len(m)),
       "net_new": float(daily["net"].sum()), "net_ref": float(ref["net"].sum()),
       "max_abs_daily_diff": float((m["net_new"] - m["net_ref"]).abs().max()),
       "n_days_differing_gt_1c": int(((m["net_new"] - m["net_ref"]).abs() > 0.01).sum())}
print("\n=== CONTROL REBUILD CROSS-CHECK vs SMV2AD committed artifact ===")
print(json.dumps(chk, indent=2), flush=True)
json.dump(chk, open(os.path.join(C.OUT, "control_crosscheck.json"), "w"), indent=2)
print("\nstep1 done", flush=True)
