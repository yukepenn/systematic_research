"""U6 shared substrate: load u0_state_table.parquet, build the causal feature list (once), the
block-level net_pnl table, and the PA0-consistent forward-20-bar-per-contract target at every
ENTRY/SCALE_IN bar. Imported by 01/02 scripts -- no other run's ledger is read, per spec.yaml."""
import os
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
U0_PATH = os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet")
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

FWD = 20  # PA0's own forward-bar window (02_exposure_path.py)


def load():
    df = pd.read_parquet(U0_PATH)
    assert (df["t_idx"].to_numpy() == np.arange(len(df))).all(), "t_idx must be 0..n-1 sequential"
    df = df.sort_values("t_idx").reset_index(drop=True)
    return df


def build_causal_features(df):
    """All features are read directly off the row they're evaluated on -- u0_state_table's own
    columns are already built causally (UNIFIED_STATE_MAP.md 'Correctness discipline'); no new
    look-ahead is introduced by orienting/aligning them to trade direction here."""
    pos = df["target_exposure_A"].to_numpy()
    sign = np.sign(pos).astype(float)
    sign_safe = np.where(sign == 0, np.nan, sign)  # undefined orientation on flat bars (unused there)

    out = pd.DataFrame(index=df.index)
    out["t_idx"] = df["t_idx"]
    out["m_abs"] = df["M_A_raw"].abs()
    out["slope_aligned"] = df["M_slope_20"] * sign_safe
    # vote_dispersion = n_bullish-n_bearish across the 13-member Solar13 ensemble (a net-vote
    # measure, not a spread, despite the name -- U0 build script line 322). Raw/signed is NOT
    # directionally meaningful pooled across long+short blocks (positive=bullish consensus is
    # "agreement" for longs but "disagreement" for shorts) -- SA0's own 02_ensemble.py established
    # convention (sec7) uses |vote_dispersion| (magnitude/conviction) as primary and a separate
    # sign-match-rate check, not a raw pooled value. We follow that convention here: aligned
    # (signed, oriented to trade direction -- consensus FOR this trade's own side) and abs
    # (direction-agnostic ensemble conviction strength) both constructed; raw kept only for
    # reference, not used as a test feature (see CAUSAL_FEATURES_* below).
    out["vote_dispersion_raw"] = df["vote_dispersion"]
    out["vote_dispersion_aligned"] = df["vote_dispersion"] * sign_safe
    out["vote_dispersion_abs"] = df["vote_dispersion"].abs()
    out["b_aligned"] = df["B"] * sign_safe
    out["b_abs"] = df["B"].abs()  # direction-agnostic B-MOM engagement magnitude (added after
    # step2 first-pass found a U-shaped, not monotonic-aligned, relationship -- see 02 script note
    out["htf_agree_code"] = df["HTF_tilt_state"] * sign_safe  # +1 agree / 0 neutral / -1 disagree
    out["age_bars_A"] = df["age_bars_A"]
    out["sigma460"] = df["sigma460_atr_proxy_pts"]
    out["session_phase"] = df["session_phase"]
    out["is_rth"] = df["is_rth"]
    return out


def build_block_table(df):
    """One row per nonzero block_id_A (position != 0 at block start): start t_idx, end t_idx,
    start year / is_health_only_bar, start |exposure|, max|exposure| ever reached, net_pnl
    (= cumulative bar_pnl_A_dollars = last run_pnl_A_dollars in the block, verified equal)."""
    nz = df[df["target_exposure_A"] != 0].copy()
    g = nz.groupby("block_id_A")
    starts = df[df["age_bars_A"] == 1]
    starts = starts[starts["target_exposure_A"] != 0].set_index("block_id_A")

    block = pd.DataFrame({
        "block_id_A": g.size().index,
        "n_bars": g.size().to_numpy(),
        "t_idx_start": g["t_idx"].min().to_numpy(),
        "t_idx_end": g["t_idx"].max().to_numpy(),
        "start_exposure": g["target_exposure_A"].apply(lambda s: s.iloc[0]).to_numpy(),
        "max_abs_exposure": g["target_exposure_A"].apply(lambda s: s.abs().max()).to_numpy(),
        "net_pnl": g["bar_pnl_A_dollars"].sum().to_numpy(),
    }).set_index("block_id_A")

    # cross-check: net_pnl must equal last run_pnl_A_dollars in the block
    last_run_pnl = g["run_pnl_A_dollars"].apply(lambda s: s.iloc[-1])
    diff = (block["net_pnl"] - last_run_pnl).abs()
    assert diff.max() < 1e-6, f"net_pnl vs run_pnl_A_dollars mismatch, max diff {diff.max()}"

    block["start_year"] = starts["year"].reindex(block.index)
    block["start_is_health_only"] = starts["is_health_only_bar"].reindex(block.index)
    block["start_sess_date"] = starts["sess_date"].reindex(block.index)
    return block.reset_index()


