"""SKEW01 shared substrate: load u0_state_table.parquet, build the causal return-skewness_20
(primary) / skewness_10 (robustness) features on U0's own ret_1 column, verify against
scipy.stats.skew(bias=True) (the standard Fisher-Pearson / third-standardized-moment "moment
coefficient of skewness", g1 -- exactly the construction preregistered in spec.yaml) and hand-
built synthetic cases, then merge in U8's already-computed perm_entropy_20/reversal_rate_20/
run_persistence_20 columns (reused verbatim, not re-derived) for the Step-0 redundancy check.
No new backtest logic, no new pricing -- reads u0_state_table.parquet and
u8_bars_with_features.parquet only, adds descriptive columns on top."""
import os
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
U0_PATH = os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet")
U8_PATH = os.path.join(ROOT, "runs", "U8_PATH_ORGANIZATION", "out", "u8_bars_with_features.parquet")
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

WINDOWS = [10, 20]
EPS = 1e-8  # std-guard, points units, far below NQ's realistic 1-bar tick noise floor


def skewness_windowed(r, W):
    """Causal trailing-W-bar (inclusive of t) Fisher-Pearson moment-coefficient skewness of r
    (here: ret_1). skewness_W(t) = mean((r-mean(r))^3) / std(r)^3 over window [t-W+1, t].
    std is population (ddof=0), consistent with the uncorrected third-moment numerator. NaN if
    the window has any NaN input or std(r) < EPS (degenerate/near-constant window)."""
    n = len(r)
    out = np.full(n, np.nan)
    if n < W:
        return out
    windows = np.lib.stride_tricks.sliding_window_view(r, W)  # shape (n-W+1, W), row j = r[j:j+W]
    mean = windows.mean(axis=1)
    dev = windows - mean[:, None]
    m2 = (dev ** 2).mean(axis=1)
    m3 = (dev ** 3).mean(axis=1)
    std = np.sqrt(m2)
    with np.errstate(invalid="ignore", divide="ignore"):
        skew = m3 / (std ** 3)
    skew[std < EPS] = np.nan
    # any NaN in the raw window (e.g. ret_1[0] is NaN) -> NaN result
    any_nan = np.isnan(windows).any(axis=1)
    skew[any_nan] = np.nan
    out[W - 1:] = skew
    return out


def _self_test():
    print("[SKEW01 substrate] running synthetic self-tests ...", flush=True)
    from scipy import stats as sstats

    rng = np.random.default_rng(20260809)

    # Case 1: symmetric returns (mean-zero, sign-alternating magnitudes) -> skewness ~ 0
    sym = np.tile([1.0, -1.0, 2.0, -2.0, 0.5, -0.5, 1.5, -1.5, 3.0, -3.0], 6)  # len 60, exactly symmetric
    sk = skewness_windowed(sym, 20)
    ref = sstats.skew(sym[20:40], bias=True)
    assert np.isclose(sk[39], ref, atol=1e-9), f"symmetric case mismatch: {sk[39]} vs scipy {ref}"
    assert np.isclose(sk[39], 0.0, atol=1e-9), f"symmetric case expected ~0, got {sk[39]}"
    print(f"  symmetric alternating @ t=39: skewness_20={sk[39]:.6f} (scipy ref={ref:.6f}, expected ~0.0) OK")

    # Case 2: right-skewed synthetic (mostly small negative, one large positive outlier per block
    # of 20) -> positive skewness, cross-checked against scipy.stats.skew(bias=True) exactly
    block = np.array([-1.0] * 19 + [30.0])  # 19 small negatives + 1 large positive outlier
    right = np.tile(block, 3)  # len 60
    sk_r = skewness_windowed(right, 20)
    ref_r = sstats.skew(right[20:40], bias=True)
    assert np.isclose(sk_r[39], ref_r, atol=1e-9), f"right-skew mismatch: {sk_r[39]} vs scipy {ref_r}"
    assert sk_r[39] > 0.5, f"right-skew case expected clearly positive skew, got {sk_r[39]}"
    print(f"  right-skewed (19 small-neg + 1 big-pos) @ t=39: skewness_20={sk_r[39]:.6f} "
          f"(scipy ref={ref_r:.6f}, expected >0) OK")

    # Case 3: left-skewed (mirror of case 2) -> negative skewness
    left = -right
    sk_l = skewness_windowed(left, 20)
    ref_l = sstats.skew(left[20:40], bias=True)
    assert np.isclose(sk_l[39], ref_l, atol=1e-9), f"left-skew mismatch: {sk_l[39]} vs scipy {ref_l}"
    assert sk_l[39] < -0.5, f"left-skew case expected clearly negative skew, got {sk_l[39]}"
    assert np.isclose(sk_l[39], -sk_r[39], atol=1e-9), "left should be exact mirror of right"
    print(f"  left-skewed (mirror of case 2) @ t=39: skewness_20={sk_l[39]:.6f} "
          f"(scipy ref={ref_l:.6f}, expected <0, exact mirror of +{sk_r[39]:.6f}) OK")

    # Case 4: near-constant window (std < EPS) -> NaN, not a divide-by-~0 explosion
    const = np.full(60, 1.2345)
    sk_c = skewness_windowed(const, 20)
    assert np.isnan(sk_c[39]), f"near-constant case expected NaN (std guard), got {sk_c[39]}"
    print(f"  near-constant window @ t=39: skewness_20={sk_c[39]} (expected NaN via std<{EPS} guard) OK")

    # Case 5: random N(0, sigma) noise -> skewness should be small in magnitude on average
    # (sanity check only, not an exact assert -- confirms no systematic bias in the estimator)
    noise = rng.normal(0, 1.0, 5000)
    sk_n = skewness_windowed(noise, 20)
    mean_abs_skew = np.nanmean(np.abs(sk_n))
    print(f"  random N(0,1) noise, mean(|skewness_20|) over {len(sk_n)} windows = {mean_abs_skew:.4f} "
          f"(sanity: should be modest, small-sample noise expected at W=20, no assert)")

    print("[SKEW01 substrate] self-tests passed.\n")


