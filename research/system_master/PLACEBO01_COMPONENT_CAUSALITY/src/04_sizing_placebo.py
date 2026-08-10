"""PLACEBO01 -- 04_sizing_placebo.py

Product-A SIZING causal placebo test (campaign directive sec44-50: falsification, not an alpha
trial). Question: does Product A's |target| exposure-magnitude mapping (0-13 contracts) do real
causal work beyond DIRECTION/TIMING plus a proportional-exposure histogram, or is the specific
size chosen on a given bar interchangeable (within a matched stratum) with a randomly-assigned
size from the same aggregate distribution?

REUSE (per governance instructions -- do not reinvent):
  - Incumbent Product-A reconstruction: runs/U0_UNIFIED_STATE/out/u0_state_table.parquet
    ('target_exposure_A' column == pa0_substrate.product_a_exec's own bar_pos array, byte-
    verified below against the certified canonical-window net BEFORE any placebo is touched).
  - Fill/commission primitive: sm01_solarsim._fill (imported verbatim, not reimplemented) with
    Product A's own certified constants PV_MNQ=2.0, COMM_MNQ=0.65 (sm01_solarsim.MNQ_POINT_VALUE
    / MNQ_COMM_SIDE).
  - Sharpe/Sortino/Calmar/CDaR/maxDD/turnover battery: src/analytics/smv2_common.dd_battery
    (used for daily-net context columns only; not one of the three headline metrics).
  - CANONICAL_MATHEMATICAL_SPEC.md constants (KSolar/KBmom/TiltRescale/ss) are NOT touched here --
    this script never re-derives or perturbs the decoder; it only permutes the REALIZED |size|
    label across bars within a stratum, holding direction/timing fixed.

PREREGISTRATION (written to out/ by write_preregistration(), called FIRST, before any data is
loaded or any placebo is run -- see out/PREREGISTRATION.md / out/preregistration.json):
  - N_RANDOMIZATIONS = 500 (>= 200 minimum per directive)
  - SEED_FAMILY: seed_i = 20260810 + i, for i in range(500)  (deterministic, disclosed, no
    time-seeded or unseeded RNG anywhere in this script)
  - NULL CONSTRUCTION: stratify nonzero-direction canonical bars by
      (direction in {long, short}) x (session_phase, the 7-way U0 causal clock label) x
      (volatility tercile of sigma460_atr_proxy_pts) x (Solar-conviction tercile of |Tp|),
    then, independently within EACH stratum, apply a uniform random permutation (via the
    replicate's seeded Generator) of the REAL |target_exposure_A| values observed in that
    stratum across the bars of that stratum. Direction, timing (which bars are long/short/flat),
    and the exact GLOBAL histogram of |target_exposure_A| are all preserved exactly by
    construction (permutation is within-stratum and bijective) -- only the pairing of "this bar's
    size" to "this bar's realized market outcome" is broken, and only within the coarse
    stratification cells (i.e., the null is NOT allowed to reassign size across a direction flip,
    a different session-phase, a different vol regime, or a different conviction regime -- it is
    a FINE-GRAINED, WITHIN-REGIME resampling test).

CORRECTNESS GATE (mandatory, run before any placebo touches the data): reconstruct Product A's
own bar-level P&L from the realized 'target_exposure_A' path using a from-scratch, from-given-
position executor (loop_exec, below) built on sm01_solarsim._fill, and require its canonical-
window net to match the certified Product-A net (177924.40, EQV02/PA0/U0-certified) to within
$1 -- and, as an extra rigor check beyond the task's minimum bar, require the reconstructed
bar_pnl array to be BIT-IDENTICAL to U0's own certified 'bar_pnl_A_dollars' column (verified
0.0 max abs diff on 2026-08-10). This proves loop_exec is a faithful re-expression of the
certified execution model before it is trusted to price any placebo path.
"""
import os
import sys
import json
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from sm01_solarsim import _fill, MNQ_POINT_VALUE, MNQ_COMM_SIDE  # noqa: E402  (verbatim reuse)
from smv2_common import dd_battery  # noqa: E402  (verbatim reuse)

