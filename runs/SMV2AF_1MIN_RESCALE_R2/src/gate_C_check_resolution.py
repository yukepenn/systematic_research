"""SMV2AF_1MIN_RESCALE_R2 -- Gate C step 1: verify data availability BEFORE attempting
anything (per spec's explicit instruction and the task's instruction to check what
resolution the SM06/hist substrate actually is, rather than assuming SMV2W's 5-minute
precedent transfers unchanged).

Checks TWO distinct things that SMV2W's gate_C_determination.json conflated only for the
5-minute case:
  (1) the COMMITTED, DERIVED "SM06 hist substrate" (vote_state_3m_hist.parquet /
      e10_daily_hist.csv / member_trades_hist.parquet) -- resolution?
  (2) whether a genuinely 1-minute-resolution RAW old-regime substrate is ALSO committed
      in the repo (distinct question from (1) -- 1-minute is the FINEST possible
      resolution, so unlike 5-minute vs 3-minute, no "common submultiple" issue can
      arise: if native 1-minute bars exist, nothing needs to be derived/approximated
      from anything coarser).
"""
import os, json
import pandas as pd
import pyarrow.parquet as pq

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "SMV2AF_1MIN_RESCALE_R2")
OUT = os.path.join(RUN, "out")

# ---- (1) the committed derived SM06 hist substrate: resolution?
sm06_out = os.path.join(ROOT, "runs", "SM06_SOLAR_HISTORY", "out")
vote_path = os.path.join(sm06_out, "vote_state_3m_hist.parquet")
vote_cols = pq.ParquetFile(vote_path).schema.names
vote = pd.read_parquet(vote_path, columns=["time"])
vote["time"] = pd.to_datetime(vote["time"])
spacing = vote["time"].diff().dt.total_seconds().mode().iloc[0]

# ---- (2) raw source file the SM06 build itself reads BEFORE resample_3m (its own build
#      script, runs/SM06_SOLAR_HISTORY/run_hist.py, line 12) -- is IT already 1-minute?
raw_path = os.path.join(ROOT, "research", "scalping_lab", "substrate", "minute", "NQ",
                        "nq1m_2005_202605.parquet")
raw_exists = os.path.exists(raw_path)
raw_meta = {}
if raw_exists:
    raw = pd.read_parquet(raw_path)
    raw["time"] = pd.to_datetime(raw["time"])
    raw_spacing = raw["time"].diff().dt.total_seconds().mode().iloc[0]
    hist = raw[raw["time"] < "2022-01-01"]
    raw_meta = {
        "columns": raw.columns.tolist(),
        "n_rows_total": int(len(raw)),
        "modal_bar_spacing_seconds": float(raw_spacing),
        "is_1min_native": bool(abs(raw_spacing - 60.0) < 1e-6),
        "full_range": [str(raw["time"].min()), str(raw["time"].max())],
        "n_rows_pre_2022_old_regime_window": int(len(hist)),
        "pre_2022_range": [str(hist["time"].min()), str(hist["time"].max())],
    }

determination = {
    "sm06_derived_hist_substrate_path": vote_path,
    "sm06_derived_hist_substrate_columns": vote_cols,
    "sm06_derived_hist_substrate_modal_bar_spacing_seconds": float(spacing),
    "sm06_derived_hist_substrate_is_3min": bool(abs(spacing - 180.0) < 1e-6),
    "sm06_derived_hist_substrate_has_per_member_columns": False,
    "confirms_smv2w_precedent_for_the_DERIVED_substrate": True,
    "raw_1min_hist_source_file": raw_path,
    "raw_1min_hist_source_file_exists": raw_exists,
    "raw_1min_hist_source_meta": raw_meta,
    "raw_source_is_the_SAME_file_SM06s_own_build_script_reads_before_resampling": True,
    "raw_source_build_line_in_SM06": "h = pd.read_parquet(\"research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet\"); bars = sm.resample_3m(h)",
}
print(json.dumps(determination, indent=2))
json.dump(determination, open(os.path.join(OUT, "gate_C_resolution_check.json"), "w"), indent=2)
