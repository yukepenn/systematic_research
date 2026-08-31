"""G3_CLOCKLAG01 - estimators, session-clustered inference, and the circular-shift MAX null.

THREE ESTIMATORS (spec section 3, frozen):
    beta_same(b)      r(b,d)  on  r(b,d-1)      same clock bucket, one day back   TREATMENT
    beta_adj(b)       r(b,d)  on  r(b-1,d)      adjacent bucket, same day         CONTROL A
    beta_nonmult(b)   r(b,d)  on  r(b',d-1), b' != b, averaged over b'            CONTROL B

beta_adj(0) IS UNDEFINED: bucket -1 does not exist. It is reported NaN and every head-to-head
comparison of beta_same against beta_adj is therefore also computed on the MATCHED bucket set
b = 1..12 where both estimators exist. Both versions are printed; neither is chosen after the fact.

THE NULL (spec section 3, S1_GATE_NULL). MC-11 died by reporting a best-of-13 without replicating
the argmax inside its null. Here one circular shift k of the DAY INDEX is drawn per draw and applied
to the PREDICTOR matrix only. A whole day-row moves together, so
    * each bucket's own marginal distribution is preserved exactly (it is a permutation of days), and
    * the within-day cross-bucket dependence is preserved exactly.
The ENTIRE analysis - all 13 buckets, all three estimators, every mean and every max-over-buckets
step - is recomputed on each draw and the maxima are recorded.

k is drawn from {BUFFER .. n-BUFFER} with BUFFER=5, i.e. shifts that would re-align the predictor
with the outcome to within a week are excluded, since those are not null draws.

Univariate OLS with an intercept has beta = Sxy/Sxx, so the whole 13x13 grid of
"regress outcome bucket b on predictor bucket b'" is one matrix product. That is what makes 2,000
full re-analyses cheap enough that no shortcut is needed anywhere.
"""
from __future__ import annotations

import numpy as np

K = 13
NULL_BUFFER = 5


# ==================================================================================================
# Univariate OLS with intercept: point estimate + per-observation influence function
# ==================================================================================================
def ols_beta_infl(y: np.ndarray, x: np.ndarray):
    """Return (beta, psi) for y = a + b*x + e.

    psi_i is the influence function of beta, so that beta - beta_true ~= sum_i psi_i and the
    HC0 / cluster-robust variance of any linear combination of betas is just the sum of squared
    within-cluster sums of the combined influence. Because there is exactly ONE observation per
    session here, clustering by session and White HC0 coincide for a single regression; clustering
    only starts to bite for statistics that AVERAGE ACROSS BUCKETS, which is exactly the statistic
    the Stage 1 gate is written on.
    """
    xc = x - x.mean()
    yc = y - y.mean()
    sxx = float(xc @ xc)
    beta = float(xc @ yc) / sxx
    e = yc - beta * xc
    return beta, xc * e / sxx


def clustered_se(psi_sum: np.ndarray, n_params: int = 2) -> float:
    """Session-clustered SE of a statistic whose per-session influence contribution is psi_sum.

    One observation per cluster, so G = N; the usual finite-sample factor
    G/(G-1) * (N-1)/(N-K) collapses to N/(N-K).
    """
    n = len(psi_sum)
    corr = n / max(n - n_params, 1)
    return float(np.sqrt(corr * float(psi_sum @ psi_sum)))