RUN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(RUN_DIR, "out")
os.makedirs(OUT, exist_ok=True)

U0_PATH = os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet")

PV_MNQ = MNQ_POINT_VALUE   # 2.0  -- Product A's certified per-contract $/point
COMM_MNQ = MNQ_COMM_SIDE   # 0.65 -- Product A's certified $/contract/side commission
CERTIFIED_CANON_NET_A = 177924.40
BAR_MINUTES = 3.0
BAR_HOURS = BAR_MINUTES / 60.0

N_RANDOMIZATIONS = 500
SEED_BASE = 20260810
MIN_BARS_PER_K = 30           # disclosed minimum bar count for a size level k to enter the
                               # marginal-exposure-value gradient regression


# ============================================================================ 0. PREREGISTRATION
def write_preregistration():
    prereg = {
        "written_utc_note": "written FIRST, before any data load or placebo randomization",
        "task": "Product-A sizing causal placebo test (campaign directive sec44-50)",
        "n_randomizations": N_RANDOMIZATIONS,
        "seed_family": f"seed_i = {SEED_BASE} + i, for i in range(0, {N_RANDOMIZATIONS})",
        "rng": "numpy.random.default_rng(seed_i), one fresh Generator per replicate, no "
               "time-seeded or unseeded randomness anywhere in this script",
        "stratification_factors": [
            "direction: sign(target_exposure_A) in {long(+1), short(-1)} -- flat (0) bars are "
            "excluded from the permutation universe (no size to permute when flat)",
            "session_phase: U0's own causal 7-level clock label (RTH_OPEN, RTH_MID, RTH_CLOSE, "
            "US_PREMARKET, ETH_EUROPE, ETH_ASIA, POST_RTH), used as-is, not rebinned",
            "volatility tercile: tercile of sigma460_atr_proxy_pts (the causal 460-bar rolling "
            "|dClose| ATR proxy that feeds the incumbent Solar member ensemble), tercile edges "
            "computed once from the nonzero-direction canonical population "
            "(<= q1 low, (q1,q2] mid, > q2 high)",
            "Solar-conviction tercile: tercile of |Tp| (the tilt-adjusted Solar-ensemble score "
            "stored in the U0 table; identical formula to Product A's own Tpp except it omits "
            "Product A's short-halving 'ss' term -- disclosed simplification, stratification-"
            "only, does not touch execution), same edge convention as volatility",
        ],
        "null_construction": (
            "Within each of the (direction x session_phase x vol_tercile x conviction_tercile) "
            "strata, independently apply a uniform random permutation (numpy Generator.permutation) "
            "to the REAL |target_exposure_A| values observed at the bars belonging to that stratum, "
            "reassigning them across those same bars. Direction and bar timing are untouched -- "
            "only the |size| label is reshuffled, and only among bars that already share direction, "
            "session-phase, volatility regime, and Solar-conviction regime with each other. This "
            "preserves the GLOBAL histogram of |target_exposure_A| exactly (a bijection within each "
            "stratum, strata partition the nonzero population), and preserves direction/timing "
            "exactly, while breaking the specific pairing of 'this bar's size' to 'this bar's "
            "realized market outcome' beyond what the coarse stratum already controls for."
        ),
        "metrics_per_replicate": [
            "PnL/contract = net PnL / total contracts traded (sum |delta position| over all bars)",
            "PnL/exposure-hour = net PnL / total exposure-hours (sum |position| x 3-min bar "
            "duration in hours)",
            "marginal-exposure-value gradient = weighted-least-squares slope, across contract "
            "levels k=1..K_max (weight = bar count n_k, minimum n_k >= 30 to enter the fit), of "
            "avg_unit_pnl(k) := mean(bar_pnl[t] / |position[t]|) over bars with |position[t]|==k, "
            "regressed on k. A positive slope means bars where the REAL/placebo system carried a "
            "larger size were, on average, more profitable per contract than bars carrying a "
            "smaller size (disclosed as APPROXIMATE: bar_pnl on a bar where the position changed "
            "mixes the markout of pre-existing and newly-added contracts; see script docstring).",
        ],
        "comparison": (
            "Empirical percentile of the REAL system's value for each metric within its own "
            "500-replicate null distribution: percentile = 100 * mean(null_values <= real_value). "
            "Reported for all three metrics; no single yes/no beats-placebo verdict is treated as "
            "sufficient on its own."
        ),
        "correctness_gate": (
            "Reconstruct Product A's realized bar-level P&L from 'target_exposure_A' via loop_exec "
            "(built on sm01_solarsim._fill) and require canonical-window net to match the certified "
            f"{CERTIFIED_CANON_NET_A} to within $1 AND require the reconstructed bar_pnl array to "
            "be bit-identical to U0's own certified bar_pnl_A_dollars column, BEFORE any placebo "
            "replicate is run."
        ),
        "decided_before_looking_at_any_placebo_result": True,
    }
    with open(os.path.join(OUT, "preregistration.json"), "w") as f:
        json.dump(prereg, f, indent=2, default=str)
    md = ["# PLACEBO01 sizing placebo -- PREREGISTRATION",
          "",
          "Written before any data load or placebo randomization. See `preregistration.json` for",
          "the machine-readable version (identical content).",
          "",
          f"- N randomizations: **{N_RANDOMIZATIONS}**",
          f"- Seed family: **seed_i = {SEED_BASE} + i, for i in range(0, {N_RANDOMIZATIONS})**",
          "- Null construction: within-stratum permutation of |target_exposure_A| "
          "(direction x session_phase x vol tercile x Solar-conviction tercile); direction/timing "
          "and the global size histogram are preserved exactly.",
          "- Metrics: PnL/contract, PnL/exposure-hour, marginal-exposure-value WLS gradient.",
          "- Comparison: empirical percentile of the real system within its own null distribution, "
          "for each metric separately.",
          "- Correctness gate: loop_exec on the real target_exposure_A path must reproduce the "
          f"certified canonical net ({CERTIFIED_CANON_NET_A}) to within $1 and be bit-identical to "
          "U0's own bar_pnl_A_dollars column.",
          ""]
    with open(os.path.join(OUT, "PREREGISTRATION.md"), "w") as f:
        f.write("\n".join(md))
    print("[PLACEBO01] preregistration written to out/PREREGISTRATION.md / preregistration.json",
          flush=True)
    return prereg


