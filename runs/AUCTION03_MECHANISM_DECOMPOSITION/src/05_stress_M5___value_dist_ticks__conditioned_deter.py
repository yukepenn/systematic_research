"""AUCTION03 -- stress test / confound attack on the M5 finding:
"|value_dist_ticks|-conditioned deterioration in incumbent's forward-return (PRODUCT B,
controls for |M|, sigma460, session phase)" (runs/AUCTION03_MECHANISM_DECOMPOSITION/out/
m5_action_value_residual.{csv,json}, PRODUCT B ROWS ONLY -- product A is a different finding
and is not attacked here).

NOTE ON PROVENANCE: an earlier draft at this exact script path analyzed PRODUCT A instead of
product B (writing runs/AUCTION03_MECHANISM_DECOMPOSITION/out/05_stress_M5_value_dist_
deterioration.{json,txt}). That was a mismatch against this task's assignment (the finding under
test here is explicitly product B: discovery H1=-7.35t/H3=-22.01t/H20=-90.21t, confirmation
H1=-12.13t/H3=-32.11t/H20=-22.04t -- these match the PRODUCT B rows of m5_action_value_residual
.json, not product A's). This file replaces that content with a correct product-B analysis. The
old product-A output files are left untouched (not deleted, not overwritten -- a real, completed
analysis of a different cell) and this script writes to NEW, distinctly-named output files
(05_stress_M5_productB_value_dist_ticks.*) so the two are never confused. One finding from that
earlier product-A run is important and generalizes here (both products read the same shared
upstream poc_1s_full.parquet / grid1s substrate): a genuine small look-ahead was found in the
"last price" numerator of value_dist_ticks (poc_price itself is exactly causal), traced to
grid1s's 1-second buckets being labelled by window START while aggregating trades in [T,T+1).
Step 7 below independently re-derives this check from scratch using PRODUCT B's own decision
points and sessions (not just citing the product-A result), and sizes the bias against product
B's own tercile cuts/scale.

Baseline numbers under test (from m5_action_value_residual.json, product B):
  DISCOVERY (n_sessions=31, n_trade_blocks=47, n=2786):
    H1  controlled_effect=-7.349t  dual_sig=True   raw_diff=-6.391t
    H3  controlled_effect=-22.013t dual_sig=True   raw_diff=-15.857t
    H20 controlled_effect=-90.208t dual_sig=True   raw_diff=-53.031t
  CONFIRMATION (n_sessions=5, n_trade_blocks=7, n=522) -- NOT dual-significant, wide CIs:
    H1  controlled_effect=-12.131t dual_sig=False  raw_diff=-3.569t
    H3  controlled_effect=-32.114t dual_sig=False  raw_diff=+1.489t  (RAW FLIPS SIGN)
    H20 controlled_effect=-22.040t dual_sig=False  raw_diff=+11.201t (RAW FLIPS SIGN)

Attacks run (product B only, both samples where sample size allows; discovery is the only
sample with a live "significant" claim to attack -- confirmation's job here is just to check
whether its already-fragile same-signed persistence is itself session-driven):
  1. Reproduce official controlled_effect/raw_diff exactly (build-correctness gate) before
     touching anything.
  2. Leave-one-session-out (LOSO): recompute controlled_effect with each of the 31 (discovery)
     / 5 (confirmation) sessions held out in turn -- point estimate only (no bootstrap, this is
     a sign-stability / influence diagnostic, not a significance test) -- report the distribution
     and % sign-consistent with the full-sample estimate.
  3. Remove the single most-influential session (identified from the LOSO deltas, combined
     across H1/H3/H20 via relative-to-baseline delta) and recompute with full dual-cluster
     significance test. Same for the top-3 most-influential sessions removed together.
  4. Median split by session-mean sigma460_atr_proxy_pts (realized-vol proxy) -- recompute in
     each half with full dual-cluster significance test.
  5. Split by NQ contract-month (ground truth from research/scalping_lab/runs/EXPORT01/
     runlist_40.csv for discovery, runs/W5_PROTECTED_CONFIRMATION/ELIGIBLE_SESSION_MANIFEST_
     METADATA_ONLY.csv for confirmation -- NOT a guessed calendar-quarter proxy) -- recompute
     per contract with full dual-cluster significance test where the session count supports it.
  6. Confound check: correlate the predictor (abs_value_dist_ticks) against |M| and sigma460
     (the two already-in-model controls) AND two controls NOT in the M5 regression that are
     mechanically plausible relabelings -- bars-since-block-start (trade age) and block duration
     (trade length in bars) -- at both row level and session-mean level.
  7. Independent lookahead spot-check: for 6 timestamps across 3 discovery product-B sessions,
     recompute value_dist_ticks from RAW trade prints truncated to time<=t (t-or-earlier only,
     re-deriving the causal running-POC from scratch, not trusting poc_1s_full.parquet), compare
     to poc_1s_full.parquet's own stored value AND diagnose the grid1s window-labeling issue
     described above.

GOVERNANCE: reads only already-built derived files (action_substrate.parquet,
action_substrate_CONFIRM.parquet, poc_1s_full.parquet) plus raw trade prints + grid1s files for 3
discovery dates already in the permitted DISCOVERY_DATES list (for step 7's independent
recompute) plus two small metadata-only manifest CSVs (session->contract-month mapping, no price
data). No session outside the permitted discovery/confirmation lists is read. Writes only under
runs/AUCTION03_MECHANISM_DECOMPOSITION/out/.
"""
import os
import sys
import json

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
AUCTION02_SRC = os.path.join(ROOT, "runs", "AUCTION02_ACTION_RELEVANCE", "src")
sys.path.insert(0, AUCTION02_SRC)