# ==================================================================================================
# The vectorised 13-bucket analysis - identical code path for observed and for every null draw
# ==================================================================================================
def analyse(Y: np.ndarray, Xs: np.ndarray, Xa: np.ndarray):
    """Y, Xs, Xa are (n, 13).

    Xs supplies the LAG-1 (cross-day) predictors, Xa the SAME-DAY predictors.
    Returns (beta_same[13], beta_adj[13] with NaN at 0, beta_nonmult[13]).
    """
    yc = Y - Y.mean(0)
    sc = Xs - Xs.mean(0)
    ac = Xa - Xa.mean(0)
    bs = (yc.T @ sc) / (sc * sc).sum(0)[None, :]     # bs[b, b'] = beta of y_b on xs_b'
    ba = (yc.T @ ac) / (ac * ac).sum(0)[None, :]
    beta_same = np.diag(bs).copy()
    off = bs.copy()
    np.fill_diagonal(off, np.nan)
    beta_nonmult = np.nanmean(off, axis=1)
    beta_adj = np.full(K, np.nan)
    beta_adj[1:] = ba[np.arange(1, K), np.arange(0, K - 1)]
    return beta_same, beta_adj, beta_nonmult


# --- the bucket sets. FROZEN HERE, BEFORE ANY NUMBER EXISTS, and never re-chosen. --------------
BUCKET_SETS = {
    "ALL_13":       np.arange(0, 13),   # beta_adj undefined at b=0, so its mean uses 1..12
    "MATCHED_1_12": np.arange(1, 13),   # the only set where BOTH estimators exist -> gate set
    "INTERIOR_1_11": np.arange(1, 12),  # spec trap 4: open and close auctions removed, for READING
}
GATE_SET = "MATCHED_1_12"


def summarise(beta_same, beta_adj, beta_nonmult) -> dict:
    """Every mean / max statistic the gate and the null need, for every frozen bucket set."""
    out = {}
    for nm, idx in BUCKET_SETS.items():
        adj_idx = idx[idx >= 1]
        out[nm] = dict(
            mean_same=float(np.mean(beta_same[idx])),
            mean_adj=float(np.mean(beta_adj[adj_idx])),
            mean_nonmult=float(np.mean(beta_nonmult[idx])),
            # margin on a MATCHED index set: same and adj averaged over identical buckets
            margin=float(np.mean(beta_same[adj_idx]) - np.mean(beta_adj[adj_idx])),
            max_same=float(np.max(beta_same[idx])),
            # max_abs_same prices the TWO-SIDED bucket family. max_same alone prices only the
            # right tail, which understates multiplicity whenever the table also contains a large
            # negative beta_same. It is strictly more conservative and never enters the gate.
            max_abs_same=float(np.max(np.abs(beta_same[idx]))),
            min_same=float(np.min(beta_same[idx])),
            max_margin=float(np.max(beta_same[adj_idx] - beta_adj[adj_idx])),
            max_abs_nonmult=float(np.max(np.abs(beta_nonmult[idx]))),
            # head-to-head: in how many buckets does the clock-aligned term beat the adjacent one?
            frac_same_gt_adj=float(np.mean(beta_same[adj_idx] > beta_adj[adj_idx])),
        )
    return out