# ============================================================================ 1. DATA LOAD
def load_canonical():
    df = pd.read_parquet(U0_PATH)
    canon = df[~df["is_health_only_bar"]].sort_values("t_idx").reset_index(drop=True)
    sess = canon["sess_date"].to_numpy()
    is_last = (sess != np.roll(sess, -1))
    is_last[-1] = True
    canon = canon.assign(is_last_of_sess=is_last)
    print(f"[PLACEBO01] canonical bars: {len(canon)}  "
          f"{canon['time'].min()} .. {canon['time'].max()}  "
          f"sessions={canon['sess_date'].nunique()}", flush=True)
    return canon


# ============================================================================ 2. EXECUTOR
def loop_exec(pos_target, open_, high, low, close, is_last, sess, comm=COMM_MNQ, pv=PV_MNQ):
    """From-GIVEN-realized-position executor. pos_target[t] is treated as the position ALREADY
    held through bar t's close (the same semantics as pa0_substrate.product_a_exec's own
    bar_pos array / U0's target_exposure_A) -- not a next-bar instruction. A trade of size
    d = pos_target[t]-pos_target[t-1] is filled at bar t's open (or, on a session's last bar, at
    bar t's close, matching the incumbent's own forced-flatten fill convention). Byte-verified
    against U0's certified bar_pnl_A_dollars on the real path (see main() gate)."""
    n = len(pos_target)
    cash = 0.0
    p_prev = 0
    prev_eq = 0.0
    bar_pnl = np.zeros(n)
    bar_pos = np.zeros(n, dtype=np.int64)
    contracts_traded = 0
    for t in range(n):
        p_new = int(pos_target[t])
        if p_new != p_prev:
            d = p_new - p_prev
            side = 1 if d > 0 else -1
            if is_last[t]:
                px = _fill(open_[t], high[t], low[t], side, at_close=close[t])
            else:
                px = _fill(open_[t], high[t], low[t], side)
            cash -= d * px * pv
            cash -= abs(d) * comm
            contracts_traded += abs(d)
            p_prev = p_new
        eq = cash + p_prev * close[t] * pv
        bar_pnl[t] = eq - prev_eq
        prev_eq = eq
        bar_pos[t] = p_prev
    return bar_pos, bar_pnl, contracts_traded