OUT = os.path.join(ROOT, "runs", "AUCTION03_MECHANISM_DECOMPOSITION", "out")
os.makedirs(OUT, exist_ok=True)

HORIZONS = [1, 3, 20]
NBOOT = 1000
C1_TICKS = 2.872
TICK = 0.25
RNG_MAIN = np.random.default_rng(2026081099)  # independent seed from the original script's 20260810

DISCOVERY_DATES = [
    "20250814", "20250820", "20250901", "20250902", "20250905", "20250910",
    "20250911", "20250922", "20251002", "20251009", "20251027", "20251029",
    "20251110", "20251117", "20251124", "20251128", "20251209", "20251222",
    "20260123", "20260206", "20260211", "20260218", "20260220", "20260223",
    "20260303", "20260312", "20260317", "20260320", "20260406", "20260409",
    "20260417", "20260423", "20260428", "20260506", "20260511", "20260519",
    "20260520",
]
CONFIRM_DATES = [
    "20250819", "20250912", "20251028", "20251125", "20260217",
    "20260302", "20260422", "20260512",
]

DIR_COL, TRADE_COL, M_ABS_SRC = "position_B", "block_id_B", "M"
PHASE_DUMMY_LEVELS = ["RTH_OPEN", "RTH_CLOSE"]
X_COLS = ["abs_value_dist_ticks", "m_abs", "sigma460_atr_proxy_pts",
          "phase_RTH_OPEN", "phase_RTH_CLOSE"]

LOG_LINES = []


def log(msg):
    print(msg, flush=True)
    LOG_LINES.append(str(msg))


def _norm_date(s):
    return pd.to_datetime(s).dt.strftime("%Y%m%d")


def make_phase_dummies(sub):
    d = sub.copy()
    for lvl in PHASE_DUMMY_LEVELS:
        d[f"phase_{lvl}"] = (d["session_phase"] == lvl).astype(float)
    return d


def load_product_b(path, date_list, label):
    df = pd.read_parquet(path)
    df = df.copy()
    df["_datekey"] = _norm_date(df["sess_date"])
    df = df[df["_datekey"].isin(date_list)].copy()
    ok = df[df["analysis_ok"]].copy()
    sub = ok[ok[DIR_COL] != 0].copy()
    sub["m_abs"] = sub[M_ABS_SRC].abs()
    sub = make_phase_dummies(sub)
    log(f"[load] {label}: {len(sub)} product-B in-direction analysis_ok rows, "
        f"{sub['sess_tag'].nunique()} sessions, {sub[TRADE_COL].nunique()} trade blocks")
    return sub


# ---------------------------------------------------------------------- core regression machinery
# (deliberately mirrors 02_m5_action_value_residual.py's ols_fit / dual_cluster_ols_coef_ci exactly,
# so point estimates are bit-for-bit reproducible; re-implemented locally rather than imported so
# this stress script has no hidden coupling to the original script's module-level RNG state.)

def ols_fit(X, y):
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ coef
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    return coef, r2


def _group_index(keys_arr):
    codes, uniques = pd.factorize(keys_arr)
    idx_by_group = [np.where(codes == g)[0] for g in range(len(uniques))]
    return len(uniques), idx_by_group


def dual_cluster_ols_coef_ci(d, y_col, x_cols, sess_col, trade_col, nboot, rng):
    X = np.column_stack([np.ones(len(d)), d[x_cols].to_numpy(dtype=float)])
    y = d[y_col].to_numpy(dtype=float)
    k = X.shape[1]
    out = {}
    for label, key_col in [("session_block_ci", sess_col), ("trade_block_ci", trade_col)]:
        n_groups, idx_by_group = _group_index(d[key_col].to_numpy())
        boots = np.full(nboot, np.nan)
        for b in range(nboot):
            picks = rng.integers(0, n_groups, size=n_groups)
            idx = np.concatenate([idx_by_group[g] for g in picks])
            if len(idx) < k + 5:
                continue
            Xb, yb = X[idx], y[idx]
            if np.linalg.matrix_rank(Xb) < k:
                continue
            cb, _ = ols_fit(Xb, yb)
            boots[b] = cb[1]
        boots = boots[~np.isnan(boots)]
        lo, hi = (np.percentile(boots, [2.5, 97.5]) if len(boots) else (np.nan, np.nan))
        out[label] = [float(lo), float(hi)]
        out[f"{label}_n_clusters"] = n_groups
        out[f"{label}_n_boots_used"] = int(len(boots))
    return out


