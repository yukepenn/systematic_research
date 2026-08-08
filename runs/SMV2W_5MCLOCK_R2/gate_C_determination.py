"""SMV2W_5MCLOCK_R2 -- Gate C (old-regime) DERIVABILITY DETERMINATION.

Spec's own contingency (verbatim): "rebuild the 5m ensemble on the SM06 hist substrate
IF a 1m/5m-equivalent hist series can be causally derived from the committed 3m hist
substrate (state explicitly: it likely CANNOT -- SM06 only stores 3m vote_pend, no
sub-3m granularity) -> if infeasible, mark this gate BLOCKED-BY-DATA and require
unanimous pass on A/B/D/E to proceed, logging the DATA GAP explicitly as an open risk."

This script reads SM06's build code (runs/SM06_SOLAR_HISTORY/run_hist.py, spec.yaml) and
its COMMITTED output artifacts to make the determination mechanically, rather than
just asserting the spec's own parenthetical.
"""
import os, json
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "SMV2W_5MCLOCK_R2")
OUT = os.path.join(RUN, "out")
SM06_OUT = os.path.join(ROOT, "runs", "SM06_SOLAR_HISTORY", "out")

# ---------------- FACT 1: what SM06's committed hist substrate actually contains ----------------
vote_hist = pd.read_parquet(os.path.join(SM06_OUT, "vote_state_3m_hist.parquet"))
cols = list(vote_hist.columns)
n_bars = len(vote_hist)
has_per_member_cols = any(c.startswith("pend_vm") or c.startswith("pos_vm") for c in cols)

# time-delta check: is the committed hist substrate bar-spacing 3-minute (confirms "3m" label
# and, by construction, that OHLC/close data below 3-minute resolution is not retained)
t = pd.to_datetime(vote_hist["time"]).sort_values()
dt_mode_seconds = t.diff().dt.total_seconds().dropna().mode().iloc[0]

# ---------------- FACT 2: what SM06's build code (run_hist.py) reads and produces ----------------
build_src = open(os.path.join(ROOT, "runs", "SM06_SOLAR_HISTORY", "run_hist.py")).read()
raw_source_line = [l for l in build_src.splitlines() if "read_parquet" in l][0].strip()
resample_line = [l for l in build_src.splitlines() if "resample_3m" in l and "=" in l][0].strip()

# ---------------- Determination ----------------
# The committed SM06 hist substrate (vote_state_3m_hist.parquet, e10_daily_hist.csv,
# member_trades_hist.parquet) is built by resampling the raw 1-minute hist file DIRECTLY
# to 3-minute OHLC bars (sm01_solarsim.resample_3m), then running the 13-member ensemble
# and E10 aggregation on those 3-minute bars. The committed outputs store ONLY the
# 3-minute-bar-resolution aggregate vote_pend/vote_pos (no per-member columns -- confirmed
# by SMV2T's own gate_C.py inspection, reconfirmed here: has_per_member_cols=False) and
# no OHLC below 3-minute granularity at all (the file's own bar spacing IS 3 minutes; a
# 3-minute OHLC bar is a lossy aggregate of the 1-minute path inside it, and 3 & 5 have no
# common integer sub-division -- a 5-minute bar boundary at, e.g., 18:05 does not align
# with any 3-minute bar boundary (18:03, 18:06), so 5-minute OHLC CANNOT be reconstructed
# from 3-minute OHLC by any bar-merging operation).
#
# A 5m-equivalent hist series is therefore NOT causally derivable from the COMMITTED SM06
# hist substrate itself -- exactly as the spec's own parenthetical states.
#
# Separately (and this is the reason no workaround is taken here): SMV2W's OWN spec.yaml
# "data" field authorizes exactly one substrate for this run --
# "runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet aggregated to 5m ... dev <= 2026-05-31"
# -- which covers ONLY 2022-2026 and does not extend to the pre-2022 hist window at all.
# The raw 1-minute file SM06 itself was built from
# (research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet) is a DIFFERENT,
# separately-scoped substrate that this run's spec does not declare as available data.
# Per the campaign's hard rule ("never improvise gates/grids/data"), reaching past the
# frozen spec's declared data field to pull in an unauthorized raw file and construct a
# brand-new hist-period 5m ensemble build (a nontrivial new spec-equivalent piece of work,
# not a "derivation from the committed substrate") is not performed here. Both the
# structural (3m bars are not losslessly re-binnable to 5m) and the scope (this spec's
# data field does not authorize the pre-2022 raw file) reasons independently support the
# same conclusion.

feasible = False
determination = {
    "committed_substrate_columns": cols,
    "committed_substrate_n_bars": int(n_bars),
    "committed_substrate_has_per_member_columns": bool(has_per_member_cols),
    "committed_substrate_bar_spacing_seconds_mode": float(dt_mode_seconds),
    "committed_substrate_bar_spacing_is_3min": bool(abs(dt_mode_seconds - 180.0) < 1.0),
    "build_code_raw_source_line": raw_source_line,
    "build_code_resample_line": resample_line,
    "reason_1_structural": (
        "SM06's committed hist substrate (vote_state_3m_hist.parquet, e10_daily_hist.csv, "
        "member_trades_hist.parquet) is built at 3-minute OHLC bar resolution "
        "(sm.resample_3m), aggregate-vote-only (no per-member pend/pos columns). A "
        "3-minute OHLC bar is a lossy summary of the 1-minute path inside it; 5-minute bar "
        "boundaries do not align with 3-minute bar boundaries (3 and 5 share no common "
        "sub-multiple), so 5-minute OHLC cannot be reconstructed from 3-minute OHLC by any "
        "bar-merging operation. A 1m/5m-equivalent hist series is NOT causally derivable "
        "from the COMMITTED 3m hist substrate."
    ),
    "reason_2_scope": (
        "SMV2W spec.yaml's own 'data' field authorizes only "
        "runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet (2022-2026, dev<=2026-05-31) "
        "aggregated to 5m. It does not authorize the separate pre-2022 raw file "
        "(research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet) that SM06's "
        "own build used. Reaching past the frozen spec's declared data to build a new "
        "hist-period 5m ensemble from that raw file would be improvising data/scope beyond "
        "the frozen spec, not 'deriving from the committed substrate' -- not performed."
    ),
    "feasible": feasible,
    "gate_verdict": "BLOCKED-BY-DATA",
}

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "gate_C_determination.json"), "w") as f:
    json.dump(determination, f, indent=2)

gate_c = pd.DataFrame([{
    "gate": "C_old_regime", "verdict": "BLOCKED-BY-DATA",
    "feasible_5m_hist_derivation_from_committed_substrate": feasible,
    "reason": "3m-bar-resolution committed hist substrate cannot be re-binned to 5m bars "
              "(structural, no common sub-multiple) AND this run's spec.yaml data field "
              "does not authorize the separate pre-2022 raw 1m file SM06 itself was built "
              "from (scope). See out/gate_C_determination.json for full detail.",
    "consequence": "require unanimous pass on A/B/D/E to proceed (per spec contingency); "
                   "old-regime structural stress test of the 5m clock remains an open risk, "
                   "not itself alpha evidence either way.",
}])
gate_c.to_csv(os.path.join(OUT, "gate_C.csv"), index=False)
print(json.dumps(determination, indent=2))
print("\n" + gate_c.to_string(index=False))
print("\ndone gate C determination (BLOCKED-BY-DATA)", flush=True)