# ============================================================================ 3. STRATIFICATION
def build_strata(canon):
    direction = np.sign(canon["target_exposure_A"].to_numpy())
    size = np.abs(canon["target_exposure_A"].to_numpy()).astype(np.int64)
    nz = direction != 0

    vol = canon["sigma460_atr_proxy_pts"].to_numpy()
    conv = np.abs(canon["Tp"].to_numpy())
    phase = canon["session_phase"].to_numpy()

    vol_q1, vol_q2 = np.quantile(vol[nz], [1 / 3, 2 / 3])
    conv_q1, conv_q2 = np.quantile(conv[nz], [1 / 3, 2 / 3])

    def bucket(x, q1, q2):
        b = np.where(x <= q1, "lo", np.where(x <= q2, "mid", "hi"))
        return b

    vol_bucket = bucket(vol, vol_q1, vol_q2)
    conv_bucket = bucket(conv, conv_q1, conv_q2)
    dir_lab = np.where(direction > 0, "long", np.where(direction < 0, "short", "flat"))

    stratum = np.array(
        [f"{d}|{p}|v={v}|c={c}" for d, p, v, c in zip(dir_lab, phase, vol_bucket, conv_bucket)])

    edges = {"vol_q1": float(vol_q1), "vol_q2": float(vol_q2),
             "conv_q1": float(conv_q1), "conv_q2": float(conv_q2)}
    return direction, size, nz, stratum, edges


# ============================================================================ 4. PLACEBO SIZE ARRAY
def permuted_sizes(size, stratum, nz, rng):
    """Deterministic-given-rng, within-stratum permutation of |size| across the nonzero-direction
    population. Iterates strata in a FIXED sorted order so replicate reproducibility depends only
    on the seeded Generator, never on dict/set iteration order."""
    out = size.copy()
    nz_idx = np.flatnonzero(nz)
    strat_nz = stratum[nz_idx]
    for s in np.unique(strat_nz):  # np.unique returns sorted order -- fixed, deterministic
        member_idx = nz_idx[strat_nz == s]
        vals = size[member_idx]
        out[member_idx] = rng.permutation(vals)
    return out


# ============================================================================ 5. METRICS
def wls_slope(k_arr, y_arr, w_arr):
    k_arr = np.asarray(k_arr, dtype=float)
    y_arr = np.asarray(y_arr, dtype=float)
    w_arr = np.asarray(w_arr, dtype=float)
    wsum = w_arr.sum()
    kbar = (w_arr * k_arr).sum() / wsum
    ybar = (w_arr * y_arr).sum() / wsum
    num = (w_arr * (k_arr - kbar) * (y_arr - ybar)).sum()
    den = (w_arr * (k_arr - kbar) ** 2).sum()
    return float(num / den) if den > 0 else float("nan")