def controlled_effect_for_subset(sub, H, with_ci=True, nboot=NBOOT, rng=None, min_n=20):
    """Recomputes tercile cuts fresh on THIS subset's own marginal distribution of
    abs_value_dist_ticks (matching the original preregistered-on-marginal-distribution
    convention), the OLS beta on abs_value_dist_ticks, and controlled_effect = beta*tercile_scale.
    Returns None if subset is too small to fit."""
    y_col = f"signed_markout_{H}_B"
    d = sub.dropna(subset=X_COLS + [y_col]).reset_index(drop=True)
    if len(d) < min_n:
        return None
    vd_cuts = d["abs_value_dist_ticks"].quantile([1 / 3, 2 / 3]).tolist()
    if vd_cuts[0] == vd_cuts[1]:
        return None
    d["vd_tercile"] = pd.cut(d["abs_value_dist_ticks"],
                              bins=[-np.inf, vd_cuts[0], vd_cuts[1], np.inf],
                              labels=["near", "mid", "far"])
    mean_top = float(d.loc[d["vd_tercile"] == "far", "abs_value_dist_ticks"].mean())
    mean_bot = float(d.loc[d["vd_tercile"] == "near", "abs_value_dist_ticks"].mean())
    scale = mean_top - mean_bot

    X = np.column_stack([np.ones(len(d)), d[X_COLS].to_numpy(dtype=float)])
    y = d[y_col].to_numpy(dtype=float)
    coef, r2 = ols_fit(X, y)
    beta = float(coef[1])
    controlled_effect = beta * scale

    # raw unconditional top-vs-bottom tercile diff on this subset too, for cross-reference
    far = d.loc[d["vd_tercile"] == "far", y_col]
    near = d.loc[d["vd_tercile"] == "near", y_col]
    raw_diff = float(far.mean() - near.mean()) if len(far) and len(near) else np.nan

    result = {
        "n": len(d), "n_sessions": int(d["sess_tag"].nunique()),
        "n_trade_blocks": int(d[TRADE_COL].nunique()),
        "beta": beta, "tercile_scale": scale, "controlled_effect": controlled_effect,
        "raw_diff": raw_diff, "r2": r2,
    }
    if with_ci:
        ols = dual_cluster_ols_coef_ci(d, y_col, X_COLS, "sess_tag", TRADE_COL,
                                        nboot=nboot, rng=rng or RNG_MAIN)
        ci_sess = [ols["session_block_ci"][0] * scale, ols["session_block_ci"][1] * scale]
        ci_trade = [ols["trade_block_ci"][0] * scale, ols["trade_block_ci"][1] * scale]
        sig_sess = not (min(ci_sess) <= 0 <= max(ci_sess))
        sig_trade = not (min(ci_trade) <= 0 <= max(ci_trade))
        result.update({
            "ci_session": ci_sess, "ci_trade": ci_trade,
            "n_session_clusters": ols["session_block_ci_n_clusters"],
            "n_trade_clusters": ols["trade_block_ci_n_clusters"],
            "significant_session": bool(sig_sess), "significant_trade": bool(sig_trade),
            "significant_dual": bool(sig_sess and sig_trade),
        })
    return result


# ============================================================================ 1. LOAD DATA
disc_path = os.path.join(ROOT, "runs", "AUCTION02_ACTION_RELEVANCE", "out", "action_substrate.parquet")
conf_path = os.path.join(ROOT, "runs", "W5_PROTECTED_CONFIRMATION", "results", "out",
                          "action_substrate_CONFIRM.parquet")
disc = load_product_b(disc_path, DISCOVERY_DATES, "discovery")
conf = load_product_b(conf_path, CONFIRM_DATES, "confirmation")

# official published numbers (product B), for the build-correctness gate
OFFICIAL = {
    ("discovery", 1): dict(controlled_effect=-7.348623106045878, raw_diff=-6.3905440055440055),
    ("discovery", 3): dict(controlled_effect=-22.01284778152096, raw_diff=-15.857068607068609),
    ("discovery", 20): dict(controlled_effect=-90.20801051532831, raw_diff=-53.030539385539385),
    ("confirmation", 1): dict(controlled_effect=-12.130782777447072, raw_diff=-3.5689655172413794),
    ("confirmation", 3): dict(controlled_effect=-32.11403420466694, raw_diff=1.4885057471264371),
    ("confirmation", 20): dict(controlled_effect=-22.039765904653105, raw_diff=11.201149425287362),
}

# ============================================================================ 2. BASELINE REPRODUCTION GATE
log("\n" + "=" * 78)
log("STEP 1: BASELINE REPRODUCTION (build-correctness gate)")
log("=" * 78)
baseline = {}
gate_pass = True
for label, sub in [("discovery", disc), ("confirmation", conf)]:
    for H in HORIZONS:
        res = controlled_effect_for_subset(sub, H, with_ci=True, nboot=NBOOT, rng=RNG_MAIN)
        baseline[(label, H)] = res
        off = OFFICIAL[(label, H)]
        ce_match = abs(res["controlled_effect"] - off["controlled_effect"]) < 1e-6
        rd_match = abs(res["raw_diff"] - off["raw_diff"]) < 1e-6
        gate_pass = gate_pass and ce_match and rd_match
        log(f"[{label}] H={H}: controlled_effect={res['controlled_effect']:+.6f}t "
            f"(official {off['controlled_effect']:+.6f}t, match={ce_match}) | "
            f"raw_diff={res['raw_diff']:+.6f}t (official {off['raw_diff']:+.6f}t, match={rd_match}) | "
            f"dual_sig={res['significant_dual']} sess_CI={[round(x,3) for x in res['ci_session']]} "
            f"trade_CI={[round(x,3) for x in res['ci_trade']]}")
