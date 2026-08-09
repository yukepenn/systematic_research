"""U8 shared substrate: load u0_state_table.parquet, build the 6 preregistered causal path-
organization features (reversal_rate/run_persistence/perm_entropy x {10,20}-bar window), verify
them against hand-computed synthetic cases, and export a slim table + block-level frames reused
by every downstream script. No new backtest logic, no new pricing -- reads u0_state_table.parquet
only and adds descriptive columns on top, matching U4/U6's own convention."""
import os
import numpy as np
import pandas as pd
from itertools import permutations

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
U0_PATH = os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet")
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

WINDOWS = [10, 20]

# ---------------------------------------------------------------------------
# permutation-id lookup: 6 permutations of (0,1,2) encoded as order[0]*9+order[1]*3+order[2]
# ---------------------------------------------------------------------------
PERM_LOOKUP = {p[0] * 9 + p[1] * 3 + p[2]: i for i, p in enumerate(permutations([0, 1, 2]))}


def sign_transition_series(ret_1):
    """transition[i] = 1{sign(ret_1[i]) != sign(ret_1[i-1])}, NaN if either side undefined.
    sign in {-1,0,1}; a bar-to-bar tie (ret_1==0) is its own category (standard convention)."""
    sr = np.sign(ret_1)
    n = len(sr)
    transition = np.full(n, np.nan)
    valid = np.zeros(n, dtype=bool)
    valid[1:] = ~np.isnan(sr[1:]) & ~np.isnan(sr[:-1])
    transition[valid] = (sr[1:][valid[1:]] != sr[:-1][valid[1:]]).astype(float)
    return transition


def reversal_rate_and_run_persistence(ret_1, W):
    """Causal, window [t-W+1, t] inclusive. reversal_rate = fraction of the W-1 internal bar-to-
    bar transitions that are sign flips. run_persistence = mean run length = W / (1 + #transitions)."""
    transition = sign_transition_series(ret_1)
    roll = pd.Series(transition).rolling(W - 1, min_periods=W - 1).sum().to_numpy()
    reversal_rate = roll / (W - 1)
    run_persistence = W / (1.0 + roll)
    return reversal_rate, run_persistence


def perm_entropy_ordinal_ids(close):
    """Bandt-Pompe ordinal pattern id (0-5) of (close[i-2],close[i-1],close[i]) for every i,
    stable-sort tie-break (earlier index ranked lower on ties -- standard BP convention). NaN
    (encoded -1) for i<2."""
    n = len(close)
    pid = np.full(n, -1, dtype=np.int64)
    if n < 3:
        return pid
    windows = np.lib.stride_tricks.sliding_window_view(close, 3)  # shape (n-2, 3), row j = close[j:j+3]
    order = np.argsort(windows, axis=1, kind="stable")  # values in {0,1,2}
    code = order[:, 0] * 9 + order[:, 1] * 3 + order[:, 2]
    ids = np.vectorize(PERM_LOOKUP.get)(code)
    pid[2:] = ids
    return pid


def perm_entropy_windowed(close, W):
    """Normalized (0..1) Shannon entropy of the ordinal-pattern-class distribution over the
    trailing W-2 triples within window [t-W+1, t] inclusive. Causal, requires the FULL W-2
    triples to be valid (min_periods = W-2), else NaN."""
    n = len(close)
    pid = perm_entropy_ordinal_ids(close)
    onehot = np.full((n, 6), np.nan)
    valid = pid >= 0
    onehot[valid] = 0.0
    onehot[valid, pid[valid]] = 1.0
    win = W - 2
    counts = pd.DataFrame(onehot).rolling(win, min_periods=win).sum().to_numpy()
    total = win
    probs = counts / total
    with np.errstate(divide="ignore", invalid="ignore"):
        term = np.where(probs > 0, probs * np.log2(probs), 0.0)
    ent = -term.sum(axis=1)
    ent[np.isnan(counts).any(axis=1)] = np.nan
    return ent / np.log2(6)