def compute_metrics(bar_pos, bar_pnl, contracts_traded, sess_dates, tag):
    net = float(bar_pnl.sum())
    exposure_hours = float(np.abs(bar_pos).sum() * BAR_HOURS)
    pnl_per_contract = net / contracts_traded if contracts_traded > 0 else float("nan")
    pnl_per_exposure_hour = net / exposure_hours if exposure_hours > 0 else float("nan")

    abs_pos = np.abs(bar_pos)
    k_max = int(abs_pos.max())
    unit_pnl_by_k = {}
    n_by_k = {}
    for k in range(1, k_max + 1):
        mask = abs_pos == k
        n_k = int(mask.sum())
        n_by_k[k] = n_k
        if n_k > 0:
            unit_pnl_by_k[k] = float((bar_pnl[mask] / k).mean())
    ks_fit = [k for k in unit_pnl_by_k if n_by_k[k] >= MIN_BARS_PER_K]
    if len(ks_fit) >= 2:
        gradient = wls_slope(ks_fit, [unit_pnl_by_k[k] for k in ks_fit],
                              [n_by_k[k] for k in ks_fit])
    else:
        gradient = float("nan")

    daily = pd.DataFrame({"sess": sess_dates, "pnl": bar_pnl}).groupby("sess")["pnl"].sum()
    b = dd_battery(pd.to_datetime(pd.Series(daily.index)), daily.to_numpy(), label=tag)

    return {
        "tag": tag, "net": net, "contracts_traded": int(contracts_traded),
        "exposure_hours": exposure_hours, "pnl_per_contract": pnl_per_contract,
        "pnl_per_exposure_hour": pnl_per_exposure_hour, "marginal_gradient": gradient,
        "k_max_observed": k_max, "n_by_k": n_by_k, "unit_pnl_by_k": unit_pnl_by_k,
        "ks_used_in_fit": ks_fit, "sharpe": b["sharpe"], "n_days": b["n_days"],
    }