log(f"BUILD-CORRECTNESS GATE: {'PASS' if gate_pass else 'FAIL'} "
    f"(all point estimates reproduce official m5_action_value_residual.json to 1e-6)")
assert gate_pass, "stress-test regression code does not reproduce the official M5 numbers -- abort"

# ============================================================================ 3. LOSO (point estimates)
log("\n" + "=" * 78)
log("STEP 2: LEAVE-ONE-SESSION-OUT (point estimates, no bootstrap -- sign-stability diagnostic)")
log("=" * 78)
loso_results = {"discovery": {}, "confirmation": {}}
for label, sub in [("discovery", disc), ("confirmation", conf)]:
    sessions = sorted(sub["sess_tag"].unique())
    for H in HORIZONS:
        deltas = []
        for s in sessions:
            sub_loso = sub[sub["sess_tag"] != s]
            res = controlled_effect_for_subset(sub_loso, H, with_ci=False)
            ce = res["controlled_effect"] if res is not None else np.nan
            deltas.append({"session_removed": s, "controlled_effect": ce})
        loso_results[label][H] = deltas
        vals = np.array([r["controlled_effect"] for r in deltas if not np.isnan(r["controlled_effect"])])
        base_ce = baseline[(label, H)]["controlled_effect"]
        base_sign = np.sign(base_ce)
        n_same_sign = int((np.sign(vals) == base_sign).sum())
        log(f"[{label}] H={H}: LOSO n={len(vals)}/{len(sessions)} sessions | "
            f"full-sample controlled_effect={base_ce:+.3f}t | "
            f"LOSO range=[{vals.min():+.3f}, {vals.max():+.3f}]t, mean={vals.mean():+.3f}t, "
            f"std={vals.std():.3f}t | sign-stable (same sign as full sample): "
            f"{n_same_sign}/{len(vals)} ({100*n_same_sign/len(vals):.1f}%)")

# ============================================================================ 4. single-/top3-session removal
log("\n" + "=" * 78)
log("STEP 3: REMOVE SINGLE MOST-INFLUENTIAL SESSION / TOP-3 MOST-INFLUENTIAL SESSIONS (discovery)")
log("=" * 78)
# influence score per session = mean over H of (loso_delta / |baseline controlled_effect|), where
# loso_delta = controlled_effect_with_session_removed - controlled_effect_full (positive delta =
# removing this session PUSHES the effect toward zero/positive = weakens the deterioration finding
# = "most extreme in the finding's favor" session)
sessions_disc = sorted(disc["sess_tag"].unique())
score = {s: [] for s in sessions_disc}
for H in HORIZONS:
    base_ce = baseline[("discovery", H)]["controlled_effect"]
    for r in loso_results["discovery"][H]:
        s = r["session_removed"]
        ce = r["controlled_effect"]
        if np.isnan(ce):
            continue
        delta = ce - base_ce
        rel_delta = delta / abs(base_ce)
        score[s].append(rel_delta)
influence = {s: float(np.mean(v)) if v else np.nan for s, v in score.items()}
ranked = sorted(influence.items(), key=lambda kv: -kv[1])
log("Top 5 most-influential sessions (removing them weakens the deterioration finding most, "
    "ranked by mean relative LOSO delta across H1/H3/H20):")
for s, sc in ranked[:5]:
    log(f"  {s}: relative_influence={sc:+.4f}")
top1 = [ranked[0][0]]
top3 = [ranked[i][0] for i in range(3)]
log(f"single most-influential session: {top1[0]}")
log(f"top-3 most-influential sessions: {top3}")

removal_results = {"remove_top1": {}, "remove_top3": {}}
for tag, drop_list in [("remove_top1", top1), ("remove_top3", top3)]:
    sub_drop = disc[~disc["sess_tag"].isin(drop_list)]
    for H in HORIZONS:
        res = controlled_effect_for_subset(sub_drop, H, with_ci=True, nboot=NBOOT, rng=RNG_MAIN)
        removal_results[tag][H] = res
        base_ce = baseline[("discovery", H)]["controlled_effect"]
        log(f"[discovery, {tag}={drop_list}] H={H}: controlled_effect={res['controlled_effect']:+.3f}t "
            f"(full-sample was {base_ce:+.3f}t) | n_sessions={res['n_sessions']} | "
            f"sess_CI={[round(x,3) for x in res['ci_session']]} trade_CI={[round(x,3) for x in res['ci_trade']]} "
            f"| dual_sig={res['significant_dual']}")