def _self_test():
    print("[U8 substrate] running synthetic self-tests ...", flush=True)
    # Case 1: strictly monotonic increasing close -> zero reversals, max run persistence, zero entropy
    close_mono = np.arange(1.0, 61.0)
    ret1_mono = np.r_[np.nan, np.diff(close_mono)]
    rr, rp = reversal_rate_and_run_persistence(ret1_mono, 20)
    pe = perm_entropy_windowed(close_mono, 20)
    assert np.isclose(rr[40], 0.0), f"monotonic reversal_rate expected 0, got {rr[40]}"
    assert np.isclose(rp[40], 20.0), f"monotonic run_persistence expected 20, got {rp[40]}"
    assert np.isclose(pe[40], 0.0, atol=1e-9), f"monotonic perm_entropy expected 0, got {pe[40]}"
    print(f"  monotonic-increasing @ t=40: reversal_rate={rr[40]:.4f} run_persistence={rp[40]:.4f} "
          f"perm_entropy={pe[40]:.6f}  (expected 0.0000 / 20.0000 / 0.000000) OK")

    # Case 2: perfectly alternating (period-2, no ties) -> reversal on every internal transition
    close_alt = np.array([0.0, 10.0, 1.0, 11.0, 2.0, 12.0, 3.0, 13.0, 4.0, 14.0,
                           5.0, 15.0, 6.0, 16.0, 7.0, 17.0, 8.0, 18.0, 9.0, 19.0,
                           10.0, 20.0, 11.0, 21.0])
    ret1_alt = np.r_[np.nan, np.diff(close_alt)]
    rr2, rp2 = reversal_rate_and_run_persistence(ret1_alt, 10)
    assert np.isclose(rr2[20], 1.0), f"alternating reversal_rate expected 1.0, got {rr2[20]}"
    assert np.isclose(rp2[20], 1.0), f"alternating run_persistence expected 1.0, got {rp2[20]}"
    print(f"  perfectly-alternating @ t=20: reversal_rate={rr2[20]:.4f} run_persistence={rp2[20]:.4f} "
          f"(expected 1.0000 / 1.0000) OK")
    print("[U8 substrate] self-tests passed.\n")


_self_test()

# ---------------------------------------------------------------------------
# build on the real table
# ---------------------------------------------------------------------------
COLS = [
    "t_idx", "sess_date", "hm", "year", "is_health_only_bar", "close",
    "M", "M_A_raw", "ret_1", "sigma460_atr_proxy_pts",
    "trend_efficiency_20", "range_efficiency_20",
    "position_B", "action_B", "block_id_B", "age_bars_B",
    "run_pnl_B_dollars", "bar_pnl_B_nq_dollars",
    "target_exposure_A", "action_A", "block_id_A", "age_bars_A",
    "run_pnl_A_dollars", "bar_pnl_A_dollars",
]


def load_with_features():
    print("[U8 substrate] loading U0 state table ...", flush=True)
    df = pd.read_parquet(U0_PATH, columns=COLS)
    df = df.sort_values("t_idx").reset_index(drop=True)
    assert (df["t_idx"].to_numpy() == np.arange(len(df))).all(), "t_idx must be 0..n-1 sequential"
    n = len(df)
    print(f"  {n} rows, {df['sess_date'].nunique()} sessions")

    close = df["close"].to_numpy()
    ret_1 = df["ret_1"].to_numpy()

    print("[U8 substrate] building reversal_rate / run_persistence (10, 20 bar) ...", flush=True)
    for W in WINDOWS:
        rr, rp = reversal_rate_and_run_persistence(ret_1, W)
        df[f"reversal_rate_{W}"] = rr
        df[f"run_persistence_{W}"] = rp

    print("[U8 substrate] building permutation entropy (10, 20 bar) -- this is the slow step ...", flush=True)
    for W in WINDOWS:
        df[f"perm_entropy_{W}"] = perm_entropy_windowed(close, W)

    return df


FEATURE_COLS_20 = ["reversal_rate_20", "run_persistence_20", "perm_entropy_20"]
FEATURE_COLS_10 = ["reversal_rate_10", "run_persistence_10", "perm_entropy_10"]
FEATURE_COLS_ALL = FEATURE_COLS_10 + FEATURE_COLS_20


if __name__ == "__main__":
    df = load_with_features()
    out_path = os.path.join(OUT, "u8_bars_with_features.parquet")
    df.to_parquet(out_path)
    print(f"wrote {out_path} ({df.shape})")
    print(df[FEATURE_COLS_ALL].describe().to_string())