# ==================================================================================================
# Observed estimates with session-clustered standard errors
# ==================================================================================================
def observed(R: np.ndarray):
    """R is the (n_sess, 13) bucket-return matrix of ONE era, in session order.

    Outcome rows are 1..n-1 (every day that has a predecessor IN THIS ERA). The same row set is
    used for all three estimators so that the comparison is on one sample, not three.
    """
    Y, Xs, Xa = R[1:], R[:-1], R[1:]
    n = len(Y)
    bs, ba, bn = analyse(Y, Xs, Xa)

    psi_same = np.zeros((K, n))
    psi_adj = np.full((K, n), np.nan)
    psi_non = np.zeros((K, n))
    for b in range(K):
        _, psi_same[b] = ols_beta_infl(Y[:, b], Xs[:, b])
        if b >= 1:
            _, psi_adj[b] = ols_beta_infl(Y[:, b], Xa[:, b - 1])
        acc = np.zeros(n)
        for bp in range(K):
            if bp == b:
                continue
            _, p = ols_beta_infl(Y[:, b], Xs[:, bp])
            acc += p
        psi_non[b] = acc / (K - 1)

    def se_of(psi_rows, idx, sign=1.0):
        return clustered_se(sign * psi_rows[idx].mean(axis=0))

    per_bucket = []
    for b in range(K):
        row = dict(bucket=b, n=n)
        row["beta_same"] = bs[b]
        row["se_same"] = clustered_se(psi_same[b])
        row["beta_adj"] = ba[b]
        row["se_adj"] = clustered_se(psi_adj[b]) if b >= 1 else float("nan")
        row["beta_nonmult"] = bn[b]
        row["se_nonmult"] = clustered_se(psi_non[b])
        for k_ in ("same", "adj", "nonmult"):
            row[f"t_{k_}"] = (row[f"beta_{k_}"] / row[f"se_{k_}"]
                              if np.isfinite(row[f"se_{k_}"]) and row[f"se_{k_}"] > 0
                              else float("nan"))
        per_bucket.append(row)

    agg = summarise(bs, ba, bn)
    for nm, idx in BUCKET_SETS.items():
        adj_idx = idx[idx >= 1]
        agg[nm]["se_mean_same"] = se_of(psi_same, idx)
        agg[nm]["se_mean_adj"] = se_of(psi_adj, adj_idx)
        agg[nm]["se_mean_nonmult"] = se_of(psi_non, idx)
        agg[nm]["se_margin"] = clustered_se(psi_same[adj_idx].mean(axis=0)
                                            - psi_adj[adj_idx].mean(axis=0))
        for lab, key in (("mean_same", "se_mean_same"), ("mean_adj", "se_mean_adj"),
                         ("mean_nonmult", "se_mean_nonmult"), ("margin", "se_margin")):
            s = agg[nm][key]
            agg[nm][f"t_{lab}"] = agg[nm][lab] / s if s > 0 else float("nan")
    return dict(per_bucket=per_bucket, agg=agg, n=n,
                beta_same=bs, beta_adj=ba, beta_nonmult=bn)


# ==================================================================================================
# rho_bar and K_eff
# ==================================================================================================
def rho_bar_and_keff(R: np.ndarray):
    """Mean PAIRWISE correlation of the 13 bucket return series, and K_eff = K/(1+(K-1)*rho_bar)."""
    C = np.corrcoef(R, rowvar=False)
    iu = np.triu_indices(K, 1)
    rb = float(np.mean(C[iu]))
    keff = K / (1.0 + (K - 1) * rb)
    return rb, float(keff), C


# ==================================================================================================
# The circular-shift MAX null
# ==================================================================================================
def circular_shift_null(R: np.ndarray, n_draws: int = 2000, seed: int = 20260831,
                        buffer: int = NULL_BUFFER):
    """Redo the ENTIRE analysis on each of n_draws circular day-shifts of the predictor matrix.

    NULL_A (the gate null): the shifted matrix supplies BOTH the lag-1 and the same-day predictors,
      so no estimator retains its true day alignment. This is the null of "no day-aligned structure
      of any kind", against which the margin (same - adj) has its correct sampling distribution.

    NULL_B (a stricter diagnostic, printed but not the gate): only the CROSS-DAY predictor is
      shifted; beta_adj keeps its true same-day alignment. The margin is then measured against the
      REAL adjacent-bucket benchmark, which is the sharper reading of the identifying restriction.

    Every draw records means AND maxima over buckets, so a best-bucket claim is priced.
    """
    n_sess = len(R)
    Y = R[1:]
    rng = np.random.default_rng(seed)
    lo, hi = buffer, n_sess - buffer
    if hi <= lo:
        raise ValueError("era too short for a buffered circular shift")
    ks = rng.integers(lo, hi + 1, size=n_draws)

    keys = ["mean_same", "mean_adj", "mean_nonmult", "margin",
            "max_same", "max_abs_same", "min_same", "max_margin", "max_abs_nonmult",
            "frac_same_gt_adj"]
    A = {nm: {k: np.empty(n_draws) for k in keys} for nm in BUCKET_SETS}
    B = {nm: {k: np.empty(n_draws) for k in keys} for nm in BUCKET_SETS}

    for i, k in enumerate(ks):
        Rp = np.roll(R, int(k), axis=0)
        bs, ba, bn = analyse(Y, Rp[:-1], Rp[1:])       # NULL_A
        sA = summarise(bs, ba, bn)
        bs2, ba2, bn2 = analyse(Y, Rp[:-1], R[1:])     # NULL_B: adj keeps its true alignment
        sB = summarise(bs2, ba2, bn2)
        for nm in BUCKET_SETS:
            for kk in keys:
                A[nm][kk][i] = sA[nm][kk]
                B[nm][kk][i] = sB[nm][kk]
    return dict(NULL_A=A, NULL_B=B, shifts=ks, n_draws=n_draws, buffer=buffer, seed=seed)