# ============================================================================ 6. MAIN
def main():
    prereg = write_preregistration()

    canon = load_canonical()
    open_ = canon["open"].to_numpy(); high = canon["high"].to_numpy()
    low = canon["low"].to_numpy(); close = canon["close"].to_numpy()
    is_last = canon["is_last_of_sess"].to_numpy()
    sess_dates = canon["sess_date"].to_numpy()
    target_A = canon["target_exposure_A"].to_numpy().astype(np.int64)

    # ---------------------------------------------------------- correctness gate (mandatory)
    print("[PLACEBO01] running correctness gate: reconstruct TRUE incumbent from "
          "target_exposure_A via loop_exec ...", flush=True)
    real_bar_pos, real_bar_pnl, real_contracts = loop_exec(
        target_A, open_, high, low, close, is_last, sess_dates)
    real_net = float(real_bar_pnl.sum())
    gate_net_ok = abs(real_net - CERTIFIED_CANON_NET_A) < 1.0
    u0_bar_pnl = canon["bar_pnl_A_dollars"].to_numpy()
    max_abs_diff = float(np.max(np.abs(real_bar_pnl - u0_bar_pnl)))
    gate_bytewise_ok = max_abs_diff < 1e-6
    print(f"[PLACEBO01] gate: reconstructed net={real_net:.4f}  certified={CERTIFIED_CANON_NET_A}  "
          f"net_match={gate_net_ok}  max|bar_pnl diff vs U0|={max_abs_diff:.3e}  "
          f"bytewise_match={gate_bytewise_ok}", flush=True)
    assert gate_net_ok, f"CORRECTNESS GATE FAILED: net mismatch {real_net} vs {CERTIFIED_CANON_NET_A}"
    assert gate_bytewise_ok, f"CORRECTNESS GATE FAILED: bar_pnl array diverges from U0 (max diff {max_abs_diff})"
    assert bool((target_A[is_last] == 0).all()), \
        "CORRECTNESS GATE FAILED: target_exposure_A is not flat at every is_last_of_sess bar"
    print("[PLACEBO01] correctness gate PASSED -- proceeding to placebo randomizations.", flush=True)

    # ---------------------------------------------------------- stratification
    direction, size, nz, stratum, edges = build_strata(canon)
    assert np.array_equal(direction.astype(np.int64) * size, target_A), \
        "stratification direction*size does not reconstruct target_exposure_A exactly"
    strat_counts = pd.Series(stratum[nz]).value_counts()
    n_strata = int(len(strat_counts))
    print(f"[PLACEBO01] {int(nz.sum())} nonzero-direction bars across {n_strata} strata "
          f"(min={int(strat_counts.min())}, median={float(strat_counts.median()):.0f}, "
          f"max={int(strat_counts.max())}, n_strata_size<10={(strat_counts < 10).sum()})",
          flush=True)

    # ---------------------------------------------------------- real-system metrics
    real_metrics = compute_metrics(real_bar_pos, real_bar_pnl, real_contracts, sess_dates, "REAL")
    real_size_hist = pd.Series(size[nz]).value_counts().sort_index()
    print(f"[PLACEBO01] REAL: net={real_metrics['net']:.2f}  "
          f"contracts={real_metrics['contracts_traded']}  "
          f"PnL/contract={real_metrics['pnl_per_contract']:.4f}  "
          f"PnL/exposure-hr={real_metrics['pnl_per_exposure_hour']:.4f}  "
          f"gradient={real_metrics['marginal_gradient']:.4f}", flush=True)

    # ---------------------------------------------------------- placebo randomizations
    rows = []
    null_pnl_per_contract = np.zeros(N_RANDOMIZATIONS)
    null_pnl_per_exposure_hour = np.zeros(N_RANDOMIZATIONS)
    null_gradient = np.zeros(N_RANDOMIZATIONS)

    for i in range(N_RANDOMIZATIONS):
        seed_i = SEED_BASE + i
        rng = np.random.default_rng(seed_i)
        placebo_size = permuted_sizes(size, stratum, nz, rng)
        # exact-preservation checks (cheap, run every replicate for full disclosure)
        assert np.array_equal(np.sort(placebo_size[nz]), np.sort(size[nz])), \
            f"replicate {i}: global |size| histogram not preserved exactly"
        assert np.array_equal(placebo_size[~nz], size[~nz]), \
            f"replicate {i}: a flat bar was assigned nonzero size"
        placebo_target = (direction.astype(np.int64) * placebo_size).astype(np.int64)

        p_pos, p_pnl, p_contracts = loop_exec(placebo_target, open_, high, low, close,
                                               is_last, sess_dates)
        m = compute_metrics(p_pos, p_pnl, p_contracts, sess_dates, f"placebo_{i}")
        null_pnl_per_contract[i] = m["pnl_per_contract"]
        null_pnl_per_exposure_hour[i] = m["pnl_per_exposure_hour"]
        null_gradient[i] = m["marginal_gradient"]
        rows.append({
            "rep": i, "seed": seed_i, "net": m["net"], "contracts_traded": m["contracts_traded"],
            "exposure_hours": m["exposure_hours"], "pnl_per_contract": m["pnl_per_contract"],
            "pnl_per_exposure_hour": m["pnl_per_exposure_hour"],
            "marginal_gradient": m["marginal_gradient"], "sharpe": m["sharpe"],
        })
        if (i + 1) % 50 == 0:
            print(f"[PLACEBO01] {i + 1}/{N_RANDOMIZATIONS} replicates done "
                  f"(last net={m['net']:.2f})", flush=True)

    rows.append({
        "rep": "REAL", "seed": None, "net": real_metrics["net"],
        "contracts_traded": real_metrics["contracts_traded"],
        "exposure_hours": real_metrics["exposure_hours"],
        "pnl_per_contract": real_metrics["pnl_per_contract"],
        "pnl_per_exposure_hour": real_metrics["pnl_per_exposure_hour"],
        "marginal_gradient": real_metrics["marginal_gradient"], "sharpe": real_metrics["sharpe"],
    })
    results_df = pd.DataFrame(rows)
    results_csv_path = os.path.join(OUT, "sizing_placebo_results.csv")
    results_df.to_csv(results_csv_path, index=False)

    # ---------------------------------------------------------- percentiles
    def pctile(real_val, null_arr):
        null_arr = null_arr[np.isfinite(null_arr)]
        return float(100.0 * np.mean(null_arr <= real_val))

    pct_pnl_per_contract = pctile(real_metrics["pnl_per_contract"], null_pnl_per_contract)
    pct_pnl_per_exposure_hour = pctile(real_metrics["pnl_per_exposure_hour"],
                                        null_pnl_per_exposure_hour)
    pct_gradient = pctile(real_metrics["marginal_gradient"], null_gradient)

    def null_summary(arr):
        arr = arr[np.isfinite(arr)]
        return {"mean": float(arr.mean()), "std": float(arr.std(ddof=1)),
                "min": float(arr.min()), "max": float(arr.max()),
                "p05": float(np.quantile(arr, 0.05)), "p50": float(np.quantile(arr, 0.50)),
                "p95": float(np.quantile(arr, 0.95)), "n_finite": int(len(arr))}

    summary = {
        "preregistration": prereg,
        "correctness_gate": {
            "reconstructed_net": real_net, "certified_net": CERTIFIED_CANON_NET_A,
            "net_match_within_1usd": gate_net_ok,
            "max_abs_bar_pnl_diff_vs_u0_certified": max_abs_diff,
            "bytewise_match": gate_bytewise_ok,
            "flat_at_every_session_close": True,
        },
        "data": {
            "source": "runs/U0_UNIFIED_STATE/out/u0_state_table.parquet (canonical, "
                      "is_health_only_bar==False)",
            "n_bars_canonical": int(len(canon)),
            "n_sessions": int(canon["sess_date"].nunique()),
            "n_nonzero_direction_bars": int(nz.sum()),
            "date_range": [str(canon["time"].min()), str(canon["time"].max())],
        },
        "stratification": {
            "n_strata_populated": n_strata,
            "stratum_bar_count_min": int(strat_counts.min()),
            "stratum_bar_count_median": float(strat_counts.median()),
            "stratum_bar_count_max": int(strat_counts.max()),
            "n_strata_with_fewer_than_10_bars": int((strat_counts < 10).sum()),
            "vol_tercile_edges_atr_pts": {"q1": edges["vol_q1"], "q2": edges["vol_q2"]},
            "conviction_tercile_edges_abs_Tp": {"q1": edges["conv_q1"], "q2": edges["conv_q2"]},
            "session_phase_levels": sorted(pd.unique(canon["session_phase"]).tolist()),
            "real_size_histogram": {int(k): int(v) for k, v in real_size_hist.items()},
        },
        "real_system": real_metrics,
        "null_distribution": {
            "n_randomizations": N_RANDOMIZATIONS,
            "pnl_per_contract": null_summary(null_pnl_per_contract),
            "pnl_per_exposure_hour": null_summary(null_pnl_per_exposure_hour),
            "marginal_gradient": null_summary(null_gradient),
        },
        "real_vs_null_percentiles": {
            "pnl_per_contract_percentile": pct_pnl_per_contract,
            "pnl_per_exposure_hour_percentile": pct_pnl_per_exposure_hour,
            "marginal_gradient_percentile": pct_gradient,
        },
    }
    with open(os.path.join(OUT, "sizing_placebo_results.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print("\n[PLACEBO01] ==== REAL vs NULL (500-replicate within-stratum size-permutation) ====")
    print(f"  PnL/contract:        real={real_metrics['pnl_per_contract']:.5f}  "
          f"null[mean={null_summary(null_pnl_per_contract)['mean']:.5f}, "
          f"p05={null_summary(null_pnl_per_contract)['p05']:.5f}, "
          f"p95={null_summary(null_pnl_per_contract)['p95']:.5f}]  "
          f"percentile={pct_pnl_per_contract:.1f}")
    print(f"  PnL/exposure-hour:    real={real_metrics['pnl_per_exposure_hour']:.5f}  "
          f"null[mean={null_summary(null_pnl_per_exposure_hour)['mean']:.5f}, "
          f"p05={null_summary(null_pnl_per_exposure_hour)['p05']:.5f}, "
          f"p95={null_summary(null_pnl_per_exposure_hour)['p95']:.5f}]  "
          f"percentile={pct_pnl_per_exposure_hour:.1f}")
    print(f"  marginal gradient:    real={real_metrics['marginal_gradient']:.5f}  "
          f"null[mean={null_summary(null_gradient)['mean']:.5f}, "
          f"p05={null_summary(null_gradient)['p05']:.5f}, "
          f"p95={null_summary(null_gradient)['p95']:.5f}]  "
          f"percentile={pct_gradient:.1f}")
    print(f"\n[PLACEBO01] wrote {results_csv_path}")
    print(f"[PLACEBO01] wrote {os.path.join(OUT, 'sizing_placebo_results.json')}")
    return summary


if __name__ == "__main__":
    main()
