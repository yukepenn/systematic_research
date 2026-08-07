"""trials.py — the preregistered campaign trial-accounting rule.

Implements research/registry/TRIAL_ACCOUNTING_RULE.md exactly. That document was written
BEFORE any figure was recomputed under it; this module must not be edited to change an
answer, only to fix a demonstrated deviation from the written rule.

R2  cluster trials by daily-P&L correlation, average linkage on d = sqrt(0.5*(1-rho))
R3  N_eff = K = participation ratio of the correlation eigenvalues (deterministic)
R4  V = variance of CLUSTER-REPRESENTATIVE Sharpes (equal-weight mean of each cluster)
R5  report DSR with N_eff, V and the pool description inline
R6  always report the Harvey-Liu Bonferroni / BHY haircut at the RAW N alongside
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import stats
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform

from validation import psr, sharpe


def effective_n_trials(matrix):
    """R3: participation ratio of the correlation-matrix eigenvalues."""
    C = np.corrcoef(np.asarray(matrix, float).T)
    C = np.nan_to_num(C, nan=0.0)
    lam = np.linalg.eigvalsh(C)
    lam = np.clip(lam, 0, None)
    return int(round(lam.sum() ** 2 / np.sum(lam ** 2)))


def cluster_trials(matrix, k):
    """R2: average-linkage clusters on d = sqrt(0.5*(1-rho)), cut at k clusters."""
    C = np.corrcoef(np.asarray(matrix, float).T)
    C = np.nan_to_num(C, nan=0.0)
    np.fill_diagonal(C, 1.0)
    D = np.sqrt(np.clip(0.5 * (1.0 - C), 0, None))
    np.fill_diagonal(D, 0.0)
    Z = linkage(squareform(D, checks=False), method="average")
    return fcluster(Z, t=k, criterion="maxclust")


def cluster_representatives(matrix, labels):
    """R4: each cluster's representative is the equal-weight mean of its members."""
    df = pd.DataFrame(matrix)
    reps = {}
    for c in np.unique(labels):
        cols = df.columns[labels == c]
        reps[f"cluster{c}"] = df[cols].mean(axis=1)
    return pd.DataFrame(reps)


def deflated_sharpe(series, v_ann, n_eff, ann=252):
    """DSR under the preregistered (N_eff, V) pair. v_ann is the ANNUALISED SR variance."""
    e = 0.5772156649015329
    z1 = stats.norm.ppf(1 - 1.0 / max(n_eff, 2))
    z2 = stats.norm.ppf(1 - 1.0 / (max(n_eff, 2) * math.e))
    sr0_ann = math.sqrt(max(v_ann, 1e-12)) * ((1 - e) * z1 + e * z2)
    return psr(series, sr_benchmark=sr0_ann, ann=ann), sr0_ann


def harvey_liu_haircut(series, n_raw, ann=252):
    """R6: Bonferroni and BHY haircuts at the RAW trial count. Deliberately harsh."""
    x = np.asarray(series, float)
    n = len(x)
    sr = sharpe(x, ann)
    t = sr / math.sqrt(ann) * math.sqrt(n)
    p = 2 * (1 - stats.norm.cdf(abs(t)))
    p_bonf = min(1.0, p * n_raw)
    t_bonf = stats.norm.ppf(1 - p_bonf / 2) if p_bonf < 1 else 0.0
    sr_bonf = t_bonf / math.sqrt(n) * math.sqrt(ann)
    bhy_thr = 0.05 / (n_raw * (math.log(n_raw) + 0.5772156649015329))
    return {
        "sharpe": sr, "t": t, "p": p, "n_days": n,
        "p_bonferroni": p_bonf, "haircut_sharpe_bonferroni": sr_bonf,
        "bhy_threshold": bhy_thr, "passes_bhy": bool(p < bhy_thr),
    }


def campaign_dsr(pool_matrix, candidates, n_raw, ann=252, pool_name=""):
    """Full R2-R6 pipeline.

    pool_matrix : DataFrame (days x trials) of EVERY trial from R1, survivors and rejects.
    candidates  : dict name -> daily series to deflate.
    n_raw       : raw trial count from R1, for the R6 haircut.
    """
    M = pool_matrix.fillna(0.0)
    k = effective_n_trials(M)
    labels = cluster_trials(M, k)
    reps = cluster_representatives(M, labels)
    rep_sr = np.array([sharpe(reps[c], ann) for c in reps.columns])
    v_ann = float(np.var(rep_sr, ddof=1))

    rows = []
    for name, s in candidates.items():
        d, sr0 = deflated_sharpe(s, v_ann, k, ann)
        hl = harvey_liu_haircut(s, n_raw, ann)
        rows.append({
            "candidate": name, "sharpe": sharpe(s, ann), "psr": psr(s),
            "N_raw": n_raw, "N_eff": k, "V_cluster": v_ann,
            "benchmark_sr": sr0, "DSR": d,
            "t": hl["t"], "p": hl["p"],
            "haircut_sharpe_bonferroni": hl["haircut_sharpe_bonferroni"],
            "passes_bhy": hl["passes_bhy"],
            "promotable_by_R7": bool(d >= 0.90),
        })
    meta = {"pool": pool_name, "n_trials_in_pool": M.shape[1], "N_eff": k,
            "V_cluster": v_ann, "cluster_sizes": np.bincount(labels)[1:].tolist()}
    return pd.DataFrame(rows), meta