def pct_of(dist: np.ndarray, obs: float) -> float:
    """Percentile of `obs` within `dist`, i.e. the share of draws it strictly exceeds, in %."""
    return float(100.0 * np.mean(dist < obs))


def p_right(dist: np.ndarray, obs: float) -> float:
    """One-sided right-tail p-value with the +1 correction (never reports p = 0)."""
    return float((1.0 + np.sum(dist >= obs)) / (1.0 + len(dist)))


# ==================================================================================================
# Self-test - synthetic panels whose answers are known before the code runs
# ==================================================================================================
def selftest(log=print) -> int:
    checks = []

    def chk(name, cond, detail=""):
        checks.append((name, bool(cond), detail))

    rng = np.random.default_rng(11)

    # --- OLS against numpy's own least squares ------------------------------------------------
    x = rng.normal(0, 1, 500)
    y = 0.3 * x + rng.normal(0, 1, 500)
    b, psi = ols_beta_infl(y, x)
    ref = np.polyfit(x, y, 1)[0]
    chk("beta matches polyfit", abs(b - ref) < 1e-10, f"{b:.8f} vs {ref:.8f}")
    chk("influence sums to zero", abs(psi.sum()) < 1e-12)
    # HC0 SE against the textbook sandwich formula
    xc = x - x.mean()
    e = (y - y.mean()) - b * xc
    hc0 = np.sqrt(np.sum(xc ** 2 * e ** 2) / (np.sum(xc ** 2) ** 2))
    chk("clustered SE (1 obs/cluster) == HC0 x fs correction",
        abs(clustered_se(psi) - hc0 * np.sqrt(500 / 498)) < 1e-12)

    # --- analyse() recovers a PLANTED same-bucket cross-day effect and nothing else -----------
    n = 4000
    base = rng.normal(0, 1, (n, K))
    Rp = base.copy()
    for d in range(1, n):
        Rp[d] += 0.25 * base[d - 1]          # same clock bucket, one day back, beta = 0.25
    o = observed(Rp)
    chk("planted beta_same ~ 0.25", abs(np.mean(o["beta_same"]) - 0.25) < 0.03,
        f"{np.mean(o['beta_same']):.4f}")
    chk("planted design leaves beta_nonmult ~ 0", abs(np.mean(o["beta_nonmult"])) < 0.02,
        f"{np.mean(o['beta_nonmult']):.4f}")
    chk("planted design leaves beta_adj ~ 0", abs(np.nanmean(o["beta_adj"])) < 0.03,
        f"{np.nanmean(o['beta_adj']):.4f}")
    chk("gate margin is positive on the planted cross-day design",
        o["agg"][GATE_SET]["margin"] > 0.15, f"{o['agg'][GATE_SET]['margin']:.4f}")

    # --- the ADVERSARIAL case this whole run exists to detect: generic within-day momentum ----
    Rm = rng.normal(0, 1, (n, K))
    for d in range(n):
        for b in range(1, K):
            Rm[d, b] += 0.25 * Rm[d, b - 1]   # adjacent bucket, SAME day
    om = observed(Rm)
    chk("within-day momentum shows up in beta_adj", np.nanmean(om["beta_adj"]) > 0.15,
        f"{np.nanmean(om['beta_adj']):.4f}")
    chk("within-day momentum does NOT create beta_same",
        abs(np.mean(om["beta_same"])) < 0.03, f"{np.mean(om['beta_same']):.4f}")
    chk("gate margin is NEGATIVE when the mechanism is absent - the falsifier fires",
        om["agg"][GATE_SET]["margin"] < -0.15, f"{om['agg'][GATE_SET]['margin']:.4f}")

    # --- the null: on pure noise the observed margin must sit mid-distribution ----------------
    Rn = rng.normal(0, 1, (1200, K))
    on = observed(Rn)
    nl = circular_shift_null(Rn, n_draws=200, seed=3)
    pc = pct_of(nl["NULL_A"][GATE_SET]["margin"], on["agg"][GATE_SET]["margin"])
    chk("noise panel: margin percentile is not extreme", 2.0 < pc < 98.0, f"{pc:.1f}%")
    chk("null preserves the sample size", len(nl["NULL_A"][GATE_SET]["margin"]) == 200)
    chk("max statistic dominates the mean statistic in every draw",
        (nl["NULL_A"][GATE_SET]["max_margin"] >= nl["NULL_A"][GATE_SET]["margin"] - 1e-12).all())
    chk("no null shift re-aligns the predictor", (nl["shifts"] >= NULL_BUFFER).all()
        and (nl["shifts"] <= 1200 - NULL_BUFFER).all())

    # --- the null MUST reject on the planted design -------------------------------------------
    nlp = circular_shift_null(Rp[:1200], n_draws=200, seed=4)
    op = observed(Rp[:1200])
    chk("planted design beats its own max null",
        op["agg"][GATE_SET]["margin"] > np.percentile(nlp["NULL_A"][GATE_SET]["max_margin"], 95))
    # --- and MUST NOT reject on the within-day-momentum design ---------------------------------
    nlm = circular_shift_null(Rm[:1200], n_draws=200, seed=5)
    omm = observed(Rm[:1200])
    chk("within-day-momentum design fails its own max null",
        omm["agg"][GATE_SET]["margin"] < np.percentile(nlm["NULL_A"][GATE_SET]["max_margin"], 95))

    # --- rho_bar / K_eff --------------------------------------------------------------------
    rb, keff, _ = rho_bar_and_keff(Rn)
    chk("rho_bar of independent buckets ~ 0", abs(rb) < 0.02, f"{rb:.4f}")
    chk("K_eff obeys its definition exactly", abs(keff - K / (1 + (K - 1) * rb)) < 1e-12,
        f"{keff:.3f}")
    chk("K_eff ~ K when rho_bar ~ 0", abs(keff - K) < 1.5, f"{keff:.3f}")
    Rc = rng.normal(0, 1, (2000, 1)) + 0.0 * rng.normal(0, 1, (2000, K))
    Rc = np.repeat(Rc, K, axis=1)
    rb2, keff2, _ = rho_bar_and_keff(Rc)
    chk("perfectly correlated buckets give rho_bar = 1 and K_eff = 1",
        abs(rb2 - 1) < 1e-9 and abs(keff2 - 1) < 1e-9, f"rho {rb2:.4f} keff {keff2:.4f}")

    # --- bucket sets are frozen ---------------------------------------------------------------
    chk("beta_adj(0) is undefined and reported NaN", np.isnan(o["beta_adj"][0]))
    chk("gate set is the matched set b=1..12", GATE_SET == "MATCHED_1_12"
        and list(BUCKET_SETS[GATE_SET]) == list(range(1, 13)))

    npass = sum(c[1] for c in checks)
    w = max(len(c[0]) for c in checks)
    for name, okk, det in checks:
        log(f"  [{'PASS' if okk else 'FAIL'}] {name:<{w}}  {det}")
    log(f"  estim selftest {npass}/{len(checks)}")
    return 0 if npass == len(checks) else 1


if __name__ == "__main__":
    import sys
    sys.exit(selftest())