_self_test()

# ---------------------------------------------------------------------------
# build on the real table
# ---------------------------------------------------------------------------
U0_COLS = [
    "t_idx", "sess_date", "hm", "year", "is_health_only_bar", "close",
    "M", "M_A_raw", "M_slope_20", "ret_1", "sigma460_atr_proxy_pts",
    "trend_efficiency_20", "range_efficiency_20",
    "position_B", "action_B", "block_id_B", "age_bars_B",
    "run_pnl_B_dollars", "bar_pnl_B_nq_dollars",
    "target_exposure_A", "action_A", "block_id_A", "age_bars_A",
    "run_pnl_A_dollars", "bar_pnl_A_dollars",
]
U8_COLS = ["t_idx", "perm_entropy_20", "reversal_rate_20", "run_persistence_20"]


def load_with_features():
    print("[SKEW01 substrate] loading U0 state table ...", flush=True)
    df = pd.read_parquet(U0_PATH, columns=U0_COLS)
    df = df.sort_values("t_idx").reset_index(drop=True)
    assert (df["t_idx"].to_numpy() == np.arange(len(df))).all(), "t_idx must be 0..n-1 sequential"
    n = len(df)
    print(f"  {n} rows, {df['sess_date'].nunique()} sessions")

    ret_1 = df["ret_1"].to_numpy()

    print("[SKEW01 substrate] building skewness_10 / skewness_20 (causal, trailing ret_1) ...", flush=True)
    for W in WINDOWS:
        df[f"skewness_{W}"] = skewness_windowed(ret_1, W)

    n_valid_20 = df["skewness_20"].notna().sum()
    n_nan_std_guard_20 = int(((df["skewness_20"].isna()) & (df["ret_1"].notna()) &
                               (df["t_idx"] >= 19)).sum())
    print(f"  skewness_20: {n_valid_20}/{n} valid, describe:\n{df['skewness_20'].describe().to_string()}")
    print(f"  (of the NaN rows with a fully-populated ret_1 window, {n_nan_std_guard_20} triggered "
          f"the std<{EPS} degenerate-window guard or leading-window insufficiency)")

    print("[SKEW01 substrate] merging U8's already-computed perm_entropy_20/reversal_rate_20/"
          "run_persistence_20 (reused verbatim, not re-derived) ...", flush=True)
    u8 = pd.read_parquet(U8_PATH, columns=U8_COLS)
    before = len(df)
    df = df.merge(u8, on="t_idx", how="left", validate="one_to_one")
    assert len(df) == before, "merge must not change row count"
    print(f"  merged; perm_entropy_20 non-null: {df['perm_entropy_20'].notna().sum()}")

    return df


FEATURE_COLS = ["skewness_10", "skewness_20"]

if __name__ == "__main__":
    df = load_with_features()
    out_path = os.path.join(OUT, "skew01_bars_with_features.parquet")
    df.to_parquet(out_path)
    print(f"wrote {out_path} ({df.shape})")