# ============================================================================ 5. volatility median split
log("\n" + "=" * 78)
log("STEP 4: MEDIAN SPLIT BY SESSION-MEAN sigma460_atr_proxy_pts (realized-vol proxy, discovery)")
log("=" * 78)
sess_sigma = disc.groupby("sess_tag")["sigma460_atr_proxy_pts"].mean().sort_values()
n_sess = len(sess_sigma)
low_vol_sessions = set(sess_sigma.index[: n_sess // 2 + n_sess % 2])
high_vol_sessions = set(sess_sigma.index) - low_vol_sessions
log(f"low-vol sessions (n={len(low_vol_sessions)}, sigma460 range "
    f"[{sess_sigma.loc[list(low_vol_sessions)].min():.2f},{sess_sigma.loc[list(low_vol_sessions)].max():.2f}]): "
    f"{sorted(low_vol_sessions)}")
log(f"high-vol sessions (n={len(high_vol_sessions)}, sigma460 range "
    f"[{sess_sigma.loc[list(high_vol_sessions)].min():.2f},{sess_sigma.loc[list(high_vol_sessions)].max():.2f}]): "
    f"{sorted(high_vol_sessions)}")

vol_split_results = {"low_vol": {}, "high_vol": {}}
for tag, sess_set in [("low_vol", low_vol_sessions), ("high_vol", high_vol_sessions)]:
    sub_v = disc[disc["sess_tag"].isin(sess_set)]
    for H in HORIZONS:
        res = controlled_effect_for_subset(sub_v, H, with_ci=True, nboot=NBOOT, rng=RNG_MAIN)
        vol_split_results[tag][H] = res
        log(f"[discovery, {tag}] H={H}: controlled_effect={res['controlled_effect']:+.3f}t | "
            f"n={res['n']}, n_sessions={res['n_sessions']}, n_trade_blocks={res['n_trade_blocks']} | "
            f"sess_CI={[round(x,3) for x in res['ci_session']]} trade_CI={[round(x,3) for x in res['ci_trade']]} "
            f"| dual_sig={res['significant_dual']}")

# ============================================================================ 6. contract-month split
log("\n" + "=" * 78)
log("STEP 5: SPLIT BY NQ CONTRACT-MONTH (ground truth from runlist_40.csv / ELIGIBLE_SESSION_MANIFEST)")
log("=" * 78)
runlist = pd.read_csv(os.path.join(ROOT, "research", "scalping_lab", "runs", "EXPORT01", "runlist_40.csv"),
                       dtype=str)
runlist["sess_tag"] = runlist["tag"].str.replace("s", "", regex=False)
contract_map_disc = dict(zip(runlist["sess_tag"], runlist["instrument"]))
missing = set(disc["sess_tag"].unique()) - set(contract_map_disc)
assert not missing, f"discovery sessions missing contract-month mapping: {missing}"
disc["contract"] = disc["sess_tag"].map(contract_map_disc)

manifest = pd.read_csv(os.path.join(ROOT, "runs", "W5_PROTECTED_CONFIRMATION",
                                     "ELIGIBLE_SESSION_MANIFEST_METADATA_ONLY.csv"), dtype=str)
manifest["sess_tag"] = manifest["session_date"]
contract_map_conf = dict(zip(manifest["sess_tag"], manifest["contract_month_folder(s)"]))
missing_c = set(conf["sess_tag"].unique()) - set(contract_map_conf)
assert not missing_c, f"confirmation sessions missing contract-month mapping: {missing_c}"
conf["contract"] = conf["sess_tag"].map(contract_map_conf)

log("Discovery product-B sessions per contract-month:")
for c, g in disc.groupby("contract"):
    log(f"  {c}: {g['sess_tag'].nunique()} sessions, n_rows={len(g)}, "
        f"dates={sorted(g['sess_tag'].unique())}")
log("Confirmation product-B sessions per contract-month:")
for c, g in conf.groupby("contract"):
    log(f"  {c}: {g['sess_tag'].nunique()} sessions, n_rows={len(g)}, "
        f"dates={sorted(g['sess_tag'].unique())}")

contract_split_results = {"discovery": {}, "confirmation": {}}
for label, sub, cmap in [("discovery", disc, contract_map_disc), ("confirmation", conf, contract_map_conf)]:
    for c in sorted(sub["contract"].dropna().unique()):
        sub_c = sub[sub["contract"] == c]
        n_sess_c = sub_c["sess_tag"].nunique()
        for H in HORIZONS:
            # with_ci only where there's any hope of a non-degenerate bootstrap (>=3 sessions);
            # smaller groups still get a point estimate, explicitly flagged as descriptive-only
            with_ci = n_sess_c >= 3
            res = controlled_effect_for_subset(sub_c, H, with_ci=with_ci, nboot=NBOOT, rng=RNG_MAIN)
            contract_split_results[label].setdefault(c, {})[H] = res
            if res is None:
                log(f"[{label}, contract={c}] H={H}: subset too small to fit (n_sessions={n_sess_c})")
                continue
            if with_ci:
                log(f"[{label}, contract={c}] H={H}: controlled_effect={res['controlled_effect']:+.3f}t | "
                    f"n={res['n']}, n_sessions={res['n_sessions']}, n_trade_blocks={res['n_trade_blocks']} | "
                    f"sess_CI={[round(x,3) for x in res['ci_session']]} "
                    f"trade_CI={[round(x,3) for x in res['ci_trade']]} | dual_sig={res['significant_dual']}")
            else:
                log(f"[{label}, contract={c}] H={H}: controlled_effect={res['controlled_effect']:+.3f}t "
                    f"(POINT ESTIMATE ONLY, n_sessions={n_sess_c} too small for a bootstrap CI -- "
                    f"descriptive, not a significance test) | n={res['n']}, "
                    f"n_trade_blocks={res['n_trade_blocks']}")

# ============================================================================ 7. confound correlation check
log("\n" + "=" * 78)
log("STEP 6: PREDICTOR-CONFOUND CORRELATION CHECK (abs_value_dist_ticks vs |M|, sigma460, "
    "trade-age, block-duration)")
log("=" * 78)


def bars_since_block_start(sub):
    d = sub.sort_values(["sess_tag", "t_idx"]).copy()
    d["_bar_seq_in_block"] = d.groupby(TRADE_COL).cumcount()
    block_len = d.groupby(TRADE_COL)[TRADE_COL].transform("size")
    d["_block_duration_bars"] = block_len
    return d


confound_results = {}
for label, sub in [("discovery", disc), ("confirmation", conf)]:
    d = bars_since_block_start(sub)
    row_level = {}
    for col in ["m_abs", "sigma460_atr_proxy_pts", "_bar_seq_in_block", "_block_duration_bars"]:
        pear = float(d["abs_value_dist_ticks"].corr(d[col], method="pearson"))
        spear = float(d["abs_value_dist_ticks"].corr(d[col], method="spearman"))
        row_level[col] = {"pearson": pear, "spearman": spear}
    sess_mean = d.groupby("sess_tag").agg(
        abs_value_dist_ticks=("abs_value_dist_ticks", "mean"),
        m_abs=("m_abs", "mean"),
        sigma460=("sigma460_atr_proxy_pts", "mean"),
        bar_seq=("_bar_seq_in_block", "mean"),
        block_dur=("_block_duration_bars", "mean"),
    )
    sess_level = {}
    for col, key in [("m_abs", "m_abs"), ("sigma460", "sigma460_atr_proxy_pts"),
                      ("bar_seq", "_bar_seq_in_block"), ("block_dur", "_block_duration_bars")]:
        pear = float(sess_mean["abs_value_dist_ticks"].corr(sess_mean[col], method="pearson"))
        sess_level[key] = {"pearson_session_level": pear}
    confound_results[label] = {"row_level": row_level, "session_level": sess_level,
                                "n_sessions": len(sess_mean)}
    log(f"[{label}] row-level corr(abs_value_dist_ticks, X):")
    for col, v in row_level.items():
        log(f"    {col}: pearson={v['pearson']:+.4f}, spearman={v['spearman']:+.4f}")
    log(f"[{label}] session-mean-level corr(abs_value_dist_ticks, X) (n_sessions={len(sess_mean)}):")
    for col, v in sess_level.items():
        log(f"    {col}: pearson={v['pearson_session_level']:+.4f}")

# ============================================================================ 8. lookahead spot-check
log("\n" + "=" * 78)
log("STEP 7: INDEPENDENT LOOKAHEAD SPOT-CHECK (raw trade prints, t-or-earlier only, product-B "
    "decision points)")
log("=" * 78)

RAW_DIR = os.path.join(ROOT, "research", "scalping_lab", "substrate", "raw", "NQ")
GRID1S_DIR = os.path.join(ROOT, "research", "scalping_lab", "substrate", "grid1s", "NQ")
POC_1S_PATH = os.path.join(ROOT, "runs", "AUCTION01_VALUE_STATE", "out", "poc_1s_full.parquet")


def causal_running_poc(last):
    """Re-implementation of AUCTION01_VALUE_STATE/src/02_build_poc_substrate.py's
    causal_running_poc, applied here to a raw-trades slice TRUNCATED to time<=t -- since every
    op (groupby-cumsum, cummax, ffill) is backward-only in time-sorted order, running this on the
    truncated slice and reading the LAST row is provably identical to running it on the full
    session and reading the row at time t. This independently re-derives poc_price from scratch,
    without reading poc_1s_full.parquet at all."""
    last = last.sort_values("time").reset_index(drop=True)
    tick_id = np.round(last["price"].values / TICK).astype(np.int64)
    last = last.copy()
    last["tick_id"] = tick_id
    last["cum_vol_at_price"] = last.groupby("tick_id")["volume"].cumsum()
    running_max = last["cum_vol_at_price"].cummax()
    is_record = last["cum_vol_at_price"].values >= running_max.values
    poc_tick = np.where(is_record, tick_id, np.nan)
    poc_tick = pd.Series(poc_tick).ffill().values
    last["poc_price"] = poc_tick * TICK
    return last


def spot_check(sess_tag, target_time, raw_cache, poc_cache):
    raw = raw_cache[sess_tag]
    last_trades = raw[(raw["bip"] == 0) & (raw["time"] <= target_time)]
    if len(last_trades) == 0:
        return {"sess_tag": sess_tag, "time": str(target_time), "skip": "no trades <=t"}
    poc = causal_running_poc(last_trades)
    manual_poc_price = float(poc.iloc[-1]["poc_price"])
    causal_last = float(last_trades.sort_values("time").iloc[-1]["price"])
    causal_value_dist = (causal_last - manual_poc_price) / TICK

    poc_sess = poc_cache[sess_tag]
    stored_row = poc_sess[poc_sess["time"] <= target_time]
    if len(stored_row) == 0:
        return {"sess_tag": sess_tag, "time": str(target_time), "skip": "no poc_1s_full row <=t"}
    stored_row = stored_row.iloc[-1]
    stored_poc_price = float(stored_row["poc_price"])
    stored_value_dist = float(stored_row["value_dist_ticks"])
    stored_last = float(stored_row["last"])

    # diagnose the known grid1s window-labeling issue: is stored_last actually drawn from trades
    # in [t, t+1) (bucket labelled by window START) rather than strictly time<=t?
    window_trades = last_trades[last_trades["time"] >= target_time - pd.Timedelta(seconds=1)]
    window_trades_fwd = raw[(raw["bip"] == 0) & (raw["time"] >= target_time) &
                             (raw["time"] < target_time + pd.Timedelta(seconds=1))]
    window_last = (float(window_trades_fwd.sort_values("time").iloc[-1]["price"])
                   if len(window_trades_fwd) else np.nan)
    stored_matches_window = (not np.isnan(window_last)) and abs(stored_last - window_last) < 1e-9

    match_poc = abs(manual_poc_price - stored_poc_price) < 1e-6
    match_vd_strict = abs(causal_value_dist - stored_value_dist) < 1e-6
    lookahead_bias_ticks = stored_value_dist - causal_value_dist

    return {
        "sess_tag": sess_tag, "time": str(target_time),
        "manual_poc_price": manual_poc_price, "stored_poc_price": stored_poc_price,
        "match_poc_price": bool(match_poc),
        "causal_last_at_or_before_t": causal_last, "stored_last_grid1s": stored_last,
        "window_last_within_t_to_t1s": window_last,
        "stored_last_matches_forward_window": bool(stored_matches_window),
        "causal_value_dist_ticks": causal_value_dist,
        "stored_value_dist_ticks": stored_value_dist,
        "match_value_dist_strict_causal": bool(match_vd_strict),
        "lookahead_bias_ticks": float(lookahead_bias_ticks),
    }


# 6 checkpoints across 3 discovery product-B sessions (2 each), spread across the session
check_sessions = ["20250901", "20251209", "20260406"]
raw_cache, poc_cache = {}, {}
poc_1s_full = pd.read_parquet(POC_1S_PATH, columns=["time", "sess_tag", "poc_price",
                                                      "value_dist_ticks", "last"])
for tag in check_sessions:
    raw_f = os.path.join(RAW_DIR, f"s{tag}.parquet")
    rth_f = os.path.join(RAW_DIR, f"s{tag}_rth.parquet")
    parts = [pd.read_parquet(raw_f)]
    if os.path.exists(rth_f):
        parts.append(pd.read_parquet(rth_f))
    raw = pd.concat(parts, ignore_index=True)
    raw["time"] = pd.to_datetime(raw["time"])
    raw = raw.drop_duplicates(subset=["bip", "time", "price", "volume"])
    raw_cache[tag] = raw
    poc_sess = poc_1s_full[poc_1s_full["sess_tag"] == tag].sort_values("time").reset_index(drop=True)
    poc_cache[tag] = poc_sess

check_targets = []
for tag in check_sessions:
    rows = disc[(disc["sess_tag"] == tag)].sort_values("time")
    if len(rows) == 0:
        log(f"[lookahead-check] {tag}: no product-B analysis_ok rows, skipping session")
        continue
    idxs = sorted(set([0, len(rows) - 1])) if len(rows) < 2 else [0, len(rows) - 1]
    for i in idxs:
        check_targets.append((tag, rows.iloc[i]["time"]))

spot_results = []
for tag, t in check_targets:
    res = spot_check(tag, t, raw_cache, poc_cache)
    spot_results.append(res)
    if "skip" in res:
        log(f"[lookahead-check] {tag} @ {t}: SKIPPED ({res['skip']})")
        continue
    log(f"[lookahead-check] {tag} @ {t}: poc_price manual={res['manual_poc_price']:.2f} "
        f"vs stored={res['stored_poc_price']:.2f} (exact match={res['match_poc_price']}) | "
        f"last: strict-causal(<=t)={res['causal_last_at_or_before_t']:.2f}, "
        f"stored(grid1s)={res['stored_last_grid1s']:.2f}, "
        f"window[t,t+1)_last={res['window_last_within_t_to_t1s']} "
        f"(stored==fwd-window: {res['stored_last_matches_forward_window']}) | "
        f"value_dist_ticks: strict-causal={res['causal_value_dist_ticks']:+.2f}t "
        f"vs stored={res['stored_value_dist_ticks']:+.2f}t "
        f"(look-ahead bias={res['lookahead_bias_ticks']:+.2f}t) -> "
        f"{'PASS (0 bias)' if res['match_value_dist_strict_causal'] else 'BIAS DETECTED'}")

n_checks = len([r for r in spot_results if "skip" not in r])
n_poc_exact = sum(1 for r in spot_results if r.get("match_poc_price"))
n_vd_exact = sum(1 for r in spot_results if r.get("match_value_dist_strict_causal"))
biases = [r["lookahead_bias_ticks"] for r in spot_results if "lookahead_bias_ticks" in r]
max_abs_bias = max((abs(b) for b in biases), default=0.0)
disc_tercile_scale_b = baseline[("discovery", 1)]["tercile_scale"]
conf_tercile_scale_b = baseline[("confirmation", 1)]["tercile_scale"]
log(f"Lookahead spot-check (product B decision points, n={n_checks}): "
    f"poc_price exact causal match {n_poc_exact}/{n_checks} | "
    f"value_dist_ticks exact causal match (0 bias) {n_vd_exact}/{n_checks} | "
    f"max |look-ahead bias| = {max_abs_bias:.2f}t vs product-B tercile_scale "
    f"discovery={disc_tercile_scale_b:.1f}t / confirmation={conf_tercile_scale_b:.1f}t "
    f"(bias is {100*max_abs_bias/disc_tercile_scale_b:.1f}% of the discovery tercile scale, "
    f"{100*max_abs_bias/conf_tercile_scale_b:.1f}% of the confirmation tercile scale, in the "
    f"worst observed check)")
if n_poc_exact < n_checks:
    log("WARNING: poc_price itself failed an exact causal match -- would be a more serious bug "
        "than the known grid1s window-labeling issue; investigate before trusting this result.")
if max_abs_bias > 0:
    log("Root cause (matches the product-A finding at this same script path): grid1s's 1-second "
        "buckets are labeled by window START and aggregate trades in [T,T+1), so the 'last' price "
        "merged into value_dist_ticks can reflect a trade up to ~1s AFTER its own timestamp label. "
        "poc_price (the dominant, slower-moving driver of far/near tercile membership) is exactly "
        "causal in every check above. This is inherited from the campaign's existing grid1s "
        "substrate (research/scalping_lab), not introduced by AUCTION01/02/03 code.")

# ============================================================================ WRITE OUTPUT
log("\n" + "=" * 78)
log("SUMMARY")
log("=" * 78)

out_payload = {
    "finding": "M5 |value_dist_ticks|-conditioned deterioration, product B",
    "c1_ticks": C1_TICKS,
    "build_correctness_gate_pass": gate_pass,
    "baseline": {f"{lbl}_H{H}": {k: v for k, v in res.items()} for (lbl, H), res in baseline.items()},
    "loso": {
        label: {str(H): loso_results[label][H] for H in HORIZONS}
        for label in ["discovery", "confirmation"]
    },
    "loso_sign_stability": {
        label: {
            str(H): {
                "n": int(np.sum(~np.isnan([r["controlled_effect"] for r in loso_results[label][H]]))),
                "n_same_sign_as_full_sample": int(np.sum(
                    np.sign([r["controlled_effect"] for r in loso_results[label][H]
                             if not np.isnan(r["controlled_effect"])])
                    == np.sign(baseline[(label, H)]["controlled_effect"]))),
                "min": float(np.nanmin([r["controlled_effect"] for r in loso_results[label][H]])),
                "max": float(np.nanmax([r["controlled_effect"] for r in loso_results[label][H]])),
                "mean": float(np.nanmean([r["controlled_effect"] for r in loso_results[label][H]])),
                "std": float(np.nanstd([r["controlled_effect"] for r in loso_results[label][H]])),
            }
            for H in HORIZONS
        }
        for label in ["discovery", "confirmation"]
    },
    "influence_ranking_discovery": ranked,
    "top1_session_removed": top1,
    "top3_sessions_removed": top3,
    "removal_results": removal_results,
    "vol_split_results": vol_split_results,
    "vol_split_sessions": {"low_vol": sorted(low_vol_sessions), "high_vol": sorted(high_vol_sessions)},
    "contract_split_results": contract_split_results,
    "contract_map_discovery": contract_map_disc,
    "contract_map_confirmation": contract_map_conf,
    "confound_correlations": confound_results,
    "lookahead_spot_check": {
        "n_checks": n_checks, "n_poc_price_exact_match": n_poc_exact,
        "n_value_dist_ticks_exact_match": n_vd_exact,
        "max_abs_lookahead_bias_ticks": max_abs_bias,
        "pct_of_discovery_tercile_scale": 100 * max_abs_bias / disc_tercile_scale_b,
        "pct_of_confirmation_tercile_scale": 100 * max_abs_bias / conf_tercile_scale_b,
        "checks": spot_results,
    },
}

json_path = os.path.join(OUT, "05_stress_M5_productB_value_dist_ticks.json")
with open(json_path, "w") as f:
    json.dump(out_payload, f, indent=2, default=float)
log(f"\nWrote {json_path}")

log_path = os.path.join(OUT, "05_stress_M5_productB_value_dist_ticks_log.txt")
with open(log_path, "w") as f:
    f.write("\n".join(LOG_LINES))
log(f"Wrote {log_path}")
log("STRESS TEST DONE")