def build_entry_scaling_events(df, feat):
    """ENTRY and SCALE_IN bars with the PA0-consistent forward-20-bar-per-contract target
    (contracts_changed = ABS(position delta), matching PA0 02_exposure_path.py line 71 exactly)."""
    pos = df["target_exposure_A"].to_numpy()
    bpnl = df["bar_pnl_A_dollars"].to_numpy()
    n = len(df)

    is_event = df["action_A"].isin(["ENTRY", "SCALE_IN"]).to_numpy()
    idx = np.where(is_event)[0]
    idx = idx[idx > 0]  # need a t-1

    contracts_changed = np.abs(pos[idx] - pos[idx - 1])
    fwd20 = np.array([bpnl[t: min(t + FWD, n)].sum() for t in idx])
    per_contract = fwd20 / contracts_changed

    ev = pd.DataFrame({
        "t_idx": idx,
        "action_A": df["action_A"].to_numpy()[idx],
        "block_id_A": df["block_id_A"].to_numpy()[idx],
        "contracts_changed": contracts_changed,
        "fwd20_pnl": fwd20,
        "fwd20_pnl_per_contract": per_contract,
        "is_scale_in": (df["action_A"].to_numpy()[idx] == "SCALE_IN").astype(int),
    })
    ev = ev.merge(feat, on="t_idx", how="left")

    # m_abs_vs_entry: |M_A_raw| at this bar minus |M_A_raw| at the SAME block's own entry bar
    entry_rows = df[(df["age_bars_A"] == 1) & (df["target_exposure_A"] != 0)][["block_id_A", "t_idx"]]
    entry_m_abs_by_tidx = feat.set_index("t_idx")["m_abs"]
    entry_m_abs_by_block = entry_rows["t_idx"].map(entry_m_abs_by_tidx)
    entry_m_abs_by_block.index = entry_rows["block_id_A"].to_numpy()
    ev["entry_m_abs"] = ev["block_id_A"].map(entry_m_abs_by_block)
    ev["m_abs_vs_entry"] = ev["m_abs"] - ev["entry_m_abs"]

    ev["start_year"] = df["year"].to_numpy()[idx]
    ev["is_health_only_bar"] = df["is_health_only_bar"].to_numpy()[idx]
    return ev


CAUSAL_FEATURES_STEP1 = ["m_abs", "m_abs_vs_entry", "slope_aligned", "vote_dispersion_aligned",
                          "vote_dispersion_abs", "b_aligned", "b_abs", "htf_agree_code",
                          "age_bars_A", "sigma460"]
CAUSAL_FEATURES_STEP2 = ["m_abs", "slope_aligned", "vote_dispersion_aligned", "vote_dispersion_abs",
                          "b_aligned", "b_abs", "htf_agree_code", "sigma460"]  # age_bars_A dropped: ==1 by construction


if __name__ == "__main__":
    df = load()
    feat = build_causal_features(df)
    block = build_block_table(df)
    ev = build_entry_scaling_events(df, feat)
    print(f"loaded {len(df)} bars, {len(block)} nonzero blocks, {len(ev)} ENTRY/SCALE_IN events")
    print(ev["action_A"].value_counts())
    feat.to_parquet(os.path.join(OUT, "u6_causal_features.parquet"))
    block.to_csv(os.path.join(OUT, "u6_block_table.csv"), index=False)
    ev.to_csv(os.path.join(OUT, "u6_entry_scale_events.csv"), index=False)
    print("substrate build complete.")
